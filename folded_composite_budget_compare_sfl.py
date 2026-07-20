#!/usr/bin/env python3
"""Budget-matched comparison: folded composite vs SFL.

For each mutant, the folded composite (condition_node ∪ folded_edge_partition)
has a ``hit_region`` at each Top-R — the union of all source lines predicted
by the top R items from both rankings.  This script gives SFL the same number
of unique source lines as its inspection budget and compares hit rates.

Usage::

    python3 folded_composite_budget_compare_sfl.py \\
        --experiment-dir experiments/EX_CSC_dataset/fault_localization_core_b \\
        --experiment-dir experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization \\
        --experiment-dir experiments/EX_CSC_dataset/rq_extension_b/FL \\
        --experiment-dir experiments/EX_CSC_dataset/boundary_stress_subjects/RQ3-fault-localization \\
        --output-dir experiments/EX_CSC_dataset/folded_fault_localization/budget_matched \\
        --top-r "1,2,3"
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from csc_engine import (
    CCT,
    aggregate_localization_report,
    load_manifest,
    write_aggregated_localization_report,
)
from csc_engine.failure_localization_fold import (
    build_folded_localization_report,
    write_folded_localization_report,
)


DEFAULT_TOP_R = [1, 2, 3]
DEFAULT_SFL_FORMULA = "ochiai"


def main() -> int:
    args = _build_parser().parse_args()
    experiment_dirs = [Path(d).resolve() for d in args.experiment_dir]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    top_r = _parse_int_list(args.top_r)
    formula = args.sfl_formula

    records = _collect_mutant_records(experiment_dirs)
    all_rows: list[dict[str, Any]] = []
    for record in records:
        row = _compare_one_mutant(record, output_dir, formula, top_r,
                                  args.scoring_strategy)
        all_rows.append(row)

    evaluated = [r for r in all_rows if r.get("status") == "evaluated"]
    _write_outputs(output_dir, all_rows, evaluated, formula, top_r)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Budget-matched folded-composite vs SFL comparison.",
    )
    p.add_argument("--experiment-dir", action="append", required=True,
                   help="Archived experiment directory (repeat for multiple).")
    p.add_argument("--output-dir", required=True, type=Path,
                   help="Output directory for report.")
    p.add_argument("--top-r", default=",".join(str(v) for v in DEFAULT_TOP_R),
                   help="Comma-separated composite Top-R values.")
    p.add_argument("--sfl-formula", default=DEFAULT_SFL_FORMULA,
                   help="SFL formula to compare against.")
    p.add_argument("--scoring-strategy", default="density_log",
                   help="Folded scoring strategy key.")
    return p


# ---------------------------------------------------------------------------
# Mutant record collection
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MutantRecord:
    mutant_id: str
    result_dir: Path           # directory with *_cct.pkl + testcases.json
    sfl_report: Path | None    # sfl_localization.json path
    ground_truth: dict[str, Any]
    subject: str
    operator: str
    fault_kind: str
    fault_category: str


def _collect_mutant_records(experiment_dirs: list[Path]) -> list[MutantRecord]:
    records: list[MutantRecord] = []
    for exp_dir in experiment_dirs:
        records.extend(_collect_from_experiment(exp_dir))
    return records


def _collect_from_experiment(exp_dir: Path) -> list[MutantRecord]:
    # Try manifest-based discovery first.
    manifest_path = exp_dir / "aggregation_ready" / "mutants_manifest.jsonl"
    if manifest_path.exists():
        return _collect_from_manifest(exp_dir, manifest_path)
    return _collect_from_scan(exp_dir)


def _collect_from_manifest(exp_dir: Path,
                           manifest_path: Path) -> list[MutantRecord]:
    records: list[MutantRecord] = []
    for mr in load_manifest(manifest_path):
        mutant_id = str(mr.get("mutant_id", ""))
        result_dir = _find_result_dir(exp_dir, mutant_id)
        if result_dir is None:
            continue
        sfl = _find_sfl_report(exp_dir, mutant_id)
        records.append(MutantRecord(
            mutant_id=mutant_id,
            result_dir=result_dir,
            sfl_report=sfl,
            ground_truth=mr.get("ground_truth", {}),
            subject=str(mr.get("subject", "")),
            operator=str(mr.get("operator", "")),
            fault_kind=str(mr.get("fault_kind", "")),
            fault_category=str(mr.get("fault_category", "")),
        ))
    return records


def _collect_from_scan(exp_dir: Path) -> list[MutantRecord]:
    """Fallback: scan for CCT pickle directories."""
    records: list[MutantRecord] = []
    for cct_path in sorted(exp_dir.glob("**/*_cct.pkl")):
        result_dir = cct_path.parent
        mutant_id = result_dir.name
        sfl = _find_sfl_report(exp_dir, mutant_id)
        records.append(MutantRecord(
            mutant_id=mutant_id,
            result_dir=result_dir,
            sfl_report=sfl,
            ground_truth={},
            subject="",
            operator="",
            fault_kind="",
            fault_category="",
        ))
    return records


def _find_result_dir(exp_dir: Path, mutant_id: str) -> Path | None:
    # Flat layout.
    for cand in sorted(exp_dir.glob(f"**/{mutant_id}")):
        if cand.is_dir() and list(cand.glob("*_cct.pkl")):
            return cand
    # Suffix match.
    for cand in sorted(exp_dir.glob(f"**/*_{mutant_id}")):
        if not cand.is_dir():
            continue
        if list(cand.glob("*_cct.pkl")):
            return cand
        for sub in cand.iterdir():
            if sub.is_dir() and list(sub.glob("*_cct.pkl")):
                return sub
    # Nested csc_tmp layout.
    csc_tmp = exp_dir / "artifacts" / "csc_tmp"
    if csc_tmp.exists():
        for cand in sorted(csc_tmp.glob(f"*_{mutant_id}")):
            if not cand.is_dir():
                continue
            for sub in cand.iterdir():
                if sub.is_dir() and list(sub.glob("*_cct.pkl")):
                    return sub
            if list(cand.glob("*_cct.pkl")):
                return cand
    return None


def _find_sfl_report(exp_dir: Path, mutant_id: str) -> Path | None:
    """Locate sfl_localization.json for *mutant_id*."""
    for base in ["baseline-SFL-v2", "baseline-SFL"]:
        sfl_dir = exp_dir / base
        if not sfl_dir.exists():
            continue
        for cand in _mutant_dir_candidates(sfl_dir, mutant_id):
            path = cand / "sfl_localization.json"
            if path.exists():
                return path
    return None


def _mutant_dir_candidates(base: Path, mutant_id: str) -> list[Path]:
    cands: list[Path] = []
    for c in sorted(base.glob(f"**/{mutant_id}")):
        if c.is_dir():
            cands.append(c)
    for c in sorted(base.glob(f"**/*_{mutant_id}")):
        if c.is_dir():
            cands.append(c)
    return cands


# ---------------------------------------------------------------------------
# Per-mutant comparison
# ---------------------------------------------------------------------------


def _compare_one_mutant(
    rec: MutantRecord,
    output_dir: Path,
    formula: str,
    top_r: list[int],
    scoring: str,
) -> dict[str, Any]:
    base = {
        "mutant_id": rec.mutant_id,
        "subject": rec.subject,
        "operator": rec.operator,
        "fault_kind": rec.fault_kind,
        "fault_category": rec.fault_category,
        "primary_line": rec.ground_truth.get("primary_line"),
        "scoring_strategy": scoring,
    }

    # --- Load CCT ---
    cct_paths = sorted(rec.result_dir.glob("*_cct.pkl"))
    if not cct_paths:
        return base | {"status": "skipped", "reason": "no_cct_pickle"}
    cct = CCT.load_from_file(str(cct_paths[0]))
    if cct is None:
        return base | {"status": "skipped", "reason": "cct_load_failed"}

    # --- Load testcases ---
    tc_path = rec.result_dir / "testcases.json"
    if not tc_path.exists():
        return base | {"status": "skipped", "reason": "no_testcases_json"}
    testcase_records: list[dict[str, Any]] = json.loads(
        tc_path.read_text(encoding="utf-8")
    )
    for tc in testcase_records:
        tp = Path(tc.get("trace_path", ""))
        if not tp.exists():
            remapped = rec.result_dir / tp
            if remapped.exists():
                tc["trace_path"] = str(remapped)
            elif "traces" in tp.parts:
                idx = tp.parts.index("traces")
                remapped2 = rec.result_dir.joinpath(*tp.parts[idx:])
                if remapped2.exists():
                    tc["trace_path"] = str(remapped2)

    # --- Build folded report ---
    try:
        report = build_folded_localization_report(cct, testcase_records, scoring)
    except Exception as exc:
        return base | {"status": "skipped", "reason": f"fold_error:{exc}"}

    # --- Aggregate report ---
    source_file = rec.ground_truth.get("primary_file")
    aggregated = aggregate_localization_report(
        report, source_file=source_file,
    )

    # Write artifacts.
    out_dir = output_dir / "artifacts" / rec.mutant_id
    out_dir.mkdir(parents=True, exist_ok=True)
    write_folded_localization_report(report, str(out_dir / "cct_folded_localization.json"))
    write_aggregated_localization_report(aggregated,
                                         str(out_dir / "cct_folded_localization_aggregated.json"))

    # Check TBFV failures.
    F_total = report["summary"].get("F_total", 0)
    if F_total == 0:
        return base | {"status": "not_detected", "reason": "no_tbfv_failures",
                       "F_total": F_total,
                       "P_total": report["summary"].get("P_total", 0)}

    # --- Extract composite hit regions ---
    condition_ranking = aggregated.get("aggregated_condition_node_ranking", [])
    edge_partition = aggregated.get("aggregated_interval_rankings", {}).get(
        "folded_edge_partition", [])

    # --- Load SFL ranking ---
    sfl_ranked: list[dict[str, Any]] = []
    if rec.sfl_report is not None and rec.sfl_report.exists():
        sfl_data = json.loads(rec.sfl_report.read_text(encoding="utf-8"))
        sfl_ranked = sfl_data.get("rankings", {}).get(formula, [])

    # --- Acceptable lines for hit check ---
    acceptable = _acceptable_line_set(rec.ground_truth)
    window = _acceptable_window(rec.ground_truth)

    def _lines_hit(lines: set[int]) -> bool:
        if acceptable.intersection(lines):
            return True
        if window is not None:
            start, end = window
            return any(start <= line <= end for line in lines)
        return False

    # --- Compute budgets and hits per Top-R ---
    row = dict(base)
    row["status"] = "evaluated"
    row["F_total"] = F_total
    row["P_total"] = report["summary"].get("P_total", 0)

    for r_val in sorted(top_r):
        # Folded composite: union of condition[:r] + edge_partition[:r] lines.
        folded_lines: set[int] = set()
        for p in condition_ranking[:r_val]:
            line = p.get("line")
            if line is not None:
                folded_lines.add(int(line))
        for p in edge_partition[:r_val]:
            for sl in (p.get("statement_lines") or []):
                if sl is not None:
                    folded_lines.add(int(sl))
        budget = len(folded_lines)
        folded_hit = _lines_hit(folded_lines)

        # SFL: same budget of unique source lines.
        sfl_lines: set[int] = set()
        for item in sfl_ranked:
            if len(sfl_lines) >= budget:
                break
            sfl_lines.add(int(item["line"]))
        sfl_hit = _lines_hit(sfl_lines)

        row.update({
            f"top{r_val}_budget": budget,
            f"top{r_val}_folded_hit": folded_hit,
            f"top{r_val}_sfl_hit": sfl_hit,
        })

    return row


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def _write_outputs(
    output_dir: Path,
    all_rows: list[dict[str, Any]],
    evaluated: list[dict[str, Any]],
    formula: str,
    top_r: list[int],
) -> None:
    # JSONL.
    (output_dir / "budget_matched_rows.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in all_rows),
        encoding="utf-8",
    )
    # CSV.
    if all_rows:
        fields = sorted({k for r in all_rows for k in r})
        with (output_dir / "budget_matched_rows.csv").open("w", encoding="utf-8",
                                                           newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(all_rows)

    # Summary + markdown.
    summary = _build_summary(evaluated, top_r)
    (output_dir / "budget_matched_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    (output_dir / "budget_matched_summary.md").write_text(
        "\n".join(_build_markdown(summary, formula, top_r)), encoding="utf-8",
    )

    # Metadata.
    (output_dir / "budget_matched_metadata.json").write_text(json.dumps({
        "sfl_formula": formula,
        "top_r": top_r,
        "total_tasks": len(all_rows),
        "evaluated": len(evaluated),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Budget-matched comparison complete: {output_dir}")
    print(f"  Tasks:     {len(all_rows)}")
    print(f"  Evaluated: {len(evaluated)}")


def _build_summary(evaluated: list[dict[str, Any]],
                   top_r: list[int]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    categories = ["overall"]
    for r in evaluated:
        cat = str(r.get("fault_category") or "<missing>")
        if cat not in categories:
            categories.append(cat)

    for cat in categories:
        if cat == "overall":
            cat_rows = evaluated
        else:
            cat_rows = [r for r in evaluated
                        if str(r.get("fault_category")) == cat]
        N = len(cat_rows)
        if N == 0:
            continue
        s = {"fault_category": cat, "cases": N}
        for r_val in sorted(top_r):
            fold_hits = sum(1 for r in cat_rows
                            if r.get(f"top{r_val}_folded_hit"))
            sfl_hits = sum(1 for r in cat_rows
                           if r.get(f"top{r_val}_sfl_hit"))
            budgets = [int(r.get(f"top{r_val}_budget", 0)) for r in cat_rows]
            s.update({
                f"top{r_val}_mean_budget": mean(budgets) if budgets else 0,
                f"top{r_val}_folded_hits": fold_hits,
                f"top{r_val}_folded_rate": fold_hits / N if N else 0,
                f"top{r_val}_sfl_hits": sfl_hits,
                f"top{r_val}_sfl_rate": sfl_hits / N if N else 0,
            })
        summary.append(s)
    return summary


def _build_markdown(summary: list[dict[str, Any]],
                    formula: str,
                    top_r: list[int]) -> list[str]:
    lines = [
        "# Budget-Matched Comparison: Folded Composite vs SFL",
        "",
        f"- SFL formula: `{formula}`",
        f"- Top-R: {', '.join(str(r) for r in sorted(top_r))}",
        "- Method: folded composite inspection budget = union of condition[:R] "
        "and edge_partition[:R] lines.  SFL receives the same number of unique "
        "source lines.",
        "",
    ]
    for s in summary:
        r_vals = sorted(top_r)
        lines.append(f"## {s['fault_category']} (N={s['cases']})")
        lines.append("")
        header = ("| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate "
                  "(same budget) |")
        sep = "| --- | ---: | ---: | ---: |"
        lines.append(header)
        lines.append(sep)
        for r_val in r_vals:
            budget = s[f"top{r_val}_mean_budget"]
            fr = s[f"top{r_val}_folded_rate"]
            sr = s[f"top{r_val}_sfl_rate"]
            lines.append(
                f"| {r_val} | {budget:.1f} | "
                f"{s[f'top{r_val}_folded_hits']}/{s['cases']} ({fr:.3f}) | "
                f"{s[f'top{r_val}_sfl_hits']}/{s['cases']} ({sr:.3f}) |"
            )
        lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Ground-truth helpers (mirrors eval layer logic)
# ---------------------------------------------------------------------------


def _acceptable_line_set(gt: dict[str, Any]) -> set[int]:
    lines = gt.get("acceptable_lines")
    if not lines:
        primary = gt.get("primary_line")
        lines = [primary] if primary is not None else []
    return {int(line) for line in lines if line is not None}


def _acceptable_window(gt: dict[str, Any]) -> tuple[int, int] | None:
    window = gt.get("acceptable_line_window")
    if not isinstance(window, list) or len(window) != 2:
        return None
    start, end = window
    if start is None or end is None:
        return None
    return int(start), int(end)


def _parse_int_list(raw: str) -> list[int]:
    vals = sorted({int(s.strip()) for s in raw.split(",") if s.strip()})
    return [v for v in vals if v > 0]


if __name__ == "__main__":
    raise SystemExit(main())
