#!/usr/bin/env python3
"""Run a dataset-level fault-localization experiment.

This is a portable orchestration layer around the existing CSC, refined TBFV,
failure-localization, aggregation, and evaluation tools. It intentionally keeps
the underlying per-subject workflow and output formats unchanged.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from csc_engine import (
    DEFAULT_FL_SUMMARY_TOP_K,
    ExperimentOptions,
    discover_evaluation_reports,
    load_manifest,
    summarize_fault_localization_results,
    validate_fault_localization_dataset,
    write_csv_rows,
    write_jsonl_rows,
    write_markdown_summary,
    write_validation_json,
    write_validation_markdown,
)
from csc_engine.subject_experiment import _safe_id, run_subject_experiment


DEFAULT_MODE = "expanded"
DEFAULT_RANGE_BOUND = 200
DEFAULT_MAX_ITER = 100
DEFAULT_STRATEGY = "batch"
DEFAULT_WORKERS = 4
DEFAULT_EVAL_GLOB = "**/fault_localization_eval.json"


@dataclass(frozen=True)
class SubjectSelection:
    """One selected subject and the mutants that should be run."""

    subject: str
    subject_dir: Path
    mutant_ids: list[str]


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()

    if args.check_env:
        return check_environment(project_dir)
    if args.build_java_bridge:
        return build_java_bridge(project_dir)

    try:
        return run_dataset_experiment(args, project_dir)
    except Exception as exc:
        print(f"Fault-localization experiment failed: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a portable dataset-level fault-localization experiment."
    )
    parser.add_argument(
        "--project-dir",
        default=Path(__file__).resolve().parent,
        help="CSC_EXPANDED project directory. Defaults to this script's directory.",
    )
    parser.add_argument("--dataset-root", help="Fault-localization dataset root.")
    parser.add_argument(
        "--manifest",
        help="mutants_manifest.jsonl path. Defaults to <dataset-root>/mutants_manifest.jsonl.",
    )
    parser.add_argument(
        "--experiment-root",
        help="Output experiment directory, e.g. experiments/FL-061002.",
    )
    parser.add_argument(
        "--session-prefix",
        help="Prefix for CSC session directories. Defaults to a safe experiment-root name.",
    )
    parser.add_argument("--subjects", help="Comma-separated subject names to run.")
    parser.add_argument("--mutants", help="Comma-separated mutant ids to run.")
    parser.add_argument("--mode", choices=["original", "expanded"], default=DEFAULT_MODE)
    parser.add_argument("--range-bound", type=int, default=DEFAULT_RANGE_BOUND)
    parser.add_argument("--max-iter", type=int, default=DEFAULT_MAX_ITER)
    parser.add_argument("--strategy", choices=["sequential", "batch"], default=DEFAULT_STRATEGY)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--bootstrap", help='Bootstrap inputs, e.g. "x=1,y=2".')
    parser.add_argument("--top-k", default=",".join(str(k) for k in DEFAULT_FL_SUMMARY_TOP_K))
    parser.add_argument("--include-original", action="store_true", help="Also run original programs.")
    parser.add_argument("--skip-validation", action="store_true", help="Skip dataset validation.")
    parser.add_argument("--skip-tbfv", action="store_true", help="Only run CSC generation.")
    parser.add_argument("--skip-localization", action="store_true", help="Do not run localization.")
    parser.add_argument("--skip-aggregation", action="store_true", help="Do not aggregate rankings.")
    parser.add_argument("--skip-evaluation", action="store_true", help="Do not evaluate rankings.")
    parser.add_argument(
        "--run-sfl-baseline",
        action="store_true",
        help="After CCT localization, run the line-level SFL baseline over the same archived CSC/TBFV artifacts.",
    )
    parser.add_argument(
        "--reuse-existing-sfl",
        action="store_true",
        help="Reuse existing per-mutant sfl_localization.json files when running the SFL baseline. "
             "By default SFL rankings are recomputed to avoid stale or top-k-truncated reports.",
    )
    parser.add_argument("--render-cct", action="store_true", help="Render standard CCT views.")
    parser.add_argument("--render-localization", action="store_true", help="Render localization CCT views.")
    parser.add_argument("--resume", action="store_true", help="Skip mutants with existing eval reports.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Remove the experiment directory before running. Does not delete project csc_tmp.",
    )
    parser.add_argument("--stop-on-error", action="store_true", help="Stop after a failed subject.")
    parser.add_argument("--dry-run", action="store_true", help="Plan the workflow without running commands.")
    parser.add_argument(
        "--no-archive-artifacts",
        action="store_true",
        help="Do not copy matching csc_tmp session directories into the experiment directory.",
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check Python, Java, Maven, Z3, and optional Graphviz availability.",
    )
    parser.add_argument(
        "--build-java-bridge",
        action="store_true",
        help="Run Maven package for the Java bridge.",
    )
    return parser


def run_dataset_experiment(args: argparse.Namespace, project_dir: Path) -> int:
    dataset_root = require_path(args.dataset_root, "--dataset-root")
    experiment_root = require_output_path(args.experiment_root, "--experiment-root")
    manifest = Path(args.manifest).resolve() if args.manifest else dataset_root / "mutants_manifest.jsonl"
    session_prefix = _safe_id(args.session_prefix or experiment_root.name.lower())
    top_k = parse_int_list(args.top_k)

    if experiment_root.exists() and args.overwrite:
        shutil.rmtree(experiment_root)
    experiment_root.mkdir(parents=True, exist_ok=True)

    if not args.skip_validation:
        validation = validate_fault_localization_dataset(dataset_root, manifest)
        write_validation_json(validation, experiment_root / "dataset_validation.json")
        write_validation_markdown(validation, experiment_root / "dataset_validation.md")
        if validation["summary"]["error_count"] > 0:
            print_validation_summary(validation)
            return 1

    records = load_manifest(manifest)
    selections = select_subjects(records, dataset_root, args.subjects, args.mutants)
    if not selections:
        raise ValueError("No subjects selected. Check --dataset-root, --manifest, --subjects, and --mutants.")
    config = build_config(args, project_dir, dataset_root, manifest, experiment_root, session_prefix, selections)
    write_json(experiment_root / "experiment_config.json", config)
    copy_dataset_snapshot(dataset_root, manifest, experiment_root)

    subject_logs = experiment_root / "subject_logs"
    subject_logs.mkdir(parents=True, exist_ok=True)
    run_records_path = experiment_root / "subject_run_records.jsonl"
    completed = 0
    failed = 0
    skipped = 0

    for selection in selections:
        mutant_ids = selection.mutant_ids
        if args.resume:
            mutant_ids = [
                mutant_id for mutant_id in mutant_ids
                if not eval_report_exists(project_dir, session_prefix, mutant_id)
            ]
        if not mutant_ids and not args.include_original:
            skipped += 1
            write_run_record(run_records_path, {
                "subject": selection.subject,
                "status": "skipped",
                "reason": "all_selected_mutants_already_have_eval_reports",
                "mutants": selection.mutant_ids,
            })
            continue

        elapsed, summary, stdout_text, stderr_text = run_one_subject(
            args,
            project_dir,
            experiment_root,
            manifest,
            session_prefix,
            selection,
            mutant_ids,
        )
        stdout_path = subject_logs / f"{selection.subject}.stdout.txt"
        stderr_path = subject_logs / f"{selection.subject}.stderr.txt"
        stdout_path.write_text(stdout_text, encoding="utf-8")
        stderr_path.write_text(stderr_text, encoding="utf-8")
        returncode = 0 if summary["status"] in {"completed", "planned"} else 2
        write_run_record(run_records_path, {
            "subject": selection.subject,
            "mutants": mutant_ids,
            "elapsed_s": elapsed,
            "returncode": returncode,
            "status": summary["status"],
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
            "summary": str(default_subject_summary_path(experiment_root, session_prefix, selection.subject)),
        })
        if returncode == 0:
            completed += 1
        else:
            failed += 1
            if args.stop_on_error:
                break
        print(f"{selection.subject}: returncode={returncode}, elapsed_s={elapsed:.2f}")

    summary_report = write_fault_localization_summary(project_dir, experiment_root, manifest, session_prefix, top_k)
    copied = 0
    if not args.no_archive_artifacts:
        copied = archive_csc_tmp(project_dir, experiment_root, session_prefix)
    sfl_summary = None
    if args.run_sfl_baseline:
        sfl_summary = run_sfl_baseline(
            args,
            project_dir=project_dir,
            experiment_root=experiment_root,
            manifest=manifest,
            session_prefix=session_prefix,
            use_archived_artifacts=not args.no_archive_artifacts,
        )

    final_summary = {
        "completed_subjects": completed,
        "failed_subjects": failed,
        "skipped_subjects": skipped,
        "selected_subjects": len(selections),
        "copied_csc_tmp_dirs": copied,
        "fault_localization_summary": summary_report["summary"],
        "sfl_baseline_summary": sfl_summary,
        "finished_at": now_iso(),
    }
    write_json(experiment_root / "experiment_run_summary.json", final_summary)
    print(json.dumps(final_summary, indent=2))
    sfl_failed = bool(sfl_summary and sfl_summary.get("returncode") not in (0, None))
    return 0 if failed == 0 and not sfl_failed else 2


def run_one_subject(args: argparse.Namespace,
                    project_dir: Path,
                    experiment_root: Path,
                    manifest: Path,
                    session_prefix: str,
                    selection: SubjectSelection,
                    mutant_ids: list[str]) -> tuple[float, dict[str, Any], str, str]:
    options = ExperimentOptions(
        project_dir=project_dir,
        subject_dir=selection.subject_dir,
        manifest_path=manifest,
        mutant_ids=mutant_ids,
        session_prefix=session_prefix,
        summary_root=experiment_root / "subject_summaries",
        mode=args.mode,
        range_bound=args.range_bound,
        max_iter=args.max_iter,
        strategy=args.strategy,
        workers=max(1, args.workers),
        bootstrap=args.bootstrap,
        run_original=args.include_original,
        run_mutants=True,
        run_tbfv=not args.skip_tbfv,
        run_localization=not args.skip_localization,
        run_aggregation=not args.skip_aggregation,
        run_evaluation=not args.skip_evaluation,
        render_cct=args.render_cct,
        render_localization=args.render_localization,
        stop_on_error=args.stop_on_error,
        dry_run=args.dry_run,
        python_executable=sys.executable,
    )
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    start = time.monotonic()
    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
        summary = run_subject_experiment(options)
    elapsed = time.monotonic() - start
    stdout_text = stdout_buffer.getvalue()
    if not stdout_text:
        stdout_text = json.dumps({
            "subject": selection.subject,
            "status": summary["status"],
            "step_count": summary["step_count"],
            "mutants": mutant_ids,
        }, indent=2)
    return elapsed, summary, stdout_text, stderr_buffer.getvalue()


def write_fault_localization_summary(project_dir: Path,
                                     experiment_root: Path,
                                     manifest: Path,
                                     session_prefix: str,
                                     top_k: list[int]) -> dict[str, Any]:
    eval_glob = f"{session_prefix}_*/**/fault_localization_eval.json"
    evaluation_paths = discover_evaluation_reports(project_dir / "csc_tmp", eval_glob)
    manifest_records = load_manifest(manifest)
    report = summarize_fault_localization_results(manifest_records, evaluation_paths, top_k=top_k)
    write_jsonl_rows(report["rows"], experiment_root / "fault_localization_rows.jsonl")
    write_csv_rows(report["rows"], experiment_root / "fault_localization_rows.csv")
    write_markdown_summary(report, experiment_root / "fault_localization_summary.md")
    return report


def run_sfl_baseline(args: argparse.Namespace,
                     project_dir: Path,
                     experiment_root: Path,
                     manifest: Path,
                     session_prefix: str,
                     use_archived_artifacts: bool) -> dict[str, Any]:
    """Run the optional line-level SFL baseline on this experiment's artifacts."""

    if args.dry_run:
        return {
            "status": "skipped",
            "reason": "dry_run",
        }
    if args.skip_tbfv:
        return {
            "status": "skipped",
            "reason": "SFL baseline requires refined TBFV pass/fail reports",
        }
    csc_tmp_root = (
        experiment_root / "artifacts" / "csc_tmp"
        if use_archived_artifacts
        else project_dir / "csc_tmp"
    )
    baseline_runner = find_sfl_baseline_runner(project_dir)
    output_dir = experiment_root / "baseline-SFL"
    stdout_path = output_dir / "sfl_baseline.stdout.txt"
    stderr_path = output_dir / "sfl_baseline.stderr.txt"
    output_dir.mkdir(parents=True, exist_ok=True)

    if baseline_runner is None:
        searched = [
            project_dir / "baseline" / "run_sfl_baseline_experiment.py",
            project_dir.parents[1] / "baseline" / "run_sfl_baseline_experiment.py",
        ]
        message = "SFL baseline runner not found. Searched: " + ", ".join(str(p) for p in searched)
        stderr_path.write_text(message + "\n", encoding="utf-8")
        return {
            "status": "failed",
            "returncode": 2,
            "reason": message,
            "output_dir": str(output_dir),
        }

    command = [
        sys.executable,
        str(baseline_runner),
        "--manifest",
        str(manifest),
        "--csc-tmp-root",
        str(csc_tmp_root),
        "--session-prefix",
        session_prefix,
        "--output-dir",
        str(output_dir),
        "--top-k",
        args.top_k,
    ]
    if args.reuse_existing_sfl:
        command.append("--reuse-existing-sfl")

    start = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=str(baseline_runner.parents[1]),
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - start
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    return {
        "status": "completed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "elapsed_s": elapsed,
        "output_dir": str(output_dir),
        "rows_jsonl": str(output_dir / "sfl_fault_localization_rows.jsonl"),
        "rows_csv": str(output_dir / "sfl_fault_localization_rows.csv"),
        "summary_md": str(output_dir / "sfl_fault_localization_summary.md"),
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
    }


def find_sfl_baseline_runner(project_dir: Path) -> Path | None:
    """Locate the SFL baseline runner in portable-kit or source-checkout layouts."""

    candidates = [
        project_dir / "baseline" / "run_sfl_baseline_experiment.py",
        project_dir.parents[1] / "baseline" / "run_sfl_baseline_experiment.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def select_subjects(records: list[dict[str, Any]],
                    dataset_root: Path,
                    subjects_raw: str | None,
                    mutants_raw: str | None) -> list[SubjectSelection]:
    wanted_subjects = set(parse_csv(subjects_raw))
    wanted_mutants = set(parse_csv(mutants_raw))
    by_subject: dict[str, list[str]] = {}
    for record in records:
        subject = str(record.get("subject") or "")
        mutant_id = str(record.get("mutant_id") or "")
        if not subject or not mutant_id:
            continue
        if wanted_subjects and subject not in wanted_subjects:
            continue
        if wanted_mutants and mutant_id not in wanted_mutants:
            continue
        by_subject.setdefault(subject, []).append(mutant_id)
    selections = []
    for subject, mutant_ids in by_subject.items():
        subject_dir = dataset_root / subject
        if subject_dir.exists():
            selections.append(SubjectSelection(subject, subject_dir.resolve(), mutant_ids))
    return selections


def archive_csc_tmp(project_dir: Path, experiment_root: Path, session_prefix: str) -> int:
    source_root = project_dir / "csc_tmp"
    archive_root = experiment_root / "artifacts" / "csc_tmp"
    archive_root.mkdir(parents=True, exist_ok=True)
    copied = 0
    for source in sorted(source_root.glob(f"{session_prefix}_*")):
        if not source.is_dir():
            continue
        destination = archive_root / source.name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        copied += 1
    return copied


def copy_dataset_snapshot(dataset_root: Path, manifest: Path, experiment_root: Path) -> None:
    snapshot = experiment_root / "dataset_snapshot"
    snapshot.mkdir(parents=True, exist_ok=True)
    if manifest.exists():
        shutil.copy2(manifest, snapshot / manifest.name)
    for name in ("quality_report.md", "README.md", "Readme.md"):
        source = dataset_root / name
        if source.exists():
            shutil.copy2(source, snapshot / source.name)


def eval_report_exists(project_dir: Path, session_prefix: str, mutant_id: str) -> bool:
    session_id = _safe_id(f"{session_prefix}_{mutant_id}")
    return any((project_dir / "csc_tmp" / session_id).glob("*/fault_localization_eval.json"))


def default_subject_summary_path(experiment_root: Path, session_prefix: str, subject: str) -> Path:
    return experiment_root / "subject_summaries" / session_prefix / subject / "subject_experiment_summary.json"


def check_environment(project_dir: Path) -> int:
    checks = []
    checks.append(("python", sys.executable, True))
    for binary in ("java", "javac", "mvn"):
        checks.append((binary, shutil.which(binary) or "", shutil.which(binary) is not None))
    for optional in ("dot",):
        checks.append((optional, shutil.which(optional) or "", shutil.which(optional) is not None))
    try:
        import z3  # type: ignore  # noqa: F401
        z3_ok = True
        z3_value = "import ok"
    except Exception as exc:  # pragma: no cover - environment-specific
        z3_ok = False
        z3_value = str(exc)
    checks.append(("z3-solver", z3_value, z3_ok))
    jar = project_dir / "java_bridge" / "target" / "csc-bridge-0.1.0-jar-with-dependencies.jar"
    checks.append(("java_bridge_jar", str(jar), jar.exists()))

    failed_required = False
    for name, value, ok in checks:
        status = "OK" if ok else "MISSING"
        print(f"{status:7} {name}: {value}")
        if name not in {"dot"} and not ok:
            failed_required = True
    return 1 if failed_required else 0


def build_java_bridge(project_dir: Path) -> int:
    pom = project_dir / "java_bridge" / "pom.xml"
    if not pom.exists():
        print(f"Java bridge pom.xml not found: {pom}", file=sys.stderr)
        return 2
    completed = subprocess.run(
        ["mvn", "-f", str(pom), "package"],
        cwd=str(project_dir),
        text=True,
        check=False,
    )
    return completed.returncode


def build_config(args: argparse.Namespace,
                 project_dir: Path,
                 dataset_root: Path,
                 manifest: Path,
                 experiment_root: Path,
                 session_prefix: str,
                 selections: list[SubjectSelection]) -> dict[str, Any]:
    return {
        "created_at": now_iso(),
        "project_dir": str(project_dir),
        "dataset_root": str(dataset_root),
        "manifest": str(manifest),
        "experiment_root": str(experiment_root),
        "session_prefix": session_prefix,
        "mode": args.mode,
        "range_bound": args.range_bound,
        "max_iter": args.max_iter,
        "strategy": args.strategy,
        "workers": args.workers,
        "include_original": args.include_original,
        "resume": args.resume,
        "dry_run": args.dry_run,
        "run_sfl_baseline": args.run_sfl_baseline,
        "reuse_existing_sfl": args.reuse_existing_sfl,
        "subjects": [
            {
                "subject": selection.subject,
                "subject_dir": str(selection.subject_dir),
                "mutant_ids": selection.mutant_ids,
            }
            for selection in selections
        ],
    }


def print_validation_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("Dataset validation failed")
    print(f"  Status:   {summary['status']}")
    print(f"  Errors:   {summary['error_count']}")
    print(f"  Warnings: {summary['warning_count']}")


def write_run_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_int_list(raw: str) -> list[int]:
    values = []
    for item in raw.split(","):
        stripped = item.strip()
        if stripped:
            values.append(int(stripped))
    return values or list(DEFAULT_FL_SUMMARY_TOP_K)


def require_path(raw: str | None, flag: str) -> Path:
    if not raw:
        raise ValueError(f"{flag} is required")
    path = Path(raw).resolve()
    if not path.exists():
        raise FileNotFoundError(f"{flag} does not exist: {path}")
    return path


def require_output_path(raw: str | None, flag: str) -> Path:
    if not raw:
        raise ValueError(f"{flag} is required")
    return Path(raw).resolve()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
