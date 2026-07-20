#!/usr/bin/env python3
"""Run the RQ2 parallel CSC generation experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csc_experiments.parallel_generation import (
    DEFAULT_WORKERS,
    run_parallel_generation_experiment,
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_parallel_generation_experiment(
            dataset_root=args.dataset_root,
            experiment_dir=args.experiment_dir,
            workers=parse_workers(args.workers),
            mode=args.mode,
            range_bound=args.range_bound,
            max_iter=args.max_iter,
            timeout_s=args.timeout_s,
            session_prefix=args.session_prefix,
            project_root=Path(__file__).resolve().parent,
            dry_run=args.dry_run,
            allow_existing_sessions=args.allow_existing_sessions,
            append=args.append,
        )
    except Exception as exc:
        print(f"Parallel generation experiment failed: {exc}", file=sys.stderr)
        return 2

    print("Parallel generation experiment complete")
    print(f"  Config: {Path(result['config']['experiment_dir']) / 'parallel_generation_config.json'}")
    print(f"  Runs:   {result['runs_jsonl']}")
    print(f"  Count:  {len(result['runs'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run generation-only CSC worker-scaling experiments for RQ2."
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
        "--workers",
        default=",".join(str(value) for value in DEFAULT_WORKERS),
        help="Comma-separated worker counts (default: 1,2,4,8).",
    )
    parser.add_argument("--mode", choices=["original", "expanded"], default="expanded")
    parser.add_argument("--range-bound", type=int, default=200)
    parser.add_argument("--max-iter", type=int, default=100)
    parser.add_argument("--timeout-s", type=int)
    parser.add_argument("--session-prefix")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--allow-existing-sessions",
        action="store_true",
        help="Allow reusing existing csc_tmp session directories. Off by default to avoid stale CCT timing.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to an existing parallel_generation_runs.jsonl. Off by default.",
    )
    return parser


def parse_workers(raw: str) -> list[int]:
    values = []
    for item in raw.split(","):
        stripped = item.strip()
        if stripped:
            values.append(int(stripped))
    return values


if __name__ == "__main__":
    raise SystemExit(main())
