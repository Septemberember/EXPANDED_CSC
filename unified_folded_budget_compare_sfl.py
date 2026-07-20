#!/usr/bin/env python3
"""Experimental unified folded-candidate ranking vs SFL.

This script is intentionally isolated from the production fault-localization
pipeline.  It reuses archived folded localization artifacts and builds one
experimental ranking by merging source-level condition candidates and
edge-partition candidates into a single list sorted by their existing folded
risk score.  For each Top-K in the unified list, SFL receives the same unique
source-line budget.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_TOP_K = [1, 2, 3, 4, 5]
DEFAULT_SFL_FORMULA = "ochiai"
UNIFIED_STRATEGY = "experimental.unified_folded_source_candidate"


def main() -> int:
    args = _build_parser().parse_args()
    folded_rows_path = args.folded_rows.resolve()
    experiment_dirs = [Path(p).resolve() for p in args.experiment_dir]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    top_k = _parse_int_list(args.top_k)

    manifests = _load_manifests(experiment_dirs)
    folded_rows = _read_jsonl(folded_rows_path)
    result_rows: list[dict[str, Any]] = []

    for row in folded_rows:
        if row.get("status") != "evaluated":
            result_rows.append(_base_row(row) | {
                "status": row.get("status", "skipped"),
                "reason": "folded_row_not_evaluated",
            })
            continue
        result_rows.append(_compare_one(row, manifests, experiment_dirs,
                                        args.sfl_formula, top_k))

    evaluated = [r for r in result_rows if r.get("status") == "evaluated"]
    _write_outputs(output_dir, result_rows, evaluated, folded_rows_path,
                   experiment_dirs, args.sfl_formula, top_k)
    print(f"Unified folded budget-matched experiment complete: {output_dir}")
    print(f"  Rows:      {len(result_rows)}")
    print(f"  Evaluated: {len(evaluated)}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Experimental budget-matched comparison for one unified folded "
            "source-candidate ranking."
        )
    )
    parser.add_argument(
        "--folded-rows",
        required=True,
        type=Path,
        help="folded_replay_rows.jsonl containing aggregated report paths.",
    )
    parser.add_argument(
        "--experiment-dir",
        action="append",
        required=True,
        help="Archived FL experiment directory with manifest and SFL reports. Repeatable.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory for experimental rows, summary, and artifacts.",
    )
    parser.add_argument(
        "--top-k",
        default=",".join(str(v) for v in DEFAULT_TOP_K),
        help="Comma-separated Top-K values for the unified folded ranking.",
    )
    parser.add_argument(
        "--sfl-formula",
        default=DEFAULT_SFL_FORMULA,
        help="SFL formula key, e.g. ochiai.",
    )
    return parser


def _parse_int_list(text: str) -> list[int]:
    values = sorted({int(part.strip()) for part in text.split(",") if part.strip()})
    if not values or any(v <= 0 for v in values):
        raise ValueError(f"Top-K values must be positive: {text!r}")
    return values


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _load_manifests(experiment_dirs: list[Path]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for exp_dir in experiment_dirs:
        manifest = exp_dir / "aggregation_ready" / "mutants_manifest.jsonl"
        if not manifest.exists():
            continue
        for row in _read_jsonl(manifest):
            mutant_id = str(row.get("mutant_id", ""))
            if mutant_id:
                records[mutant_id] = row
    return records


def _compare_one(
    folded_row: dict[str, Any],
    manifests: dict[str, dict[str, Any]],
    experiment_dirs: list[Path],
    sfl_formula: str,
    top_k: list[int],
) -> dict[str, Any]:
    base = _base_row(folded_row)
    mutant_id = str(folded_row.get("mutant_id", ""))
    manifest_row = manifests.get(mutant_id, {})
    ground_truth = manifest_row.get("ground_truth", {})

    aggregated_path = Path(str(folded_row.get("aggregated_report", "")))
    if not aggregated_path.exists():
        return base | {"status": "skipped", "reason": "missing_aggregated_report"}

    sfl_report = _find_sfl_report(experiment_dirs, mutant_id)
    if sfl_report is None:
        return base | {"status": "skipped", "reason": "missing_sfl_report"}

    aggregated = json.loads(aggregated_path.read_text(encoding="utf-8"))
    sfl_data = json.loads(sfl_report.read_text(encoding="utf-8"))
    sfl_ranking = sfl_data.get("rankings", {}).get(sfl_formula)
    if not isinstance(sfl_ranking, list):
        return base | {"status": "skipped", "reason": f"missing_sfl_formula:{sfl_formula}"}

    unified = _build_unified_ranking(aggregated)
    acceptable = _acceptable_line_set(ground_truth)
    window = _acceptable_window(ground_truth)

    def hit(lines: set[int]) -> bool:
        if acceptable.intersection(lines):
            return True
        if window is not None:
            start, end = window
            return any(start <= line <= end for line in lines)
        return False

    result = base | {
        "status": "evaluated",
        "strategy": UNIFIED_STRATEGY,
        "primary_line": ground_truth.get("primary_line"),
        "primary_file": ground_truth.get("primary_file"),
        "candidate_count": len(unified),
        "condition_candidate_count": sum(1 for item in unified if item["kind"] == "condition"),
        "edge_candidate_count": sum(1 for item in unified if item["kind"] == "edge_partition"),
        "sfl_formula": sfl_formula,
    }

    for k in top_k:
        folded_lines = _unique_lines_from_items(unified[:k])
        sfl_lines = _sfl_budget_lines(sfl_ranking, len(folded_lines))
        result.update({
            f"top{k}_budget": len(folded_lines),
            f"top{k}_unified_hit": hit(folded_lines),
            f"top{k}_sfl_hit": hit(sfl_lines),
            f"top{k}_unified_region_lines": sorted(folded_lines),
            f"top{k}_sfl_region_lines": sorted(sfl_lines),
        })

    result["top_unified_items"] = unified[:max(top_k)]
    return result


def _base_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "mutant_id": row.get("mutant_id"),
        "subject": row.get("subject"),
        "operator": row.get("operator"),
        "fault_kind": row.get("fault_kind"),
        "fault_category": row.get("fault_category"),
        "scoring_strategy": row.get("scoring_strategy"),
        "F_total": row.get("F_total"),
        "P_total": row.get("P_total"),
        "aggregated_report": row.get("aggregated_report"),
    }


def _build_unified_ranking(aggregated: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for record in aggregated.get("aggregated_condition_node_ranking", []) or []:
        line = record.get("line")
        if line is None:
            continue
        items.append({
            "kind": "condition",
            "source_file": record.get("source_file"),
            "line": int(line),
            "condition": record.get("condition"),
            "region_lines": [int(line)],
            "region_size": 1,
            "risk_score": float(record.get("risk_score", 0.0)),
            "pass_count": int(record.get("pass_count", 0)),
            "fail_count": int(record.get("fail_count", 0)),
            "support_count": int(record.get("support_count", 0)),
            "best_raw_rank": _int_or_large(record.get("best_raw_rank")),
            "original_rank": _int_or_large(record.get("rank")),
        })

    edge_records = (
        aggregated.get("aggregated_interval_rankings", {}) or {}
    ).get("folded_edge_partition", []) or []
    for record in edge_records:
        lines = sorted({int(v) for v in (record.get("statement_lines") or [])})
        if not lines:
            continue
        items.append({
            "kind": "edge_partition",
            "source_file": record.get("source_file"),
            "from_line": record.get("from_line"),
            "from_condition": record.get("from_condition"),
            "outcome": record.get("outcome"),
            "to_line": record.get("to_line"),
            "to_condition": record.get("to_condition"),
            "region_lines": lines,
            "region_size": len(lines),
            "risk_score": float(record.get("risk_score", 0.0)),
            "base_risk_score": float(record.get("base_risk_score", record.get("risk_score", 0.0))),
            "pass_count": int(record.get("pass_count", 0)),
            "fail_count": int(record.get("fail_count", 0)),
            "support_count": int(record.get("support_count", 0)),
            "best_raw_rank": _int_or_large(record.get("best_raw_rank")),
            "original_rank": _int_or_large(record.get("rank")),
        })

    items.sort(key=_unified_sort_key)
    for rank, item in enumerate(items, start=1):
        item["rank"] = rank
    return items


def _unified_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -float(item.get("risk_score", 0.0)),
        int(item.get("pass_count", 0)),
        -int(item.get("support_count", 0)),
        int(item.get("best_raw_rank", 10**9)),
        int(item.get("region_size", 10**9)),
        min(item.get("region_lines") or [10**9]),
        0 if item.get("kind") == "condition" else 1,
    )


def _int_or_large(value: Any) -> int:
    if value is None:
        return 10**9
    try:
        return int(value)
    except (TypeError, ValueError):
        return 10**9


def _unique_lines_from_items(items: list[dict[str, Any]]) -> set[int]:
    lines: set[int] = set()
    for item in items:
        lines.update(int(v) for v in (item.get("region_lines") or []))
    return lines


def _sfl_budget_lines(ranking: list[dict[str, Any]], budget: int) -> set[int]:
    lines: set[int] = set()
    for item in ranking:
        if len(lines) >= budget:
            break
        line = item.get("line")
        if line is not None:
            lines.add(int(line))
    return lines


def _acceptable_line_set(ground_truth: dict[str, Any]) -> set[int]:
    lines: set[int] = set()
    for value in ground_truth.get("acceptable_lines", []) or []:
        lines.add(int(value))
    primary = ground_truth.get("primary_line")
    if primary is not None:
        lines.add(int(primary))
    return lines


def _acceptable_window(ground_truth: dict[str, Any]) -> tuple[int, int] | None:
    window = ground_truth.get("acceptable_line_window")
    if isinstance(window, dict) and window.get("start") is not None and window.get("end") is not None:
        return int(window["start"]), int(window["end"])
    return None


def _find_sfl_report(experiment_dirs: list[Path], mutant_id: str) -> Path | None:
    for exp_dir in experiment_dirs:
        for base in ("baseline-SFL-v2", "baseline-SFL"):
            sfl_dir = exp_dir / base
            if not sfl_dir.exists():
                continue
            for cand in _mutant_dir_candidates(sfl_dir, mutant_id):
                report = cand / "sfl_localization.json"
                if report.exists():
                    return report
    return None


def _mutant_dir_candidates(base: Path, mutant_id: str) -> list[Path]:
    candidates: list[Path] = []
    for cand in sorted(base.glob(f"**/{mutant_id}")):
        if cand.is_dir():
            candidates.append(cand)
    for cand in sorted(base.glob(f"**/*_{mutant_id}")):
        if cand.is_dir():
            candidates.append(cand)
    return candidates


def _write_outputs(
    output_dir: Path,
    rows: list[dict[str, Any]],
    evaluated: list[dict[str, Any]],
    folded_rows_path: Path,
    experiment_dirs: list[Path],
    sfl_formula: str,
    top_k: list[int],
) -> None:
    _write_jsonl(output_dir / "unified_budget_rows.jsonl", rows)
    _write_csv(output_dir / "unified_budget_rows.csv", rows)
    summary = _build_summary(evaluated, top_k)
    (output_dir / "unified_budget_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "unified_budget_summary.md").write_text(
        "\n".join(_build_markdown(summary, sfl_formula, top_k)),
        encoding="utf-8",
    )
    metadata = {
        "strategy": UNIFIED_STRATEGY,
        "folded_rows": str(folded_rows_path),
        "experiment_dirs": [str(p) for p in experiment_dirs],
        "sfl_formula": sfl_formula,
        "top_k": top_k,
        "total_rows": len(rows),
        "evaluated_rows": len(evaluated),
        "note": (
            "Experimental only: condition and folded edge-partition candidates "
            "are merged into one source-candidate ranking. Existing production "
            "strategies are not modified."
        ),
    }
    (output_dir / "unified_budget_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _build_summary(evaluated: list[dict[str, Any]], top_k: list[int]) -> list[dict[str, Any]]:
    categories = ["overall"]
    for row in evaluated:
        category = str(row.get("fault_category") or "<missing>")
        if category not in categories:
            categories.append(category)

    summary: list[dict[str, Any]] = []
    for category in categories:
        rows = evaluated if category == "overall" else [
            row for row in evaluated if str(row.get("fault_category")) == category
        ]
        if not rows:
            continue
        item: dict[str, Any] = {"fault_category": category, "cases": len(rows)}
        for k in top_k:
            budgets = [int(row.get(f"top{k}_budget", 0)) for row in rows]
            unified_hits = sum(1 for row in rows if row.get(f"top{k}_unified_hit"))
            sfl_hits = sum(1 for row in rows if row.get(f"top{k}_sfl_hit"))
            item.update({
                f"top{k}_mean_budget": mean(budgets) if budgets else 0.0,
                f"top{k}_median_budget": _median(budgets),
                f"top{k}_unified_hits": unified_hits,
                f"top{k}_unified_rate": unified_hits / len(rows),
                f"top{k}_sfl_hits": sfl_hits,
                f"top{k}_sfl_rate": sfl_hits / len(rows),
                f"top{k}_delta_rate": (unified_hits - sfl_hits) / len(rows),
            })
        summary.append(item)
    return summary


def _median(values: list[int]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2:
        return float(sorted_values[mid])
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2


def _build_markdown(summary: list[dict[str, Any]], sfl_formula: str,
                    top_k: list[int]) -> list[str]:
    lines = [
        "# Experimental Unified Folded Ranking vs SFL",
        "",
        f"- Unified strategy: `{UNIFIED_STRATEGY}`",
        f"- SFL formula: `{sfl_formula}`",
        "- Scope: experimental analysis only; existing folded composite, condition, "
        "and edge-partition strategies are not changed.",
        "- Ranking: source-level condition candidates and folded edge-partition "
        "candidates are merged and sorted by the existing folded risk score.",
        "- Budget matching: for unified Top-K, SFL receives the same number of "
        "unique source lines as the unified region.",
        "",
    ]
    for item in summary:
        lines.append(f"## {item['fault_category']} (N={item['cases']})")
        lines.append("")
        lines.append("| Top-K | Mean Budget | Median Budget | Unified Hit Rate | SFL Hit Rate | Delta |")
        lines.append("| ---: | ---: | ---: | ---: | ---: | ---: |")
        for k in top_k:
            unified_rate = item[f"top{k}_unified_rate"]
            sfl_rate = item[f"top{k}_sfl_rate"]
            delta = item[f"top{k}_delta_rate"]
            lines.append(
                f"| {k} | {item[f'top{k}_mean_budget']:.1f} | "
                f"{item[f'top{k}_median_budget']:.1f} | "
                f"{item[f'top{k}_unified_hits']}/{item['cases']} ({unified_rate:.3f}) | "
                f"{item[f'top{k}_sfl_hits']}/{item['cases']} ({sfl_rate:.3f}) | "
                f"{delta:+.3f} |"
            )
        lines.append("")
    lines.extend(_build_brief_observations(summary, top_k))
    return lines


def _build_brief_observations(summary: list[dict[str, Any]],
                              top_k: list[int]) -> list[str]:
    overall = next((item for item in summary if item["fault_category"] == "overall"), None)
    if overall is None:
        return []
    lines = ["## Brief Observations", ""]
    for k in top_k:
        delta = overall[f"top{k}_delta_rate"]
        direction = "ahead of" if delta > 0 else ("behind" if delta < 0 else "tied with")
        lines.append(
            f"- Top-{k}: unified folded is {direction} SFL by {abs(delta):.3f} "
            f"hit-rate points under a mean budget of {overall[f'top{k}_mean_budget']:.1f} lines."
        )
    return lines


if __name__ == "__main__":
    raise SystemExit(main())
