"""Evaluation helpers for CCT-based failure-localization reports.

This module is intentionally read-only: it consumes a mutant manifest and
failure-localization reports, then computes Top-k hit metrics without touching
CSC, TBFV, or CCT artifacts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


DEFAULT_TOP_K = (1, 3, 5, 10)
RAW_CONDITION_STRATEGY = "raw.condition_node"
AGGREGATED_CONDITION_STRATEGY = "aggregated.condition_node"
RAW_INTERVAL_PREFIX = "raw.interval."
AGGREGATED_INTERVAL_PREFIX = "aggregated.interval."
AGGREGATED_EDGE_DIVERGENCE_GATED_STRATEGY = "aggregated.interval.edge_divergence_gated"
AGGREGATED_EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_STRATEGY = (
    "aggregated.interval.edge_divergence_sibling_exclusive"
)
AGGREGATED_EDGE_DIVERGENCE_SIBLING_SHARED_STRATEGY = (
    "aggregated.interval.edge_divergence_sibling_shared"
)
AGGREGATED_COMPOSITE_STRATEGY = "aggregated.composite.condition_or_interval"
FOLDED_STATEMENT_INTERVAL_STRATEGIES = frozenset({
    "folded_seed_e",
    "folded_seed_s",
    "folded_edge_partition",
})


@dataclass(frozen=True)
class LocalizationPrediction:
    """A normalized localization prediction from raw or aggregated reports."""

    target_type: str
    strategy: str
    rank: int
    score: float
    predicted_lines: tuple[int, ...]
    region_size: int
    source_file: Optional[str]
    location_basis: str
    raw: dict[str, Any]


def load_manifest(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSONL mutant manifest."""

    records = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            records.append(json.loads(stripped))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return records


def find_mutant_record(records: Iterable[dict[str, Any]],
                       mutant_id: str) -> dict[str, Any]:
    """Return the manifest record for a mutant id."""

    for record in records:
        if record.get("mutant_id") == mutant_id:
            return record
    raise ValueError(f"Mutant id not found in manifest: {mutant_id}")


def validate_mutant_record(record: dict[str, Any]) -> None:
    """Validate the minimal manifest fields required for evaluation."""

    required_top = ["mutant_id", "mutant_file", "ground_truth"]
    missing_top = [field for field in required_top if field not in record]
    if missing_top:
        raise ValueError(f"Manifest record missing required field(s): {', '.join(missing_top)}")

    ground_truth = record.get("ground_truth")
    if not isinstance(ground_truth, dict):
        raise ValueError("Manifest record ground_truth must be an object")

    if ground_truth.get("primary_line") is None:
        raise ValueError("Manifest ground_truth.primary_line is required")

    acceptable_lines = ground_truth.get("acceptable_lines")
    if acceptable_lines is None:
        ground_truth["acceptable_lines"] = [ground_truth["primary_line"]]
    elif not isinstance(acceptable_lines, list) or not acceptable_lines:
        raise ValueError("Manifest ground_truth.acceptable_lines must be a non-empty list")

    window = ground_truth.get("acceptable_line_window")
    if window is not None:
        if not isinstance(window, dict) or window.get("start") is None or window.get("end") is None:
            raise ValueError("Manifest ground_truth.acceptable_line_window requires start and end")


def load_json_report(path: str | Path) -> dict[str, Any]:
    """Load a JSON report."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def extract_raw_predictions(report: dict[str, Any]) -> list[LocalizationPrediction]:
    """Extract normalized predictions from a raw localization report."""

    predictions: list[LocalizationPrediction] = []
    predictions.extend(_extract_condition_predictions(
        report.get("condition_node_ranking", []),
        strategy=RAW_CONDITION_STRATEGY,
    ))

    for strategy, records in report.get("interval_rankings", {}).items():
        predictions.extend(_extract_interval_predictions(
            records,
            strategy=f"{RAW_INTERVAL_PREFIX}{strategy}",
        ))
    return predictions


def extract_aggregated_predictions(report: dict[str, Any]) -> list[LocalizationPrediction]:
    """Extract normalized predictions from an aggregated localization report."""

    predictions: list[LocalizationPrediction] = []
    predictions.extend(_extract_condition_predictions(
        report.get("aggregated_condition_node_ranking", []),
        strategy=AGGREGATED_CONDITION_STRATEGY,
    ))

    for strategy, records in report.get("aggregated_interval_rankings", {}).items():
        predictions.extend(_extract_interval_predictions(
            records,
            strategy=f"{AGGREGATED_INTERVAL_PREFIX}{strategy}",
        ))
    return predictions


def evaluate_predictions(record: dict[str, Any],
                         predictions: list[LocalizationPrediction],
                         top_k: Iterable[int] = DEFAULT_TOP_K) -> dict[str, Any]:
    """Evaluate predictions grouped by strategy."""

    validate_mutant_record(record)
    normalized_top_k = sorted({int(k) for k in top_k if int(k) > 0})
    grouped: dict[str, list[LocalizationPrediction]] = {}
    for prediction in predictions:
        grouped.setdefault(prediction.strategy, []).append(prediction)

    results = {}
    for strategy, items in grouped.items():
        sorted_items = sorted(items, key=lambda item: item.rank)
        results[strategy] = evaluate_strategy_predictions(
            record,
            sorted_items,
            normalized_top_k,
        )

    return results


def evaluate_strategy_predictions(record: dict[str, Any],
                                  predictions: list[LocalizationPrediction],
                                  top_k: Iterable[int] = DEFAULT_TOP_K) -> dict[str, Any]:
    """Evaluate Top-k hit metrics for one strategy."""

    normalized_top_k = sorted({int(k) for k in top_k if int(k) > 0})
    hit_predictions = [
        prediction
        for prediction in predictions
        if prediction_hits_ground_truth(prediction, record)
    ]
    best = min(hit_predictions, key=lambda prediction: prediction.rank) if hit_predictions else None
    best_rank = best.rank if best else None
    region_summary = _region_size_summary(predictions, normalized_top_k, best)
    inspection_summary = _inspection_region_summary(predictions, normalized_top_k, best_rank)

    topk = {
        f"top{k}": bool(best_rank is not None and best_rank <= k)
        for k in normalized_top_k
    }
    return {
        "strategy": predictions[0].strategy if predictions else None,
        "target_type": predictions[0].target_type if predictions else None,
        "prediction_count": len(predictions),
        "hit": best is not None,
        "best_rank": best_rank,
        "hit_lines": _hit_lines(best, record) if best else [],
        "hit_prediction": _prediction_to_dict(best) if best else None,
        "hit_item_region_size": best.region_size if best else None,
        "region_size": region_summary,
        "inspection_region": inspection_summary,
        "topk": topk,
    }


def prediction_hits_ground_truth(prediction: LocalizationPrediction,
                                 record: dict[str, Any]) -> bool:
    """Return True if a prediction intersects the manifest ground truth."""

    if not _prediction_file_matches(prediction, record):
        return False

    acceptable = _acceptable_line_set(record)
    if acceptable.intersection(prediction.predicted_lines):
        return True

    window = _acceptable_window(record)
    if window is None:
        return False
    start, end = window
    return any(start <= line <= end for line in prediction.predicted_lines)


def evaluate_reports(manifest_record: dict[str, Any],
                     raw_report: Optional[dict[str, Any]] = None,
                     aggregated_report: Optional[dict[str, Any]] = None,
                     top_k: Iterable[int] = DEFAULT_TOP_K) -> dict[str, Any]:
    """Evaluate raw and/or aggregated reports for one manifest record."""

    predictions = []
    if raw_report is not None:
        predictions.extend(extract_raw_predictions(raw_report))
    if aggregated_report is not None:
        predictions.extend(extract_aggregated_predictions(aggregated_report))

    metrics = evaluate_predictions(manifest_record, predictions, top_k=top_k)
    composite = evaluate_aggregated_composite_predictions(
        manifest_record,
        predictions,
        top_k=top_k,
    )
    if composite is not None:
        metrics[AGGREGATED_COMPOSITE_STRATEGY] = composite
    return {
        "mutant_id": manifest_record.get("mutant_id"),
        "mutant_file": manifest_record.get("mutant_file"),
        "operator": manifest_record.get("operator"),
        "fault_kind": manifest_record.get("fault_kind"),
        "ground_truth": manifest_record.get("ground_truth", {}),
        "summary": {
            "prediction_strategies": sorted(metrics),
            "top_k": sorted({int(k) for k in top_k if int(k) > 0}),
        },
        "metrics": metrics,
    }


def evaluate_aggregated_composite_predictions(record: dict[str, Any],
                                              predictions: list[LocalizationPrediction],
                                              top_k: Iterable[int] = DEFAULT_TOP_K
                                              ) -> Optional[dict[str, Any]]:
    """Evaluate the dual-view aggregated condition-or-interval workflow."""

    condition_items = _predictions_for_strategy(predictions, AGGREGATED_CONDITION_STRATEGY)
    interval_items = _predictions_for_strategy(predictions, AGGREGATED_EDGE_DIVERGENCE_GATED_STRATEGY)
    if not condition_items and not interval_items:
        return None

    validate_mutant_record(record)
    normalized_top_k = sorted({int(k) for k in top_k if int(k) > 0})
    prediction_count = max(len(condition_items), len(interval_items))
    union_sizes = [
        _composite_region_size(condition_items, interval_items, rank)
        for rank in range(1, prediction_count + 1)
    ]
    best_rank = None
    for rank in range(1, prediction_count + 1):
        if _composite_hits_ground_truth(condition_items, interval_items, rank, record):
            best_rank = rank
            break

    topk = {
        f"top{k}": bool(best_rank is not None and best_rank <= k)
        for k in normalized_top_k
    }
    hit_lines = (
        _composite_hit_lines(condition_items, interval_items, best_rank, record)
        if best_rank is not None else []
    )
    hit_item_region_size = _composite_rank_item_region_size(
        condition_items,
        interval_items,
        best_rank,
    )
    return {
        "strategy": AGGREGATED_COMPOSITE_STRATEGY,
        "target_type": "composite",
        "prediction_count": prediction_count,
        "hit": best_rank is not None,
        "best_rank": best_rank,
        "hit_lines": hit_lines,
        "hit_prediction": (
            _composite_prediction_to_dict(condition_items, interval_items, best_rank)
            if best_rank is not None else None
        ),
        "hit_item_region_size": hit_item_region_size,
        "region_size": {
            "average": _average(union_sizes),
            "max": max(union_sizes) if union_sizes else 0,
            "top1": _composite_region_size(condition_items, interval_items, 1),
            "hit": hit_item_region_size,
            "topk_average": {
                f"top{k}": _composite_region_size(condition_items, interval_items, k)
                for k in normalized_top_k
            },
        },
        "inspection_region": {
            "at_first_hit": (
                _composite_region_size(condition_items, interval_items, best_rank)
                if best_rank is not None else None
            ),
            "topk": {
                f"top{k}": _composite_region_size(condition_items, interval_items, k)
                for k in normalized_top_k
            },
        },
        "topk": topk,
    }


def write_evaluation_report(report: dict[str, Any],
                            output_path: str | Path) -> None:
    """Write an evaluation report JSON file."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _predictions_for_strategy(predictions: list[LocalizationPrediction],
                              strategy: str) -> list[LocalizationPrediction]:
    return sorted(
        [prediction for prediction in predictions if prediction.strategy == strategy],
        key=lambda prediction: prediction.rank,
    )


def _composite_region_size(condition_items: list[LocalizationPrediction],
                           interval_items: list[LocalizationPrediction],
                           rank: Optional[int]) -> int:
    return len(_composite_line_set(condition_items, interval_items, rank))


def _composite_line_set(condition_items: list[LocalizationPrediction],
                        interval_items: list[LocalizationPrediction],
                        rank: Optional[int]) -> set[int]:
    if rank is None or rank <= 0:
        return set()
    lines: set[int] = set()
    for prediction in condition_items[:rank]:
        lines.update(prediction.predicted_lines)
    for prediction in interval_items[:rank]:
        lines.update(prediction.predicted_lines)
    return lines


def _composite_hits_ground_truth(condition_items: list[LocalizationPrediction],
                                 interval_items: list[LocalizationPrediction],
                                 rank: int,
                                 record: dict[str, Any]) -> bool:
    return any(
        prediction_hits_ground_truth(prediction, record)
        for prediction in [*condition_items[:rank], *interval_items[:rank]]
    )


def _composite_hit_lines(condition_items: list[LocalizationPrediction],
                         interval_items: list[LocalizationPrediction],
                         rank: Optional[int],
                         record: dict[str, Any]) -> list[int]:
    if rank is None:
        return []
    hits: set[int] = set()
    for prediction in [*condition_items[:rank], *interval_items[:rank]]:
        hits.update(_hit_lines(prediction, record))
    return sorted(hits)


def _composite_rank_item_region_size(condition_items: list[LocalizationPrediction],
                                     interval_items: list[LocalizationPrediction],
                                     rank: Optional[int]) -> Optional[int]:
    if rank is None or rank <= 0:
        return None
    lines: set[int] = set()
    found_item = False
    for items in (condition_items, interval_items):
        if len(items) >= rank:
            found_item = True
            lines.update(items[rank - 1].predicted_lines)
    return len(lines) if found_item else None


def _composite_prediction_to_dict(condition_items: list[LocalizationPrediction],
                                  interval_items: list[LocalizationPrediction],
                                  rank: Optional[int]) -> dict[str, Any]:
    return {
        "target_type": "composite",
        "strategy": AGGREGATED_COMPOSITE_STRATEGY,
        "rank": rank,
        "component_strategies": [
            AGGREGATED_CONDITION_STRATEGY,
            AGGREGATED_EDGE_DIVERGENCE_GATED_STRATEGY,
        ],
        "predicted_lines": sorted(_composite_line_set(condition_items, interval_items, rank)),
        "region_size": _composite_region_size(condition_items, interval_items, rank),
        "components": {
            "condition_nodes": [
                _prediction_to_dict(prediction)
                for prediction in condition_items[:rank or 0]
            ],
            "edge_divergence_gated_intervals": [
                _prediction_to_dict(prediction)
                for prediction in interval_items[:rank or 0]
            ],
        },
    }


def _extract_condition_predictions(records: list[dict[str, Any]],
                                   strategy: str) -> list[LocalizationPrediction]:
    predictions = []
    for index, record in enumerate(records, start=1):
        line = _safe_int(record.get("line"))
        predictions.append(LocalizationPrediction(
            target_type="condition",
            strategy=strategy,
            rank=_rank(record, index),
            score=float(record.get("risk_score", 0.0)),
            predicted_lines=tuple([line] if line is not None else []),
            region_size=1 if line is not None else 0,
            source_file=record.get("source_file"),
            location_basis=record.get("location_basis", "condition_line"),
            raw=record,
        ))
    return predictions


def _extract_interval_predictions(records: list[dict[str, Any]],
                                  strategy: str) -> list[LocalizationPrediction]:
    predictions = []
    for index, record in enumerate(records, start=1):
        lines, basis = _interval_prediction_lines(record, strategy)
        predictions.append(LocalizationPrediction(
            target_type="interval",
            strategy=strategy,
            rank=_rank(record, index),
            score=float(record.get("risk_score", 0.0)),
            predicted_lines=tuple(lines),
            region_size=_prediction_region_size(record, lines),
            source_file=record.get("source_file"),
            location_basis=basis,
            raw=record,
        ))
    return predictions


def _interval_prediction_lines(record: dict[str, Any], strategy: str) -> tuple[list[int], str]:
    statement_lines = _line_list(record.get("statement_lines", []))
    if statement_lines:
        return statement_lines, "statement_lines"

    if _is_statement_aware_interval_strategy(strategy):
        return [], "statement_lines_missing"

    span = record.get("normalized_anchor_span") or record.get("condition_anchor_span")
    if span is None:
        span = record.get("line_interval")
    span_lines = _span_to_lines(span)
    if span_lines:
        return span_lines, record.get("location_basis", "condition_anchor_span")

    fallback = [
        line
        for line in (_safe_int(record.get("from_line")), _safe_int(record.get("to_line")))
        if line is not None
    ]
    return sorted(set(fallback)), record.get("location_basis", "condition_anchors")


def _is_statement_aware_interval_strategy(strategy: str) -> bool:
    # Import locally to avoid circular dependency at module level.
    from .failure_localization import INTERVAL_STRATEGY_REGISTRY, RankingSlot  # noqa: PLC0415

    for prefix in (RAW_INTERVAL_PREFIX, AGGREGATED_INTERVAL_PREFIX):
        if strategy.startswith(prefix):
            name = strategy[len(prefix):]
            if name in FOLDED_STATEMENT_INTERVAL_STRATEGIES:
                return True
            entry = INTERVAL_STRATEGY_REGISTRY.get(name)
            return entry is not None and entry.slot != RankingSlot.ANCHOR
    return False


def _prediction_file_matches(prediction: LocalizationPrediction,
                             record: dict[str, Any]) -> bool:
    if not prediction.source_file:
        return True
    ground_truth = record.get("ground_truth", {})
    acceptable_files = ground_truth.get("acceptable_files") or [ground_truth.get("primary_file")]
    acceptable_files = [file for file in acceptable_files if file]
    if not acceptable_files:
        return True
    predicted = _normalize_path(prediction.source_file)
    return any(predicted == _normalize_path(file) or predicted.endswith(_normalize_path(file))
               for file in acceptable_files)


def _acceptable_line_set(record: dict[str, Any]) -> set[int]:
    ground_truth = record.get("ground_truth", {})
    lines = ground_truth.get("acceptable_lines") or [ground_truth.get("primary_line")]
    return {
        int(line)
        for line in lines
        if line is not None
    }


def _acceptable_window(record: dict[str, Any]) -> Optional[tuple[int, int]]:
    window = record.get("ground_truth", {}).get("acceptable_line_window")
    if not window:
        return None
    start = _safe_int(window.get("start"))
    end = _safe_int(window.get("end"))
    if start is None or end is None:
        return None
    return min(start, end), max(start, end)


def _hit_lines(prediction: LocalizationPrediction,
               record: dict[str, Any]) -> list[int]:
    acceptable = _acceptable_line_set(record)
    hits = set(prediction.predicted_lines).intersection(acceptable)
    window = _acceptable_window(record)
    if window is not None:
        start, end = window
        hits.update(line for line in prediction.predicted_lines if start <= line <= end)
    return sorted(hits)


def _prediction_to_dict(prediction: LocalizationPrediction) -> dict[str, Any]:
    return {
        "target_type": prediction.target_type,
        "strategy": prediction.strategy,
        "rank": prediction.rank,
        "score": prediction.score,
        "predicted_lines": list(prediction.predicted_lines),
        "region_size": prediction.region_size,
        "source_file": prediction.source_file,
        "location_basis": prediction.location_basis,
        "raw": prediction.raw,
    }


def _region_size_summary(predictions: list[LocalizationPrediction],
                         top_k: list[int],
                         best: Optional[LocalizationPrediction]) -> dict[str, Any]:
    sizes = [prediction.region_size for prediction in predictions]
    return {
        "average": _average(sizes),
        "max": max(sizes) if sizes else 0,
        "top1": predictions[0].region_size if predictions else 0,
        "hit": best.region_size if best else None,
        "topk_average": {
            f"top{k}": _average([prediction.region_size for prediction in predictions[:k]])
            for k in top_k
        },
    }


def _inspection_region_summary(predictions: list[LocalizationPrediction],
                               top_k: list[int],
                               best_rank: Optional[int]) -> dict[str, Any]:
    return {
        "at_first_hit": (
            _inspection_region_size(predictions, best_rank)
            if best_rank is not None else None
        ),
        "topk": {
            f"top{k}": _inspection_region_size(predictions, k)
            for k in top_k
        },
    }


def _inspection_region_size(predictions: list[LocalizationPrediction],
                            rank: Optional[int]) -> int:
    if rank is None or rank <= 0:
        return 0
    lines = {
        line
        for prediction in predictions[:rank]
        for line in prediction.predicted_lines
    }
    return len(lines)


def _prediction_region_size(record: dict[str, Any], predicted_lines: list[int]) -> int:
    explicit = _safe_int(record.get("region_size"))
    if explicit is not None:
        return max(0, explicit)
    line_count = _safe_int(record.get("statement_line_count"))
    if line_count is not None:
        return max(0, line_count)
    return len(predicted_lines)


def _average(values: list[int]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _rank(record: dict[str, Any], fallback: int) -> int:
    rank = _safe_int(record.get("rank"))
    return rank if rank is not None else fallback


def _line_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []
    return sorted({
        line
        for item in value
        for line in [_safe_int(item)]
        if line is not None
    })


def _span_to_lines(value: Any) -> list[int]:
    if not isinstance(value, list) or len(value) != 2:
        return []
    start = _safe_int(value[0])
    end = _safe_int(value[1])
    if start is None or end is None:
        return []
    low, high = min(start, end), max(start, end)
    return list(range(low, high + 1))


def _safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_path(value: str) -> str:
    return str(value).replace("\\", "/")
