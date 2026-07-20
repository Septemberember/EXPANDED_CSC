import os
import json
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csc_engine import (
    CCT,
    Condition,
    ConditionResult,
    FSFUnit,
    VerificationResult,
    annotate_cct_with_failures,
    build_match_formula,
    build_path_context,
    build_verification_formula,
    derive_ct_in,
    derive_wp,
    find_fsf_file,
    load_fsf,
    match_scenario,
    parse_fsf_text,
    parse_trace_jsonl_text,
    verify_record,
    verify_results_file,
    verify_scenario,
    write_report,
)


def test_load_fsf_defaults_to_true_true_when_file_missing(tmp_path):
    units = load_fsf("MissingClass", tmp_path)

    assert units == [FSFUnit(id="default", T="true", D="true")]


def test_parse_fsf_text_single_unit_without_header():
    units = parse_fsf_text(
        """
        T: x > 0
        D: return_value > 0
        """
    )

    assert units == [FSFUnit(id="fsf_1", T="x > 0", D="return_value > 0")]


def test_parse_fsf_text_multiple_units_with_headers_and_comments():
    units = parse_fsf_text(
        """
        # positive inputs
        [positive]
        T: x > 0
        D: return_value > 0

        [non_positive]
        T: x <= 0
        D: return_value >= 0
        """
    )

    assert units == [
        FSFUnit(id="positive", T="x > 0", D="return_value > 0"),
        FSFUnit(id="non_positive", T="x <= 0", D="return_value >= 0"),
    ]


def test_parse_fsf_text_normalizes_empty_expressions_to_true():
    units = parse_fsf_text(
        """
        [defaultish]
        T:
        D:
        """
    )

    assert units == [FSFUnit(id="defaultish", T="true", D="true")]


def test_load_fsf_reads_class_named_file(tmp_path):
    fsf_file = tmp_path / "Try1_FSF.txt"
    fsf_file.write_text("T: x >= 0\nD: return_value >= 0\n", encoding="utf-8")

    assert load_fsf("Try1", tmp_path) == [
        FSFUnit(id="fsf_1", T="x >= 0", D="return_value >= 0")
    ]


def test_load_fsf_accepts_lowercase_suffix(tmp_path):
    fsf_file = tmp_path / "Try1_fsf.txt"
    fsf_file.write_text("T: x >= 0\nD: return_value >= 0\n", encoding="utf-8")

    assert find_fsf_file("Try1", tmp_path) == fsf_file
    assert load_fsf("Try1", tmp_path) == [
        FSFUnit(id="fsf_1", T="x >= 0", D="return_value >= 0")
    ]


def test_parse_fsf_text_rejects_malformed_unit():
    with pytest.raises(ValueError, match="both T and D"):
        parse_fsf_text(
            """
            [broken]
            T: x > 0
            """
        )


def test_parse_fsf_text_rejects_unknown_lines():
    with pytest.raises(ValueError, match="Malformed FSF line"):
        parse_fsf_text("x > 0\n")


def test_derive_ct_in_uses_structured_trace_conditions():
    events = parse_trace_jsonl_text(
        '{"type":"ASSIGN","line":5,"kind":"var_decl","target":"i","rhs":"n / 2","value":"3"}\n'
        '{"type":"COND","line":6,"kind":"while","order":1,"expr":"i > 1","value":true}\n'
        '{"type":"ASSIGN","line":7,"kind":"assign","target":"i","rhs":"i - 1","value":"2"}\n'
        '{"type":"COND","line":6,"kind":"while","order":1,"expr":"i > 1","value":false}\n'
    )

    assert derive_ct_in(events, ["n"]) == "((n / 2) > 1) && !(((n / 2) - 1) > 1)"


def test_derive_wp_rewrites_return_value_and_assignments():
    events = parse_trace_jsonl_text(
        '{"type":"ASSIGN","line":5,"kind":"var_decl","target":"y","rhs":"x + 1","value":"4"}\n'
        '{"type":"RETURN","line":6,"target":"return_value","rhs":"y","value":"4"}\n'
    )

    assert derive_wp("return_value > 3", events, ["x"]) == "((x + 1)) > 3"


def test_derive_wp_ignores_conditions_because_ct_in_is_separate():
    events = parse_trace_jsonl_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"x","value":"5"}\n'
    )

    assert derive_wp("return_value >= 0", events, ["x"]) == "(x) >= 0"


def test_build_match_and_verification_formulas_keep_t_and_ct():
    assert build_match_formula("x > 0", "x != 0") == "(x > 0) && (x != 0)"
    assert (
        build_verification_formula("x > 0", "x != 0", "return_value > 0")
        == "(x > 0) && (x != 0) && (!(return_value > 0))"
    )


def test_formula_builders_simplify_true_identity():
    assert build_match_formula("true", "x > 0") == "(x > 0)"
    assert build_match_formula("true", "true") == "true"
    assert build_verification_formula("true", "true", "true") == "(!(true))"


def test_build_path_context_from_trace_record(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n',
        encoding="utf-8",
    )
    record = {"iteration": 2, "trace_path": str(trace)}

    context = build_path_context(record, ["x"])

    assert context.test_case_id == "tc_2"
    assert context.trace_path == str(trace)
    assert context.ct_in == "(x > 0)"
    assert context.condition_count == 1
    assert context.trace_status == "trusted"


def test_match_scenario_uses_t_and_ct_intersection():
    matched = match_scenario("x > 0", "x != 0", {"x": "int"})
    unmatched = match_scenario("x > 0", "x < 0", {"x": "int"})

    assert matched.matched
    assert matched.solver_status == "sat"
    assert not unmatched.matched
    assert unmatched.solver_status == "unsat"


def test_verify_scenario_passes_when_counterexample_is_unsat(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"x","value":"5"}\n',
        encoding="utf-8",
    )
    path = build_path_context({"iteration": 2, "trace_path": str(trace)}, ["x"])
    fsf = FSFUnit(id="positive", T="x > 0", D="return_value >= 0")

    result = verify_scenario(path, fsf, {"x": "int", "return_value": "int"})

    assert result.status == "pass"
    assert result.wp == "(x) >= 0"
    assert result.verification_formula == "(x > 0) && ((x > 0)) && (!((x) >= 0))"


def test_verify_scenario_fails_with_counterexample():
    events = parse_trace_jsonl_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"-1","value":"-1"}\n'
    )
    path = build_path_context_from_events_for_test("tc_bad", events)
    fsf = FSFUnit(id="positive", T="x > 0", D="return_value >= 0")

    result = verify_scenario(path, fsf, {"x": "int", "return_value": "int"})

    assert result.status == "fail"
    assert result.counterexample is not None
    assert int(result.counterexample["x"]) > 0


def test_verify_scenario_skips_unmatched_scenario(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n',
        encoding="utf-8",
    )
    path = build_path_context({"iteration": 2, "trace_path": str(trace)}, ["x"])
    fsf = FSFUnit(id="negative", T="x < 0", D="return_value >= 0")

    result = verify_scenario(path, fsf, {"x": "int", "return_value": "int"})

    assert result.status == "skipped"
    assert result.reason == "scenario_unmatched"


def test_verify_record_skips_records_without_trace():
    results = verify_record(
        {"iteration": 3, "status": "infeasible"},
        [FSFUnit(id="default", T="true", D="true")],
        {"x": "int"},
    )

    assert len(results) == 1
    assert results[0].status == "skipped"
    assert results[0].reason == "missing_trace_path"


def test_verify_results_file_writes_summary_and_report(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"x","value":"5"}\n',
        encoding="utf-8",
    )
    results_json = tmp_path / "results.json"
    results_json.write_text(
        '[{"iteration": 2, "inputs": {"x": "5"}, "trace_path": "%s", "status": "sat"}]'
        % str(trace),
        encoding="utf-8",
    )
    fsf_file = tmp_path / "Sample_FSF.txt"
    fsf_file.write_text("T: x > 0\nD: return_value >= 0\n", encoding="utf-8")

    report = verify_results_file(
        results_json,
        "Sample",
        {"x": "int", "return_value": "int"},
        tmp_path,
    )
    output = tmp_path / "report.json"
    write_report(report, output)

    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 0
    assert report["results"][0]["status"] == "pass"
    assert output.exists()


def test_cct_marks_tbfv_failure_without_changing_csc_leaf():
    cct = CCT()
    cct.add_sequence([
        ConditionResult(
            condition=Condition(1, "x > 0", "x > 0", 1),
            result=True,
        )
    ], "tc_2", test_inputs={"x": "5"})

    assert cct.mark_tbfv_failure(
        "tc_2",
        "positive",
        {"x": 5},
        "(x > 0) && !((x) >= 0)",
        "SAT(T_i && Ct_in && !wp(path, D_i))",
    )
    assert cct.root.right.test_cases == {"tc_2"}
    assert cct.root.right.tbfv_failures["tc_2"][0]["fsf_id"] == "positive"
    assert not cct.mark_tbfv_failure("missing", "positive", {}, "false")


def test_cct_tbfv_fault_dot_is_separate_from_normal_dot():
    cct = CCT()
    cct.add_sequence([
        ConditionResult(
            condition=Condition(1, "x > 0", "x > 0", 1),
            result=True,
        )
    ], "tc_2", test_inputs={"x": 5})
    cct.mark_tbfv_failure("tc_2", "positive", {"x": 5}, "formula")

    normal_dot = cct.to_dot()
    fault_dot = cct.to_tbfv_fault_dot()

    assert "tc_2 FAIL [positive]" not in normal_dot
    assert "tc_2(x=5) FAIL [positive]" in fault_dot
    assert "#ffcdd2" in fault_dot


def test_cct_collect_stats_counts_leaf_categories():
    cct = CCT()
    cct.add_sequence([
        ConditionResult(
            condition=Condition(1, "x > 0", "x > 0", 1),
            result=True,
        )
    ], "tc_2")
    cct.mark_infeasible([
        ConditionResult(
            condition=Condition(1, "x > 0", "x > 0", 1),
            result=False,
        )
    ])
    cct.mark_tbfv_failure("tc_2", "positive", {"x": 5}, "formula")

    stats = cct.collect_stats()

    assert stats["total_nodes"] == 3
    assert stats["internal_nodes"] == 1
    assert stats["leaf_nodes"] == 2
    assert stats["covered_leaves"] == 1
    assert stats["valid_testcases"] == 1
    assert stats["infeasible_leaves"] == 1
    assert stats["tbfv_fault_leaves"] == 1
    assert stats["tbfv_failure_cases"] == 1
    assert stats["tbfv_failure_count"] == 1


def test_annotate_cct_with_failures_persists_metadata_and_fault_view(tmp_path):
    cct = CCT()
    cct.add_sequence([
        ConditionResult(
            condition=Condition(1, "x > 0", "x > 0", 1),
            result=True,
        )
    ], "tc_2")
    cct_path = tmp_path / "Sample_cct.pkl"
    cct.save_to_file(str(cct_path))

    summary = annotate_cct_with_failures(
        cct_path,
        [
            VerificationResult(
                test_case_id="tc_2",
                fsf_id="positive",
                status="fail",
                ct_in="x > 0",
                T="x > 0",
                D="return_value >= 0",
                wp="false",
                verification_formula="x > 0 && !false",
                counterexample={"x": 5},
            )
        ],
        tmp_path,
    )
    loaded = CCT.load_from_file(str(cct_path))

    assert summary["marked"] == 1
    assert loaded.root.right.tbfv_failures["tc_2"][0]["fsf_id"] == "positive"
    assert os.path.exists(summary["fault_dot"])
    assert os.path.exists(summary["tbfv_stats_json"])
    assert os.path.exists(summary["localization_json"])
    assert os.path.exists(summary["localization_dot"])
    assert summary["localization_dot"].endswith("cct_failure_localization_cct_only.dot")
    assert summary["tbfv_stats"]["tbfv_fault_leaves"] == 1
    assert summary["localization_summary"]["failed_cases"] == 1
    assert summary["localization_summary"]["default_interval_strategy"] == "cct_only"


def test_batch_record_id_fallback_uses_branch_idx(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n',
        encoding="utf-8",
    )

    context = build_path_context(
        {
            "iteration": 2,
            "branch_idx": 1,
            "status": "batch_safe",
            "trace_path": str(trace),
        },
        ["x"],
    )

    assert context.test_case_id == "tc_2_b1"


def test_refined_tbfv_tool_cli_writes_report(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"x","value":"5"}\n',
        encoding="utf-8",
    )
    results_json = tmp_path / "results.json"
    results_json.write_text(
        json.dumps([{
            "iteration": 2,
            "inputs": {"x": 5},
            "trace_path": str(trace),
            "status": "sat",
        }]),
        encoding="utf-8",
    )
    fsf_file = tmp_path / "Sample_fsf.txt"
    fsf_file.write_text("T: x > 0\nD: return_value >= 0\n", encoding="utf-8")
    report_path = tmp_path / "report.json"
    tool_path = os.path.join(os.path.dirname(__file__), "..", "refined_tbfv_tool.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            str(results_json),
            "--class",
            "Sample",
            "--fsf",
            str(fsf_file),
            "--var-types",
            "return_value:int,x:int",
            "--output",
            str(report_path),
            "--no-annotate-cct",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 0


def test_refined_tbfv_tool_cli_infers_from_csc_result_dir(tmp_path):
    result_dir = tmp_path / "session" / "Sample"
    trace_dir = result_dir / "traces" / "t2"
    trace_dir.mkdir(parents=True)
    trace = trace_dir / "trace.jsonl"
    trace.write_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"x","value":"5"}\n',
        encoding="utf-8",
    )
    (result_dir / "testcases.json").write_text(
        json.dumps([{
            "iteration": 2,
            "inputs": {"x": 5},
            "trace_path": str(trace),
            "status": "sat",
        }]),
        encoding="utf-8",
    )
    (result_dir / "run_log.jsonl").write_text(
        json.dumps({
            "event": "run_start",
            "classname": "Sample",
            "var_types": {"return_value": "int", "x": "int"},
        }) + "\n",
        encoding="utf-8",
    )
    fsf_file = tmp_path / "Sample_fsf.txt"
    fsf_file.write_text("T: x > 0\nD: return_value >= 0\n", encoding="utf-8")
    tool_path = os.path.join(os.path.dirname(__file__), "..", "refined_tbfv_tool.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--csc-result-dir",
            str(result_dir),
            "--fsf",
            str(fsf_file),
            "--no-annotate-cct",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads((result_dir / "refined_tbfv_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["passed"] == 1
    assert "CSC result:" in completed.stdout


def test_refined_tbfv_tool_cli_writes_localization_report_when_annotating(tmp_path):
    result_dir = tmp_path / "session" / "Sample"
    trace_dir = result_dir / "traces" / "t2"
    trace_dir.mkdir(parents=True)
    trace = trace_dir / "trace.jsonl"
    trace.write_text(
        '{"type":"COND","line":3,"kind":"if","order":1,"expr":"x > 0","value":true}\n'
        '{"type":"RETURN","line":4,"target":"return_value","rhs":"-1","value":"-1"}\n',
        encoding="utf-8",
    )
    (result_dir / "testcases.json").write_text(
        json.dumps([{
            "iteration": 2,
            "inputs": {"x": 5},
            "trace_path": str(trace),
            "status": "sat",
        }]),
        encoding="utf-8",
    )
    (result_dir / "run_log.jsonl").write_text(
        json.dumps({
            "event": "run_start",
            "classname": "Sample",
            "var_types": {"return_value": "int", "x": "int"},
        }) + "\n",
        encoding="utf-8",
    )
    cct = CCT()
    cct.add_sequence([
        ConditionResult(
            condition=Condition(3, "x > 0", "x > 0", 1),
            result=True,
        )
    ], "tc_2")
    cct.save_to_file(str(result_dir / "Sample_cct.pkl"))
    fsf_file = tmp_path / "Sample_fsf.txt"
    fsf_file.write_text("T: x > 0\nD: return_value >= 0\n", encoding="utf-8")
    tool_path = os.path.join(os.path.dirname(__file__), "..", "refined_tbfv_tool.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--csc-result-dir",
            str(result_dir),
            "--fsf",
            str(fsf_file),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Localization:" in completed.stdout
    assert "Risk DOT:" in completed.stdout
    localization = json.loads((result_dir / "cct_failure_localization.json").read_text(encoding="utf-8"))
    assert (result_dir / "cct_failure_localization_statement_presence.dot").exists()
    assert "cct_failure_localization_*.dot" in (result_dir / "render_cct.sh").read_text(encoding="utf-8")
    assert localization["summary"]["failed_cases"] == 1
    assert localization["summary"]["default_interval_strategy"] == "statement_presence"
    assert "statement_presence" in localization["interval_rankings"]
    assert localization["condition_node_ranking"][0]["condition"] == "x > 0"


def build_path_context_from_events_for_test(test_case_id, events):
    from csc_engine import path_condition_from_condition_results, condition_results_from_trace
    from csc_engine.refined_tbfv import PathContext

    condition_results = condition_results_from_trace(events, ["x"])
    return PathContext(
        test_case_id=test_case_id,
        trace_path="<memory>",
        events=events,
        ct_in=path_condition_from_condition_results(condition_results),
        condition_count=len(condition_results),
    )
