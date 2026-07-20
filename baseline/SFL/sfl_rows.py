"""Generate SFL row-level output (JSONL/CSV) compatible with CCT aggregation.

Produces flat rows in the same semantic format as CCT ``fault_localization_rows.jsonl``,
so that downstream aggregators can merge SFL and CCT results into a single table.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .evaluate import acceptable_line_set
from .formulas import FORMULA_NAMES

DEFAULT_TOP_K = (1, 3, 5, 10)
FORMULA_LABELS = {
    "ochiai": "SFL Ochiai",
    "dstar": "SFL DStar (e=2)",
    "tarantula": "SFL Tarantula",
    "barinel": "SFL Barinel",
    "op2": "SFL Op2",
}


def generate_sfl_rows(sfl_report_path: str | Path,
                      manifest_record: dict[str, Any],
                      top_k: tuple[int, ...] = DEFAULT_TOP_K) -> list[dict[str, Any]]:
    """Generate flat SFL localization rows for a single mutant.

    Args:
        sfl_report_path: Path to ``sfl_localization.json``.
        manifest_record: The matching mutant manifest entry.
        top_k: Top-k thresholds to evaluate (default 1, 3, 5, 10).

    Returns:
        One row per SFL formula.  Rows carry the same field names as the
        CCT ``fault_localization_rows`` format so they can be concatenated.
    """
    sfl = json.loads(Path(sfl_report_path).read_text(encoding="utf-8"))
    rankings = sfl.get("rankings", {})
    summary = sfl.get("summary", {})

    acceptable = acceptable_line_set(manifest_record)
    sorted_top_k = sorted(int(k) for k in top_k if int(k) > 0)
    prediction_count = summary.get("entities", 0)

    rows: list[dict[str, Any]] = []
    for formula in rankings:
        records = rankings[formula]
        hit, best_rank, topk_hits, hit_lines = _evaluate_line_ranking(
            records, acceptable, sorted_top_k
        )

        row = {
            # Identification
            "method_family": "SFL",
            "strategy": f"sfl.{formula}",
            "target_type": "line",

            # Mutant metadata (from manifest)
            "status": "evaluated",
            "mutant_id": manifest_record.get("mutant_id"),
            "subject": manifest_record.get("subject"),
            "operator": manifest_record.get("operator"),
            "fault_kind": manifest_record.get("fault_kind"),
            "fault_category": manifest_record.get("fault_category",
                                                   manifest_record.get("fault_kind")),
            "mutant_file": manifest_record.get("mutant_file"),
            "primary_file": manifest_record.get("ground_truth", {}).get("primary_file"),
            "primary_line": manifest_record.get("ground_truth", {}).get("primary_line"),

            # Hit metrics
            "hit": hit,
            "best_rank": best_rank,
            "top1_hit": topk_hits.get(1, False),
            "top3_hit": topk_hits.get(3, False),
            "top5_hit": topk_hits.get(5, False),
            "top10_hit": topk_hits.get(10, False),

            # Region / inspection metrics (SFL = line-level)
            "prediction_count": prediction_count,
            "region_size_average": 1 if prediction_count else None,
            "region_size_max": 1 if prediction_count else None,
            "region_size_hit": 1 if hit else None,
            "region_size_top1": 1 if prediction_count >= 1 else 0,
            "region_size_top1_average": 1 if prediction_count >= 1 else 0,
            "region_size_top3_average": 1 if prediction_count >= 1 else 0,
            "region_size_top5_average": 1 if prediction_count >= 1 else 0,
            "region_size_top10_average": 1 if prediction_count >= 1 else 0,
            "hit_item_region_size": 1 if hit else None,
            "cumulative_inspection_region_at_first_hit": best_rank if hit else None,
            "inspection_region_top1": 1 if prediction_count >= 1 else 0,
            "inspection_region_top3": min(3, prediction_count),
            "inspection_region_top5": min(5, prediction_count),
            "inspection_region_top10": min(10, prediction_count),
            "hit_lines": hit_lines,

            # SFL-specific metadata
            "sfl_entities": prediction_count,
            "sfl_test_cases": summary.get("test_cases"),
            "sfl_failed_cases": summary.get("failed_cases"),
            "sfl_passed_cases": summary.get("passed_cases"),
            "sfl_coverage_ratio": summary.get("coverage_ratio"),
            "sfl_total_s": summary.get("timings", {}).get("total_s"),
        }

        # Strategy display name (for reports)
        row["strategy_label"] = FORMULA_LABELS.get(formula, f"SFL {formula}")
        row.setdefault("notes", "")

        rows.append(row)

    return rows


def generate_no_metrics_row(manifest_record: dict[str, Any],
                            reason: str = "",
                            formula: str = "ochiai") -> dict[str, Any]:
    """Generate a ``no_metrics`` row for a mutant that cannot be evaluated by SFL.

    Use this when the mutant has zero TBFV failures (all pass / all skipped),
    or when the SFL report is missing / could not be generated.
    """
    return {
        "method_family": "SFL",
        "strategy": f"sfl.{formula}",
        "strategy_label": FORMULA_LABELS.get(formula, f"SFL {formula}"),
        "target_type": "line",
        "status": "no_metrics",
        "mutant_id": manifest_record.get("mutant_id"),
        "subject": manifest_record.get("subject"),
        "operator": manifest_record.get("operator"),
        "fault_kind": manifest_record.get("fault_kind"),
        "fault_category": manifest_record.get("fault_category",
                                               manifest_record.get("fault_kind")),
        "mutant_file": manifest_record.get("mutant_file"),
        "primary_file": manifest_record.get("ground_truth", {}).get("primary_file"),
        "primary_line": manifest_record.get("ground_truth", {}).get("primary_line"),
        "hit": False,
        "best_rank": None,
        "top1_hit": False, "top3_hit": False, "top5_hit": False, "top10_hit": False,
        "prediction_count": 0,
        "region_size_average": None,
        "region_size_max": None,
        "region_size_hit": None,
        "region_size_top1": 0,
        "region_size_top1_average": 0,
        "region_size_top3_average": 0,
        "region_size_top5_average": 0,
        "region_size_top10_average": 0,
        "hit_item_region_size": None,
        "cumulative_inspection_region_at_first_hit": None,
        "inspection_region_top1": 0, "inspection_region_top3": 0,
        "inspection_region_top5": 0, "inspection_region_top10": 0,
        "hit_lines": [],
        "sfl_entities": 0,
        "sfl_test_cases": None,
        "sfl_failed_cases": None,
        "sfl_passed_cases": None,
        "sfl_coverage_ratio": None,
        "sfl_total_s": None,
        "notes": reason or "no failed/passed TBFV signal for SFL spectrum",
    }


def generate_no_metrics_rows(manifest_record: dict[str, Any],
                             reason: str = "") -> list[dict[str, Any]]:
    """Generate one ``no_metrics`` row per SFL formula for a mutant."""

    return [
        generate_no_metrics_row(manifest_record, reason, formula=formula)
        for formula in FORMULA_NAMES
    ]


def write_rows_jsonl(rows: list[dict[str, Any]], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_rows_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    if not rows:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Collect all field names across all rows (no_metrics rows may have extra fields)
    fieldnames = list(dict.fromkeys(k for row in rows for k in row))
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _evaluate_line_ranking(
    records: list[dict[str, Any]],
    acceptable_lines: set[int],
    top_k: list[int],
) -> tuple[bool, int | None, dict[int, bool], list[int]]:
    """Evaluate a line-level ranking against a set of acceptable lines.

    Returns:
        hit: whether any line was found.
        best_rank: rank of the first hit (None if no hit).
        topk_hits: mapping k -> bool.
        hit_lines: the acceptable lines actually found.
    """
    hits = sorted(
        (r for r in records if r["line"] in acceptable_lines),
        key=lambda r: r["rank"],
    )
    best = hits[0] if hits else None
    best_rank = best["rank"] if best else None
    topk = {}
    for k in sorted(top_k):
        topk[k] = best_rank is not None and best_rank <= k
    hit_lines = sorted({r["line"] for r in hits})
    return best is not None, best_rank, topk, hit_lines
