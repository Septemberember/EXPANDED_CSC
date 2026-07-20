"""Summarize fault-localization evaluation reports.

The summarizer is read-only. It consumes ``mutants_manifest.jsonl`` plus
existing ``fault_localization_eval.json`` files and writes flat experiment
tables for paper-facing analysis.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Optional


DEFAULT_EVAL_GLOB = "**/fault_localization_eval.json"
DEFAULT_TOP_K = (1, 3, 5, 10)
FAULT_CATEGORY_LABELS = {
    "condition": "Condition/Control-Flow Mutants",
    "statement": "Statement/Data-Flow Mutants",
}
CSV_FIELDS = [
    "status",
    "mutant_id",
    "subject",
    "operator",
    "fault_kind",
    "fault_category",
    "mutant_file",
    "primary_file",
    "primary_line",
    "evaluation_report",
    "duplicate_report_count",
    "strategy",
    "target_type",
    "prediction_count",
    "hit",
    "best_rank",
    "top1_hit",
    "top3_hit",
    "top5_hit",
    "top10_hit",
    "region_size_average",
    "region_size_max",
    "region_size_top1",
    "region_size_hit",
    "region_size_top1_average",
    "region_size_top3_average",
    "region_size_top5_average",
    "region_size_top10_average",
    "hit_item_region_size",
    "cumulative_inspection_region_at_first_hit",
    "inspection_region_top1",
    "inspection_region_top3",
    "inspection_region_top5",
    "inspection_region_top10",
    "hit_lines",
    "notes",
]


def discover_evaluation_reports(results_root: str | Path,
                                pattern: str = DEFAULT_EVAL_GLOB) -> list[Path]:
    """Find evaluation reports under ``results_root``."""

    root = Path(results_root)
    if not root.exists():
        return []
    return sorted(path for path in root.glob(pattern) if path.is_file())


def load_json_report(path: str | Path) -> dict[str, Any]:
    """Load one JSON report."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def summarize_fault_localization_results(manifest_records: list[dict[str, Any]],
                                         evaluation_paths: Iterable[str | Path],
                                         top_k: Iterable[int] = DEFAULT_TOP_K) -> dict[str, Any]:
    """Build a flat row table and aggregate summary."""

    normalized_top_k = sorted({int(k) for k in top_k if int(k) > 0})
    evaluation_path_list = [Path(path) for path in evaluation_paths]
    manifest_by_id = _manifest_index(manifest_records)
    report_index, invalid_rows = _evaluation_report_index(evaluation_path_list, manifest_by_id, normalized_top_k)

    rows: list[dict[str, Any]] = []
    for record in manifest_records:
        mutant_id = str(record.get("mutant_id") or "")
        selected = report_index.get(mutant_id)
        if selected is None:
            rows.append(_missing_result_row(record, normalized_top_k))
            continue
        report_path, report, duplicate_count = selected
        rows.extend(_rows_from_evaluation_report(
            report,
            manifest_record=record,
            evaluation_report=report_path,
            duplicate_count=duplicate_count,
            top_k=normalized_top_k,
        ))

    rows.extend(invalid_rows)
    summary = _build_summary(rows, len(manifest_records), len(evaluation_path_list), normalized_top_k)
    return {
        "summary": summary,
        "rows": rows,
    }


def write_jsonl_rows(rows: list[dict[str, Any]], output_path: str | Path) -> None:
    """Write flat rows as JSONL."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def write_csv_rows(rows: list[dict[str, Any]], output_path: str | Path) -> None:
    """Write flat rows as CSV."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = _csv_fields(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field)) for field in fields})


def write_markdown_summary(report: dict[str, Any], output_path: str | Path) -> None:
    """Write a compact Markdown summary."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_markdown_summary(report), encoding="utf-8")


def _evaluation_report_index(evaluation_paths: Iterable[str | Path],
                             manifest_by_id: dict[str, dict[str, Any]],
                             top_k: list[int]) -> tuple[dict[str, tuple[Path, dict[str, Any], int]],
                                                        list[dict[str, Any]]]:
    grouped: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    invalid_rows: list[dict[str, Any]] = []

    for raw_path in evaluation_paths:
        path = Path(raw_path)
        try:
            report = load_json_report(path)
        except Exception as exc:
            invalid_rows.append(_invalid_report_row(path, exc, top_k))
            continue
        mutant_id = str(report.get("mutant_id") or "")
        if not mutant_id:
            invalid_rows.append(_invalid_report_row(path, ValueError("missing mutant_id"), top_k))
            continue
        if mutant_id not in manifest_by_id:
            invalid_rows.extend(_orphan_rows(report, path, top_k))
            continue
        grouped.setdefault(mutant_id, []).append((path, report))

    index: dict[str, tuple[Path, dict[str, Any], int]] = {}
    for mutant_id, reports in grouped.items():
        selected = _select_report(reports)
        index[mutant_id] = (selected[0], selected[1], len(reports))
    return index, invalid_rows


def _select_report(reports: list[tuple[Path, dict[str, Any]]]) -> tuple[Path, dict[str, Any]]:
    return max(
        reports,
        key=lambda item: (
            item[0].stat().st_mtime if item[0].exists() else 0.0,
            str(item[0]),
        ),
    )


def _rows_from_evaluation_report(report: dict[str, Any],
                                 manifest_record: dict[str, Any],
                                 evaluation_report: Path,
                                 duplicate_count: int,
                                 top_k: list[int]) -> list[dict[str, Any]]:
    metrics = report.get("metrics", {})
    if not metrics:
        return [_base_row(
            manifest_record,
            status="no_metrics",
            evaluation_report=evaluation_report,
            duplicate_count=duplicate_count,
            top_k=top_k,
            notes="evaluation report contains no strategy metrics",
        )]

    rows = []
    for strategy, item in sorted(metrics.items()):
        row = _base_row(
            manifest_record,
            status="evaluated",
            evaluation_report=evaluation_report,
            duplicate_count=duplicate_count,
            top_k=top_k,
        )
        region_size = item.get("region_size", {})
        row.update({
            "strategy": strategy,
            "target_type": item.get("target_type"),
            "prediction_count": item.get("prediction_count"),
            "hit": bool(item.get("hit")),
            "best_rank": item.get("best_rank"),
            "hit_lines": item.get("hit_lines", []),
            "region_size_average": region_size.get("average"),
            "region_size_max": region_size.get("max"),
            "region_size_top1": region_size.get("top1"),
            "region_size_hit": region_size.get("hit"),
        })
        topk = item.get("topk", {})
        topk_average = region_size.get("topk_average", {})
        inspection_region = item.get("inspection_region", {})
        inspection_topk = inspection_region.get("topk", {})
        row["hit_item_region_size"] = item.get("hit_item_region_size", region_size.get("hit"))
        row["cumulative_inspection_region_at_first_hit"] = inspection_region.get("at_first_hit")
        for k in top_k:
            row[f"top{k}_hit"] = bool(topk.get(f"top{k}", False))
            row[f"region_size_top{k}_average"] = topk_average.get(f"top{k}")
            row[f"inspection_region_top{k}"] = inspection_topk.get(f"top{k}")
        rows.append(row)
    return rows


def _missing_result_row(record: dict[str, Any], top_k: list[int]) -> dict[str, Any]:
    return _base_row(
        record,
        status="missing_result",
        evaluation_report=None,
        duplicate_count=0,
        top_k=top_k,
        notes="no fault_localization_eval.json found for this mutant",
    )


def _invalid_report_row(path: Path, exc: Exception, top_k: list[int]) -> dict[str, Any]:
    row = _empty_row(top_k)
    row.update({
        "status": "invalid_report",
        "evaluation_report": str(path),
        "notes": str(exc),
    })
    return row


def _orphan_rows(report: dict[str, Any], path: Path, top_k: list[int]) -> list[dict[str, Any]]:
    record = {
        "mutant_id": report.get("mutant_id"),
        "mutant_file": report.get("mutant_file"),
        "operator": report.get("operator"),
        "fault_kind": report.get("fault_kind"),
        "ground_truth": report.get("ground_truth", {}),
    }
    rows = _rows_from_evaluation_report(
        report,
        manifest_record=record,
        evaluation_report=path,
        duplicate_count=1,
        top_k=top_k,
    )
    for row in rows:
        row["status"] = "orphan_result"
        row["notes"] = "evaluation report mutant_id is not present in manifest"
    return rows


def _base_row(record: dict[str, Any],
              status: str,
              evaluation_report: Optional[Path],
              duplicate_count: int,
              top_k: list[int],
              notes: str = "") -> dict[str, Any]:
    row = _empty_row(top_k)
    ground_truth = record.get("ground_truth", {}) if isinstance(record.get("ground_truth"), dict) else {}
    row.update({
        "status": status,
        "mutant_id": record.get("mutant_id"),
        "subject": record.get("subject"),
        "operator": record.get("operator") or ground_truth.get("operator"),
        "fault_kind": record.get("fault_kind"),
        "fault_category": record.get("fault_category") or ground_truth.get("fault_category"),
        "mutant_file": record.get("mutant_file"),
        "primary_file": ground_truth.get("primary_file"),
        "primary_line": ground_truth.get("primary_line"),
        "evaluation_report": str(evaluation_report) if evaluation_report else None,
        "duplicate_report_count": duplicate_count,
        "notes": notes,
    })
    return row


def _empty_row(top_k: list[int]) -> dict[str, Any]:
    row = {
        field: None
        for field in CSV_FIELDS
    }
    for k in top_k:
        row.setdefault(f"top{k}_hit", None)
        row.setdefault(f"region_size_top{k}_average", None)
    row["hit_lines"] = []
    row["duplicate_report_count"] = 0
    row["notes"] = ""
    return row


def _manifest_index(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index = {}
    for record in records:
        mutant_id = record.get("mutant_id")
        if mutant_id:
            index[str(mutant_id)] = record
    return index


def _build_summary(rows: list[dict[str, Any]],
                   manifest_count: int,
                   evaluation_report_count: int,
                   top_k: list[int]) -> dict[str, Any]:
    evaluated_rows = [row for row in rows if row.get("status") == "evaluated"]
    missing_mutants = {
        row.get("mutant_id")
        for row in rows
        if row.get("status") == "missing_result"
    }
    strategies = {}
    for strategy in sorted({row.get("strategy") for row in evaluated_rows if row.get("strategy")}):
        strategy_rows = [row for row in evaluated_rows if row.get("strategy") == strategy]
        strategies[strategy] = _strategy_summary(strategy_rows, top_k)
    fault_categories = {}
    for category in sorted({
        str(row.get("fault_category") or "<missing>")
        for row in evaluated_rows
    }):
        category_rows = [
            row for row in evaluated_rows
            if str(row.get("fault_category") or "<missing>") == category
        ]
        category_strategies = {}
        for strategy in sorted({row.get("strategy") for row in category_rows if row.get("strategy")}):
            strategy_rows = [row for row in category_rows if row.get("strategy") == strategy]
            category_strategies[strategy] = _strategy_summary(strategy_rows, top_k)
        fault_categories[category] = {
            "label": FAULT_CATEGORY_LABELS.get(category, category),
            "mutant_count": len({row.get("mutant_id") for row in category_rows}),
            "row_count": len(category_rows),
            "strategies": category_strategies,
        }
    return {
        "manifest_count": manifest_count,
        "evaluation_report_count": evaluation_report_count,
        "row_count": len(rows),
        "evaluated_row_count": len(evaluated_rows),
        "evaluated_mutant_count": len({row.get("mutant_id") for row in evaluated_rows}),
        "missing_result_count": len(missing_mutants),
        "invalid_report_count": sum(1 for row in rows if row.get("status") == "invalid_report"),
        "orphan_result_count": sum(1 for row in rows if row.get("status") == "orphan_result"),
        "top_k": top_k,
        "strategies": strategies,
        "fault_categories": fault_categories,
    }


def _strategy_summary(rows: list[dict[str, Any]], top_k: list[int]) -> dict[str, Any]:
    hit_rows = [row for row in rows if row.get("hit")]
    summary = {
        "row_count": len(rows),
        "hit_count": len(hit_rows),
        "hit_rate": _rate(len(hit_rows), len(rows)),
        "mean_best_rank": _average([
            row.get("best_rank")
            for row in hit_rows
            if row.get("best_rank") is not None
        ]),
        "mean_region_size_average": _average([
            row.get("region_size_average")
            for row in rows
            if row.get("region_size_average") is not None
        ]),
        "mean_hit_region_size": _average([
            row.get("region_size_hit")
            for row in hit_rows
            if row.get("region_size_hit") is not None
        ]),
        "mean_hit_item_region_size": _average([
            row.get("hit_item_region_size")
            for row in hit_rows
            if row.get("hit_item_region_size") is not None
        ]),
        "mean_cumulative_inspection_region_at_first_hit": _average([
            row.get("cumulative_inspection_region_at_first_hit")
            for row in hit_rows
            if row.get("cumulative_inspection_region_at_first_hit") is not None
        ]),
    }
    for k in top_k:
        key = f"top{k}_hit"
        count = sum(1 for row in rows if row.get(key))
        summary[f"top{k}_hit_count"] = count
        summary[f"top{k}_hit_rate"] = _rate(count, len(rows))
        summary[f"mean_top{k}_inspection_region"] = _average([
            row.get(f"inspection_region_top{k}")
            for row in rows
            if row.get(f"inspection_region_top{k}") is not None
        ])
    return summary


def _markdown_summary(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Fault Localization Summary",
        "",
        "## Overview",
        "",
        f"- Manifest mutants: {summary['manifest_count']}",
        f"- Evaluation reports discovered: {summary['evaluation_report_count']}",
        f"- Evaluated mutants: {summary['evaluated_mutant_count']}",
        f"- Missing-result mutants: {summary['missing_result_count']}",
        f"- Invalid reports: {summary['invalid_report_count']}",
        f"- Orphan reports: {summary['orphan_result_count']}",
        "",
        "## Strategy Summary",
        "",
    ]
    top_k = summary.get("top_k", list(DEFAULT_TOP_K))
    _append_strategy_table(lines, summary.get("strategies", {}), top_k)
    fault_categories = summary.get("fault_categories", {})
    if fault_categories:
        lines.extend([
            "",
            "## Strategy Summary by Fault Category",
            "",
        ])
        for category, item in fault_categories.items():
            label = item.get("label") or FAULT_CATEGORY_LABELS.get(category, category)
            lines.extend([
                f"### {label}",
                "",
                f"- Fault category: `{category}`",
                f"- Mutants: {item.get('mutant_count', 0)}",
                f"- Strategy rows: {item.get('row_count', 0)}",
                "",
            ])
            _append_strategy_table(lines, item.get("strategies", {}), top_k)
            lines.append("")
    return "\n".join(lines)


def _append_strategy_table(lines: list[str],
                           strategies: dict[str, dict[str, Any]],
                           top_k: list[int]) -> None:
    headers = [
        "Strategy",
        "Rows",
        "Hit Rate",
        *[f"Top-{k}" for k in top_k],
        "Mean Best Rank",
        "Mean Region Size",
        "Mean Hit Item Region",
        "Mean Cumulative Region at First Hit",
    ]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for strategy, item in strategies.items():
        values = [
            strategy,
            str(item.get("row_count", 0)),
            _format_rate(item.get("hit_rate")),
            *[_format_rate(item.get(f"top{k}_hit_rate")) for k in top_k],
            _format_number(item.get("mean_best_rank")),
            _format_number(item.get("mean_region_size_average")),
            _format_number(item.get("mean_hit_item_region_size")),
            _format_number(item.get("mean_cumulative_inspection_region_at_first_hit")),
        ]
        lines.append("| " + " | ".join(values) + " |")


def _csv_fields(rows: list[dict[str, Any]]) -> list[str]:
    fields = list(CSV_FIELDS)
    extra = sorted({
        key
        for row in rows
        for key in row
        if key not in fields
    })
    return fields + extra


def _csv_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True)
    return value


def _rate(count: int, total: int) -> Optional[float]:
    if total <= 0:
        return None
    return count / total


def _average(values: list[Any]) -> Optional[float]:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return sum(numeric) / len(numeric)


def _format_rate(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.3f}"


def _format_number(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.3f}"
