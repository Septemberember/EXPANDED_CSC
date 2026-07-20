#!/usr/bin/env python3
"""Run RQ1 CSC-only + CSC+Boundary W=1 on all 24 EX_CSC original programs.

The dataset is split across three subdirectories under
dataset/EX_CSC_dataset_oringinal_only/ (EX_CSC, EX_CSC_dataset). EX_CSC
uses subject-directory layout; EX_CSC_dataset and EX_CSC_dataset use flat layouts. This
script discovers all original programs, runs both configurations for each, and
archives the generation artifacts.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSC_TOOL = PROJECT_ROOT / "csc_tool.py"
DATASET_ROOT = PROJECT_ROOT / "dataset" / "EX_CSC_dataset_oringinal_only"
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / "RQ1-0613-full24"

MAX_ITER = 2000
RANGE_BOUND = 200

CONFIG_CSC_ONLY = {"mode": "original", "strategy": "sequential", "max_iter": MAX_ITER}
CONFIG_BOUNDARY = {"mode": "expanded", "strategy": "batch", "workers": 1,
                   "range_bound": RANGE_BOUND, "max_iter": MAX_ITER}


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover_all_original_programs() -> list[dict[str, Any]]:
    """Discover all original programs across the three sub-datasets."""
    programs: list[dict[str, Any]] = []
    for ds_name in ("EX_CSC", "EX_CSC_dataset", "EX_CSC_dataset"):
        ds_dir = DATASET_ROOT / ds_name
        if not ds_dir.is_dir():
            continue
        for java_file in sorted(ds_dir.glob("*.java")):
            if _is_mutant(java_file.stem):
                continue
            programs.append({
                "dataset": ds_name,
                "subject": java_file.stem,
                "class_name": java_file.stem,
                "java_file": str(java_file),
            })
    return programs


def _is_mutant(stem: str) -> bool:
    return bool(re.search(r"_M\d+$", stem))


def classify_program(java_file: str) -> str:
    """Classify a program as loop-free or loop-bearing."""
    src = Path(java_file).read_text(encoding="utf-8")
    has_loop = bool(re.search(r'\b(while|for)\s*\(', src))
    return "loop-bearing" if has_loop else "loop-free"


# ---------------------------------------------------------------------------
# Run one configuration
# ---------------------------------------------------------------------------

def run_one_config(
    program: dict[str, Any],
    config: dict[str, Any],
    config_label: str,
    session_id: str,
    experiment_dir: Path,
    timeout_s: Optional[int] = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run csc_tool.py once and archive artifacts."""

    result_dir = PROJECT_ROOT / "csc_tmp" / session_id / program["class_name"]
    if result_dir.exists():
        shutil.rmtree(result_dir)  # fresh run

    command = [
        sys.executable, str(CSC_TOOL), str(program["java_file"]),
        "--mode", config["mode"],
        "--strategy", config["strategy"],
        "--max-iter", str(config["max_iter"]),
        "--session", session_id,
        "--keep-artifacts",
    ]
    if config.get("range_bound"):
        command.extend(["--range-bound", str(config["range_bound"])])
    if "workers" in config:
        command.extend(["--workers", str(config["workers"])])

    started_at = _now()
    started = time.perf_counter()
    if dry_run:
        returncode = 0
        stdout = stderr = ""
        timed_out = False
    else:
        try:
            completed = subprocess.run(
                command, cwd=PROJECT_ROOT, text=True,
                capture_output=True, timeout=timeout_s, check=False,
            )
            returncode = completed.returncode
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            timed_out = True
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""

    wall_time_s = time.perf_counter() - started

    archive_dir = experiment_dir / "artifacts" / config_label / session_id / program["class_name"]
    archive_dir.mkdir(parents=True, exist_ok=True)
    _archive_artifacts(result_dir, archive_dir)
    _write_text(archive_dir / "stdout.txt", stdout)
    _write_text(archive_dir / "stderr.txt", stderr)

    return {
        "subject": program["subject"],
        "class_name": program["class_name"],
        "dataset": program["dataset"],
        "config": config_label,
        "mode": config["mode"],
        "strategy": config["strategy"],
        "max_iter": config["max_iter"],
        "range_bound": config.get("range_bound"),
        "workers": config.get("workers"),
        "session": session_id,
        "java_file": program["java_file"],
        "command": command,
        "started_at": started_at,
        "finished_at": _now(),
        "wall_time_s": wall_time_s,
        "returncode": returncode,
        "timed_out": timed_out,
        "archive_dir": str(archive_dir),
    }


def _archive_artifacts(result_dir: Path, archive_dir: Path):
    for name in ("run_log.jsonl", "cct_stats.json", "testcases.json"):
        src = result_dir / name
        if src.is_file():
            shutil.copy2(src, archive_dir / name)


# ---------------------------------------------------------------------------
# Enrich run record with CCT stats
# ---------------------------------------------------------------------------

def enrich(record: dict[str, Any]) -> dict[str, Any]:
    """Attach CCT leaf-distribution stats to a run record."""
    row = dict(record)
    archive = Path(row["archive_dir"])
    stats = _load_json(archive / "cct_stats.json")
    cct = stats.get("cct", {}) if stats else {}
    tcs = stats.get("testcases", {}) if stats else {}

    row["completed"] = bool(row.get("returncode") == 0 and stats)
    row["testcase_count"] = tcs.get("generated_records") or cct.get("valid_testcases")
    for key in (
        "total_nodes", "internal_nodes", "leaf_nodes",
        "covered_leaves", "infeasible_leaves", "out_of_range_leaves",
        "empty_leaves", "expanded_leaves", "valid_testcases", "max_depth",
    ):
        row[key] = cct.get(key)

    # Classify
    row["program_class"] = classify_program(row["java_file"])
    return row


# ---------------------------------------------------------------------------
# Summarize
# ---------------------------------------------------------------------------

def summarize(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce RQ1 comparison tables from enriched run records."""

    # Group by subject + config
    by_subject: dict[str, dict[str, dict[str, Any]]] = {}
    for row in runs:
        if not row.get("completed"):
            continue
        subj = row["subject"]
        cfg = row["config"]
        by_subject.setdefault(subj, {})[cfg] = row

    # Per-subject deltas
    deltas: list[dict[str, Any]] = []
    for subj, configs in sorted(by_subject.items()):
        csc_only = configs.get("csc_only", {})
        boundary = configs.get("csc_boundary", {})
        if not csc_only or not boundary:
            continue
        prog_class = csc_only.get("program_class", "?")
        d_tests = (boundary.get("valid_testcases") or 0) - (csc_only.get("valid_testcases") or 0)
        d_covered = (boundary.get("covered_leaves") or 0) - (csc_only.get("covered_leaves") or 0)
        d_infeas = (boundary.get("infeasible_leaves") or 0) - (csc_only.get("infeasible_leaves") or 0)
        d_empty = (boundary.get("empty_leaves") or 0) - (csc_only.get("empty_leaves") or 0)
        d_nodes = (boundary.get("total_nodes") or 0) - (csc_only.get("total_nodes") or 0)
        d_time = (boundary.get("wall_time_s") or 0) - (csc_only.get("wall_time_s") or 0)

        deltas.append({
            "subject": subj,
            "dataset": csc_only.get("dataset", ""),
            "program_class": prog_class,
            "csc_only_tests": csc_only.get("valid_testcases"),
            "boundary_tests": boundary.get("valid_testcases"),
            "csc_only_empty": csc_only.get("empty_leaves"),
            "boundary_empty": boundary.get("empty_leaves"),
            "csc_only_infeasible": csc_only.get("infeasible_leaves"),
            "boundary_infeasible": boundary.get("infeasible_leaves"),
            "boundary_range_excluded": boundary.get("out_of_range_leaves"),
            "boundary_expanded": boundary.get("expanded_leaves"),
            "csc_only_nodes": csc_only.get("total_nodes"),
            "boundary_nodes": boundary.get("total_nodes"),
            "csc_only_depth": csc_only.get("max_depth"),
            "boundary_depth": boundary.get("max_depth"),
            "csc_only_time": csc_only.get("wall_time_s"),
            "boundary_time": boundary.get("wall_time_s"),
            "delta_tests": d_tests,
            "delta_covered": d_covered,
            "delta_infeasible": d_infeas,
            "delta_empty": d_empty,
            "delta_nodes": d_nodes,
            "delta_time": d_time,
        })

    # Split by program class
    loop_free = [d for d in deltas if d["program_class"] == "loop-free"]
    loop_bearing = [d for d in deltas if d["program_class"] == "loop-bearing"]

    def agg(rows, label):
        if not rows:
            return {"class": label, "count": 0}
        return {
            "class": label,
            "count": len(rows),
            "mean_csc_tests": _mean(r["csc_only_tests"] for r in rows),
            "mean_bnd_tests": _mean(r["boundary_tests"] for r in rows),
            "mean_csc_empty": _mean(r["csc_only_empty"] for r in rows),
            "mean_bnd_empty": _mean(r["boundary_empty"] for r in rows),
            "mean_csc_infeas": _mean(r["csc_only_infeasible"] for r in rows),
            "mean_bnd_infeas": _mean(r["boundary_infeasible"] for r in rows),
            "mean_bnd_range_excl": _mean(r["boundary_range_excluded"] for r in rows),
            "mean_csc_nodes": _mean(r["csc_only_nodes"] for r in rows),
            "mean_bnd_nodes": _mean(r["boundary_nodes"] for r in rows),
            "mean_csc_time": _mean(r["csc_only_time"] for r in rows),
            "mean_bnd_time": _mean(r["boundary_time"] for r in rows),
            "mean_delta_tests": _mean(r["delta_tests"] for r in rows),
            "mean_delta_covered": _mean(r["delta_covered"] for r in rows),
            "mean_delta_infeasible": _mean(r["delta_infeasible"] for r in rows),
            "mean_delta_empty": _mean(r["delta_empty"] for r in rows),
            "mean_delta_nodes": _mean(r["delta_nodes"] for r in rows),
            "mean_delta_time": _mean(r["delta_time"] for r in rows),
        }

    aggregate = [agg(loop_free, "loop-free"), agg(loop_bearing, "loop-bearing"),
                  agg(deltas, "all")]

    # Leaf-classification breakdown (loop-bearing only)
    leaf_breakdown = {
        "class": "loop-bearing",
        "csc_only_empty_leaves": _mean(r["csc_only_empty"] for r in loop_bearing),
        "resolved_as_concrete": _mean(r["delta_covered"] for r in loop_bearing),
        "resolved_as_infeasible": _mean(r["delta_infeasible"] for r in loop_bearing),
        "resolved_as_range_excluded": _mean(r["boundary_range_excluded"] for r in loop_bearing),
    }

    return {
        "per_subject_deltas": deltas,
        "aggregate": aggregate,
        "leaf_breakdown": leaf_breakdown,
    }


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# RQ1 Bounded Completion — Full 24-Program Results",
        "",
        f"Generated: {_now()}",
        "",
        "## Table 1 — Aggregate, Split by Structural Class",
        "",
    ]

    agg = report["aggregate"]
    headers = [
        "Class", "N",
        "CSC-only Tests", "Bnd Tests", "Δ Tests",
        "CSC-only Empty", "Bnd Empty",
        "CSC-only ⊥", "Bnd ⊥",
        "Bnd ⊥_B",
        "CSC-only Nodes", "Bnd Nodes", "Δ Nodes",
        "CSC-only Time (s)", "Bnd Time (s)", "Δ Time (s)",
    ]
    rows = []
    for a in agg:
        rows.append([
            a["class"], a["count"],
            _f1(a.get("mean_csc_tests")), _f1(a.get("mean_bnd_tests")),
            _delta_s(a.get("mean_delta_tests")),
            _f1(a.get("mean_csc_empty")), _f1(a.get("mean_bnd_empty")),
            _f1(a.get("mean_csc_infeas")), _f1(a.get("mean_bnd_infeas")),
            _f1(a.get("mean_bnd_range_excl")),
            _f1(a.get("mean_csc_nodes")), _f1(a.get("mean_bnd_nodes")),
            _delta_s(a.get("mean_delta_nodes")),
            _f1(a.get("mean_csc_time")), _f1(a.get("mean_bnd_time")),
            _delta_s(a.get("mean_delta_time")),
        ])
    lines.extend(_md_table(headers, rows))
    lines.append("")

    lines.append("## Table 2 — Leaf-Classification Breakdown (Loop-Bearing Only)")
    lines.append("")
    lb = report["leaf_breakdown"]
    lines.extend(_md_table(
        ["Metric", "Mean per Program"],
        [
            ["CSC-only empty leaves (ancestor-stopped)", _f1(lb["csc_only_empty_leaves"])],
            ["→ Resolved as concrete (new tests)", _f1(lb["resolved_as_concrete"])],
            ["→ Resolved as infeasible (⊥)", _f1(lb["resolved_as_infeasible"])],
            ["→ Resolved as range-excluded (⊥_B)", _f1(lb["resolved_as_range_excluded"])],
        ],
    ))
    lines.append("")

    # Table 3 — Representative subjects
    lines.append("## Table 3 — Representative Loop-Bearing Subjects by Completion Delta")
    lines.append("")
    deltas = [d for d in report["per_subject_deltas"] if d["program_class"] == "loop-bearing"]
    deltas.sort(key=lambda d: d.get("delta_covered", 0) or 0)
    reps = []
    if deltas:
        for role, idx in [("min", 0), ("Q1", max(0, len(deltas)//4)),
                           ("median", len(deltas)//2), ("Q3", min(len(deltas)-1, 3*len(deltas)//4)),
                           ("max", len(deltas)-1)]:
            d = deltas[idx]
            reps.append({
                "role": role,
                "subject": d["subject"],
                "dataset": d["dataset"],
                "delta_covered": d["delta_covered"],
                "delta_infeasible": d["delta_infeasible"],
                "delta_empty": d["delta_empty"],
                "delta_nodes": d["delta_nodes"],
                "delta_time": d["delta_time"],
            })

    rep_headers = ["Role", "Subject", "Dataset", "Δ Covered", "Δ Infeasible", "Δ Empty", "Δ Nodes", "Δ Time (s)"]
    rep_rows = [[
        r["role"], r["subject"], r["dataset"],
        _delta_s(r["delta_covered"]), _delta_s(r["delta_infeasible"]),
        _delta_s(r["delta_empty"]), _delta_s(r["delta_nodes"]),
        _delta_s(r["delta_time"]),
    ] for r in reps]
    lines.extend(_md_table(rep_headers, rep_rows))
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout-s", type=int)
    parser.add_argument("--skip-csc-only", action="store_true")
    parser.add_argument("--skip-boundary", action="store_true")
    parser.add_argument("--summarize-only", action="store_true")
    args = parser.parse_args()

    programs = discover_all_original_programs()
    print(f"Discovered {len(programs)} original programs")

    # Classify
    loop_free = sum(1 for p in programs if classify_program(p["java_file"]) == "loop-free")
    loop_bearing = len(programs) - loop_free
    print(f"  Loop-free: {loop_free}")
    print(f"  Loop-bearing: {loop_bearing}")

    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

    if args.summarize_only:
        run_records = []
        for line in (EXPERIMENT_DIR / "runs.jsonl").read_text().splitlines():
            if line.strip():
                run_records.append(json.loads(line.strip()))
        enriched = [enrich(r) for r in run_records]
        report = summarize(enriched)
        _write_json(EXPERIMENT_DIR / "rq1_summary.json", report)
        _write_text(EXPERIMENT_DIR / "rq1_summary.md", render_markdown(report))
        print(f"Summary written to {EXPERIMENT_DIR}/rq1_summary.md")
        return

    prefix = "rq1_0613"
    runs_path = EXPERIMENT_DIR / "runs.jsonl"
    all_records: list[dict[str, Any]] = []

    for i, prog in enumerate(programs):
        subj = prog["subject"]
        print(f"\n[{i+1}/{len(programs)}] {subj} ({prog['dataset']})")

        # CSC-only
        if not args.skip_csc_only:
            sid = _safe_id(f"{prefix}_csconly_{prog['dataset']}_{subj}")
            print(f"  CSC-only ...")
            rec = run_one_config(prog, CONFIG_CSC_ONLY, "csc_only", sid,
                                 EXPERIMENT_DIR, timeout_s=args.timeout_s,
                                 dry_run=args.dry_run)
            if not args.dry_run:
                print(f"    wall={rec['wall_time_s']:.1f}s  rc={rec['returncode']}")
            all_records.append(rec)
            _append_jsonl(runs_path, rec)

        # CSC+Boundary
        if not args.skip_boundary:
            sid = _safe_id(f"{prefix}_bndw1_{prog['dataset']}_{subj}")
            print(f"  CSC+Boundary (W=1) ...")
            rec = run_one_config(prog, CONFIG_BOUNDARY, "csc_boundary", sid,
                                 EXPERIMENT_DIR, timeout_s=args.timeout_s,
                                 dry_run=args.dry_run)
            if not args.dry_run:
                print(f"    wall={rec['wall_time_s']:.1f}s  rc={rec['returncode']}")
            all_records.append(rec)
            _append_jsonl(runs_path, rec)

    # Summarize
    if not args.dry_run:
        enriched = [enrich(r) for r in all_records]
        report = summarize(enriched)
        _write_json(EXPERIMENT_DIR / "rq1_summary.json", report)
        _write_text(EXPERIMENT_DIR / "rq1_summary.md", render_markdown(report))
        print(f"\nSummary written to {EXPERIMENT_DIR}/rq1_summary.md")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict[str, Any]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _write_json(path: Path, payload: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _append_jsonl(path: Path, record: dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def _mean(values) -> Optional[float]:
    vals = [float(v) for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


def _f1(value) -> str:
    if value is None:
        return "-"
    return f"{float(value):.1f}"


def _delta_s(value) -> str:
    if value is None:
        return "-"
    v = float(value)
    return f"{v:+.1f}"


def _safe_id(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", raw).strip("_").lower()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    return [
        "| " + " | ".join(str(h) for h in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *["| " + " | ".join(str(v) for v in row) + " |" for row in rows],
    ]


if __name__ == "__main__":
    main()
