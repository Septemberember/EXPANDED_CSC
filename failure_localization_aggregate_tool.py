#!/usr/bin/env python3
"""CLI wrapper for aggregating CCT failure-localization reports."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csc_engine import (
    CONDITION_NODE_TARGET,
    DEFAULT_SCORE_AGGREGATION,
    INTERVAL_TARGET_PREFIX,
    aggregate_localization_report,
    load_localization_report,
    write_aggregated_localization_report,
)


DEFAULT_OUTPUT_NAME = "cct_failure_localization_aggregated.json"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        report_path = Path(args.report)
        report = load_localization_report(report_path)
        targets = parse_targets(args.targets)
        aggregated = aggregate_localization_report(
            report,
            source_file=args.source_file,
            targets=targets,
            score_aggregation=args.score_aggregation,
            source_report=str(report_path),
        )
        output_path = resolve_output_path(args, report_path)
        write_aggregated_localization_report(aggregated, output_path)
        print_summary(output_path, aggregated)
        return 0
    except Exception as exc:
        print(f"Failure localization aggregation failed: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate dynamic CCT failure-localization rankings by source locations."
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Raw cct_failure_localization.json report.",
    )
    parser.add_argument(
        "--output",
        help=f"Aggregated report path. Defaults to <report-dir>/{DEFAULT_OUTPUT_NAME}.",
    )
    parser.add_argument(
        "--source-file",
        help="Source file associated with this report, used as source-level context.",
    )
    parser.add_argument(
        "--targets",
        help=(
            "Comma-separated targets. Examples: "
            f"{CONDITION_NODE_TARGET},{INTERVAL_TARGET_PREFIX}statement_presence,"
            f"{INTERVAL_TARGET_PREFIX}edge_divergence_gated"
        ),
    )
    parser.add_argument(
        "--score-aggregation",
        default=DEFAULT_SCORE_AGGREGATION,
        help=f"Score aggregation method (default: {DEFAULT_SCORE_AGGREGATION}).",
    )
    return parser


def parse_targets(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def resolve_output_path(args: argparse.Namespace, report_path: Path) -> Path:
    if args.output:
        return Path(args.output)
    return report_path.parent / DEFAULT_OUTPUT_NAME


def print_summary(output_path: Path, report: dict) -> None:
    summary = report["summary"]
    print("Failure localization aggregation complete")
    print(f"  Output:      {output_path}")
    print(f"  Source file: {summary.get('source_file') or '<not provided>'}")
    print(f"  Targets:     {', '.join(summary.get('targets', []))}")
    print(
        "  Conditions:  "
        f"{summary.get('condition_node_count_raw', 0)} raw -> "
        f"{summary.get('condition_node_count_aggregated', 0)} aggregated"
    )
    interval_raw = summary.get("interval_count_raw", {})
    interval_agg = summary.get("interval_count_aggregated", {})
    for strategy in interval_raw:
        print(
            f"  Intervals[{strategy}]: "
            f"{interval_raw[strategy]} raw -> {interval_agg.get(strategy, 0)} aggregated"
        )


if __name__ == "__main__":
    raise SystemExit(main())
