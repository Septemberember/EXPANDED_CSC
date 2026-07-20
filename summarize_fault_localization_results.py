#!/usr/bin/env python3
"""Summarize fault-localization evaluation reports into experiment tables."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csc_engine import (
    DEFAULT_FL_SUMMARY_EVAL_GLOB,
    DEFAULT_FL_SUMMARY_TOP_K,
    discover_evaluation_reports,
    load_manifest,
    summarize_fault_localization_results,
    write_csv_rows,
    write_jsonl_rows,
    write_markdown_summary,
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        manifest = load_manifest(args.manifest)
        evaluation_paths = discover_evaluation_reports(args.results_root, args.eval_glob)
        top_k = parse_top_k(args.top_k)
        report = summarize_fault_localization_results(
            manifest,
            evaluation_paths,
            top_k=top_k,
        )
        if args.output_jsonl:
            write_jsonl_rows(report["rows"], args.output_jsonl)
        if args.output_csv:
            write_csv_rows(report["rows"], args.output_csv)
        if args.output_md:
            write_markdown_summary(report, args.output_md)
        print_summary(report, args, evaluation_paths)
        return 0
    except Exception as exc:
        print(f"Fault localization summary failed: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize fault-localization evaluation reports."
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="mutants_manifest.jsonl file.",
    )
    parser.add_argument(
        "--results-root",
        required=True,
        help="Directory to scan for fault_localization_eval.json files.",
    )
    parser.add_argument(
        "--eval-glob",
        default=DEFAULT_FL_SUMMARY_EVAL_GLOB,
        help=f"Glob under --results-root (default: {DEFAULT_FL_SUMMARY_EVAL_GLOB}).",
    )
    parser.add_argument(
        "--top-k",
        default=",".join(str(k) for k in DEFAULT_FL_SUMMARY_TOP_K),
        help="Comma-separated Top-k values to summarize (default: 1,3,5,10).",
    )
    parser.add_argument(
        "--output-jsonl",
        help="Flat per-mutant/per-strategy JSONL output.",
    )
    parser.add_argument(
        "--output-csv",
        help="Flat per-mutant/per-strategy CSV output.",
    )
    parser.add_argument(
        "--output-md",
        help="Markdown strategy summary output.",
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
    return values or list(DEFAULT_FL_SUMMARY_TOP_K)


def print_summary(report: dict, args: argparse.Namespace, evaluation_paths: list[Path]) -> None:
    summary = report["summary"]
    print("Fault localization summary complete")
    print(f"  Manifest:       {args.manifest}")
    print(f"  Results root:   {args.results_root}")
    print(f"  Reports found:  {len(evaluation_paths)}")
    print(f"  Rows:           {summary['row_count']}")
    print(f"  Evaluated:      {summary['evaluated_mutant_count']}")
    print(f"  Missing:        {summary['missing_result_count']}")
    if args.output_jsonl:
        print(f"  JSONL:          {args.output_jsonl}")
    if args.output_csv:
        print(f"  CSV:            {args.output_csv}")
    if args.output_md:
        print(f"  Markdown:       {args.output_md}")


if __name__ == "__main__":
    raise SystemExit(main())

