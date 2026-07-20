"""Cross-platform RQ2 parallel generation experiment runner.

This module is the public experiment package for the RQ2 worker-scaling study.
It wraps the lower-level generation helper with config files, optional subject
manifests, repeats, environment capture, and stable output artifacts.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from csc_experiments.parallel_generation import (
    CONFIG_JSON,
    DEFAULT_WORKERS,
    RUNS_JSONL,
    OriginalProgram,
    append_jsonl,
    discover_original_programs,
    read_jsonl,
    run_one_generation,
    summarize_parallel_generation_experiment,
    write_json,
)


DEFAULT_EXPERIMENT_NAME = "RQ2-parallel-generation"


@dataclass(frozen=True)
class RQ2ParallelOptions:
    """Configuration for one RQ2 experiment run."""

    dataset_root: str = "dataset/EX_CSC_dataset"
    subjects_manifest: Optional[str] = None
    output_root: str = "experiments"
    experiment_dir: Optional[str] = None
    experiment_name: str = DEFAULT_EXPERIMENT_NAME
    workers: tuple[int, ...] = DEFAULT_WORKERS
    repeats: int = 1
    mode: str = "expanded"
    range_bound: int = 200
    max_iter: int = 100
    timeout_s: Optional[int] = 600
    session_prefix: Optional[str] = None
    project_root: Optional[str] = None
    dry_run: bool = False
    allow_existing_sessions: bool = False
    append: bool = False
    summarize: bool = True


def run_rq2_parallel_experiment(options: RQ2ParallelOptions) -> dict[str, Any]:
    """Run a full RQ2 experiment using explicit cross-platform artifacts."""

    project_root = _resolve_project_root(options.project_root)
    dataset_root = _resolve_path(options.dataset_root, project_root)
    output_dir = _resolve_experiment_dir(options, project_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    runs_path = output_dir / RUNS_JSONL
    if runs_path.exists() and not options.append:
        raise FileExistsError(
            f"Run record already exists: {runs_path}. "
            "Use a new --experiment-dir or pass --append."
        )

    programs = _load_programs(options, dataset_root, project_root)
    if not programs:
        raise ValueError(f"No original Java programs found under {dataset_root}")

    prefix = options.session_prefix or _default_session_prefix(options.experiment_name)
    config = _experiment_config(options, project_root, dataset_root, output_dir, programs, prefix)
    write_json(output_dir / CONFIG_JSON, config)
    write_json(output_dir / "experiment_config.json", config)
    write_json(output_dir / "environment.json", collect_environment(project_root))
    _write_subjects(output_dir / "subjects.jsonl", programs)

    records: list[dict[str, Any]] = []
    for repeat in range(1, options.repeats + 1):
        for program in programs:
            for worker_count in _normalize_workers(options.workers):
                session_id = _safe_id(
                    f"{prefix}_r{repeat:02d}_{program.subject}_{program.class_name}_w{worker_count}"
                )
                record = run_one_generation(
                    program,
                    worker_count,
                    session_id=session_id,
                    project_root=project_root,
                    experiment_dir=output_dir,
                    mode=options.mode,
                    range_bound=options.range_bound,
                    max_iter=options.max_iter,
                    timeout_s=options.timeout_s,
                    dry_run=options.dry_run,
                    allow_existing_session=options.allow_existing_sessions,
                )
                record["repeat"] = repeat
                records.append(record)
                append_jsonl(runs_path, record)

    report = None
    if options.summarize:
        report = summarize_parallel_generation_experiment(runs_path, output_dir=output_dir)

    return {
        "config": config,
        "runs": records,
        "runs_jsonl": str(runs_path),
        "experiment_dir": str(output_dir),
        "summary": report,
    }


def collect_environment(project_root: Path) -> dict[str, Any]:
    """Collect reproducibility metadata without platform-specific shell use."""

    return {
        "stage": "rq2_parallel_environment",
        "created_at": _now_local(),
        "project_root": str(project_root),
        "cwd": os.getcwd(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },
        "cpu_count": os.cpu_count(),
        "executables": {
            "python": sys.executable,
            "java": shutil.which("java"),
            "javac": shutil.which("javac"),
        },
        "versions": {
            "java": _version_output(["java", "-version"]),
            "javac": _version_output(["javac", "-version"]),
        },
    }


def load_options(config_path: Optional[str | Path], overrides: dict[str, Any]) -> RQ2ParallelOptions:
    """Load config JSON and apply non-null CLI overrides."""

    data: dict[str, Any] = {}
    if config_path:
        data.update(json.loads(Path(config_path).read_text(encoding="utf-8")))
    data.update({key: value for key, value in overrides.items() if value is not None})
    allowed = {field.name for field in fields(RQ2ParallelOptions)}
    data = {key: value for key, value in data.items() if key in allowed}
    if "workers" in data:
        data["workers"] = tuple(_parse_workers(data["workers"]))
    return RQ2ParallelOptions(**data)


def write_sample_config(path: str | Path) -> None:
    """Write a sample JSON config for a portable RQ2 experiment."""

    sample = {
        "dataset_root": "dataset/EX_CSC_dataset",
        "subjects_manifest": None,
        "output_root": "experiments",
        "experiment_name": "RQ2-EX-CSC",
        "workers": [1, 2, 4, 8],
        "repeats": 3,
        "mode": "expanded",
        "range_bound": 200,
        "max_iter": 100,
        "timeout_s": 600,
        "allow_existing_sessions": False,
        "append": False,
        "summarize": True,
    }
    write_json(path, sample)


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            options = load_options(args.config, _run_overrides(args))
            result = run_rq2_parallel_experiment(options)
            print("RQ2 parallel experiment complete")
            print(f"  Experiment: {result['experiment_dir']}")
            print(f"  Runs:       {result['runs_jsonl']}")
            print(f"  Count:      {len(result['runs'])}")
        elif args.command == "summarize":
            report = summarize_parallel_generation_experiment(
                Path(args.experiment_dir) / RUNS_JSONL,
                output_dir=args.output_dir or args.experiment_dir,
            )
            print("RQ2 parallel summary complete")
            print(f"  Subjects: {len(report['subjects'])}")
            print(f"  Workers:  {', '.join(str(worker) for worker in report['workers'])}")
        elif args.command == "sample-config":
            write_sample_config(args.output)
            print(f"Sample config written to: {args.output}")
        else:
            parser.print_help()
            return 1
    except Exception as exc:
        print(f"RQ2 parallel experiment failed: {exc}", file=sys.stderr)
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run and summarize portable RQ2 parallel CSC generation experiments."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the full RQ2 experiment.")
    run_parser.add_argument("--config", help="JSON config file. CLI args override matching fields.")
    run_parser.add_argument("--dataset-root")
    run_parser.add_argument("--subjects-manifest")
    run_parser.add_argument("--output-root")
    run_parser.add_argument("--experiment-dir")
    run_parser.add_argument("--experiment-name")
    run_parser.add_argument("--workers", help="Comma-separated worker counts, e.g. 1,2,4,8.")
    run_parser.add_argument("--repeats", type=int)
    run_parser.add_argument("--mode", choices=["original", "expanded"])
    run_parser.add_argument("--range-bound", type=int)
    run_parser.add_argument("--max-iter", type=int)
    run_parser.add_argument("--timeout-s", type=int)
    run_parser.add_argument("--session-prefix")
    run_parser.add_argument("--project-root")
    run_parser.add_argument("--dry-run", action="store_true", default=None)
    run_parser.add_argument("--allow-existing-sessions", action="store_true", default=None)
    run_parser.add_argument("--append", action="store_true", default=None)
    run_parser.add_argument("--no-summarize", action="store_true", default=None)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize an existing experiment directory.")
    summarize_parser.add_argument("--experiment-dir", required=True)
    summarize_parser.add_argument("--output-dir")

    sample_parser = subparsers.add_parser("sample-config", help="Write a portable sample config JSON.")
    sample_parser.add_argument("--output", required=True)
    return parser


def _run_overrides(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "dataset_root": args.dataset_root,
        "subjects_manifest": args.subjects_manifest,
        "output_root": args.output_root,
        "experiment_dir": args.experiment_dir,
        "experiment_name": args.experiment_name,
        "workers": args.workers,
        "repeats": args.repeats,
        "mode": args.mode,
        "range_bound": args.range_bound,
        "max_iter": args.max_iter,
        "timeout_s": args.timeout_s,
        "session_prefix": args.session_prefix,
        "project_root": args.project_root,
        "dry_run": args.dry_run,
        "allow_existing_sessions": args.allow_existing_sessions,
        "append": args.append,
        "summarize": False if args.no_summarize else None,
    }


def _load_programs(options: RQ2ParallelOptions,
                   dataset_root: Path,
                   project_root: Path) -> list[OriginalProgram]:
    if options.subjects_manifest:
        manifest = _resolve_path(options.subjects_manifest, project_root)
        return load_subject_manifest(manifest, dataset_root)
    return discover_original_programs(dataset_root)


def load_subject_manifest(path: str | Path, dataset_root: str | Path) -> list[OriginalProgram]:
    """Load explicit original programs from a JSONL manifest."""

    manifest = Path(path)
    root = Path(dataset_root)
    programs: list[OriginalProgram] = []
    for line_no, record in enumerate(read_jsonl(manifest), start=1):
        try:
            subject = str(record["subject"])
            class_name = str(record.get("class_name") or Path(record["java_file"]).stem)
            java_file = Path(str(record["java_file"]))
        except KeyError as exc:
            raise ValueError(f"{manifest}:{line_no} missing required field {exc}") from exc
        if not java_file.is_absolute():
            java_file = root / java_file
        if not java_file.is_file():
            raise FileNotFoundError(f"{manifest}:{line_no} java_file not found: {java_file}")
        programs.append(OriginalProgram(subject=subject, class_name=class_name, java_file=java_file.resolve()))
    return programs


def _experiment_config(options: RQ2ParallelOptions,
                       project_root: Path,
                       dataset_root: Path,
                       output_dir: Path,
                       programs: list[OriginalProgram],
                       session_prefix: str) -> dict[str, Any]:
    config = asdict(options)
    config.update({
        "stage": "rq2_parallel_experiment",
        "created_at": _now_local(),
        "project_root": str(project_root),
        "dataset_root": str(dataset_root),
        "experiment_dir": str(output_dir),
        "session_prefix": session_prefix,
        "workers": list(_normalize_workers(options.workers)),
        "program_count": len(programs),
        "programs": [
            {
                "subject": program.subject,
                "class_name": program.class_name,
                "java_file": str(program.java_file),
            }
            for program in programs
        ],
    })
    return config


def _write_subjects(path: Path, programs: list[OriginalProgram]) -> None:
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for program in programs:
            handle.write(json.dumps({
                "subject": program.subject,
                "class_name": program.class_name,
                "java_file": str(program.java_file),
            }, sort_keys=True) + "\n")


def _resolve_project_root(raw: Optional[str | Path]) -> Path:
    if raw:
        return Path(raw).resolve()
    return Path(__file__).resolve().parents[1]


def _resolve_experiment_dir(options: RQ2ParallelOptions, project_root: Path) -> Path:
    if options.experiment_dir:
        return _resolve_path(options.experiment_dir, project_root)
    output_root = _resolve_path(options.output_root, project_root)
    name = _safe_id(options.experiment_name)
    return output_root / f"{name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def _resolve_path(path: str | Path, project_root: Path) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    if p.exists():
        return p.resolve()
    repo_root = project_root.parents[1] if len(project_root.parents) > 1 else project_root
    if p.parts[:2] == ("project", "CSC_EXPANDED"):
        return (repo_root / p).resolve()
    return (project_root / p).resolve()


def _parse_workers(raw: Any) -> list[int]:
    if isinstance(raw, str):
        values = [item.strip() for item in raw.split(",") if item.strip()]
        return [int(value) for value in values]
    return [int(value) for value in raw]


def _normalize_workers(values: tuple[int, ...]) -> list[int]:
    normalized = sorted({int(value) for value in values if int(value) > 0})
    if not normalized:
        raise ValueError("At least one positive worker count is required")
    return normalized


def _version_output(command: list[str]) -> Optional[str]:
    if shutil.which(command[0]) is None:
        return None
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    return output.strip() or None


def _default_session_prefix(experiment_name: str) -> str:
    return _safe_id(f"{experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")


def _safe_id(raw: str) -> str:
    return "".join(char.lower() if char.isalnum() or char in "._-" else "_" for char in raw).strip("_")


def _now_local() -> str:
    return datetime.now().astimezone().isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
