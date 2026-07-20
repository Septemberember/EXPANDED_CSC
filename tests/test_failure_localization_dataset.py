import json
import os
import subprocess
import sys

from csc_engine import (
    validate_fault_localization_dataset,
    write_validation_json,
    write_validation_markdown,
)


def test_validate_dataset_passes_for_valid_manifest(tmp_path):
    dataset = make_dataset(tmp_path)
    manifest = dataset / "mutants_manifest.jsonl"
    manifest.write_text(json.dumps(valid_record()) + "\n", encoding="utf-8")

    report = validate_fault_localization_dataset(dataset, manifest)

    assert report["summary"]["status"] == "passed"
    assert report["summary"]["error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["mutant_count"] == 1


def test_validate_dataset_reports_missing_manifest(tmp_path):
    dataset = make_dataset(tmp_path)

    report = validate_fault_localization_dataset(dataset)

    assert report["summary"]["status"] == "failed"
    assert issue_codes(report) == {"manifest_missing", "unlisted_mutant_file"}


def test_validate_dataset_reports_invalid_jsonl_and_duplicate_ids(tmp_path):
    dataset = make_dataset(tmp_path)
    manifest = dataset / "mutants_manifest.jsonl"
    manifest.write_text(
        json.dumps(valid_record()) + "\n"
        + "{bad json\n"
        + json.dumps(valid_record()) + "\n",
        encoding="utf-8",
    )

    report = validate_fault_localization_dataset(dataset, manifest)

    assert "manifest_invalid_jsonl" in issue_codes(report)
    assert "duplicate_mutant_id" in issue_codes(report)
    assert report["summary"]["error_count"] >= 2


def test_validate_dataset_reports_missing_files_and_fsf(tmp_path):
    dataset = make_dataset(tmp_path)
    manifest = dataset / "mutants_manifest.jsonl"
    record = valid_record()
    record["original_file"] = "Subject/MissingOriginal.java"
    record["mutant_file"] = "Subject/MissingMutant_M1.java"
    record["bound_fsf"] = "Subject/FSF/Missing_FSF.txt"
    manifest.write_text(json.dumps(record) + "\n", encoding="utf-8")

    report = validate_fault_localization_dataset(dataset, manifest)

    codes = issue_codes(report)
    assert "file_missing" in codes
    assert "bound_fsf_missing" in codes


def test_validate_dataset_checks_ground_truth_consistency(tmp_path):
    dataset = make_dataset(tmp_path)
    manifest = dataset / "mutants_manifest.jsonl"
    record = valid_record()
    record["ground_truth"]["primary_line"] = 10
    record["ground_truth"]["acceptable_lines"] = [3]
    record["ground_truth"]["acceptable_line_window"] = {"start": 1, "end": 5}
    manifest.write_text(json.dumps(record) + "\n", encoding="utf-8")

    report = validate_fault_localization_dataset(dataset, manifest)

    codes = issue_codes(report)
    assert "primary_line_not_in_acceptable_lines" in codes
    assert "primary_line_outside_window" in codes
    assert "primary_line_out_of_range" in codes


def test_validate_dataset_checks_location_code_and_line_warnings(tmp_path):
    dataset = make_dataset(tmp_path)
    manifest = dataset / "mutants_manifest.jsonl"
    record = valid_record()
    record["mutant_location"] = {
        "line": 2,
        "code": "return x + 999;",
    }
    record["original_location"] = {
        "line": 2,
        "code": "return x + 999;",
    }
    manifest.write_text(json.dumps(record) + "\n", encoding="utf-8")

    report = validate_fault_localization_dataset(dataset, manifest)

    codes = issue_codes(report)
    assert "mutant_location_line_mismatch" in codes
    assert "location_code_mismatch" in codes
    assert report["summary"]["warning_count"] >= 2


def test_validate_dataset_reports_unlisted_mutant_file(tmp_path):
    dataset = make_dataset(tmp_path)
    write_java(dataset / "Subject" / "Subject_M2.java", "Subject_M2", "return x + 2;")
    manifest = dataset / "mutants_manifest.jsonl"
    manifest.write_text(json.dumps(valid_record()) + "\n", encoding="utf-8")

    report = validate_fault_localization_dataset(dataset, manifest)

    assert "unlisted_mutant_file" in issue_codes(report)
    assert report["summary"]["unlisted_mutant_file_count"] == 1


def test_validation_writers(tmp_path):
    dataset = make_dataset(tmp_path)
    manifest = dataset / "mutants_manifest.jsonl"
    manifest.write_text(json.dumps(valid_record()) + "\n", encoding="utf-8")
    report = validate_fault_localization_dataset(dataset, manifest)
    output_json = tmp_path / "validation.json"
    output_md = tmp_path / "validation.md"

    write_validation_json(report, output_json)
    write_validation_markdown(report, output_md)

    assert json.loads(output_json.read_text(encoding="utf-8"))["summary"]["status"] == "passed"
    assert "Fault Localization Dataset Validation" in output_md.read_text(encoding="utf-8")


def test_validate_fault_localization_dataset_cli_smoke(tmp_path):
    dataset = make_dataset(tmp_path)
    manifest = dataset / "mutants_manifest.jsonl"
    manifest.write_text(json.dumps(valid_record()) + "\n", encoding="utf-8")
    output_json = tmp_path / "validation.json"
    output_md = tmp_path / "validation.md"
    tool_path = os.path.join(os.path.dirname(__file__), "..", "validate_fault_localization_dataset.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--dataset-root",
            str(dataset),
            "--manifest",
            str(manifest),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--fail-on-error",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Fault localization dataset validation complete" in completed.stdout
    assert output_json.exists()
    assert output_md.exists()


def test_validate_fault_localization_dataset_cli_fail_on_error(tmp_path):
    dataset = make_dataset(tmp_path)
    tool_path = os.path.join(os.path.dirname(__file__), "..", "validate_fault_localization_dataset.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--dataset-root",
            str(dataset),
            "--fail-on-error",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1


def make_dataset(tmp_path):
    dataset = tmp_path / "EX_CSC"
    subject = dataset / "Subject"
    (subject / "FSF").mkdir(parents=True)
    write_java(subject / "Subject.java", "Subject", "return x;")
    write_java(subject / "Subject_M1.java", "Subject_M1", "return x + 1;")
    (subject / "FSF" / "Subject_FSF.txt").write_text("T: true\nD: true\n", encoding="utf-8")
    return dataset


def write_java(path, class_name, return_line):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"public class {class_name} {{\n"
        "  public static int MD(int x) {\n"
        f"    {return_line}\n"
        "  }\n"
        "}\n",
        encoding="utf-8",
    )


def valid_record():
    return {
        "mutant_id": "Subject_M1",
        "subject": "Subject",
        "operator": "AOR",
        "fault_kind": "data-flow",
        "fault_category": "statement",
        "original_file": "Subject/Subject.java",
        "mutant_file": "Subject/Subject_M1.java",
        "original_location": {
            "line": 3,
            "code": "return x;",
        },
        "mutant_location": {
            "line": 3,
            "code": "return x + 1;",
        },
        "ground_truth": {
            "primary_file": "Subject/Subject_M1.java",
            "primary_line": 3,
            "acceptable_files": ["Subject/Subject_M1.java"],
            "acceptable_lines": [3],
            "acceptable_line_window": {
                "start": 3,
                "end": 3,
            },
        },
    }


def issue_codes(report):
    return {issue["code"] for issue in report["issues"]}

