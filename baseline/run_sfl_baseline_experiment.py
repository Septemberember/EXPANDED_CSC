#!/usr/bin/env python3
"""Run SFL baseline on a complete CSC experiment and produce standardised output.

Usage::

    python3 run_sfl_baseline_experiment.py \\
        --manifest dataset/EX_CSC_dataset/mutants_manifest.jsonl \\
        --csc-tmp-root experiments/FL-EX_CSC_dataset/artifacts/csc_tmp \\
        --output-dir experiments/FL-EX_CSC_dataset/baseline-SFL \\
        --top-k 1,3,5,10

Output::

    baseline-SFL/
      <mutant_id>/sfl_localization.json       # per-mutant SFL ranking
      sfl_fault_localization_rows.jsonl        # flat rows (CCT-compatible)
      sfl_fault_localization_rows.csv          # same, CSV
      sfl_fault_localization_summary.md        # human-readable summary
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# Ensure baseline/ and CSC_EXPANDED modules are importable in both portable-kit
# and source-checkout layouts.
_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_CANDIDATES = [
    _ROOT,
    _ROOT / "project" / "CSC_EXPANDED",
]
for _p in _PROJECT_CANDIDATES:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from baseline.SFL.sfl_runner import run_sfl_localization  # noqa: E402
from baseline.SFL.sfl_rows import (  # noqa: E402
    DEFAULT_TOP_K,
    generate_no_metrics_rows,
    generate_sfl_rows,
    write_rows_csv,
    write_rows_jsonl,
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    manifest_by_id = {m["mutant_id"]: m for m in manifest}
    top_k = parse_top_k(args.top_k)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csc_tmp = Path(args.csc_tmp_root)
    session_prefix = args.session_prefix

    all_rows: list[dict[str, Any]] = []
    stats = {"total_manifest": len(manifest), "evaluated": 0, "no_metrics": 0, "errors": 0}

    t0 = time.perf_counter()

    for mid, mrec in sorted(manifest_by_id.items()):
        # Locate the CSC session directory for this mutant
        session_dir = _find_session_dir(csc_tmp, mrec, mid, session_prefix)
        if session_dir is None:
            all_rows.extend(generate_no_metrics_rows(mrec, "session directory not found"))
            stats["no_metrics"] += 1
            stats["errors"] += 1
            continue

        class_dir = session_dir / mrec.get("subject", "")
        if not class_dir.is_dir():
            # Try other class dirs
            subdirs = [d for d in session_dir.iterdir() if d.is_dir()]
            if subdirs:
                class_dir = subdirs[0]

        sfl_path = class_dir / "sfl_localization.json" if class_dir.is_dir() else None
        tbfv_path = class_dir / "refined_tbfv_report.json" if class_dir.is_dir() else None

        # Check if TBFV has any failures
        has_signal = True
        if tbfv_path and tbfv_path.exists():
            tbfv = json.loads(tbfv_path.read_text(encoding="utf-8"))
            if tbfv.get("summary", {}).get("failed", 0) == 0:
                has_signal = False

        if not has_signal:
            all_rows.extend(generate_no_metrics_rows(mrec, "no TBFV failures for SFL spectrum"))
            stats["no_metrics"] += 1
            continue

        # Run SFL.  By default we recompute instead of reusing an existing
        # class-dir report because older reports may contain top-k-truncated
        # rankings and therefore cannot support reliable aggregate evaluation.
        if not args.reuse_existing_sfl:
            sfl_path = None

        if sfl_path is None or not sfl_path.exists():
            if not class_dir.is_dir():
                all_rows.extend(generate_no_metrics_rows(mrec, "class directory not found"))
                stats["no_metrics"] += 1
                stats["errors"] += 1
                continue
            try:
                report = run_sfl_localization(str(class_dir), top_k=None)
            except Exception as exc:
                all_rows.extend(generate_no_metrics_rows(mrec, f"SFL failed: {exc}"))
                stats["no_metrics"] += 1
                stats["errors"] += 1
                continue
        else:
            report = json.loads(sfl_path.read_text(encoding="utf-8"))

        # Save per-mutant report
        per_mutant_dir = output_dir / mid
        per_mutant_dir.mkdir(parents=True, exist_ok=True)
        (per_mutant_dir / "sfl_localization.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )

        # Generate rows
        try:
            rows = generate_sfl_rows(per_mutant_dir / "sfl_localization.json", mrec, top_k)
        except Exception as exc:
            all_rows.extend(generate_no_metrics_rows(mrec, f"row generation failed: {exc}"))
            stats["no_metrics"] += 1
            stats["errors"] += 1
            continue

        all_rows.extend(rows)
        stats["evaluated"] += 1

    t_total = time.perf_counter() - t0

    # Write row-level outputs
    write_rows_jsonl(all_rows, output_dir / "sfl_fault_localization_rows.jsonl")
    write_rows_csv(all_rows, output_dir / "sfl_fault_localization_rows.csv")

    # Write summary
    _write_summary_md(all_rows, stats, output_dir, t_total, top_k)

    print(f"\nSFL baseline experiment complete ({t_total:.1f}s)")
    print(f"  Manifest:    {stats['total_manifest']}")
    print(f"  Evaluated:   {stats['evaluated']}")
    print(f"  No metrics:  {stats['no_metrics']}")
    print(f"  Errors:      {stats['errors']}")
    print(f"  Rows:        {len(all_rows)}")
    print(f"  Output:      {output_dir}")
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_manifest(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Manifest not found: {p}")
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_top_k(raw: str) -> tuple[int, ...]:
    vals = []
    for item in raw.split(","):
        s = item.strip()
        if s and int(s) > 0:
            vals.append(int(s))
    return tuple(vals) if vals else DEFAULT_TOP_K


def _find_session_dir(csc_tmp: Path, mrec: dict[str, Any], mutant_id: str,
                      session_prefix: str) -> Path | None:
    """Find the CSC session directory for a mutant.

    Tries several naming conventions:
      1. <prefix>_<Subject>_M<num>  (e.g. fl_061003_WeightedAddLoop_M1)
      2. ex_csc_*_<Subject>_M<num>
      3. mut_<subject>_m<num>  (legacy)
      4. Direct match on mutant_id suffix
    """
    subject = mrec.get("subject", "")
    # Extract mutant number: "WeightedAddLoop_M1" -> "1"
    mnum = mutant_id.rsplit("_M", 1)[1] if "_M" in mutant_id else None
    if mnum is None:
        return None

    candidates = []

    # 1. Prefix convention
    if session_prefix:
        candidates.append(csc_tmp / f"{session_prefix}_{subject}_M{mnum}")

    # 2. Generic prefix patterns
    for d in sorted(csc_tmp.iterdir()):
        name = d.name
        if not d.is_dir():
            continue
        # Match patterns like *_Subject_M<num>
        d_mnum = name.rsplit("_M", 1)[1] if "_M" in name else None
        if d_mnum and d_mnum == mnum:
            # Check if subject name appears in dir name
            if subject.lower() in name.lower():
                candidates.append(d)
            # Also try matching by class directory name
            for cd in d.iterdir():
                if cd.is_dir() and cd.name == subject:
                    candidates.append(d)
                    break

    # Deduplicate keeping order
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen and c.is_dir():
            seen.add(c)
            unique.append(c)

    return unique[0] if unique else None


def _write_summary_md(rows: list[dict[str, Any]], stats: dict[str, int],
                      output_dir: Path, total_time: float,
                      top_k: tuple[int, ...]) -> None:
    """Write a compact SFL summary Markdown file."""
    evaluated = [r for r in rows if r["status"] == "evaluated"]
    no_metrics = [r for r in rows if r["status"] == "no_metrics"]

    lines = [
        "# SFL Baseline Fault Localization Summary",
        "",
        f"- Manifest mutants: {stats['total_manifest']}",
        f"- Evaluated: {stats['evaluated']}",
        f"- No metrics: {stats['no_metrics']} (no TBFV failures / could not run)",
        f"- Errors: {stats['errors']}",
        f"- Total time: {total_time:.2f}s",
        "",
        "## Strategy Summary",
        "",
    ]

    _append_strategy_table(lines, evaluated)

    if evaluated:
        lines.extend([
            "",
            "## Strategy Summary by Fault Category",
            "",
        ])
        for category, label in (
            ("condition", "Condition/Control-Flow Mutants"),
            ("statement", "Statement/Data-Flow Mutants"),
        ):
            category_rows = [r for r in evaluated if r.get("fault_category") == category]
            lines.extend([
                f"### {label}",
                "",
                f"- Fault category: `{category}`",
                f"- Mutants: {len({r.get('mutant_id') for r in category_rows})}",
                f"- Strategy rows: {len(category_rows)}",
                "",
            ])
            _append_strategy_table(lines, category_rows)
            lines.append("")

    # No-metrics section (deduplicated by mutant)
    if no_metrics:
        seen_mutants = {}
        for r in no_metrics:
            mid = r.get("mutant_id", "")
            if mid not in seen_mutants:
                seen_mutants[mid] = r.get("notes", "")
        lines.extend([
            "",
            "## No-Metrics Mutants",
            "",
            "| Mutant ID | Reason |",
            "|---|---|",
        ])
        for mid in sorted(seen_mutants):
            lines.append(f"| {mid} | {seen_mutants[mid]} |")

    (output_dir / "sfl_fault_localization_summary.md").write_text("\n".join(lines) + "\n")


def _append_strategy_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    by_strategy = {}
    for r in rows:
        by_strategy.setdefault(r["strategy"], []).append(r)

    header = (
        "| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | "
        "Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |"
    )
    sep = "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    lines.extend([header, sep])

    if not by_strategy:
        lines.append("| - | 0 | - | - | - | - | - | - | - | - |")
        return

    for strat in sorted(by_strategy):
        rs = by_strategy[strat]
        n = len(rs)
        hits = sum(1 for r in rs if r["hit"])
        t1 = sum(1 for r in rs if r["top1_hit"]) / n
        t3 = sum(1 for r in rs if r["top3_hit"]) / n
        t5 = sum(1 for r in rs if r["top5_hit"]) / n
        t10 = sum(1 for r in rs if r["top10_hit"]) / n
        ranks = [r["best_rank"] for r in rs if r["best_rank"] is not None]
        avg_rank = sum(ranks) / len(ranks) if ranks else None
        hit_regions = [r["hit_item_region_size"] for r in rs
                       if r["hit_item_region_size"] is not None]
        avg_hit_region = sum(hit_regions) / len(hit_regions) if hit_regions else None
        crs = [r["cumulative_inspection_region_at_first_hit"] for r in rs
               if r["cumulative_inspection_region_at_first_hit"] is not None]
        avg_cr = sum(crs) / len(crs) if crs else None
        label = rs[0].get("strategy_label", strat)
        lines.append(
            f"| {label} | {n} | {hits/n:.3f} | {t1:.3f} | {t3:.3f} | "
            f"{t5:.3f} | {t10:.3f} | {_fmt(avg_rank)} | "
            f"{_fmt(avg_hit_region)} | {_fmt(avg_cr)} |"
        )


def _fmt(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.3f}"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run SFL baseline on a CSC experiment")
    p.add_argument("--manifest", required=True, help="mutants_manifest.jsonl path")
    p.add_argument("--csc-tmp-root", required=True,
                   help="Root of CSC session directories (artifacts/csc_tmp)")
    p.add_argument("--session-prefix", default="",
                   help="Session directory prefix (e.g. 'fl_061003')")
    p.add_argument("--output-dir", required=True,
                   help="Output directory (e.g. experiments/.../baseline-SFL)")
    p.add_argument("--top-k", default="1,3,5,10",
                   help="Comma-separated top-k values (default: 1,3,5,10)")
    p.add_argument("--reuse-existing-sfl", action="store_true",
                   help="Reuse existing class-dir sfl_localization.json files. "
                        "By default SFL rankings are recomputed to avoid stale "
                        "or top-k-truncated reports.")
    return p


if __name__ == "__main__":
    raise SystemExit(main())
