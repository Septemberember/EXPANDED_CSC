#!/usr/bin/env python3
"""Build the paper-facing RQ3 tables from coverage_x_purity artifacts."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "experiments" / "EX_CSC_dataset" / "paper_tables"
BUDGET_ROWS = [
    ROOT / "experiments/EX_CSC_dataset/folded_fault_localization/budget_matched_coverage_x_purity/multi-sfl/multi_sfl_budget_rows.csv",
    ROOT / "experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/folded-budget-matched-coverage-x-purity/multi-sfl/multi_sfl_budget_rows.csv",
    ROOT / "experiments/EX_CSC_dataset/rq_extension_b/FL/folded-budget-matched-coverage-x-purity/multi-sfl/multi_sfl_budget_rows.csv",
    ROOT / "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ3-fault-localization/folded-budget-matched-coverage-x-purity/multi-sfl/multi_sfl_budget_rows.csv",
]
REPLAY_ROWS = [
    ROOT / "experiments/EX_CSC_dataset/folded_fault_localization/fl_combined_3exp_144tasks/folded_replay_rows.csv",
    ROOT / "experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/folded-replay-v2/folded_replay_rows.csv",
    ROOT / "experiments/EX_CSC_dataset/rq_extension_b/FL/folded-replay-coverage-x-purity/folded_replay_rows.csv",
    ROOT / "experiments/EX_CSC_dataset/boundary_stress_subjects/RQ3-fault-localization/folded-replay-coverage-x-purity/folded_replay_rows.csv",
]
FORMULAS = ("op2", "dstar", "ochiai", "tarantula", "barinel")
TOP_K = (1, 2, 3)


def read_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def is_true(value: object) -> bool:
    return str(value).lower() == "true"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def exact_mcnemar(fold_only: int, baseline_only: int) -> float:
    discordant = fold_only + baseline_only
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, i) for i in range(min(fold_only, baseline_only) + 1))
    return min(1.0, 2.0 * tail / (2**discordant))


def build_budget_tables(rows: list[dict[str, str]]) -> None:
    evaluated = [row for row in rows if row.get("status") == "evaluated"]
    strategies = {row.get("scoring_strategy") for row in evaluated}
    if strategies != {"coverage_x_purity"}:
        raise ValueError(f"Unexpected scoring strategies: {sorted(strategies)}")

    all_rows: list[dict] = []
    for category in ("overall", "condition", "statement"):
        group = evaluated if category == "overall" else [
            row for row in evaluated if row.get("fault_category") == category
        ]
        for top_k in TOP_K:
            record: dict[str, object] = {
                "fault_category": category,
                "cases": len(group),
                "top_k": top_k,
                "mean_budget": round(mean(int(row[f"top{top_k}_budget"]) for row in group), 2),
                "folded_hits": sum(is_true(row[f"top{top_k}_folded_hit"]) for row in group),
            }
            record["folded_rate_pct"] = round(100 * int(record["folded_hits"]) / len(group), 1)
            for formula in FORMULAS:
                hits = sum(is_true(row[f"top{top_k}_{formula}_hit"]) for row in group)
                record[f"{formula}_hits"] = hits
                record[f"{formula}_rate_pct"] = round(100 * hits / len(group), 1)
            all_rows.append(record)

    fields = ["fault_category", "cases", "top_k", "mean_budget", "folded_hits", "folded_rate_pct"]
    fields.extend(item for formula in FORMULAS for item in (f"{formula}_hits", f"{formula}_rate_pct"))
    write_csv(OUTPUT / "rq3_budget_matched_all_baselines.csv", fields, all_rows)

    overall = [row for row in all_rows if row["fault_category"] == "overall"]
    main_rows = []
    for row in overall:
        cases = int(row["cases"])
        main = {"top_k": row["top_k"], "mean_budget": round(float(row["mean_budget"]), 1)}
        main["folded_composite"] = f"{row['folded_hits']}/{cases} ({row['folded_rate_pct']:.1f}%)"
        for formula in ("op2", "dstar", "ochiai"):
            main[f"sbfl_{formula}"] = (
                f"{row[f'{formula}_hits']}/{cases} ({row[f'{formula}_rate_pct']:.1f}%)"
            )
        main_rows.append(main)
    write_csv(
        OUTPUT / "rq3_budget_matched_main_table.csv",
        ["top_k", "mean_budget", "folded_composite", "sbfl_op2", "sbfl_dstar", "sbfl_ochiai"],
        main_rows,
    )

    misses = [row for row in evaluated if not is_true(row["top3_folded_hit"])]
    miss_counts = Counter(row["operator"] for row in misses)
    write_csv(
        OUTPUT / "rq3_top3_misses_by_operator.csv",
        ["operator", "top3_misses"],
        [{"operator": operator, "top3_misses": count} for operator, count in miss_counts.most_common()],
    )

    paired_rows = []
    for top_k in TOP_K:
        for formula in FORMULAS:
            fold_only = sum(
                is_true(row[f"top{top_k}_folded_hit"]) and not is_true(row[f"top{top_k}_{formula}_hit"])
                for row in evaluated
            )
            baseline_only = sum(
                not is_true(row[f"top{top_k}_folded_hit"]) and is_true(row[f"top{top_k}_{formula}_hit"])
                for row in evaluated
            )
            paired_rows.append({
                "top_k": top_k,
                "baseline": formula,
                "folded_only_hits": fold_only,
                "baseline_only_hits": baseline_only,
                "exact_mcnemar_p": round(exact_mcnemar(fold_only, baseline_only), 6),
            })
    write_csv(
        OUTPUT / "rq3_paired_comparison.csv",
        ["top_k", "baseline", "folded_only_hits", "baseline_only_hits", "exact_mcnemar_p"],
        paired_rows,
    )


def build_view_decomposition(rows: list[dict[str, str]]) -> None:
    evaluated = [row for row in rows if row.get("status") == "evaluated"]
    output_rows = []
    for category, label, hit_field, rank_field in (
        ("condition", "Condition faults (condition candidates)", "condition_node_hit", "condition_node_best_rank"),
        ("statement", "State-update faults (edge-partition candidates)", "interval_folded_edge_partition_hit", "interval_folded_edge_partition_best_rank"),
    ):
        group = [row for row in evaluated if row.get("fault_category") == category]
        record = {
            "target_class_folded_view": label,
            "evaluated": len(group),
            "any_rank_hit": f"{sum(is_true(row[hit_field]) for row in group)}/{len(group)}",
        }
        for k in TOP_K:
            hits = sum(
                bool(row.get(rank_field)) and int(row[rank_field]) <= k
                for row in group
            )
            record[f"top{k}"] = f"{hits}/{len(group)} ({100 * hits / len(group):.1f}%)"
        any_hits = sum(is_true(row[hit_field]) for row in group)
        record["any_rank_hit"] += f" ({100 * any_hits / len(group):.1f}%)"
        output_rows.append(record)
    write_csv(
        OUTPUT / "rq3_folded_view_decomposition.csv",
        ["target_class_folded_view", "evaluated", "any_rank_hit", "top1", "top2", "top3"],
        output_rows,
    )


def update_metadata() -> None:
    path = OUTPUT / "metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["rq3_note"] = (
        "Budget-matched and diagnostic-decomposition tables are rebuilt from "
        "coverage_x_purity artifacts for EX_CSC_dataset."
    )
    metadata["sources"]["rq3"] = [str(path.relative_to(ROOT)) for path in BUDGET_ROWS + REPLAY_ROWS]
    path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_budget_tables(read_rows(BUDGET_ROWS))
    build_view_decomposition(read_rows(REPLAY_ROWS))
    update_metadata()
    print(f"RQ3 paper tables written to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
