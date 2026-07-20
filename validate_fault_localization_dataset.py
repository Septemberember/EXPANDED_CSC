#!/usr/bin/env python3
"""Validate a fault-localization dataset before running experiments."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csc_engine import (
    validate_fault_localization_dataset,
    write_validation_json,
    write_validation_markdown,
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        dataset_root = Path(args.dataset_root)
        manifest = Path(args.manifest) if args.manifest else dataset_root / "mutants_manifest.jsonl"
        report = validate_fault_localization_dataset(dataset_root, manifest)
        if args.output_json:
            write_validation_json(report, args.output_json)
        if args.output_md:
            write_validation_markdown(report, args.output_md)
        print_summary(report, args, manifest)
        if args.fail_on_error and report["summary"]["error_count"] > 0:
            return 1
        return 0
    except Exception as exc:
        print(f"Fault localization dataset validation failed: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate manifest and file metadata for fault-localization experiments."
    )
    parser.add_argument(
        "--dataset-root",
        required=True,
        help="Dataset root directory, e.g. project/CSC_EXPANDED/dataset/EX_CSC_dataset.",
    )
    parser.add_argument(
        "--manifest",
        help="mutants_manifest.jsonl path. Defaults to <dataset-root>/mutants_manifest.jsonl.",
    )
    parser.add_argument(
        "--output-json",
        help="Write machine-readable validation report JSON.",
    )
    parser.add_argument(
        "--output-md",
        help="Write human-readable validation report Markdown.",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with code 1 when validation errors are found.",
    )
    return parser


def print_summary(report: dict, args: argparse.Namespace, manifest: Path) -> None:
    summary = report["summary"]
    print("Fault localization dataset validation complete")
    print(f"  Dataset:  {args.dataset_root}")
    print(f"  Manifest: {manifest}")
    print(f"  Status:   {summary['status']}")
    print(f"  Subjects: {summary['subject_count']}")
    print(f"  Mutants:  {summary['mutant_count']}")
    print(f"  Errors:   {summary['error_count']}")
    print(f"  Warnings: {summary['warning_count']}")
    if args.output_json:
        print(f"  JSON:     {args.output_json}")
    if args.output_md:
        print(f"  Markdown: {args.output_md}")


if __name__ == "__main__":
    raise SystemExit(main())

