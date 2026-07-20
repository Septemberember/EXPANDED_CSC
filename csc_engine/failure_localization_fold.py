"""Fold-the-Tree fault localization — source-candidate-based evidence folding.

This module implements the RQ4 Fold-the-Tree approach. Instead of scoring
dynamic CCT occurrences and then max-aggregating to source lines, it:

1. Discovers source-level candidates from CCT nodes and edge trace segments.
2. Folds repeated dynamic occurrences on the same root-to-leaf path into a
   single first-hit representative per candidate.
3. Accumulates leaf-level pass/fail evidence across all first-hit
   representatives via set union.
4. Scores candidates with a pluggable strategy (default: coverage × purity).

The module is intentionally isolated from the existing failure_localization
pipeline — it reads the same CCT / trace / TBFV inputs but produces its own
report format (compatible with the existing aggregation and evaluation layers).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .cct import CCT, INFEASIBLE_MARKER, Node, RANGE_EXCLUDED_MARKER
from .execution_trace import ExecutionEvent, parse_trace_jsonl
from .failure_localization import (
    _empty_segment_evidence,
    _int_line_set,
    _sibling_edge_id,
    _sibling_exclusive_segment,
    _sibling_shared_segment,
    build_trace_segment_index,
)


# ---------------------------------------------------------------------------
# Scoring strategy registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FoldedScoringStrategy:
    """Pluggable risk-score formula for folded source candidates."""

    name: str
    description: str
    score: Callable[["SourceCandidate", int, int], float]
    # Signature: (candidate, F_total, P_total) -> risk_score


def _score_coverage_x_purity(
    candidate: SourceCandidate, F_total: int, _P_total: int
) -> float:
    """FailedCoverage × FailurePurity — parameter-free."""
    F_c = len(candidate.failed_tc_ids)
    if F_c == 0 or F_total == 0:
        return 0.0
    coverage = F_c / F_total
    purity = F_c / max(1, F_c + len(candidate.passed_tc_ids))
    return coverage * purity


def _score_density_log(
    candidate: SourceCandidate, _F_total: int, _P_total: int
) -> float:
    """FailureDensity × log(1 + F_c).

    This keeps the folded evidence organization but avoids globally penalising
    candidates that are highly pure yet cover only a small subset of failed
    test cases.
    """
    F_c = len(candidate.failed_tc_ids)
    if F_c == 0:
        return 0.0
    return candidate.failure_density * math.log1p(F_c)


FOLDED_SCORING_REGISTRY: dict[str, FoldedScoringStrategy] = {
    "coverage_x_purity": FoldedScoringStrategy(
        name="coverage_x_purity",
        description=(
            "FailedCoverage × FailurePurity.  Coverage = F_c / F_total measures "
            "how many failed leaves this candidate covers.  Purity = F_c / (F_c + P_c) "
            "penalises candidates that also cover many passing leaves.  Parameter-free."
        ),
        score=_score_coverage_x_purity,
    ),
    "density_log": FoldedScoringStrategy(
        name="density_log",
        description=(
            "FailureDensity × ln(1 + F_c).  Preserves folded source-candidate "
            "evidence while giving pure low-coverage candidates a meaningful "
            "score when only a small subset of failed test cases exposes the fault."
        ),
        score=_score_density_log,
    ),
}

DEFAULT_FOLDED_SCORING = "coverage_x_purity"


# ---------------------------------------------------------------------------
# Analysis-only data structures (never mutate CCT)
# ---------------------------------------------------------------------------


@dataclass
class EdgeView:
    """Read-only view of a CCT edge with sibling and statement-segment data."""

    edge_id: str
    parent_node_id: str
    child_node_id_or_leaf_id: Optional[str]
    outcome: str  # "TRUE" or "FALSE"
    sibling_edge_id: str
    raw_statement_lines: list[int] = field(default_factory=list)
    seed_e_statement_lines: list[int] = field(default_factory=list)
    seed_s_statement_lines: list[int] = field(default_factory=list)
    # Transition metadata for report compatibility.
    from_line: Optional[int] = None
    from_condition: Optional[str] = None
    to_line: Optional[int] = None
    to_condition: Optional[str] = None


@dataclass
class CandidateOccurrence:
    """One dynamic appearance of a source candidate on the CCT."""

    id: str
    candidate_id: str
    kind: str  # "condition" | "seed_e" | "seed_s"
    node_id: Optional[str] = None  # set for condition occurrences
    edge_id: Optional[str] = None  # set for edge occurrences
    statement_lines: list[int] = field(default_factory=list)
    # Transition context for report / later analysis.
    transition_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceCandidate:
    """A folded source-level fault candidate.

    Leaf evidence is accumulated via set union across all first-hit
    representatives (Pass 3).  This prevents double-counting when a
    candidate appears multiple times on overlapping paths.
    """

    id: str
    kind: str  # "condition" | "seed_e" | "seed_s"
    source_identity: tuple  # stable identity key for folding
    failed_tc_ids: set[str] = field(default_factory=set)
    passed_tc_ids: set[str] = field(default_factory=set)
    occurrence_ids: list[str] = field(default_factory=list)
    representative_ids: list[str] = field(default_factory=list)
    representative_contexts: list[dict[str, Any]] = field(default_factory=list)

    @property
    def F_c(self) -> int:
        return len(self.failed_tc_ids)

    @property
    def P_c(self) -> int:
        return len(self.passed_tc_ids)

    @property
    def exec_count(self) -> int:
        return self.F_c + self.P_c

    @property
    def failure_density(self) -> float:
        total = self.exec_count
        return self.F_c / total if total > 0 else 0.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REAL_LEAF_MARKERS = frozenset({INFEASIBLE_MARKER, RANGE_EXCLUDED_MARKER})


def _leaf_test_case_ids(node: Node) -> tuple[set[str], set[str]]:
    """Return (failed_tc_ids, passed_tc_ids) for a CCT leaf node.

    Each leaf may hold multiple test cases.  A test case is classified as
    *failed* if it appears in ``node.tbfv_failures`` with non-empty entries,
    otherwise *passed*.  Infeasible / out-of-range markers are excluded.

    When the same test case reaches multiple leaves and fails at any one of
    them, it will appear in the failed set of that leaf and the passed set of
    the other.  The caller is responsible for removing passed entries that also
    appear as failed elsewhere (see ``_deduplicate_passed``).
    """
    test_cases = getattr(node, "test_cases", set()) or set()
    real = {str(tc) for tc in test_cases if str(tc) not in _REAL_LEAF_MARKERS}
    if not real:
        return set(), set()
    failures = getattr(node, "tbfv_failures", None) or {}
    failed = {tc for tc in real if failures.get(tc)}
    passed = real - failed
    return failed, passed


def _deduplicate_passed(
    passed_leaves: set[str], failed_leaves: set[str],
) -> set[str]:
    """Remove test cases from *passed_leaves* that also appear as failed anywhere.

    A test case that fails on any execution path is considered failed overall
    (single-fault assumption: the fault is present, just didn't manifest on
    some paths).
    """
    return passed_leaves - failed_leaves


def _make_candidate_id(kind: str, source_identity: tuple) -> str:
    """Produce a stable, human-readable candidate id."""
    parts = [kind]
    for item in source_identity:
        if isinstance(item, tuple):
            parts.append("_".join(str(x) for x in item))
        else:
            parts.append(str(item))
    return "_".join(parts)


def _tiebreak_key(record: dict[str, Any]) -> tuple:
    """Parameter-free tiebreaker for ranking folded candidates.

    Priority (after risk_score descending):
    1. F_c descending   — more failed leaves = more suspicious
    2. P_c ascending    — fewer passed leaves = more suspicious
    3. region_size asc  — smaller region = more precise
    4. line_start asc   — stable ordering
    """
    return (
        -float(record.get("risk_score", 0.0)),
        -int(record.get("F_c", 0)),
        int(record.get("P_c", 0)),
        int(record.get("region_size", 10**9)),
        int(record.get("line_start", 10**9)),
    )


def _rank_folded_records(records: list[dict[str, Any]]) -> None:
    """Sort *records* in-place and assign rank numbers."""
    records.sort(key=_tiebreak_key)
    for index, record in enumerate(records, start=1):
        record["rank"] = index


# ---------------------------------------------------------------------------
# Pass 1 — Candidate and EdgeView discovery
# ---------------------------------------------------------------------------


def _discover_candidates(
    cct: CCT,
    trace_segment_index: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, SourceCandidate],
    dict[str, CandidateOccurrence],
    dict[str, EdgeView],
    dict[str, Any],
]:
    """Top-down DFS: discover all source candidates and their occurrences.

    Returns:
        candidate_registry: candidate_id -> SourceCandidate
        occurrence_registry: occurrence_id -> CandidateOccurrence
        edge_views: edge_id -> EdgeView
        discovery_stats: summary dict with {unstable_segment_variants, ...}
    """
    candidate_registry: dict[str, SourceCandidate] = {}
    occurrence_registry: dict[str, CandidateOccurrence] = {}
    edge_views: dict[str, EdgeView] = {}
    # Track line-set variants per transition key for stability diagnostics.
    transition_variants: dict[tuple, list[frozenset[int]]] = {}

    _discover_from_node(
        cct.root,
        node_id="root",
        candidate_registry=candidate_registry,
        occurrence_registry=occurrence_registry,
        edge_views=edge_views,
        trace_segment_index=trace_segment_index,
        transition_variants=transition_variants,
    )

    # Count unstable transitions.
    unstable = 0
    for key, variants in transition_variants.items():
        unique = set(variants)
        if len(unique) > 1:
            unstable += 1

    return (
        candidate_registry,
        occurrence_registry,
        edge_views,
        {"unstable_segment_variants": unstable,
         "total_edge_transitions": len(transition_variants)},
    )


def _discover_from_node(
    node: Node,
    node_id: str,
    candidate_registry: dict[str, SourceCandidate],
    occurrence_registry: dict[str, CandidateOccurrence],
    edge_views: dict[str, EdgeView],
    trace_segment_index: dict[str, dict[str, Any]],
    transition_variants: dict[tuple, list[frozenset[int]]],
) -> None:
    """Recurse CCT subtree, registering candidates and EdgeViews."""
    if node is None or node.is_leaf:
        return

    condition = node.condition

    # --- condition candidate ---
    cond_identity = (condition.line_number, condition.condition_string)
    cond_candidate = _ensure_candidate(
        "condition", cond_identity, candidate_registry,
    )
    occ_id = f"cond_occurrence_{node_id}"
    cond_occ = CandidateOccurrence(
        id=occ_id,
        candidate_id=cond_candidate.id,
        kind="condition",
        node_id=node_id,
        statement_lines=[],
        transition_context={
            "node_id": node_id,
            "line": condition.line_number,
            "condition": condition.condition_string,
            "loop_count": condition.loop_count,
        },
    )
    cond_candidate.occurrence_ids.append(occ_id)
    occurrence_registry[occ_id] = cond_occ

    # --- edge candidates ---
    for outcome, child, sibling, child_id in [
        ("false", node.left, node.right, f"{node_id}.F"),
        ("true", node.right, node.left, f"{node_id}.T"),
    ]:
        edge_id = f"{node_id}.{outcome.upper()}"
        child_condition = (
            child.condition if child is not None and not child.is_leaf else None
        )
        sibling_edge_id = _sibling_edge_id(edge_id)

        # Build EdgeView from trace segment data.
        segment = trace_segment_index.get(
            edge_id, _empty_segment_evidence("unmatched")
        )
        sibling_segment = trace_segment_index.get(
            sibling_edge_id, _empty_segment_evidence("unmatched")
        )

        raw_lines = sorted(
            _int_line_set(segment.get("statement_lines", []))
        )
        sibling_lines = sorted(
            _int_line_set(sibling_segment.get("statement_lines", []))
        )

        # Compute SEED-E (set difference) and SEED-S (set intersection).
        raw_set = frozenset(raw_lines)
        sib_set = frozenset(sibling_lines)
        exclusive_lines = sorted(raw_set - sib_set)
        shared_lines = sorted(raw_set & sib_set)

        # Track transition variants for stability diagnostics.
        trans_key = (
            condition.line_number,
            condition.condition_string,
            outcome,
            child_condition.line_number if child_condition else None,
            child_condition.condition_string if child_condition else None,
        )
        transition_variants.setdefault(trans_key, []).append(raw_set)

        ev = EdgeView(
            edge_id=edge_id,
            parent_node_id=node_id,
            child_node_id_or_leaf_id=(
                child_id if child is not None and not child.is_leaf else None
            ),
            outcome=outcome,
            sibling_edge_id=sibling_edge_id,
            raw_statement_lines=raw_lines,
            seed_e_statement_lines=exclusive_lines,
            seed_s_statement_lines=shared_lines,
            from_line=condition.line_number,
            from_condition=condition.condition_string,
            to_line=(
                child_condition.line_number if child_condition else None
            ),
            to_condition=(
                child_condition.condition_string if child_condition else None
            ),
        )
        edge_views[edge_id] = ev

        # --- seed_e candidate (exclusive lines) ---
        if exclusive_lines:
            seed_e_identity = ("seed_e", tuple(exclusive_lines))
            seed_e_candidate = _ensure_candidate(
                "seed_e", seed_e_identity, candidate_registry,
            )
            occ_id_e = f"seed_e_{edge_id}"
            occ_e = CandidateOccurrence(
                id=occ_id_e,
                candidate_id=seed_e_candidate.id,
                kind="seed_e",
                edge_id=edge_id,
                statement_lines=exclusive_lines,
                transition_context={
                    "from_line": condition.line_number,
                    "from_condition": condition.condition_string,
                    "outcome": outcome,
                    "to_line": (
                        child_condition.line_number if child_condition else None
                    ),
                    "to_condition": (
                        child_condition.condition_string
                        if child_condition
                        else None
                    ),
                    "parent_condition_line": condition.line_number,
                    "parent_condition_text": condition.condition_string,
                },
            )
            seed_e_candidate.occurrence_ids.append(occ_id_e)
            occurrence_registry[occ_id_e] = occ_e

        # --- seed_s candidate (shared lines) ---
        if shared_lines:
            seed_s_identity = ("seed_s", tuple(shared_lines))
            seed_s_candidate = _ensure_candidate(
                "seed_s", seed_s_identity, candidate_registry,
            )
            occ_id_s = f"seed_s_{edge_id}"
            occ_s = CandidateOccurrence(
                id=occ_id_s,
                candidate_id=seed_s_candidate.id,
                kind="seed_s",
                edge_id=edge_id,
                statement_lines=shared_lines,
                transition_context={
                    "from_line": condition.line_number,
                    "from_condition": condition.condition_string,
                    "outcome": outcome,
                    "to_line": (
                        child_condition.line_number if child_condition else None
                    ),
                    "to_condition": (
                        child_condition.condition_string
                        if child_condition
                        else None
                    ),
                    "parent_condition_line": condition.line_number,
                    "parent_condition_text": condition.condition_string,
                },
            )
            seed_s_candidate.occurrence_ids.append(occ_id_s)
            occurrence_registry[occ_id_s] = occ_s

    # Recurse.
    _discover_from_node(
        node.left,
        f"{node_id}.F",
        candidate_registry,
        occurrence_registry,
        edge_views,
        trace_segment_index,
        transition_variants,
    )
    _discover_from_node(
        node.right,
        f"{node_id}.T",
        candidate_registry,
        occurrence_registry,
        edge_views,
        trace_segment_index,
        transition_variants,
    )


def _ensure_candidate(
    kind: str,
    identity: tuple,
    registry: dict[str, SourceCandidate],
) -> SourceCandidate:
    """Return existing candidate or create and register a new one."""
    cand_id = _make_candidate_id(kind, identity)
    if cand_id not in registry:
        registry[cand_id] = SourceCandidate(
            id=cand_id,
            kind=kind,
            source_identity=identity,
        )
    return registry[cand_id]


# ---------------------------------------------------------------------------
# Pass 2 — Subtree leaf evidence (post-order DFS)
# ---------------------------------------------------------------------------


def _compute_subtree_leaf_evidence(
    node: Optional[Node],
) -> tuple[set[str], set[str]]:
    """Return (failed_tc_ids, passed_tc_ids) for the CCT subtree.

    Test case IDs are the atomic evidence unit — each TC is counted exactly
    once regardless of how many CCT leaves it reaches.
    """
    if node is None:
        return set(), set()

    if node.is_leaf:
        failed, passed = _leaf_test_case_ids(node)
        return failed, passed

    left_fail, left_pass = _compute_subtree_leaf_evidence(node.left)
    right_fail, right_pass = _compute_subtree_leaf_evidence(node.right)
    return (
        left_fail | right_fail,
        left_pass | right_pass,
    )


# ---------------------------------------------------------------------------
# Pass 3 — First-hit folding (top-down DFS, copy-on-write seen set)
# ---------------------------------------------------------------------------


def _fold_first_hit(
    node: Optional[Node],
    node_id: str,
    seen_on_path: frozenset[str],
    node_evidence: dict[str, tuple[set[str], set[str]]],
    candidate_registry: dict[str, SourceCandidate],
    edge_views: dict[str, EdgeView],
    # Maps candidate_id -> (edge_id, node_id) for representative tracking.
    cond_at_node: dict[str, str],
    edge_cands_at_node: dict[str, list[tuple[str, str]]],
) -> frozenset[str]:
    """Fold first-hit evidence for candidates on path *node_id*.

    This is candidate-specific folding, *not* subtree pruning.  Even when a
    candidate has already been seen, traversal continues because deeper nodes
    may host first-hit occurrences of *other* candidates.
    """
    if node is None or node.is_leaf:
        return seen_on_path

    next_seen = seen_on_path
    failed, passed = node_evidence.get(
        node_id, (set(), set())
    )

    # --- condition candidate ---
    cond_cid = cond_at_node.get(node_id)
    if cond_cid is not None and cond_cid not in next_seen:
        candidate = candidate_registry.get(cond_cid)
        if candidate is not None:
            candidate.failed_tc_ids |= failed
            candidate.passed_tc_ids |= passed
            candidate.representative_ids.append(node_id)
            candidate.representative_contexts.append({
                "node_id": node_id,
            })
            next_seen = next_seen | {cond_cid}

    # --- edge candidates ---
    #
    # Each outgoing edge starts from the node-local seen set.  The seen set
    # returned by one child must not be reused for its sibling; otherwise the
    # traversal would treat source candidates encountered only on the false
    # branch as if they had also appeared on the true branch.  That would break
    # the root-to-current-path invariant of first-hit folding.
    for outcome, child, child_id in [
        ("false", node.left, f"{node_id}.F"),
        ("true", node.right, f"{node_id}.T"),
    ]:
        branch_seen = next_seen
        edge_id = f"{node_id}.{outcome.upper()}"
        child_failed, child_passed = node_evidence.get(
            child_id, (set(), set())
        )
        for cand_id, occ_id in edge_cands_at_node.get(edge_id, []):
            if cand_id not in branch_seen:
                candidate = candidate_registry.get(cand_id)
                if candidate is not None:
                    candidate.failed_tc_ids |= child_failed
                    candidate.passed_tc_ids |= child_passed
                    candidate.representative_ids.append(occ_id)
                    candidate.representative_contexts.append({
                        "edge_id": edge_id,
                        "representative_occurrence": occ_id,
                    })
                    branch_seen = branch_seen | {cand_id}

        # Always recurse — unseen candidates may appear deeper.  The recursive
        # result is intentionally ignored to keep sibling paths isolated.
        _fold_first_hit(
            child, child_id, branch_seen,
            node_evidence, candidate_registry, edge_views,
            cond_at_node, edge_cands_at_node,
        )

    return next_seen


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build_folded_localization_report(
    cct: CCT,
    testcase_records: list[dict[str, Any]],
    scoring_strategy: str = DEFAULT_FOLDED_SCORING,
) -> dict[str, Any]:
    """Build a folded fault-localization report from an annotated CCT.

    Parameters
    ----------
    cct:
        Annotated CCT with TBFV failure labels on leaves.
    testcase_records:
        List of dicts, each with a ``"trace_path"`` key pointing to a trace
        JSONL file.
    scoring_strategy:
        Key into :data:`FOLDED_SCORING_REGISTRY`.

    Returns
    -------
    A dict with keys ``"summary"``, ``"condition_node_ranking"``, and
    ``"interval_rankings"`` (containing ``"folded_seed_e"`` and
    ``"folded_seed_s"`` sub-keys).  The schema is compatible with
    :func:`~csc_engine.failure_localization_eval.extract_aggregated_predictions`
    and :func:`~csc_engine.failure_localization_aggregate.aggregate_localization_report`.
    """
    score_strat = FOLDED_SCORING_REGISTRY.get(scoring_strategy)
    if score_strat is None:
        raise ValueError(f"Unknown folded scoring strategy: {scoring_strategy}")

    # Build trace segment index (reuses existing infrastructure).
    segment_index = build_trace_segment_index(
        testcase_records,
        candidate_edge_ids=_all_cct_edge_ids(cct),
    )

    # ---------- Pass 1: discover ----------
    (
        candidate_registry,
        occurrence_registry,
        edge_views,
        discovery_stats,
    ) = _discover_candidates(cct, segment_index)

    # Build fast lookup maps for Pass 3.
    # cond_at_node: node_id -> condition candidate_id
    cond_at_node: dict[str, str] = {}
    # edge_cands_at_node: edge_id -> list[(candidate_id, occurrence_id)]
    edge_cands_at_node: dict[str, list[tuple[str, str]]] = {}
    for occ in occurrence_registry.values():
        if occ.kind == "condition" and occ.node_id is not None:
            cond_at_node[occ.node_id] = occ.candidate_id
        elif occ.edge_id is not None:
            edge_cands_at_node.setdefault(occ.edge_id, []).append(
                (occ.candidate_id, occ.id)
            )

    # ---------- Pass 2: leaf evidence ----------
    root_failed, root_passed = _compute_subtree_leaf_evidence(cct.root)
    # Deduplicate: a TC that fails on ANY path is failed overall.
    root_passed = _deduplicate_passed(root_passed, root_failed)
    F_total = len(root_failed)
    P_total = len(root_passed)

    # Pre-compute evidence for every node (used by Pass 3 for fast lookup).
    node_evidence: dict[str, tuple[set[str], set[str]]] = {}
    _collect_all_node_evidence(
        cct.root, "root", node_evidence,
    )
    # Deduplicate per-node evidence as well.
    for node_id, (failed, passed) in node_evidence.items():
        node_evidence[node_id] = (
            failed,
            _deduplicate_passed(passed, failed),
        )

    # ---------- Pass 3: first-hit folding ----------
    _fold_first_hit(
        cct.root, "root", frozenset(),
        node_evidence, candidate_registry, edge_views,
        cond_at_node, edge_cands_at_node,
    )

    # Deduplicate candidate-level evidence.
    for candidate in candidate_registry.values():
        candidate.passed_tc_ids = _deduplicate_passed(
            candidate.passed_tc_ids, candidate.failed_tc_ids,
        )

    # ---------- Build rankings ----------
    scoring_fn = score_strat.score

    condition_ranking: list[dict[str, Any]] = []
    seed_e_ranking: list[dict[str, Any]] = []
    seed_s_ranking: list[dict[str, Any]] = []

    for candidate in candidate_registry.values():
        if candidate.F_c == 0:
            # Candidate covers no failed leaves — skip.
            continue
        risk = scoring_fn(candidate, F_total, P_total)
        record = _candidate_to_report_record(candidate, risk, edge_views)
        if candidate.kind == "condition":
            condition_ranking.append(record)
        elif candidate.kind == "seed_e":
            seed_e_ranking.append(record)
        elif candidate.kind == "seed_s":
            seed_s_ranking.append(record)

    _rank_folded_records(condition_ranking)
    _rank_folded_records(seed_e_ranking)
    _rank_folded_records(seed_s_ranking)

    # Edge-partition ranking: merge SEED-E and SEED-S, re-rank by score.
    edge_partition_ranking = seed_e_ranking + seed_s_ranking
    _rank_folded_records(edge_partition_ranking)

    return {
        "summary": {
            "strategy": "folded_source_candidate_v1",
            "scoring_strategy": scoring_strategy,
            "F_total": F_total,
            "P_total": P_total,
            "condition_candidates": len(condition_ranking),
            "seed_e_candidates": len(seed_e_ranking),
            "seed_s_candidates": len(seed_s_ranking),
            "edge_partition_candidates": len(edge_partition_ranking),
            **discovery_stats,
        },
        "condition_node_ranking": condition_ranking,
        "interval_rankings": {
            "folded_seed_e": seed_e_ranking,
            "folded_seed_s": seed_s_ranking,
            "folded_edge_partition": edge_partition_ranking,
        },
    }


def _all_cct_edge_ids(cct: CCT) -> set[str]:
    """Collect all CCT edge IDs for trace segment indexing."""
    edge_ids: set[str] = set()

    def collect(node: Optional[Node], node_id: str) -> None:
        if node is None or node.is_leaf:
            return
        for outcome, child, child_id in [
            ("false", node.left, f"{node_id}.F"),
            ("true", node.right, f"{node_id}.T"),
        ]:
            edge_ids.add(f"{node_id}.{outcome.upper()}")
            collect(child, child_id)

    collect(cct.root, "root")
    # Also add sibling edges so the segment index covers them.
    siblings = {_sibling_edge_id(eid) for eid in edge_ids}
    siblings.discard("")
    edge_ids |= siblings
    return edge_ids


def _collect_all_node_evidence(
    node: Optional[Node],
    node_id: str,
    evidence_map: dict[str, tuple[set[str], set[str]]],
) -> tuple[set[str], set[str]]:
    """Recurse and fill *evidence_map* with per-node TC-level evidence."""
    if node is None:
        result = (set(), set())
        evidence_map[node_id] = result
        return result

    if node.is_leaf:
        failed, passed = _leaf_test_case_ids(node)
        result = (failed, passed)
        evidence_map[node_id] = result
        return result

    left_fail, left_pass = _collect_all_node_evidence(
        node.left, f"{node_id}.F", evidence_map,
    )
    right_fail, right_pass = _collect_all_node_evidence(
        node.right, f"{node_id}.T", evidence_map,
    )
    result = (left_fail | right_fail, left_pass | right_pass)
    evidence_map[node_id] = result
    return result


def _candidate_to_report_record(
    candidate: SourceCandidate,
    risk_score: float,
    edge_views: dict[str, EdgeView],
) -> dict[str, Any]:
    """Convert a folded candidate into a report record.

    The record schema includes all fields required by the existing aggregation
    and evaluation layers for backward compatibility.
    """
    base: dict[str, Any] = {
        "candidate_id": candidate.id,
        "kind": candidate.kind,
        "F_c": candidate.F_c,
        "P_c": candidate.P_c,
        "exec_count": candidate.exec_count,
        "fail_count": candidate.F_c,
        "pass_count": candidate.P_c,
        "failure_density": candidate.failure_density,
        "risk_score": risk_score,
        "occurrence_count": len(candidate.occurrence_ids),
        "representative_count": len(candidate.representative_ids),
        "representative_contexts": candidate.representative_contexts,
        "location_basis": "statement_lines",
    }

    # Fill transition metadata from the best representative occurrence.
    # For condition candidates: line / condition come from source_identity.
    # For SEED candidates: borrow from the first representative's edge context.
    if candidate.kind == "condition":
        # source_identity = (line_number, condition_string)
        if len(candidate.source_identity) >= 2:
            base["line"] = int(candidate.source_identity[0])
            base["condition"] = str(candidate.source_identity[1])
        base["statement_lines"] = []
        base["region_size"] = 1
        base["line_start"] = base.get("line", 0)
        base["line_end"] = base.get("line", 0)
        base["location_basis"] = "condition_line"
    else:
        # source_identity = (kind, tuple(lines))
        if len(candidate.source_identity) >= 2:
            lines_tuple = candidate.source_identity[1]
            lines = sorted(lines_tuple)
        else:
            lines = []
        base["statement_lines"] = lines
        base["region_size"] = len(lines)
        base["line_start"] = lines[0] if lines else None
        base["line_end"] = lines[-1] if lines else None

        # Borrow transition metadata from a representative's EdgeView.
        best_edge_id = None
        for ctx in candidate.representative_contexts:
            eid = ctx.get("edge_id")
            if eid and eid in edge_views:
                best_edge_id = eid
                break
        if best_edge_id is not None:
            ev = edge_views[best_edge_id]
            base["from_line"] = ev.from_line
            base["from_condition"] = ev.from_condition
            base["outcome"] = ev.outcome
            base["to_line"] = ev.to_line
            base["to_condition"] = ev.to_condition
        else:
            base["from_line"] = None
            base["from_condition"] = None
            base["outcome"] = None
            base["to_line"] = None
            base["to_condition"] = None

    return base


def write_folded_localization_report(
    report: dict[str, Any], output_path: str,
) -> None:
    """Write a folded localization report as JSON."""
    import json
    from pathlib import Path

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
