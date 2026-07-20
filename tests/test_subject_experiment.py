import json
import subprocess
import sys
from pathlib import Path

from csc_engine import (
    ExperimentOptions,
    build_subject_steps,
    default_summary_path,
    discover_subject,
    result_dir_for_program,
    run_subject_experiment,
)


def test_discover_subject_with_local_fsf(tmp_path):
    project_dir = tmp_path / "project"
    subject = tmp_path / "CSC_V2_dataset" / "Subject"
    fsf_dir = subject / "FSF"
    fsf_dir.mkdir(parents=True)
    write_java(subject / "Subject.java", "Subject")
    write_java(subject / "Subject_M1.java", "Subject_M1")
    fsf = fsf_dir / "Subject_FSF.txt"
    fsf.write_text("T: true\nD: true\n", encoding="utf-8")

    options = ExperimentOptions(project_dir=project_dir, subject_dir=subject)

    original, mutants, resolved_fsf = discover_subject(options)

    assert original.class_name == "Subject"
    assert [mutant.mutant_id for mutant in mutants] == ["Subject_M1"]
    assert resolved_fsf == fsf.resolve()


def test_discover_subject_uses_manifest_candidate_dataset_paths(tmp_path):
    project_dir = tmp_path / "project"
    dataset = tmp_path / "CSC_V2_dataset"
    subject = dataset / "candidate_dataset" / "ParkingFee"
    subject.mkdir(parents=True)
    write_java(subject / "ParkingFee.java", "ParkingFee")
    write_java(subject / "ParkingFee_M1.java", "ParkingFee_M1")
    manifest = dataset / "mutants_manifest.jsonl"
    manifest.write_text(
        json.dumps({
            "mutant_id": "ParkingFee_M1",
            "subject": "ParkingFee",
            "original_file": "candidate_dataset/ParkingFee/ParkingFee.java",
            "mutant_file": "candidate_dataset/ParkingFee/ParkingFee_M1.java",
            "ground_truth": {
                "primary_file": "candidate_dataset/ParkingFee/ParkingFee_M1.java",
                "primary_line": 6,
            },
        }) + "\n",
        encoding="utf-8",
    )

    options = ExperimentOptions(
        project_dir=project_dir,
        subject_dir=subject,
        manifest_path=manifest,
    )

    original, mutants, _ = discover_subject(options)

    assert original.java_file == (subject / "ParkingFee.java").resolve()
    assert len(mutants) == 1
    assert mutants[0].java_file == (subject / "ParkingFee_M1.java").resolve()
    assert mutants[0].manifest_record["mutant_id"] == "ParkingFee_M1"


def test_build_subject_steps_includes_full_mutant_workflow(tmp_path):
    project_dir = tmp_path / "CSC_EXPANDED"
    subject = tmp_path / "CSC_V2_dataset" / "Subject"
    subject.mkdir(parents=True)
    write_java(subject / "Subject.java", "Subject")
    write_java(subject / "Subject_M1.java", "Subject_M1")
    manifest = tmp_path / "CSC_V2_dataset" / "mutants_manifest.jsonl"
    manifest.write_text(
        json.dumps({
            "mutant_id": "Subject_M1",
            "subject": "Subject",
            "original_file": "Subject/Subject.java",
            "mutant_file": "Subject/Subject_M1.java",
            "ground_truth": {"primary_file": "Subject/Subject_M1.java", "primary_line": 3},
        }) + "\n",
        encoding="utf-8",
    )
    fsf = subject / "FSF" / "Subject_FSF.txt"
    fsf.parent.mkdir()
    fsf.write_text("T: true\nD: true\n", encoding="utf-8")
    options = ExperimentOptions(
        project_dir=project_dir,
        subject_dir=subject,
        manifest_path=manifest,
        session_prefix="demo",
        summary_root=tmp_path / "out",
    )
    original, mutants, resolved_fsf = discover_subject(options)

    steps = build_subject_steps(options, original, mutants, resolved_fsf)
    step_names = [step.name for step in steps]

    assert step_names == [
        "original:Subject:csc",
        "original:Subject:refined_tbfv",
        "mutant:Subject_M1:csc",
        "mutant:Subject_M1:refined_tbfv",
        "Subject_M1:failure_localization",
        "Subject_M1:failure_localization_aggregate",
        "Subject_M1:failure_localization_eval",
    ]
    mutant_result_dir = result_dir_for_program(options, mutants[0])
    assert str(mutant_result_dir / "testcases.json") in [str(path) for path in steps[2].expected_outputs]
    assert "--aggregated-report" in steps[-1].command


def test_run_subject_experiment_dry_run_writes_summary(tmp_path):
    project_dir = tmp_path / "CSC_EXPANDED"
    subject = tmp_path / "CSC_V2_dataset" / "Subject"
    subject.mkdir(parents=True)
    write_java(subject / "Subject.java", "Subject")
    write_java(subject / "Subject_M1.java", "Subject_M1")
    options = ExperimentOptions(
        project_dir=project_dir,
        subject_dir=subject,
        session_prefix="dry",
        summary_root=tmp_path / "out",
        dry_run=True,
    )

    summary = run_subject_experiment(options, runner=failing_runner)

    assert summary["status"] == "planned"
    assert summary["step_count"] == 6
    assert all(step["status"] == "planned" for step in summary["steps"])
    assert default_summary_path(options).exists()


def test_run_subject_experiment_cli_dry_run(tmp_path):
    subject = tmp_path / "CSC_V2_dataset" / "Subject"
    subject.mkdir(parents=True)
    write_java(subject / "Subject.java", "Subject")
    write_java(subject / "Subject_M1.java", "Subject_M1")
    summary_root = tmp_path / "out"
    tool_path = Path(__file__).resolve().parents[1] / "run_subject_experiment.py"

    completed = subprocess.run(
        [
            sys.executable,
            str(tool_path),
            str(subject),
            "--dry-run",
            "--session-prefix",
            "cli",
            "--output-root",
            str(summary_root),
        ],
        cwd=str(tool_path.parent),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Subject experiment complete" in completed.stdout
    summary_path = summary_root / "cli" / "Subject" / "subject_experiment_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["dry_run"]


def write_java(path, class_name):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"public class {class_name} {{\n"
        "  public static int MD(int x) {\n"
        "    return x;\n"
        "  }\n"
        "}\n",
        encoding="utf-8",
    )


def failing_runner(command, cwd):
    raise AssertionError("dry-run must not execute commands")
