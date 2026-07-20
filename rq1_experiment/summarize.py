#!/usr/bin/env python3
"""Summarize RQ1 CSC-only runs against RQ2 W=1 CSC+Boundary runs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rq1_experiment.bounded_completion import (
    RUNS_JSONL,
    summarize_rq1,
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    runs_rq1, runs_rq2 = resolve_inputs(args)
    try:
        report = summarize_rq1(
            runs_rq1,
            runs_rq2,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        print(f"RQ1 summary failed: {exc}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir) if args.output_dir else Path(runs_rq1).parent
    print("RQ1 summary complete")
    print(f"  RQ1 runs:    {runs_rq1}")
    print(f"  RQ2 runs:    {runs_rq2}")
    print(f"  Output:      {output_dir}")
    print(f"  Subjects:    {len(report['subjects'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize RQ1 CSC-only runs against RQ2 W=1 CSC+Boundary runs."
    )
    parser.add_argument(
        "--rq1-runs",
        help="Path to rq1_csc_only_runs.jsonl.",
    )
    parser.add_argument(
        "--rq2-runs",
        help="Path to RQ2 parallel_generation_runs.jsonl.",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for JSON/CSV/Markdown summaries. Defaults to the RQ1 runs directory.",
    )
    parser.add_argument(
        "--rq1-experiment-dir",
        help="RQ1 experiment directory containing rq1_csc_only_runs.jsonl.",
    )
    parser.add_argument(
        "--rq2-experiment-dir",
        help="RQ2 experiment directory containing parallel_generation_runs.jsonl.",
    )
    return parser


def resolve_inputs(args: argparse.Namespace) -> tuple[str, str]:
    rq1_path = args.rq1_runs or (
        Path(args.rq1_experiment_dir) / RUNS_JSONL if args.rq1_experiment_dir else None
    )
    rq2_path = args.rq2_runs or (
        Path(args.rq2_experiment_dir) / "parallel_generation_runs.jsonl"
        if args.rq2_experiment_dir
        else None
    )
    if not rq1_path or not rq2_path:
        raise ValueError(
            "Provide --rq1-runs and --rq2-runs, or --rq1-experiment-dir and --rq2-experiment-dir."
        )
    return str(rq1_path), str(rq2_path)


if __name__ == "__main__":
    raise SystemExit(main())
