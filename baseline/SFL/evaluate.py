#!/usr/bin/env python3
"""Compare SFL and CCT-based fault localization against ground truth.

Evaluates top-k hit rates and timing for each method on a per-mutant basis.
Supports both single-mutant and batch (all-mutants) modes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_TOP_K = (1, 3, 5)


# ---------------------------------------------------------------------------
# Manifest loading (same format as csc_engine.failure_localization_eval)
# ---------------------------------------------------------------------------

def load_manifest(path: str | Path) -> list[dict[str, Any]]:
    records = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            records.append(json.loads(stripped))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return records


def find_mutant_record(records: list[dict[str, Any]], mutant_id: str) -> dict[str, Any]:
    for record in records:
        if record.get("mutant_id") == mutant_id:
            return record
    raise ValueError(f"Mutant id not found in manifest: {mutant_id}")


def acceptable_line_set(record: dict[str, Any]) -> set[int]:
    gt = record.get("ground_truth", {})
    lines = gt.get("acceptable_lines") or [gt.get("primary_line")]
    return {int(ln) for ln in lines if ln is not None}


# ---------------------------------------------------------------------------
# SFL evaluation
# ---------------------------------------------------------------------------

def evaluate_sfl(sfl_report: dict[str, Any],
                 manifest_record: dict[str, Any],
                 top_k: list[int]) -> dict[str, Any]:
    """Evaluate each SFL formula ranking against ground truth."""
    acceptable = acceptable_line_set(manifest_record)
    rankings = sfl_report.get("rankings", {})
    timings = sfl_report.get("summary", {}).get("timings", {})

    results: dict[str, Any] = {}
    for formula, records in rankings.items():
        results[f"sfl_{formula}"] = _evaluate_line_ranking(
            records, acceptable, top_k,
            meta={"timing_s": timings.get("total_s"), "timings": timings},
        )
    return results


def _evaluate_line_ranking(records: list[dict[str, Any]],
                           acceptable_lines: set[int],
                           top_k: list[int],
                           meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Check if any line in acceptable_lines appears in the top-k records."""
    hits = sorted(
        (rec for rec in records if rec["line"] in acceptable_lines),
        key=lambda rec: rec["rank"],
    )
    best = hits[0] if hits else None
    best_rank = best["rank"] if best else None
    topk = {}
    for k in sorted(top_k):
        topk[f"top{k}"] = best_rank is not None and best_rank <= k

    result: dict[str, Any] = {
        "prediction_count": len(records),
        "hit": best is not None,
        "best_rank": best_rank,
        "hit_line": best["line"] if best else None,
        "hit_score": best.get("score") if best else None,
        "topk": topk,
    }
    if meta:
        result.update(meta)
    return result


# ---------------------------------------------------------------------------
# CCT evaluation (self-contained, same logic as failure_localization_eval)
# ---------------------------------------------------------------------------

def evaluate_cct(cct_report: dict[str, Any],
                 manifest_record: dict[str, Any],
                 top_k: list[int]) -> dict[str, Any]:
    """Evaluate CCT localization strategies against ground truth."""
    acceptable = acceptable_line_set(manifest_record)
    results: dict[str, Any] = {}

    # Condition node ranking
    cond_records = cct_report.get("condition_node_ranking", [])
    results["cct_condition_node"] = _evaluate_cct_condition_ranking(
        cond_records, acceptable, top_k,
    )

    # Default interval ranking
    intv_records = cct_report.get("condition_interval_ranking", [])
    results["cct_interval_default"] = _evaluate_cct_interval_ranking(
        intv_records, acceptable, top_k,
    )

    # Each interval strategy
    for strategy_name, intv_records in cct_report.get("interval_rankings", {}).items():
        results[f"cct_interval_{strategy_name}"] = _evaluate_cct_interval_ranking(
            intv_records, acceptable, top_k,
        )

    return results


def _evaluate_cct_condition_ranking(records: list[dict[str, Any]],
                                    acceptable_lines: set[int],
                                    top_k: list[int]) -> dict[str, Any]:
    """CCT condition nodes have a 'line' field."""
    hits = sorted(
        (rec for rec in records if rec.get("line") in acceptable_lines),
        key=lambda rec: rec.get("rank", 10**9),
    )
    best = hits[0] if hits else None
    best_rank = best["rank"] if best else None
    topk = {}
    for k in sorted(top_k):
        topk[f"top{k}"] = best_rank is not None and best_rank <= k

    return {
        "prediction_count": len(records),
        "hit": best is not None,
        "best_rank": best_rank,
        "hit_line": best.get("line") if best else None,
        "hit_score": best.get("risk_score") if best else None,
        "hit_node_id": best.get("node_id") if best else None,
        "topk": topk,
    }


def _evaluate_cct_interval_ranking(records: list[dict[str, Any]],
                                   acceptable_lines: set[int],
                                   top_k: list[int]) -> dict[str, Any]:
    """CCT interval records may have statement_lines or a line_interval."""
    hits = sorted(
        (rec for rec in records if _interval_hits(rec, acceptable_lines)),
        key=lambda rec: rec.get("rank", 10**9),
    )
    best = hits[0] if hits else None
    best_rank = best["rank"] if best else None
    topk = {}
    for k in sorted(top_k):
        topk[f"top{k}"] = best_rank is not None and best_rank <= k

    matched_lines = _matched_acceptable_lines(best, acceptable_lines) if best else []

    return {
        "prediction_count": len(records),
        "hit": best is not None,
        "best_rank": best_rank,
        "hit_lines": matched_lines,
        "hit_edge_id": best.get("edge_id") if best else None,
        "hit_score": best.get("risk_score") if best else None,
        "topk": topk,
    }


def _interval_hits(record: dict[str, Any], acceptable_lines: set[int]) -> bool:
    """Check if a CCT interval record intersects acceptable_lines.

    The location_basis field determines which evidence to check:
    - statement_lines: only check the concrete ASSIGN/RETURN lines from traces
    - condition_anchor_span: check the condition-anchor range and from/to lines
    """
    basis = record.get("location_basis", "")

    if basis == "statement_lines":
        stmt_lines = record.get("statement_lines", [])
        return stmt_lines and any(int(ln) in acceptable_lines for ln in stmt_lines)

    if basis == "statement_lines_missing":
        return False

    # condition_anchor_span or fallback: check span and anchor lines
    span = record.get("condition_anchor_span") or record.get("line_interval")
    if span and len(span) >= 2:
        lo = min(int(span[0] or 0), int(span[1] or 0))
        hi = max(int(span[0] or 0), int(span[1] or 0))
        if lo > 0 and any(lo <= ln <= hi for ln in acceptable_lines):
            return True

    from_ln = record.get("from_line")
    to_ln = record.get("to_line")
    if from_ln is not None and int(from_ln) in acceptable_lines:
        return True
    if to_ln is not None and int(to_ln) in acceptable_lines:
        return True

    return False


def _matched_acceptable_lines(record: dict[str, Any] | None,
                              acceptable_lines: set[int]) -> list[int]:
    if record is None:
        return []
    stmt_lines = record.get("statement_lines", [])
    return sorted(
        ln for ln in acceptable_lines
        if ln in stmt_lines or ln == record.get("from_line") or ln == record.get("to_line")
    )


# ---------------------------------------------------------------------------
# Comparison report
# ---------------------------------------------------------------------------

def compare(mutant_record: dict[str, Any],
            sfl_report: dict[str, Any] | None,
            cct_report: dict[str, Any] | None,
            top_k: list[int]) -> dict[str, Any]:
    """Produce a side-by-side comparison of SFL vs CCT localization."""

    gt = mutant_record.get("ground_truth", {})
    comparison: dict[str, Any] = {}

    if sfl_report is not None:
        comparison.update(evaluate_sfl(sfl_report, mutant_record, list(top_k)))

    if cct_report is not None:
        # CCT timings are not in the report; we note that
        comparison.update(evaluate_cct(cct_report, mutant_record, list(top_k)))

    return {
        "mutant_id": mutant_record.get("mutant_id"),
        "mutant_file": mutant_record.get("mutant_file"),
        "subject": mutant_record.get("subject"),
        "operator": mutant_record.get("operator"),
        "fault_kind": mutant_record.get("fault_kind"),
        "fault_category": mutant_record.get("fault_category",
                                             mutant_record.get("fault_kind")),
        "ground_truth": {
            "primary_line": gt.get("primary_line"),
            "acceptable_lines": sorted(acceptable_line_set(mutant_record)),
        },
        "top_k": sorted(top_k),
        "comparison": comparison,
    }


def write_report(report: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Batch evaluation
# ---------------------------------------------------------------------------

def batch_compare(manifest_path: str | Path,
                  sfl_report_map: dict[str, str | Path],
                  cct_report_map: dict[str, str | Path],
                  top_k: list[int]) -> list[dict[str, Any]]:
    """Run comparison for all mutants in the manifest."""
    manifest = load_manifest(manifest_path)
    results = []
    for record in manifest:
        mutant_id = record["mutant_id"]
        sfl_path = sfl_report_map.get(mutant_id)
        cct_path = cct_report_map.get(mutant_id)
        if sfl_path is None and cct_path is None:
            continue
        sfl = json.loads(Path(sfl_path).read_text(encoding="utf-8")) if sfl_path else None
        cct = json.loads(Path(cct_path).read_text(encoding="utf-8")) if cct_path else None
        results.append(compare(record, sfl, cct, top_k))
    return results


def batch_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute aggregate statistics from batch comparison results."""
    all_methods: set[str] = set()
    for r in results:
        all_methods.update(r["comparison"].keys())

    summary: dict[str, Any] = {
        "total_mutants": len(results),
        "methods": {},
    }

    for method in sorted(all_methods):
        method_results = [
            r["comparison"][method]
            for r in results
            if method in r["comparison"]
        ]
        if not method_results:
            continue

        hit_counts: dict[str, int] = {}
        total_hits = 0
        total_rank_sum = 0
        total_rank_count = 0
        for mr in method_results:
            topk = mr.get("topk", {})
            for k_label, hit in topk.items():
                hit_counts[k_label] = hit_counts.get(k_label, 0) + (1 if hit else 0)
            if mr.get("hit"):
                total_hits += 1
            if mr.get("best_rank") is not None:
                total_rank_sum += mr["best_rank"]
                total_rank_count += 1

        n = len(method_results)
        summary["methods"][method] = {
            "count": n,
            "total_hits": total_hits,
            "hit_rate": round(total_hits / n, 4) if n > 0 else 0.0,
            "hit_rates": {
                k: round(hit_counts.get(k, 0) / n, 4) if n > 0 else 0.0
                for k in sorted(hit_counts)
            },
            "avg_best_rank": round(total_rank_sum / total_rank_count, 2)
            if total_rank_count > 0 else None,
            "median_best_rank": _median([mr["best_rank"] for mr in method_results
                                         if mr.get("best_rank") is not None]),
        }

    return summary


def _median(values: list[int]) -> float | None:
    if not values:
        return None
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        return float(sorted_vals[n // 2])
    return (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest)
        top_k = parse_top_k(args.top_k)

        if args.batch:
            results = batch_compare(args.manifest, {}, {}, top_k)
            # In batch mode we use --sfl-dir and --cct-dir to discover reports
            sfl_map = _discover_report_map(args.sfl_dir, "sfl_localization.json") if args.sfl_dir else {}
            cct_map = _discover_report_map(args.cct_dir, "cct_failure_localization.json") if args.cct_dir else {}
            results = batch_compare(args.manifest, sfl_map, cct_map, top_k)
            if args.output:
                s = batch_summary(results)
                write_report({"results": results, "summary": s}, args.output)
            output_path = Path(args.output) if args.output else Path("sfl_cct_comparison_batch.json")
            print_batch_summary(results)
            if args.output:
                print(f"Batch comparison saved to {output_path}")
            return 0

        # Single-mutant mode
        record = find_mutant_record(manifest, args.mutant_id)
        sfl = json.loads(Path(args.sfl_report).read_text(encoding="utf-8")) if args.sfl_report else None
        cct = json.loads(Path(args.cct_report).read_text(encoding="utf-8")) if args.cct_report else None

        comparison = compare(record, sfl, cct, top_k)
        output_path = resolve_output_path(args, comparison)
        write_report(comparison, output_path)
        print_single_summary(comparison, output_path)
        return 0
    except Exception as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare SFL and CCT fault localization results."
    )
    parser.add_argument("--manifest", required=True,
                        help="mutants_manifest.jsonl file.")
    parser.add_argument("--mutant-id",
                        help="Mutant id to evaluate (single mode).")
    parser.add_argument("--sfl-report",
                        help="sfl_localization.json path (single mode).")
    parser.add_argument("--cct-report",
                        help="cct_failure_localization.json path (single mode).")
    parser.add_argument("--output",
                        help="Output JSON path.")
    parser.add_argument("--top-k", default="1,3,5",
                        help="Comma-separated top-k values (default: 1,3,5).")
    parser.add_argument("--batch", action="store_true",
                        help="Batch mode: compare all mutants in manifest.")
    parser.add_argument("--sfl-dir",
                        help="Directory containing sfl_localization.json (batch mode).")
    parser.add_argument("--cct-dir",
                        help="Directory containing cct_failure_localization.json (batch mode).")
    return parser


def parse_top_k(raw: str) -> list[int]:
    values = []
    for item in raw.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        val = int(stripped)
        if val <= 0:
            raise ValueError("Top-k values must be positive")
        values.append(val)
    return values or list(DEFAULT_TOP_K)


def resolve_output_path(args: argparse.Namespace, comparison: dict[str, Any]) -> Path:
    if args.output:
        return Path(args.output)
    mutant_id = comparison.get("mutant_id", "unknown")
    return Path(f"sfl_cct_comparison_{mutant_id}.json")


def _discover_report_map(base_dir: str, filename: str) -> dict[str, str]:
    """Map mutant session names to report paths."""
    result: dict[str, str] = {}
    base = Path(base_dir)
    if not base.is_dir():
        return result
    for session_dir in base.iterdir():
        if not session_dir.is_dir():
            continue
        for class_dir in session_dir.iterdir():
            if not class_dir.is_dir():
                continue
            report_path = class_dir / filename
            if report_path.is_file():
                session_name = session_dir.name
                result[session_name] = str(report_path)
    return result


def print_single_summary(comparison: dict[str, Any], output_path: Path) -> None:
    print("SFL vs CCT comparison complete")
    print(f"  Output:     {output_path}")
    print(f"  Mutant:     {comparison.get('mutant_id')}")
    print(f"  Operator:   {comparison.get('operator', '<unknown>')}")
    print(f"  Fault kind: {comparison.get('fault_kind', '<unknown>')}")
    gt = comparison.get("ground_truth", {})
    print(f"  Ground truth line: {gt.get('primary_line')}")
    top_k = comparison.get("top_k", [])
    print(f"  Top-k:      {', '.join(str(k) for k in top_k)}")
    print()
    for method, result in comparison.get("comparison", {}).items():
        topk = result.get("topk", {})
        flags = "  ".join(
            f"{k}={'hit' if v else 'miss'}" for k, v in sorted(topk.items())
        )
        best = result.get("best_rank", "-")
        print(f"  {method}: best_rank={best}, {flags}")


def print_batch_summary(results: list[dict[str, Any]]) -> None:
    s = batch_summary(results)
    print(f"Batch comparison: {s['total_mutants']} mutants")
    for method, stats in s.get("methods", {}).items():
        print(
            f"  {method}: "
            f"hit_rate={stats['hit_rate']:.2%} "
            f"avg_best_rank={stats['avg_best_rank']} "
            f"({stats['total_hits']}/{stats['count']})"
        )
        for k, rate in stats.get("hit_rates", {}).items():
            print(f"    {k}: {rate:.2%}")


if __name__ == "__main__":
    raise SystemExit(main())
