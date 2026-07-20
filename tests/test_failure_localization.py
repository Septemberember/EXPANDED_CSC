import json
import math
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csc_engine import (
    CCT,
    Condition,
    ConditionResult,
    INFEASIBLE_MARKER,
    Node,
    RANGE_EXCLUDED_MARKER,
    build_localization_dot,
    build_localization_report,
    build_trace_segment_index,
    localization_dot_filename,
    write_localization_dot,
)


def test_localization_report_is_empty_without_failures():
    cct = CCT()
    a = condition(10, "x > 0")
    cct.add_sequence([ConditionResult(a, False)], "tc_f")
    cct.add_sequence([ConditionResult(a, True)], "tc_t")

    report = build_localization_report(cct)

    assert report["summary"]["executed_cases"] == 2
    assert report["summary"]["failed_cases"] == 0
    assert report["condition_node_ranking"] == []
    assert report["condition_interval_ranking"] == []


def test_localization_ignores_infeasible_and_out_of_range_leaves():
    cct = CCT()
    a = condition(10, "x > 0")
    cct.add_sequence([ConditionResult(a, True)], "tc_pass")
    cct.mark_tbfv_failure("tc_pass", "default", {}, "formula")
    cct.root.left = Node(INFEASIBLE_MARKER, is_leaf=True)
    cct.root.left.test_cases = {INFEASIBLE_MARKER}
    cct.root.right = Node("tc_fail", is_leaf=True)
    cct.root.right.tbfv_failures = {"tc_fail": [{"fsf_id": "default"}]}
    cct.root.left = Node(RANGE_EXCLUDED_MARKER, is_leaf=True)
    cct.root.left.test_cases = {RANGE_EXCLUDED_MARKER}

    report = build_localization_report(cct)

    assert report["summary"]["executed_cases"] == 1
    assert report["summary"]["failed_cases"] == 1
    assert report["summary"]["ignored"]["out_of_range_leaves"] == 1
    assert report["condition_node_ranking"][0]["failure_density"] == 1.0


def test_condition_node_ranking_uses_density_and_failure_support():
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1", "tc_rt2", "tc_rt3", "tc_rt4", "tc_rt5", "tc_lf")

    report = build_localization_report(cct)
    ranking = report["condition_node_ranking"]

    assert ranking[0]["condition"] == "z == 0"
    assert ranking[0]["fail_count"] == 5
    assert ranking[0]["exec_count"] == 6
    assert ranking[1]["condition"] == "x > 0"
    assert ranking[2]["condition"] == "y > 0"


def test_failed_subtree_pruning_excludes_pass_only_conditions():
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1")

    report = build_localization_report(cct)
    ranked_conditions = [record["condition"] for record in report["condition_node_ranking"]]

    assert "x > 0" in ranked_conditions
    assert "z == 0" in ranked_conditions
    assert "y > 0" not in ranked_conditions


def test_interval_ranking_scores_each_failed_child_edge():
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1", "tc_rt2", "tc_rt3", "tc_rt4", "tc_rt5", "tc_lf")

    report = build_localization_report(cct)
    intervals = report["condition_interval_ranking"]
    root_true_edge = next(record for record in intervals if record["edge_id"] == "root.TRUE")
    root_false_edge = next(record for record in intervals if record["edge_id"] == "root.FALSE")

    assert root_true_edge["line_interval"] == [10, 30]
    assert root_true_edge["failure_density"] == pytest.approx(5 / 6)
    assert root_true_edge["outcome_delta"] > root_false_edge["outcome_delta"]
    assert root_true_edge["risk_score"] > root_false_edge["risk_score"]


def test_interval_rankings_keep_cct_only_strategy_for_compatibility():
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1", "tc_rt2")

    report = build_localization_report(cct)

    assert report["summary"]["default_interval_strategy"] == "cct_only"
    assert report["summary"]["available_interval_strategies"] == ["cct_only"]
    assert report["condition_interval_ranking"] == report["interval_rankings"]["cct_only"]
    assert report["condition_interval_ranking"][0]["base_risk_score"] == (
        report["condition_interval_ranking"][0]["risk_score"]
    )


def test_statement_presence_strategy_zeros_edges_without_statement_segments(tmp_path):
    cct = CCT()
    a = condition(10, "a")
    b = condition(20, "b")
    cct.add_sequence([ConditionResult(a, False), ConditionResult(b, True)], "tc_f")
    cct.add_sequence([ConditionResult(a, True)], "tc_t")
    mark_failures(cct, "tc_f", "tc_t")
    trace_f = write_trace(
        tmp_path,
        "tf",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":false}\n'
        '{"type":"COND","line":20,"kind":"if","order":1,"expr":"b","value":true}\n'
        '{"type":"RETURN","line":21,"target":"return_value","rhs":"0","value":"0"}\n',
    )
    trace_t = write_trace(
        tmp_path,
        "tt",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"ASSIGN","line":12,"kind":"assign","target":"x","rhs":"x + 1","value":"2"}\n'
        '{"type":"RETURN","line":13,"target":"return_value","rhs":"x","value":"2"}\n',
    )

    report = build_localization_report(
        cct,
        testcase_records=[{"trace_path": str(trace_f)}, {"trace_path": str(trace_t)}],
    )
    cct_only = {record["edge_id"]: record for record in report["interval_rankings"]["cct_only"]}
    statement = {record["edge_id"]: record for record in report["interval_rankings"]["statement_presence"]}
    seed = {
        record["edge_id"]: record
        for record in report["interval_rankings"]["edge_divergence_sibling_exclusive"]
    }

    assert report["summary"]["default_interval_strategy"] == "statement_presence"
    assert report["condition_interval_ranking"] == report["interval_rankings"]["statement_presence"]
    assert report["summary"]["statement_aware_intervals"]
    assert "edge_divergence_gated" not in report["interval_rankings"]
    assert report["summary"]["available_interval_strategies"] == [
        "cct_only",
        "statement_presence",
        "edge_divergence_sibling_exclusive",
        "edge_divergence_sibling_shared",
    ]
    assert cct_only["root.FALSE"]["risk_score"] > 0
    assert cct_only["root.FALSE"]["location_basis"] == "condition_anchor_span"
    assert cct_only["root.FALSE"]["condition_anchor_span"] == [10, 20]
    assert statement["root.FALSE"]["statement_count"] == 0
    assert statement["root.FALSE"]["location_basis"] == "statement_lines"
    assert statement["root.FALSE"]["risk_score"] == 0
    assert statement["root.TRUE"]["statement_count"] == 2
    assert statement["root.TRUE"]["statement_lines"] == [12, 13]
    assert statement["root.TRUE"]["region_size"] == 2
    assert statement["root.TRUE"]["risk_score"] == statement["root.TRUE"]["base_risk_score"]
    assert seed["root.TRUE"]["raw_statement_lines"] == [12, 13]
    assert seed["root.TRUE"]["sibling_statement_lines"] == []
    assert seed["root.TRUE"]["statement_lines"] == [12, 13]


def test_edge_divergence_gated_weights_distinct_statement_lines(tmp_path):
    cct = CCT()
    a = condition(10, "a")
    cct.add_sequence([ConditionResult(a, True)], "tc_t")
    mark_failures(cct, "tc_t")
    trace_t = write_trace(
        tmp_path,
        "tt",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"ASSIGN","line":12,"kind":"assign","target":"x","rhs":"x + 1","value":"2"}\n'
        '{"type":"ASSIGN","line":12,"kind":"assign","target":"x","rhs":"x + 1","value":"3"}\n'
        '{"type":"RETURN","line":13,"target":"return_value","rhs":"x","value":"3"}\n',
    )

    report = build_localization_report(
        cct,
        testcase_records=[{"trace_path": str(trace_t)}],
        interval_strategies=["edge_divergence_gated"],
        default_interval_strategy="edge_divergence_gated",
    )
    edge = report["condition_interval_ranking"][0]

    assert edge["edge_id"] == "root.TRUE"
    assert edge["statement_count"] == 3
    assert edge["statement_line_count"] == 2
    assert edge["region_size"] == 2
    assert edge["base_interval_score"] == pytest.approx(math.log10(2))
    assert edge["base_risk_score"] == pytest.approx(2 * math.log10(2))
    assert edge["statement_line_weight"] == pytest.approx(1 + math.log10(3))
    assert edge["risk_score"] == pytest.approx(edge["base_risk_score"] * (1 + math.log10(3)))


def test_sibling_exclusive_strategy_removes_shared_sibling_statement_lines(tmp_path):
    cct = CCT()
    a = condition(10, "a")
    cct.add_sequence([ConditionResult(a, True)], "tc_t")
    cct.add_sequence([ConditionResult(a, False)], "tc_f")
    mark_failures(cct, "tc_t")
    trace_t = write_trace(
        tmp_path,
        "tt",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"ASSIGN","line":12,"kind":"assign","target":"x","rhs":"1","value":"1"}\n'
        '{"type":"ASSIGN","line":13,"kind":"assign","target":"i","rhs":"i + 1","value":"2"}\n',
    )
    trace_f = write_trace(
        tmp_path,
        "tf",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":false}\n'
        '{"type":"ASSIGN","line":13,"kind":"assign","target":"i","rhs":"i + 1","value":"2"}\n',
    )

    report = build_localization_report(
        cct,
        testcase_records=[{"trace_path": str(trace_t)}, {"trace_path": str(trace_f)}],
        default_interval_strategy="edge_divergence_sibling_exclusive",
    )
    edge = report["condition_interval_ranking"][0]

    assert report["summary"]["default_interval_strategy"] == "edge_divergence_sibling_exclusive"
    assert "edge_divergence_sibling_exclusive" in report["summary"]["available_interval_strategies"]
    assert edge["edge_id"] == "root.TRUE"
    assert edge["raw_statement_lines"] == [12, 13]
    assert edge["sibling_statement_lines"] == [13]
    assert edge["removed_shared_statement_lines"] == [13]
    assert edge["exclusive_statement_lines"] == [12]
    assert edge["statement_lines"] == [12]
    assert edge["region_size"] == 1
    assert edge["statement_line_weight"] == pytest.approx(1 + math.log10(2))
    assert edge["risk_score"] == pytest.approx(edge["base_risk_score"])


def test_sibling_shared_strategy_scores_shared_statement_lines_with_parent_density(tmp_path):
    cct = CCT()
    a = condition(10, "a")
    cct.add_sequence([ConditionResult(a, True)], "tc_t")
    cct.add_sequence([ConditionResult(a, False)], "tc_f")
    mark_failures(cct, "tc_t")
    trace_t = write_trace(
        tmp_path,
        "tt",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"ASSIGN","line":12,"kind":"assign","target":"x","rhs":"1","value":"1"}\n'
        '{"type":"ASSIGN","line":13,"kind":"assign","target":"i","rhs":"i + 1","value":"2"}\n',
    )
    trace_f = write_trace(
        tmp_path,
        "tf",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":false}\n'
        '{"type":"ASSIGN","line":13,"kind":"assign","target":"i","rhs":"i + 1","value":"2"}\n',
    )

    report = build_localization_report(
        cct,
        testcase_records=[{"trace_path": str(trace_t)}, {"trace_path": str(trace_f)}],
        default_interval_strategy="edge_divergence_sibling_shared",
    )
    edge = report["condition_interval_ranking"][0]

    expected_shared_score = 0.5 * math.log10(2) * (2 - 1)
    assert report["summary"]["default_interval_strategy"] == "edge_divergence_sibling_shared"
    assert edge["edge_id"] == "root.TRUE"
    assert edge["raw_statement_lines"] == [12, 13]
    assert edge["sibling_statement_lines"] == [13]
    assert edge["shared_statement_lines"] == [13]
    assert edge["statement_lines"] == [13]
    assert edge["parent_exec_count"] == 2
    assert edge["parent_fail_count"] == 1
    assert edge["parent_failure_density"] == pytest.approx(0.5)
    assert edge["statement_line_weight"] == pytest.approx(1 + math.log10(2))
    assert edge["shared_risk_score"] == pytest.approx(expected_shared_score)
    assert edge["risk_score"] == pytest.approx(expected_shared_score)


def test_statement_presence_strategy_requires_testcase_records():
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1")

    with pytest.raises(ValueError, match="requires testcase records"):
        build_localization_report(
            cct,
            interval_strategies=["statement_presence"],
        )

    with pytest.raises(ValueError, match="requires testcase records"):
        build_localization_report(
            cct,
            interval_strategies=["edge_divergence_gated"],
        )

    with pytest.raises(ValueError, match="requires testcase records"):
        build_localization_report(
            cct,
            interval_strategies=["edge_divergence_sibling_exclusive"],
        )

    with pytest.raises(ValueError, match="requires testcase records"):
        build_localization_report(
            cct,
            interval_strategies=["edge_divergence_sibling_shared"],
        )


def test_interval_score_keeps_base_risk_when_sibling_is_also_risky():
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1", "tc_rt2", "tc_rt3", "tc_rt4", "tc_rt5", "tc_lf")

    report = build_localization_report(cct)
    edge = next(record for record in report["condition_interval_ranking"]
                if record["edge_id"] == "root.TRUE")

    assert edge["failure_density"] == pytest.approx(5 / 6)
    assert edge["sibling_failure_density"] == 0.5
    assert edge["outcome_delta"] == pytest.approx(1 / 3)
    assert edge["base_interval_score"] > 0
    assert edge["risk_score"] > edge["base_interval_score"]


def test_interval_reports_loop_or_backward_line_ranges():
    cct = CCT()
    a = condition(40, "i > 0", loop_count=2)
    b = condition(20, "x > 0")
    cct.add_sequence([ConditionResult(a, True), ConditionResult(b, True)], "tc_loop")
    cct.mark_tbfv_failure("tc_loop", "default", {}, "formula")

    report = build_localization_report(cct)
    edge = next(record for record in report["condition_interval_ranking"]
                if record["edge_id"] == "root.TRUE")

    assert edge["line_interval"] == [20, 40]
    assert edge["interval_kind"] == "backward_or_loop"


def test_interval_reports_leaf_edges_without_end_line():
    cct = CCT()
    a = condition(10, "x > 0")
    cct.add_sequence([ConditionResult(a, True)], "tc_t")
    cct.mark_tbfv_failure("tc_t", "default", {}, "formula")

    report = build_localization_report(cct)
    edge = report["condition_interval_ranking"][0]

    assert edge["edge_id"] == "root.TRUE"
    assert edge["line_interval"] == [10, None]
    assert edge["interval_kind"] == "to_leaf"


def test_top_k_truncates_rankings_but_keeps_total_candidate_counts():
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1", "tc_rt2", "tc_rt3", "tc_rt4", "tc_lf")

    report = build_localization_report(cct, top_k=1)

    assert len(report["condition_node_ranking"]) == 1
    assert len(report["condition_interval_ranking"]) == 1
    assert report["summary"]["condition_node_candidates"] == 3
    assert report["summary"]["condition_interval_candidates"] == 4


def test_localization_dot_marks_risky_nodes_and_edges():
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1", "tc_rt2", "tc_rt3", "tc_rt4", "tc_rt5", "tc_lf")
    report = build_localization_report(cct)

    dot = build_localization_dot(cct, report)

    assert "CCT_Failure_Localization" in dot
    assert "rank #1 score=" in dot
    assert "fail=5/6" in dot
    assert "root.TRUE" not in dot
    assert "style=\"bold\"" in dot or "style=\"bold,dashed\"" in dot
    assert "fillcolor=\"#ffcdd2\"" in dot
    assert r"\\n" not in dot
    assert r"\nL" in dot
    assert r"\nrank #" in dot


def test_localization_dot_renders_tbfv_failure_leaf_label_with_line_break():
    cct = CCT()
    a = condition(10, "x > 0")
    cct.add_sequence([ConditionResult(a, True)], "tc_fail")
    mark_failures(cct, "tc_fail")
    report = build_localization_report(cct)

    dot = build_localization_dot(cct, report)

    assert r"\\n" not in dot
    assert r"tc_fail\nTBFV FAIL" in dot


def test_localization_dot_can_select_interval_strategy(tmp_path):
    cct = CCT()
    a = condition(10, "a")
    b = condition(20, "b")
    cct.add_sequence([ConditionResult(a, False), ConditionResult(b, True)], "tc_f")
    cct.add_sequence([ConditionResult(a, True)], "tc_t")
    mark_failures(cct, "tc_f", "tc_t")
    trace_f = write_trace(
        tmp_path,
        "tf",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":false}\n'
        '{"type":"COND","line":20,"kind":"if","order":1,"expr":"b","value":true}\n'
        '{"type":"RETURN","line":21,"target":"return_value","rhs":"0","value":"0"}\n',
    )
    trace_t = write_trace(
        tmp_path,
        "tt",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"RETURN","line":13,"target":"return_value","rhs":"x","value":"2"}\n',
    )
    report = build_localization_report(
        cct,
        testcase_records=[{"trace_path": str(trace_f)}, {"trace_path": str(trace_t)}],
        interval_strategies=["cct_only", "statement_presence", "edge_divergence_gated"],
        default_interval_strategy="statement_presence",
    )

    cct_only_dot = build_localization_dot(cct, report, interval_strategy="cct_only")
    statement_dot = build_localization_dot(cct, report, interval_strategy="statement_presence")
    gated_dot = build_localization_dot(cct, report, interval_strategy="edge_divergence_gated")

    assert "Failure localization edge strategy: cct_only" in cct_only_dot
    assert "Failure localization edge strategy: statement_presence" in statement_dot
    assert "Failure localization edge strategy: edge_divergence_gated" in gated_dot
    assert "stmt=0" not in cct_only_dot
    assert "stmt=0" in statement_dot
    assert "LC=" in gated_dot
    assert "lines=13" in statement_dot
    assert "w=" in gated_dot
    assert "score=0.0000" in statement_dot
    assert "base=" in statement_dot
    assert localization_dot_filename("statement_presence") == (
        "cct_failure_localization_statement_presence.dot"
    )
    assert localization_dot_filename("edge_divergence_gated") == (
        "cct_failure_localization_edge_divergence_gated.dot"
    )


def test_write_localization_dot_does_not_mutate_cct(tmp_path):
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1", "tc_rt2")
    report = build_localization_report(cct)
    before = cct.collect_stats()
    dot_path = tmp_path / "cct_failure_localization.dot"

    write_localization_dot(cct, report, dot_path)

    assert dot_path.exists()
    assert "Failure" in dot_path.read_text(encoding="utf-8")
    assert cct.collect_stats() == before


def test_trace_segment_index_counts_zero_statement_condition_transition(tmp_path):
    trace = write_trace(
        tmp_path,
        "t1",
        '{"type":"COND","line":1,"kind":"if","order":1,"expr":"a","value":false}\n'
        '{"type":"COND","line":2,"kind":"if","order":1,"expr":"b","value":true}\n',
    )

    index = build_trace_segment_index([{"trace_path": str(trace)}], {"root.FALSE"})

    assert index["root.FALSE"]["segment_status"] == "matched"
    assert index["root.FALSE"]["statement_count"] == 0
    assert index["root.FALSE"]["statement_line_count"] == 0
    assert index["root.FALSE"]["statement_lines"] == []


def test_trace_segment_index_counts_assignment_between_conditions(tmp_path):
    trace = write_trace(
        tmp_path,
        "t1",
        '{"type":"COND","line":1,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"ASSIGN","line":3,"kind":"assign","target":"x","rhs":"x + 1","value":"2"}\n'
        '{"type":"COND","line":4,"kind":"if","order":1,"expr":"b","value":false}\n',
    )

    index = build_trace_segment_index([{"trace_path": str(trace)}], {"root.TRUE"})

    assert index["root.TRUE"]["statement_count"] == 1
    assert index["root.TRUE"]["assignment_count"] == 1
    assert index["root.TRUE"]["return_count"] == 0
    assert index["root.TRUE"]["statement_lines"] == [3]
    assert index["root.TRUE"]["sample_events"][0]["rhs"] == "x + 1"


def test_trace_segment_index_counts_assignment_and_return_to_leaf(tmp_path):
    trace = write_trace(
        tmp_path,
        "t1",
        '{"type":"COND","line":1,"kind":"if","order":1,"expr":"a","value":false}\n'
        '{"type":"ASSIGN","line":3,"kind":"assign","target":"sum","rhs":"sum - 1","value":"-1"}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"sum","value":"-1"}\n',
    )

    index = build_trace_segment_index([{"trace_path": str(trace)}], {"root.FALSE"})

    assert index["root.FALSE"]["statement_count"] == 2
    assert index["root.FALSE"]["assignment_count"] == 1
    assert index["root.FALSE"]["return_count"] == 1
    assert index["root.FALSE"]["statement_lines"] == [3, 4]


def test_trace_segment_index_only_records_candidate_edges(tmp_path):
    trace = write_trace(
        tmp_path,
        "t1",
        '{"type":"COND","line":1,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"ASSIGN","line":3,"kind":"assign","target":"x","rhs":"x + 1","value":"2"}\n'
        '{"type":"COND","line":4,"kind":"if","order":1,"expr":"b","value":false}\n',
    )

    index = build_trace_segment_index([{"trace_path": str(trace)}], {"root.FALSE"})

    assert index["root.FALSE"]["segment_status"] == "unmatched"
    assert "root.TRUE" not in index


def test_trace_segment_index_stops_after_pending_edges_are_matched(tmp_path):
    first = write_trace(
        tmp_path,
        "t1",
        '{"type":"COND","line":1,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"ASSIGN","line":3,"kind":"assign","target":"x","rhs":"x + 1","value":"2"}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"x","value":"2"}\n',
    )
    second = tmp_path / "missing" / "trace.jsonl"

    index = build_trace_segment_index(
        [{"trace_path": str(first)}, {"trace_path": str(second)}],
        {"root.TRUE"},
    )

    assert index["root.TRUE"]["segment_status"] == "matched"


def test_failure_localization_tool_reads_csc_result_dir(tmp_path):
    result_dir = tmp_path / "Sample"
    result_dir.mkdir()
    cct = two_level_tree()
    mark_failures(cct, "tc_rt1", "tc_rt2")
    cct.save_to_file(str(result_dir / "Sample_cct.pkl"))
    (result_dir / "run_log.jsonl").write_text(
        json.dumps({"event": "run_start", "classname": "Sample"}) + "\n",
        encoding="utf-8",
    )
    tool_path = os.path.join(os.path.dirname(__file__), "..", "failure_localization_tool.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--csc-result-dir",
            str(result_dir),
            "--top-k",
            "1",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Failure localization complete" in completed.stdout
    assert "Risk DOT:" in completed.stdout
    report = json.loads((result_dir / "cct_failure_localization.json").read_text(encoding="utf-8"))
    assert (result_dir / "cct_failure_localization_cct_only.dot").exists()
    assert len(report["condition_node_ranking"]) == 1
    assert report["summary"]["default_interval_strategy"] == "cct_only"
    assert report["summary"]["condition_node_candidates"] > 1


def test_failure_localization_tool_defaults_to_statement_presence_with_result_records(tmp_path):
    result_dir = tmp_path / "Sample"
    result_dir.mkdir()
    cct = CCT()
    a = condition(10, "a")
    cct.add_sequence([ConditionResult(a, True)], "tc_2")
    mark_failures(cct, "tc_2")
    cct.save_to_file(str(result_dir / "Sample_cct.pkl"))
    trace = write_trace(
        tmp_path,
        "t2",
        '{"type":"COND","line":10,"kind":"if","order":1,"expr":"a","value":true}\n'
        '{"type":"RETURN","line":11,"target":"return_value","rhs":"0","value":"0"}\n',
    )
    (result_dir / "testcases.json").write_text(
        json.dumps([{
            "iteration": 2,
            "trace_path": str(trace),
            "status": "sat",
        }]),
        encoding="utf-8",
    )
    tool_path = os.path.join(os.path.dirname(__file__), "..", "failure_localization_tool.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--csc-result-dir",
            str(result_dir),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads((result_dir / "cct_failure_localization.json").read_text(encoding="utf-8"))
    assert report["summary"]["default_interval_strategy"] == "statement_presence"
    assert (result_dir / "cct_failure_localization_statement_presence.dot").exists()
    assert "Edge strategy: statement_presence" in completed.stdout


def test_failure_localization_tool_can_list_strategies():
    tool_path = os.path.join(os.path.dirname(__file__), "..", "failure_localization_tool.py")

    completed = subprocess.run(
        [sys.executable, tool_path, "--list-strategies"],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "cct_only" in completed.stdout
    assert "statement_presence" in completed.stdout
    assert "edge_divergence_gated" in completed.stdout
    assert "Edge-level Divergence and Gated Evaluation" in completed.stdout


def condition(line, expr, input_constraint=None, loop_count=1):
    return Condition(line, expr, input_constraint or expr, loop_count)


def two_level_tree():
    cct = CCT()
    a = condition(10, "x > 0")
    b = condition(20, "y > 0")
    c = condition(30, "z == 0")
    cct.add_sequence([ConditionResult(a, False), ConditionResult(b, False)], "tc_lf")
    cct.add_sequence([ConditionResult(a, False), ConditionResult(b, True)], "tc_lt")
    cct.add_sequence([ConditionResult(a, True), ConditionResult(c, False)], "tc_rf")
    for index in range(1, 6):
        cct.add_sequence(
            [ConditionResult(a, True), ConditionResult(c, True)],
            f"tc_rt{index}",
        )
    return cct


def mark_failures(cct, *test_case_ids):
    for test_case_id in test_case_ids:
        assert cct.mark_tbfv_failure(test_case_id, "default", {}, "formula")


def write_trace(tmp_path, name, text):
    trace_dir = tmp_path / name
    trace_dir.mkdir()
    trace = trace_dir / "trace.jsonl"
    trace.write_text(text, encoding="utf-8")
    return trace
