#!/usr/bin/env python3
"""Run a subject-level CSC/TBFV/localization experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csc_engine import (
    ExperimentOptions,
    default_summary_path,
    run_subject_experiment,
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        options = build_options(args)
        summary = run_subject_experiment(options)
        print_summary(summary, default_summary_path(options))
        return 0 if summary["status"] in {"completed", "planned"} else 2
    except Exception as exc:
        print(f"Subject experiment failed: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run CSC, refined TBFV, failure localization, and evaluation for a subject directory."
    )
    parser.add_argument(
        "subject_dir",
        help="Subject directory containing an original Java file and mutant Java files.",
    )
    parser.add_argument(
        "--project-dir",
        default=Path(__file__).resolve().parent,
        help="CSC_EXPANDED project directory (default: this script's directory).",
    )
    parser.add_argument("--manifest", help="mutants_manifest.jsonl used for mutant discovery/evaluation.")
    parser.add_argument("--fsf", help="Explicit FSF file path.")
    parser.add_argument("--fsf-dir", help="Directory containing the subject FSF.")
    parser.add_argument("--original-file", help="Explicit original Java file.")
    parser.add_argument(
        "--mutants",
        help="Comma-separated mutant ids to run. Defaults to manifest-selected or discovered mutants.",
    )
    parser.add_argument("--session-prefix", help="Prefix for generated CSC sessions.")
    parser.add_argument(
        "--summary-root",
        default="csc_tmp",
        help="Root directory for subject summaries (default: csc_tmp). CSC artifacts stay under csc_tmp/session/ClassName.",
    )
    parser.add_argument(
        "--output-root",
        dest="summary_root",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--mode", choices=["original", "expanded"], default="expanded")
    parser.add_argument("--range-bound", type=int, default=200)
    parser.add_argument("--max-iter", type=int, default=30)
    parser.add_argument("--strategy", choices=["sequential", "batch"], default="sequential")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bootstrap", help='Bootstrap inputs, e.g. "x=1,y=2".')
    parser.add_argument("--skip-original", action="store_true", help="Do not run the original program.")
    parser.add_argument("--skip-mutants", action="store_true", help="Do not run mutant programs.")
    parser.add_argument("--skip-tbfv", action="store_true", help="Only run CSC generation.")
    parser.add_argument("--skip-localization", action="store_true", help="Do not run failure localization.")
    parser.add_argument("--skip-aggregation", action="store_true", help="Do not aggregate localization reports.")
    parser.add_argument("--skip-evaluation", action="store_true", help="Do not evaluate localization rankings.")
    parser.add_argument("--render-cct", action="store_true", help="Pass --render-cct to csc_tool.py.")
    parser.add_argument(
        "--render-localization",
        action="store_true",
        help="Render failure-localization CCT views.",
    )
    parser.add_argument("--stop-on-error", action="store_true", help="Stop after the first failed step.")
    parser.add_argument("--dry-run", action="store_true", help="Write the planned workflow without running commands.")
    return parser


def build_options(args: argparse.Namespace) -> ExperimentOptions:
    subject_dir = Path(args.subject_dir)
    project_dir = Path(args.project_dir)
    return ExperimentOptions(
        project_dir=project_dir,
        subject_dir=subject_dir,
        fsf_path=Path(args.fsf) if args.fsf else None,
        fsf_dir=Path(args.fsf_dir) if args.fsf_dir else None,
        manifest_path=Path(args.manifest) if args.manifest else None,
        original_file=Path(args.original_file) if args.original_file else None,
        mutant_ids=parse_mutant_ids(args.mutants),
        session_prefix=args.session_prefix,
        summary_root=Path(args.summary_root),
        mode=args.mode,
        range_bound=args.range_bound,
        max_iter=args.max_iter,
        strategy=args.strategy,
        workers=max(1, args.workers),
        bootstrap=args.bootstrap,
        run_original=not args.skip_original,
        run_mutants=not args.skip_mutants,
        run_tbfv=not args.skip_tbfv,
        run_localization=not args.skip_localization,
        run_aggregation=not args.skip_aggregation,
        run_evaluation=not args.skip_evaluation,
        render_cct=args.render_cct,
        render_localization=args.render_localization,
        stop_on_error=args.stop_on_error,
        dry_run=args.dry_run,
    )


def parse_mutant_ids(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or None


def print_summary(summary: dict, summary_path: Path) -> None:
    print("Subject experiment complete")
    print(f"  Subject:   {summary['subject']}")
    print(f"  Status:    {summary['status']}")
    print(f"  Dry run:   {summary['dry_run']}")
    print(f"  Steps:     {summary['step_count']}")
    print(f"  FSF:       {summary['fsf'] or '<default true/true>'}")
    print(f"  Summary:   {summary_path}")


if __name__ == "__main__":
    raise SystemExit(main())
