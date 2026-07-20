"""
CSC Engine Test Suite — ported from csc_expanded.py.

Tests the core CCT data structure, CSC algorithms, expansion features,
and integration with real Java execution traces.
"""

import os
import sys
import tempfile
import subprocess
import pickle

# Add parent dir to path so we can import csc_engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csc_engine import (
    CCT, Node, Condition, ConditionResult, Result, INFEASIBLE_MARKER,
    RANGE_EXCLUDED_MARKER,
    CCT_NOT_INITIALIZED, parse_path_info,
    solver_check_z3, java_expr_to_z3,
    add_value_constraints, batch_discover, batch_verify_and_merge,
)


def _make_condition(cond_str, input_constraint="", loop_count=1):
    return Condition(line_number=1, condition_string=cond_str,
                     input_constraint=input_constraint if input_constraint else cond_str,
                     loop_count=loop_count)


def _make_cr(cond_str, result, constraint="", loop_count=1):
    return ConditionResult(
        condition=_make_condition(cond_str, constraint, loop_count),
        result=result)


# ===========================================================================
# Test 1: Basic CCT Construction
# ===========================================================================

def test_basic_cct_construction():
    cct = CCT()
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "!(n <= 1) && (n/2 > 1)"),
    ]
    cct.add_sequence(path1, "tc_0")
    path2 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", False, "!(n <= 1) && !(n/2 > 1)"),
    ]
    cct.add_sequence(path2, "tc_1")
    assert cct.root is not None
    assert cct.root.left is not None
    inner = cct.root.left
    assert not inner.is_leaf
    assert inner.left is not None
    assert inner.right is not None


def test_condition_identity_includes_line_number():
    c1 = Condition(line_number=10, condition_string="x > 0",
                   input_constraint="x > 0", loop_count=1)
    c2 = Condition(line_number=20, condition_string="x > 0",
                   input_constraint="x > 0", loop_count=1)

    assert c1 != c2
    assert len({c1, c2}) == 2


# ===========================================================================
# Test 2: Ancestor Check
# ===========================================================================

def test_ancestor_check_simple():
    cct = CCT()
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "!(n <= 1) && (n/2 > 1)"),
    ]
    cct.add_sequence(path1, "tc_0")
    path_to_node = [_make_cr("n <= 1", False, "!(n <= 1)")]
    result = cct._has_ancestor_with_same_condition(path_to_node, "i > 1", is_right_branch=True)
    assert not result, "Should NOT find matching ancestor"

    path2 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "!(n <= 1) && (n/2 > 1)"),
        _make_cr("n % i == 0", True, "!(n <= 1) && (n/2 > 1) && (n/2 | n)"),
        _make_cr("i > 1", True, "...", loop_count=2),
    ]
    cct.add_sequence(path2, "tc_2")
    path_to_deep = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "!(n <= 1) && (n/2 > 1)"),
        _make_cr("n % i == 0", True, "!(n <= 1) && (n/2 > 1) && (n/2 | n)"),
    ]
    result = cct._has_ancestor_with_same_condition(path_to_deep, "i > 1", is_right_branch=True)
    assert result, "Should find matching ancestor"


# ===========================================================================
# Test 3: check_for_csc — No Ancestor
# ===========================================================================

def test_check_for_csc_no_ancestor():
    cct = CCT()
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "i > 1"),
    ]
    cct.add_sequence(path1, "tc_0")
    result = cct.check_for_csc()
    assert result is not None, "Should find uncovered branch"
    assert len(result) == 2
    assert result[-1].condition.condition_string == "i > 1"
    assert result[-1].result == False


# ===========================================================================
# Test 4: check_for_csc — Ancestor Match (Original CSC)
# ===========================================================================

def test_check_for_csc_with_ancestor_original():
    cct = CCT(use_bounded_range=False)
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "i > 1"),
        _make_cr("n % i == 0", False, "!(n % i == 0)"),
        _make_cr("i > 1", True, "...", loop_count=2),
    ]
    cct.add_sequence(path1, "tc_0")
    result = cct.check_for_csc()
    assert result is not None, "Should find uncovered branch"
    assert result[-1].condition.condition_string == "i > 1"
    assert result[-1].result == False

    path2 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", False, "!(i > 1)"),
    ]
    cct.add_sequence(path2, "tc_2")
    result = cct.check_for_csc()
    assert result is not None
    assert result[-1].condition.condition_string == "n % i == 0"
    assert result[-1].result == True

    path3 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "i > 1"),
        _make_cr("n % i == 0", True, "n % i == 0"),
    ]
    cct.add_sequence(path3, "tc_3")
    result = cct.check_for_csc()
    assert result is not None
    assert result[-1].condition.condition_string == "n <= 1"
    assert result[-1].result == True

    path4 = [_make_cr("n <= 1", True, "n <= 1")]
    cct.add_sequence(path4, "tc_4")
    result = cct.check_for_csc()
    assert result is None, "CCT should be FULL"


def test_check_for_csc_continues_after_skipped_sibling():
    cct = CCT()
    cct.root = Node(_make_condition("x > 0"), is_leaf=False)
    calls = []

    def handle(node, sequence, is_right_branch, var_types):
        calls.append(is_right_branch)
        if not is_right_branch:
            return None
        return sequence + [ConditionResult(node.condition, True)]

    cct._handle_uncovered_branch = handle
    result = cct.check_for_csc()

    assert calls == [False, True]
    assert result is not None
    assert result[-1].result is True


# ===========================================================================
# Test 5: Truncated Leaf Detection
# ===========================================================================

def test_truncated_leaf_detection():
    cct = CCT()
    path1 = [
        _make_cr("x >= 0", True, "x >= 0"),
        _make_cr("x > 10", True, "x > 10"),
        _make_cr("x >= 0", True, "...", loop_count=2),
        _make_cr("x > 10", True, "...", loop_count=2),
        _make_cr("x >= 0", True, "...", loop_count=3),
    ]
    cct.add_sequence(path1, "tc_0")
    root = cct.root
    assert root is not None
    inner3 = root.right.right.right
    truncated_leaf = inner3.right
    assert cct._is_truncated_leaf(truncated_leaf)
    assert not cct._is_infeasible_leaf(truncated_leaf)
    assert truncated_leaf.truncated_remainder is not None
    assert len(truncated_leaf.truncated_remainder) == 1


# ===========================================================================
# Test 6: Truncated Leaf Promotion
# ===========================================================================

def test_truncated_leaf_promotion():
    cct = CCT()
    path1 = [
        _make_cr("x >= 0", True, "x >= 0"),
        _make_cr("x > 10", True, "x > 10"),
        _make_cr("x >= 0", True, "...", loop_count=2),
        _make_cr("x > 10", True, "...", loop_count=2),
        _make_cr("x >= 0", True, "...", loop_count=3),
    ]
    cct.add_sequence(path1, "tc_0")
    root = cct.root
    inner3 = root.right.right.right
    truncated_leaf = inner3.right
    assert cct._is_truncated_leaf(truncated_leaf)
    cct._promote_truncated_leaf(inner3, is_right_child=True)
    new_internal = inner3.right
    assert not new_internal.is_leaf
    assert new_internal.is_expanded
    assert new_internal.condition.condition_string == "x >= 0"
    assert new_internal.condition.loop_count == 3
    assert new_internal.right is not None
    assert new_internal.right.is_leaf
    assert "tc_0" in (new_internal.right.test_cases or set())
    assert new_internal.left is None


# ===========================================================================
# Test 7: Backward Compat Pickle
# ===========================================================================

def test_backward_compat_pickle():
    cct1 = CCT(use_bounded_range=True, range_bound=100)
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "i > 1"),
    ]
    cct1.add_sequence(path1, "tc_0")

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        tmpfile = f.name
    try:
        cct1.save_to_file(tmpfile)
        assert hasattr(cct1.root, 'is_expanded')
        assert hasattr(cct1.root, 'truncated_remainder')

        # Strip new fields to simulate old pickle
        def strip_new_fields(node):
            if node is None:
                return
            if hasattr(node, 'is_expanded'):
                delattr(node, 'is_expanded')
            if hasattr(node, 'truncated_remainder'):
                delattr(node, 'truncated_remainder')
            strip_new_fields(node.left)
            strip_new_fields(node.right)

        strip_new_fields(cct1.root)
        with open(tmpfile, 'wb') as f:
            pickle.dump(cct1.root, f)

        cct2 = CCT.load_from_file(tmpfile)
        assert cct2 is not None

        def check_fields(node):
            if node is None:
                return
            assert hasattr(node, 'is_expanded')
            assert node.is_expanded == False
            assert hasattr(node, 'truncated_remainder')
            assert node.truncated_remainder is None
            check_fields(node.left)
            check_fields(node.right)

        check_fields(cct2.root)
    finally:
        os.unlink(tmpfile)


# ===========================================================================
# Test 8: DOT Output
# ===========================================================================

def test_dot_output():
    cct = CCT(use_bounded_range=True, range_bound=200)
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "i > 1"),
        _make_cr("n % i == 0", True, "n % i == 0"),
    ]
    cct.add_sequence(path1, "tc_0")
    path2 = [
        _make_cr("n <= 1", True, "n <= 1"),
    ]
    cct.add_sequence(path2, "tc_1")
    cct.mark_infeasible([
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", False, "!(i > 1)"),
    ])

    dot = cct.to_dot()
    assert "digraph CCT" in dot
    assert "node0" in dot
    assert "INFEASIBLE" in dot or "✗" in dot

    with tempfile.NamedTemporaryFile(suffix=".dot", delete=False) as f:
        tmpfile = f.name
    try:
        cct.save_dot(tmpfile)
        assert os.path.exists(tmpfile)
        assert not os.path.exists(tmpfile.replace('.dot', '.png'))
        with open(tmpfile) as f:
            content = f.read()
        assert "digraph CCT" in content
        svg = cct.save_svg(tmpfile)
        pdf = cct.save_pdf(tmpfile)
        assert svg is None or os.path.exists(svg)
        assert pdf is None or os.path.exists(pdf)
    finally:
        os.unlink(tmpfile)
        png = tmpfile.replace('.dot', '.png')
        if os.path.exists(png):
            os.unlink(png)
        svg = tmpfile.replace('.dot', '.svg')
        if os.path.exists(svg):
            os.unlink(svg)
        pdf = tmpfile.replace('.dot', '.pdf')
        if os.path.exists(pdf):
            os.unlink(pdf)


def test_dot_output_includes_test_inputs():
    cct = CCT(use_bounded_range=True, range_bound=200)
    cct.add_sequence([
        _make_cr("x > 0", True, "x > 0"),
    ], "tc_2_b1", test_inputs={"x": 9})

    dot = cct.to_dot()

    assert "tc_2_b1(x=9)" in dot


# ===========================================================================
# Test 9: Save/Load Roundtrip
# ===========================================================================

def test_save_load_roundtrip():
    cct1 = CCT(use_bounded_range=True, range_bound=150)
    path1 = [
        _make_cr("a > 0", True, "a > 0"),
        _make_cr("b < 10", False, "a > 0 && !(b < 10)"),
    ]
    cct1.add_sequence(path1, "tc_0")

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        tmpfile = f.name
    try:
        cct1.save_to_file(tmpfile)
        cct2 = CCT.load_from_file(tmpfile)
        assert cct2 is not None
        assert cct2.root is not None
        assert not cct2.root.is_leaf
        assert cct2.root.condition.condition_string == "a > 0"
        result = cct2.check_for_csc()
        assert result is not None
    finally:
        os.unlink(tmpfile)


# ===========================================================================
# Test 10: Z3 Helper Integration
# ===========================================================================

def test_z3_helpers():
    var_types = {"x": "int", "y": "int", "return_value": "int"}
    expr = "x > 5 && y < 10"
    z3_expr = java_expr_to_z3(expr, var_types)
    assert z3_expr is not None
    result = solver_check_z3(z3_expr, var_types)
    assert result != "OK"
    assert "x=" in result
    assert "y=" in result


# ===========================================================================
# Test 11: Parse Path Info
# ===========================================================================

def test_parse_path_info():
    csc_path = [
        "n <= 1,False,!(n <= 1),1",
        "i > 1,True,!(n <= 1) && (n/2 > 1),1",
        "n % i == 0,True,!(n <= 1) && (n/2 > 1) && (n/2 | n),1",
    ]
    results = parse_path_info(csc_path)
    assert len(results) == 3
    assert results[0].condition.condition_string == "n <= 1"
    assert results[0].result == False
    assert results[0].condition.loop_count == 1
    assert results[1].condition.condition_string == "i > 1"
    assert results[1].result == True


# ===========================================================================
# Test 12: Parse Execution Path
# ===========================================================================

def test_parse_execution_path():
    from csc_engine import parse_execution_path

    trace = """
Function input int parameter n = 10
Evaluating if condition: n <= 1 is evaluated as: false
i = 9, current value of i: 9
Entering loop with condition: i > 1 is evaluated as: true
Exiting loop, condition no longer holds: i > 1 is evaluated as: false
some other noise line
REP
NP detecting: x = true
PARAM_MAP: callerVar -> calleeParam, current value of callerVar: 5
RETURN_VALUE: foo() = 42, current value of return_value : 42
""".strip()

    path = parse_execution_path(trace)
    assert len(path) == 5, f"Expected 5 active stdout lines, got {len(path)}"
    assert any("Function input" in p for p in path)
    assert not any("Evaluating if condition" in p for p in path)
    assert not any("Entering loop" in p for p in path)
    assert not any("Exiting loop" in p for p in path)
    assert any("REP" in p for p in path)
    assert any("NP detecting" in p for p in path)
    assert any("PARAM_MAP:" in p for p in path)
    assert any("RETURN_VALUE:" in p for p in path)

# ===========================================================================
# Test 13: exist_flag_in_path
# ===========================================================================

def test_exist_flag_in_path():
    from csc_engine import exist_flag_in_path

    assert exist_flag_in_path(["REP", "other line"])
    assert exist_flag_in_path(["line1", "REP is here"])
    assert not exist_flag_in_path(["line1", "line2", "no flag here"])


# ===========================================================================
# Test 18: parse_class_name
# ===========================================================================

def test_parse_class_name():
    from csc_engine import parse_class_name

    assert parse_class_name("public class Foo { }") == "Foo"
    assert parse_class_name("class Bar { }") == "Bar"
    assert parse_class_name("private static class Inner { }") == "Inner"
    assert parse_class_name("public final class Constants { }") == "Constants"
    assert parse_class_name("no class here") == "classNameUnknown"


# ===========================================================================
# Test 19: add_value_constraints
# ===========================================================================

def test_add_value_constraints():
    from csc_engine import add_value_constraints, add_bounded_range_constraints

    var_types = {"x": "int", "y": "int"}
    result = add_value_constraints("x > 5", var_types)
    assert "x > 5" in result
    assert "x >=" in result or "x <=" in result or "x >" in result
    assert "y" in result

    bounded = add_bounded_range_constraints("x > 5", var_types, bound=200)
    assert "x > 5" in bounded
    assert "x >= -200" in bounded
    assert "x <= 200" in bounded
    assert "y >= -200" in bounded
    assert "y <= 200" in bounded

    char_bounded = add_bounded_range_constraints(
        "letter != 0", {"letter": "char", "return_value": "int"}, bound=200)
    assert "letter >= 0" in char_bounded
    assert "letter <= 200" in char_bounded
    assert "return_value" not in char_bounded


def test_range_excluded_leaf_is_not_ancestor_evidence():
    cct = CCT(use_bounded_range=True, range_bound=200)
    condition = _make_condition("x > 0")
    cct.root = Node(condition, is_leaf=False)
    cct.root.right = Node(RANGE_EXCLUDED_MARKER, is_leaf=True)

    assert not cct._node_has_nonempty_child(cct.root, is_right_branch=True)


# ===========================================================================
# Test 20: run_java_code (now that fix #1 is in place)
# ===========================================================================

def test_run_java_code():
    from csc_engine.java_exec import run_java_code

    code = 'public class TestRun { public static void main(String[] args) { System.out.println("RUN_OK"); } }'
    result = run_java_code(code)
    assert result != "", "run_java_code should not return empty string"
    assert result.returncode == 0, f"Expected returncode 0, got {result.returncode}"
    assert "RUN_OK" in result.stdout, f"Expected RUN_OK in stdout, got: {result.stdout!r}"


# ===========================================================================
# Test 21: Expanded CSC — bounded range satisfiability
# ===========================================================================

def test_expanded_csc_bounded_range():
    cct = CCT(use_bounded_range=True, range_bound=200)

    # Build a CCT with an ancestor match situation
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "i > 1"),
        _make_cr("n % i == 0", False, "!(n % i == 0)"),
        _make_cr("i > 1", True, "i > 1", loop_count=2),
    ]
    cct.add_sequence(path1, "tc_0")

    var_types = {"n": "int", "i": "int", "return_value": "int"}

    # The T branch of i>1 (cnt=1) is covered, F branch is None
    # There's an ancestor match: root's "i>1" (cnt=1) vs deep "i>1" (cnt=2)
    # With expanded mode, it should check bounded range before skipping
    seq = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
    ]
    # i>1, False branch — ancestor match with self
    sat = cct._is_bounded_range_satisfiable(
        seq + [_make_cr("i > 1", False, "!(n <= 1) && !(i > 1)")], var_types)
    assert isinstance(sat, bool)

    global_sat = cct._is_globally_satisfiable(
        seq + [_make_cr("i > 1", False, "!(n <= 1) && !(i > 1)")], var_types)
    assert isinstance(global_sat, bool)


# ===========================================================================
# Test 22: discover_all_uncovered
# ===========================================================================

def test_discover_all_uncovered():
    cct = CCT()
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "i > 1"),
    ]
    cct.add_sequence(path1, "tc_0")

    var_types = {"n": "int", "i": "int", "return_value": "int"}
    branches = cct.discover_all_uncovered(var_types)
    assert isinstance(branches, list)
    # Should find at least the F branch of i>1 and the T branch of n<=1
    assert len(branches) >= 1, f"Expected >=1 uncovered branches, got {len(branches)}"
    branch_ids = [branch["branch_id"] for branch in branches]
    assert branch_ids == sorted(branch_ids)
    assert len(branch_ids) == len(set(branch_ids))


def test_batch_discovery_defers_terminal_update_until_merge():
    cct = CCT()
    cct.add_sequence([_make_cr("x == x", True, "x == x")], "tc_0")

    branches = cct.discover_all_uncovered({"x": "int"})

    assert branches == []
    assert cct.root.left is None
    assert cct.last_terminal_updates == [{
        "branch_id": "F",
        "path": [],
        "target_side": False,
        "marker": INFEASIBLE_MARKER,
        "condition": "x == x",
        "line_number": 1,
    }]

    update = cct.last_terminal_updates[0]
    assert cct.apply_terminal_update(
        update["path"], update["target_side"], update["marker"]) == "applied"
    assert cct.apply_terminal_update(
        update["path"], update["target_side"], update["marker"]) == "idempotent"
    assert cct._is_infeasible_leaf(cct.root.left)
    assert cct.apply_terminal_update([], True, INFEASIBLE_MARKER) == "incompatible"


def test_batch_merge_applies_discovery_terminal_updates(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    session_id = "pending_terminal_merge"
    class_name = "PendingTerminalMerge"
    class_dir = tmp_path / "csc_tmp" / session_id / class_name
    class_dir.mkdir(parents=True)

    cct = CCT()
    cct.add_sequence([_make_cr("x == x", True, "x == x")], "tc_0")
    cct.save_to_file(str(class_dir / f"{class_name}_cct.pkl"))

    program = """
public class PendingTerminalMerge {
    public static int f(int x) {
        if (x == x) { return 1; }
        return 0;
    }
}
"""
    discovery = batch_discover(program, session_id=session_id)
    assert discovery["branches"] == []
    assert not discovery["cct_full"]
    assert len(discovery["terminal_updates"]) == 1

    results = batch_verify_and_merge(
        program,
        T="true",
        D="true",
        branches=[],
        var_types={"x": "int", "return_value": "int"},
        session_id=session_id,
        terminal_updates=discovery["terminal_updates"],
    )
    assert results == []

    merged = CCT.load_from_file(str(class_dir / f"{class_name}_cct.pkl"))
    assert merged is not None
    assert merged._is_infeasible_leaf(merged.root.left)


def test_discover_all_uncovered_records_solver_errors():
    cct = CCT()
    cct.add_sequence([_make_cr("age < 6", True, "age < 6")], "tc_0")

    branches = cct.discover_all_uncovered({})

    assert branches == []
    assert cct.last_discovery_errors
    assert cct.last_discovery_errors[0]["condition"] == "age < 6"
    assert "unknown vars: age" in cct.last_discovery_errors[0]["error"]


def test_batch_discover_original_mode_keeps_var_types(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    session_id = "batch_original_var_types"
    class_name = "SimpleBatchOriginal"
    class_dir = tmp_path / "csc_tmp" / session_id / class_name
    class_dir.mkdir(parents=True)

    cct = CCT()
    cct.add_sequence([_make_cr("age < 6", True, "age < 6")], "bootstrap")
    cct.save_to_file(str(class_dir / f"{class_name}_cct.pkl"))

    program = """
public class SimpleBatchOriginal {
    public static int f(int age) {
        if (age < 6) {
            return 1;
        }
        return 0;
    }
}
"""

    discovery = batch_discover(program, session_id=session_id, use_expanded=False)

    assert discovery["status"] == "ok"
    assert discovery["discovery_errors"] == []
    assert not discovery["cct_full"]
    assert len(discovery["branches"]) >= 1
    assert any("age" in branch["inputs"] for branch in discovery["branches"])


# ===========================================================================
# Test 23: check_for_csc with var_types (expanded mode)
# ===========================================================================

def test_csc_with_var_types():
    cct = CCT(use_bounded_range=True, range_bound=200)
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "i > 1"),
    ]
    cct.add_sequence(path1, "tc_0")

    var_types = {"n": "int", "i": "int", "return_value": "int"}
    result = cct.check_for_csc(var_types)
    # Should find an uncovered branch (either i>1 F or n<=1 T)
    assert result is not None, "Should find uncovered branch in expanded mode"
    assert len(result) >= 1


# ===========================================================================
# Test 24: generate_tcs_by_csc — initial call (CCT not initialized)
# ===========================================================================

def test_generate_tcs_by_csc_initial():
    from csc_engine import generate_tcs_by_csc, CCT_NOT_INITIALIZED

    code = """public class TestCSC {
    public static int foo(int n) {
        System.out.println("Function input int parameter n = " + n);
        if (n <= 1) { return -1; }
        return 1;
    }
    public static void main(String[] args) {
        int r = foo(5);
        System.out.println("RETURN_VALUE: foo() = " + r);
    }
}"""
    result = generate_tcs_by_csc(code, session_id="test_csc_init")
    assert result.status == CCT_NOT_INITIALIZED, \
        f"Expected status {CCT_NOT_INITIALIZED} (CCT_NOT_INITIALIZED), got {result.status}"


# ===========================================================================
# Main test runner
# ===========================================================================

if __name__ == "__main__":
    tests = [
        ("Basic CCT Construction", test_basic_cct_construction),
        ("Ancestor Check Simple", test_ancestor_check_simple),
        ("check_for_csc No Ancestor", test_check_for_csc_no_ancestor),
        ("check_for_csc With Ancestor (Original)", test_check_for_csc_with_ancestor_original),
        ("Truncated Leaf Detection", test_truncated_leaf_detection),
        ("Truncated Leaf Promotion", test_truncated_leaf_promotion),
        ("Backward Compat Pickle", test_backward_compat_pickle),
        ("DOT Output", test_dot_output),
        ("Save/Load Roundtrip", test_save_load_roundtrip),
        ("Z3 Helper Integration", test_z3_helpers),
        ("Parse Path Info", test_parse_path_info),
        ("Parse Execution Path", test_parse_execution_path),
        ("exist_flag_in_path", test_exist_flag_in_path),
        ("parse_class_name", test_parse_class_name),
        ("add_value_constraints", test_add_value_constraints),
        ("run_java_code", test_run_java_code),
        ("Expanded CSC Bounded Range", test_expanded_csc_bounded_range),
        ("discover_all_uncovered", test_discover_all_uncovered),
        ("check_for_csc with var_types", test_csc_with_var_types),
        ("generate_tcs_by_csc Initial", test_generate_tcs_by_csc_initial),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
            print(f"  PASS {name}")
        except Exception as e:
            failed += 1
            print(f"  FAIL {name}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    if failed == 0:
        print("All tests passed!")
    sys.exit(0 if failed == 0 else 1)
