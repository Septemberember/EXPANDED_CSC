#!/usr/bin/env python3
"""Run the RQ1 CSC-only sequential generation experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rq1_experiment.bounded_completion import run_rq1_experiment


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_rq1_experiment(
            dataset_root=args.dataset_root,
            experiment_dir=args.experiment_dir,
            max_iter=args.max_iter,
            timeout_s=args.timeout_s,
            session_prefix=args.session_prefix,
            project_root=Path(__file__).resolve().parent.parent,
            dry_run=args.dry_run,
            allow_existing_sessions=args.allow_existing_sessions,
        )
    except Exception as exc:
        print(f"RQ1 experiment failed: {exc}", file=sys.stderr)
        return 2

    print("RQ1 CSC-only experiment complete")
    print(f"  Config: {Path(result['config']['experiment_dir']) / 'rq1_config.json'}")
    print(f"  Runs:   {result['runs_jsonl']}")
    print(f"  Count:  {len(result['runs'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run CSC-only sequential generation experiments for RQ1."
    )
    parser.add_argument(
        "--dataset-root",
        default="dataset/EX_CSC_dataset",
        help="Dataset root containing subject directories (default: dataset/EX_CSC_dataset).",
    )
    parser.add_argument(
        "--experiment-dir",
        required=True,
        help="Directory where run records and compact artifacts are written.",
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=2000,
        help="Maximum CSC iterations (default: 2000).",
    )
    parser.add_argument("--timeout-s", type=int, help="Timeout per program in seconds.")
    parser.add_argument(
        "--session-prefix",
        help="Prefix for generated CSC session IDs (default: rq1_csc_only_<timestamp>).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned commands without executing.",
    )
    parser.add_argument(
        "--allow-existing-sessions",
        action="store_true",
        help="Allow reusing existing csc_tmp session directories.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
