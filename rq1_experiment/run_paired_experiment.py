#!/usr/bin/env python3
"""Run and summarize the scheduler-matched RQ1 experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rq1_experiment.bounded_completion import (
    run_paired_rq1_experiment,
    summarize_paired_rq1,
)


DEFAULT_DATASETS = (
    "dataset/EX_CSC_dataset",
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parent.parent
    try:
        result = run_paired_rq1_experiment(
            dataset_roots=args.dataset_root or list(DEFAULT_DATASETS),
            experiment_dir=args.experiment_dir,
            repeats=args.repeats,
            range_bound=args.range_bound,
            max_iter=args.max_iter,
            timeout_s=args.timeout_s,
            session_prefix=args.session_prefix,
            project_root=project_root,
            dry_run=args.dry_run,
            allow_existing_sessions=args.allow_existing_sessions,
        )
        report = summarize_paired_rq1(
            result["runs_jsonl"],
            output_dir=result["config"]["experiment_dir"],
        )
    except Exception as exc:
        print(f"Paired RQ1 experiment failed: {exc}", file=sys.stderr)
        return 2

    print("Scheduler-matched RQ1 experiment complete")
    print(f"  Runs: {result['runs_jsonl']}")
    print(f"  Normal completions: {report['normal_completion_count']}/{report['run_count']}")
    print(
        "  Fully paired subjects: "
        f"{report['fully_paired_subject_count']}/{report['subject_count']}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare CSC-only and CSC+Boundary under the same sequential scheduler."
        )
    )
    parser.add_argument(
        "--dataset-root",
        action="append",
        help="Dataset root; repeat for multiple roots (default: unified EX_CSC_dataset).",
    )
    parser.add_argument("--experiment-dir", required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--range-bound", type=int, default=200)
    parser.add_argument("--max-iter", type=int, default=2000)
    parser.add_argument("--timeout-s", type=int)
    parser.add_argument("--session-prefix")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-existing-sessions", action="store_true")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
