#!/usr/bin/env python3
"""Prepare and aggregate fault-localization experiment row files.

This utility is intentionally row-oriented. It does not run CSC, Refined TBFV,
or localization; it only normalizes existing CCT/SFL outputs so several dataset
experiments can be combined without hand-editing reports.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from csc_engine import (
    DEFAULT_EVAL_TOP_K,
    evaluate_reports,
    load_json_report,
    load_manifest,
    summarize_fault_localization_results,
    write_csv_rows,
    write_evaluation_report,
    write_jsonl_rows,
    write_markdown_summary,
)
from csc_engine.failure_localization_summary import _build_summary


@dataclass(frozen=True)
class ExperimentSpec:
    experiment_id: str
    dataset_id: str
    root: Path
    manifest: Path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    top_k = parse_top_k(args.top_k)
    specs = [parse_experiment(raw) for raw in args.experiment]

    prepared = []
    for spec in specs:
        ready_dir = prepare_experiment(spec, top_k=top_k)
        prepared.append((spec, ready_dir))

    if args.combine:
        combine_experiments(prepared, args.output_dir, top_k=top_k)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize and optionally combine CCT/SFL fault-localization row files."
    )
    parser.add_argument(
        "--experiment",
        action="append",
        required=True,
        metavar="EXPERIMENT_ID:DATASET_ID:ROOT:MANIFEST",
        help="Experiment descriptor. May be repeated.",
    )
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Also write a combined report from the prepared experiments.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Combined output directory. Required when --combine is used.",
    )
    parser.add_argument(
        "--top-k",
        default=",".join(str(k) for k in DEFAULT_EVAL_TOP_K),
        help="Comma-separated Top-k values.",
    )
    return parser


def parse_experiment(raw: str) -> ExperimentSpec:
    parts = raw.split(":", 3)
    if len(parts) != 4:
        raise ValueError(
            "--experiment must use EXPERIMENT_ID:DATASET_ID:ROOT:MANIFEST"
        )
    experiment_id, dataset_id, root, manifest = parts
    return ExperimentSpec(
        experiment_id=experiment_id,
        dataset_id=dataset_id,
        root=Path(root),
        manifest=Path(manifest),
    )


def parse_top_k(raw: str) -> list[int]:
    values = sorted({int(item.strip()) for item in raw.split(",") if item.strip()})
    return [value for value in values if value > 0] or list(DEFAULT_EVAL_TOP_K)


def prepare_experiment(spec: ExperimentSpec, top_k: list[int]) -> Path:
    ready_dir = spec.root / "aggregation_ready"
    ready_dir.mkdir(parents=True, exist_ok=True)
    manifest_records = load_manifest(spec.manifest)
    write_jsonl_rows(
        [tag_manifest_record(record, spec) for record in manifest_records],
        ready_dir / "mutants_manifest.jsonl",
    )

    cct_report = build_cct_rows(spec, manifest_records, top_k, ready_dir)
    write_prepared_rows(
        normalize_rows(cct_report["rows"], spec, method_family="CCT"),
        ready_dir,
        "cct_fault_localization_rows",
        manifest_count=len(manifest_records),
        report_count=cct_report["summary"].get("evaluation_report_count", 0),
        top_k=top_k,
    )

    sfl_rows = load_sfl_rows(spec)
    write_prepared_rows(
        normalize_rows(sfl_rows, spec, method_family="SFL"),
        ready_dir,
        "sfl_fault_localization_rows",
        manifest_count=len(manifest_records),
        report_count=count_distinct_evaluated_mutants(sfl_rows),
        top_k=top_k,
    )

    metadata = {
        "experiment_id": spec.experiment_id,
        "dataset_id": spec.dataset_id,
        "root": str(spec.root),
        "manifest": str(spec.manifest),
        "manifest_count": len(manifest_records),
        "cct_rows": len(cct_report["rows"]),
        "sfl_rows": len(sfl_rows),
        "top_k": top_k,
    }
    write_json(ready_dir / "aggregation_metadata.json", metadata)
    return ready_dir


def tag_manifest_record(record: dict[str, Any], spec: ExperimentSpec) -> dict[str, Any]:
    tagged = dict(record)
    tagged["experiment_id"] = spec.experiment_id
    tagged["dataset_id"] = spec.dataset_id
    return tagged


def build_cct_rows(spec: ExperimentSpec,
                   manifest_records: list[dict[str, Any]],
                   top_k: list[int],
                   ready_dir: Path) -> dict[str, Any]:
    eval_dir = ready_dir / "cct_eval_reports"
    eval_dir.mkdir(parents=True, exist_ok=True)
    eval_paths = []

    for record in manifest_records:
        mutant_id = str(record.get("mutant_id") or "")
        reports = find_cct_reports(spec.root, mutant_id)
        output_path = eval_dir / mutant_id / "fault_localization_eval.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if reports is None:
            continue
        class_dir, raw_report, aggregated_report = reports
        if not has_tbfv_failure_signal(class_dir):
            write_no_metrics_evaluation(record, output_path, top_k)
            eval_paths.append(output_path)
            continue
        evaluation = evaluate_reports(
            record,
            raw_report=load_json_report(raw_report) if raw_report else None,
            aggregated_report=load_json_report(aggregated_report) if aggregated_report else None,
            top_k=top_k,
        )
        write_evaluation_report(evaluation, output_path)
        eval_paths.append(output_path)

    return summarize_fault_localization_results(
        manifest_records,
        eval_paths,
        top_k=top_k,
    )


def find_cct_reports(root: Path, mutant_id: str) -> tuple[Path, Path | None, Path | None] | None:
    if not mutant_id:
        return None
    candidate_dirs = sorted({
        path.parent
        for path in root.glob("**/cct_failure_localization.json")
        if path.is_file() and path_belongs_to_mutant(path, mutant_id)
    })
    if not candidate_dirs:
        return None
    # Prefer the deepest, most specific class directory.
    selected = max(candidate_dirs, key=lambda path: (len(path.parts), str(path)))
    raw = selected / "cct_failure_localization.json"
    aggregated = selected / "cct_failure_localization_aggregated.json"
    return (
        selected,
        raw if raw.exists() else None,
        aggregated if aggregated.exists() else None,
    )


def path_belongs_to_mutant(path: Path, mutant_id: str) -> bool:
    return any(
        part == mutant_id or part.endswith(f"_{mutant_id}")
        for part in path.parts
    )


def has_tbfv_failure_signal(class_dir: Path) -> bool:
    report_path = class_dir / "refined_tbfv_report.json"
    if not report_path.exists():
        return True
    report = load_json_report(report_path)
    return int(report.get("summary", {}).get("failed", 0) or 0) > 0


def write_no_metrics_evaluation(record: dict[str, Any],
                                output_path: Path,
                                top_k: list[int]) -> None:
    ground_truth = record.get("ground_truth", {}) if isinstance(record.get("ground_truth"), dict) else {}
    evaluation = {
        "mutant_id": record.get("mutant_id"),
        "mutant_file": record.get("mutant_file"),
        "operator": record.get("operator") or ground_truth.get("operator"),
        "fault_kind": record.get("fault_kind"),
        "ground_truth": ground_truth,
        "summary": {
            "top_k": top_k,
            "status": "no_metrics",
            "reason": "no Refined TBFV failures for this mutant",
        },
        "metrics": {},
    }
    write_evaluation_report(evaluation, output_path)


def load_sfl_rows(spec: ExperimentSpec) -> list[dict[str, Any]]:
    candidates = [
        spec.root / "baseline-SFL-v2" / "sfl_fault_localization_rows.jsonl",
        spec.root / "baseline-SFL" / "sfl_fault_localization_rows.jsonl",
    ]
    for candidate in candidates:
        if candidate.exists():
            return load_jsonl(candidate)
    return []


def normalize_rows(rows: Iterable[dict[str, Any]],
                   spec: ExperimentSpec,
                   method_family: str) -> list[dict[str, Any]]:
    normalized = []
    for row in rows:
        item = dict(row)
        item["experiment_id"] = spec.experiment_id
        item["dataset_id"] = spec.dataset_id
        item.setdefault("method_family", method_family)
        if item.get("hit_item_region_size") is None:
            item["hit_item_region_size"] = item.get("region_size_hit")
        normalized.append(item)
    return normalized


def write_prepared_rows(rows: list[dict[str, Any]],
                        ready_dir: Path,
                        stem: str,
                        manifest_count: int,
                        report_count: int,
                        top_k: list[int]) -> None:
    write_jsonl_rows(rows, ready_dir / f"{stem}.jsonl")
    write_csv_rows(rows, ready_dir / f"{stem}.csv")
    report = {
        "summary": _build_summary(
            rows,
            manifest_count=manifest_count,
            evaluation_report_count=report_count,
            top_k=top_k,
        ),
        "rows": rows,
    }
    write_markdown_summary(report, ready_dir / f"{stem}_summary.md")


def combine_experiments(prepared: list[tuple[ExperimentSpec, Path]],
                        output_dir: Path | None,
                        top_k: list[int]) -> None:
    if output_dir is None:
        raise ValueError("--output-dir is required when --combine is used")
    output_dir.mkdir(parents=True, exist_ok=True)

    cct_rows = []
    sfl_rows = []
    manifest_rows = []
    for spec, ready_dir in prepared:
        cct_rows.extend(load_jsonl(ready_dir / "cct_fault_localization_rows.jsonl"))
        sfl_rows.extend(load_jsonl(ready_dir / "sfl_fault_localization_rows.jsonl"))
        manifest_rows.extend(load_jsonl(ready_dir / "mutants_manifest.jsonl"))

    write_jsonl_rows(manifest_rows, output_dir / "combined_mutants_manifest.jsonl")
    write_combined_group(output_dir, "combined_cct_fault_localization_rows", cct_rows, manifest_rows, top_k)
    write_combined_group(output_dir, "combined_sfl_fault_localization_rows", sfl_rows, manifest_rows, top_k)
    write_combined_group(output_dir, "combined_fault_localization_rows", cct_rows + sfl_rows, manifest_rows, top_k)
    write_json(output_dir / "combined_experiment_metadata.json", {
        "experiments": [
            {
                "experiment_id": spec.experiment_id,
                "dataset_id": spec.dataset_id,
                "root": str(spec.root),
                "aggregation_ready": str(ready_dir),
            }
            for spec, ready_dir in prepared
        ],
        "manifest_count": len(manifest_rows),
        "cct_rows": len(cct_rows),
        "sfl_rows": len(sfl_rows),
        "top_k": top_k,
    })


def write_combined_group(output_dir: Path,
                         stem: str,
                         rows: list[dict[str, Any]],
                         manifest_rows: list[dict[str, Any]],
                         top_k: list[int]) -> None:
    write_jsonl_rows(rows, output_dir / f"{stem}.jsonl")
    write_csv_rows(rows, output_dir / f"{stem}.csv")
    report = {
        "summary": _build_summary(
            rows,
            manifest_count=len(manifest_rows),
            evaluation_report_count=count_distinct_evaluated_mutants(rows),
            top_k=top_k,
        ),
        "rows": rows,
    }
    write_markdown_summary(report, output_dir / f"{stem}_summary.md")


def count_distinct_evaluated_mutants(rows: Iterable[dict[str, Any]]) -> int:
    return len({
        row.get("mutant_id")
        for row in rows
        if row.get("status") == "evaluated" and row.get("mutant_id")
    })


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
