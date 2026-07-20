import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from csc_experiments.parallel_generation import (
    build_worker_summary,
    compute_generation_fingerprint,
    discover_original_programs,
    run_parallel_generation_experiment,
    summarize_parallel_generation_experiment,
)
from csc_engine.cct import CCT, Condition, Node
from csc_experiments.rq2_parallel import (
    RQ2ParallelOptions,
    collect_environment,
    load_subject_manifest,
    run_rq2_parallel_experiment,
)


def test_discover_original_programs_skips_mutants(tmp_path):
    dataset = tmp_path / "EX_CSC"
    subject = dataset / "Subject"
    subject.mkdir(parents=True)
    (subject / "Subject.java").write_text("class Subject {}", encoding="utf-8")
    (subject / "Subject_M1.java").write_text("class Subject_M1 {}", encoding="utf-8")
    (subject / "FSF").mkdir()

    programs = discover_original_programs(dataset)

    assert len(programs) == 1
    assert programs[0].subject == "Subject"
    assert programs[0].class_name == "Subject"


def test_experiment_accepts_repo_root_relative_paths(tmp_path):
    repo = tmp_path / "repo"
    project_root = repo / "project" / "CSC_EXPANDED"
    dataset = project_root / "dataset" / "EX_CSC"
    subject = dataset / "Subject"
    subject.mkdir(parents=True)
    (project_root / "csc_tool.py").write_text("# test stub\n", encoding="utf-8")
    (subject / "Subject.java").write_text("class Subject {}", encoding="utf-8")

    result = run_parallel_generation_experiment(
        "project/CSC_EXPANDED/dataset/EX_CSC_dataset",
        "project/CSC_EXPANDED/experiments/RQ2",
        workers=[1],
        project_root=project_root,
        dry_run=True,
    )

    assert Path(result["runs_jsonl"]) == project_root / "experiments" / "RQ2" / "parallel_generation_runs.jsonl"


def test_summarize_parallel_generation_experiment_outputs_metrics(tmp_path):
    runs = tmp_path / "parallel_generation_runs.jsonl"
    for subject, base_time, frontier in [
        ("Alpha", 10.0, [2, 4]),
        ("Beta", 20.0, [6, 8]),
    ]:
        for workers, factor in [(1, 1.0), (2, 0.6), (4, 0.4), (8, 0.3)]:
            session = f"{subject}_w{workers}"
            archive = tmp_path / "artifacts" / session / subject
            archive.mkdir(parents=True)
            write_json(archive / "cct_stats.json", {
                "cct": {
                    "total_nodes": 100,
                    "internal_nodes": 49,
                    "leaf_nodes": 51,
                    "valid_testcases": 20,
                    "expanded_leaves": 10,
                    "infeasible_leaves": 1,
                    "out_of_range_leaves": 0,
                    "max_depth": 7,
                },
                "testcases": {
                    "generated_records": 20,
                    "executable_records": 20,
                    "trace_backed_records": 20,
                },
            })
            write_jsonl(archive / "run_log.jsonl", [
                {"event": "run_start"},
                *[
                    {"event": "batch_discover_complete", "branch_count": value}
                    for value in frontier
                ],
                {"event": "cct_full"},
                {"event": "run_summary", "generated_count": 20},
            ])
            append_jsonl(runs, {
                "subject": subject,
                "class_name": subject,
                "java_file": f"{subject}.java",
                "workers": workers,
                "session": session,
                "wall_time_s": base_time * factor,
                "returncode": 0,
                "archive_dir": str(archive),
            })

    report = summarize_parallel_generation_experiment(runs)

    summary_by_worker = {
        row["workers"]: row
        for row in report["overall_summary"]
    }
    assert summary_by_worker[1]["mean_speedup"] == 1.0
    assert round(summary_by_worker[2]["mean_speedup"], 3) == 1.667
    assert summary_by_worker[4]["mean_testcases"] == 20
    assert summary_by_worker[8]["mean_frontier_width"] == 5.0
    assert (tmp_path / "parallel_generation_summary.md").exists()
    assert report["speedup_quantile_cases"]
    assert report["frontier_width_quantile_cases"]


def test_summary_uses_valid_testcases_when_export_records_are_empty(tmp_path):
    runs = tmp_path / "parallel_generation_runs.jsonl"
    for workers, wall_time in [(1, 4.0), (2, 2.0)]:
        session = f"Subject_w{workers}"
        archive = tmp_path / "artifacts" / session / "Subject"
        archive.mkdir(parents=True)
        write_json(archive / "cct_stats.json", {
            "cct": {
                "total_nodes": 9,
                "valid_testcases": 5,
            },
            "testcases": {
                "generated_records": 0,
                "executable_records": 0,
                "trace_backed_records": 0,
            },
        })
        write_jsonl(archive / "run_log.jsonl", [
            {"event": "run_start"},
            {"event": "batch_discover_complete", "branch_count": 3},
            {"event": "cct_full"},
            {"event": "run_summary", "generated_count": 5},
        ])
        append_jsonl(runs, {
            "subject": "Subject",
            "class_name": "Subject",
            "java_file": "Subject.java",
            "workers": workers,
            "session": session,
            "wall_time_s": wall_time,
            "returncode": 0,
            "archive_dir": str(archive),
        })

    report = summarize_parallel_generation_experiment(runs)
    by_worker = {row["workers"]: row for row in report["overall_summary"]}

    assert by_worker[1]["mean_testcases"] == 5
    assert by_worker[2]["mean_testcases"] == 5


def test_worker_summary_gives_subjects_equal_weight_with_unequal_repetitions():
    rows = []
    for subject, repetitions, t1, t2 in [
        ("Repeated", 3, 10.0, 5.0),
        ("Single", 1, 100.0, 100.0),
    ]:
        for _ in range(repetitions):
            for workers, wall_time in [(1, t1), (2, t2)]:
                rows.append({
                    "subject": subject,
                    "workers": workers,
                    "wall_time_s": wall_time,
                    "completed": True,
                    "normal_completion": True,
                    "fresh_generation": True,
                    "testcase_count": 10,
                    "new_testcases_in_run": 10,
                    "total_nodes": 20,
                })

    by_worker = {row["workers"]: row for row in build_worker_summary(rows)}

    assert by_worker[1]["mean_time_s"] == 55.0
    assert by_worker[2]["mean_time_s"] == 52.5
    assert by_worker[2]["mean_speedup"] == 1.5


def test_experiment_rejects_existing_sessions_by_default(tmp_path):
    project_root = tmp_path / "project"
    dataset = project_root / "dataset" / "EX_CSC"
    subject = dataset / "Subject"
    subject.mkdir(parents=True)
    (project_root / "csc_tool.py").write_text("# test stub\n", encoding="utf-8")
    (subject / "Subject.java").write_text("class Subject {}", encoding="utf-8")
    existing = project_root / "csc_tmp" / "fixed_subject_subject_w1" / "Subject"
    existing.mkdir(parents=True)

    try:
        run_parallel_generation_experiment(
            dataset,
            project_root / "experiments" / "RQ2",
            workers=[1],
            session_prefix="fixed",
            project_root=project_root,
            dry_run=True,
        )
    except FileExistsError as exc:
        assert "Session result already exists" in str(exc)
    else:
        raise AssertionError("Expected existing session to be rejected")


def test_subject_manifest_loads_originals(tmp_path):
    dataset = tmp_path / "EX_CSC"
    subject = dataset / "Subject"
    subject.mkdir(parents=True)
    java_file = subject / "Subject.java"
    java_file.write_text("class Subject {}", encoding="utf-8")
    manifest = dataset / "subjects.jsonl"
    append_jsonl(manifest, {
        "subject": "Subject",
        "class_name": "Subject",
        "java_file": "Subject/Subject.java",
    })

    programs = load_subject_manifest(manifest, dataset)

    assert len(programs) == 1
    assert programs[0].subject == "Subject"
    assert programs[0].java_file == java_file.resolve()


def test_rq2_runner_writes_portable_metadata(tmp_path):
    project_root = tmp_path / "project"
    dataset = project_root / "dataset" / "EX_CSC"
    subject = dataset / "Subject"
    subject.mkdir(parents=True)
    (project_root / "csc_tool.py").write_text("# test stub\n", encoding="utf-8")
    (subject / "Subject.java").write_text("class Subject {}", encoding="utf-8")
    experiment_dir = project_root / "experiments" / "RQ2"

    result = run_rq2_parallel_experiment(RQ2ParallelOptions(
        dataset_root=str(dataset),
        experiment_dir=str(experiment_dir),
        workers=(1,),
        repeats=2,
        project_root=str(project_root),
        dry_run=True,
        summarize=False,
    ))

    assert len(result["runs"]) == 2
    assert (experiment_dir / "experiment_config.json").exists()
    assert (experiment_dir / "environment.json").exists()
    assert (experiment_dir / "subjects.jsonl").exists()
    assert (experiment_dir / "parallel_generation_runs.jsonl").exists()


def test_collect_environment_has_cross_platform_fields(tmp_path):
    env = collect_environment(tmp_path)

    assert env["platform"]["system"]
    assert "python" in env["executables"]
    assert "java" in env["versions"]


def test_generation_fingerprint_ignores_ids_but_detects_input_changes(tmp_path):
    first = write_cct(tmp_path / "first", "tc_1", {"x": 1})
    renamed = write_cct(tmp_path / "renamed", "arbitrary_id", {"x": 1})
    changed = write_cct(tmp_path / "changed", "tc_1", {"x": 2})

    first_hashes = compute_generation_fingerprint(first)
    renamed_hashes = compute_generation_fingerprint(renamed)
    changed_hashes = compute_generation_fingerprint(changed)

    assert first_hashes == renamed_hashes
    assert first_hashes["cct_structure_sha256"] == changed_hashes["cct_structure_sha256"]
    assert first_hashes["cct_semantic_sha256"] != changed_hashes["cct_semantic_sha256"]
    assert first_hashes["test_inputs_sha256"] != changed_hashes["test_inputs_sha256"]


def write_json(path: Path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_jsonl(path: Path, records):
    path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )


def append_jsonl(path: Path, record):
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def write_cct(result_dir: Path, test_id: str, inputs: dict) -> Path:
    result_dir.mkdir(parents=True)
    cct = CCT(use_bounded_range=True, range_bound=200)
    cct.root = Node(Condition(7, "x > 0", "x > 0", 1), is_leaf=False)
    cct.root.left = Node("X", is_leaf=True)
    cct.root.right = Node(test_id, is_leaf=True)
    cct.root.right.test_inputs = {test_id: inputs}
    cct.save_to_file(str(result_dir / "Subject_cct.pkl"))
    return result_dir
