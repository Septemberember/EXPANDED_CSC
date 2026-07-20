"""Read-only CCT-based failure localization strategies.

The first strategy ranks two kinds of suspicious regions from a CCT that has
already been annotated with Refined TBFV failures:

* condition nodes: risk that a condition itself is faulty;
* condition transitions: risk that the CCT edge from one condition outcome to
  the next condition or leaf leads to faulty behavior.

For statement-aware edge strategies, the concrete source-location evidence is
the ASSIGN/RETURN lines observed in the trace segment, not the condition-anchor
span between the two condition lines.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from .cct import CCT, INFEASIBLE_MARKER, Node, RANGE_EXCLUDED_MARKER
from .execution_trace import ExecutionEvent, parse_trace_jsonl


class RankingSlot(Enum):
    """The three semantic categories induced by the CCT structure."""

    ANCHOR = "anchor"
    STATEMENT = "statement"
    SEED_E = "seed_e"
    SEED_S = "seed_s"


@dataclass(frozen=True)
class IntervalStrategy:
    """Descriptor for one CCT edge-level scoring strategy.

    Each strategy belongs to one :class:`RankingSlot` and self-describes
    whether it requires trace segments and/or sibling-edge segments.
    """

    name: str
    description: str
    slot: RankingSlot
    uses_trace_segments: bool
    uses_sibling_edges: bool
    enrich: Callable[[dict[str, Any], dict[str, dict[str, Any]]], None]


LOCALIZATION_STRATEGY = "condition_and_interval_v1"
CCT_ONLY_INTERVAL_STRATEGY = "cct_only"
STATEMENT_PRESENCE_INTERVAL_STRATEGY = "statement_presence"
EDGE_DIVERGENCE_GATED_INTERVAL_STRATEGY = "edge_divergence_gated"
EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_INTERVAL_STRATEGY = "edge_divergence_sibling_exclusive"
EDGE_DIVERGENCE_SIBLING_SHARED_INTERVAL_STRATEGY = "edge_divergence_sibling_shared"
DEFAULT_INTERVAL_STRATEGY = CCT_ONLY_INTERVAL_STRATEGY
STATEMENT_EVENT_TYPES = {"ASSIGN", "RETURN"}


# ---------------------------------------------------------------------------
# Strategy enrich functions — one per strategy, extracted from the old
# if-elif chain in _score_interval_records().
# ---------------------------------------------------------------------------


def _enrich_cct_only(record: dict[str, Any],
                     _segment_index: dict[str, dict[str, Any]]) -> None:
    record["location_basis"] = "condition_anchor_span"
    record["region_size"] = _line_interval_size(record.get("condition_anchor_span"))
    record["risk_score"] = float(record.get("base_risk_score", record.get("risk_score", 0.0)))


def _enrich_statement_presence(record: dict[str, Any],
                               segment_index: dict[str, dict[str, Any]]) -> None:
    base_score = float(record.get("base_risk_score", record.get("risk_score", 0.0)))
    segment = segment_index.get(record["edge_id"], _empty_segment_evidence("unmatched"))
    record.update(segment)
    record["location_basis"] = "statement_lines"
    record["region_size"] = int(segment.get("statement_line_count", 0))
    record["risk_score"] = base_score if segment.get("statement_count", 0) > 0 else 0.0


def _enrich_edge_divergence_gated(record: dict[str, Any],
                                  segment_index: dict[str, dict[str, Any]]) -> None:
    base_score = float(record.get("base_risk_score", record.get("risk_score", 0.0)))
    segment = segment_index.get(record["edge_id"], _empty_segment_evidence("unmatched"))
    record.update(segment)
    line_count = int(segment.get("statement_line_count", 0))
    line_weight = _statement_line_weight(line_count)
    record["location_basis"] = "statement_lines"
    record["region_size"] = line_count
    record["statement_line_weight"] = line_weight
    record["risk_score"] = base_score * line_weight


def _enrich_edge_divergence_sibling_exclusive(record: dict[str, Any],
                                              segment_index: dict[str, dict[str, Any]]) -> None:
    base_score = float(record.get("base_risk_score", record.get("risk_score", 0.0)))
    segment = segment_index.get(record["edge_id"], _empty_segment_evidence("unmatched"))
    sibling_edge_id = _sibling_edge_id(record["edge_id"])
    sibling_segment = segment_index.get(sibling_edge_id, _empty_segment_evidence("unmatched"))
    exclusive_segment = _sibling_exclusive_segment(segment, sibling_segment)
    record.update(exclusive_segment)
    line_count = int(exclusive_segment.get("statement_line_count", 0))
    line_weight = _statement_line_weight(line_count)
    record["sibling_edge_id"] = sibling_edge_id
    record["location_basis"] = "sibling_exclusive_statement_lines"
    record["region_size"] = line_count
    record["statement_line_weight"] = line_weight
    record["risk_score"] = base_score


def _enrich_edge_divergence_sibling_shared(record: dict[str, Any],
                                           segment_index: dict[str, dict[str, Any]]) -> None:
    segment = segment_index.get(record["edge_id"], _empty_segment_evidence("unmatched"))
    sibling_edge_id = _sibling_edge_id(record["edge_id"])
    sibling_segment = segment_index.get(sibling_edge_id, _empty_segment_evidence("unmatched"))
    shared_segment = _sibling_shared_segment(segment, sibling_segment)
    record.update(shared_segment)
    line_count = int(shared_segment.get("statement_line_count", 0))
    line_weight = _statement_line_weight(line_count)
    shared_score = _sibling_shared_risk_score(record)
    record["sibling_edge_id"] = sibling_edge_id
    record["location_basis"] = "sibling_shared_statement_lines"
    record["region_size"] = line_count
    record["statement_line_weight"] = line_weight
    record["shared_risk_score"] = shared_score
    record["risk_score"] = shared_score


# ---------------------------------------------------------------------------
# Strategy registry — the single source of truth for all interval strategies.
# Adding a new strategy: add one entry here + its enrich function above.
# ---------------------------------------------------------------------------

INTERVAL_STRATEGY_REGISTRY: dict[str, IntervalStrategy] = {
    CCT_ONLY_INTERVAL_STRATEGY: IntervalStrategy(
        name=CCT_ONLY_INTERVAL_STRATEGY,
        description="Uses CCT subtree failure evidence only.",
        slot=RankingSlot.ANCHOR,
        uses_trace_segments=False,
        uses_sibling_edges=False,
        enrich=_enrich_cct_only,
    ),
    STATEMENT_PRESENCE_INTERVAL_STRATEGY: IntervalStrategy(
        name=STATEMENT_PRESENCE_INTERVAL_STRATEGY,
        description=(
            "Keeps CCT edge risk only when the concrete edge segment contains "
            "ASSIGN or RETURN trace events."
        ),
        slot=RankingSlot.STATEMENT,
        uses_trace_segments=True,
        uses_sibling_edges=False,
        enrich=_enrich_statement_presence,
    ),
    EDGE_DIVERGENCE_GATED_INTERVAL_STRATEGY: IntervalStrategy(
        name=EDGE_DIVERGENCE_GATED_INTERVAL_STRATEGY,
        description=(
            "Edge-level Divergence and Gated Evaluation: gates empty statement "
            "regions and weights non-empty regions by 1 + log10(1 + LC), where LC "
            "is the number of distinct ASSIGN/RETURN source lines."
        ),
        slot=RankingSlot.STATEMENT,
        uses_trace_segments=True,
        uses_sibling_edges=False,
        enrich=_enrich_edge_divergence_gated,
    ),
    EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_INTERVAL_STRATEGY: IntervalStrategy(
        name=EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_INTERVAL_STRATEGY,
        description=(
            "Sibling-Exclusive Edge Divergence (SEED): scores the CCT edge using "
            "only statement lines that are present on the edge but absent from its "
            "sibling edge under the same parent condition."
        ),
        slot=RankingSlot.SEED_E,
        uses_trace_segments=True,
        uses_sibling_edges=True,
        enrich=_enrich_edge_divergence_sibling_exclusive,
    ),
    EDGE_DIVERGENCE_SIBLING_SHARED_INTERVAL_STRATEGY: IntervalStrategy(
        name=EDGE_DIVERGENCE_SIBLING_SHARED_INTERVAL_STRATEGY,
        description=(
            "Sibling-Shared Edge Divergence (SEED-S): scores statement lines shared "
            "by sibling edges under the same parent condition using parent failure "
            "density and a small-sibling-divergence bonus."
        ),
        slot=RankingSlot.SEED_S,
        uses_trace_segments=True,
        uses_sibling_edges=True,
        enrich=_enrich_edge_divergence_sibling_shared,
    ),
}

# Backward-compatible descriptive dict — rebuilt from the registry.
INTERVAL_STRATEGY_DESCRIPTIONS: dict[str, str] = {
    entry.name: entry.description
    for entry in INTERVAL_STRATEGY_REGISTRY.values()
}


@dataclass
class Evidence:
    """Executable and failing testcase evidence for one CCT subtree."""

    exec_cases: set[str] = field(default_factory=set)
    fail_cases: set[str] = field(default_factory=set)
    infeasible_leaves: int = 0
    out_of_range_leaves: int = 0
    empty_leaves: int = 0

    def merge(self, other: "Evidence") -> "Evidence":
        return Evidence(
            exec_cases=set(self.exec_cases) | set(other.exec_cases),
            fail_cases=set(self.fail_cases) | set(other.fail_cases),
            infeasible_leaves=self.infeasible_leaves + other.infeasible_leaves,
            out_of_range_leaves=self.out_of_range_leaves + other.out_of_range_leaves,
            empty_leaves=self.empty_leaves + other.empty_leaves,
        )

    @property
    def exec_count(self) -> int:
        return len(self.exec_cases)

    @property
    def fail_count(self) -> int:
        return len(self.fail_cases)

    @property
    def pass_count(self) -> int:
        return max(0, self.exec_count - self.fail_count)

    @property
    def failure_density(self) -> float:
        return self.fail_count / self.exec_count if self.exec_count else 0.0

    def ignored_counts(self) -> dict[str, int]:
        return {
            "infeasible_leaves": self.infeasible_leaves,
            "out_of_range_leaves": self.out_of_range_leaves,
            "empty_leaves": self.empty_leaves,
        }


def build_localization_report(cct: CCT,
                              top_k: Optional[int] = None,
                              testcase_records: Optional[list[dict[str, Any]]] = None,
                              interval_strategies: Optional[list[str]] = None,
                              default_interval_strategy: Optional[str] = None) -> dict[str, Any]:
    """Build a failure-localization report from an annotated CCT."""

    evidence_map: dict[int, Evidence] = {}
    child_evidence_map: dict[int, dict[str, Evidence]] = {}
    root_evidence = _collect_evidence(cct.root, evidence_map, child_evidence_map)

    condition_nodes: list[dict[str, Any]] = []
    condition_intervals: list[dict[str, Any]] = []
    _rank_failed_subtrees(
        cct.root,
        depth=0,
        node_id="root",
        evidence_map=evidence_map,
        child_evidence_map=child_evidence_map,
        condition_nodes=condition_nodes,
        condition_intervals=condition_intervals,
    )

    _rank_records(condition_nodes)
    _rank_records(condition_intervals)
    condition_node_candidates = len(condition_nodes)
    condition_interval_candidates = len(condition_intervals)

    available_strategies = _resolve_interval_strategies(testcase_records, interval_strategies)
    default_interval_strategy = _resolve_default_interval_strategy(
        available_strategies,
        default_interval_strategy,
    )
    segment_index = {}
    if _uses_trace_segments(available_strategies):
        candidate_edge_ids = {
            record["edge_id"]
            for record in condition_intervals
            if record.get("fail_count", 0) > 0
            and record.get("base_risk_score", record.get("risk_score", 0.0)) > 0
        }
        if any(
            INTERVAL_STRATEGY_REGISTRY[s].uses_sibling_edges
            for s in available_strategies
        ):
            candidate_edge_ids.update(
                sibling
                for sibling in (_sibling_edge_id(edge_id) for edge_id in list(candidate_edge_ids))
                if sibling
            )
        segment_index = build_trace_segment_index(testcase_records or [], candidate_edge_ids)

    interval_rankings = {
        strategy: _score_interval_records(condition_intervals, strategy, segment_index)
        for strategy in available_strategies
    }
    zero_statement_intervals = _count_zero_statement_intervals(
        interval_rankings.get(STATEMENT_PRESENCE_INTERVAL_STRATEGY, [])
    )
    if top_k is not None:
        condition_nodes = condition_nodes[:top_k]
        interval_rankings = {
            name: records[:top_k]
            for name, records in interval_rankings.items()
        }
    default_interval_ranking = interval_rankings[default_interval_strategy]

    return {
        "summary": {
            "strategy": LOCALIZATION_STRATEGY,
            "default_interval_strategy": default_interval_strategy,
            "available_interval_strategies": list(interval_rankings.keys()),
            "statement_aware_intervals": STATEMENT_PRESENCE_INTERVAL_STRATEGY in interval_rankings,
            "zero_statement_intervals": zero_statement_intervals,
            "executed_cases": root_evidence.exec_count,
            "failed_cases": root_evidence.fail_count,
            "condition_node_candidates": condition_node_candidates,
            "condition_interval_candidates": condition_interval_candidates,
            "ignored": root_evidence.ignored_counts(),
        },
        "condition_node_ranking": condition_nodes,
        "condition_interval_ranking": default_interval_ranking,
        "interval_rankings": interval_rankings,
    }


def write_localization_report(report: dict[str, Any], output_path: str | Path) -> None:
    """Write a failure-localization report as JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def build_trace_segment_index(records: list[dict[str, Any]],
                              candidate_edge_ids: set[str],
                              max_sample_events: int = 3) -> dict[str, dict[str, Any]]:
    """Collect statement-segment evidence for selected concrete CCT edges.

    Each candidate edge is observed at most once. Scanning stops early once all
    candidates have been matched.
    """

    segment_index = {
        edge_id: _empty_segment_evidence("unmatched")
        for edge_id in candidate_edge_ids
    }
    pending_edges = set(candidate_edge_ids)
    if not pending_edges:
        return {}

    for record in records:
        if not pending_edges:
            break
        trace_path = record.get("trace_path")
        if not trace_path:
            continue
        events = parse_trace_jsonl(trace_path)
        _collect_trace_segments_from_events(
            events,
            pending_edges,
            segment_index,
            max_sample_events=max_sample_events,
        )

    return segment_index


def build_localization_dot(cct: CCT,
                           report: Optional[dict[str, Any]] = None,
                           name: str = "CCT_Failure_Localization",
                           interval_strategy: Optional[str] = None) -> str:
    """Build a DOT risk view from a CCT and its localization report.

    The CCT is not mutated. Node and edge styles are derived from report records
    while traversing the tree.
    """

    report = report or build_localization_report(cct)
    selected_strategy = _selected_interval_strategy(report, interval_strategy)
    node_records = {
        str(record["node_id"]): record
        for record in report.get("condition_node_ranking", [])
    }
    edge_records = {
        str(record["edge_id"]): record
        for record in _interval_records_for_strategy(report, selected_strategy)
    }
    max_node_score = max(
        (float(record.get("risk_score", 0.0)) for record in node_records.values()),
        default=0.0,
    )
    max_edge_score = max(
        (float(record.get("risk_score", 0.0)) for record in edge_records.values()),
        default=0.0,
    )

    lines = [
        f"digraph {name} {{",
        "  rankdir=TB;",
        '  node [shape=box, style=filled, fontname="monospace", fontsize=10];',
        '  edge [fontname="monospace", fontsize=9];',
        f'  graph [label="Failure localization edge strategy: {selected_strategy}", labelloc=t];',
        "",
        "  // Legend",
        "  {",
        "    rank=sink;",
        "    legend [shape=plaintext, label=<",
        '      <table border="0" cellborder="1" cellspacing="0" cellpadding="4">',
        '        <tr><td bgcolor="#ffcdd2"><b>High risk</b></td><td>Top suspicious condition node or interval</td></tr>',
        '        <tr><td bgcolor="#ffe0b2"><b>Medium risk</b></td><td>Moderate suspiciousness</td></tr>',
        '        <tr><td bgcolor="#fff8e1"><b>Low risk</b></td><td>Low but nonzero suspiciousness</td></tr>',
        '        <tr><td bgcolor="#f5f5f5"><b>Condition</b></td><td>No failed executable evidence</td></tr>',
        '        <tr><td bgcolor="#ffcdd2"><b>Leaf</b></td><td>TBFV failure leaf</td></tr>',
        "      </table>",
        "    >];",
        "  }",
        "",
    ]

    counter = 0

    def next_dot_id() -> str:
        nonlocal counter
        dot_id = f"node{counter}"
        counter += 1
        return dot_id

    def visit(node: Optional[Node],
              cct_id: str,
              parent_dot_id: Optional[str],
              incoming_outcome: Optional[str],
              incoming_edge_id: Optional[str]) -> None:
        dot_id = next_dot_id()
        lines.append(f"  {dot_id} [{_node_attrs(node, cct_id, node_records, max_node_score)}];")
        if parent_dot_id is not None and incoming_outcome is not None and incoming_edge_id is not None:
            lines.append(
                f"  {parent_dot_id} -> {dot_id} "
                f"[{_edge_attrs(incoming_outcome, incoming_edge_id, edge_records, max_edge_score)}];"
            )
        if node is not None and not node.is_leaf:
            visit(node.left, f"{cct_id}.F", dot_id, "F", f"{cct_id}.FALSE")
            visit(node.right, f"{cct_id}.T", dot_id, "T", f"{cct_id}.TRUE")

    visit(cct.root, "root", None, None, None)
    lines.append("}")
    return "\n".join(lines)


def write_localization_dot(cct: CCT,
                           report: dict[str, Any],
                           output_path: str | Path,
                           interval_strategy: Optional[str] = None) -> None:
    """Write the failure-localization DOT risk view."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_localization_dot(cct, report, interval_strategy=interval_strategy),
        encoding="utf-8",
    )


def localization_dot_filename(interval_strategy: str) -> str:
    """Return the strategy-specific localization DOT filename."""

    return f"cct_failure_localization_{interval_strategy}.dot"


def _collect_evidence(node: Optional[Node],
                      evidence_map: dict[int, Evidence],
                      child_evidence_map: dict[int, dict[str, Evidence]]) -> Evidence:
    if node is None:
        return Evidence(empty_leaves=1)

    if node.is_leaf:
        evidence = _leaf_evidence(node)
        evidence_map[id(node)] = evidence
        return evidence

    false_evidence = _collect_evidence(node.left, evidence_map, child_evidence_map)
    true_evidence = _collect_evidence(node.right, evidence_map, child_evidence_map)
    evidence = false_evidence.merge(true_evidence)
    evidence_map[id(node)] = evidence
    child_evidence_map[id(node)] = {
        "false": false_evidence,
        "true": true_evidence,
    }
    return evidence


def _leaf_evidence(node: Node) -> Evidence:
    test_cases = getattr(node, "test_cases", set()) or set()
    if test_cases == {INFEASIBLE_MARKER}:
        return Evidence(infeasible_leaves=1)
    if test_cases == {RANGE_EXCLUDED_MARKER}:
        return Evidence(out_of_range_leaves=1)

    real_cases = {
        str(tc)
        for tc in test_cases
        if tc not in {INFEASIBLE_MARKER, RANGE_EXCLUDED_MARKER}
    }
    failures = getattr(node, "tbfv_failures", None) or {}
    failed_cases = {str(tc) for tc, entries in failures.items() if entries}
    failed_cases &= real_cases
    return Evidence(exec_cases=real_cases, fail_cases=failed_cases)


def _collect_trace_segments_from_events(events: list[ExecutionEvent],
                                        pending_edges: set[str],
                                        segment_index: dict[str, dict[str, Any]],
                                        max_sample_events: int) -> None:
    current_node_id = "root"
    index = 0
    while index < len(events):
        event = events[index]
        if event.type != "COND":
            index += 1
            continue

        outcome = "TRUE" if _event_truthy(event.value) else "FALSE"
        child_suffix = "T" if outcome == "TRUE" else "F"
        edge_id = f"{current_node_id}.{outcome}"
        segment_events, next_index = _events_until_next_condition(events, index + 1)
        if edge_id in pending_edges:
            segment_index[edge_id] = _segment_evidence_from_events(
                segment_events,
                max_sample_events=max_sample_events,
            )
            pending_edges.remove(edge_id)
            if not pending_edges:
                return

        current_node_id = f"{current_node_id}.{child_suffix}"
        index = next_index


def _events_until_next_condition(events: list[ExecutionEvent],
                                 start_index: int) -> tuple[list[ExecutionEvent], int]:
    segment_events: list[ExecutionEvent] = []
    index = start_index
    while index < len(events) and events[index].type != "COND":
        segment_events.append(events[index])
        index += 1
    return segment_events, index


def _segment_evidence_from_events(events: list[ExecutionEvent],
                                  max_sample_events: int) -> dict[str, Any]:
    statement_events = [event for event in events if event.type in STATEMENT_EVENT_TYPES]
    assignment_count = sum(1 for event in statement_events if event.type == "ASSIGN")
    return_count = sum(1 for event in statement_events if event.type == "RETURN")
    lines = sorted({
        event.line
        for event in statement_events
        if event.line
    })
    return {
        "segment_status": "matched",
        "statement_count": len(statement_events),
        "statement_line_count": len(lines),
        "region_size": len(lines),
        "assignment_count": assignment_count,
        "return_count": return_count,
        "statement_lines": lines,
        "sample_events": [
            _sample_event(event)
            for event in statement_events[:max_sample_events]
        ],
    }


def _empty_segment_evidence(status: str) -> dict[str, Any]:
    return {
        "segment_status": status,
        "statement_count": 0,
        "statement_line_count": 0,
        "region_size": 0,
        "assignment_count": 0,
        "return_count": 0,
        "statement_lines": [],
        "sample_events": [],
    }


def _sample_event(event: ExecutionEvent) -> dict[str, Any]:
    return {
        "type": event.type,
        "line": event.line,
        "kind": event.kind,
        "target": event.target,
        "rhs": event.rhs,
    }


def _event_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def _rank_failed_subtrees(node: Optional[Node],
                          depth: int,
                          node_id: str,
                          evidence_map: dict[int, Evidence],
                          child_evidence_map: dict[int, dict[str, Evidence]],
                          condition_nodes: list[dict[str, Any]],
                          condition_intervals: list[dict[str, Any]]) -> None:
    if node is None or node.is_leaf:
        return

    evidence = evidence_map[id(node)]
    if evidence.fail_count == 0:
        return

    if evidence.exec_count > 0:
        condition_nodes.append(_condition_node_record(node, evidence, depth, node_id))

    children = [
        ("false", node.left, node.right, f"{node_id}.F"),
        ("true", node.right, node.left, f"{node_id}.T"),
    ]
    child_evidence = child_evidence_map.get(id(node), {})
    for outcome, child, sibling, child_id in children:
        ev = child_evidence.get(outcome, Evidence())
        if ev.fail_count > 0 and ev.exec_count > 0:
            sibling_ev = evidence_map.get(id(sibling), Evidence()) if sibling is not None else Evidence(empty_leaves=1)
            condition_intervals.append(
                _condition_interval_record(node, child, evidence, ev, sibling_ev, depth, node_id, outcome)
            )

    _rank_failed_subtrees(
        node.left,
        depth + 1,
        f"{node_id}.F",
        evidence_map,
        child_evidence_map,
        condition_nodes,
        condition_intervals,
    )
    _rank_failed_subtrees(
        node.right,
        depth + 1,
        f"{node_id}.T",
        evidence_map,
        child_evidence_map,
        condition_nodes,
        condition_intervals,
    )


def _condition_node_record(node: Node, evidence: Evidence,
                           depth: int, node_id: str) -> dict[str, Any]:
    density = evidence.failure_density
    risk_score = _density_support_score(density, evidence.fail_count)
    condition = node.condition
    return {
        "node_id": node_id,
        "line": condition.line_number,
        "condition": condition.condition_string,
        "loop_count": condition.loop_count,
        "depth": depth,
        "exec_count": evidence.exec_count,
        "fail_count": evidence.fail_count,
        "pass_count": evidence.pass_count,
        "failure_density": density,
        "risk_score": risk_score,
        "ignored": evidence.ignored_counts(),
    }


def _condition_interval_record(parent: Node,
                               child: Optional[Node],
                               parent_evidence: Evidence,
                               child_evidence: Evidence,
                               sibling_evidence: Evidence,
                               depth: int,
                               parent_id: str,
                               outcome: str) -> dict[str, Any]:
    child_density = child_evidence.failure_density
    sibling_density = sibling_evidence.failure_density
    outcome_delta = max(0.0, child_density - sibling_density)
    base_score = _interval_density_support_score(child_density, child_evidence.fail_count)
    outcome_delta_bonus = 1.0 + outcome_delta
    risk_score = base_score * outcome_delta_bonus

    parent_condition = parent.condition
    child_condition = child.condition if child is not None and not child.is_leaf else None
    interval = _line_interval(parent_condition.line_number, child_condition.line_number if child_condition else None)
    anchor_region_size = _line_interval_size(interval["line_interval"])
    return {
        "edge_id": f"{parent_id}.{outcome.upper()}",
        "from_line": parent_condition.line_number,
        "from_condition": parent_condition.condition_string,
        "from_loop_count": parent_condition.loop_count,
        "outcome": outcome,
        "to_line": child_condition.line_number if child_condition else None,
        "to_condition": child_condition.condition_string if child_condition else None,
        "to_loop_count": child_condition.loop_count if child_condition else None,
        "line_interval": interval["line_interval"],
        "interval_kind": interval["interval_kind"],
        "condition_anchor_span": interval["line_interval"],
        "condition_anchor_kind": interval["interval_kind"],
        "location_basis": "condition_anchor_span",
        "region_size": anchor_region_size,
        "depth": depth + 1,
        "exec_count": child_evidence.exec_count,
        "fail_count": child_evidence.fail_count,
        "pass_count": child_evidence.pass_count,
        "failure_density": child_density,
        "parent_exec_count": parent_evidence.exec_count,
        "parent_fail_count": parent_evidence.fail_count,
        "parent_pass_count": parent_evidence.pass_count,
        "parent_failure_density": parent_evidence.failure_density,
        "sibling_failure_density": sibling_density,
        "outcome_delta": outcome_delta,
        "base_interval_score": base_score,
        "outcome_delta_bonus": outcome_delta_bonus,
        "base_risk_score": risk_score,
        "risk_score": risk_score,
        "ignored": child_evidence.ignored_counts(),
    }


def _line_interval(from_line: int, to_line: Optional[int]) -> dict[str, Any]:
    if to_line is None:
        return {
            "line_interval": [from_line, None],
            "interval_kind": "to_leaf",
        }
    if from_line <= to_line:
        return {
            "line_interval": [from_line, to_line],
            "interval_kind": "forward",
        }
    return {
        "line_interval": [to_line, from_line],
        "interval_kind": "backward_or_loop",
    }


def _density_support_score(density: float, fail_count: int) -> float:
    return density * math.log(1 + fail_count)


def _interval_density_support_score(density: float, fail_count: int) -> float:
    return density * math.log10(1 + fail_count)


def _rank_records(records: list[dict[str, Any]]) -> None:
    records.sort(
        key=lambda record: (
            record.get("risk_score", 0.0),
            record.get("fail_count", 0),
            record.get("failure_density", 0.0),
            record.get("depth", 0),
        ),
        reverse=True,
    )
    for index, record in enumerate(records, start=1):
        record["rank"] = index


def _resolve_interval_strategies(testcase_records: Optional[list[dict[str, Any]]],
                                 requested: Optional[list[str]]) -> list[str]:
    if requested is None:
        if testcase_records is not None:
            return [s for s in INTERVAL_STRATEGY_REGISTRY
                    if s != EDGE_DIVERGENCE_GATED_INTERVAL_STRATEGY]
        return [CCT_ONLY_INTERVAL_STRATEGY]

    strategies = []
    for strategy in requested:
        if strategy not in INTERVAL_STRATEGY_REGISTRY:
            raise ValueError(f"Unknown interval strategy: {strategy}")
        if INTERVAL_STRATEGY_REGISTRY[strategy].uses_trace_segments and testcase_records is None:
            raise ValueError(f"{strategy} interval strategy requires testcase records")
        if strategy not in strategies:
            strategies.append(strategy)
    return strategies or [CCT_ONLY_INTERVAL_STRATEGY]


def _resolve_default_interval_strategy(available: list[str],
                                       requested: Optional[str]) -> str:
    if requested is not None:
        if requested not in available:
            raise ValueError(f"Default interval strategy is not available: {requested}")
        return requested
    if STATEMENT_PRESENCE_INTERVAL_STRATEGY in available:
        return STATEMENT_PRESENCE_INTERVAL_STRATEGY
    return CCT_ONLY_INTERVAL_STRATEGY


def _score_interval_records(records: list[dict[str, Any]],
                            strategy: str,
                            segment_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    strategy_def = INTERVAL_STRATEGY_REGISTRY.get(strategy)
    if strategy_def is None:
        raise ValueError(f"Unknown interval strategy: {strategy}")
    scored = []
    for record in records:
        copied = dict(record)
        copied.pop("rank", None)
        base_score = float(copied.get("base_risk_score", copied.get("risk_score", 0.0)))
        copied["base_risk_score"] = base_score
        strategy_def.enrich(copied, segment_index)
        scored.append(copied)
    _rank_records(scored)
    return scored


def _uses_trace_segments(strategies: list[str]) -> bool:
    return any(
        INTERVAL_STRATEGY_REGISTRY[s].uses_trace_segments
        for s in strategies
    )


def _sibling_edge_id(edge_id: str) -> str:
    if edge_id.endswith(".TRUE"):
        return f"{edge_id[:-5]}.FALSE"
    if edge_id.endswith(".FALSE"):
        return f"{edge_id[:-6]}.TRUE"
    return ""


def _sibling_exclusive_segment(segment: dict[str, Any],
                               sibling_segment: dict[str, Any]) -> dict[str, Any]:
    raw_lines = _int_line_set(segment.get("statement_lines", []))
    sibling_lines = _int_line_set(sibling_segment.get("statement_lines", []))
    sibling_matched = sibling_segment.get("segment_status") == "matched"
    if sibling_matched:
        statement_lines = sorted(raw_lines - sibling_lines)
        removed_lines = sorted(raw_lines & sibling_lines)
        region_basis = "sibling_exclusive"
    else:
        statement_lines = sorted(raw_lines)
        removed_lines = []
        region_basis = "raw_no_sibling"

    sample_events = [
        event
        for event in segment.get("sample_events", [])
        if event.get("line") in statement_lines
    ]
    return {
        "segment_status": segment.get("segment_status", "unmatched"),
        "sibling_segment_status": sibling_segment.get("segment_status", "unmatched"),
        "statement_count": len(sample_events),
        "raw_statement_count": int(segment.get("statement_count", 0)),
        "statement_line_count": len(statement_lines),
        "raw_statement_line_count": len(raw_lines),
        "sibling_statement_line_count": len(sibling_lines),
        "removed_shared_statement_line_count": len(removed_lines),
        "region_size": len(statement_lines),
        "assignment_count": sum(1 for event in sample_events if event.get("type") == "ASSIGN"),
        "return_count": sum(1 for event in sample_events if event.get("type") == "RETURN"),
        "raw_statement_lines": sorted(raw_lines),
        "sibling_statement_lines": sorted(sibling_lines),
        "exclusive_statement_lines": statement_lines,
        "removed_shared_statement_lines": removed_lines,
        "statement_lines": statement_lines,
        "sample_events": sample_events,
        "region_basis": region_basis,
    }


def _sibling_shared_segment(segment: dict[str, Any],
                            sibling_segment: dict[str, Any]) -> dict[str, Any]:
    raw_lines = _int_line_set(segment.get("statement_lines", []))
    sibling_lines = _int_line_set(sibling_segment.get("statement_lines", []))
    sibling_matched = sibling_segment.get("segment_status") == "matched"
    if sibling_matched:
        statement_lines = sorted(raw_lines & sibling_lines)
        region_basis = "sibling_shared"
    else:
        statement_lines = []
        region_basis = "shared_no_sibling"

    sample_events = [
        event
        for event in segment.get("sample_events", [])
        if event.get("line") in statement_lines
    ]
    return {
        "segment_status": segment.get("segment_status", "unmatched"),
        "sibling_segment_status": sibling_segment.get("segment_status", "unmatched"),
        "statement_count": len(sample_events),
        "raw_statement_count": int(segment.get("statement_count", 0)),
        "statement_line_count": len(statement_lines),
        "raw_statement_line_count": len(raw_lines),
        "sibling_statement_line_count": len(sibling_lines),
        "shared_statement_line_count": len(statement_lines),
        "region_size": len(statement_lines),
        "assignment_count": sum(1 for event in sample_events if event.get("type") == "ASSIGN"),
        "return_count": sum(1 for event in sample_events if event.get("type") == "RETURN"),
        "raw_statement_lines": sorted(raw_lines),
        "sibling_statement_lines": sorted(sibling_lines),
        "shared_statement_lines": statement_lines,
        "statement_lines": statement_lines,
        "sample_events": sample_events,
        "region_basis": region_basis,
    }


def _sibling_shared_risk_score(record: dict[str, Any]) -> float:
    parent_density = float(record.get("parent_failure_density", 0.0))
    parent_fail_count = int(record.get("parent_fail_count", 0))
    child_density = float(record.get("failure_density", 0.0))
    sibling_density = float(record.get("sibling_failure_density", 0.0))
    sibling_gap = abs(child_density - sibling_density)
    shared_bonus = 2.0 - min(1.0, max(0.0, sibling_gap))
    return parent_density * math.log10(1 + parent_fail_count) * shared_bonus


def _int_line_set(lines: Any) -> set[int]:
    result = set()
    if not isinstance(lines, list):
        return result
    for line in lines:
        if line is None:
            continue
        try:
            result.add(int(line))
        except (TypeError, ValueError):
            continue
    return result


def _statement_line_weight(line_count: int) -> float:
    if line_count <= 0:
        return 0.0
    return 1.0 + math.log10(1 + line_count)


def _line_interval_size(span: Any) -> int:
    if not isinstance(span, list) or len(span) != 2:
        return 0
    start, end = span
    if start is None or end is None:
        return 0
    return abs(int(end) - int(start)) + 1


def _count_zero_statement_intervals(records: list[dict[str, Any]]) -> int:
    return sum(
        1
        for record in records
        if record.get("base_risk_score", 0.0) > 0
        and record.get("statement_count", 0) == 0
    )


def _selected_interval_strategy(report: dict[str, Any],
                                requested: Optional[str]) -> str:
    if requested is not None:
        if requested not in report.get("interval_rankings", {}):
            raise ValueError(f"Interval strategy not found in report: {requested}")
        return requested
    return report.get("summary", {}).get("default_interval_strategy", CCT_ONLY_INTERVAL_STRATEGY)


def _interval_records_for_strategy(report: dict[str, Any],
                                   strategy: str) -> list[dict[str, Any]]:
    rankings = report.get("interval_rankings", {})
    if strategy in rankings:
        return rankings[strategy]
    return report.get("condition_interval_ranking", [])


def _node_attrs(node: Optional[Node],
                cct_id: str,
                node_records: dict[str, dict[str, Any]],
                max_score: float) -> str:
    if node is None:
        return _dot_attrs({
            "label": "{EMPTY}",
            "shape": "ellipse",
            "fillcolor": "#eeeeee",
            "fontcolor": "#999999",
            "style": "dashed",
        })

    if node.is_leaf:
        return _leaf_node_attrs(node)

    cond = node.condition
    record = node_records.get(cct_id)
    label = f"({cond.loop_count}) {cond.condition_string}\nL{cond.line_number}"
    attrs = {
        "label": label,
        "fillcolor": "#f5f5f5",
        "fontcolor": "#333333",
        "color": "#9e9e9e",
        "penwidth": "1",
    }
    if record is not None:
        score = float(record.get("risk_score", 0.0))
        style = _risk_style(score, max_score)
        attrs.update({
            "label": (
                f"{label}\n"
                f"rank #{record.get('rank')} score={score:.4f}\n"
                f"fail={record.get('fail_count', 0)}/{record.get('exec_count', 0)}"
            ),
            "fillcolor": style["fillcolor"],
            "fontcolor": style["fontcolor"],
            "color": style["color"],
            "penwidth": style["penwidth"],
            "style": "filled,bold",
        })
    return _dot_attrs(attrs)


def _leaf_node_attrs(node: Node) -> str:
    test_cases = getattr(node, "test_cases", set()) or set()
    if test_cases == {INFEASIBLE_MARKER}:
        label = "INFEASIBLE"
        color = "#d6d6d6"
        font = "#555555"
    elif test_cases == {RANGE_EXCLUDED_MARKER}:
        label = "OUT-OF-RANGE"
        color = "#fff9c4"
        font = "#f57f17"
    else:
        sorted_cases = sorted(str(tc) for tc in test_cases)
        failures = getattr(node, "tbfv_failures", None) or {}
        failed_cases = [tc for tc in sorted_cases if failures.get(tc)]
        shown = failed_cases if failed_cases else sorted_cases
        label = ", ".join(shown[:5])
        if len(shown) > 5:
            label += f" ... (+{len(shown) - 5})"
        if failed_cases:
            label += "\nTBFV FAIL"
            color = "#ffcdd2"
            font = "#b71c1c"
        else:
            color = "#e8f5e9"
            font = "#1b5e20"

    return _dot_attrs({
        "label": label,
        "shape": "ellipse",
        "fillcolor": color,
        "fontcolor": font,
    })


def _edge_attrs(outcome: str,
                edge_id: str,
                edge_records: dict[str, dict[str, Any]],
                max_score: float) -> str:
    is_true = outcome == "T"
    attrs = {
        "label": outcome,
        "color": "#2e7d32" if is_true else "#c62828",
        "fontcolor": "#2e7d32" if is_true else "#c62828",
        "style": "solid" if is_true else "dashed",
        "penwidth": "1",
    }
    record = edge_records.get(edge_id)
    if record is not None:
        score = float(record.get("risk_score", 0.0))
        label_parts = [
            outcome,
            f"rank #{record.get('rank')} score={score:.4f}",
            f"fail={record.get('fail_count', 0)}/{record.get('exec_count', 0)}",
        ]
        if "base_risk_score" in record:
            label_parts.append(f"base={float(record.get('base_risk_score', 0.0)):.4f}")
        if "statement_count" in record:
            label_parts.append(f"stmt={record.get('statement_count', 0)}")
        if "statement_line_count" in record:
            label_parts.append(f"LC={record.get('statement_line_count', 0)}")
        if "raw_statement_line_count" in record:
            label_parts.append(f"rawLC={record.get('raw_statement_line_count', 0)}")
        if "removed_shared_statement_line_count" in record:
            label_parts.append(f"removed={record.get('removed_shared_statement_line_count', 0)}")
        if record.get("statement_lines"):
            label_parts.append(f"lines={_format_statement_lines(record['statement_lines'])}")
        if record.get("removed_shared_statement_lines"):
            label_parts.append(
                f"shared={_format_statement_lines(record['removed_shared_statement_lines'])}"
            )
        if "statement_line_weight" in record:
            label_parts.append(
                f"w={float(record.get('statement_line_weight', 0.0)):.4f}"
            )
        attrs.update({
            "label": "\n".join(label_parts),
        })
        if score > 0:
            style = _risk_style(score, max_score)
            attrs.update({
                "color": style["color"],
                "fontcolor": style["fontcolor"],
                "penwidth": style["penwidth"],
                "style": "bold" if is_true else "bold,dashed",
            })
    return _dot_attrs(attrs)


def _format_statement_lines(lines: list[int], max_lines: int = 4) -> str:
    shown = [str(line) for line in lines[:max_lines]]
    if len(lines) > max_lines:
        shown.append(f"+{len(lines) - max_lines}")
    return ",".join(shown)


def _risk_style(score: float, max_score: float) -> dict[str, str]:
    ratio = score / max_score if max_score > 0 else 0.0
    if ratio >= 0.66:
        fill = "#ffcdd2"
        color = "#b71c1c"
        penwidth = "4"
    elif ratio >= 0.33:
        fill = "#ffe0b2"
        color = "#e65100"
        penwidth = "3"
    else:
        fill = "#fff8e1"
        color = "#f9a825"
        penwidth = "2"
    return {
        "fillcolor": fill,
        "fontcolor": color,
        "color": color,
        "penwidth": penwidth,
    }


def _dot_attrs(attrs: dict[str, Any]) -> str:
    return ", ".join(f'{key}="{_dot_escape(value)}"' for key, value in attrs.items())


def _dot_escape(value: Any) -> str:
    text = str(value)
    return (
        text
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )
