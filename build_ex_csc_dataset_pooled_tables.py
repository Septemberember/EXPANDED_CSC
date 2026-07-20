#!/usr/bin/env python3
"""Pool EX_CSC_dataset data into combined paper tables for RQ1, RQ2, and Kill."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "experiments" / "EX_CSC_dataset" / "paper_tables"

# ============================================================================
# RQ1: Bounded Completion Structural Comparison
# ============================================================================

# Loop-free subjects from the unified EX_CSC dataset.
LOOP_FREE = {
    "BubbleSortFive", "GappedSwapFive", "MaxOfFive", "MedianOfSix",
    "MedianWindowFive", "PairSortCheck", "SelectionSortFive",
}
# Some RQ1 summaries use shorter names such as "BubbleSort"; normalize them
# to the public subject directory names.
NAME_NORMALIZE = {
    "BubbleSort": "BubbleSortFive",
    "SelectionSort": "SelectionSortFive",
}


def _norm(name: str) -> str:
    return NAME_NORMALIZE.get(name, name)


def load_rq1_subjects() -> dict[str, list[dict]]:
    """Return {mode: [per-subject rows]} for all 42 subjects."""
    rows: dict[str, list[dict]] = {"CSC-only": [], "CSC+Boundary": []}

    # Core RQ1 summary from the unified experiment directory.
    # Parse the markdown table manually
    md_path = ROOT / "experiments/EX_CSC_dataset/rq1_bounded_completion/rq1_summary.md"
    with md_path.open() as f:
        lines = f.readlines()

    in_table = False
    for line in lines:
        line = line.strip()
        if line.startswith("| Subject"):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 12:
            continue
        # | Subject | Class | T CSC | T Bnd | E CSC | E Bnd | ⊥ CSC | ⊥ Bnd | ⊥_B | N CSC | N Bnd | W CSC | W Bnd |
        try:
            subject = _norm(parts[1])
            cls = parts[2].strip()
            t_csc = float(parts[3]) if parts[3].strip() else 0
            t_bnd = float(parts[4]) if parts[4].strip() else 0
            e_csc = float(parts[5]) if parts[5].strip() else 0
            e_bnd = float(parts[6]) if parts[6].strip() else 0
            inf_csc = float(parts[7]) if parts[7].strip() else 0
            inf_bnd = float(parts[8]) if parts[8].strip() else 0
            oor_bnd = float(parts[9]) if parts[9].strip() else 0
            n_csc = float(parts[10]) if parts[10].strip() else 0
            n_bnd = float(parts[11]) if parts[11].strip() else 0
            w_csc = float(parts[12]) if parts[12].strip() else 0
            w_bnd = float(parts[13]) if len(parts) > 13 and parts[13].strip() else 0
        except (ValueError, IndexError):
            continue

        rows["CSC-only"].append({
            "subject": subject, "class": cls,
            "tests": t_csc, "empty_anc": e_csc, "infeasible": inf_csc,
            "out_of_range": 0, "nodes": n_csc, "wall_time": w_csc,
        })
        rows["CSC+Boundary"].append({
            "subject": subject, "class": cls,
            "tests": t_bnd, "empty_anc": e_bnd, "infeasible": inf_bnd,
            "out_of_range": oor_bnd, "nodes": n_bnd, "wall_time": w_bnd,
        })

    # Additional unified-dataset RQ1 summaries from rq1_comparison.json.
    # per_subject_comparison contains CSC-only (one per subject) and CSC+Boundary
    # (1 per subject per repeat for W=1).
    # For CSC-only: one row per subject, use directly.
    # For CSC+Boundary: average over repeats for each subject.
    from collections import defaultdict

    for exp_dir in [
        "experiments/EX_CSC_dataset/rq_extension_a/RQ1-boundary",
        "experiments/EX_CSC_dataset/rq_extension_b/RQ1-boundary",
        "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ1-boundary",
    ]:
        comp_path = ROOT / exp_dir / "rq1_comparison.json"
        if not comp_path.exists():
            continue
        comp = json.loads(comp_path.read_text())
        per_subj = comp.get("per_subject_comparison", [])
        cls = "loop-bearing"

        # Separate CSC-only and CSC+Boundary
        csc_only_rows = [s for s in per_subj if s.get("mode") == "CSC-only"]
        boundary_rows = [s for s in per_subj if s.get("mode") == "CSC+Boundary"]

        for s in csc_only_rows:
            rows["CSC-only"].append({
                "subject": _norm(s.get("subject", "")),
                "class": cls,
                "tests": s.get("covered_leaves", 0),
                "empty_anc": s.get("empty_leaves", 0),
                "infeasible": s.get("infeasible_leaves", 0),
                "out_of_range": 0,
                "nodes": s.get("total_nodes", 0),
                "wall_time": s.get("wall_time_s", 0),
            })

        # Average Boundary repeats per subject
        bnd_by_subject = defaultdict(list)
        for s in boundary_rows:
            bnd_by_subject[s.get("subject", "")].append(s)
        for subject, reps in bnd_by_subject.items():
            rows["CSC+Boundary"].append({
                "subject": _norm(subject),
                "class": cls,
                "tests": mean(s.get("covered_leaves", 0) for s in reps),
                "empty_anc": mean(s.get("empty_leaves", 0) for s in reps),
                "infeasible": mean(s.get("infeasible_leaves", 0) for s in reps),
                "out_of_range": mean(s.get("out_of_range_leaves", 0) for s in reps),
                "nodes": mean(s.get("total_nodes", 0) for s in reps),
                "wall_time": mean(s.get("wall_time_s", 0) for s in reps),
            })

    return rows


def build_rq1_table(rows: dict[str, list[dict]]) -> None:
    """Build RQ1 structural table."""
    output_rows = []
    for cls_name, cls_label in [("loop-free", "Loop-free"), ("loop-bearing", "Loop-bearing")]:
        cls_subjects = [r for r in rows["CSC-only"] if r["class"] == cls_name]
        n = len(cls_subjects)
        for mode in ["CSC-only", "CSC+Boundary"]:
            mode_rows = [r for r in rows[mode] if r["class"] == cls_name]
            if not mode_rows:
                continue
            output_rows.append({
                "structural_class": cls_label,
                "n": n,
                "configuration": mode,
                "test_cases": round(mean(r["tests"] for r in mode_rows), 1),
                "empty_anc": round(mean(r["empty_anc"] for r in mode_rows), 1),
                "infeasible": round(mean(r["infeasible"] for r in mode_rows), 1),
                "out_of_range": round(mean(r["out_of_range"] for r in mode_rows), 1),
                "cct_nodes": round(mean(r["nodes"] for r in mode_rows), 1),
                "wall_time_s": round(mean(r["wall_time"] for r in mode_rows), 1),
            })

    with open(OUTPUT / "rq1_bounded_completion.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=output_rows[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(output_rows)
    return output_rows


# ============================================================================
# RQ1 Kill: Mutant Killing Analysis
# ============================================================================

def build_kill_tables() -> dict:
    """Pool kill rows and produce per-dataset and per-category tables."""
    rows = []
    for kill_file in [
        "experiments/EX_CSC_dataset/boundary_kill_core/aggregate_ready/tbfv_boundary_kill_rows.jsonl",
        "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ1-kill-mutant/aggregate_ready/tbfv_boundary_kill_rows.jsonl",
    ]:
        full_path = ROOT / kill_file
        with open(full_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        print(f"  Loaded {len(rows)} rows so far from {kill_file}")

    # Verify kill invariants
    for r in rows:
        assert r["both_killed"] == (r["csc_only_killed"] and r["boundary_killed"]), \
            f"Invariant violation: both_killed for {r['mutant_id']}"
        assert r["boundary_only_killed"] == (r["boundary_killed"] and not r["csc_only_killed"]), \
            f"Invariant violation: boundary_only for {r['mutant_id']}"
        assert r["neither_killed"] == (not r["csc_only_killed"] and not r["boundary_killed"]), \
            f"Invariant violation: neither for {r['mutant_id']}"

    # Per-dataset table
    by_dataset = defaultdict(list)
    for r in rows:
        by_dataset[r.get("dataset_label", r.get("dataset_key", "?"))].append(r)

    dataset_order = ["EX_CSC_dataset"]
    dataset_rows = []
    for ds in dataset_order:
        if ds not in by_dataset:
            continue
        group = by_dataset[ds]
        n = len(group)
        csc = sum(1 for r in group if r["csc_only_killed"])
        bnd = sum(1 for r in group if r["boundary_killed"])
        bnd_only = sum(1 for r in group if r["boundary_only_killed"])
        both = sum(1 for r in group if r["both_killed"])
        neither = sum(1 for r in group if r["neither_killed"])
        dataset_rows.append({
            "dataset": ds,
            "mutants": n,
            "csc_only_killed": csc,
            "csc_only_pct": round(100 * csc / n, 1),
            "boundary_killed": bnd,
            "boundary_pct": round(100 * bnd / n, 1),
            "boundary_only": bnd_only,
            "boundary_only_pct": round(100 * bnd_only / n, 1),
            "both_killed": both,
            "neither_killed": neither,
            "neither_pct": round(100 * neither / n, 1),
        })
    # Total row
    n = len(rows)
    csc = sum(1 for r in rows if r["csc_only_killed"])
    bnd = sum(1 for r in rows if r["boundary_killed"])
    bnd_only = sum(1 for r in rows if r["boundary_only_killed"])
    both = sum(1 for r in rows if r["both_killed"])
    neither = sum(1 for r in rows if r["neither_killed"])
    dataset_rows.append({
        "dataset": "Total",
        "mutants": n,
        "csc_only_killed": csc,
        "csc_only_pct": round(100 * csc / n, 1),
        "boundary_killed": bnd,
        "boundary_pct": round(100 * bnd / n, 1),
        "boundary_only": bnd_only,
        "boundary_only_pct": round(100 * bnd_only / n, 1),
        "both_killed": both,
        "neither_killed": neither,
        "neither_pct": round(100 * neither / n, 1),
    })

    with open(OUTPUT / "rq1_mutant_killing.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=dataset_rows[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(dataset_rows)

    # Per-category table
    for cat, cat_label in [("condition", "Condition"), ("statement", "Statement")]:
        group = [r for r in rows if r.get("fault_category") == cat]
        cat_n = len(group)
        cat_csc = sum(1 for r in group if r["csc_only_killed"])
        cat_bnd = sum(1 for r in group if r["boundary_killed"])
        cat_bnd_only = sum(1 for r in group if r["boundary_only_killed"])
        cat_both = sum(1 for r in group if r["both_killed"])
        cat_neither = sum(1 for r in group if r["neither_killed"])
        # Write as append
        mode = "w" if cat == "condition" else "a"
        with open(OUTPUT / "rq1_mutant_killing_by_category.csv", mode, newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "fault_category", "mutants", "csc_only_killed", "csc_only_pct",
                "boundary_killed", "boundary_pct", "boundary_only", "boundary_only_pct",
                "both_killed", "neither_killed", "neither_pct",
            ], lineterminator="\n")
            if mode == "w":
                w.writeheader()
            w.writerow({
                "fault_category": cat_label,
                "mutants": cat_n,
                "csc_only_killed": cat_csc,
                "csc_only_pct": round(100 * cat_csc / cat_n, 1),
                "boundary_killed": cat_bnd,
                "boundary_pct": round(100 * cat_bnd / cat_n, 1),
                "boundary_only": cat_bnd_only,
                "boundary_only_pct": round(100 * cat_bnd_only / cat_n, 1),
                "both_killed": cat_both,
                "neither_killed": cat_neither,
                "neither_pct": round(100 * cat_neither / cat_n, 1),
            })

    # Per-operator table
    by_op = defaultdict(list)
    for r in rows:
        by_op[r.get("operator", "?")].append(r)
    op_rows = []
    for op in sorted(by_op):
        group = by_op[op]
        op_n = len(group)
        op_csc = sum(1 for r in group if r["csc_only_killed"])
        op_bnd = sum(1 for r in group if r["boundary_killed"])
        op_bnd_only = sum(1 for r in group if r["boundary_only_killed"])
        op_both = sum(1 for r in group if r["both_killed"])
        op_neither = sum(1 for r in group if r["neither_killed"])
        op_rows.append({
            "operator": op,
            "mutants": op_n,
            "csc_only_killed": op_csc,
            "csc_only_pct": round(100 * op_csc / op_n, 1),
            "boundary_killed": op_bnd,
            "boundary_pct": round(100 * op_bnd / op_n, 1),
            "boundary_only": op_bnd_only,
            "boundary_only_pct": round(100 * op_bnd_only / op_n, 1),
            "neither_killed": op_neither,
            "neither_pct": round(100 * op_neither / op_n, 1),
        })
    with open(OUTPUT / "rq1_mutant_killing_by_operator.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=op_rows[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(op_rows)

    # Save combined JSONL for reference
    combined_kill_path = OUTPUT / "aggregate_ready" / "tbfv_boundary_kill_rows.jsonl"
    with open(combined_kill_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    return {
        "total_mutants": n,
        "csc_only_killed": csc,
        "boundary_killed": bnd,
        "boundary_only": bnd_only,
        "both_killed": both,
        "neither_killed": neither,
    }


# ============================================================================
# RQ2: Worker Scaling
# ============================================================================

def load_rq2_subject_means() -> tuple[dict[int, list[dict]], dict[int, dict]]:
    """Return ({worker: [per-subject mean rows]}, {worker: aggregate_test_node_data}).

    Wall time from parallel_generation_runs.jsonl (subject-level means).
    Test/cct counts from parallel_generation_summary.json overall_summary.
    """
    from collections import defaultdict

    all_runs: list[dict] = []
    for rq2_file in [
        "experiments/EX_CSC_dataset/rq2_parallel_generation/parallel_generation_runs.jsonl",
        "experiments/EX_CSC_dataset/rq_extension_a/RQ2-parallel/parallel_generation_runs.jsonl",
        "experiments/EX_CSC_dataset/rq_extension_b/RQ2-parallel/parallel_generation_runs.jsonl",
        "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ2-parallel/parallel_generation_runs.jsonl",
    ]:
        with open(ROOT / rq2_file) as f:
            for line in f:
                all_runs.append(json.loads(line))

    # Group runs by (subject, workers) → average wall_time over repeats
    groups = defaultdict(list)
    for r in all_runs:
        if "wall_time_s" not in r:
            continue
        key = (r["subject"], r["workers"])
        groups[key].append(r)

    # Compute subject-level means (wall time only for now)
    subj_means: dict[int, list[dict]] = defaultdict(list)
    for (subject, workers), reps in groups.items():
        tw = mean(r["wall_time_s"] for r in reps)
        subj_means[workers].append({
            "subject": subject, "workers": workers,
            "wall_time_s": tw,
        })

    # Compute T1 map and speedup
    t1_map = {}
    for sm in subj_means[1]:
        t1_map[sm["subject"]] = sm["wall_time_s"]

    for w in subj_means:
        for sm in subj_means[w]:
            t1 = t1_map.get(sm["subject"])
            if t1 and t1 > 0:
                sm["speedup"] = t1 / sm["wall_time_s"]
            else:
                sm["speedup"] = 1.0

    # Read aggregate test/cct counts from summary overall_summary
    # These are invariant across workers (same for all W), use W=1
    agg_counts: dict[int, dict] = {}
    all_summaries = []
    for summary_file in [
        "experiments/EX_CSC_dataset/rq2_parallel_generation/parallel_generation_summary.json",
        "experiments/EX_CSC_dataset/rq_extension_a/RQ2-parallel/parallel_generation_summary.json",
        "experiments/EX_CSC_dataset/rq_extension_b/RQ2-parallel/parallel_generation_summary.json",
        "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ2-parallel/parallel_generation_summary.json",
    ]:
        sp = ROOT / summary_file
        if sp.exists():
            all_summaries.append(json.loads(sp.read_text()))

    # Pool all enriched runs from all summaries to compute aggregate means
    all_enriched: list[dict] = []
    for summary in all_summaries:
        all_enriched.extend(summary.get("runs", []))

    # Per-worker aggregate: per-subject mean (avg over repeats first, then mean over subjects)
    for w in [1, 2, 4, 8]:
        w_runs = [r for r in all_enriched if r.get("workers") == w]
        # Group by subject, average over repeats
        subj_reps: dict[str, list] = defaultdict(list)
        for r in w_runs:
            subj_reps[r.get("subject", "")].append(r)
        subj_means_tc = []
        subj_means_cn = []
        for reps in subj_reps.values():
            tc_vals = [r.get("testcase_count") for r in reps if r.get("testcase_count") is not None]
            cn_vals = [r.get("total_nodes") for r in reps if r.get("total_nodes") is not None]
            if tc_vals:
                subj_means_tc.append(mean(tc_vals))
            if cn_vals:
                subj_means_cn.append(mean(cn_vals))
        agg_counts[w] = {
            "testcases": round(mean(subj_means_tc), 1) if subj_means_tc else 0,
            "cct_nodes": round(mean(subj_means_cn), 1) if subj_means_cn else 0,
        }

    return subj_means, agg_counts, all_summaries


def build_rq2_table(subj_means: dict[int, list[dict]], agg_counts: dict[int, dict],
                    all_summaries: list[dict]) -> list[dict]:
    """Build RQ2 worker scaling table."""
    # Build T1 map for speedup computation
    t1_map = {}
    for sm in subj_means[1]:
        t1_map[sm["subject"]] = sm["wall_time_s"]

    output_rows = []
    for w in [1, 2, 4, 8]:
        sm_list = subj_means[w]
        times = [sm["wall_time_s"] for sm in sm_list]
        sp = [sm["speedup"] for sm in sm_list]
        tc = agg_counts.get(w, {}).get("testcases", 0)
        cn = agg_counts.get(w, {}).get("cct_nodes", 0)

        output_rows.append({
            "workers": w,
            "n_subjects": len(sm_list),
            "mean_time_s": round(mean(times), 2),
            "median_time_s": round(median(times), 2),
            "mean_testcases": tc,
            "mean_cct_nodes": cn,
            "mean_speedup": round(mean(sp), 2),
            "median_speedup": round(median(sp), 2),
        })

    with open(OUTPUT / "rq2_worker_scaling.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=output_rows[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(output_rows)

    # Representative cases at W=8
    w8_list = subj_means[8]
    w8_sorted = sorted(w8_list, key=lambda x: x["speedup"])
    n = len(w8_sorted)
    # Get per-subject test/node counts from W=1 enriched runs
    subj_tc_cn: dict[str, dict] = {}
    for summary in all_summaries:
        for r in summary.get("runs", []):
            if r.get("workers") == 1:
                subj = r.get("subject", "")
                if subj not in subj_tc_cn:
                    subj_tc_cn[subj] = {
                        "testcases": r.get("testcase_count"),
                        "cct_nodes": r.get("total_nodes"),
                        "mean_frontier_width": r.get("mean_frontier_width"),
                        "max_frontier_width": r.get("max_frontier_width"),
                    }
    quantiles = {}
    for role, idx in [("min", 0), ("q1", n // 4), ("median", n // 2), ("q3", 3 * n // 4), ("max", -1)]:
        sm = w8_sorted[idx]
        t1 = t1_map.get(sm["subject"])
        info = subj_tc_cn.get(sm["subject"], {})
        quantiles[role] = {
            "role": role,
            "subject": sm["subject"],
            "tests": info.get("testcases", ""),
            "cct_nodes": info.get("cct_nodes", ""),
            "mean_frontier_width": info.get("mean_frontier_width", ""),
            "max_frontier_width": info.get("max_frontier_width", ""),
            "t1": round(t1, 2) if t1 else "",
            "t8": round(sm["wall_time_s"], 2),
            "s8": round(sm["speedup"], 2),
        }

    rep_rows = [quantiles[r] for r in ["min", "q1", "median", "q3", "max"]]
    with open(OUTPUT / "rq2_representative_cases.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rep_rows[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(rep_rows)

    return output_rows


# ============================================================================
# Markdown Preview
# ============================================================================

def write_preview(rq1_rows, rq2_rows, kill_stats):
    lines = []
    lines.append("# Paper Result Tables Draft: EX_CSC_dataset")
    lines.append("")
    lines.append("This directory contains standalone draft tables for RQ1, RQ2, RQ1-Kill, and RQ3.")
    lines.append("")

    # RQ1
    lines.append("## RQ1: Bounded Completion (Structural Class)")
    lines.append("")
    h = rq1_rows[0].keys()
    lines.append("| " + " | ".join(h) + " |")
    lines.append("|" + "|".join(["---"] * len(h)) + "|")
    for r in rq1_rows:
        vals = [str(r[k]) for k in h]
        lines.append("| " + " | ".join(vals) + " |")
    lines.append("")

    # RQ1 Kill
    lines.append("## RQ1: Mutant Killing (CSC-only vs CSC+Boundary)")
    lines.append("")
    kill_csv = OUTPUT / "rq1_mutant_killing.csv"
    with open(kill_csv) as f:
        kill_rows = list(csv.DictReader(f))
    h2 = kill_rows[0].keys()
    lines.append("| " + " | ".join(h2) + " |")
    lines.append("|" + "|".join(["---:"] * len(h2)) + "|")
    for r in kill_rows:
        vals = [str(r[k]) for k in h2]
        lines.append("| " + " | ".join(vals) + " |")
    lines.append("")

    # Kill by category
    lines.append("### Kill Results by Fault Category")
    lines.append("")
    cat_csv = OUTPUT / "rq1_mutant_killing_by_category.csv"
    with open(cat_csv) as f:
        cat_rows = list(csv.DictReader(f))
    h3 = cat_rows[0].keys()
    lines.append("| " + " | ".join(h3) + " |")
    lines.append("|" + "|".join(["---:"] * len(h3)) + "|")
    for r in cat_rows:
        vals = [str(r[k]) for k in h3]
        lines.append("| " + " | ".join(vals) + " |")
    lines.append("")

    # RQ2
    lines.append("## RQ2: Parallel Worker Scaling")
    lines.append("")
    h4 = rq2_rows[0].keys()
    lines.append("| " + " | ".join(h4) + " |")
    lines.append("|" + "|".join(["---:"] * len(h4)) + "|")
    for r in rq2_rows:
        vals = [str(r[k]) for k in h4]
        lines.append("| " + " | ".join(vals) + " |")
    lines.append("")

    # RQ3 placeholder (refer to auto-generated tables)
    lines.append("## RQ3: Budget-Matched Fault Localization")
    lines.append("")
    lines.append("See auto-generated tables:")
    lines.append("- `rq3_budget_matched_main_table.csv`")
    lines.append("- `rq3_budget_matched_all_baselines.csv`")
    lines.append("- `rq3_folded_view_decomposition.csv`")
    lines.append("- `rq3_top3_misses_by_operator.csv`")
    lines.append("- `rq3_paired_comparison.csv`")
    lines.append("")

    # Notes
    lines.append("## Notes")
    lines.append(f"- Combined from EX_CSC_dataset: {kill_stats['total_mutants']} mutants, "
                  f"{kill_stats['csc_only_killed']} CSC-only kills, {kill_stats['boundary_killed']} Boundary kills, "
                  f"{kill_stats['boundary_only']} Boundary-only, {kill_stats['neither_killed']} Neither.")
    lines.append("- RQ2 worker scaling: subject-level means (averaged over repeats), then mean/median over subjects.")
    lines.append("- RQ3 tables auto-generated by build_rq3_paper_tables_dataset.py.")

    preview = OUTPUT / "paper_tables_preview.md"
    preview.write_text("\n".join(lines) + "\n")
    print(f"Preview written to {preview}")


# ============================================================================
# Main
# ============================================================================

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    print("=== RQ1: Bounded Completion ===")
    rq1_rows_raw = load_rq1_subjects()
    print(f"  CSC-only subjects: {len(rq1_rows_raw['CSC-only'])}")
    print(f"  CSC+Boundary subjects: {len(rq1_rows_raw['CSC+Boundary'])}")
    rq1_rows = build_rq1_table(rq1_rows_raw)
    for r in rq1_rows:
        print(f"  {r['structural_class']} {r['configuration']}: n={r['n']}, tests={r['test_cases']}, nodes={r['cct_nodes']}")

    print("\n=== RQ1 Kill: Mutant Killing ===")
    kill_stats = build_kill_tables()
    print(f"  Total: {kill_stats['total_mutants']} mutants")
    print(f"  CSC-only: {kill_stats['csc_only_killed']}, Boundary: {kill_stats['boundary_killed']}")
    print(f"  Boundary-only: {kill_stats['boundary_only']}, Both: {kill_stats['both_killed']}, Neither: {kill_stats['neither_killed']}")

    print("\n=== RQ2: Worker Scaling ===")
    subj_means, agg_counts, all_summaries = load_rq2_subject_means()
    for w in [1, 2, 4, 8]:
        print(f"  W={w}: {len(subj_means[w])} subjects, tests={agg_counts[w]['testcases']}, nodes={agg_counts[w]['cct_nodes']}")
    rq2_rows = build_rq2_table(subj_means, agg_counts, all_summaries)
    for r in rq2_rows:
        print(f"  W={r['workers']}: time={r['mean_time_s']}s/{r['median_time_s']}s, S={r['mean_speedup']}/{r['median_speedup']}")

    print("\n=== Markdown Preview ===")
    write_preview(rq1_rows, rq2_rows, kill_stats)

    # Update metadata
    metadata_path = OUTPUT / "metadata.json"
    metadata = json.loads(metadata_path.read_text())
    metadata["sources"]["rq1"] = [
        "experiments/EX_CSC_dataset/rq1_bounded_completion/rq1_summary.md",
        "experiments/EX_CSC_dataset/rq_extension_a/RQ1-boundary/rq1_comparison.json",
        "experiments/EX_CSC_dataset/rq_extension_b/RQ1-boundary/rq1_comparison.json",
        "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ1-boundary/rq1_comparison.json",
    ]
    metadata["sources"]["rq2"] = [
        "experiments/EX_CSC_dataset/rq2_parallel_generation/parallel_generation_runs.jsonl",
        "experiments/EX_CSC_dataset/rq_extension_a/RQ2-parallel/parallel_generation_runs.jsonl",
        "experiments/EX_CSC_dataset/rq_extension_b/RQ2-parallel/parallel_generation_runs.jsonl",
        "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ2-parallel/parallel_generation_runs.jsonl",
    ]
    metadata["sources"]["rq1_kill"] = [
        "experiments/EX_CSC_dataset/boundary_kill_core/aggregate_ready/tbfv_boundary_kill_rows.jsonl",
        "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ1-kill-mutant/aggregate_ready/tbfv_boundary_kill_rows.jsonl",
    ]
    metadata["rq1_note"] = "Unified EX_CSC_dataset RQ1 rows are pooled from rq1_summary.md and rq1_comparison.json per_subject_comparison."
    metadata["rq2_note"] = "Subject-level means averaged over repeats, then mean/median over all subjects."
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")

    print("\nDone. All tables written to experiments/EX_CSC_dataset/paper_tables/")


if __name__ == "__main__":
    main()
