#!/usr/bin/env python3
"""
Basic CSC Engine usage example.

Demonstrates:
  1. Building a CCT from execution paths
  2. Finding uncovered branches (check_for_csc)
  3. Z3-solving for test inputs
  4. Marking infeasible branches
  5. Visualizing with DOT output
  6. Toggle between Original and Expanded CSC modes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csc_engine import (
    CCT, Condition, ConditionResult, parse_path_info,
    java_expr_to_z3, solver_check_z3, add_value_constraints,
)


def _make_cr(cond_str, result, constraint="", loop_count=1):
    return ConditionResult(
        condition=Condition(line_number=1, condition_string=cond_str,
                           input_constraint=constraint if constraint else cond_str,
                           loop_count=loop_count),
        result=result)


def main():
    print("=" * 60)
    print("CSC Engine — Basic Usage Example")
    print("=" * 60)

    # -------------------------------------------------------------------
    # Step 1: Create a CCT and add execution paths
    # -------------------------------------------------------------------
    print("\n[Step 1] Building CCT from execution paths...")

    cct = CCT(use_bounded_range=True, range_bound=200)

    # Simulating paths from a program like:
    #   if (n <= 1) return -1;
    #   for (int i = n/2; i > 1; i--) {
    #       if (n % i == 0) return i;
    #   }
    #   return 1;

    # Path for n=6: n<=1(F), i>1(T), n%i==0(T) → found factor
    path1 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "!(n <= 1) && (n/2 > 1)"),
        _make_cr("n % i == 0", True, "!(n <= 1) && (n/2 > 1) && (n/2 | n)"),
    ]
    cct.add_sequence(path1, "tc_n=6")

    # Path for n=5: n<=1(F), i>1(T), n%i==0(F), i>1(F) → prime
    path2 = [
        _make_cr("n <= 1", False, "!(n <= 1)"),
        _make_cr("i > 1", True, "!(n <= 1) && (n/2 > 1)"),
        _make_cr("n % i == 0", False, "!(n <= 1) && (n/2 > 1) && !(n/2 | n)"),
        _make_cr("i > 1", False, "!(n <= 1) && (n/2 > 1) && !(n/2 | n) && !(n/2-1 > 1)", loop_count=2),
    ]
    cct.add_sequence(path2, "tc_n=5")

    cct.print_tree()

    # -------------------------------------------------------------------
    # Step 2: Find uncovered branches
    # -------------------------------------------------------------------
    print("\n[Step 2] Finding uncovered branches...")

    var_types = {"n": "int", "return_value": "int"}
    target = cct.check_for_csc(var_types)

    if target:
        print(f"Found target sequence: {target}")
        path_constraint = cct.construct_path_constraint(target)
        print(f"Path constraint: {path_constraint}")

        # Z3-solve for inputs
        bounded_pc = add_value_constraints(path_constraint, var_types)
        z3_expr = java_expr_to_z3(bounded_pc, var_types)
        result = solver_check_z3(z3_expr, var_types)

        if result != "OK":
            print(f"Z3 found inputs: {result}")
        else:
            print("Path constraint is UNSAT — marking infeasible")
            cct.mark_infeasible(target)
    else:
        print("CCT is fully covered — no uncovered branches!")

    # -------------------------------------------------------------------
    # Step 3: Show expanded vs original CSC difference
    # -------------------------------------------------------------------
    print("\n[Step 3] Comparing Original vs Expanded CSC...")

    # Build identical tree for original CSC
    cct_orig = CCT(use_bounded_range=False)
    cct_orig.add_sequence(path1, "tc_n=6")
    cct_orig.add_sequence(path2, "tc_n=5")

    result_off = cct_orig.check_for_csc()
    result_on = cct.check_for_csc(var_types)

    print(f"  Original CSC  (toggle OFF): {result_off}")
    print(f"  Expanded CSC  (toggle ON):  {result_on}")

    if result_off != result_on:
        print("  >> Difference detected! Toggle matters for this tree.")
    else:
        print("  >> Both modes returned the same result for this tree.")

    # -------------------------------------------------------------------
    # Step 4: Visualize
    # -------------------------------------------------------------------
    print("\n[Step 4] Generating DOT visualization...")
    cct.save_dot("example_cct.dot")
    print("  Saved to example_cct.dot (and example_cct.png if Graphviz installed)")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
