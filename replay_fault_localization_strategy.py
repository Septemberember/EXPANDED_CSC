#!/usr/bin/env python3
"""Replay a CCT fault-localization strategy from archived experiment artifacts.

This script does not rerun CSC generation, Java executions, or Refined TBFV. It
reuses archived CCT pickles, testcases.json files, and trace JSONL files to
recompute a selected edge-localization strategy and evaluate it against the
experiment's mutant manifest.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from csc_engine import (
    CCT,
    INTERVAL_TARGET_PREFIX,
    INTERVAL_STRATEGY_DESCRIPTIONS,
    aggregate_localization_report,
    build_localization_report,
    evaluate_reports,
    load_json_report,
    load_manifest,
    write_aggregated_localization_report,
    write_localization_report,
)


DEFAULT_TOP_K = [1, 3, 5, 10]
DEFAULT_STRATEGY = "edge_divergence_sibling_exclusive"


@dataclass(frozen=True)
class ReplayCase:
    experiment_id: str
    experiment_root: Path
    mutant_record: dict[str, Any]
    csc_result_dir: Path | None
    raw_report: Path | None
    aggregated_report: Path | None


def main() -> int:
    args = build_parser().parse_args()
    experiment_roots = [Path(root).resolve() for root in args.experiment_root]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    top_k = parse_top_k(args.top_k)

    rows: list[dict[str, Any]] = []
    for root in experiment_roots:
        rows.extend(replay_experiment(root, output_dir, args.strategy, top_k))

    summary_rows = summarize_rows(rows, top_k)
    write_jsonl(output_dir / "seed_replay_rows.jsonl", rows)
    write_csv(output_dir / "seed_replay_rows.csv", rows)
    write_csv(output_dir / "seed_replay_summary.csv", summary_rows)
    write_markdown(output_dir / "seed_replay_summary.md", summary_rows, args.strategy, top_k)
    write_json(output_dir / "seed_replay_metadata.json", {
        "strategy": args.strategy,
        "top_k": top_k,
        "experiment_roots": [str(root) for root in experiment_roots],
        "output_dir": str(output_dir),
        "task_count": len(rows),
        "evaluated_count": sum(1 for row in rows if row["status"] == "evaluated"),
        "skipped_count": sum(1 for row in rows if row["status"] != "evaluated"),
    })
    print(f"Replay complete: {output_dir}")
    print(f"  Tasks:     {len(rows)}")
    print(f"  Evaluated: {sum(1 for row in rows if row['status'] == 'evaluated')}")
    print(f"  Skipped:   {sum(1 for row in rows if row['status'] != 'evaluated')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replay a fault-localization strategy from archived CCT artifacts."
    )
    parser.add_argument(
        "--experiment-root",
        action="append",
        required=True,
        help="Archived experiment root. Repeat for multiple experiments.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Output directory for replay reports and summaries.",
    )
    parser.add_argument(
        "--strategy",
        default=DEFAULT_STRATEGY,
        choices=sorted(INTERVAL_STRATEGY_DESCRIPTIONS),
        help=f"Interval strategy to replay (default: {DEFAULT_STRATEGY}).",
    )
    parser.add_argument(
        "--top-k",
        default=",".join(str(k) for k in DEFAULT_TOP_K),
        help="Comma-separated top-k values for evaluation (default: 1,3,5,10).",
    )
    return parser


def replay_experiment(root: Path,
                      output_dir: Path,
                      strategy: str,
                      top_k: list[int]) -> list[dict[str, Any]]:
    manifest_path = root / "aggregation_ready" / "mutants_manifest.jsonl"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    experiment_id = root.name
    manifest_records = load_manifest(manifest_path)
    report_index = build_report_index(root)
    rows = []
    for record in manifest_records:
        mutant_id = str(record.get("mutant_id"))
        paths = report_index.get(mutant_id)
        case = ReplayCase(
            experiment_id=experiment_id,
            experiment_root=root,
            mutant_record=record,
            csc_result_dir=paths[0].parent if paths else None,
            raw_report=paths[0] if paths else None,
            aggregated_report=paths[1] if paths else None,
        )
        rows.append(replay_case(case, output_dir, strategy, top_k))
    return rows


def build_report_index(root: Path) -> dict[str, tuple[Path, Path | None]]:
    candidates = sorted(root.glob("**/cct_failure_localization.json"))
    index: dict[str, tuple[Path, Path | None]] = {}
    manifest_path = root / "aggregation_ready" / "mutants_manifest.jsonl"
    for record in load_manifest(manifest_path):
        mutant_id = str(record.get("mutant_id"))
        matched = [
            path for path in candidates
            if path_belongs_to_mutant(path, mutant_id)
        ]
        if not matched:
            continue
        selected = min(matched, key=lambda path: len(path.parts))
        index[mutant_id] = (
            selected,
            selected.with_name("cct_failure_localization_aggregated.json"),
        )
    return index


def path_belongs_to_mutant(path: Path, mutant_id: str) -> bool:
    parts = path.parts
    return any(part == mutant_id or part.endswith(f"_{mutant_id}") for part in parts)


def replay_case(case: ReplayCase,
                output_dir: Path,
                strategy: str,
                top_k: list[int]) -> dict[str, Any]:
    record = case.mutant_record
    mutant_id = str(record.get("mutant_id"))
    base_row = base_result_row(case, strategy)
    if case.csc_result_dir is None:
        return base_row | {"status": "skipped", "skip_reason": "missing_csc_result_dir"}

    try:
        cct_path = find_cct_path(case.csc_result_dir)
        testcase_records = load_replay_testcases(case.csc_result_dir)
        cct = CCT.load_from_file(str(cct_path))
        if cct is None:
            return base_row | {"status": "skipped", "skip_reason": f"cct_load_failed:{cct_path}"}

        report = build_localization_report(
            cct,
            testcase_records=testcase_records,
            interval_strategies=[strategy],
            default_interval_strategy=strategy,
        )
        source_file = resolve_source_file(case, record)
        aggregated = aggregate_localization_report(
            report,
            source_file=source_file,
            targets=[f"{INTERVAL_TARGET_PREFIX}{strategy}"],
        )

        artifact_dir = output_dir / "artifacts" / case.experiment_id / mutant_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        raw_out = artifact_dir / "cct_failure_localization_replay.json"
        aggregated_out = artifact_dir / "cct_failure_localization_replay_aggregated.json"
        write_localization_report(report, raw_out)
        write_aggregated_localization_report(aggregated, aggregated_out)

        replay_metrics = evaluate_reports(record, aggregated_report=aggregated, top_k=top_k)["metrics"]
        old_metrics = load_old_metrics(case, record, top_k)
        replay_key = f"aggregated.interval.{strategy}"
        replay_strategy_metrics = replay_metrics.get(replay_key, {})
        old_strategy_metrics = old_metrics.get("aggregated.interval.edge_divergence_gated", {})

        eval_out = artifact_dir / "fault_localization_replay_eval.json"
        write_json(eval_out, {
            "mutant_id": mutant_id,
            "strategy": strategy,
            "metrics": replay_metrics,
            "old_metrics": old_metrics,
        })

        return base_row | {
            "status": "evaluated",
            "skip_reason": "",
            "source_file": source_file,
            "raw_replay_report": str(raw_out),
            "aggregated_replay_report": str(aggregated_out),
            "eval_replay_report": str(eval_out),
            "prediction_count": replay_strategy_metrics.get("prediction_count"),
            "replay_hit": replay_strategy_metrics.get("hit", False),
            "replay_best_rank": replay_strategy_metrics.get("best_rank"),
            "replay_hit_item_region_size": replay_strategy_metrics.get("hit_item_region_size"),
            "replay_cumulative_region_at_first_hit": (
                replay_strategy_metrics.get("inspection_region", {}).get("at_first_hit")
            ),
            "replay_average_region_size": (
                replay_strategy_metrics.get("region_size", {}).get("average")
            ),
            "old_hit": old_strategy_metrics.get("hit", False),
            "old_best_rank": old_strategy_metrics.get("best_rank"),
            "old_hit_item_region_size": old_strategy_metrics.get("hit_item_region_size"),
            "old_cumulative_region_at_first_hit": (
                old_strategy_metrics.get("inspection_region", {}).get("at_first_hit")
            ),
            "old_average_region_size": old_strategy_metrics.get("region_size", {}).get("average"),
        } | topk_fields("replay", replay_strategy_metrics, top_k) | topk_fields("old", old_strategy_metrics, top_k)
    except Exception as exc:
        return base_row | {"status": "skipped", "skip_reason": str(exc)}


def base_result_row(case: ReplayCase, strategy: str) -> dict[str, Any]:
    record = case.mutant_record
    ground_truth = record.get("ground_truth", {})
    return {
        "experiment_id": case.experiment_id,
        "mutant_id": record.get("mutant_id"),
        "subject": record.get("subject"),
        "operator": record.get("operator"),
        "fault_kind": record.get("fault_kind"),
        "fault_category": record.get("fault_category"),
        "primary_line": ground_truth.get("primary_line"),
        "strategy": strategy,
        "csc_result_dir": str(case.csc_result_dir) if case.csc_result_dir else "",
    }


def find_cct_path(csc_result_dir: Path) -> Path:
    candidates = sorted(csc_result_dir.glob("*_cct.pkl"))
    if not candidates:
        raise FileNotFoundError(f"CCT pickle not found in {csc_result_dir}")
    return candidates[0]


def load_replay_testcases(csc_result_dir: Path) -> list[dict[str, Any]]:
    path = csc_result_dir / "testcases.json"
    if not path.exists():
        raise FileNotFoundError(f"testcases.json not found: {path}")
    records = json.loads(path.read_text(encoding="utf-8"))
    for record in records:
        trace_path = Path(record.get("trace_path", ""))
        if trace_path.exists():
            continue
        remapped = remap_trace_path(csc_result_dir, trace_path)
        if not remapped.exists():
            raise FileNotFoundError(f"Trace not found: {trace_path} (remapped: {remapped})")
        record["trace_path"] = str(remapped)
    return records


def remap_trace_path(csc_result_dir: Path, trace_path: Path) -> Path:
    if "traces" in trace_path.parts:
        index = trace_path.parts.index("traces")
        return csc_result_dir.joinpath(*trace_path.parts[index:])
    return csc_result_dir / trace_path


def resolve_source_file(case: ReplayCase, record: dict[str, Any]) -> str | None:
    if case.aggregated_report and case.aggregated_report.exists():
        try:
            summary = load_json_report(case.aggregated_report).get("summary", {})
            if summary.get("source_file"):
                return summary["source_file"]
        except Exception:
            pass
    return record.get("mutant_file")


def load_old_metrics(case: ReplayCase,
                     record: dict[str, Any],
                     top_k: list[int]) -> dict[str, Any]:
    if not case.aggregated_report or not case.aggregated_report.exists():
        return {}
    return evaluate_reports(
        record,
        aggregated_report=load_json_report(case.aggregated_report),
        top_k=top_k,
    )["metrics"]


def topk_fields(prefix: str, metrics: dict[str, Any], top_k: list[int]) -> dict[str, Any]:
    topk = metrics.get("topk", {}) if metrics else {}
    return {
        f"{prefix}_top{k}": bool(topk.get(f"top{k}", False))
        for k in top_k
    }


def summarize_rows(rows: list[dict[str, Any]], top_k: list[int]) -> list[dict[str, Any]]:
    summary = []
    groups = [("overall", rows)]
    experiments = sorted({
        str(row.get("experiment_id"))
        for row in rows
        if row.get("experiment_id")
    })
    groups.extend((f"experiment:{experiment}", [row for row in rows if row.get("experiment_id") == experiment])
                  for experiment in experiments)
    categories = sorted({
        str(row.get("fault_category"))
        for row in rows
        if row.get("fault_category")
    })
    groups.extend((category, [row for row in rows if row.get("fault_category") == category])
                  for category in categories)
    groups.extend(
        (
            f"{experiment}:{category}",
            [
                row for row in rows
                if row.get("experiment_id") == experiment
                and row.get("fault_category") == category
            ],
        )
        for experiment in experiments
        for category in categories
    )
    for group_name, group_rows in groups:
        evaluated = [row for row in group_rows if row.get("status") == "evaluated"]
        row = {
            "group": group_name,
            "tasks": len(group_rows),
            "evaluated": len(evaluated),
            "skipped": len(group_rows) - len(evaluated),
            "old_mean_hit_item_region": numeric_mean(evaluated, "old_hit_item_region_size"),
            "replay_mean_hit_item_region": numeric_mean(evaluated, "replay_hit_item_region_size"),
            "old_mean_cumulative_region": numeric_mean(evaluated, "old_cumulative_region_at_first_hit"),
            "replay_mean_cumulative_region": numeric_mean(evaluated, "replay_cumulative_region_at_first_hit"),
            "old_average_region_size": numeric_mean(evaluated, "old_average_region_size"),
            "replay_average_region_size": numeric_mean(evaluated, "replay_average_region_size"),
        }
        for k in top_k:
            row[f"old_top{k}_hit_rate"] = bool_rate(evaluated, f"old_top{k}")
            row[f"replay_top{k}_hit_rate"] = bool_rate(evaluated, f"replay_top{k}")
        summary.append(row)
    return summary


def numeric_mean(rows: list[dict[str, Any]], field: str) -> float | None:
    values = [
        float(row[field])
        for row in rows
        if row.get(field) is not None
    ]
    return mean(values) if values else None


def bool_rate(rows: list[dict[str, Any]], field: str) -> float | None:
    if not rows:
        return None
    return sum(1 for row in rows if row.get(field)) / len(rows)


def write_markdown(path: Path,
                   summary_rows: list[dict[str, Any]],
                   strategy: str,
                   top_k: list[int]) -> None:
    headers = [
        "Group",
        "Tasks",
        "Evaluated",
        "Skipped",
    ]
    for k in top_k:
        headers.extend([f"Old Top-{k}", f"SEED Top-{k}"])
    headers.extend([
        "Old Hit Item Region",
        "SEED Hit Item Region",
        "Old Cum. Region",
        "SEED Cum. Region",
        "Old Avg Region",
        "SEED Avg Region",
    ])
    lines = [
        "# SEED Replay Fault Localization Summary",
        "",
        f"- Strategy: `{strategy}`",
        f"- Top-k: {', '.join(str(k) for k in top_k)}",
        "- Old strategy baseline: `aggregated.interval.edge_divergence_gated`",
        "- Replay uses archived CCT, testcases.json, and trace JSONL artifacts only.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in summary_rows:
        values = [
            row["group"],
            row["tasks"],
            row["evaluated"],
            row["skipped"],
        ]
        for k in top_k:
            values.extend([
                fmt(row.get(f"old_top{k}_hit_rate")),
                fmt(row.get(f"replay_top{k}_hit_rate")),
            ])
        values.extend([
            fmt(row.get("old_mean_hit_item_region")),
            fmt(row.get("replay_mean_hit_item_region")),
            fmt(row.get("old_mean_cumulative_region")),
            fmt(row.get("replay_mean_cumulative_region")),
            fmt(row.get("old_average_region_size")),
            fmt(row.get("replay_average_region_size")),
        ])
        lines.append("| " + " | ".join(str(value) for value in values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def parse_top_k(raw: str) -> list[int]:
    values = sorted({int(item.strip()) for item in raw.split(",") if item.strip()})
    return [value for value in values if value > 0]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({field for row in rows for field in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
