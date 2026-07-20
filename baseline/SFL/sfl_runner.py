#!/usr/bin/env python3
"""SFL-based failure localization: end-to-end CLI.

Builds a program spectrum from instrumented trace files and TBFV verification
results, computes SFL suspiciousness scores with classic formulas, and produces
a ranked localization report.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from .spectrum import build_spectrum
from .formulas import FORMULA_NAMES, compute_suspiciousness


DEFAULT_TOP_K = 10


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        report = run_sfl_localization(
            session_dir=args.session_dir,
            tbfv_report=args.tbfv_report,
            top_k=args.top_k,
        )
        output_path = resolve_output_path(args)
        write_report(report, output_path)
        print_summary(report, output_path)
        return 0
    except Exception as exc:
        print(f"SFL localization failed: {exc}", file=sys.stderr)
        return 2


def run_sfl_localization(session_dir: str | Path,
                         tbfv_report: str | Path | None = None,
                         top_k: int | None = None) -> dict[str, Any]:
    """Build spectrum, compute SFL scores, and return a ranked report."""

    t0 = time.perf_counter()

    spectrum = build_spectrum(session_dir, tbfv_report_path=tbfv_report)

    t1 = time.perf_counter()
    all_scores = compute_suspiciousness(spectrum)
    t_compute = t1 - t0 if spectrum.timings else time.perf_counter() - t0
    # compute time = total time minus spectrum-building time
    spectrum_time = spectrum.timings.get("spectrum_total_s", 0.0)
    t_compute = max(0.0, (time.perf_counter() - t0) - spectrum_time)

    rankings: dict[str, list[dict[str, Any]]] = {}
    for name in FORMULA_NAMES:
        scores = all_scores[name]
        rankings[name] = _build_ranking(
            spectrum,
            scores,
            formula=name,
            top_k=top_k,
        )

    t_total = time.perf_counter() - t0

    return {
        "summary": {
            "method": "SFL",
            "strategies": FORMULA_NAMES,
            "entities": spectrum.n_entities,
            "test_cases": spectrum.n_tests,
            "failed_cases": spectrum.total_failed,
            "passed_cases": spectrum.total_passed,
            "coverage_ratio": round(spectrum.coverage_ratio, 4),
            "timings": {
                **_format_spectrum_timings(spectrum.timings),
                "sfl_computation_s": round(t_compute, 4),
                "ranking_generation_s": round(
                    max(0.0, t_total - t_compute - spectrum_time), 4
                ),
                "total_s": round(t_total, 4),
            },
        },
        "rankings": rankings,
    }


def _build_ranking(spectrum: "ProgramSpectrum",
                   scores: "np.ndarray",
                   formula: str,
                   top_k: int | None) -> list[dict[str, Any]]:
    """Build a ranked list of suspicious lines from formula scores."""
    # Import numpy locally for type annotations
    import numpy as np

    # Get counts for detailed output
    total_f = spectrum.total_failed
    total_p = spectrum.total_passed
    coverage = spectrum.coverage
    results = spectrum.results

    # Tie-breaking: stable sort by descending score.  Because ``np.argsort`` with
    # ``kind="stable"`` preserves the original entity order for equal scores, and
    # entities are sorted by line number ascending, ties are broken in favour of
    # the numerically smallest line number.  This is documented so that reviewers
    # and readers know the tie-breaking rule.
    order = np.argsort(-scores, kind="stable")
    records: list[dict[str, Any]] = []
    for rank_idx, entity_idx in enumerate(order, start=1):
        if top_k is not None and rank_idx > top_k:
            break
        line = spectrum.entities[entity_idx]
        score = float(scores[entity_idx])

        # Compute per-entity counts
        a_ef = int(np.sum(coverage[entity_idx] & results))
        a_ep = int(np.sum(coverage[entity_idx] & ~results))
        a_nf = total_f - a_ef
        a_np = total_p - a_ep

        records.append({
            "rank": rank_idx,
            "line": line,
            "score": round(score, 8),
            "formula": formula,
            "a_ef": a_ef,
            "a_ep": a_ep,
            "a_nf": a_nf,
            "a_np": a_np,
            "total_executed_by": a_ef + a_ep,
            "failure_fraction": round(a_ef / total_f, 4) if total_f > 0 else 0.0,
        })

    # Attach total candidate count and tie-group size so evaluation tools can
    # optionally use average-rank semantics for zero-score / tied blocks.
    for record in records:
        record["total_candidates"] = len(spectrum.entities)
        # Count how many entities share the same score (tie group)
        same_score = int(np.sum(np.isclose(scores, record["score"], rtol=1e-12)))
        record["tie_group_size"] = same_score

    return records


def _format_spectrum_timings(timings: dict[str, float]) -> dict[str, float]:
    return {f"spectrum_{key}": val for key, val in timings.items()}


def write_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SFL fault localization from instrumented traces."
    )
    parser.add_argument(
        "--session-dir",
        required=True,
        help="CSC session directory, e.g. csc_tmp/mut_loopselection_m4/LoopSelectionSortFive/",
    )
    parser.add_argument(
        "--tbfv-report",
        help="Path to refined_tbfv_report.json. Defaults to <session-dir>/refined_tbfv_report.json.",
    )
    parser.add_argument(
        "--output",
        help="Output JSON path. Defaults to <session-dir>/sfl_localization.json.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Keep only the top K records per formula (default: {DEFAULT_TOP_K}).",
    )
    return parser


def resolve_output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return Path(args.output)
    return Path(args.session_dir) / "sfl_localization.json"


def print_summary(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    print("SFL localization complete")
    print(f"  Output:        {output_path}")
    print(
        f"  Spectrum:      {summary['entities']} entities, "
        f"{summary['test_cases']} tests "
        f"(failed={summary['failed_cases']}, passed={summary['passed_cases']})"
    )
    print(f"  Coverage ratio: {summary['coverage_ratio']:.2%}")
    print(f"  Total time:     {summary['timings']['total_s']:.4f}s")
    print(f"  Strategies:     {', '.join(summary['strategies'])}")

    # Show top-3 for primary formula (ochiai)
    ochiai_ranking = report["rankings"].get("ochiai", [])
    if ochiai_ranking:
        print("  Top-3 (Ochiai):")
        for record in ochiai_ranking[:3]:
            print(
                f"    #{record['rank']} line={record['line']} "
                f"score={record['score']:.4f} "
                f"a_ef={record['a_ef']} a_ep={record['a_ep']}"
            )


if __name__ == "__main__":
    raise SystemExit(main())
