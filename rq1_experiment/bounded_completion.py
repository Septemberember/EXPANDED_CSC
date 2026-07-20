"""RQ1 bounded-completion experiments for CSC-only and CSC+Boundary.

The current paired protocol runs both configurations with the same sequential
scheduler and budget.  The legacy summary functions remain available for
reproducing the earlier CSC-only versus batch-W=1 tables.
"""

from __future__ import annotations

import csv
import json
import re
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

# Reuse discovery and I/O utilities from the RQ2 experiment package.
from csc_experiments.parallel_generation import (
    OriginalProgram,
    discover_original_programs,
    read_jsonl,
    append_jsonl,
    write_json,
    write_csv,
    write_text,
    archive_generation_artifacts,
    _safe_id,
    _now,
    _tail,
    _fmt,
    _mean,
    _median,
    _load_json_if_exists,
    _split_run_log,
    _last_event,
)

CONFIG_JSON = "rq1_config.json"
RUNS_JSONL = "rq1_csc_only_runs.jsonl"
COMPARISON_JSON = "rq1_comparison.json"
COMPARISON_CSV = "rq1_comparison.csv"
COMPARISON_MD = "rq1_comparison.md"
PAIRED_CONFIG_JSON = "rq1_paired_config.json"
PAIRED_RUNS_JSONL = "rq1_paired_runs.jsonl"
PAIRED_SUMMARY_JSON = "rq1_paired_summary.json"
PAIRED_SUMMARY_CSV = "rq1_paired_subjects.csv"
PAIRED_SUMMARY_MD = "rq1_paired_summary.md"


# ---------------------------------------------------------------------------
# Run one CSC-only generation
# ---------------------------------------------------------------------------

def run_csc_only(
    program: OriginalProgram,
    *,
    session_id: str,
    project_root: Path,
    experiment_dir: Path,
    max_iter: int = 2000,
    timeout_s: Optional[int] = None,
    dry_run: bool = False,
    allow_existing_session: bool = False,
) -> dict[str, Any]:
    """Run csc_tool.py once in CSC-only sequential mode and archive artifacts."""

    return _run_sequential_generation(
        program,
        stage="rq1_csc_only_run",
        configuration="csc_only",
        mode="original",
        range_bound=None,
        session_id=session_id,
        project_root=project_root,
        experiment_dir=experiment_dir,
        max_iter=max_iter,
        timeout_s=timeout_s,
        dry_run=dry_run,
        allow_existing_session=allow_existing_session,
    )


def run_csc_boundary_sequential(
    program: OriginalProgram,
    *,
    session_id: str,
    project_root: Path,
    experiment_dir: Path,
    range_bound: int = 200,
    max_iter: int = 2000,
    timeout_s: Optional[int] = None,
    dry_run: bool = False,
    allow_existing_session: bool = False,
) -> dict[str, Any]:
    """Run CSC+Boundary with the one-obligation-at-a-time sequential strategy."""

    return _run_sequential_generation(
        program,
        stage="rq1_paired_run",
        configuration="csc_boundary",
        mode="expanded",
        range_bound=range_bound,
        session_id=session_id,
        project_root=project_root,
        experiment_dir=experiment_dir,
        max_iter=max_iter,
        timeout_s=timeout_s,
        dry_run=dry_run,
        allow_existing_session=allow_existing_session,
    )


def _run_sequential_generation(
    program: OriginalProgram,
    *,
    stage: str,
    configuration: str,
    mode: str,
    range_bound: Optional[int],
    session_id: str,
    project_root: Path,
    experiment_dir: Path,
    max_iter: int,
    timeout_s: Optional[int],
    dry_run: bool,
    allow_existing_session: bool,
) -> dict[str, Any]:
    """Run one fresh sequential generation configuration and archive its artifacts."""

    csc_tool = project_root / "csc_tool.py"
    result_dir = project_root / "csc_tmp" / session_id / program.class_name
    if result_dir.exists() and not allow_existing_session:
        raise FileExistsError(
            f"Session result already exists: {result_dir}. "
            "Use a fresh --session-prefix or pass --allow-existing-sessions."
        )
    command = [
        sys.executable,
        str(csc_tool),
        str(program.java_file),
        "--mode",
        mode,
        "--strategy",
        "sequential",
        "--max-iter",
        str(max_iter),
        "--session",
        session_id,
        "--keep-artifacts",
    ]
    if range_bound is not None:
        command.extend(["--range-bound", str(range_bound)])
    started_at = _now()
    started = time.perf_counter()
    completed = None
    timed_out = False
    if dry_run:
        returncode = 0
        stdout = ""
        stderr = ""
    else:
        try:
            completed = subprocess.run(
                command,
                cwd=project_root,
                text=True,
                capture_output=True,
                timeout=timeout_s,
                check=False,
            )
            returncode = completed.returncode
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            timed_out = True
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
    wall_time_s = time.perf_counter() - started

    archive_dir = experiment_dir / "artifacts" / session_id / program.class_name
    archived = archive_generation_artifacts(result_dir, archive_dir)
    write_text(archive_dir / "stdout.txt", stdout)
    write_text(archive_dir / "stderr.txt", stderr)

    return {
        "stage": stage,
        "configuration": configuration,
        "subject": program.subject,
        "class_name": program.class_name,
        "java_file": str(program.java_file),
        "mode": mode,
        "strategy": "sequential",
        "range_bound": range_bound,
        "session": session_id,
        "max_iter": max_iter,
        "command": command,
        "started_at": started_at,
        "finished_at": _now(),
        "wall_time_s": wall_time_s,
        "returncode": returncode,
        "timed_out": timed_out,
        "result_dir": str(result_dir),
        "archive_dir": str(archive_dir),
        "archived_files": archived,
        "stdout_tail": _tail(stdout),
        "stderr_tail": _tail(stderr),
    }


# ---------------------------------------------------------------------------
# Run all CSC-only programs
# ---------------------------------------------------------------------------

def run_rq1_experiment(
    dataset_root: str | Path,
    experiment_dir: str | Path,
    *,
    max_iter: int = 2000,
    timeout_s: Optional[int] = None,
    session_prefix: Optional[str] = None,
    project_root: Optional[str | Path] = None,
    dry_run: bool = False,
    allow_existing_sessions: bool = False,
) -> dict[str, Any]:
    """Run CSC-only generation for all original programs under ``dataset_root``."""

    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    dataset = _resolve_path(dataset_root, root)
    out_dir = _resolve_path(experiment_dir, root)
    out_dir.mkdir(parents=True, exist_ok=True)

    programs = discover_original_programs(dataset)
    prefix = session_prefix or _default_session_prefix()
    config = {
        "stage": "rq1_csc_only_experiment",
        "created_at": _now(),
        "dataset_root": str(dataset),
        "experiment_dir": str(out_dir),
        "project_root": str(root),
        "mode": "original",
        "strategy": "sequential",
        "max_iter": max_iter,
        "timeout_s": timeout_s,
        "session_prefix": prefix,
        "dry_run": dry_run,
        "allow_existing_sessions": allow_existing_sessions,
        "program_count": len(programs),
        "programs": [
            {
                "subject": program.subject,
                "class_name": program.class_name,
                "java_file": str(program.java_file),
            }
            for program in programs
        ],
    }
    write_json(out_dir / CONFIG_JSON, config)

    runs_path = out_dir / RUNS_JSONL
    if runs_path.exists():
        raise FileExistsError(
            f"Run record already exists: {runs_path}. "
            "Use a new experiment directory."
        )
    run_records: list[dict[str, Any]] = []
    for program in programs:
        session_id = _safe_id(f"{prefix}_{program.subject}_{program.class_name}")
        record = run_csc_only(
            program,
            session_id=session_id,
            project_root=root,
            experiment_dir=out_dir,
            max_iter=max_iter,
            timeout_s=timeout_s,
            dry_run=dry_run,
            allow_existing_session=allow_existing_sessions,
        )
        run_records.append(record)
        append_jsonl(runs_path, record)

    return {
        "config": config,
        "runs": run_records,
        "runs_jsonl": str(runs_path),
    }


# ---------------------------------------------------------------------------
# Enrich run records with RQ1-specific leaf-distribution metrics
# ---------------------------------------------------------------------------

def enrich_rq1_record(record: dict[str, Any]) -> dict[str, Any]:
    """Attach CCT stats and leaf-distribution metrics for one run record."""

    row = dict(record)
    archive_dir = Path(row.get("archive_dir", ""))
    cct_stats = _load_json_if_exists(archive_dir / "cct_stats.json")
    fingerprint = _load_json_if_exists(archive_dir / "generation_fingerprint.json")
    run_log = read_jsonl(archive_dir / "run_log.jsonl") if (archive_dir / "run_log.jsonl").is_file() else []
    run_segments = _split_run_log(run_log)
    current_run_log = run_segments[-1] if run_segments else run_log
    current_summary = _last_event(current_run_log, "run_summary")
    reached_cct_full = any(event.get("event") == "cct_full" for event in current_run_log)

    row["completed"] = bool(row.get("returncode") == 0 and cct_stats)
    row["normal_completion"] = bool(row["completed"] and reached_cct_full)
    row["budget_terminated"] = bool(
        row["completed"] and current_summary and not reached_cct_full
    )
    row["run_start_count"] = len(run_segments)
    row["new_testcases_in_run"] = current_summary.get("generated_count")
    row["fresh_generation"] = bool(row.get("completed") and (row.get("new_testcases_in_run") or 0) > 0)

    cct = cct_stats.get("cct", {}) if cct_stats else {}
    testcase_stats = cct_stats.get("testcases", {}) if cct_stats else {}

    # Core RQ1 leaf-distribution metrics
    for key in (
        "total_nodes",
        "internal_nodes",
        "leaf_nodes",
        "covered_leaves",
        "infeasible_leaves",
        "out_of_range_leaves",
        "empty_leaves",
        "expanded_leaves",
        "valid_testcases",
        "max_depth",
    ):
        row[key] = cct.get(key)

    row["generated_records"] = testcase_stats.get("generated_records")
    row["executable_records"] = testcase_stats.get("executable_records")
    row["trace_backed_records"] = testcase_stats.get("trace_backed_records")
    row["testcase_count"] = row.get("valid_testcases") or row.get("executable_records")
    for key in (
        "cct_structure_sha256",
        "cct_semantic_sha256",
        "test_inputs_sha256",
        "concrete_input_count",
    ):
        row[key] = fingerprint.get(key)
    return row


# ---------------------------------------------------------------------------
# Scheduler-matched paired protocol
# ---------------------------------------------------------------------------

def run_paired_rq1_experiment(
    dataset_roots: Iterable[str | Path],
    experiment_dir: str | Path,
    *,
    repeats: int = 3,
    range_bound: int = 200,
    max_iter: int = 2000,
    timeout_s: Optional[int] = None,
    session_prefix: Optional[str] = None,
    project_root: Optional[str | Path] = None,
    dry_run: bool = False,
    allow_existing_sessions: bool = False,
) -> dict[str, Any]:
    """Run scheduler-matched CSC-only/CSC+Boundary pairs on all subjects."""

    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    datasets = [_resolve_path(path, root) for path in dataset_roots]
    out_dir = _resolve_path(experiment_dir, root)
    out_dir.mkdir(parents=True, exist_ok=True)
    programs = _discover_unique_programs(datasets)
    prefix = session_prefix or "rq1_paired_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    config = {
        "stage": "rq1_paired_experiment",
        "created_at": _now(),
        "dataset_roots": [str(path) for path in datasets],
        "experiment_dir": str(out_dir),
        "project_root": str(root),
        "configurations": {
            "csc_only": {"mode": "original", "strategy": "sequential"},
            "csc_boundary": {
                "mode": "expanded",
                "strategy": "sequential",
                "range_bound": range_bound,
            },
        },
        "repeats": repeats,
        "max_iter": max_iter,
        "timeout_s": timeout_s,
        "session_prefix": prefix,
        "dry_run": dry_run,
        "allow_existing_sessions": allow_existing_sessions,
        "program_count": len(programs),
        "programs": [
            {
                "subject": program.subject,
                "class_name": program.class_name,
                "java_file": str(program.java_file),
                "structural_class": _structural_class(program.java_file),
            }
            for program in programs
        ],
    }
    write_json(out_dir / PAIRED_CONFIG_JSON, config)
    from csc_experiments.rq2_parallel import collect_environment
    write_json(out_dir / "environment.json", collect_environment(root))

    runs_path = out_dir / PAIRED_RUNS_JSONL
    if runs_path.exists():
        raise FileExistsError(f"Run record already exists: {runs_path}. Use a new experiment directory.")

    records: list[dict[str, Any]] = []
    for repeat in range(1, repeats + 1):
        # Reverse the order on alternate repetitions to reduce fixed order bias.
        configurations = ("csc_only", "csc_boundary") if repeat % 2 else ("csc_boundary", "csc_only")
        for program in programs:
            for configuration in configurations:
                session_id = _safe_id(
                    f"{prefix}_r{repeat}_{program.subject}_{program.class_name}_{configuration}"
                )
                common = {
                    "session_id": session_id,
                    "project_root": root,
                    "experiment_dir": out_dir,
                    "max_iter": max_iter,
                    "timeout_s": timeout_s,
                    "dry_run": dry_run,
                    "allow_existing_session": allow_existing_sessions,
                }
                if configuration == "csc_only":
                    record = run_csc_only(program, **common)
                else:
                    record = run_csc_boundary_sequential(
                        program,
                        range_bound=range_bound,
                        **common,
                    )
                record["stage"] = "rq1_paired_run"
                record["repeat"] = repeat
                record["structural_class"] = _structural_class(program.java_file)
                records.append(record)
                append_jsonl(runs_path, record)

    return {"config": config, "runs": records, "runs_jsonl": str(runs_path)}


def summarize_paired_rq1(
    runs_jsonl: str | Path,
    *,
    output_dir: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Summarize scheduler-matched pairs without conflating budget termination with completion."""

    runs_path = Path(runs_jsonl)
    out_dir = Path(output_dir) if output_dir is not None else runs_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [enrich_rq1_record(record) for record in read_jsonl(runs_path)]

    by_key: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row["subject"]), int(row.get("repeat", 1)), str(row["configuration"]))
        if key in by_key:
            raise ValueError(f"Duplicate paired RQ1 run: {key}")
        by_key[key] = row

    subjects = sorted({str(row["subject"]) for row in rows})
    subject_rows: list[dict[str, Any]] = []
    for subject in subjects:
        subject_runs = [row for row in rows if row["subject"] == subject]
        repeats = sorted({int(row.get("repeat", 1)) for row in subject_runs})
        valid_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for repeat in repeats:
            original = by_key.get((subject, repeat, "csc_only"))
            boundary = by_key.get((subject, repeat, "csc_boundary"))
            if _is_valid_paired_run(original) and _is_valid_paired_run(boundary):
                valid_pairs.append((original, boundary))

        reference = valid_pairs[0] if valid_pairs else (None, None)
        original_ref, boundary_ref = reference
        structural_class = subject_runs[0].get("structural_class", "unknown")
        item: dict[str, Any] = {
            "subject": subject,
            "structural_class": structural_class,
            "planned_pairs": len(repeats),
            "valid_pairs": len(valid_pairs),
            "all_pairs_completed": len(valid_pairs) == len(repeats),
        }
        for label, index in (("csc_only", 0), ("csc_boundary", 1)):
            valid_runs = [pair[index] for pair in valid_pairs]
            ref = original_ref if index == 0 else boundary_ref
            item[f"{label}_normal_completions"] = sum(
                1 for row in subject_runs
                if row.get("configuration") == label and row.get("normal_completion")
            )
            item[f"{label}_budget_terminations"] = sum(
                1 for row in subject_runs
                if row.get("configuration") == label and row.get("budget_terminated")
            )
            item[f"{label}_median_time_s"] = _median(row.get("wall_time_s") for row in valid_runs)
            for metric in _RQ1_STRUCTURE_METRICS:
                item[f"{label}_{metric}"] = ref.get(metric) if ref else None
                values = {row.get(metric) for row in valid_runs}
                item[f"{label}_{metric}_stable"] = len(values) <= 1

        item["time_ratio_boundary_over_csc"] = _safe_ratio(
            item.get("csc_boundary_median_time_s"), item.get("csc_only_median_time_s")
        )
        for metric in _RQ1_STRUCTURE_METRICS:
            item[f"delta_{metric}"] = _numeric_delta(
                item.get(f"csc_only_{metric}"), item.get(f"csc_boundary_{metric}")
            )
        subject_rows.append(item)

    aggregate_rows = _aggregate_paired_subjects(subject_rows)
    report = {
        "stage": "rq1_paired_summary",
        "created_at": _now(),
        "runs_jsonl": str(runs_path),
        "run_count": len(rows),
        "normal_completion_count": sum(1 for row in rows if row.get("normal_completion")),
        "budget_termination_count": sum(1 for row in rows if row.get("budget_terminated")),
        "failed_or_timeout_count": sum(1 for row in rows if not row.get("completed")),
        "fresh_generation_count": sum(1 for row in rows if row.get("fresh_generation")),
        "subject_count": len(subject_rows),
        "fully_paired_subject_count": sum(1 for row in subject_rows if row["all_pairs_completed"]),
        "subjects": subject_rows,
        "aggregate": aggregate_rows,
        "runs": rows,
    }
    write_json(out_dir / PAIRED_SUMMARY_JSON, report)
    write_csv(out_dir / PAIRED_SUMMARY_CSV, subject_rows)
    write_text(out_dir / PAIRED_SUMMARY_MD, render_paired_rq1_markdown(report))
    return report


_RQ1_STRUCTURE_METRICS = (
    "testcase_count",
    "total_nodes",
    "leaf_nodes",
    "covered_leaves",
    "empty_leaves",
    "infeasible_leaves",
    "out_of_range_leaves",
    "expanded_leaves",
    "max_depth",
)


def _is_valid_paired_run(row: Optional[dict[str, Any]]) -> bool:
    return bool(row and row.get("normal_completion") and row.get("fresh_generation"))


def _aggregate_paired_subjects(subject_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregates: list[dict[str, Any]] = []
    for structural_class in ("loop-free", "loop-bearing", "all"):
        group = [
            row for row in subject_rows
            if row.get("all_pairs_completed")
            and (structural_class == "all" or row.get("structural_class") == structural_class)
        ]
        if not group:
            continue
        aggregate: dict[str, Any] = {
            "structural_class": structural_class,
            "subjects": len(group),
            "planned_pairs": sum(int(row["planned_pairs"]) for row in group),
            "valid_pairs": sum(int(row["valid_pairs"]) for row in group),
        }
        for label in ("csc_only", "csc_boundary"):
            aggregate[f"mean_{label}_time_s"] = _mean(
                row.get(f"{label}_median_time_s") for row in group
            )
            aggregate[f"median_{label}_time_s"] = _median(
                row.get(f"{label}_median_time_s") for row in group
            )
            for metric in _RQ1_STRUCTURE_METRICS:
                aggregate[f"mean_{label}_{metric}"] = _mean(
                    row.get(f"{label}_{metric}") for row in group
                )
        aggregate["median_time_ratio_boundary_over_csc"] = _median(
            row.get("time_ratio_boundary_over_csc") for row in group
        )
        for metric in _RQ1_STRUCTURE_METRICS:
            aggregate[f"mean_delta_{metric}"] = _mean(
                row.get(f"delta_{metric}") for row in group
            )
        aggregates.append(aggregate)
    return aggregates


def render_paired_rq1_markdown(report: dict[str, Any]) -> str:
    """Render the compact paper-facing paired RQ1 summary."""

    lines = [
        "# Scheduler-Matched RQ1 Summary",
        "",
        f"- Runs: {report['run_count']}",
        f"- Normal completions: {report['normal_completion_count']}",
        f"- Budget terminations: {report['budget_termination_count']}",
        f"- Failed or timed out: {report['failed_or_timeout_count']}",
        f"- Fully paired subjects: {report['fully_paired_subject_count']}/{report['subject_count']}",
        "",
        "## Aggregate Results",
        "",
    ]
    headers = [
        "Class", "Subjects", "Pairs", "CSC Tests", "Boundary Tests",
        "CSC Nodes", "Boundary Nodes", "CSC Time (s)", "Boundary Time (s)",
        "Median Time Ratio",
    ]
    lines.extend(_markdown_table(headers, [
        [
            row["structural_class"], row["subjects"], row["valid_pairs"],
            _fmt(row.get("mean_csc_only_testcase_count")),
            _fmt(row.get("mean_csc_boundary_testcase_count")),
            _fmt(row.get("mean_csc_only_total_nodes")),
            _fmt(row.get("mean_csc_boundary_total_nodes")),
            _fmt(row.get("mean_csc_only_time_s")),
            _fmt(row.get("mean_csc_boundary_time_s")),
            _fmt(row.get("median_time_ratio_boundary_over_csc")),
        ]
        for row in report.get("aggregate", [])
    ]))
    lines.extend(["", "## Per-Subject Completion", ""])
    lines.extend(_markdown_table(
        ["Subject", "Class", "Valid/Planned", "CSC Tests", "Boundary Tests", "Time Ratio"],
        [
            [
                row["subject"], row["structural_class"],
                f"{row['valid_pairs']}/{row['planned_pairs']}",
                row.get("csc_only_testcase_count"), row.get("csc_boundary_testcase_count"),
                _fmt(row.get("time_ratio_boundary_over_csc")),
            ]
            for row in report.get("subjects", [])
        ],
    ))
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Build comparison tables
# ---------------------------------------------------------------------------

def build_per_subject_comparison(
    rq1_rows: list[dict[str, Any]],
    rq2_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build one row per subject per mode for the per-subject comparison table."""

    comparison: list[dict[str, Any]] = []

    # CSC-only rows (from RQ1)
    for row in rq1_rows:
        if not row.get("completed"):
            continue
        comparison.append({
            "subject": row["subject"],
            "mode": "CSC-only",
            "tests": row.get("valid_testcases"),
            "total_nodes": row.get("total_nodes"),
            "internal_nodes": row.get("internal_nodes"),
            "leaf_nodes": row.get("leaf_nodes"),
            "covered_leaves": row.get("covered_leaves"),
            "infeasible_leaves": row.get("infeasible_leaves"),
            "out_of_range_leaves": row.get("out_of_range_leaves"),
            "empty_leaves": row.get("empty_leaves"),
            "expanded_leaves": row.get("expanded_leaves"),
            "max_depth": row.get("max_depth"),
            "wall_time_s": row.get("wall_time_s"),
        })

    # CSC+Boundary rows (from RQ2 W=1)
    for row in rq2_rows:
        if not row.get("completed"):
            continue
        if int(row.get("workers", 0)) != 1:
            continue
        comparison.append({
            "subject": row["subject"],
            "mode": "CSC+Boundary",
            "tests": row.get("valid_testcases"),
            "total_nodes": row.get("total_nodes"),
            "internal_nodes": row.get("internal_nodes"),
            "leaf_nodes": row.get("leaf_nodes"),
            "covered_leaves": row.get("covered_leaves"),
            "infeasible_leaves": row.get("infeasible_leaves"),
            "out_of_range_leaves": row.get("out_of_range_leaves"),
            "empty_leaves": row.get("empty_leaves"),
            "expanded_leaves": row.get("expanded_leaves"),
            "max_depth": row.get("max_depth"),
            "wall_time_s": row.get("wall_time_s"),
        })

    return comparison


def build_aggregate_comparison(
    comparison_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate per-subject rows into per-mode summary rows."""

    by_mode: dict[str, list[dict[str, Any]]] = {}
    for row in comparison_rows:
        by_mode.setdefault(row["mode"], []).append(row)

    aggregate: list[dict[str, Any]] = []
    for mode in ("CSC-only", "CSC+Boundary"):
        group = by_mode.get(mode, [])
        if not group:
            continue
        agg: dict[str, Any] = {"mode": mode, "subject_count": len(group)}
        numeric_keys = [
            "tests", "total_nodes", "internal_nodes", "leaf_nodes",
            "covered_leaves", "infeasible_leaves", "out_of_range_leaves",
            "empty_leaves", "expanded_leaves", "max_depth", "wall_time_s",
        ]
        for key in numeric_keys:
            values = [row[key] for row in group if row.get(key) is not None]
            if values:
                agg[f"mean_{key}"] = statistics.mean(values)
                agg[f"median_{key}"] = statistics.median(values)
        aggregate.append(agg)
    return aggregate


# ---------------------------------------------------------------------------
# Summarize
# ---------------------------------------------------------------------------

def summarize_rq1(
    rq1_runs_jsonl: str | Path,
    rq2_runs_jsonl: str | Path,
    *,
    output_dir: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Summarize RQ1 CSC-only runs against RQ2 W=1 CSC+Boundary runs."""

    runs_path_rq1 = Path(rq1_runs_jsonl)
    runs_path_rq2 = Path(rq2_runs_jsonl)
    out_dir = Path(output_dir) if output_dir is not None else runs_path_rq1.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load and enrich both datasets
    rq1_rows = [enrich_rq1_record(record) for record in read_jsonl(runs_path_rq1)]
    rq2_rows = [enrich_rq1_record(record) for record in read_jsonl(runs_path_rq2)]  # same enrichment works

    # Filter to completed runs
    rq1_completed = [row for row in rq1_rows if row.get("completed")]
    rq2_w1 = [row for row in rq2_rows if row.get("completed") and int(row.get("workers", 0)) == 1]

    # Build comparison
    per_subject = build_per_subject_comparison(rq1_rows, rq2_rows)
    aggregate = build_aggregate_comparison(per_subject)

    report = {
        "stage": "rq1_bounded_completion_summary",
        "created_at": _now(),
        "rq1_runs_jsonl": str(runs_path_rq1),
        "rq2_runs_jsonl": str(runs_path_rq2),
        "rq1_run_count": len(rq1_rows),
        "rq1_completed_count": len(rq1_completed),
        "rq2_w1_count": len(rq2_w1),
        "subjects": sorted({row["subject"] for row in per_subject}),
        "per_subject_comparison": per_subject,
        "aggregate_comparison": aggregate,
    }

    write_json(out_dir / COMPARISON_JSON, report)
    write_csv(out_dir / COMPARISON_CSV, per_subject)
    write_text(out_dir / COMPARISON_MD, render_rq1_markdown(report))
    return report


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_rq1_markdown(report: dict[str, Any]) -> str:
    """Render RQ1 comparison tables as Markdown."""

    lines = [
        "# RQ1 Bounded Completion Summary",
        "",
        f"- RQ1 CSC-only runs: {report['rq1_completed_count']} completed",
        f"- RQ2 CSC+Boundary W=1 runs: {report['rq2_w1_count']} completed",
        f"- Subjects: {len(report['subjects'])}",
        "",
        "## Per-Subject Comparison",
        "",
    ]

    # Per-subject table
    per_subject_headers = [
        "Subject", "Mode",
        "Tests", "Total Nodes", "Leaf Nodes",
        "Covered", "Infeasible", "Out-of-Range", "Empty", "Expanded",
        "Max Depth", "Wall Time (s)",
    ]
    per_subject_rows = report.get("per_subject_comparison", [])
    lines.extend(_markdown_table(per_subject_headers, [
        [
            row["subject"],
            row["mode"],
            row.get("tests"),
            row.get("total_nodes"),
            row.get("leaf_nodes"),
            row.get("covered_leaves"),
            row.get("infeasible_leaves"),
            row.get("out_of_range_leaves"),
            row.get("empty_leaves"),
            row.get("expanded_leaves"),
            row.get("max_depth"),
            _fmt(row.get("wall_time_s")),
        ]
        for row in per_subject_rows
    ]))
    lines.append("")

    # Aggregate table
    lines.append("## Aggregate Comparison")
    lines.append("")
    agg_headers = [
        "Mode", "Subjects",
        "Mean Tests", "Mean Total Nodes", "Mean Leaf Nodes",
        "Mean Covered", "Mean Infeasible", "Mean Out-of-Range",
        "Mean Empty", "Mean Expanded",
        "Mean Max Depth", "Mean Wall Time (s)",
    ]
    aggregate = report.get("aggregate_comparison", [])
    lines.extend(_markdown_table(agg_headers, [
        [
            row["mode"],
            row.get("subject_count"),
            _fmt(row.get("mean_tests")),
            _fmt(row.get("mean_total_nodes")),
            _fmt(row.get("mean_leaf_nodes")),
            _fmt(row.get("mean_covered_leaves")),
            _fmt(row.get("mean_infeasible_leaves")),
            _fmt(row.get("mean_out_of_range_leaves")),
            _fmt(row.get("mean_empty_leaves")),
            _fmt(row.get("mean_expanded_leaves")),
            _fmt(row.get("mean_max_depth")),
            _fmt(row.get("mean_wall_time_s")),
        ]
        for row in aggregate
    ]))
    lines.append("")

    # Leaf distribution delta
    if len(aggregate) >= 2:
        csc_only = aggregate[0] if aggregate[0]["mode"] == "CSC-only" else aggregate[1]
        csc_boundary = aggregate[1] if aggregate[1]["mode"] == "CSC+Boundary" else aggregate[0]
        lines.append("## Leaf Distribution Delta (CSC+Boundary - CSC-only)")
        lines.append("")
        delta_headers = ["Metric", "CSC-only", "CSC+Boundary", "Delta"]
        delta_keys = [
            ("Tests", "mean_tests"),
            ("Total Nodes", "mean_total_nodes"),
            ("Leaf Nodes", "mean_leaf_nodes"),
            ("Covered Leaves", "mean_covered_leaves"),
            ("Infeasible Leaves", "mean_infeasible_leaves"),
            ("Out-of-Range Leaves", "mean_out_of_range_leaves"),
            ("Empty Leaves", "mean_empty_leaves"),
            ("Expanded Leaves", "mean_expanded_leaves"),
            ("Wall Time (s)", "mean_wall_time_s"),
        ]
        lines.extend(_markdown_table(delta_headers, [
            [
                label,
                _fmt(csc_only.get(key)),
                _fmt(csc_boundary.get(key)),
                _fmt(_delta(csc_only.get(key), csc_boundary.get(key))),
            ]
            for label, key in delta_keys
        ]))
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    return [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *["| " + " | ".join(str(_cell(v)) for v in row) + " |" for row in rows],
    ]


def _cell(value: Any) -> str:
    if value is None:
        return "-"
    return str(value)


def _delta(before: Any, after: Any) -> str:
    if before is None or after is None:
        return "-"
    try:
        b = float(before)
        a = float(after)
        d = a - b
        if b == 0:
            return f"{d:+.1f}"
        pct = (d / abs(b)) * 100
        return f"{d:+.1f} ({pct:+.1f}%)"
    except (TypeError, ValueError):
        return "-"


def _numeric_delta(before: Any, after: Any) -> Optional[float]:
    if before is None or after is None:
        return None
    try:
        return float(after) - float(before)
    except (TypeError, ValueError):
        return None


def _safe_ratio(numerator: Any, denominator: Any) -> Optional[float]:
    if numerator is None or denominator in (None, 0):
        return None
    try:
        return float(numerator) / float(denominator)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _discover_unique_programs(dataset_roots: Iterable[Path]) -> list[OriginalProgram]:
    programs: dict[str, OriginalProgram] = {}
    for dataset_root in dataset_roots:
        for program in discover_original_programs(dataset_root):
            if program.subject in programs:
                previous = programs[program.subject]
                raise ValueError(
                    f"Duplicate subject {program.subject}: {previous.java_file} and {program.java_file}"
                )
            programs[program.subject] = program
    return [programs[subject] for subject in sorted(programs)]


def _structural_class(java_file: Path) -> str:
    source = java_file.read_text(encoding="utf-8", errors="replace")
    has_loop = re.search(r"\b(?:for|while)\s*\(|\bdo\s*\{", source) is not None
    return "loop-bearing" if has_loop else "loop-free"


def _default_session_prefix() -> str:
    return "rq1_csc_only_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def _resolve_path(path: str | Path, project_root: Path) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    if p.exists():
        return p.resolve()
    repo_root = project_root.parents[1]
    repo_relative = repo_root / p
    if p.parts[:2] == ("project", "CSC_EXPANDED"):
        return repo_relative.resolve()
    return (project_root / p).resolve()
