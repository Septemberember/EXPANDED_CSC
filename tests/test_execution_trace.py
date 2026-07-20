import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csc_engine import (
    condition_results_from_trace,
    path_condition_from_trace,
    parse_trace_jsonl_text,
    update_expr_with_trace,
)


def test_parse_trace_jsonl_text():
    events = parse_trace_jsonl_text(
        '{"type":"INPUT","line":1,"name":"n","javaType":"int","value":"6"}\n'
        '{"type":"COND","line":7,"kind":"if","order":1,"expr":"n % i == 0","value":true}\n'
    )

    assert len(events) == 2
    assert events[0].type == "INPUT"
    assert events[0].java_type == "int"
    assert events[1].type == "COND"
    assert events[1].expr == "n % i == 0"
    assert events[1].value is True


def test_condition_results_from_trace_with_loop_counts_and_lines():
    events = parse_trace_jsonl_text(
        '{"type":"COND","line":6,"kind":"while","order":1,"expr":"i > 1","value":true}\n'
        '{"type":"COND","line":7,"kind":"if","order":1,"expr":"n % i == 0","value":false}\n'
        '{"type":"COND","line":6,"kind":"while","order":1,"expr":"i > 1","value":false}\n'
    )

    results = condition_results_from_trace(events)

    assert len(results) == 3
    assert results[0].condition.line_number == 6
    assert results[0].condition.condition_string == "i > 1"
    assert results[0].condition.loop_count == 1
    assert results[0].result is True
    assert results[1].condition.line_number == 7
    assert results[1].result is False
    assert results[2].condition.line_number == 6
    assert results[2].condition.loop_count == 2
    assert results[2].result is False


def test_update_expr_with_trace_uses_source_rhs_not_runtime_value():
    events = parse_trace_jsonl_text(
        '{"type":"INPUT","line":1,"name":"n","javaType":"int","value":"6"}\n'
        '{"type":"ASSIGN","line":5,"kind":"var_decl","target":"i","rhs":"n / 2","value":"3"}\n'
        '{"type":"COND","line":6,"kind":"while","order":1,"expr":"i > 1","value":true}\n'
    )

    updated = update_expr_with_trace("i > 1", events[:2])

    assert updated == "(n / 2) > 1"


def test_condition_results_from_trace_derives_input_constraint():
    events = parse_trace_jsonl_text(
        '{"type":"ASSIGN","line":5,"kind":"var_decl","target":"i","rhs":"n / 2","value":"3"}\n'
        '{"type":"COND","line":7,"kind":"if","order":1,"expr":"n % i == 0","value":true}\n'
    )

    results = condition_results_from_trace(events)

    assert len(results) == 1
    assert results[0].condition.input_constraint == "n % (n / 2) == 0"


def test_path_condition_from_trace_uses_atomic_condition_results():
    events = parse_trace_jsonl_text(
        '{"type":"ASSIGN","line":5,"kind":"var_decl","target":"i","rhs":"n / 2","value":"2"}\n'
        '{"type":"COND","line":6,"kind":"while","order":1,"expr":"i > 1","value":true}\n'
        '{"type":"COND","line":7,"kind":"if","order":1,"expr":"n % i == 0","value":false}\n'
    )

    assert path_condition_from_trace(events) == "((n / 2) > 1) && !(n % (n / 2) == 0)"
