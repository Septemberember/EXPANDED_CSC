import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rq1_experiment.bounded_completion import summarize_paired_rq1


def test_paired_summary_requires_fresh_normal_completion(tmp_path):
    runs = tmp_path / "rq1_paired_runs.jsonl"
    write_run(runs, tmp_path, "Complete", "csc_only", cct_full=True, tests=2)
    write_run(runs, tmp_path, "Complete", "csc_boundary", cct_full=True, tests=4)
    write_run(runs, tmp_path, "Partial", "csc_only", cct_full=True, tests=2)
    write_run(runs, tmp_path, "Partial", "csc_boundary", cct_full=False, tests=3)

    report = summarize_paired_rq1(runs)
    by_subject = {row["subject"]: row for row in report["subjects"]}

    assert report["normal_completion_count"] == 3
    assert report["budget_termination_count"] == 1
    assert report["fully_paired_subject_count"] == 1
    assert by_subject["Complete"]["valid_pairs"] == 1
    assert by_subject["Complete"]["delta_testcase_count"] == 2.0
    assert by_subject["Partial"]["valid_pairs"] == 0
    assert by_subject["Partial"]["csc_boundary_budget_terminations"] == 1


def write_run(
    runs: Path,
    root: Path,
    subject: str,
    configuration: str,
    *,
    cct_full: bool,
    tests: int,
) -> None:
    archive = root / "artifacts" / f"{subject}_{configuration}" / subject
    archive.mkdir(parents=True)
    (archive / "cct_stats.json").write_text(json.dumps({
        "cct": {
            "total_nodes": tests * 2 - 1,
            "internal_nodes": tests - 1,
            "leaf_nodes": tests,
            "covered_leaves": tests,
            "empty_leaves": 0,
            "infeasible_leaves": 0,
            "out_of_range_leaves": 0,
            "expanded_leaves": 0,
            "valid_testcases": tests,
            "max_depth": 2,
        },
        "testcases": {"generated_records": tests},
    }), encoding="utf-8")
    events = [{"event": "run_start"}]
    if cct_full:
        events.append({"event": "cct_full"})
    events.append({"event": "run_summary", "generated_count": tests})
    (archive / "run_log.jsonl").write_text(
        "".join(json.dumps(event) + "\n" for event in events),
        encoding="utf-8",
    )
    with runs.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "subject": subject,
            "configuration": configuration,
            "repeat": 1,
            "structural_class": "loop-bearing",
            "returncode": 0,
            "wall_time_s": 1.0 if configuration == "csc_only" else 2.0,
            "archive_dir": str(archive),
        }) + "\n")
