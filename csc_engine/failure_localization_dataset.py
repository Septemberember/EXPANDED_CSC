"""Dataset validation for fault-localization experiments.

The validator is read-only. It checks manifest structure, file paths, ground
truth line metadata, FSF bindings, and unlisted mutant files before a dataset is
used for paper-facing fault-localization evaluation.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .java_exec import parse_class_name
from .refined_tbfv import find_fsf_file


MUTANT_FILE_PATTERN = re.compile(r"_M\d+(?:_|$)")


@dataclass(frozen=True)
class ValidationIssue:
    """One dataset validation issue."""

    severity: str
    code: str
    message: str
    mutant_id: Optional[str] = None
    path: Optional[str] = None
    field: Optional[str] = None
    manifest_line: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "mutant_id": self.mutant_id,
            "path": self.path,
            "field": self.field,
            "manifest_line": self.manifest_line,
        }


def validate_fault_localization_dataset(dataset_root: str | Path,
                                        manifest_path: str | Path | None = None) -> dict[str, Any]:
    """Validate a fault-localization dataset and manifest."""

    root = Path(dataset_root)
    manifest = Path(manifest_path) if manifest_path is not None else root / "mutants_manifest.jsonl"
    issues: list[ValidationIssue] = []

    if not root.exists():
        issues.append(_issue(
            "error",
            "dataset_root_missing",
            f"Dataset root does not exist: {root}",
            path=str(root),
        ))
        return _build_report(root, manifest, [], issues, [])

    records = _load_manifest_records(manifest, issues)
    _validate_records(root, records, issues)
    unlisted_mutants = _discover_unlisted_mutants(root, records)
    for path in unlisted_mutants:
        issues.append(_issue(
            "warning",
            "unlisted_mutant_file",
            "Mutant-looking Java file is not listed in the manifest",
            path=str(path),
        ))

    return _build_report(root, manifest, records, issues, unlisted_mutants)


def write_validation_json(report: dict[str, Any], output_path: str | Path) -> None:
    """Write validation report JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def write_validation_markdown(report: dict[str, Any], output_path: str | Path) -> None:
    """Write validation report Markdown."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_validation_markdown(report), encoding="utf-8")


def _load_manifest_records(manifest: Path, issues: list[ValidationIssue]) -> list[dict[str, Any]]:
    if not manifest.exists():
        issues.append(_issue(
            "error",
            "manifest_missing",
            f"Manifest file does not exist: {manifest}",
            path=str(manifest),
        ))
        return []

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            issues.append(_issue(
                "error",
                "manifest_invalid_jsonl",
                f"Invalid JSONL record: {exc}",
                path=str(manifest),
                manifest_line=line_number,
            ))
            continue
        if not isinstance(record, dict):
            issues.append(_issue(
                "error",
                "manifest_record_not_object",
                "Manifest line must be a JSON object",
                path=str(manifest),
                manifest_line=line_number,
            ))
            continue
        record["_manifest_line"] = line_number
        records.append(record)
    return records


def _validate_records(root: Path,
                      records: list[dict[str, Any]],
                      issues: list[ValidationIssue]) -> None:
    seen_ids: dict[str, int] = {}
    for record in records:
        mutant_id = _string(record.get("mutant_id"))
        manifest_line = _safe_int(record.get("_manifest_line"))
        if not mutant_id:
            issues.append(_issue(
                "error",
                "missing_mutant_id",
                "Manifest record is missing mutant_id",
                field="mutant_id",
                manifest_line=manifest_line,
            ))
        elif mutant_id in seen_ids:
            issues.append(_issue(
                "error",
                "duplicate_mutant_id",
                f"Duplicate mutant_id also appears at manifest line {seen_ids[mutant_id]}",
                mutant_id=mutant_id,
                field="mutant_id",
                manifest_line=manifest_line,
            ))
        else:
            seen_ids[mutant_id] = manifest_line or 0

        _require_field(record, "subject", issues, mutant_id, manifest_line)
        original_path = _validate_path_field(root, record, "original_file", issues, mutant_id, manifest_line)
        mutant_path = _validate_path_field(root, record, "mutant_file", issues, mutant_id, manifest_line)
        _validate_ground_truth(record, mutant_path, issues, mutant_id, manifest_line)
        _validate_location_text(record, "original_location", original_path, issues, mutant_id, manifest_line)
        _validate_location_text(record, "mutant_location", mutant_path, issues, mutant_id, manifest_line)
        _validate_fsf(root, record, original_path, mutant_path, issues, mutant_id, manifest_line)


def _require_field(record: dict[str, Any],
                   field: str,
                   issues: list[ValidationIssue],
                   mutant_id: Optional[str],
                   manifest_line: Optional[int]) -> None:
    if record.get(field) in (None, ""):
        issues.append(_issue(
            "error",
            "missing_required_field",
            f"Required field is missing: {field}",
            mutant_id=mutant_id,
            field=field,
            manifest_line=manifest_line,
        ))


def _validate_path_field(root: Path,
                         record: dict[str, Any],
                         field: str,
                         issues: list[ValidationIssue],
                         mutant_id: Optional[str],
                         manifest_line: Optional[int]) -> Optional[Path]:
    value = record.get(field)
    if value in (None, ""):
        issues.append(_issue(
            "error",
            "missing_required_field",
            f"Required field is missing: {field}",
            mutant_id=mutant_id,
            field=field,
            manifest_line=manifest_line,
        ))
        return None

    path = resolve_dataset_path(value, root)
    if path is None or not path.exists():
        issues.append(_issue(
            "error",
            "file_missing",
            f"{field} cannot be resolved: {value}",
            mutant_id=mutant_id,
            path=str(value),
            field=field,
            manifest_line=manifest_line,
        ))
        return None
    return path


def _validate_ground_truth(record: dict[str, Any],
                           mutant_path: Optional[Path],
                           issues: list[ValidationIssue],
                           mutant_id: Optional[str],
                           manifest_line: Optional[int]) -> None:
    ground_truth = record.get("ground_truth")
    if not isinstance(ground_truth, dict):
        issues.append(_issue(
            "error",
            "ground_truth_missing",
            "ground_truth must be an object",
            mutant_id=mutant_id,
            field="ground_truth",
            manifest_line=manifest_line,
        ))
        return

    primary_line = _safe_int(ground_truth.get("primary_line"))
    if primary_line is None:
        issues.append(_issue(
            "error",
            "primary_line_missing",
            "ground_truth.primary_line is required",
            mutant_id=mutant_id,
            field="ground_truth.primary_line",
            manifest_line=manifest_line,
        ))
        return

    acceptable_lines = ground_truth.get("acceptable_lines")
    if not isinstance(acceptable_lines, list) or not acceptable_lines:
        issues.append(_issue(
            "warning",
            "acceptable_lines_missing",
            "ground_truth.acceptable_lines is missing or empty; evaluator will fall back to primary_line",
            mutant_id=mutant_id,
            field="ground_truth.acceptable_lines",
            manifest_line=manifest_line,
        ))
    else:
        parsed_lines = {_safe_int(line) for line in acceptable_lines}
        if primary_line not in parsed_lines:
            issues.append(_issue(
                "warning",
                "primary_line_not_in_acceptable_lines",
                "ground_truth.primary_line is not listed in acceptable_lines",
                mutant_id=mutant_id,
                field="ground_truth.acceptable_lines",
                manifest_line=manifest_line,
            ))

    window = ground_truth.get("acceptable_line_window")
    if window is not None:
        parsed = _parse_window(window)
        if parsed is None:
            issues.append(_issue(
                "error",
                "acceptable_window_malformed",
                "ground_truth.acceptable_line_window requires numeric start and end",
                mutant_id=mutant_id,
                field="ground_truth.acceptable_line_window",
                manifest_line=manifest_line,
            ))
        else:
            start, end = parsed
            if not start <= primary_line <= end:
                issues.append(_issue(
                    "error",
                    "primary_line_outside_window",
                    "ground_truth.primary_line is outside acceptable_line_window",
                    mutant_id=mutant_id,
                    field="ground_truth.acceptable_line_window",
                    manifest_line=manifest_line,
                ))

    if mutant_path is not None and mutant_path.exists():
        line_count = _line_count(mutant_path)
        if primary_line < 1 or primary_line > line_count:
            issues.append(_issue(
                "error",
                "primary_line_out_of_range",
                f"ground_truth.primary_line is outside mutant file line range 1..{line_count}",
                mutant_id=mutant_id,
                path=str(mutant_path),
                field="ground_truth.primary_line",
                manifest_line=manifest_line,
            ))


def _validate_location_text(record: dict[str, Any],
                            field: str,
                            file_path: Optional[Path],
                            issues: list[ValidationIssue],
                            mutant_id: Optional[str],
                            manifest_line: Optional[int]) -> None:
    location = record.get(field)
    if location is None:
        return
    if not isinstance(location, dict):
        issues.append(_issue(
            "warning",
            "location_not_object",
            f"{field} should be an object",
            mutant_id=mutant_id,
            field=field,
            manifest_line=manifest_line,
        ))
        return

    line_number = _safe_int(location.get("line"))
    code = location.get("code")
    if field == "mutant_location":
        primary_line = _safe_int((record.get("ground_truth") or {}).get("primary_line"))
        if line_number is not None and primary_line is not None and line_number != primary_line:
            issues.append(_issue(
                "warning",
                "mutant_location_line_mismatch",
                "mutant_location.line differs from ground_truth.primary_line",
                mutant_id=mutant_id,
                field=f"{field}.line",
                manifest_line=manifest_line,
            ))

    if file_path is None or line_number is None or code in (None, ""):
        return

    actual = _read_line(file_path, line_number)
    if actual is None:
        return
    if _normalize_code(str(code)) != _normalize_code(actual):
        issues.append(_issue(
            "warning",
            "location_code_mismatch",
            f"{field}.code does not match the actual source line",
            mutant_id=mutant_id,
            path=str(file_path),
            field=f"{field}.code",
            manifest_line=manifest_line,
        ))


def _validate_fsf(root: Path,
                  record: dict[str, Any],
                  original_path: Optional[Path],
                  mutant_path: Optional[Path],
                  issues: list[ValidationIssue],
                  mutant_id: Optional[str],
                  manifest_line: Optional[int]) -> None:
    bound_fsf = record.get("bound_fsf")
    if bound_fsf:
        path = resolve_dataset_path(bound_fsf, root)
        if path is None or not path.exists():
            issues.append(_issue(
                "error",
                "bound_fsf_missing",
                f"bound_fsf cannot be resolved: {bound_fsf}",
                mutant_id=mutant_id,
                path=str(bound_fsf),
                field="bound_fsf",
                manifest_line=manifest_line,
            ))
        return

    class_name = _class_name_from_file(original_path) or _class_name_from_file(mutant_path)
    subject_dir = _subject_dir(record, original_path, mutant_path, root)
    fsf_path = _find_subject_fsf(class_name, subject_dir)
    if fsf_path is None:
        issues.append(_issue(
            "error",
            "fsf_missing",
            "No bound_fsf provided and no subject/shared FSF could be found",
            mutant_id=mutant_id,
            path=str(subject_dir) if subject_dir else None,
            field="bound_fsf",
            manifest_line=manifest_line,
        ))


def _discover_unlisted_mutants(root: Path, records: list[dict[str, Any]]) -> list[Path]:
    listed = {
        _normalize_path(path)
        for record in records
        for path in [_resolved_manifest_path(record.get("mutant_file"), root)]
        if path is not None
    }
    result = []
    for path in root.rglob("*.java"):
        if not MUTANT_FILE_PATTERN.search(path.stem):
            continue
        if _normalize_path(path.resolve()) not in listed:
            result.append(path)
    return sorted(result)


def resolve_dataset_path(value: Any, root: Path) -> Optional[Path]:
    """Resolve a manifest path against common dataset roots."""

    if value in (None, ""):
        return None
    path = Path(str(value))
    if path.is_absolute():
        return path
    candidates = [
        path,
        root / path,
        root.parent / path,
        root.parent.parent / path,
        Path.cwd() / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return (root / path).resolve()


def _resolved_manifest_path(value: Any, root: Path) -> Optional[Path]:
    path = resolve_dataset_path(value, root)
    return path.resolve() if path is not None and path.exists() else None


def _find_subject_fsf(class_name: Optional[str], subject_dir: Optional[Path]) -> Optional[Path]:
    if subject_dir is None:
        return None
    search_dirs = []
    local = subject_dir / "FSF"
    if local.exists():
        search_dirs.append(local)
    shared = subject_dir.parent / "fsf_dir"
    if shared.exists():
        search_dirs.append(shared)
    for directory in search_dirs:
        if class_name:
            found = find_fsf_file(class_name, directory)
            if found is not None:
                return found
        txt_files = sorted(directory.glob("*.txt"))
        if len(txt_files) == 1:
            return txt_files[0]
    return None


def _subject_dir(record: dict[str, Any],
                 original_path: Optional[Path],
                 mutant_path: Optional[Path],
                 root: Path) -> Optional[Path]:
    if original_path is not None:
        return original_path.parent
    if mutant_path is not None:
        return mutant_path.parent
    subject = record.get("subject")
    if subject:
        candidate = root / str(subject)
        if candidate.exists():
            return candidate
        nested = root / "candidate_dataset" / str(subject)
        if nested.exists():
            return nested
    return None


def _class_name_from_file(path: Optional[Path]) -> Optional[str]:
    if path is None or not path.exists():
        return None
    try:
        return parse_class_name(path.read_text(encoding="utf-8"))
    except Exception:
        return path.stem


def _build_report(root: Path,
                  manifest: Path,
                  records: list[dict[str, Any]],
                  issues: list[ValidationIssue],
                  unlisted_mutants: list[Path]) -> dict[str, Any]:
    issue_dicts = [issue.to_dict() for issue in issues]
    error_count = sum(1 for issue in issues if issue.severity == "error")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")
    summary = {
        "status": "failed" if error_count else ("warning" if warning_count else "passed"),
        "dataset_root": str(root),
        "manifest": str(manifest),
        "subject_count": len({record.get("subject") for record in records if record.get("subject")}),
        "mutant_count": len([record for record in records if record.get("mutant_id")]),
        "operator_distribution": dict(Counter(_string(record.get("operator")) or "<missing>" for record in records)),
        "fault_kind_distribution": dict(Counter(_string(record.get("fault_kind")) or "<missing>" for record in records)),
        "fault_category_distribution": dict(Counter(_fault_category(record) or "<missing>" for record in records)),
        "error_count": error_count,
        "warning_count": warning_count,
        "issue_count": len(issues),
        "unlisted_mutant_file_count": len(unlisted_mutants),
    }
    return {
        "summary": summary,
        "issues": issue_dicts,
    }


def _validation_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Fault Localization Dataset Validation",
        "",
        "## Summary",
        "",
        f"- Status: {summary['status']}",
        f"- Dataset root: {summary['dataset_root']}",
        f"- Manifest: {summary['manifest']}",
        f"- Subjects: {summary['subject_count']}",
        f"- Mutants: {summary['mutant_count']}",
        f"- Errors: {summary['error_count']}",
        f"- Warnings: {summary['warning_count']}",
        f"- Unlisted mutant files: {summary['unlisted_mutant_file_count']}",
        "",
        "## Issues",
        "",
    ]
    if not report["issues"]:
        lines.append("No issues found.")
        lines.append("")
        return "\n".join(lines)

    lines.append("| Severity | Code | Mutant | Field | Path | Message |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for issue in report["issues"]:
        lines.append(
            "| "
            + " | ".join([
                _md(issue.get("severity")),
                _md(issue.get("code")),
                _md(issue.get("mutant_id")),
                _md(issue.get("field")),
                _md(issue.get("path")),
                _md(issue.get("message")),
            ])
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _issue(severity: str,
           code: str,
           message: str,
           mutant_id: Optional[str] = None,
           path: Optional[str] = None,
           field: Optional[str] = None,
           manifest_line: Optional[int] = None) -> ValidationIssue:
    return ValidationIssue(
        severity=severity,
        code=code,
        message=message,
        mutant_id=mutant_id,
        path=path,
        field=field,
        manifest_line=manifest_line,
    )


def _parse_window(value: Any) -> Optional[tuple[int, int]]:
    if not isinstance(value, dict):
        return None
    start = _safe_int(value.get("start"))
    end = _safe_int(value.get("end"))
    if start is None or end is None:
        return None
    return min(start, end), max(start, end)


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def _read_line(path: Path, line_number: int) -> Optional[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if line_number < 1 or line_number > len(lines):
        return None
    return lines[line_number - 1]


def _normalize_code(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _fault_category(record: dict[str, Any]) -> Optional[str]:
    ground_truth = record.get("ground_truth")
    if isinstance(ground_truth, dict):
        return _string(record.get("fault_category") or ground_truth.get("fault_category"))
    return _string(record.get("fault_category"))


def _safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")

