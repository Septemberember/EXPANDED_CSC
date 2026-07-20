#!/usr/bin/env python3
"""Inspection-budget-matched comparison between CCT localization and SFL.

For each mutant and each CCT Top-r prefix, this script computes the number of
unique source lines covered by the CCT predictions and gives SFL the same line
inspection budget. The resulting hit rates compare the two methods under the
same source-line budget instead of the same ranking depth.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Callable, Iterable

from csc_engine.failure_localization_eval import (
    AGGREGATED_COMPOSITE_STRATEGY,
    AGGREGATED_CONDITION_STRATEGY,
    AGGREGATED_EDGE_DIVERGENCE_GATED_STRATEGY,
    AGGREGATED_EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_STRATEGY,
    AGGREGATED_EDGE_DIVERGENCE_SIBLING_SHARED_STRATEGY,
    AGGREGATED_INTERVAL_PREFIX,
    LocalizationPrediction,
    extract_aggregated_predictions,
    load_json_report,
)


AGGREGATED_SEED_COMPOSITE_STRATEGY = "aggregated.composite.condition_or_seed_interval"
AGGREGATED_SEED_SHARED_COMPOSITE_STRATEGY = "aggregated.composite.condition_or_seed_shared_interval"
AGGREGATED_SEED_PARTITIONED_COMPOSITE_STRATEGY = "aggregated.composite.condition_or_seed_partitioned_interval"
AGGREGATED_PARTITIONED_EDGE_REGION_STRATEGY = "aggregated.interval.partitioned_edge_region"
AGGREGATED_CONDITION_OR_PARTITIONED_EDGE_REGION_STRATEGY = (
    "aggregated.composite.condition_or_partitioned_edge_region"
)

DEFAULT_CCT_STRATEGIES = [
    AGGREGATED_COMPOSITE_STRATEGY,
    AGGREGATED_CONDITION_OR_PARTITIONED_EDGE_REGION_STRATEGY,
    AGGREGATED_SEED_PARTITIONED_COMPOSITE_STRATEGY,
]
DEFAULT_SFL_FORMULAS = ["ochiai"]
DEFAULT_TOP_R = [1, 2, 3]

_DEPRECATED_CCT_STRATEGIES: frozenset[str] = frozenset({
    AGGREGATED_SEED_COMPOSITE_STRATEGY,
    AGGREGATED_SEED_SHARED_COMPOSITE_STRATEGY,
    AGGREGATED_PARTITIONED_EDGE_REGION_STRATEGY,
    AGGREGATED_CONDITION_STRATEGY,
    AGGREGATED_EDGE_DIVERGENCE_GATED_STRATEGY,
    AGGREGATED_EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_STRATEGY,
    AGGREGATED_EDGE_DIVERGENCE_SIBLING_SHARED_STRATEGY,
    f"{AGGREGATED_INTERVAL_PREFIX}statement_presence",
})


@dataclass(frozen=True)
class ExperimentRef:
    experiment_id: str
    dataset_id: str
    root: Path
    aggregation_ready: Path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    combined_root = args.combined_root.resolve()
    output_dir = args.output_dir or (combined_root / "budget_matched_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    replay_roots = [root.resolve() for root in (args.replay_root or [])]

    experiments = load_experiments(combined_root / "combined_experiment_metadata.json", combined_root)
    cct_strategies = parse_csv_list(args.cct_strategies, DEFAULT_CCT_STRATEGIES)
    sfl_formulas = parse_csv_list(args.sfl_formulas, DEFAULT_SFL_FORMULAS)
    top_r = parse_int_list(args.top_r, DEFAULT_TOP_R)

    rows = []
    for experiment in experiments:
        rows.extend(analyze_experiment(experiment, cct_strategies, sfl_formulas, top_r, replay_roots))

    summary_rows = summarize(rows)
    write_jsonl(output_dir / "budget_matched_rows.jsonl", rows)
    write_csv(output_dir / "budget_matched_rows.csv", rows)
    write_csv(output_dir / "budget_matched_summary.csv", summary_rows)
    write_markdown(output_dir / "budget_matched_summary.md", summary_rows, combined_root, replay_roots, top_r)
    write_json(output_dir / "budget_matched_metadata.json", {
        "combined_root": str(combined_root),
        "replay_roots": [str(root) for root in replay_roots],
        "experiments": [experiment.__dict__ | {
            "root": str(experiment.root),
            "aggregation_ready": str(experiment.aggregation_ready),
        } for experiment in experiments],
        "cct_strategies": [s for s in cct_strategies if s not in _DEPRECATED_CCT_STRATEGIES],
        "sfl_formulas": sfl_formulas,
        "top_r": top_r,
        "row_count": len(rows),
    })

    print(f"Budget-matched analysis complete: {output_dir}")
    print(f"  Rows: {len(rows)}")
    print(f"  Summary rows: {len(summary_rows)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute inspection-budget-matched CCT-vs-SFL hit rates."
    )
    parser.add_argument(
        "--combined-root",
        required=True,
        type=Path,
        help="Combined experiment directory, e.g. experiments/EX_CSC_dataset/fault_localization_combined.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory. Defaults to <combined-root>/budget_matched_analysis.",
    )
    parser.add_argument(
        "--top-r",
        default=",".join(str(v) for v in DEFAULT_TOP_R),
        help="CSC ranking depths, e.g. 1,2,3.",
    )
    parser.add_argument(
        "--cct-strategies",
        default=",".join(DEFAULT_CCT_STRATEGIES),
        help="Comma-separated CCT strategies to analyze.",
    )
    parser.add_argument(
        "--sfl-formulas",
        default=",".join(DEFAULT_SFL_FORMULAS),
        help="Comma-separated SFL formulas to compare against.",
    )
    parser.add_argument(
        "--replay-root",
        action="append",
        type=Path,
        help=(
            "Optional replay analysis directory, e.g. "
            "<combined-root>/seed_replay_analysis. Repeat to merge multiple "
            "replayed aggregated interval prediction sets into the CCT budget calculation."
        ),
    )
    return parser


def load_experiments(metadata_path: Path, combined_root: Path) -> list[ExperimentRef]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    project_root = combined_root.parents[1]
    experiments = []
    for item in metadata.get("experiments", []):
        experiments.append(ExperimentRef(
            experiment_id=str(item["experiment_id"]),
            dataset_id=str(item["dataset_id"]),
            root=resolve_path(project_root, item["root"]),
            aggregation_ready=resolve_path(project_root, item["aggregation_ready"]),
        ))
    return experiments


def resolve_path(project_root: Path, raw: str | Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else project_root / path


def analyze_experiment(experiment: ExperimentRef,
                       cct_strategies: list[str],
                       sfl_formulas: list[str],
                       top_r: list[int],
                       replay_roots: list[Path]) -> list[dict[str, Any]]:
    manifest = load_jsonl(experiment.aggregation_ready / "mutants_manifest.jsonl")
    rows = []
    for record in manifest:
        mutant_id = str(record.get("mutant_id") or "")
        cct_report_path = experiment.aggregation_ready / "cct_eval_reports" / mutant_id / "fault_localization_eval.json"
        if not cct_report_path.exists():
            continue
        cct_eval = load_json_report(cct_report_path)
        if not cct_eval.get("metrics"):
            continue

        report_paths = find_cct_report_paths(experiment.root, mutant_id)
        if report_paths is None:
            continue
        _, aggregated_report_path = report_paths
        if aggregated_report_path is None or not aggregated_report_path.exists():
            continue
        aggregated_report = load_json_report(aggregated_report_path)
        predictions = extract_aggregated_predictions(aggregated_report)
        for replay_report_path in find_replay_aggregated_reports(replay_roots, experiment.experiment_id, mutant_id):
            predictions.extend(extract_aggregated_predictions(load_json_report(replay_report_path)))

        sfl_report_path = experiment.root / "baseline-SFL-v2" / mutant_id / "sfl_localization.json"
        if not sfl_report_path.exists():
            sfl_report_path = experiment.root / "baseline-SFL" / mutant_id / "sfl_localization.json"
        if not sfl_report_path.exists():
            continue
        sfl_report = load_json_report(sfl_report_path)

        for cct_strategy in cct_strategies:
            for formula in sfl_formulas:
                rows.extend(analyze_strategy_pair(
                    experiment=experiment,
                    record=record,
                    cct_strategy=cct_strategy,
                    cct_predictions=predictions,
                    sfl_formula=formula,
                    sfl_report=sfl_report,
                    top_r=top_r,
                ))
    return rows


def analyze_strategy_pair(experiment: ExperimentRef,
                          record: dict[str, Any],
                          cct_strategy: str,
                          cct_predictions: list[LocalizationPrediction],
                          sfl_formula: str,
                          sfl_report: dict[str, Any],
                          top_r: list[int]) -> list[dict[str, Any]]:
    cct_line_fn = cct_line_set_fn(cct_strategy, cct_predictions)
    if cct_line_fn is None:
        return []
    sfl_ranked_lines = ranked_sfl_lines(sfl_report, sfl_formula)
    if not sfl_ranked_lines:
        return []

    rows = []
    for r in top_r:
        cct_lines = cct_line_fn(r)
        budget = len(cct_lines)
        sfl_lines = set(sfl_ranked_lines[:budget])
        rows.append({
            "experiment_id": experiment.experiment_id,
            "dataset_id": experiment.dataset_id,
            "mutant_id": record.get("mutant_id"),
            "subject": record.get("subject"),
            "operator": record.get("operator"),
            "fault_kind": record.get("fault_kind"),
            "fault_category": record.get("fault_category"),
            "cct_strategy": cct_strategy,
            "sfl_strategy": f"sfl.{sfl_formula}",
            "cct_top_r": r,
            "inspection_budget_lines": budget,
            "cct_hit": cct_lines_hit(cct_lines, record),
            "sfl_budget_hit": lines_hit_ground_truth(sfl_lines, record),
            "cct_lines": sorted(cct_lines),
            "sfl_budget_lines": sorted(sfl_lines),
            "primary_line": record.get("ground_truth", {}).get("primary_line"),
        })
    return rows


_warned_deprecated: set[str] = set()


def cct_line_set_fn(strategy: str,
                    predictions: list[LocalizationPrediction]) -> Callable[[int], set[int]] | None:
    if strategy in _DEPRECATED_CCT_STRATEGIES:
        if strategy not in _warned_deprecated:
            _warned_deprecated.add(strategy)
            print(f"[WARN] Deprecated strategy '{strategy}' — skipping.", file=sys.stderr)
        return None
    if strategy == AGGREGATED_COMPOSITE_STRATEGY:
        condition = predictions_for(predictions, AGGREGATED_CONDITION_STRATEGY)
        interval = predictions_for(predictions, AGGREGATED_EDGE_DIVERGENCE_GATED_STRATEGY)
        if not condition and not interval:
            return None

        def composite(rank: int) -> set[int]:
            return union_prediction_lines(condition[:rank] + interval[:rank])

        return composite

    if strategy == AGGREGATED_SEED_COMPOSITE_STRATEGY:
        condition = predictions_for(predictions, AGGREGATED_CONDITION_STRATEGY)
        interval = predictions_for(predictions, AGGREGATED_EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_STRATEGY)
        if not condition and not interval:
            return None

        def seed_composite(rank: int) -> set[int]:
            return union_prediction_lines(condition[:rank] + interval[:rank])

        return seed_composite

    if strategy == AGGREGATED_SEED_SHARED_COMPOSITE_STRATEGY:
        condition = predictions_for(predictions, AGGREGATED_CONDITION_STRATEGY)
        interval = predictions_for(predictions, AGGREGATED_EDGE_DIVERGENCE_SIBLING_SHARED_STRATEGY)
        if not condition and not interval:
            return None

        def shared_composite(rank: int) -> set[int]:
            return union_prediction_lines(condition[:rank] + interval[:rank])

        return shared_composite

    if strategy == AGGREGATED_SEED_PARTITIONED_COMPOSITE_STRATEGY:
        condition = predictions_for(predictions, AGGREGATED_CONDITION_STRATEGY)
        exclusive = predictions_for(predictions, AGGREGATED_EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_STRATEGY)
        shared = predictions_for(predictions, AGGREGATED_EDGE_DIVERGENCE_SIBLING_SHARED_STRATEGY)
        if not condition and not exclusive and not shared:
            return None

        def partitioned_composite(rank: int) -> set[int]:
            return union_prediction_lines(condition[:rank] + exclusive[:rank] + shared[:rank])

        return partitioned_composite

    if strategy == AGGREGATED_PARTITIONED_EDGE_REGION_STRATEGY:
        edge_region = partitioned_edge_region_predictions(predictions)
        if not edge_region:
            return None

        def partitioned_edge_region(rank: int) -> set[int]:
            return union_prediction_lines(edge_region[:rank])

        return partitioned_edge_region

    if strategy == AGGREGATED_CONDITION_OR_PARTITIONED_EDGE_REGION_STRATEGY:
        condition = predictions_for(predictions, AGGREGATED_CONDITION_STRATEGY)
        edge_region = partitioned_edge_region_predictions(predictions)
        if not condition and not edge_region:
            return None

        def condition_or_partitioned_edge_region(rank: int) -> set[int]:
            return union_prediction_lines(condition[:rank] + edge_region[:rank])

        return condition_or_partitioned_edge_region

    items = predictions_for(predictions, strategy)
    if not items:
        return None

    def simple(rank: int) -> set[int]:
        return union_prediction_lines(items[:rank])

    return simple


def predictions_for(predictions: list[LocalizationPrediction],
                    strategy: str) -> list[LocalizationPrediction]:
    return sorted(
        [prediction for prediction in predictions if prediction.strategy == strategy],
        key=lambda prediction: prediction.rank,
    )


def partitioned_edge_region_predictions(predictions: list[LocalizationPrediction]) -> list[LocalizationPrediction]:
    """Return one unified ranking over exclusive and shared edge-region items."""

    exclusive = predictions_for(predictions, AGGREGATED_EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_STRATEGY)
    shared = predictions_for(predictions, AGGREGATED_EDGE_DIVERGENCE_SIBLING_SHARED_STRATEGY)
    non_empty = [
        prediction
        for prediction in exclusive + shared
        if prediction.predicted_lines
    ]
    return sorted(
        non_empty,
        key=lambda prediction: (
            -prediction.score,
            prediction.rank,
            prediction.strategy,
            tuple(prediction.predicted_lines),
        ),
    )


def union_prediction_lines(predictions: Iterable[LocalizationPrediction]) -> set[int]:
    return {
        line
        for prediction in predictions
        for line in prediction.predicted_lines
    }


def ranked_sfl_lines(sfl_report: dict[str, Any], formula: str) -> list[int]:
    rows = sorted(sfl_report.get("rankings", {}).get(formula, []), key=lambda item: int(item.get("rank", 0)))
    lines = []
    seen = set()
    for row in rows:
        line = row.get("line")
        if line is None:
            continue
        line = int(line)
        if line in seen:
            continue
        seen.add(line)
        lines.append(line)
    return lines


def cct_lines_hit(lines: set[int], record: dict[str, Any]) -> bool:
    return lines_hit_ground_truth(lines, record)


def lines_hit_ground_truth(lines: set[int], record: dict[str, Any]) -> bool:
    acceptable = acceptable_lines(record)
    if lines.intersection(acceptable):
        return True
    window = acceptable_window(record)
    if window is None:
        return False
    start, end = window
    return any(start <= line <= end for line in lines)


def acceptable_lines(record: dict[str, Any]) -> set[int]:
    ground_truth = record.get("ground_truth", {})
    lines = ground_truth.get("acceptable_lines") or [ground_truth.get("primary_line")]
    return {int(line) for line in lines if line is not None}


def acceptable_window(record: dict[str, Any]) -> tuple[int, int] | None:
    window = record.get("ground_truth", {}).get("acceptable_line_window")
    if not window:
        return None
    start = window.get("start")
    end = window.get("end")
    if start is None or end is None:
        return None
    return min(int(start), int(end)), max(int(start), int(end))


def find_cct_report_paths(root: Path, mutant_id: str) -> tuple[Path | None, Path | None] | None:
    candidate_dirs = sorted({
        path.parent
        for path in root.glob("**/cct_failure_localization.json")
        if path.is_file() and path_belongs_to_mutant(path, mutant_id)
    })
    if not candidate_dirs:
        return None
    selected = max(candidate_dirs, key=lambda path: (len(path.parts), str(path)))
    raw = selected / "cct_failure_localization.json"
    aggregated = selected / "cct_failure_localization_aggregated.json"
    return raw if raw.exists() else None, aggregated if aggregated.exists() else None


def find_replay_aggregated_reports(replay_roots: list[Path],
                                   experiment_id: str,
                                   mutant_id: str) -> list[Path]:
    paths = []
    for replay_root in replay_roots:
        path = (
            replay_root
            / "artifacts"
            / experiment_id
            / mutant_id
            / "cct_failure_localization_replay_aggregated.json"
        )
        if path.exists():
            paths.append(path)
    return paths


def path_belongs_to_mutant(path: Path, mutant_id: str) -> bool:
    return any(part == mutant_id or part.endswith(f"_{mutant_id}") for part in path.parts)


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, int], list[dict[str, Any]]] = {}
    for row in rows:
        for category in ("overall", str(row.get("fault_category") or "<missing>")):
            key = (
                category,
                str(row["cct_strategy"]),
                str(row["sfl_strategy"]),
                int(row["cct_top_r"]),
            )
            groups.setdefault(key, []).append(row)

    summary_rows = []
    for (category, cct_strategy, sfl_strategy, r), items in sorted(groups.items()):
        budgets = [int(item["inspection_budget_lines"]) for item in items]
        cct_hits = sum(1 for item in items if item["cct_hit"])
        sfl_hits = sum(1 for item in items if item["sfl_budget_hit"])
        summary_rows.append({
            "fault_category": category,
            "cct_strategy": cct_strategy,
            "sfl_strategy": sfl_strategy,
            "cct_top_r": r,
            "cases": len(items),
            "mean_budget_lines": mean(budgets),
            "median_budget_lines": median(budgets) if budgets else None,
            "max_budget_lines": max(budgets) if budgets else None,
            "cct_hit_count": cct_hits,
            "cct_hit_rate": rate(cct_hits, len(items)),
            "sfl_budget_hit_count": sfl_hits,
            "sfl_budget_hit_rate": rate(sfl_hits, len(items)),
            "cct_minus_sfl_hit_rate": rate(cct_hits, len(items)) - rate(sfl_hits, len(items)),
        })
    return summary_rows


def write_markdown(output_path: Path,
                   summary_rows: list[dict[str, Any]],
                   combined_root: Path,
                   replay_roots: list[Path],
                   top_r: list[int]) -> None:
    lines = [
        "# Budget-Matched Fault Localization Summary",
        "",
        f"- Combined experiment: `{combined_root}`",
        "- Replay predictions: "
        + (", ".join(f"`{root}`" for root in replay_roots) if replay_roots else "`<not used>`"),
        f"- CSC Top-r values: {', '.join(str(v) for v in top_r)}",
        "- Definition: for each mutant and CSC Top-r, SFL receives the same number of unique source lines as the CSC Top-r region.",
        "",
    ]
    for category in ["overall", "condition", "statement"]:
        category_rows = [row for row in summary_rows if row["fault_category"] == category]
        if not category_rows:
            continue
        lines.extend([
            f"## {category}",
            "",
            "| CSC Strategy | SFL Strategy | CSC Top-r | Cases | Mean Budget Lines | CSC Hit Rate | SFL Budget Hit Rate | Delta |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for row in category_rows:
            lines.append(
                "| {cct_strategy} | {sfl_strategy} | {cct_top_r} | {cases} | {mean_budget_lines:.3f} | {cct_hit_rate:.3f} | {sfl_budget_hit_rate:.3f} | {cct_minus_sfl_hit_rate:.3f} |".format(**row)
            )
        lines.append("")
    active_strategies = sorted({row["cct_strategy"] for row in summary_rows})
    if active_strategies:
        lines.append("## Active CCT Strategies")
        lines.append("")
        for s in active_strategies:
            lines.append(f"- `{s}`")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field)) for field in fields})


def csv_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True)
    return value


def parse_csv_list(raw: str, default: list[str]) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or list(default)


def parse_int_list(raw: str, default: list[int]) -> list[int]:
    values = sorted({int(item.strip()) for item in raw.split(",") if item.strip() and int(item.strip()) > 0})
    return values or list(default)


def mean(values: list[int]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def rate(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return count / total


if __name__ == "__main__":
    raise SystemExit(main())
