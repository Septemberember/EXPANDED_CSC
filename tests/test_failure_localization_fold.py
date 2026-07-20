import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from csc_engine import CCT, Condition, ConditionResult
from csc_engine.failure_localization_aggregate import aggregate_localization_report
from csc_engine.failure_localization_fold import (
    FOLDED_SCORING_REGISTRY,
    build_folded_localization_report,
)


def test_first_hit_folding_keeps_sibling_paths_isolated():
    cct = CCT()
    root = condition(1, "a")
    repeated = condition(2, "z > 0")
    cct.add_sequence([ConditionResult(root, False), ConditionResult(repeated, True)], "tc_left")
    cct.add_sequence([ConditionResult(root, True), ConditionResult(repeated, True)], "tc_right")
    assert cct.mark_tbfv_failure("tc_left", "default", {}, "formula")
    assert cct.mark_tbfv_failure("tc_right", "default", {}, "formula")

    report = build_folded_localization_report(cct, testcase_records=[])
    repeated_record = next(
        record
        for record in report["condition_node_ranking"]
        if record["condition"] == "z > 0"
    )

    assert repeated_record["F_c"] == 2
    assert repeated_record["P_c"] == 0
    assert repeated_record["occurrence_count"] == 2
    assert repeated_record["representative_count"] == 2


def test_folded_statement_intervals_are_statement_aware_in_aggregation():
    report = {
        "summary": {"strategy": "folded_source_candidate_v1"},
        "condition_node_ranking": [],
        "interval_rankings": {
            "folded_seed_e": [
                {
                    "rank": 1,
                    "candidate_id": "seed_e_12_13",
                    "kind": "seed_e",
                    "from_line": 10,
                    "from_condition": "x > 0",
                    "outcome": "true",
                    "to_line": 20,
                    "to_condition": "y > 0",
                    "statement_lines": [12, 13],
                    "region_size": 2,
                    "risk_score": 1.0,
                    "exec_count": 3,
                    "fail_count": 2,
                    "pass_count": 1,
                    "failure_density": 2 / 3,
                },
            ],
            "folded_seed_s": [],
        },
    }

    aggregated = aggregate_localization_report(report, source_file="Subject_M1.java")
    item = aggregated["aggregated_interval_rankings"]["folded_seed_e"][0]

    assert item["location_basis"] == "statement_lines"
    assert item["statement_lines"] == [12, 13]
    assert item["region_size"] == 2


def test_density_log_strategy_keeps_pure_low_coverage_candidates_meaningful():
    assert "density_log" in FOLDED_SCORING_REGISTRY


def condition(line, expr):
    return Condition(line, expr, expr)
