#!/usr/bin/env python3
"""CLI wrapper for fault-localization evaluation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csc_engine import (
    DEFAULT_EVAL_TOP_K,
    evaluate_reports,
    find_mutant_record,
    load_json_report,
    load_manifest,
    validate_mutant_record,
    write_evaluation_report,
)


DEFAULT_OUTPUT_NAME = "fault_localization_eval.json"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        manifest = load_manifest(args.manifest)
        record = find_mutant_record(manifest, args.mutant_id)
        validate_mutant_record(record)

        raw_report = load_json_report(args.report) if args.report else None
        aggregated_report = (
            load_json_report(args.aggregated_report)
            if args.aggregated_report
            else None
        )
        if raw_report is None and aggregated_report is None:
            raise ValueError("At least one of --report or --aggregated-report is required")

        top_k = parse_top_k(args.top_k)
        evaluation = evaluate_reports(
            record,
            raw_report=raw_report,
            aggregated_report=aggregated_report,
            top_k=top_k,
        )
        output_path = resolve_output_path(args)
        write_evaluation_report(evaluation, output_path)
        print_summary(output_path, evaluation)
        return 0
    except Exception as exc:
        print(f"Fault localization evaluation failed: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate failure-localization rankings against a mutant manifest."
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="mutants_manifest.jsonl file.",
    )
    parser.add_argument(
        "--mutant-id",
        required=True,
        help="Mutant id to evaluate.",
    )
    parser.add_argument(
        "--report",
        help="Raw cct_failure_localization.json report.",
    )
    parser.add_argument(
        "--aggregated-report",
        help="Aggregated cct_failure_localization_aggregated.json report.",
    )
    parser.add_argument(
        "--top-k",
        default=",".join(str(k) for k in DEFAULT_EVAL_TOP_K),
        help="Comma-separated Top-k values (default: 1,3,5,10).",
    )
    parser.add_argument(
        "--output",
        help=f"Evaluation JSON path. Defaults to <report-dir>/{DEFAULT_OUTPUT_NAME}.",
    )
    return parser


def parse_top_k(raw: str) -> list[int]:
    values = []
    for item in raw.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        value = int(stripped)
        if value <= 0:
            raise ValueError("Top-k values must be positive integers")
        values.append(value)
    return values or list(DEFAULT_EVAL_TOP_K)


def resolve_output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return Path(args.output)
    base = args.aggregated_report or args.report
    return Path(base).parent / DEFAULT_OUTPUT_NAME


def print_summary(output_path: Path, evaluation: dict) -> None:
    print("Fault localization evaluation complete")
    print(f"  Output:    {output_path}")
    print(f"  Mutant:    {evaluation.get('mutant_id')}")
    print(f"  Operator:  {evaluation.get('operator') or '<unknown>'}")
    print(f"  Fault:     {evaluation.get('fault_kind') or '<unknown>'}")
    print(f"  Top-k:     {', '.join(str(k) for k in evaluation.get('summary', {}).get('top_k', []))}")
    for strategy, metrics in evaluation.get("metrics", {}).items():
        topk = metrics.get("topk", {})
        flags = ", ".join(
            f"{key}={'hit' if value else 'miss'}"
            for key, value in topk.items()
        )
        best_rank = metrics.get("best_rank")
        best = best_rank if best_rank is not None else "-"
        print(f"  {strategy}: best_rank={best}, {flags}")


if __name__ == "__main__":
    raise SystemExit(main())
