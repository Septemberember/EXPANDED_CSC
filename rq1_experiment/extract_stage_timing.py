#!/usr/bin/env python3
"""Extract stage-level Z3 / Java / merge wall-clock times from run_log.jsonl."""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Any


EXPERIMENT_DIR = Path(__file__).resolve().parents[1] / "experiments" / "RQ1-061501"
ARTIFACTS = EXPERIMENT_DIR / "artifacts"
RUNS_JSONL = EXPERIMENT_DIR / "runs.jsonl"


def _classify(java_file: str) -> str:
    if not java_file or not Path(java_file).exists():
        return "unknown"
    src = Path(java_file).read_text(encoding="utf-8")
    return "loop-bearing" if re.search(r'\b(while|for)\s*\(', src) else "loop-free"


def extract_batch_stages(events: list[dict[str, Any]]) -> dict[str, float]:
    z3_ms = 0.0
    java_wall_ms = 0.0  # batch_verify wall-clock, not cumulative
    merge_ms = 0.0
    for e in events:
        t = e.get("timings", {})
        if e.get("event") == "batch_discover_complete":
            z3_ms += float(t.get("solver_time_ms", 0))
        elif e.get("event") == "batch_verify_complete":
            java_wall_ms += float(e.get("batch_wall_time_ms", 0))
        elif e.get("event") == "batch_branch_result":
            merge_ms += float(t.get("cct_merge_time_ms", 0))
    return {"z3_s": z3_ms / 1000.0, "java_s": java_wall_ms / 1000.0, "merge_s": merge_ms / 1000.0}


def extract_sequential_stages(events: list[dict[str, Any]]) -> dict[str, float]:
    z3_ms = 0.0
    java_ms = 0.0
    merge_ms = 0.0
    for e in events:
        t = e.get("timings", {})
        if e.get("event") == "solver_complete":
            z3_ms += float(e.get("solver_time_ms", 0))
        elif e.get("event") in ("testcase_executed", "bootstrap_complete"):
            java_ms += float(t.get("compile_time_ms", 0))
            java_ms += float(t.get("java_exec_time_ms", 0))
            java_ms += float(t.get("path_log_parse_time_ms", 0))
            merge_ms += float(t.get("cct_merge_time_ms", 0))
    return {"z3_s": z3_ms / 1000.0, "java_s": java_ms / 1000.0, "merge_s": merge_ms / 1000.0}


def _agg(group: list[dict[str, Any]]) -> dict[str, float]:
    if not group:
        return {}
    return {
        "n": len(group),
        "wall_time_s": statistics.mean(r["wall_time_s"] for r in group),
        "z3_s": statistics.mean(r["z3_s"] for r in group),
        "java_s": statistics.mean(r["java_s"] for r in group),
        "merge_s": statistics.mean(r["merge_s"] for r in group),
        "other_s": statistics.mean(r["other_s"] for r in group),
    }


def main():
    runs = []
    seen: dict[tuple[str, str], int] = {}
    for i, line in enumerate(Path(RUNS_JSONL).read_text().splitlines()):
        if not line.strip():
            continue
        record = json.loads(line.strip())
        key = (record["subject"], record["config"])
        seen[key] = i  # keep last occurrence
        runs.append(record)
    # Deduplicate: keep only the last occurrence of each subject+config
    keep_idx = set(seen.values())
    runs = [r for i, r in enumerate(runs) if i in keep_idx]

    results: list[dict[str, Any]] = []
    for run in runs:
        archive = Path(run["archive_dir"])
        log_path = archive / "run_log.jsonl"
        if not log_path.is_file():
            continue
        events = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]

        config = run["config"]
        if config == "csc_boundary":
            stages = extract_batch_stages(events)
        elif config == "csc_only":
            stages = extract_sequential_stages(events)
        else:
            continue

        wall_s = float(run["wall_time_s"])
        accounted = stages["z3_s"] + stages["java_s"] + stages["merge_s"]
        prog_class = _classify(run.get("java_file", ""))
        results.append({
            "subject": run["subject"],
            "dataset": run.get("dataset", ""),
            "config": config,
            "program_class": prog_class,
            "wall_time_s": wall_s,
            "z3_s": stages["z3_s"],
            "java_s": stages["java_s"],
            "merge_s": stages["merge_s"],
            "other_s": wall_s - accounted,
            "accounted_pct": (accounted / wall_s * 100) if wall_s > 0 else 0,
        })

    # Print per-class aggregates
    for prog_class in ("loop-free", "loop-bearing"):
        for config in ("csc_only", "csc_boundary"):
            group = [r for r in results if r["program_class"] == prog_class and r["config"] == config]
            if not group:
                continue
            mean = lambda k: statistics.mean(r[k] for r in group)
            wall = mean("wall_time_s")
            print(f"\n=== {prog_class} / {config} (n={len(group)}) ===")
            print(f"  wall:  {wall:.1f}s")
            for stage in ("z3_s", "java_s", "merge_s", "other_s"):
                s = mean(stage)
                print(f"  {stage}: {s:.1f}s  ({s/wall*100:.0f}%)")

    # Stage deltas for loop-bearing
    print("\n=== Stage Deltas (loop-bearing: Bnd minus CSC-only) ===")
    by_subj: dict[str, dict[str, dict[str, float]]] = {}
    for r in results:
        if r["program_class"] != "loop-bearing":
            continue
        by_subj.setdefault(r["subject"], {})[r["config"]] = r

    total_delta = 0.0
    stage_deltas = {"z3_s": 0.0, "java_s": 0.0, "merge_s": 0.0}
    for subj, pair in by_subj.items():
        csc = pair.get("csc_only", {})
        bnd = pair.get("csc_boundary", {})
        if not csc or not bnd:
            continue
        d = bnd.get("wall_time_s", 0) - csc.get("wall_time_s", 0)
        total_delta += d
        for stage in ("z3_s", "java_s", "merge_s"):
            stage_deltas[stage] += bnd.get(stage, 0) - csc.get(stage, 0)

    n = len(by_subj)
    print(f"  n={n}")
    for stage, total in stage_deltas.items():
        mean_d = total / n
        print(f"  {stage}: mean delta = {mean_d:.1f}s  ({mean_d/(total_delta/n)*100:.0f}% of {total_delta/n:.1f}s total delta)")
    print(f"  total delta = {total_delta/n:.1f}s")

    # Write JSON
    output = {
        "per_run": results,
        "aggregate": {
            "loop_free": {
                "csc_only": _agg([r for r in results if r["program_class"] == "loop-free" and r["config"] == "csc_only"]),
                "csc_boundary": _agg([r for r in results if r["program_class"] == "loop-free" and r["config"] == "csc_boundary"]),
            },
            "loop_bearing": {
                "csc_only": _agg([r for r in results if r["program_class"] == "loop-bearing" and r["config"] == "csc_only"]),
                "csc_boundary": _agg([r for r in results if r["program_class"] == "loop-bearing" and r["config"] == "csc_boundary"]),
            },
        },
    }
    out_path = EXPERIMENT_DIR / "rq1_stage_timing.json"
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True))
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
