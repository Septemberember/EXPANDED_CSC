"""RQ2 parallel CSC generation experiment helpers.

The experiment package is intentionally generation-only.  It runs csc_tool.py
with batch frontier execution under different worker counts, then summarizes
the produced run logs and CCT statistics for paper-facing RQ2 tables.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional


DEFAULT_WORKERS = (1, 2, 4, 8)
RUNS_JSONL = "parallel_generation_runs.jsonl"
CONFIG_JSON = "parallel_generation_config.json"


@dataclass(frozen=True)
class OriginalProgram:
    """An original Java program under a subject directory."""

    subject: str
    class_name: str
    java_file: Path


def discover_original_programs(dataset_root: str | Path) -> list[OriginalProgram]:
    """Discover original programs and skip mutant Java files.

    The EX_CSC_dataset layout stores each subject in one directory.  Mutants are named
    with a ``_M<number>`` suffix, while the original program has no such suffix.
    """

    root = Path(dataset_root)
    programs: list[OriginalProgram] = []
    if not root.is_dir():
        raise FileNotFoundError(f"Dataset root not found: {root}")

    for subject_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        for java_file in sorted(subject_dir.glob("*.java")):
            stem = java_file.stem
            if _is_mutant_stem(stem):
                continue
            programs.append(OriginalProgram(
                subject=subject_dir.name,
                class_name=stem,
                java_file=java_file,
            ))
    return programs


def run_parallel_generation_experiment(
    dataset_root: str | Path,
    experiment_dir: str | Path,
    *,
    workers: Iterable[int] = DEFAULT_WORKERS,
    mode: str = "expanded",
    range_bound: int = 200,
    max_iter: int = 100,
    timeout_s: Optional[int] = None,
    session_prefix: Optional[str] = None,
    project_root: Optional[str | Path] = None,
    dry_run: bool = False,
    allow_existing_sessions: bool = False,
    append: bool = False,
) -> dict[str, Any]:
    """Run generation for all original programs under ``dataset_root``."""

    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    dataset = _resolve_path(dataset_root, root)
    out_dir = _resolve_path(experiment_dir, root)
    out_dir.mkdir(parents=True, exist_ok=True)

    worker_values = _normalize_workers(workers)
    programs = discover_original_programs(dataset)
    prefix = session_prefix or _default_session_prefix()
    config = {
        "stage": "parallel_generation_experiment",
        "created_at": _now(),
        "dataset_root": str(dataset),
        "experiment_dir": str(out_dir),
        "project_root": str(root),
        "workers": worker_values,
        "mode": mode,
        "range_bound": range_bound,
        "max_iter": max_iter,
        "timeout_s": timeout_s,
        "session_prefix": prefix,
        "dry_run": dry_run,
        "allow_existing_sessions": allow_existing_sessions,
        "append": append,
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
    if runs_path.exists() and not append:
        raise FileExistsError(
            f"Run record already exists: {runs_path}. "
            "Use a new experiment directory or pass append=True."
        )
    run_records: list[dict[str, Any]] = []
    for program in programs:
        for worker_count in worker_values:
            session_id = _safe_id(f"{prefix}_{program.subject}_{program.class_name}_w{worker_count}")
            record = run_one_generation(
                program,
                worker_count,
                session_id=session_id,
                project_root=root,
                experiment_dir=out_dir,
                mode=mode,
                range_bound=range_bound,
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


def run_one_generation(
    program: OriginalProgram,
    workers: int,
    *,
    session_id: str,
    project_root: Path,
    experiment_dir: Path,
    mode: str,
    range_bound: int,
    max_iter: int,
    timeout_s: Optional[int],
    dry_run: bool = False,
    allow_existing_session: bool = False,
) -> dict[str, Any]:
    """Run csc_tool.py once and archive the compact generation artifacts."""

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
        "--range-bound",
        str(range_bound),
        "--strategy",
        "batch",
        "--workers",
        str(workers),
        "--max-iter",
        str(max_iter),
        "--session",
        session_id,
        "--keep-artifacts",
    ]
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
        "stage": "parallel_generation_run",
        "subject": program.subject,
        "class_name": program.class_name,
        "java_file": str(program.java_file),
        "workers": workers,
        "session": session_id,
        "mode": mode,
        "range_bound": range_bound,
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


def archive_generation_artifacts(result_dir: Path, archive_dir: Path) -> list[str]:
    """Copy compact generation artifacts needed by the summarizer."""

    archive_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for name in ("run_log.jsonl", "cct_stats.json", "testcases.json"):
        source = result_dir / name
        if source.is_file():
            target = archive_dir / name
            shutil.copy2(source, target)
            copied.append(str(target))
    fingerprint = compute_generation_fingerprint(result_dir)
    if fingerprint:
        target = archive_dir / "generation_fingerprint.json"
        write_json(target, fingerprint)
        copied.append(str(target))
    return copied


def compute_generation_fingerprint(result_dir: str | Path) -> dict[str, Any]:
    """Return order-independent hashes for one completed CCT and its test inputs."""

    directory = Path(result_dir)
    pickle_files = sorted(directory.glob("*_cct.pkl"))
    if len(pickle_files) != 1:
        return {}

    # Lazy import keeps dataset discovery and dry-run utilities lightweight.
    from csc_engine.cct import CCT, INFEASIBLE_MARKER, RANGE_EXCLUDED_MARKER

    cct = CCT.load_from_file(str(pickle_files[0]))
    if cct is None or cct.root is None:
        return {}

    all_inputs: list[Any] = []

    def visit(node: Any, include_inputs: bool) -> Any:
        if node is None:
            return {"kind": "empty"}
        if node.is_leaf:
            cases = set(getattr(node, "test_cases", set()) or set())
            if cases == {INFEASIBLE_MARKER}:
                payload: dict[str, Any] = {"kind": "infeasible"}
            elif cases == {RANGE_EXCLUDED_MARKER}:
                payload = {"kind": "range_excluded"}
            else:
                inputs_by_case = getattr(node, "test_inputs", {}) or {}
                inputs = [_canonical_value(value) for value in inputs_by_case.values()]
                all_inputs.extend(inputs)
                payload = {
                    "kind": "concrete" if cases else "unresolved",
                    "case_count": len(cases),
                }
                if include_inputs:
                    payload["inputs"] = _canonical_sort(inputs)
            payload["expanded"] = bool(getattr(node, "is_expanded", False))
            return payload

        condition = node.condition
        return {
            "kind": "condition",
            "condition": {
                "line": int(condition.line_number),
                "text": _normalize_condition_text(condition.condition_string),
                "occurrence": int(condition.loop_count),
            },
            "expanded": bool(getattr(node, "is_expanded", False)),
            "false": visit(node.left, include_inputs),
            "true": visit(node.right, include_inputs),
        }

    topology = visit(cct.root, include_inputs=False)
    all_inputs.clear()
    semantics = visit(cct.root, include_inputs=True)
    canonical_inputs = _canonical_sort(all_inputs)
    return {
        "stage": "generation_fingerprint",
        "schema_version": 1,
        "condition_identity": "line+normalized-text+occurrence",
        "testcase_ids_ignored": True,
        "cct_structure_sha256": _canonical_sha256(topology),
        "cct_semantic_sha256": _canonical_sha256(semantics),
        "test_inputs_sha256": _canonical_sha256(canonical_inputs),
        "concrete_input_count": len(canonical_inputs),
    }


def summarize_parallel_generation_experiment(
    runs_jsonl: str | Path,
    *,
    output_dir: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Summarize run records into RQ2 tables and representative case sets."""

    runs_path = Path(runs_jsonl)
    out_dir = Path(output_dir) if output_dir is not None else runs_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    run_rows = [enrich_run_record(record) for record in read_jsonl(runs_path)]
    baseline_by_subject_repeat = {
        (row["subject"], int(row.get("repeat", 1))): row
        for row in run_rows
        if row.get("workers") == 1 and row.get("normal_completion") and row.get("fresh_generation")
    }
    for row in run_rows:
        baseline = baseline_by_subject_repeat.get(
            (row["subject"], int(row.get("repeat", 1)))
        )
        if baseline and row.get("normal_completion") and row.get("fresh_generation") and row.get("wall_time_s"):
            row["speedup"] = baseline["wall_time_s"] / row["wall_time_s"]
            row["efficiency"] = row["speedup"] / row["workers"]
        else:
            row["speedup"] = None
            row["efficiency"] = None
        row["time_per_testcase_s"] = _safe_div(
            row.get("wall_time_s"),
            row.get("testcase_count"),
        ) if row.get("fresh_generation") else None

    summary_rows = build_worker_summary(run_rows)
    speedup_cases = select_quantile_cases(run_rows, metric="speedup_8")
    frontier_cases = select_quantile_cases(run_rows, metric="mean_frontier_width")
    fingerprint_rows = build_fingerprint_invariance(run_rows)
    report = {
        "stage": "parallel_generation_summary",
        "created_at": _now(),
        "runs_jsonl": str(runs_path),
        "run_count": len(run_rows),
        "subjects": sorted({row["subject"] for row in run_rows}),
        "workers": sorted({row["workers"] for row in run_rows}),
        "overall_summary": summary_rows,
        "speedup_quantile_cases": speedup_cases,
        "frontier_width_quantile_cases": frontier_cases,
        "fingerprint_subjects": fingerprint_rows,
        "fingerprint_complete_subject_count": sum(
            1 for row in fingerprint_rows if row["fingerprints_complete"]
        ),
        "fingerprint_invariant_subject_count": sum(
            1 for row in fingerprint_rows if row["all_fingerprints_invariant"]
        ),
        "runs": run_rows,
    }

    write_json(out_dir / "parallel_generation_summary.json", report)
    write_csv(out_dir / "parallel_generation_runs.csv", run_rows)
    write_csv(out_dir / "parallel_generation_overall_summary.csv", summary_rows)
    write_csv(out_dir / "parallel_generation_speedup_quantile_cases.csv", speedup_cases)
    write_csv(out_dir / "parallel_generation_frontier_width_quantile_cases.csv", frontier_cases)
    write_csv(out_dir / "parallel_generation_fingerprint_invariance.csv", fingerprint_rows)
    write_text(out_dir / "parallel_generation_summary.md", render_parallel_summary_markdown(report))
    return report


def enrich_run_record(record: dict[str, Any]) -> dict[str, Any]:
    """Attach CCT stats and frontier metrics to one raw run record."""

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
    row["batch_rounds"] = sum(1 for event in current_run_log if event.get("event") == "batch_discover_complete")
    branch_counts = [
        int(event.get("branch_count") or 0)
        for event in current_run_log
        if event.get("event") == "batch_discover_complete"
    ]
    row["mean_frontier_width"] = statistics.mean(branch_counts) if branch_counts else None
    row["max_frontier_width"] = max(branch_counts) if branch_counts else None
    row["batch_verify_wall_time_s"] = sum(
        float(event.get("batch_wall_time_ms") or 0)
        for event in current_run_log
        if event.get("event") == "batch_verify_complete"
    ) / 1000.0

    cct = cct_stats.get("cct", {}) if cct_stats else {}
    testcase_stats = cct_stats.get("testcases", {}) if cct_stats else {}
    for key in (
        "total_nodes",
        "internal_nodes",
        "leaf_nodes",
        "valid_testcases",
        "expanded_leaves",
        "infeasible_leaves",
        "out_of_range_leaves",
        "max_depth",
    ):
        row[key] = cct.get(key)
    row["generated_records"] = testcase_stats.get("generated_records")
    row["executable_records"] = testcase_stats.get("executable_records")
    row["trace_backed_records"] = testcase_stats.get("trace_backed_records")
    row["testcase_count"] = row.get("generated_records") or row.get("valid_testcases")
    for key in (
        "cct_structure_sha256",
        "cct_semantic_sha256",
        "test_inputs_sha256",
        "concrete_input_count",
    ):
        row[key] = fingerprint.get(key)
    return row


def build_fingerprint_invariance(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize canonical-output invariance across workers and repetitions."""

    results: list[dict[str, Any]] = []
    for subject in sorted({str(row["subject"]) for row in rows}):
        group = [
            row for row in rows
            if row["subject"] == subject
            and row.get("normal_completion")
            and row.get("fresh_generation")
        ]
        expected = len([row for row in rows if row["subject"] == subject])
        item: dict[str, Any] = {
            "subject": subject,
            "expected_runs": expected,
            "completed_fresh_runs": len(group),
            "worker_counts": sorted({int(row["workers"]) for row in group}),
        }
        complete = len(group) == expected and expected > 0
        for key in (
            "cct_structure_sha256",
            "cct_semantic_sha256",
            "test_inputs_sha256",
        ):
            values = {row.get(key) for row in group if row.get(key)}
            missing = sum(1 for row in group if not row.get(key))
            item[f"{key}_distinct"] = len(values)
            item[f"{key}_missing"] = missing
            item[f"{key}_invariant"] = bool(group and missing == 0 and len(values) == 1)
            complete = complete and missing == 0
        item["fingerprints_complete"] = complete
        item["all_fingerprints_invariant"] = bool(
            complete
            and item["cct_structure_sha256_invariant"]
            and item["cct_semantic_sha256_invariant"]
            and item["test_inputs_sha256_invariant"]
        )
        results.append(item)
    return results


def build_worker_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate completed runs by worker count with equal subject weights."""

    summaries: list[dict[str, Any]] = []
    eligible = [
        row for row in rows
        if row.get("normal_completion") and row.get("fresh_generation")
    ]
    baseline_times = {
        subject: _mean(row.get("wall_time_s") for row in group)
        for subject, group in _group_by_subject(
            row for row in eligible if int(row["workers"]) == 1
        ).items()
    }
    for workers in sorted({int(row["workers"]) for row in rows}):
        group = [row for row in rows if int(row["workers"]) == workers]
        completed = [row for row in group if row.get("completed")]
        normal = [row for row in group if row.get("normal_completion")]
        fresh = [row for row in normal if row.get("fresh_generation")]
        subject_groups = _group_by_subject(fresh)

        def subject_means(metric: str) -> list[Optional[float]]:
            return [
                _mean(row.get(metric) for row in subject_rows)
                for subject_rows in subject_groups.values()
            ]

        subject_times = {
            subject: _mean(row.get("wall_time_s") for row in subject_rows)
            for subject, subject_rows in subject_groups.items()
        }
        subject_speedups = [
            _safe_div(baseline_times.get(subject), time_s)
            for subject, time_s in subject_times.items()
        ]
        summary = {
            "workers": workers,
            "runs": len(group),
            "completed": len(completed),
            "normal_completions": len(normal),
            "budget_terminations": sum(1 for row in group if row.get("budget_terminated")),
            "fresh_generation_runs": len(fresh),
            "subjects": len(subject_groups),
            "failed_or_timeout": len(group) - len(completed),
            "mean_time_s": _mean(subject_times.values()),
            "median_time_s": _median(subject_times.values()),
            "mean_testcases": _mean(subject_means("testcase_count")),
            "mean_new_testcases": _mean(subject_means("new_testcases_in_run")),
            "mean_cct_nodes": _mean(subject_means("total_nodes")),
            "mean_time_per_testcase_s": _mean(subject_means("time_per_testcase_s")),
            "mean_batch_verify_wall_time_s": _mean(subject_means("batch_verify_wall_time_s")),
            "mean_speedup": _mean(subject_speedups),
            "median_speedup": _median(subject_speedups),
            "mean_efficiency": _mean(
                _safe_div(speedup, workers) for speedup in subject_speedups
            ),
            "mean_frontier_width": _mean(subject_means("mean_frontier_width")),
            "mean_max_frontier_width": _mean(subject_means("max_frontier_width")),
            "mean_max_depth": _mean(subject_means("max_depth")),
        }
        summaries.append(summary)
    return summaries


def select_quantile_cases(rows: list[dict[str, Any]], metric: str) -> list[dict[str, Any]]:
    """Select min/Q1/median/Q3/max cases by a subject-level metric."""

    subject_rows = build_subject_wide_rows(rows)
    candidates = [
        row for row in subject_rows
        if row.get(metric) is not None
    ]
    candidates.sort(key=lambda row: (row[metric], row["subject"]))
    if not candidates:
        return []
    positions = {
        "min": 0,
        "q1": round(0.25 * (len(candidates) - 1)),
        "median": round(0.50 * (len(candidates) - 1)),
        "q3": round(0.75 * (len(candidates) - 1)),
        "max": len(candidates) - 1,
    }
    selected = []
    seen: set[tuple[str, str]] = set()
    for role, index in positions.items():
        item = dict(candidates[index])
        item["role"] = role
        key = (role, item["subject"])
        if key not in seen:
            selected.append(item)
            seen.add(key)
    return selected


def build_subject_wide_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pivot completed runs into one arithmetic-mean row per subject."""

    by_subject: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("normal_completion") and row.get("fresh_generation"):
            by_subject.setdefault(row["subject"], []).append(row)

    wide_rows: list[dict[str, Any]] = []
    for subject, subject_rows in sorted(by_subject.items()):
        by_worker: dict[int, list[dict[str, Any]]] = {}
        for row in subject_rows:
            by_worker.setdefault(int(row["workers"]), []).append(row)
        baseline_runs = by_worker.get(1)
        if not baseline_runs:
            continue
        baseline = baseline_runs[0]
        wide: dict[str, Any] = {
            "subject": subject,
            "class_name": baseline.get("class_name"),
            "testcases": _mean(row.get("testcase_count") for row in baseline_runs),
            "cct_nodes": _mean(row.get("total_nodes") for row in baseline_runs),
            "max_depth": _mean(row.get("max_depth") for row in baseline_runs),
            "mean_frontier_width": _mean(
                row.get("mean_frontier_width") for row in baseline_runs
            ),
            "max_frontier_width": _mean(
                row.get("max_frontier_width") for row in baseline_runs
            ),
        }
        baseline_time = _mean(row.get("wall_time_s") for row in baseline_runs)
        for worker, worker_rows in sorted(by_worker.items()):
            worker_time = _mean(row.get("wall_time_s") for row in worker_rows)
            speedup = _safe_div(baseline_time, worker_time)
            wide[f"t{worker}"] = worker_time
            wide[f"s{worker}"] = speedup
            wide[f"e{worker}"] = _safe_div(speedup, worker)
        wide["speedup_8"] = wide.get("s8")
        wide["best_speedup"] = max(
            (wide.get(f"s{worker}") for worker in by_worker if wide.get(f"s{worker}") is not None),
            default=None,
        )
        wide_rows.append(wide)
    return wide_rows


def _group_by_subject(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["subject"]), []).append(row)
    return grouped


def render_parallel_summary_markdown(report: dict[str, Any]) -> str:
    """Render a compact Markdown summary."""

    lines = [
        "# RQ2 Parallel Generation Summary",
        "",
        f"- Runs: {report['run_count']}",
        f"- Subjects: {len(report['subjects'])}",
        f"- Workers: {', '.join(str(w) for w in report['workers'])}",
        "",
        "## Overall Parallel Summary",
        "",
    ]
    headers = [
        "Workers", "Normal/Total", "Budget Stop", "Fresh", "Mean Time(s)", "Median Time(s)",
        "Mean Testcases", "Mean New Testcases", "Mean CCT Nodes",
        "Mean Batch Verify(s)", "Mean Time/Testcase(s)",
        "Mean Speedup", "Median Speedup", "Mean Efficiency",
    ]
    lines.extend(_markdown_table(headers, [
        [
            row["workers"],
            f"{row['normal_completions']}/{row['runs']}",
            row["budget_terminations"],
            f"{row['fresh_generation_runs']}/{row['runs']}",
            _fmt(row.get("mean_time_s")),
            _fmt(row.get("median_time_s")),
            _fmt(row.get("mean_testcases")),
            _fmt(row.get("mean_new_testcases")),
            _fmt(row.get("mean_cct_nodes")),
            _fmt(row.get("mean_batch_verify_wall_time_s")),
            _fmt(row.get("mean_time_per_testcase_s")),
            _fmt(row.get("mean_speedup")),
            _fmt(row.get("median_speedup")),
            _fmt(row.get("mean_efficiency")),
        ]
        for row in report["overall_summary"]
    ]))
    lines.append("")
    lines.extend([
        "## Canonical Output Invariance",
        "",
        (
            f"Complete fingerprints: {report['fingerprint_complete_subject_count']}/"
            f"{len(report['subjects'])}; invariant fingerprints: "
            f"{report['fingerprint_invariant_subject_count']}/{len(report['subjects'])}."
        ),
        "",
    ])
    lines.extend(_markdown_table(
        ["Subject", "Fresh/Expected", "Structure", "Leaf Semantics", "Input Set", "All Invariant"],
        [
            [
                row["subject"],
                f"{row['completed_fresh_runs']}/{row['expected_runs']}",
                row["cct_structure_sha256_invariant"],
                row["cct_semantic_sha256_invariant"],
                row["test_inputs_sha256_invariant"],
                row["all_fingerprints_invariant"],
            ]
            for row in report["fingerprint_subjects"]
        ],
    ))
    lines.append("")
    lines.extend(_case_section("Speedup Quantile Cases", report["speedup_quantile_cases"]))
    lines.append("")
    lines.extend(_case_section("Frontier Width Quantile Cases", report["frontier_width_quantile_cases"]))
    lines.append("")
    return "\n".join(lines)


def _case_section(title: str, rows: list[dict[str, Any]]) -> list[str]:
    headers = [
        "Role", "Subject", "T1", "T2", "T4", "T8", "S2", "S4", "S8",
        "Testcases", "CCT Nodes", "Mean Frontier", "Max Frontier", "Max Depth",
    ]
    return [
        f"## {title}",
        "",
        *_markdown_table(headers, [
            [
                row.get("role"),
                row.get("subject"),
                _fmt(row.get("t1")),
                _fmt(row.get("t2")),
                _fmt(row.get("t4")),
                _fmt(row.get("t8")),
                _fmt(row.get("s2")),
                _fmt(row.get("s4")),
                _fmt(row.get("s8")),
                _fmt(row.get("testcases")),
                _fmt(row.get("cct_nodes")),
                _fmt(row.get("mean_frontier_width")),
                _fmt(row.get("max_frontier_width")),
                _fmt(row.get("max_depth")),
            ]
            for row in rows
        ]),
    ]


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    return [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *["| " + " | ".join(str(value) for value in row) + " |" for row in rows],
    ]


def _split_run_log(events: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    runs: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for event in events:
        if event.get("event") == "run_start" and current:
            runs.append(current)
            current = []
        current.append(event)
    if current:
        runs.append(current)
    return runs


def _last_event(events: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for event in reversed(events):
        if event.get("event") == name:
            return event
    return {}


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.is_file():
        return []
    records = []
    for line in p.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            records.append(json.loads(stripped))
    return records


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_text(path: str | Path, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def write_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with p.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field)) for field in fields})


def _load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _csv_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True)
    return value


def _canonical_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _canonical_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, set):
        return _canonical_sort([_canonical_value(item) for item in value])
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _canonical_sort(values: Iterable[Any]) -> list[Any]:
    return sorted(values, key=_canonical_json)


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _normalize_condition_text(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text).strip())


def _normalize_workers(values: Iterable[int]) -> list[int]:
    normalized = sorted({int(value) for value in values if int(value) > 0})
    if not normalized:
        raise ValueError("At least one positive worker count is required")
    return normalized


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


def _is_mutant_stem(stem: str) -> bool:
    return bool(re.search(r"_M\d+$", stem))


def _default_session_prefix() -> str:
    return "rq2_parallel_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def _safe_id(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", raw).strip("_").lower()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if len(text) > limit else text


def _safe_div(numerator: Any, denominator: Any) -> Optional[float]:
    if numerator is None or denominator in (None, 0):
        return None
    return float(numerator) / float(denominator)


def _mean(values: Iterable[Any]) -> Optional[float]:
    numeric = [float(value) for value in values if value is not None]
    return statistics.mean(numeric) if numeric else None


def _median(values: Iterable[Any]) -> Optional[float]:
    numeric = [float(value) for value in values if value is not None]
    return statistics.median(numeric) if numeric else None


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)
