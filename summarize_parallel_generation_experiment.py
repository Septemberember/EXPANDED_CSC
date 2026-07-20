#!/usr/bin/env python3
"""Summarize the RQ2 parallel CSC generation experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csc_experiments.parallel_generation import (
    RUNS_JSONL,
    summarize_parallel_generation_experiment,
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    runs_jsonl = resolve_runs_jsonl(args)
    try:
        report = summarize_parallel_generation_experiment(
            runs_jsonl,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        print(f"Parallel generation summary failed: {exc}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir) if args.output_dir else Path(runs_jsonl).parent
    print("Parallel generation summary complete")
    print(f"  Runs:      {runs_jsonl}")
    print(f"  Output:    {output_dir}")
    print(f"  Subjects:  {len(report['subjects'])}")
    print(f"  Workers:   {', '.join(str(worker) for worker in report['workers'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize RQ2 parallel generation run records."
    )
    parser.add_argument(
        "--runs-jsonl",
        help="Path to parallel_generation_runs.jsonl.",
    )
    parser.add_argument(
        "--experiment-dir",
        help="Experiment directory containing parallel_generation_runs.jsonl.",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for JSON/CSV/Markdown summaries. Defaults to the runs directory.",
    )
    return parser


def resolve_runs_jsonl(args: argparse.Namespace) -> Path:
    if args.runs_jsonl:
        return Path(args.runs_jsonl)
    if args.experiment_dir:
        return Path(args.experiment_dir) / RUNS_JSONL
    raise ValueError("Provide --runs-jsonl or --experiment-dir")


if __name__ == "__main__":
    raise SystemExit(main())
