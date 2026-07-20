#!/usr/bin/env python3
"""Backfill canonical RQ2 fingerprints from retained raw CCT artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from csc_experiments.parallel_generation import (
    RUNS_JSONL,
    append_jsonl,
    archive_generation_artifacts,
    read_jsonl,
    summarize_parallel_generation_experiment,
    write_json,
)


DEFAULT_RUNS = (
    "experiments/EX_CSC_dataset/rq2_parallel_generation/parallel_generation_runs.jsonl",
    "experiments/EX_CSC_dataset/rq_extension_a/RQ2-parallel/parallel_generation_runs.jsonl",
    "experiments/EX_CSC_dataset/rq_extension_b/RQ2-parallel/parallel_generation_runs.jsonl",
)


def build_validation(source_runs: list[Path], output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    combined_runs = output_dir / RUNS_JSONL
    if combined_runs.exists():
        raise FileExistsError(f"Combined run record already exists: {combined_runs}")

    records = []
    for source in source_runs:
        for raw in read_jsonl(source):
            record = dict(raw)
            result_dir = Path(record["result_dir"])
            class_name = str(record["class_name"])
            archive_dir = output_dir / "artifacts" / str(record["session"]) / class_name
            archived = archive_generation_artifacts(result_dir, archive_dir)
            fingerprint_path = archive_dir / "generation_fingerprint.json"
            if not fingerprint_path.is_file():
                raise RuntimeError(f"Fingerprint could not be computed for {result_dir}")
            record["archive_dir"] = str(archive_dir.resolve())
            record["archived_files"] = archived
            record["fingerprint_backfilled_from"] = str(result_dir)
            record["source_runs_jsonl"] = str(source.resolve())
            append_jsonl(combined_runs, record)
            records.append(record)

    write_json(output_dir / "fingerprint_validation_config.json", {
        "stage": "rq2_fingerprint_backfill",
        "source_runs": [str(path.resolve()) for path in source_runs],
        "run_count": len(records),
        "subject_count": len({record["subject"] for record in records}),
        "workers": sorted({int(record["workers"]) for record in records}),
        "fingerprint_schema_version": 1,
    })
    return summarize_parallel_generation_experiment(combined_runs, output_dir=output_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs-jsonl",
        action="append",
        help="Source RQ2 run record; repeat for multiple batches.",
    )
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    sources = [Path(path) for path in (args.runs_jsonl or DEFAULT_RUNS)]
    report = build_validation(sources, Path(args.output_dir))
    print(f"Runs: {report['run_count']}")
    print(
        "Complete/invariant fingerprint subjects: "
        f"{report['fingerprint_complete_subject_count']}/"
        f"{report['fingerprint_invariant_subject_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
