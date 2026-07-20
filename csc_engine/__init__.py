"""
CSC Engine — Condition Sequence Coverage Test Case Generation.

A Python-first library for systematically exploring program paths using a
Condition Case Tree (CCT). Uses Z3 constraint solving to generate test inputs
for uncovered branches.

Quick start::

    from csc_engine import CCT, generate_tcs_by_csc, batch_discover, batch_verify_and_merge

    # Create a CCT and add an execution path
    cct = CCT(use_bounded_range=True, range_bound=200)
    cct.add_sequence(condition_results, "tc_0")

    # Find the next uncovered branch
    target = cct.check_for_csc(var_types)
    if target:
        path_constraint = cct.construct_path_constraint(target)
        # ... Z3-solve for inputs, execute program, add new path ...

    # Visualize
    cct.save_dot("cct.dot")  # renders to cct.png if Graphviz is installed

    # Or use high-level orchestration
    result = generate_tcs_by_csc(java_program, session_id="my_run")
"""

from .cct import (
    CCT,
    Node,
    Condition,
    ConditionResult,
    Result,
    INFEASIBLE_MARKER,
    RANGE_EXCLUDED_MARKER,
    CCT_NOT_INITIALIZED,
    MAX_LOOP_BOUND,
    parse_path_info,
)

from .csc import (
    generate_tcs_by_csc,
    batch_discover,
    batch_verify_and_merge,
    parse_execution_path,
    exist_flag_in_path,
)

from .z3_helpers import (
    java_expr_to_z3,
    solver_check_z3,
    parse_result,
    add_value_constraints,
    add_bounded_range_constraints,
)

from .execution_trace import (
    ExecutionEvent,
    parse_trace_jsonl,
    parse_trace_jsonl_text,
    parse_trace_jsonl_lines,
    condition_results_from_trace,
    update_expr_with_trace,
    path_condition_from_trace,
    path_condition_from_condition_results,
)

from .java_exec import (
    run_java_code,
    get_class_name,
    parse_top_level_md_def,
    parse_class_name,
)

from .refined_tbfv import (
    FSFUnit,
    PathContext,
    ScenarioMatch,
    VerificationResult,
    annotate_cct_with_failures,
    build_match_formula,
    build_path_context,
    build_verification_formula,
    derive_ct_in,
    derive_wp,
    default_fsf,
    find_fsf_file,
    load_fsf,
    load_fsf_file,
    load_testcase_records,
    match_scenario,
    parse_fsf_text,
    verify_record,
    verify_results_file,
    verify_scenario,
    verify_testcase_records,
    write_report,
)

from .failure_localization import (
    CCT_ONLY_INTERVAL_STRATEGY,
    EDGE_DIVERGENCE_GATED_INTERVAL_STRATEGY,
    EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_INTERVAL_STRATEGY,
    EDGE_DIVERGENCE_SIBLING_SHARED_INTERVAL_STRATEGY,
    Evidence,
    INTERVAL_STRATEGY_DESCRIPTIONS,
    INTERVAL_STRATEGY_REGISTRY,
    IntervalStrategy,
    LOCALIZATION_STRATEGY,
    RankingSlot,
    STATEMENT_PRESENCE_INTERVAL_STRATEGY,
    build_localization_dot,
    build_localization_report,
    build_trace_segment_index,
    localization_dot_filename,
    write_localization_dot,
    write_localization_report,
)

from .failure_localization_aggregate import (
    AGGREGATION_STRATEGY,
    AGGREGATION_STRATEGY_REGISTRY,
    AggregationStrategy,
    CONDITION_NODE_TARGET,
    DEFAULT_AGGREGATION_STRATEGY,
    DEFAULT_SCORE_AGGREGATION,
    INTERVAL_TARGET_PREFIX,
    aggregate_localization_report,
    load_localization_report,
    write_aggregated_localization_report,
)

from .failure_localization_eval import (
    AGGREGATED_EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_STRATEGY,
    AGGREGATED_EDGE_DIVERGENCE_SIBLING_SHARED_STRATEGY,
    AGGREGATED_CONDITION_STRATEGY,
    AGGREGATED_INTERVAL_PREFIX,
    DEFAULT_TOP_K as DEFAULT_EVAL_TOP_K,
    RAW_CONDITION_STRATEGY,
    RAW_INTERVAL_PREFIX,
    LocalizationPrediction,
    evaluate_predictions,
    evaluate_reports,
    evaluate_strategy_predictions,
    extract_aggregated_predictions,
    extract_raw_predictions,
    find_mutant_record,
    load_json_report,
    load_manifest,
    prediction_hits_ground_truth,
    validate_mutant_record,
    write_evaluation_report,
)

from .failure_localization_summary import (
    DEFAULT_EVAL_GLOB as DEFAULT_FL_SUMMARY_EVAL_GLOB,
    DEFAULT_TOP_K as DEFAULT_FL_SUMMARY_TOP_K,
    discover_evaluation_reports,
    summarize_fault_localization_results,
    write_csv_rows,
    write_jsonl_rows,
    write_markdown_summary,
)

from .failure_localization_dataset import (
    ValidationIssue,
    resolve_dataset_path,
    validate_fault_localization_dataset,
    write_validation_json,
    write_validation_markdown,
)

from .subject_experiment import (
    DEFAULT_SUMMARY_NAME,
    ExperimentOptions,
    ExperimentStep,
    StepResult,
    SubjectProgram,
    build_subject_steps,
    default_summary_path,
    discover_subject,
    resolve_subject_fsf,
    result_dir_for_program,
    run_subject_experiment,
    write_subject_summary,
)

__all__ = [
    # Core CCT
    "CCT", "Node", "Condition", "ConditionResult", "Result",
    "INFEASIBLE_MARKER", "RANGE_EXCLUDED_MARKER",
    "CCT_NOT_INITIALIZED", "MAX_LOOP_BOUND",
    "parse_path_info",
    # CSC orchestration
    "generate_tcs_by_csc", "batch_discover", "batch_verify_and_merge",
    "parse_execution_path", "exist_flag_in_path",
    # Z3 helpers
    "java_expr_to_z3", "solver_check_z3", "parse_result",
    "add_value_constraints", "add_bounded_range_constraints",
    # Structured execution trace
    "ExecutionEvent", "parse_trace_jsonl", "parse_trace_jsonl_text",
    "parse_trace_jsonl_lines", "condition_results_from_trace",
    "update_expr_with_trace", "path_condition_from_trace",
    "path_condition_from_condition_results",
    # Java execution
    "run_java_code", "get_class_name", "parse_top_level_md_def",
    "parse_class_name",
    # Refined TBFV
    "FSFUnit", "PathContext", "ScenarioMatch", "VerificationResult",
    "annotate_cct_with_failures",
    "build_match_formula", "build_path_context", "build_verification_formula",
    "derive_ct_in", "derive_wp", "default_fsf", "find_fsf_file", "load_fsf",
    "load_fsf_file", "load_testcase_records", "match_scenario", "parse_fsf_text",
    "verify_record", "verify_results_file", "verify_scenario",
    "verify_testcase_records", "write_report",
    # CCT-based failure localization
    "CCT_ONLY_INTERVAL_STRATEGY", "EDGE_DIVERGENCE_GATED_INTERVAL_STRATEGY",
    "EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_INTERVAL_STRATEGY",
    "EDGE_DIVERGENCE_SIBLING_SHARED_INTERVAL_STRATEGY",
    "Evidence", "INTERVAL_STRATEGY_DESCRIPTIONS",
    "INTERVAL_STRATEGY_REGISTRY", "IntervalStrategy",
    "LOCALIZATION_STRATEGY", "RankingSlot", "STATEMENT_PRESENCE_INTERVAL_STRATEGY",
    "build_localization_dot", "build_localization_report", "build_trace_segment_index",
    "localization_dot_filename", "write_localization_dot",
    "write_localization_report",
    # Failure localization aggregation
    "AGGREGATION_STRATEGY", "AGGREGATION_STRATEGY_REGISTRY", "AggregationStrategy",
    "CONDITION_NODE_TARGET", "DEFAULT_AGGREGATION_STRATEGY", "DEFAULT_SCORE_AGGREGATION",
    "INTERVAL_TARGET_PREFIX", "aggregate_localization_report",
    "load_localization_report", "write_aggregated_localization_report",
    # Failure localization evaluation
    "AGGREGATED_CONDITION_STRATEGY", "AGGREGATED_INTERVAL_PREFIX",
    "AGGREGATED_EDGE_DIVERGENCE_SIBLING_EXCLUSIVE_STRATEGY",
    "AGGREGATED_EDGE_DIVERGENCE_SIBLING_SHARED_STRATEGY",
    "DEFAULT_EVAL_TOP_K", "RAW_CONDITION_STRATEGY", "RAW_INTERVAL_PREFIX",
    "LocalizationPrediction", "evaluate_predictions", "evaluate_reports",
    "evaluate_strategy_predictions", "extract_aggregated_predictions",
    "extract_raw_predictions", "find_mutant_record", "load_json_report",
    "load_manifest", "prediction_hits_ground_truth",
    "validate_mutant_record", "write_evaluation_report",
    # Fault localization summary
    "DEFAULT_FL_SUMMARY_EVAL_GLOB", "DEFAULT_FL_SUMMARY_TOP_K",
    "discover_evaluation_reports", "summarize_fault_localization_results",
    "write_csv_rows", "write_jsonl_rows", "write_markdown_summary",
    # Fault localization dataset validation
    "ValidationIssue", "resolve_dataset_path",
    "validate_fault_localization_dataset", "write_validation_json",
    "write_validation_markdown",
    # Subject-level experiment orchestration
    "DEFAULT_SUMMARY_NAME", "ExperimentOptions", "ExperimentStep",
    "StepResult", "SubjectProgram", "build_subject_steps",
    "default_summary_path", "discover_subject", "resolve_subject_fsf",
    "result_dir_for_program", "run_subject_experiment",
    "write_subject_summary",
]
