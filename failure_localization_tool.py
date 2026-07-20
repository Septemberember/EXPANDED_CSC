#!/usr/bin/env python3
"""CLI wrapper for read-only CCT-based failure localization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from csc_engine import (
    CCT,
    INTERVAL_STRATEGY_DESCRIPTIONS,
    build_localization_report,
    load_testcase_records,
    localization_dot_filename,
    write_localization_dot,
    write_localization_report,
)


DEFAULT_CCT_FORMATS = ("svg", "pdf")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.list_strategies:
            print_strategies()
            return 0
        config = resolve_config(args)
        cct = CCT.load_from_file(str(config["cct_path"]))
        if cct is None:
            raise FileNotFoundError(f"CCT not found: {config['cct_path']}")

        report = build_localization_report(
            cct,
            top_k=args.top_k,
            testcase_records=config["records"],
            default_interval_strategy=args.edge_strategy,
        )
        write_localization_report(report, config["output_path"])
        edge_strategy = args.edge_strategy or report["summary"]["default_interval_strategy"]
        dot_output_path = resolve_dot_output_path(args, config["output_path"], edge_strategy)
        config["dot_output_path"] = dot_output_path
        config["edge_strategy"] = edge_strategy
        write_localization_dot(cct, report, dot_output_path, interval_strategy=edge_strategy)
        rendered = {}
        if args.render_cct:
            rendered = render_dot_artifacts(
                dot_output_path,
                parse_cct_formats(args.cct_formats),
            )
        print_summary(report, config, rendered)
        return 0
    except Exception as exc:
        print(f"Failure localization failed: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    strategy_names = sorted(INTERVAL_STRATEGY_DESCRIPTIONS)
    parser = argparse.ArgumentParser(
        description="Rank suspicious CCT condition nodes and condition intervals."
    )
    parser.add_argument(
        "--csc-result-dir",
        help="CSC result artifact directory, e.g. csc_tmp/session/ClassName.",
    )
    parser.add_argument(
        "--cct",
        help="Annotated CCT pickle. Defaults to <csc-result-dir>/<ClassName>_cct.pkl.",
    )
    parser.add_argument(
        "--class",
        "--class-name",
        dest="class_name",
        help="Target class name. Inferred from run_log, result dir, or CCT name when possible.",
    )
    parser.add_argument(
        "--output",
        help="Report JSON path. Defaults to <csc-result-dir>/cct_failure_localization.json.",
    )
    parser.add_argument(
        "--dot-output",
        help="Risk-view DOT path. Defaults to cct_failure_localization_<strategy>.dot.",
    )
    parser.add_argument(
        "--edge-strategy",
        "--failure-localization-edge-strategy",
        choices=strategy_names,
        help="Interval edge strategy to use for the DOT view and compatibility ranking.",
    )
    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="List available interval edge strategies and exit.",
    )
    parser.add_argument(
        "--no-statement-aware",
        action="store_true",
        help="Do not read testcases.json traces; only compute the cct_only interval strategy.",
    )
    parser.add_argument(
        "--render-cct",
        action="store_true",
        help="Render the localization DOT view during this run.",
    )
    parser.add_argument(
        "--cct-formats",
        default=",".join(DEFAULT_CCT_FORMATS),
        help="Comma-separated formats for --render-cct (default: svg,pdf).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        help="Keep only the top K records in each ranking while preserving total candidate counts.",
    )
    return parser


def resolve_config(args: argparse.Namespace) -> dict[str, Any]:
    csc_result_dir = Path(args.csc_result_dir) if args.csc_result_dir else None
    class_name = resolve_class_name(args, csc_result_dir)
    cct_path = resolve_cct_path(args, csc_result_dir, class_name)
    output_path = resolve_output_path(args, csc_result_dir, cct_path)
    records = resolve_testcase_records(args, csc_result_dir)
    return {
        "csc_result_dir": csc_result_dir,
        "class_name": class_name,
        "cct_path": cct_path,
        "output_path": output_path,
        "dot_output_path": None,
        "records": records,
        "edge_strategy": None,
    }


def resolve_class_name(args: argparse.Namespace, csc_result_dir: Path | None) -> str | None:
    if args.class_name:
        return args.class_name

    if csc_result_dir is not None:
        run_start = load_run_start(csc_result_dir / "run_log.jsonl")
        if run_start.get("classname"):
            return str(run_start["classname"])
        return csc_result_dir.name

    if args.cct:
        stem = Path(args.cct).stem
        return stem[:-4] if stem.endswith("_cct") else stem
    return None


def resolve_cct_path(args: argparse.Namespace,
                     csc_result_dir: Path | None,
                     class_name: str | None) -> Path:
    if args.cct:
        return Path(args.cct)
    if csc_result_dir is None:
        raise ValueError("--csc-result-dir or --cct is required")

    if class_name:
        candidate = csc_result_dir / f"{class_name}_cct.pkl"
        if candidate.exists():
            return candidate

    candidates = sorted(csc_result_dir.glob("*_cct.pkl"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise FileNotFoundError(f"No *_cct.pkl found in {csc_result_dir}")
    raise ValueError(
        f"Multiple CCT files found in {csc_result_dir}; pass --class or --cct explicitly"
    )


def resolve_output_path(args: argparse.Namespace,
                        csc_result_dir: Path | None,
                        cct_path: Path) -> Path:
    if args.output:
        return Path(args.output)
    if csc_result_dir is not None:
        return csc_result_dir / "cct_failure_localization.json"
    return cct_path.with_name("cct_failure_localization.json")


def resolve_dot_output_path(args: argparse.Namespace,
                            output_path: Path,
                            edge_strategy: str) -> Path:
    if args.dot_output:
        return Path(args.dot_output)
    return output_path.with_name(localization_dot_filename(edge_strategy))


def resolve_testcase_records(args: argparse.Namespace,
                             csc_result_dir: Path | None) -> list[dict[str, Any]] | None:
    if args.no_statement_aware or csc_result_dir is None:
        return None
    candidate = csc_result_dir / "testcases.json"
    if not candidate.exists():
        return None
    return load_testcase_records(candidate)


def parse_cct_formats(raw: str) -> list[str]:
    formats = []
    for item in raw.split(","):
        fmt = item.strip().lower().lstrip(".")
        if fmt:
            formats.append(fmt)
    allowed = {"svg", "pdf", "png", "jpg", "jpeg"}
    unsupported = [fmt for fmt in formats if fmt not in allowed]
    if unsupported:
        raise ValueError(f"Unsupported CCT render format(s): {', '.join(unsupported)}")
    return formats or list(DEFAULT_CCT_FORMATS)


def render_dot_artifacts(dot_path: Path, formats: list[str]) -> dict[str, str]:
    renderer = CCT()
    rendered = {}
    for fmt in formats:
        output_path = renderer.render_dot(str(dot_path), fmt, label="Failure localization")
        if output_path:
            rendered[fmt] = output_path
    return rendered


def load_run_start(run_log: Path) -> dict[str, Any]:
    if not run_log.exists():
        return {}

    latest: dict[str, Any] = {}
    for line in run_log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("event") == "run_start":
            latest = record
    return latest


def print_strategies() -> None:
    print("Available interval edge strategies:")
    for name in sorted(INTERVAL_STRATEGY_DESCRIPTIONS):
        print(f"  {name}")
        print(f"    {INTERVAL_STRATEGY_DESCRIPTIONS[name]}")


def print_summary(report: dict[str, Any],
                  config: dict[str, Any],
                  rendered: dict[str, str]) -> None:
    summary = report["summary"]
    print("Failure localization complete")
    print(f"  CSC result:  {config['csc_result_dir'] or '<not provided>'}")
    print(f"  CCT:         {config['cct_path']}")
    print(f"  Report:      {config['output_path']}")
    print(f"  Risk DOT:    {config['dot_output_path']}")
    print(f"  Edge strategy: {config['edge_strategy']}")
    print(
        "  Summary:     "
        f"executed={summary['executed_cases']}, "
        f"failed={summary['failed_cases']}, "
        f"condition_nodes={summary['condition_node_candidates']}, "
        f"condition_intervals={summary['condition_interval_candidates']}"
    )
    print_top_records("  Top conditions:", report["condition_node_ranking"])
    print_top_records("  Top intervals:", report["condition_interval_ranking"])
    for fmt, path in rendered.items():
        print(f"  {fmt.upper()}:         {path}")


def print_top_records(title: str, records: list[dict[str, Any]], limit: int = 3) -> None:
    if not records:
        print(f"{title} <none>")
        return
    print(title)
    for record in records[:limit]:
        label = record.get("condition") or record.get("edge_id")
        line_info = record.get("line_interval", record.get("line"))
        print(
            f"    #{record['rank']} score={record['risk_score']:.4f} "
            f"fail={record['fail_count']}/{record['exec_count']} "
            f"line={line_info} {label}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
