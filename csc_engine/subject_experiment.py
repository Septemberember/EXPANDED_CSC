"""Subject-level orchestration for CSC, refined TBFV, and localization.

This module is intentionally a thin coordinator. It discovers a subject
directory, builds CLI commands for the existing tools, and records a summary.
It does not change CSC, TBFV, or failure-localization semantics.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from .failure_localization_eval import load_manifest
from .java_exec import parse_class_name
from .refined_tbfv import find_fsf_file


DEFAULT_SESSION_ROOT = Path("csc_tmp")
DEFAULT_SUMMARY_NAME = "subject_experiment_summary.json"


@dataclass(frozen=True)
class SubjectProgram:
    """One Java program selected from a subject directory."""

    role: str
    java_file: Path
    class_name: str
    mutant_id: str | None = None
    manifest_record: dict[str, Any] | None = None


@dataclass(frozen=True)
class ExperimentStep:
    """One CLI invocation in the subject workflow."""

    name: str
    command: tuple[str, ...]
    cwd: Path
    expected_outputs: tuple[Path, ...] = ()


@dataclass
class ExperimentOptions:
    """Options shared by all generated commands."""

    project_dir: Path
    subject_dir: Path
    fsf_path: Path | None = None
    fsf_dir: Path | None = None
    manifest_path: Path | None = None
    original_file: Path | None = None
    mutant_ids: list[str] | None = None
    session_prefix: str | None = None
    summary_root: Path = DEFAULT_SESSION_ROOT
    mode: str = "expanded"
    range_bound: int = 200
    max_iter: int = 30
    strategy: str = "sequential"
    workers: int = 4
    bootstrap: str | None = None
    run_original: bool = True
    run_mutants: bool = True
    run_tbfv: bool = True
    run_localization: bool = True
    run_aggregation: bool = True
    run_evaluation: bool = True
    render_cct: bool = False
    render_localization: bool = False
    stop_on_error: bool = False
    dry_run: bool = False
    python_executable: str = sys.executable


@dataclass
class StepResult:
    """Execution result written to the subject summary."""

    name: str
    command: list[str]
    cwd: str
    status: str
    returncode: int | None = None
    expected_outputs: list[str] = field(default_factory=list)
    stdout_tail: str = ""
    stderr_tail: str = ""


CommandRunner = Callable[[Sequence[str], Path], subprocess.CompletedProcess[str]]


def discover_subject(options: ExperimentOptions) -> tuple[SubjectProgram | None, list[SubjectProgram], Path | None]:
    """Discover original, mutants, and FSF for one subject directory."""

    subject_dir = options.subject_dir.resolve()
    java_files = sorted(path for path in subject_dir.glob("*.java") if path.is_file())
    if not java_files:
        raise FileNotFoundError(f"No Java files found in subject directory: {subject_dir}")

    manifest_records = load_manifest(options.manifest_path) if options.manifest_path else []
    subject_records = _records_for_subject(
        manifest_records,
        subject_dir,
        options.mutant_ids,
    )

    original_file = _resolve_original_file(options.original_file, subject_dir, java_files, subject_records)
    original = _program_from_file("original", original_file) if original_file else None
    mutants = _resolve_mutant_programs(subject_dir, java_files, subject_records, options.mutant_ids)
    fsf_path = resolve_subject_fsf(options, original)
    return original, mutants, fsf_path


def resolve_subject_fsf(options: ExperimentOptions,
                        original: SubjectProgram | None) -> Path | None:
    """Resolve the FSF path using explicit input, FSF dirs, and subject-local hints."""

    if options.fsf_path:
        return options.fsf_path.resolve()

    search_dirs = []
    if options.fsf_dir:
        search_dirs.append(options.fsf_dir.resolve())
    subject_fsf = options.subject_dir / "FSF"
    if subject_fsf.exists():
        search_dirs.append(subject_fsf.resolve())
    shared_fsf = options.subject_dir.parent / "fsf_dir"
    if shared_fsf.exists():
        search_dirs.append(shared_fsf.resolve())

    class_name = original.class_name if original else options.subject_dir.name
    for directory in search_dirs:
        found = find_fsf_file(class_name, directory)
        if found is not None:
            return found.resolve()
        txt_files = sorted(directory.glob("*.txt"))
        if len(txt_files) == 1:
            return txt_files[0].resolve()
        stem_matches = [
            path for path in txt_files
            if path.stem == class_name or path.stem.startswith(f"{class_name}_")
        ]
        if len(stem_matches) == 1:
            return stem_matches[0].resolve()
    return None


def build_subject_steps(options: ExperimentOptions,
                        original: SubjectProgram | None,
                        mutants: list[SubjectProgram],
                        fsf_path: Path | None) -> list[ExperimentStep]:
    """Build the ordered workflow for a subject experiment."""

    steps: list[ExperimentStep] = []
    if options.run_original and original is not None:
        steps.extend(_build_program_steps(options, original, fsf_path))
    if options.run_mutants:
        for mutant in mutants:
            steps.extend(_build_program_steps(options, mutant, fsf_path))
    return steps


def run_subject_experiment(options: ExperimentOptions,
                           runner: CommandRunner | None = None) -> dict[str, Any]:
    """Discover and execute a subject experiment."""

    _normalize_options(options)
    original, mutants, fsf_path = discover_subject(options)
    steps = build_subject_steps(options, original, mutants, fsf_path)
    runner = runner or _subprocess_runner
    results: list[StepResult] = []

    for step in steps:
        if options.dry_run:
            results.append(_planned_result(step))
            continue
        completed = runner(step.command, step.cwd)
        result = _completed_result(step, completed)
        results.append(result)
        if options.stop_on_error and completed.returncode != 0:
            break

    summary = build_summary(options, original, mutants, fsf_path, steps, results)
    summary_path = default_summary_path(options)
    write_subject_summary(summary, summary_path)
    return summary


def build_summary(options: ExperimentOptions,
                  original: SubjectProgram | None,
                  mutants: list[SubjectProgram],
                  fsf_path: Path | None,
                  steps: list[ExperimentStep],
                  results: list[StepResult]) -> dict[str, Any]:
    """Build a JSON-serializable subject experiment summary."""

    failed = [result for result in results if result.status == "failed"]
    return {
        "subject": options.subject_dir.name,
        "subject_dir": str(options.subject_dir),
        "fsf": str(fsf_path) if fsf_path else None,
        "manifest": str(options.manifest_path) if options.manifest_path else None,
        "mode": options.mode,
        "strategy": options.strategy,
        "max_iter": options.max_iter,
        "dry_run": options.dry_run,
        "original": _program_summary(original) if original else None,
        "mutants": [_program_summary(mutant) for mutant in mutants],
        "step_count": len(steps),
        "status": "planned" if options.dry_run else ("failed" if failed else "completed"),
        "steps": [result.__dict__ for result in results],
    }


def write_subject_summary(summary: dict[str, Any], output_path: Path) -> None:
    """Write the subject summary JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def default_summary_path(options: ExperimentOptions) -> Path:
    """Return the default summary path for the subject run."""

    return options.summary_root / _session_prefix(options) / options.subject_dir.name / DEFAULT_SUMMARY_NAME


def _normalize_options(options: ExperimentOptions) -> None:
    """Resolve user-facing paths before building cross-cwd commands."""

    cwd = Path.cwd()
    project_dir = _resolve_user_path(options.project_dir, (cwd,))
    options.project_dir = project_dir
    roots = (
        cwd,
        project_dir,
        project_dir.parent,
        project_dir.parent.parent,
    )
    options.subject_dir = _resolve_user_path(options.subject_dir, roots)
    options.summary_root = _resolve_user_path(options.summary_root, roots)
    if options.fsf_path is not None:
        options.fsf_path = _resolve_user_path(options.fsf_path, roots)
    if options.fsf_dir is not None:
        options.fsf_dir = _resolve_user_path(options.fsf_dir, roots)
    if options.manifest_path is not None:
        options.manifest_path = _resolve_user_path(options.manifest_path, roots)
    if options.original_file is not None:
        options.original_file = _resolve_user_path(options.original_file, roots)


def _resolve_user_path(path: Path, roots: Iterable[Path]) -> Path:
    if path.is_absolute():
        return path.resolve()
    if path.exists():
        return path.resolve()
    for root in roots:
        candidate = root / path
        if candidate.exists():
            return candidate.resolve()
    return path.resolve()


def result_dir_for_program(options: ExperimentOptions, program: SubjectProgram) -> Path:
    """Return the CSC artifact directory expected for one program."""

    return DEFAULT_SESSION_ROOT / _session_id(options, program) / program.class_name


def _build_program_steps(options: ExperimentOptions,
                         program: SubjectProgram,
                         fsf_path: Path | None) -> list[ExperimentStep]:
    steps = [_csc_step(options, program)]
    csc_result_dir = result_dir_for_program(options, program)
    tbfv_report = csc_result_dir / "refined_tbfv_report.json"
    localization_report = csc_result_dir / "cct_failure_localization.json"
    aggregated_report = csc_result_dir / "cct_failure_localization_aggregated.json"
    evaluation_report = csc_result_dir / "fault_localization_eval.json"

    if options.run_tbfv:
        steps.append(_tbfv_step(options, program, csc_result_dir, fsf_path, tbfv_report))
    if program.role == "mutant" and options.run_localization:
        steps.append(_localization_step(options, csc_result_dir, localization_report))
        if options.run_aggregation:
            steps.append(_aggregation_step(options, program, localization_report, aggregated_report))
        if (
            options.run_evaluation
            and options.manifest_path
            and program.mutant_id
            and program.manifest_record is not None
        ):
            steps.append(_evaluation_step(
                options,
                program,
                localization_report,
                aggregated_report,
                evaluation_report,
            ))
    return steps


def _csc_step(options: ExperimentOptions, program: SubjectProgram) -> ExperimentStep:
    command = [
        options.python_executable,
        str(options.project_dir / "csc_tool.py"),
        str(program.java_file),
        "--mode",
        options.mode,
        "--max-iter",
        str(options.max_iter),
        "--strategy",
        options.strategy,
        "--workers",
        str(options.workers),
        "--session",
        _session_id(options, program),
    ]
    if options.mode == "expanded":
        command.extend(["--range-bound", str(options.range_bound)])
    if options.bootstrap:
        command.extend(["--bootstrap", options.bootstrap])
    if options.render_cct:
        command.append("--render-cct")
    return ExperimentStep(
        name=f"{program.role}:{program.class_name}:csc",
        command=tuple(command),
        cwd=options.project_dir,
        expected_outputs=(result_dir_for_program(options, program) / "testcases.json",),
    )


def _tbfv_step(options: ExperimentOptions,
               program: SubjectProgram,
               csc_result_dir: Path,
               fsf_path: Path | None,
               output_path: Path) -> ExperimentStep:
    command = [
        options.python_executable,
        str(options.project_dir / "refined_tbfv_tool.py"),
        "--csc-result-dir",
        str(csc_result_dir),
        "--java-file",
        str(program.java_file),
        "--output",
        str(output_path),
    ]
    if fsf_path:
        command.extend(["--fsf", str(fsf_path)])
    return ExperimentStep(
        name=f"{program.role}:{program.class_name}:refined_tbfv",
        command=tuple(command),
        cwd=options.project_dir,
        expected_outputs=(output_path,),
    )


def _localization_step(options: ExperimentOptions,
                       csc_result_dir: Path,
                       output_path: Path) -> ExperimentStep:
    command = [
        options.python_executable,
        str(options.project_dir / "failure_localization_tool.py"),
        "--csc-result-dir",
        str(csc_result_dir),
        "--output",
        str(output_path),
    ]
    if options.render_localization:
        command.append("--render-cct")
    return ExperimentStep(
        name=f"{csc_result_dir.name}:failure_localization",
        command=tuple(command),
        cwd=options.project_dir,
        expected_outputs=(output_path,),
    )


def _aggregation_step(options: ExperimentOptions,
                      program: SubjectProgram,
                      report_path: Path,
                      output_path: Path) -> ExperimentStep:
    source_file = _source_file_for_report(options, program)
    command = [
        options.python_executable,
        str(options.project_dir / "failure_localization_aggregate_tool.py"),
        "--report",
        str(report_path),
        "--output",
        str(output_path),
        "--source-file",
        source_file,
    ]
    return ExperimentStep(
        name=f"{program.class_name}:failure_localization_aggregate",
        command=tuple(command),
        cwd=options.project_dir,
        expected_outputs=(output_path,),
    )


def _evaluation_step(options: ExperimentOptions,
                     program: SubjectProgram,
                     raw_report: Path,
                     aggregated_report: Path,
                     output_path: Path) -> ExperimentStep:
    command = [
        options.python_executable,
        str(options.project_dir / "evaluate_fault_localization.py"),
        "--manifest",
        str(options.manifest_path),
        "--mutant-id",
        str(program.mutant_id),
        "--report",
        str(raw_report),
        "--aggregated-report",
        str(aggregated_report),
        "--output",
        str(output_path),
    ]
    return ExperimentStep(
        name=f"{program.class_name}:failure_localization_eval",
        command=tuple(command),
        cwd=options.project_dir,
        expected_outputs=(output_path,),
    )


def _resolve_original_file(explicit: Path | None,
                           subject_dir: Path,
                           java_files: list[Path],
                           records: list[dict[str, Any]]) -> Path | None:
    if explicit:
        return _resolve_path(explicit, subject_dir.parent)
    record_originals = [
        _resolve_path(Path(str(record["original_file"])), subject_dir)
        for record in records
        if record.get("original_file")
    ]
    existing_record_originals = sorted({path for path in record_originals if path.exists()})
    if len(existing_record_originals) == 1:
        return existing_record_originals[0]

    non_mutants = [path for path in java_files if not _looks_like_mutant(path)]
    if len(non_mutants) == 1:
        return non_mutants[0]
    subject_named = subject_dir / f"{subject_dir.name}.java"
    if subject_named.exists():
        return subject_named
    if not non_mutants:
        return None
    raise ValueError(
        f"Multiple original candidates in {subject_dir}; pass --original-file explicitly"
    )


def _resolve_mutant_programs(subject_dir: Path,
                             java_files: list[Path],
                             records: list[dict[str, Any]],
                             mutant_ids: list[str] | None) -> list[SubjectProgram]:
    selected: list[SubjectProgram] = []
    seen: set[Path] = set()
    if records:
        for record in records:
            mutant_file = record.get("mutant_file")
            if not mutant_file:
                continue
            path = _resolve_path(Path(str(mutant_file)), subject_dir)
            if not path.exists() or path in seen:
                continue
            seen.add(path)
            selected.append(_program_from_file(
                "mutant",
                path,
                mutant_id=str(record.get("mutant_id") or path.stem),
                manifest_record=record,
            ))
    else:
        id_filter = set(mutant_ids or [])
        for path in java_files:
            if not _looks_like_mutant(path):
                continue
            mutant_id = path.stem
            if id_filter and mutant_id not in id_filter:
                continue
            selected.append(_program_from_file("mutant", path, mutant_id=mutant_id))
    return sorted(selected, key=lambda program: program.mutant_id or program.class_name)


def _records_for_subject(records: list[dict[str, Any]],
                         subject_dir: Path,
                         mutant_ids: list[str] | None) -> list[dict[str, Any]]:
    if not records:
        return []
    wanted_ids = set(mutant_ids or [])
    selected = []
    subject_name = subject_dir.name
    for record in records:
        mutant_id = str(record.get("mutant_id") or "")
        if wanted_ids and mutant_id not in wanted_ids:
            continue
        record_subject = str(record.get("subject") or "")
        mutant_file = str(record.get("mutant_file") or "")
        mutant_parts = Path(mutant_file).parts
        if record_subject == subject_name or subject_name in mutant_parts:
            selected.append(record)
    return selected


def _program_from_file(role: str,
                       java_file: Path,
                       mutant_id: str | None = None,
                       manifest_record: dict[str, Any] | None = None) -> SubjectProgram:
    source = java_file.read_text(encoding="utf-8")
    class_name = parse_class_name(source)
    return SubjectProgram(
        role=role,
        java_file=java_file.resolve(),
        class_name=class_name,
        mutant_id=mutant_id,
        manifest_record=manifest_record,
    )


def _resolve_path(path: Path, subject_dir: Path) -> Path:
    if path.is_absolute():
        return path
    if path.exists():
        return path.resolve()
    roots = [
        subject_dir,
        subject_dir.parent,
        subject_dir.parent.parent,
        subject_dir.parent.parent.parent,
    ]
    for root in roots:
        candidate = root / path
        if candidate.exists():
            return candidate.resolve()
    return (subject_dir.parent / path).resolve()


def _source_file_for_report(options: ExperimentOptions, program: SubjectProgram) -> str:
    if program.manifest_record and program.manifest_record.get("mutant_file"):
        return str(program.manifest_record["mutant_file"])
    try:
        return str(program.java_file.relative_to(options.subject_dir.parent))
    except ValueError:
        return str(program.java_file)


def _looks_like_mutant(path: Path) -> bool:
    return re.search(r"_M\d+(?:_|$)", path.stem) is not None


def _session_prefix(options: ExperimentOptions) -> str:
    raw = options.session_prefix or f"{options.subject_dir.name.lower()}_subject"
    return _safe_id(raw)


def _session_id(options: ExperimentOptions, program: SubjectProgram) -> str:
    label = program.mutant_id if program.role == "mutant" and program.mutant_id else program.class_name
    return _safe_id(f"{_session_prefix(options)}_{label}")


def _safe_id(raw: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw.strip())
    return value.strip("_") or "subject_run"


def _planned_result(step: ExperimentStep) -> StepResult:
    return StepResult(
        name=step.name,
        command=list(step.command),
        cwd=str(step.cwd),
        status="planned",
        expected_outputs=[str(path) for path in step.expected_outputs],
    )


def _completed_result(step: ExperimentStep,
                      completed: subprocess.CompletedProcess[str]) -> StepResult:
    return StepResult(
        name=step.name,
        command=list(step.command),
        cwd=str(step.cwd),
        status="completed" if completed.returncode == 0 else "failed",
        returncode=completed.returncode,
        expected_outputs=[str(path) for path in step.expected_outputs],
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
    )


def _subprocess_runner(command: Sequence[str],
                      cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _tail(text: str | None, limit: int = 4000) -> str:
    if not text:
        return ""
    return text[-limit:]


def _program_summary(program: SubjectProgram | None) -> dict[str, Any] | None:
    if program is None:
        return None
    return {
        "role": program.role,
        "java_file": str(program.java_file),
        "class_name": program.class_name,
        "mutant_id": program.mutant_id,
    }
