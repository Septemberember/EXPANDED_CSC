#!/usr/bin/env python3
"""Find poor-ranked folded fault-localization tasks for RQ4 analysis.

The script is intentionally read-only with respect to existing experiment
artifacts. It scans folded replay rows, optionally joins budget-matched SFL
comparison rows, and writes a compact set of failure-analysis reports.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_FOLDED_ROWS = Path(
    "experiments/EX_CSC_dataset/folded_fault_localization/fl_combined_3exp_144tasks/folded_replay_rows.jsonl"
)
DEFAULT_BUDGET_ROWS = Path(
    "experiments/EX_CSC_dataset/folded_fault_localization/budget_matched/budget_matched_rows.jsonl"
)
DEFAULT_OUTPUT_DIR = Path(
    "experiments/EX_CSC_dataset/folded_fault_localization/poor_rank_analysis"
)


def main() -> int:
    args = _build_parser().parse_args()
    root = args.project_root.resolve()
    folded_rows_path = _resolve_path(root, args.folded_rows)
    budget_rows_path = _resolve_path(root, args.budget_rows)
    output_dir = _resolve_path(root, args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    folded_rows = _read_jsonl(folded_rows_path)
    budget_rows = _read_jsonl(budget_rows_path) if budget_rows_path.exists() else []
    budget_by_id = {str(r.get("mutant_id")): r for r in budget_rows}

    records = [
        _build_record(row, budget_by_id.get(str(row.get("mutant_id"))),
                      args.top_k)
        for row in folded_rows
        if row.get("status") == "evaluated"
    ]
    records = [r for r in records if r is not None]

    poor_records = [r for r in records if _is_poor_record(r, args.top_k)]
    poor_records.sort(key=_poor_sort_key)

    _write_jsonl(output_dir / "poor_rank_tasks.jsonl", poor_records)
    _write_csv(output_dir / "poor_rank_tasks.csv", poor_records)
    _write_markdown(output_dir / "poor_rank_analysis.md", records, poor_records,
                    folded_rows_path, budget_rows_path, args.top_k)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Screen folded FL experiment logs for poor-ranked tasks.",
    )
    p.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="CSC_EXPANDED project root. Defaults to this script's directory.",
    )
    p.add_argument(
        "--folded-rows",
        type=Path,
        default=DEFAULT_FOLDED_ROWS,
        help="folded_replay_rows.jsonl path, relative to project root unless absolute.",
    )
    p.add_argument(
        "--budget-rows",
        type=Path,
        default=DEFAULT_BUDGET_ROWS,
        help="budget_matched_rows.jsonl path, relative to project root unless absolute.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory, relative to project root unless absolute.",
    )
    p.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Treat composite misses within Top-K as poor-ranked tasks.",
    )
    return p


def _resolve_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}") from exc
    return rows


def _parse_topk(value: Any) -> dict[str, bool]:
    if isinstance(value, dict):
        return {str(k): bool(v) for k, v in value.items()}
    if isinstance(value, str) and value:
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return {str(k): bool(v) for k, v in parsed.items()}
    return {}


def _build_record(
    row: dict[str, Any],
    budget_row: dict[str, Any] | None,
    top_k: int,
) -> dict[str, Any] | None:
    mutant_id = str(row.get("mutant_id", ""))
    raw_report = Path(str(row.get("raw_report", "")))
    aggregated_report = Path(str(row.get("aggregated_report", "")))
    eval_report = Path(str(row.get("eval_report", "")))

    raw = _read_json(raw_report)
    aggregated = _read_json(aggregated_report)
    evaluation = _read_json(eval_report)

    composite_key = "condition_node_folded_edge_partition"
    composite_topk = _parse_topk(row.get(f"{composite_key}_topk"))
    condition_topk = _parse_topk(row.get("condition_node_topk"))
    edge_topk = _parse_topk(row.get("interval_folded_edge_partition_topk"))

    budget_top = {}
    primary_line = None
    if budget_row:
        primary_line = budget_row.get("primary_line")
        for k in [1, 2, 3]:
            budget_top[f"top{k}_budget"] = budget_row.get(f"top{k}_budget")
            budget_top[f"top{k}_folded_hit"] = budget_row.get(f"top{k}_folded_hit")
            budget_top[f"top{k}_sfl_hit"] = budget_row.get(f"top{k}_sfl_hit")

    eval_metrics = evaluation.get("metrics", {}) if isinstance(evaluation, dict) else {}
    composite_eval = eval_metrics.get("aggregated.composite.condition_or_interval", {})
    condition_eval = eval_metrics.get("aggregated.condition_node", {})
    edge_eval = eval_metrics.get("aggregated.interval.folded_edge_partition", {})

    record = {
        "mutant_id": mutant_id,
        "subject": row.get("subject"),
        "operator": row.get("operator"),
        "fault_kind": row.get("fault_kind"),
        "fault_category": row.get("fault_category"),
        "primary_line": primary_line,
        "F_total": row.get("F_total"),
        "P_total": row.get("P_total"),
        "unstable_segment_variants": row.get("unstable_segment_variants"),
        "condition_candidates": row.get("condition_candidates"),
        "edge_partition_candidates": row.get("interval_folded_edge_partition_prediction_count"),
        "composite_hit": row.get(f"{composite_key}_hit"),
        "composite_best_rank": row.get(f"{composite_key}_best_rank"),
        "composite_topk": composite_topk,
        "condition_hit": row.get("condition_node_hit"),
        "condition_best_rank": row.get("condition_node_best_rank"),
        "condition_topk": condition_topk,
        "edge_hit": row.get("interval_folded_edge_partition_hit"),
        "edge_best_rank": row.get("interval_folded_edge_partition_best_rank"),
        "edge_topk": edge_topk,
        "budget": budget_top,
        "budget_gap": _budget_gap_flags(budget_top),
        "top_conditions": _top_conditions(aggregated, limit=5),
        "top_edges": _top_edges(aggregated, limit=5),
        "hit_prediction": {
            "composite": composite_eval.get("hit_prediction"),
            "condition": condition_eval.get("hit_prediction"),
            "edge": edge_eval.get("hit_prediction"),
        },
        "hit_lines": {
            "composite": composite_eval.get("hit_lines"),
            "condition": condition_eval.get("hit_lines"),
            "edge": edge_eval.get("hit_lines"),
        },
        "raw_summary": raw.get("summary", {}) if isinstance(raw, dict) else {},
        "raw_report": str(raw_report),
        "aggregated_report": str(aggregated_report),
        "eval_report": str(eval_report),
    }
    record["poor_reasons"] = _poor_reasons(record, top_k=top_k)
    return record


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _budget_gap_flags(budget: dict[str, Any]) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    for k in [1, 2, 3]:
        folded_hit = budget.get(f"top{k}_folded_hit")
        sfl_hit = budget.get(f"top{k}_sfl_hit")
        flags[f"top{k}_sfl_hits_folded_misses"] = bool(sfl_hit) and not bool(folded_hit)
    return flags


def _top_conditions(aggregated: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    items = aggregated.get("aggregated_condition_node_ranking", [])
    return [_pick_condition_fields(item) for item in items[:limit]]


def _pick_condition_fields(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": item.get("rank"),
        "line": item.get("line"),
        "condition": item.get("condition"),
        "risk_score": item.get("risk_score"),
        "fail_count": item.get("fail_count"),
        "pass_count": item.get("pass_count"),
        "failure_density": item.get("failure_density"),
        "support_count": item.get("support_count"),
    }


def _top_edges(aggregated: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    rankings = aggregated.get("aggregated_interval_rankings", {})
    items = rankings.get("folded_edge_partition", [])
    return [_pick_edge_fields(item) for item in items[:limit]]


def _pick_edge_fields(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": item.get("rank"),
        "kind": item.get("kind"),
        "statement_lines": item.get("statement_lines"),
        "region_size": item.get("region_size"),
        "from_line": item.get("from_line"),
        "from_condition": item.get("from_condition"),
        "outcome": item.get("outcome"),
        "to_line": item.get("to_line"),
        "to_condition": item.get("to_condition"),
        "risk_score": item.get("risk_score"),
        "fail_count": item.get("fail_count"),
        "pass_count": item.get("pass_count"),
        "failure_density": item.get("failure_density"),
        "support_count": item.get("support_count"),
    }


def _is_poor_record(record: dict[str, Any], top_k: int) -> bool:
    return bool(_poor_reasons(record, top_k))


def _poor_reasons(record: dict[str, Any], top_k: int) -> list[str]:
    reasons: list[str] = []
    top_key = f"top{top_k}"
    if not record.get("composite_hit"):
        reasons.append("composite_no_hit")
    elif not record.get("composite_topk", {}).get(top_key):
        reasons.append(f"composite_miss_{top_key}")

    fault_category = record.get("fault_category")
    if fault_category == "condition" and not record.get("condition_topk", {}).get(top_key):
        reasons.append(f"condition_fault_condition_miss_{top_key}")
    if fault_category == "statement" and not record.get("edge_topk", {}).get(top_key):
        reasons.append(f"statement_fault_edge_miss_{top_key}")

    for key, value in record.get("budget_gap", {}).items():
        if value:
            reasons.append(key)
    return reasons


def _poor_sort_key(record: dict[str, Any]) -> tuple[int, int, int, str]:
    no_hit = 0 if not record.get("composite_hit") else 1
    top3 = 0 if not record.get("composite_topk", {}).get("top3") else 1
    best_rank = record.get("composite_best_rank")
    best_rank_value = 999999 if best_rank is None else int(best_rank)
    return (no_hit, top3, best_rank_value, str(record.get("mutant_id")))


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = [
        "mutant_id",
        "subject",
        "fault_category",
        "operator",
        "primary_line",
        "F_total",
        "P_total",
        "composite_hit",
        "composite_best_rank",
        "condition_best_rank",
        "edge_best_rank",
        "top1_budget",
        "top1_folded_hit",
        "top1_sfl_hit",
        "top2_budget",
        "top2_folded_hit",
        "top2_sfl_hit",
        "top3_budget",
        "top3_folded_hit",
        "top3_sfl_hit",
        "poor_reasons",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            budget = record.get("budget", {})
            writer.writerow({
                "mutant_id": record.get("mutant_id"),
                "subject": record.get("subject"),
                "fault_category": record.get("fault_category"),
                "operator": record.get("operator"),
                "primary_line": record.get("primary_line"),
                "F_total": record.get("F_total"),
                "P_total": record.get("P_total"),
                "composite_hit": record.get("composite_hit"),
                "composite_best_rank": record.get("composite_best_rank"),
                "condition_best_rank": record.get("condition_best_rank"),
                "edge_best_rank": record.get("edge_best_rank"),
                "top1_budget": budget.get("top1_budget"),
                "top1_folded_hit": budget.get("top1_folded_hit"),
                "top1_sfl_hit": budget.get("top1_sfl_hit"),
                "top2_budget": budget.get("top2_budget"),
                "top2_folded_hit": budget.get("top2_folded_hit"),
                "top2_sfl_hit": budget.get("top2_sfl_hit"),
                "top3_budget": budget.get("top3_budget"),
                "top3_folded_hit": budget.get("top3_folded_hit"),
                "top3_sfl_hit": budget.get("top3_sfl_hit"),
                "poor_reasons": ";".join(record.get("poor_reasons", [])),
            })


def _write_markdown(
    path: Path,
    records: list[dict[str, Any]],
    poor_records: list[dict[str, Any]],
    folded_rows_path: Path,
    budget_rows_path: Path,
    top_k: int,
) -> None:
    reason_counts = Counter(
        reason for record in poor_records for reason in record.get("poor_reasons", [])
    )
    by_category = defaultdict(list)
    for record in poor_records:
        by_category[str(record.get("fault_category"))].append(record)

    lines: list[str] = []
    lines.append("# Poor-Rank Fault Localization Analysis")
    lines.append("")
    lines.append(f"- Folded rows: `{folded_rows_path}`")
    lines.append(f"- Budget rows: `{budget_rows_path}`")
    lines.append(f"- Evaluated records: {len(records)}")
    lines.append(f"- Poor-ranked records: {len(poor_records)}")
    lines.append(f"- Poor criterion: composite miss within Top-{top_k}, "
                 "category-specific miss within Top-K, or budget-matched SFL hit while folded misses")
    lines.append("")

    lines.append("## Poor Reasons")
    lines.append("")
    lines.append("| Reason | Count |")
    lines.append("|--------|------:|")
    for reason, count in reason_counts.most_common():
        lines.append(f"| `{reason}` | {count} |")
    lines.append("")

    lines.append("## Poor Records by Fault Category")
    lines.append("")
    lines.append("| Category | Count | Mean F_total | Mean P_total |")
    lines.append("|----------|------:|-------------:|-------------:|")
    for category, items in sorted(by_category.items()):
        f_vals = [int(r.get("F_total") or 0) for r in items]
        p_vals = [int(r.get("P_total") or 0) for r in items]
        lines.append(
            f"| {category} | {len(items)} | {_safe_mean(f_vals):.2f} | {_safe_mean(p_vals):.2f} |"
        )
    lines.append("")

    lines.append("## Worst Tasks")
    lines.append("")
    lines.append("| Mutant | Category | Op | Fault Line | F/P | Composite Rank | Cond Rank | Edge Rank | Reasons |")
    lines.append("|--------|----------|----|-----------:|-----|---------------:|----------:|----------:|---------|")
    for record in poor_records[:30]:
        lines.append(
            "| {mutant} | {cat} | {op} | {line} | {fp} | {crank} | {cond} | {edge} | {reasons} |".format(
                mutant=record.get("mutant_id"),
                cat=record.get("fault_category"),
                op=record.get("operator"),
                line=_fmt(record.get("primary_line")),
                fp=f"{_fmt(record.get('F_total'))}/{_fmt(record.get('P_total'))}",
                crank=_fmt(record.get("composite_best_rank")),
                cond=_fmt(record.get("condition_best_rank")),
                edge=_fmt(record.get("edge_best_rank")),
                reasons=", ".join(f"`{r}`" for r in record.get("poor_reasons", [])),
            )
        )
    lines.append("")

    lines.append("## Concrete Case Snapshots")
    lines.append("")
    for record in poor_records[:10]:
        lines.extend(_case_snapshot(record))
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def _safe_mean(values: list[int]) -> float:
    return mean(values) if values else 0.0


def _fmt(value: Any) -> str:
    return "—" if value is None else str(value)


def _case_snapshot(record: dict[str, Any]) -> list[str]:
    lines = [
        f"### {record.get('mutant_id')}",
        "",
        f"- Category/operator: `{record.get('fault_category')}` / `{record.get('operator')}`",
        f"- Ground-truth line: `{_fmt(record.get('primary_line'))}`",
        f"- Failed/passed tests: `{_fmt(record.get('F_total'))}` / `{_fmt(record.get('P_total'))}`",
        f"- Composite best rank: `{_fmt(record.get('composite_best_rank'))}`",
        f"- Reasons: {', '.join(f'`{r}`' for r in record.get('poor_reasons', []))}",
        "",
        "Top condition candidates:",
        "",
    ]
    lines.extend(_ranking_table(record.get("top_conditions", []), condition=True))
    lines.append("")
    lines.append("Top edge-partition candidates:")
    lines.append("")
    lines.extend(_ranking_table(record.get("top_edges", []), condition=False))
    return lines


def _ranking_table(items: list[dict[str, Any]], condition: bool) -> list[str]:
    if not items:
        return ["No candidates."]
    if condition:
        lines = [
            "| Rank | Line | Condition | Risk | F/P | Density |",
            "|-----:|-----:|-----------|-----:|-----|--------:|",
        ]
        for item in items:
            lines.append(
                f"| {item.get('rank')} | {item.get('line')} | `{item.get('condition')}` | "
                f"{_num(item.get('risk_score'))} | {item.get('fail_count')}/{item.get('pass_count')} | "
                f"{_num(item.get('failure_density'))} |"
            )
        return lines
    lines = [
        "| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |",
        "|-----:|------|-------|------|---------|----|-----:|-----|--------:|",
    ]
    for item in items:
        lines.append(
            f"| {item.get('rank')} | `{item.get('kind')}` | `{item.get('statement_lines')}` | "
            f"`{item.get('from_line')}:{item.get('from_condition')}` | `{item.get('outcome')}` | "
            f"`{item.get('to_line')}:{item.get('to_condition')}` | {_num(item.get('risk_score'))} | "
            f"{item.get('fail_count')}/{item.get('pass_count')} | {_num(item.get('failure_density'))} |"
        )
    return lines


def _num(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.4f}"
    return "—"


if __name__ == "__main__":
    raise SystemExit(main())
