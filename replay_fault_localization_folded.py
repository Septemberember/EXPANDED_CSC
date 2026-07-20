#!/usr/bin/env python3
"""Replay fold-the-tree fault localization from archived experiment artifacts.

Does NOT re-run CSC, Java, or TBFV.  Reads an archived CCT pickle +
testcases.json + trace JSONL files, then builds a folded localization report
using the three-pass algorithm from :mod:`csc_engine.failure_localization_fold`.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from csc_engine import (
    CCT,
    aggregate_localization_report,
    evaluate_reports,
    load_json_report,
    load_manifest,
    write_aggregated_localization_report,
)
from csc_engine.failure_localization_fold import (
    build_folded_localization_report,
    write_folded_localization_report,
)


def main() -> int:
    args = _build_parser().parse_args()
    experiment_dirs = [Path(d).resolve() for d in args.experiment_dir]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    top_k = _parse_top_k(args.top_k)
    scoring = args.scoring_strategy

    old_combined = args.old_combined_file.resolve() if args.old_combined_file else None

    all_rows: list[dict[str, Any]] = []
    for exp_dir in experiment_dirs:
        all_rows.extend(_replay_directory(exp_dir, output_dir, scoring, top_k))

    if not all_rows:
        print("No mutants processed — check experiment directories.")
        return 1

    _write_outputs(output_dir, all_rows, scoring, top_k, old_combined)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replay fold-the-tree FL from archived experiments.",
    )
    parser.add_argument(
        "--experiment-dir",
        action="append",
        required=True,
        help="Archived experiment directory (repeat for multiple).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Output directory for folded reports and evaluation.",
    )
    parser.add_argument(
        "--scoring-strategy",
        default="coverage_x_purity",
        help="Key into FOLDED_SCORING_REGISTRY.",
    )
    parser.add_argument(
        "--top-k",
        default="1,3,5,10",
        help="Comma-separated top-k values for evaluation.",
    )
    parser.add_argument(
        "--old-combined-file",
        type=Path,
        help=(
            "Path to old combined_cct_fault_localization_rows.jsonl.  "
            "If provided, a comparison_summary.md is generated alongside "
            "the folded results."
        ),
    )
    return parser


def _replay_directory(
    exp_dir: Path,
    output_dir: Path,
    scoring: str,
    top_k: list[int],
) -> list[dict[str, Any]]:
    """Process all mutants found under *exp_dir*."""
    manifest_path = exp_dir / "aggregation_ready" / "mutants_manifest.jsonl"
    if not manifest_path.exists():
        # Try legacy layout: individual mutant dirs directly under exp_dir.
        return _replay_legacy_directory(exp_dir, output_dir, scoring, top_k)

    manifest = load_manifest(manifest_path)
    rows: list[dict[str, Any]] = []
    for record in manifest:
        mutant_id = str(record.get("mutant_id"))
        result_dir = _find_result_dir(exp_dir, mutant_id)
        if result_dir is None:
            rows.append(_skip_row(record, scoring, "missing_result_dir"))
            continue
        rows.append(
            _replay_one_mutant(
                result_dir, record, output_dir / "artifacts" / exp_dir.name,
                scoring, top_k,
            )
        )
    return rows


def _replay_legacy_directory(
    exp_dir: Path,
    output_dir: Path,
    scoring: str,
    top_k: list[int],
) -> list[dict[str, Any]]:
    """Fallback: scan for individual mutant subdirectories."""
    rows: list[dict[str, Any]] = []
    # Look for directories containing a *_cct.pkl file.
    for cct_path in sorted(exp_dir.glob("**/*_cct.pkl")):
        result_dir = cct_path.parent
        mutant_id = result_dir.name
        record = {"mutant_id": mutant_id}
        rows.append(
            _replay_one_mutant(
                result_dir, record, output_dir / "artifacts",
                scoring, top_k,
            )
        )
    return rows


def _find_result_dir(exp_dir: Path, mutant_id: str) -> Path | None:
    """Locate the CSC result directory for *mutant_id*.

    Handles several common directory layouts:
    - Flat:  <exp_dir>/<mutant_id>/*_cct.pkl
    - Suffix: <exp_dir>/*_<mutant_id>/*_cct.pkl
    - Nested: <exp_dir>/artifacts/csc_tmp/<session>_<mutant_id>/<ClassName>/*_cct.pkl
    """
    # Try flat layout.
    for cand in sorted(exp_dir.glob(f"**/{mutant_id}")):
        if cand.is_dir() and list(cand.glob("*_cct.pkl")):
            return cand

    # Try suffix match (handles <session>_<Mutant>_<M#> dirs).
    for cand in sorted(exp_dir.glob(f"**/*_{mutant_id}")):
        if not cand.is_dir():
            continue
        if list(cand.glob("*_cct.pkl")):
            return cand
        # Also check one level deeper (ClassName subdirectory).
        for sub in cand.iterdir():
            if sub.is_dir() and list(sub.glob("*_cct.pkl")):
                return sub

    # Try nested artifacts/csc_tmp layout.
    csc_tmp = exp_dir / "artifacts" / "csc_tmp"
    if csc_tmp.exists():
        for cand in sorted(csc_tmp.glob(f"*_{mutant_id}")):
            if cand.is_dir():
                # cand is <session>_<Mutant>_<M#>, look one level deeper
                for sub in cand.iterdir():
                    if sub.is_dir() and list(sub.glob("*_cct.pkl")):
                        return sub
                # Also check if the CCT is directly inside.
                if list(cand.glob("*_cct.pkl")):
                    return cand

    return None


def _replay_one_mutant(
    result_dir: Path,
    record: dict[str, Any],
    artifact_dir: Path,
    scoring: str,
    top_k: list[int],
) -> dict[str, Any]:
    """Run folded FL on one mutant and return an evaluation row."""
    mutant_id = str(record.get("mutant_id", result_dir.name))
    base = {
        "mutant_id": mutant_id,
        "subject": record.get("subject"),
        "operator": record.get("operator"),
        "fault_kind": record.get("fault_kind"),
        "fault_category": record.get("fault_category"),
        "scoring_strategy": scoring,
    }

    # --- Load CCT ---
    cct_paths = sorted(result_dir.glob("*_cct.pkl"))
    if not cct_paths:
        cct_paths = sorted(result_dir.glob("cct_failure_localization.json"))
    if not cct_paths:
        return base | {"status": "skipped", "reason": "no_cct_pickle"}
    cct = CCT.load_from_file(str(cct_paths[0]))
    if cct is None:
        return base | {"status": "skipped", "reason": "cct_load_failed"}

    # --- Load testcase records with trace paths ---
    tc_path = result_dir / "testcases.json"
    if not tc_path.exists():
        return base | {"status": "skipped", "reason": "no_testcases_json"}
    testcase_records: list[dict[str, Any]] = json.loads(
        tc_path.read_text(encoding="utf-8")
    )
    # Remap trace paths relative to result_dir.
    for tc in testcase_records:
        trace_path = Path(tc.get("trace_path", ""))
        if not trace_path.exists():
            remapped = result_dir / trace_path
            if remapped.exists():
                tc["trace_path"] = str(remapped)
            elif "traces" in trace_path.parts:
                idx = trace_path.parts.index("traces")
                remapped = result_dir.joinpath(*trace_path.parts[idx:])
                if remapped.exists():
                    tc["trace_path"] = str(remapped)

    # --- Build folded report ---
    try:
        report = build_folded_localization_report(cct, testcase_records, scoring)
    except Exception as exc:
        return base | {"status": "skipped", "reason": f"fold_error:{exc}"}

    # --- Write artifacts ---
    out_dir = artifact_dir / mutant_id
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_out = out_dir / "cct_folded_localization.json"
    write_folded_localization_report(report, str(raw_out))

    # Aggregate.
    source_file = _resolve_source_file(record)
    aggregated = aggregate_localization_report(
        report,
        source_file=source_file,
    )
    agg_out = out_dir / "cct_folded_localization_aggregated.json"
    write_aggregated_localization_report(aggregated, str(agg_out))

    # If Refined TBFV detected no failing test cases, this mutant is not a
    # localization task for the folded ranking.  Keep artifacts for inspection
    # but exclude the row from hit-rate denominators.
    if int(report["summary"].get("F_total", 0)) == 0:
        eval_out = out_dir / "cct_folded_localization_eval.json"
        eval_out.write_text(json.dumps(
            {
                "mutant_id": mutant_id,
                "scoring_strategy": scoring,
                "status": "not_detected",
                "reason": "no_tbfv_failures",
                "metrics": {},
            },
            indent=2,
            ensure_ascii=False,
        ), encoding="utf-8")
        return base | {
            "status": "not_detected",
            "reason": "no_tbfv_failures",
            "raw_report": str(raw_out),
            "aggregated_report": str(agg_out),
            "eval_report": str(eval_out),
            "F_total": report["summary"]["F_total"],
            "P_total": report["summary"]["P_total"],
            "condition_candidates": report["summary"]["condition_candidates"],
            "seed_e_candidates": report["summary"]["seed_e_candidates"],
            "seed_s_candidates": report["summary"]["seed_s_candidates"],
            "unstable_segment_variants": report["summary"].get(
                "unstable_segment_variants", 0
            ),
        }

    # Evaluate.
    eval_metrics = evaluate_reports(
        record, aggregated_report=aggregated, top_k=top_k,
    )["metrics"]

    eval_out = out_dir / "cct_folded_localization_eval.json"
    eval_out.write_text(json.dumps(
        {"mutant_id": mutant_id, "scoring_strategy": scoring, "metrics": eval_metrics},
        indent=2, ensure_ascii=False,
    ), encoding="utf-8")

    # --- Assemble row ---
    row = base | {
        "status": "evaluated",
        "raw_report": str(raw_out),
        "aggregated_report": str(agg_out),
        "eval_report": str(eval_out),
        "F_total": report["summary"]["F_total"],
        "P_total": report["summary"]["P_total"],
        "condition_candidates": report["summary"]["condition_candidates"],
        "seed_e_candidates": report["summary"]["seed_e_candidates"],
        "seed_s_candidates": report["summary"]["seed_s_candidates"],
        "unstable_segment_variants": report["summary"].get(
            "unstable_segment_variants", 0
        ),
    }

    # Extract hit metrics for each ranking.
    for strategy_key in (
        "aggregated.condition_node",
        "aggregated.interval.folded_seed_e",
        "aggregated.interval.folded_seed_s",
        "aggregated.interval.folded_edge_partition",
    ):
        metrics = eval_metrics.get(strategy_key, {})
        prefix = strategy_key.replace(".", "_").replace("aggregated_", "")
        row[f"{prefix}_hit"] = metrics.get("hit", False)
        row[f"{prefix}_best_rank"] = metrics.get("best_rank")
        row[f"{prefix}_topk"] = json.dumps(metrics.get("topk", {}))
        row[f"{prefix}_prediction_count"] = metrics.get("prediction_count")

    # --- Folded composite: condition_node ∪ folded_edge_partition ---
    _add_folded_composite(row, aggregated, record, top_k)

    return row


def _add_folded_composite(
    row: dict[str, Any],
    aggregated: dict[str, Any],
    record: dict[str, Any],
    top_k: list[int],
) -> None:
    """Add composite hit metrics: union of condition + edge_partition at each rank.

    Uses the same hit-checking logic as the eval layer, but unions two
    rankings instead of using the hardcoded old composite.
    """
    from csc_engine.failure_localization_eval import (
        _acceptable_line_set,
        _acceptable_window,
    )

    # Extract predictions from the aggregated report (raw dicts, not LocalizationPrediction).
    condition = aggregated.get("aggregated_condition_node_ranking", [])
    edge_partition = aggregated.get(
        "aggregated_interval_rankings", {}
    ).get("folded_edge_partition", [])

    acceptable = _acceptable_line_set(record)
    window = _acceptable_window(record)

    def _lines_hit_gt(lines: set[int]) -> bool:
        if acceptable.intersection(lines):
            return True
        if window is not None:
            start, end = window
            if any(start <= line <= end for line in lines):
                return True
        return False

    composite_topk: dict[str, bool] = {}
    hit = False
    best_rank = None
    for k in sorted(top_k):
        cond_lines: set[int] = set()
        for p in condition[:k]:
            line = p.get("line")
            if line is not None:
                cond_lines.add(int(line))
            for sl in (p.get("statement_lines") or []):
                if sl is not None:
                    cond_lines.add(int(sl))
        ep_lines: set[int] = set()
        for p in edge_partition[:k]:
            for sl in (p.get("statement_lines") or []):
                if sl is not None:
                    ep_lines.add(int(sl))
        union_lines = cond_lines | ep_lines
        is_hit = _lines_hit_gt(union_lines)
        composite_topk[f"top{k}"] = is_hit
        if is_hit:
            hit = True
            if best_rank is None:
                best_rank = k

    prefix = "condition_node_folded_edge_partition"
    row[f"{prefix}_hit"] = hit
    row[f"{prefix}_best_rank"] = best_rank
    row[f"{prefix}_topk"] = json.dumps(composite_topk)
    row[f"{prefix}_prediction_count"] = len(condition) + len(edge_partition)


def _resolve_source_file(record: dict[str, Any]) -> str | None:
    """Try to resolve the source file from the mutant record."""
    gt = record.get("ground_truth", {})
    return gt.get("primary_file")


def _skip_row(record: dict[str, Any], scoring: str, reason: str) -> dict[str, Any]:
    return {
        "mutant_id": record.get("mutant_id"),
        "subject": record.get("subject"),
        "operator": record.get("operator"),
        "fault_kind": record.get("fault_kind"),
        "fault_category": record.get("fault_category"),
        "scoring_strategy": scoring,
        "status": "skipped",
        "reason": reason,
    }


def _write_outputs(
    output_dir: Path,
    rows: list[dict[str, Any]],
    scoring: str,
    top_k: list[int],
    old_combined_file: Path | None = None,
) -> None:
    """Write replay rows, summary, metadata, and optional old-vs-new comparison."""
    rows_path = output_dir / "folded_replay_rows.jsonl"
    rows_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )

    summary = _summarize(rows, top_k)
    summary_path = output_dir / "folded_replay_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    # CSV rows.
    csv_path = output_dir / "folded_replay_rows.csv"
    if rows:
        fields = sorted({k for r in rows for k in r})
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    metadata_path = output_dir / "folded_replay_metadata.json"
    metadata_path.write_text(json.dumps({
        "scoring_strategy": scoring,
        "top_k": top_k,
        "total_tasks": len(rows),
        "evaluated": sum(1 for r in rows if r.get("status") == "evaluated"),
        "skipped": sum(1 for r in rows if r.get("status") != "evaluated"),
        "skipped_reasons": [
            {"mutant_id": r["mutant_id"], "reason": r.get("reason")}
            for r in rows if r.get("status") != "evaluated"
        ],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    if old_combined_file is not None:
        _write_comparison_summary(output_dir, rows, old_combined_file, top_k)

    print(f"Fold-the-tree replay complete: {output_dir}")
    print(f"  Tasks:     {len(rows)}")
    print(f"  Evaluated: {sum(1 for r in rows if r.get('status') == 'evaluated')}")
    print(f"  Skipped:   {sum(1 for r in rows if r.get('status') != 'evaluated')}")
    if old_combined_file is not None:
        print(f"  Comparison summary written.")


def _summarize(rows: list[dict[str, Any]], top_k: list[int]) -> list[dict[str, Any]]:
    """Compute per-strategy hit rates."""
    evaluated = [r for r in rows if r.get("status") == "evaluated"]
    summaries: list[dict[str, Any]] = []
    for strategy_key in (
        "aggregated.condition_node",
        "aggregated.interval.folded_seed_e",
        "aggregated.interval.folded_seed_s",
        "aggregated.interval.folded_edge_partition",
        "aggregated.composite.folded_condition_or_edge_partition",
    ):
        prefix = ("condition_node_folded_edge_partition"
                  if "composite" in strategy_key
                  else strategy_key.replace(".", "_").replace("aggregated_", ""))
        hit_field = f"{prefix}_hit"
        topk_field = f"{prefix}_topk"
        total = len(evaluated)
        hits = sum(1 for r in evaluated if r.get(hit_field))
        summary = {
            "strategy": strategy_key,
            "evaluated": total,
            "hit": hits,
            "hit_rate": hits / total if total else 0.0,
        }
        for k in top_k:
            topk_hits = 0
            for r in evaluated:
                try:
                    topk = json.loads(str(r.get(topk_field, "{}")))
                except (json.JSONDecodeError, TypeError):
                    topk = {}
                if topk.get(f"top{k}", False):
                    topk_hits += 1
            summary[f"top{k}_hits"] = topk_hits
            summary[f"top{k}_hit_rate"] = topk_hits / total if total else 0.0
        summaries.append(summary)
    return summaries


def _parse_top_k(raw: str) -> list[int]:
    values = sorted({int(item.strip()) for item in raw.split(",") if item.strip()})
    return [v for v in values if v > 0]


def _write_comparison_summary(
    output_dir: Path,
    folded_rows: list[dict[str, Any]],
    old_combined_file: Path,
    top_k: list[int],
) -> None:
    """Generate comparison_summary.md comparing folded vs old strategies."""
    import json as _json

    # --- Load old rows ---
    old: dict[tuple[str, str], dict[str, Any]] = {}
    old_categories: dict[str, str] = {}
    with old_combined_file.open(encoding="utf-8") as fh:
        for line in fh:
            r = _json.loads(line.strip())
            s = r.get("strategy") or "unknown"
            mid = r.get("mutant_id", "")
            old[(mid, s)] = r
            if r.get("fault_category"):
                old_categories[mid] = r["fault_category"]

    # --- Load categories from manifest if available ---
    manifest = old_combined_file.parent / "combined_mutants_manifest.jsonl"
    if manifest.exists():
        with manifest.open(encoding="utf-8") as fh:
            for line in fh:
                r = _json.loads(line.strip())
                if r.get("fault_category"):
                    old_categories[r["mutant_id"]] = r["fault_category"]

    evaluated = [r for r in folded_rows if r.get("status") == "evaluated"]
    if not evaluated:
        return

    # --- Build folded per-category buckets ---
    def _folded_buckets(field_prefix: str) -> dict[str, dict[str, int]]:
        buckets: dict[str, dict[str, int]] = {
            "all": {"hit": 0, "top1": 0, "top2": 0, "top3": 0, "eval": 0},
        }
        for r in evaluated:
            mid = r["mutant_id"]
            cat = old_categories.get(mid, "?")
            for ck in ("all", cat):
                buckets.setdefault(ck, {"hit": 0, "top1": 0, "top2": 0, "top3": 0, "eval": 0})
                buckets[ck]["eval"] += 1
                if r.get(f"{field_prefix}_hit"):
                    buckets[ck]["hit"] += 1
                tk = _json.loads(r.get(f"{field_prefix}_topk", "{}"))
                if tk.get("top1"):
                    buckets[ck]["top1"] += 1
                if tk.get("top2"):
                    buckets[ck]["top2"] += 1
                if tk.get("top3"):
                    buckets[ck]["top3"] += 1
        return buckets

    def _old_buckets(strategy: str) -> dict[str, dict[str, int]]:
        buckets: dict[str, dict[str, int]] = {
            "all": {"hit": 0, "top1": 0, "top2": 0, "top3": 0, "eval": 0},
        }
        for (mid, s), r in old.items():
            if s != strategy:
                continue
            cat = old_categories.get(mid, "?")
            for ck in ("all", cat):
                buckets.setdefault(ck, {"hit": 0, "top1": 0, "top2": 0, "top3": 0, "eval": 0})
                buckets[ck]["eval"] += 1
                if r.get("hit"):
                    buckets[ck]["hit"] += 1
                if r.get("top1_hit"):
                    buckets[ck]["top1"] += 1
                if r.get("top2_hit"):
                    buckets[ck]["top2"] += 1
                if r.get("top3_hit"):
                    buckets[ck]["top3"] += 1
        return buckets

    def _fmt(N: int, hits: int) -> str:
        rate = hits / N if N > 0 else 0.0
        return f"{hits:>3}/{N:<3}  ({rate:.3f})"

    # --- Build markdown ---
    lines = [
        "# RQ4 Fold-the-Tree Replay — Comparison Summary",
        "",
        f"- Folded scoring: `density_log`",
        f"- Top-K: {', '.join(str(k) for k in sorted(top_k))}",
        f"- Evaluated: {len(evaluated)} / {len(folded_rows)} total tasks",
        f"- Old baseline: `{old_combined_file}`",
        "",
    ]

    comparisons = [
        (
            "Folded Composite (cond ∪ edge-part) vs Old Composite (cond ∪ gated)",
            "condition_node_folded_edge_partition",
            "aggregated.composite.condition_or_interval",
        ),
        (
            "Folded Edge-Partition vs Old Edge-Divergence-Gated",
            "interval_folded_edge_partition",
            "aggregated.interval.edge_divergence_gated",
        ),
        (
            "Folded Condition vs Old Condition",
            "condition_node",
            "aggregated.condition_node",
        ),
    ]

    for title, f_prefix, o_strategy in comparisons:
        lines.append(f"## {title}")
        lines.append("")
        f_buckets = _folded_buckets(f_prefix)
        o_buckets = _old_buckets(o_strategy)

        for label, cat in [("overall", "all"), ("condition", "condition"), ("statement", "statement")]:
            fb = f_buckets.get(cat)
            ob = o_buckets.get(cat)
            if fb is None or ob is None:
                continue
            Nf, No = fb["eval"], ob["eval"]
            lines.append(f"### {label} (old N={No}, folded N={Nf})")
            lines.append("")
            lines.append("| Metric | Old | Folded |")
            lines.append("|--------|-----|--------|")
            lines.append(f"| hit | {_fmt(No, ob['hit'])} | {_fmt(Nf, fb['hit'])} |")
            lines.append(f"| top-1 | {_fmt(No, ob['top1'])} | {_fmt(Nf, fb['top1'])} |")
            if f_prefix == "condition_node":
                lines.append(f"| top-3 | {_fmt(No, ob['top3'])} | {_fmt(Nf, fb['top3'])} |")
            else:
                lines.append(f"| top-2 | — | {_fmt(Nf, fb['top2'])} |")
                lines.append(f"| top-3 | {_fmt(No, ob['top3'])} | {_fmt(Nf, fb['top3'])} |")
            lines.append("")

    (output_dir / "comparison_summary.md").write_text(
        "\n".join(lines), encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
