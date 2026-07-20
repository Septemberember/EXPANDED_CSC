import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csc_engine import (
    aggregate_localization_report,
    write_aggregated_localization_report,
)


def test_aggregate_condition_nodes_by_source_line_and_condition():
    report = {
        "summary": {},
        "condition_node_ranking": [
            {
                "rank": 1,
                "node_id": "root.F",
                "line": 10,
                "condition": "x > 0",
                "risk_score": 1.0,
                "exec_count": 3,
                "fail_count": 2,
                "pass_count": 1,
                "failure_density": 2 / 3,
            },
            {
                "rank": 3,
                "node_id": "root.F.T",
                "line": 10,
                "condition": "x > 0",
                "risk_score": 0.4,
                "exec_count": 2,
                "fail_count": 1,
                "pass_count": 1,
                "failure_density": 0.5,
            },
        ],
        "interval_rankings": {},
    }

    aggregated = aggregate_localization_report(report, source_file="Subject_M1.java")
    nodes = aggregated["aggregated_condition_node_ranking"]

    assert len(nodes) == 1
    assert nodes[0]["source_file"] == "Subject_M1.java"
    assert nodes[0]["line"] == 10
    assert nodes[0]["condition"] == "x > 0"
    assert nodes[0]["risk_score"] == 1.0
    assert nodes[0]["support_count"] == 2
    assert nodes[0]["raw_node_ids"] == ["root.F", "root.F.T"]


def test_aggregate_statement_aware_edges_by_condition_transition_key():
    report = {
        "summary": {},
        "condition_node_ranking": [],
        "interval_rankings": {
            "edge_divergence_gated": [
                edge_record(
                    rank=1,
                    edge_id="root.F.TRUE",
                    risk_score=2.0,
                    statement_lines=[12, 13],
                ),
                edge_record(
                    rank=5,
                    edge_id="root.F.T.TRUE",
                    risk_score=1.2,
                    statement_lines=[12, 13],
                ),
            ],
        },
    }

    aggregated = aggregate_localization_report(report, source_file="Subject_M1.java")
    intervals = aggregated["aggregated_interval_rankings"]["edge_divergence_gated"]

    assert len(intervals) == 1
    item = intervals[0]
    assert item["source_file"] == "Subject_M1.java"
    assert item["from_line"] == 10
    assert item["from_condition"] == "x > 0"
    assert item["outcome"] == "TRUE"
    assert item["to_line"] == 20
    assert item["to_condition"] == "y > 0"
    assert item["location_basis"] == "statement_lines"
    assert item["statement_lines"] == [12, 13]
    assert item["region_size"] == 2
    assert item["support_count"] == 2
    assert item["risk_score"] == 2.0
    assert item["best_raw_rank"] == 1
    assert item["raw_edge_ids"] == ["root.F.TRUE", "root.F.T.TRUE"]


def test_aggregate_statement_aware_edges_does_not_group_by_statement_lines():
    report = {
        "summary": {},
        "condition_node_ranking": [],
        "interval_rankings": {
            "statement_presence": [
                edge_record(
                    rank=1,
                    edge_id="root.TRUE",
                    risk_score=1.0,
                    statement_lines=[12],
                ),
                edge_record(
                    rank=2,
                    edge_id="root.T.TRUE",
                    risk_score=0.8,
                    statement_lines=[12, 13],
                ),
            ],
        },
    }

    aggregated = aggregate_localization_report(report, source_file="Subject_M1.java")
    intervals = aggregated["aggregated_interval_rankings"]["statement_presence"]

    assert len(intervals) == 1
    assert intervals[0]["statement_lines"] == [12, 13]
    assert intervals[0]["region_size"] == 2
    assert intervals[0]["statement_line_variants"] == [[12], [12, 13]]


def test_aggregate_sibling_exclusive_edges_keeps_exclusive_region_metadata():
    report = {
        "summary": {},
        "condition_node_ranking": [],
        "interval_rankings": {
            "edge_divergence_sibling_exclusive": [
                edge_record(
                    rank=1,
                    edge_id="root.TRUE",
                    risk_score=1.0,
                    statement_lines=[12],
                    raw_statement_lines=[12, 13],
                    sibling_statement_lines=[13],
                    exclusive_statement_lines=[12],
                    removed_shared_statement_lines=[13],
                ),
            ],
        },
    }

    aggregated = aggregate_localization_report(report, source_file="Subject_M1.java")
    item = aggregated["aggregated_interval_rankings"]["edge_divergence_sibling_exclusive"][0]

    assert item["location_basis"] == "statement_lines"
    assert item["statement_lines"] == [12]
    assert item["region_size"] == 1
    assert item["raw_statement_line_variants"] == [[12, 13]]
    assert item["sibling_statement_line_variants"] == [[13]]
    assert item["exclusive_statement_line_variants"] == [[12]]
    assert item["removed_shared_statement_line_variants"] == [[13]]


def test_aggregate_sibling_shared_edges_keeps_shared_region_metadata():
    report = {
        "summary": {},
        "condition_node_ranking": [],
        "interval_rankings": {
            "edge_divergence_sibling_shared": [
                edge_record(
                    rank=1,
                    edge_id="root.TRUE",
                    risk_score=1.0,
                    statement_lines=[13],
                    raw_statement_lines=[12, 13],
                    sibling_statement_lines=[13],
                    shared_statement_lines=[13],
                ),
            ],
        },
    }

    aggregated = aggregate_localization_report(report, source_file="Subject_M1.java")
    item = aggregated["aggregated_interval_rankings"]["edge_divergence_sibling_shared"][0]

    assert item["location_basis"] == "statement_lines"
    assert item["statement_lines"] == [13]
    assert item["region_size"] == 1
    assert item["raw_statement_line_variants"] == [[12, 13]]
    assert item["sibling_statement_line_variants"] == [[13]]
    assert item["shared_statement_line_variants"] == [[13]]


def test_cct_only_aggregation_is_marked_as_condition_anchor_span():
    report = {
        "summary": {},
        "condition_node_ranking": [],
        "interval_rankings": {
            "cct_only": [
                edge_record(
                    rank=1,
                    edge_id="root.FALSE",
                    risk_score=1.0,
                    statement_lines=[],
                    location_basis="condition_anchor_span",
                ),
            ],
        },
    }

    aggregated = aggregate_localization_report(report, source_file="Subject_M1.java")
    item = aggregated["aggregated_interval_rankings"]["cct_only"][0]

    assert item["location_basis"] == "condition_anchor_span"
    assert item["condition_anchor_span"] == [10, 20]
    assert item["region_size"] == 11
    assert item["normalized_anchor_span"] == [10, 20]


def test_aggregate_rejects_unknown_targets():
    report = {"summary": {}, "condition_node_ranking": [], "interval_rankings": {}}

    with pytest.raises(ValueError, match="Unknown aggregation targets"):
        aggregate_localization_report(report, targets=["interval_rankings.missing"])


def test_write_aggregated_localization_report(tmp_path):
    output = tmp_path / "agg.json"
    write_aggregated_localization_report({"summary": {"ok": True}}, output)

    assert json.loads(output.read_text(encoding="utf-8"))["summary"]["ok"]


def test_failure_localization_aggregate_tool_smoke(tmp_path):
    report = {
        "summary": {},
        "condition_node_ranking": [],
        "interval_rankings": {
            "edge_divergence_gated": [
                edge_record(
                    rank=1,
                    edge_id="root.TRUE",
                    risk_score=1.0,
                    statement_lines=[12],
                ),
            ],
        },
    }
    report_path = tmp_path / "cct_failure_localization.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    output_path = tmp_path / "aggregated.json"
    tool_path = os.path.join(os.path.dirname(__file__), "..", "failure_localization_aggregate_tool.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--report",
            str(report_path),
            "--output",
            str(output_path),
            "--source-file",
            "Subject_M1.java",
            "--targets",
            "interval_rankings.edge_divergence_gated",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Failure localization aggregation complete" in completed.stdout
    aggregated = json.loads(output_path.read_text(encoding="utf-8"))
    assert aggregated["summary"]["source_file"] == "Subject_M1.java"
    assert aggregated["summary"]["condition_node_count_aggregated"] == 0
    assert len(aggregated["aggregated_interval_rankings"]["edge_divergence_gated"]) == 1


def edge_record(rank,
                edge_id,
                risk_score,
                statement_lines,
                location_basis="statement_lines",
                raw_statement_lines=None,
                sibling_statement_lines=None,
                exclusive_statement_lines=None,
                shared_statement_lines=None,
                removed_shared_statement_lines=None):
    return {
        "rank": rank,
        "edge_id": edge_id,
        "from_line": 10,
        "from_condition": "x > 0",
        "outcome": "TRUE",
        "to_line": 20,
        "to_condition": "y > 0",
        "line_interval": [10, 20],
        "interval_kind": "forward",
        "condition_anchor_span": [10, 20],
        "condition_anchor_kind": "forward",
        "location_basis": location_basis,
        "statement_lines": statement_lines,
        "raw_statement_lines": raw_statement_lines or [],
        "sibling_statement_lines": sibling_statement_lines or [],
        "exclusive_statement_lines": exclusive_statement_lines or [],
        "shared_statement_lines": shared_statement_lines or [],
        "removed_shared_statement_lines": removed_shared_statement_lines or [],
        "statement_line_count": len(statement_lines),
        "risk_score": risk_score,
        "base_risk_score": risk_score,
        "exec_count": 3,
        "fail_count": 2,
        "pass_count": 1,
        "failure_density": 2 / 3,
    }
