"""Source-level aggregation for CCT failure-localization reports.

Raw failure-localization reports rank dynamic CCT nodes and edges. This module
keeps that report intact and builds a source-level post-processing view that is
better suited for fault-localization evaluation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from .failure_localization import (
    INTERVAL_STRATEGY_REGISTRY,
    RankingSlot,
)


AGGREGATION_STRATEGY = "source_transition_v1"
DEFAULT_SCORE_AGGREGATION = "max"
CONDITION_NODE_TARGET = "condition_node_ranking"
INTERVAL_TARGET_PREFIX = "interval_rankings."


# ---------------------------------------------------------------------------
# Aggregation strategy registry — pluggable aggregation strategies.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AggregationStrategy:
    """Descriptor for one source-level aggregation strategy.

    Each strategy defines how raw CCT node/edge records are aggregated into
    source-level rankings: how numerical fields are combined from a group,
    and how aggregated records are sorted.
    """

    name: str
    description: str
    aggregate_condition_fields: Callable[[list[dict[str, Any]], dict[str, Any]], dict[str, Any]]
    aggregate_interval_fields: Callable[[list[dict[str, Any]], dict[str, Any]], dict[str, Any]]
    sort_key: Callable[[dict[str, Any]], tuple]


def _aggregate_condition_fields_max(
    group: list[dict[str, Any]], best: dict[str, Any]
) -> dict[str, Any]:
    """Aggregate condition node fields using max (current default)."""
    return {
        "risk_score": float(best.get("risk_score", 0.0)),
        "exec_count": max(int(r.get("exec_count", 0)) for r in group),
        "fail_count": max(int(r.get("fail_count", 0)) for r in group),
        "pass_count": max(int(r.get("pass_count", 0)) for r in group),
        "failure_density": max(float(r.get("failure_density", 0.0)) for r in group),
        "min_exec_count": min(int(r.get("exec_count", 0)) for r in group),
        "min_fail_count": min(int(r.get("fail_count", 0)) for r in group),
        "min_pass_count": min(int(r.get("pass_count", 0)) for r in group),
        "min_failure_density": min(float(r.get("failure_density", 0.0)) for r in group),
    }


def _aggregate_interval_fields_max(
    group: list[dict[str, Any]], best: dict[str, Any]
) -> dict[str, Any]:
    """Aggregate interval record fields using max (current default)."""
    return {
        "risk_score": float(best.get("risk_score", 0.0)),
        "base_risk_score": float(best.get("base_risk_score", best.get("risk_score", 0.0))),
        "exec_count": max(int(r.get("exec_count", 0)) for r in group),
        "fail_count": max(int(r.get("fail_count", 0)) for r in group),
        "pass_count": max(int(r.get("pass_count", 0)) for r in group),
        "failure_density": max(float(r.get("failure_density", 0.0)) for r in group),
        "min_exec_count": min(int(r.get("exec_count", 0)) for r in group),
        "min_fail_count": min(int(r.get("fail_count", 0)) for r in group),
        "min_pass_count": min(int(r.get("pass_count", 0)) for r in group),
        "min_failure_density": min(float(r.get("failure_density", 0.0)) for r in group),
    }


def _aggregate_condition_fields_sum(
    group: list[dict[str, Any]], best: dict[str, Any]
) -> dict[str, Any]:
    """Aggregate condition node fields using sum across the group."""
    exec_sum = sum(int(r.get("exec_count", 0)) for r in group)
    fail_sum = sum(int(r.get("fail_count", 0)) for r in group)
    pass_sum = sum(int(r.get("pass_count", 0)) for r in group)
    return {
        "risk_score": sum(float(r.get("risk_score", 0.0)) for r in group),
        "exec_count": exec_sum,
        "fail_count": fail_sum,
        "pass_count": pass_sum,
        "failure_density": (fail_sum / exec_sum) if exec_sum > 0 else 0.0,
        "min_exec_count": min(int(r.get("exec_count", 0)) for r in group),
        "min_fail_count": min(int(r.get("fail_count", 0)) for r in group),
        "min_pass_count": min(int(r.get("pass_count", 0)) for r in group),
        "min_failure_density": min(float(r.get("failure_density", 0.0)) for r in group),
    }


def _aggregate_interval_fields_sum(
    group: list[dict[str, Any]], best: dict[str, Any]
) -> dict[str, Any]:
    """Aggregate interval record fields using sum across the group."""
    exec_sum = sum(int(r.get("exec_count", 0)) for r in group)
    fail_sum = sum(int(r.get("fail_count", 0)) for r in group)
    pass_sum = sum(int(r.get("pass_count", 0)) for r in group)
    base_score_sum = sum(float(r.get("base_risk_score", r.get("risk_score", 0.0))) for r in group)
    return {
        "risk_score": sum(float(r.get("risk_score", 0.0)) for r in group),
        "base_risk_score": base_score_sum,
        "exec_count": exec_sum,
        "fail_count": fail_sum,
        "pass_count": pass_sum,
        "failure_density": (fail_sum / exec_sum) if exec_sum > 0 else 0.0,
        "min_exec_count": min(int(r.get("exec_count", 0)) for r in group),
        "min_fail_count": min(int(r.get("fail_count", 0)) for r in group),
        "min_pass_count": min(int(r.get("pass_count", 0)) for r in group),
        "min_failure_density": min(float(r.get("failure_density", 0.0)) for r in group),
    }


def _default_aggregated_sort_key(record: dict[str, Any]) -> tuple:
    """Sort key for aggregated records.

    Tiebreakers after risk_score (descending):
    1. pass_count ascending — fewer passes = more suspicious
    2. support_count descending
    3. best_raw_rank ascending
    4. interval_width ascending
    5. line_start ascending
    """
    interval = record.get("normalized_anchor_span")
    interval_width = (
        interval[1] - interval[0] + 1
        if interval and len(interval) == 2
        else 10**9
    )
    line_start = (
        record.get("line")
        if record.get("line") is not None
        else (interval[0] if interval else 10**9)
    )
    best_raw_rank = record.get("best_raw_rank")
    if best_raw_rank is None:
        best_raw_rank = 10**9
    return (
        -float(record.get("risk_score", 0.0)),
        int(record.get("pass_count", 0)),
        -int(record.get("support_count", 0)),
        int(best_raw_rank),
        int(interval_width),
        int(line_start),
    )


AGGREGATION_STRATEGY_REGISTRY: dict[str, AggregationStrategy] = {
    "max": AggregationStrategy(
        name="max",
        description=(
            "Risk score from best raw record; numerical fields (exec/fail/pass/"
            "failure_density) use max across the group. Extra min_* fields record "
            "the minimum of each field for dispersion visibility."
        ),
        aggregate_condition_fields=_aggregate_condition_fields_max,
        aggregate_interval_fields=_aggregate_interval_fields_max,
        sort_key=_default_aggregated_sort_key,
    ),
    "sum": AggregationStrategy(
        name="sum",
        description=(
            "Risk score and numerical fields (exec/fail/pass) use sum across "
            "the group. failure_density is recomputed as fail_sum / exec_sum. "
            "Extra min_* fields record the minimum of each field."
        ),
        aggregate_condition_fields=_aggregate_condition_fields_sum,
        aggregate_interval_fields=_aggregate_interval_fields_sum,
        sort_key=_default_aggregated_sort_key,
    ),
}

DEFAULT_AGGREGATION_STRATEGY = "max"
FOLDED_STATEMENT_INTERVAL_STRATEGIES = frozenset({
    "folded_seed_e",
    "folded_seed_s",
    "folded_edge_partition",
})


def _is_statement_aware_strategy(strategy: str) -> bool:
    """Return True if *strategy* groups records by statement lines."""
    if strategy in FOLDED_STATEMENT_INTERVAL_STRATEGIES:
        return True
    entry = INTERVAL_STRATEGY_REGISTRY.get(strategy)
    return entry is not None and entry.slot != RankingSlot.ANCHOR


def load_localization_report(path: str | Path) -> dict[str, Any]:
    """Load a failure-localization report JSON file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_aggregated_localization_report(report: dict[str, Any],
                                         output_path: str | Path) -> None:
    """Write an aggregated failure-localization report as JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _resolve_aggregation_strategy(
    target_key: str,
    score_aggregation: str | dict[str, str],
) -> AggregationStrategy:
    """Resolve the aggregation strategy for a specific target.

    When *score_aggregation* is a string the same strategy is used for all
    targets.  When it is a dict each target key can select its own strategy;
    targets not listed in the dict fall back to
    :data:`DEFAULT_AGGREGATION_STRATEGY`.
    """
    if isinstance(score_aggregation, str):
        strategy_name = score_aggregation
    elif isinstance(score_aggregation, dict):
        strategy_name = score_aggregation.get(target_key, DEFAULT_AGGREGATION_STRATEGY)
    else:
        raise TypeError(
            f"score_aggregation must be str or dict, got {type(score_aggregation).__name__}"
        )

    strategy = AGGREGATION_STRATEGY_REGISTRY.get(strategy_name)
    if strategy is None:
        raise ValueError(
            f"Unsupported score aggregation: {strategy_name}. "
            f"Available: {list(AGGREGATION_STRATEGY_REGISTRY.keys())}"
        )
    return strategy


def aggregate_localization_report(
    report: dict[str, Any],
    source_file: Optional[str] = None,
    targets: Optional[list[str]] = None,
    score_aggregation: str | dict[str, str] = DEFAULT_SCORE_AGGREGATION,
    source_report: Optional[str] = None,
) -> dict[str, Any]:
    """Aggregate dynamic CCT localization rankings into source-level rankings.

    *score_aggregation* can be a single strategy name (applied to all targets)
    or a dict mapping target keys to strategy names for per-target control::

        # Same strategy for all
        aggregate_localization_report(report, score_aggregation="max")

        # Per-target strategies
        aggregate_localization_report(report, score_aggregation={
            "condition_node_ranking": "max",
            "interval_rankings.edge_divergence_sibling_exclusive": "sum",
        })
    """

    resolved_targets = _resolve_targets(report, targets)
    aggregate_condition_nodes = CONDITION_NODE_TARGET in resolved_targets
    interval_targets = [
        target.removeprefix(INTERVAL_TARGET_PREFIX)
        for target in resolved_targets
        if target.startswith(INTERVAL_TARGET_PREFIX)
    ]

    condition_records = (
        _aggregate_condition_nodes(
            report.get("condition_node_ranking", []),
            source_file=source_file,
            strategy=_resolve_aggregation_strategy(CONDITION_NODE_TARGET, score_aggregation),
        )
        if aggregate_condition_nodes
        else []
    )

    interval_rankings = {}
    for interval_strategy_name in interval_targets:
        target_key = f"{INTERVAL_TARGET_PREFIX}{interval_strategy_name}"
        raw_records = report.get("interval_rankings", {}).get(interval_strategy_name, [])
        interval_rankings[interval_strategy_name] = _aggregate_interval_records(
            raw_records,
            interval_strategy_name=interval_strategy_name,
            source_file=source_file,
            agg_strategy=_resolve_aggregation_strategy(target_key, score_aggregation),
        )

    raw_interval_counts = {
        strategy: len(report.get("interval_rankings", {}).get(strategy, []))
        for strategy in interval_targets
    }
    aggregated_interval_counts = {
        strategy: len(records)
        for strategy, records in interval_rankings.items()
    }
    average_region_sizes = {
        strategy: _average_region_size(records)
        for strategy, records in interval_rankings.items()
    }

    per_target_strategies = {
        CONDITION_NODE_TARGET: _resolve_aggregation_strategy(
            CONDITION_NODE_TARGET, score_aggregation
        ).name,
    }
    for interval_strategy_name in interval_targets:
        target_key = f"{INTERVAL_TARGET_PREFIX}{interval_strategy_name}"
        per_target_strategies[target_key] = _resolve_aggregation_strategy(
            target_key, score_aggregation
        ).name

    return {
        "summary": {
            "aggregation": AGGREGATION_STRATEGY,
            "score_aggregation": score_aggregation,
            "per_target_aggregation": per_target_strategies,
            "source_report": source_report,
            "source_file": source_file,
            "targets": resolved_targets,
            "condition_node_count_raw": len(report.get("condition_node_ranking", [])),
            "condition_node_count_aggregated": len(condition_records),
            "interval_count_raw": raw_interval_counts,
            "interval_count_aggregated": aggregated_interval_counts,
            "average_interval_region_size": average_region_sizes,
            "raw_summary": report.get("summary", {}),
        },
        "aggregated_condition_node_ranking": condition_records,
        "aggregated_interval_rankings": interval_rankings,
    }


def _resolve_targets(report: dict[str, Any],
                     targets: Optional[list[str]]) -> list[str]:
    if targets is None:
        resolved = [CONDITION_NODE_TARGET]
        resolved.extend(
            f"{INTERVAL_TARGET_PREFIX}{strategy}"
            for strategy in report.get("interval_rankings", {})
        )
        return resolved

    available = {CONDITION_NODE_TARGET}
    available.update(
        f"{INTERVAL_TARGET_PREFIX}{strategy}"
        for strategy in report.get("interval_rankings", {})
    )
    unknown = [target for target in targets if target not in available]
    if unknown:
        raise ValueError(f"Unknown aggregation targets: {', '.join(unknown)}")
    return _dedupe(targets)


def _aggregate_condition_nodes(records: list[dict[str, Any]],
                               source_file: Optional[str],
                               strategy: AggregationStrategy) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for record in records:
        key = (
            source_file,
            record.get("line"),
            record.get("condition"),
        )
        groups.setdefault(key, []).append(record)

    aggregated = []
    for (file_name, line, condition), group in groups.items():
        best = _best_record(group)
        entry = {
            "source_file": file_name,
            "line": line,
            "condition": condition,
            "location_basis": "condition_line",
            "support_count": len(group),
            "best_raw_rank": _best_raw_rank(group),
            "raw_ranks": _raw_ranks(group),
            "raw_node_ids": _raw_values(group, "node_id"),
            "representative": _representative(best),
        }
        entry.update(strategy.aggregate_condition_fields(group, best))
        aggregated.append(entry)

    _rank_aggregated_records(aggregated, strategy.sort_key)
    return aggregated


def _aggregate_interval_records(records: list[dict[str, Any]],
                                interval_strategy_name: str,
                                source_file: Optional[str],
                                agg_strategy: AggregationStrategy) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for record in records:
        key = _interval_group_key(record, interval_strategy_name, source_file)
        groups.setdefault(key, []).append(record)

    aggregated = []
    for key, group in groups.items():
        best = _best_record(group)
        basis = _location_basis_for_strategy(interval_strategy_name, best)
        statement_lines = sorted({
            int(line)
            for record in group
            for line in record.get("statement_lines", [])
            if line is not None
        })
        statement_variants = _statement_line_variants(group)
        interval = _normalized_anchor_span(best)
        region_size = _aggregated_region_size(interval_strategy_name, statement_lines, interval)
        entry = {
            "source_file": key[0],
            "from_line": best.get("from_line"),
            "from_condition": best.get("from_condition"),
            "outcome": best.get("outcome"),
            "to_line": best.get("to_line"),
            "to_condition": best.get("to_condition"),
            "location_basis": basis,
            "statement_lines": statement_lines,
            "statement_line_count": len(statement_lines),
            "region_size": region_size,
            "statement_line_variants": statement_variants,
            "raw_statement_line_variants": _line_variants(group, "raw_statement_lines"),
            "sibling_statement_line_variants": _line_variants(group, "sibling_statement_lines"),
            "removed_shared_statement_line_variants": _line_variants(group, "removed_shared_statement_lines"),
            "exclusive_statement_line_variants": _line_variants(group, "exclusive_statement_lines"),
            "shared_statement_line_variants": _line_variants(group, "shared_statement_lines"),
            "condition_anchor_span": best.get("condition_anchor_span", best.get("line_interval")),
            "condition_anchor_kind": best.get("condition_anchor_kind", best.get("interval_kind")),
            "line_interval": best.get("line_interval"),
            "interval_kind": best.get("interval_kind"),
            "normalized_anchor_span": interval,
            "support_count": len(group),
            "best_raw_rank": _best_raw_rank(group),
            "raw_ranks": _raw_ranks(group),
            "raw_edge_ids": _raw_values(group, "edge_id"),
            "representative": _representative(best),
        }
        entry.update(agg_strategy.aggregate_interval_fields(group, best))
        aggregated.append(entry)

    _rank_aggregated_records(aggregated, agg_strategy.sort_key)
    return aggregated


def _interval_group_key(record: dict[str, Any],
                        strategy: str,
                        source_file: Optional[str]) -> tuple[Any, ...]:
    if _is_statement_aware_strategy(strategy):
        return (
            source_file,
            record.get("from_line"),
            record.get("from_condition"),
            record.get("outcome"),
            record.get("to_line"),
            record.get("to_condition"),
        )
    return (
        source_file,
        tuple(record.get("condition_anchor_span", record.get("line_interval", []))),
        record.get("condition_anchor_kind", record.get("interval_kind")),
        record.get("outcome"),
        record.get("from_condition"),
        record.get("to_condition"),
    )


def _location_basis_for_strategy(strategy: str, record: dict[str, Any]) -> str:
    if _is_statement_aware_strategy(strategy):
        return "statement_lines"
    return record.get("location_basis", "condition_anchor_span")


def _aggregated_region_size(strategy: str,
                            statement_lines: list[int],
                            anchor_span: Optional[list[int]]) -> int:
    if _is_statement_aware_strategy(strategy):
        return len(statement_lines)
    return _span_size(anchor_span)


def _average_region_size(records: list[dict[str, Any]]) -> float:
    if not records:
        return 0.0
    return sum(int(record.get("region_size", 0)) for record in records) / len(records)


def _best_record(records: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        records,
        key=lambda record: (
            float(record.get("risk_score", 0.0)),
            -int(record.get("rank", 10**9)),
        ),
    )


def _best_raw_rank(records: list[dict[str, Any]]) -> Optional[int]:
    ranks = [
        int(record["rank"])
        for record in records
        if record.get("rank") is not None
    ]
    return min(ranks) if ranks else None


def _raw_ranks(records: list[dict[str, Any]]) -> list[int]:
    return sorted({
        int(record["rank"])
        for record in records
        if record.get("rank") is not None
    })


def _raw_values(records: list[dict[str, Any]], field: str) -> list[Any]:
    values = []
    for record in records:
        value = record.get(field)
        if value is not None and value not in values:
            values.append(value)
    return values


def _statement_line_variants(records: list[dict[str, Any]]) -> list[list[int]]:
    return _line_variants(records, "statement_lines")


def _line_variants(records: list[dict[str, Any]], field: str) -> list[list[int]]:
    variants = []
    for record in records:
        lines = sorted({
            int(line)
            for line in record.get(field, [])
            if line is not None
        })
        if lines not in variants:
            variants.append(lines)
    return variants


def _normalized_anchor_span(record: dict[str, Any]) -> Optional[list[int]]:
    span = record.get("condition_anchor_span", record.get("line_interval"))
    if not span:
        return None
    start = span[0]
    end = span[1] if len(span) > 1 else span[0]
    if start is None and end is None:
        return None
    if start is None:
        start = end
    if end is None:
        end = start
    return [min(start, end), max(start, end)]


def _span_size(span: Optional[list[int]]) -> int:
    if not span or len(span) != 2:
        return 0
    start, end = span
    if start is None or end is None:
        return 0
    return abs(int(end) - int(start)) + 1


def _representative(record: dict[str, Any]) -> dict[str, Any]:
    fields = [
        "rank",
        "node_id",
        "edge_id",
        "risk_score",
        "base_risk_score",
        "from_line",
        "from_condition",
        "outcome",
        "to_line",
        "to_condition",
        "line",
        "condition",
        "statement_lines",
        "raw_statement_lines",
        "sibling_statement_lines",
        "exclusive_statement_lines",
        "shared_statement_lines",
        "removed_shared_statement_lines",
        "sibling_edge_id",
        "region_basis",
        "region_size",
        "location_basis",
    ]
    return {
        field: record[field]
        for field in fields
        if field in record
    }


def _rank_aggregated_records(records: list[dict[str, Any]],
                             sort_key: Callable[[dict[str, Any]], tuple]) -> None:
    records.sort(key=sort_key)
    for index, record in enumerate(records, start=1):
        record["rank"] = index


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
