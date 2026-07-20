import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csc_engine import (
    LocalizationPrediction,
    evaluate_reports,
    evaluate_strategy_predictions,
    extract_aggregated_predictions,
    extract_raw_predictions,
    find_mutant_record,
    load_manifest,
    prediction_hits_ground_truth,
    validate_mutant_record,
    write_evaluation_report,
)


def test_load_manifest_and_find_mutant(tmp_path):
    manifest = tmp_path / "mutants_manifest.jsonl"
    manifest.write_text(
        json.dumps(mutant_record("Subject_M1", 12)) + "\n"
        + json.dumps(mutant_record("Subject_M2", 20)) + "\n",
        encoding="utf-8",
    )

    records = load_manifest(manifest)
    found = find_mutant_record(records, "Subject_M2")

    assert found["mutant_id"] == "Subject_M2"
    assert found["ground_truth"]["primary_line"] == 20


def test_validate_mutant_record_fills_default_acceptable_lines():
    record = mutant_record("Subject_M1", 12)
    del record["ground_truth"]["acceptable_lines"]

    validate_mutant_record(record)

    assert record["ground_truth"]["acceptable_lines"] == [12]


def test_condition_prediction_hits_ground_truth_line():
    record = mutant_record("Subject_M1", 12)
    prediction = LocalizationPrediction(
        target_type="condition",
        strategy="aggregated.condition_node",
        rank=1,
        score=1.0,
        predicted_lines=(12,),
        region_size=1,
        source_file=None,
        location_basis="condition_line",
        raw={},
    )

    assert prediction_hits_ground_truth(prediction, record)


def test_statement_interval_prediction_hits_statement_line():
    record = mutant_record("Subject_M1", 38)
    report = raw_report(
        condition_records=[],
        interval_records={
            "statement_presence": [
                interval_record(rank=1, statement_lines=[36, 37, 38]),
            ],
        },
    )

    metrics = evaluate_reports(record, raw_report=report, top_k=[1, 3])["metrics"]

    item = metrics["raw.interval.statement_presence"]
    assert item["hit"]
    assert item["best_rank"] == 1
    assert item["hit_lines"] == [38]
    assert item["topk"]["top1"]


def test_statement_aware_interval_without_statement_lines_does_not_anchor_hit():
    record = mutant_record("Subject_M1", 15)
    report = raw_report(
        condition_records=[],
        interval_records={
            "statement_presence": [
                interval_record(
                    rank=1,
                    from_line=10,
                    to_line=20,
                    statement_lines=[],
                ),
            ],
        },
    )

    prediction = extract_raw_predictions(report)[0]
    metrics = evaluate_strategy_predictions(record, [prediction], top_k=[1])

    assert prediction.predicted_lines == ()
    assert prediction.location_basis == "statement_lines_missing"
    assert not metrics["hit"]
    assert not metrics["topk"]["top1"]


def test_sibling_exclusive_interval_without_statement_lines_does_not_anchor_hit():
    record = mutant_record("Subject_M1", 15)
    report = raw_report(
        condition_records=[],
        interval_records={
            "edge_divergence_sibling_exclusive": [
                interval_record(
                    rank=1,
                    from_line=10,
                    to_line=20,
                    statement_lines=[],
                ),
            ],
        },
    )

    prediction = extract_raw_predictions(report)[0]
    metrics = evaluate_strategy_predictions(record, [prediction], top_k=[1])

    assert prediction.predicted_lines == ()
    assert prediction.location_basis == "statement_lines_missing"
    assert not metrics["hit"]
    assert not metrics["topk"]["top1"]


def test_sibling_shared_interval_without_statement_lines_does_not_anchor_hit():
    record = mutant_record("Subject_M1", 15)
    report = raw_report(
        condition_records=[],
        interval_records={
            "edge_divergence_sibling_shared": [
                interval_record(
                    rank=1,
                    from_line=10,
                    to_line=20,
                    statement_lines=[],
                ),
            ],
        },
    )

    prediction = extract_raw_predictions(report)[0]
    metrics = evaluate_strategy_predictions(record, [prediction], top_k=[1])

    assert prediction.predicted_lines == ()
    assert prediction.location_basis == "statement_lines_missing"
    assert not metrics["hit"]
    assert not metrics["topk"]["top1"]


def test_cct_only_interval_can_use_condition_anchor_span_baseline():
    record = mutant_record("Subject_M1", 15)
    report = raw_report(
        condition_records=[],
        interval_records={
            "cct_only": [
                interval_record(
                    rank=1,
                    from_line=10,
                    to_line=20,
                    statement_lines=[],
                ),
            ],
        },
    )

    prediction = extract_raw_predictions(report)[0]
    metrics = evaluate_strategy_predictions(record, [prediction], top_k=[1])

    assert 15 in prediction.predicted_lines
    assert metrics["hit"]


def test_aggregated_predictions_are_evaluated_by_strategy():
    record = mutant_record("Subject_M1", 41)
    aggregated = {
        "summary": {},
        "aggregated_condition_node_ranking": [
            {
                "rank": 2,
                "line": 41,
                "condition": "a < b",
                "risk_score": 1.2,
            },
        ],
        "aggregated_interval_rankings": {
            "statement_presence": [
                interval_record(rank=1, statement_lines=[36, 37, 38]),
            ],
        },
    }

    metrics = evaluate_reports(record, aggregated_report=aggregated, top_k=[1, 3])["metrics"]

    assert metrics["aggregated.condition_node"]["best_rank"] == 2
    assert not metrics["aggregated.condition_node"]["topk"]["top1"]
    assert metrics["aggregated.condition_node"]["topk"]["top3"]
    assert not metrics["aggregated.interval.statement_presence"]["hit"]
    assert metrics["aggregated.interval.statement_presence"]["region_size"]["average"] == 3
    assert metrics["aggregated.interval.statement_presence"]["region_size"]["top1"] == 3


def test_aggregated_composite_hits_when_condition_or_gated_interval_hits():
    record = mutant_record("Subject_M1", 38)
    aggregated = {
        "summary": {},
        "aggregated_condition_node_ranking": [
            {
                "rank": 1,
                "line": 12,
                "condition": "a < b",
                "risk_score": 1.2,
            },
        ],
        "aggregated_interval_rankings": {
            "edge_divergence_gated": [
                interval_record(rank=1, statement_lines=[36, 37, 38]),
            ],
        },
    }

    metrics = evaluate_reports(record, aggregated_report=aggregated, top_k=[1, 3])["metrics"]
    composite = metrics["aggregated.composite.condition_or_interval"]

    assert composite["hit"]
    assert composite["best_rank"] == 1
    assert composite["topk"]["top1"]
    assert composite["hit_lines"] == [38]
    assert composite["region_size"]["top1"] == 4
    assert composite["hit_item_region_size"] == 4
    assert composite["region_size"]["hit"] == 4
    assert composite["inspection_region"]["at_first_hit"] == 4
    assert composite["inspection_region"]["topk"]["top1"] == 4


def test_aggregated_composite_region_size_uses_unique_line_union():
    record = mutant_record("Subject_M1", 12)
    aggregated = {
        "summary": {},
        "aggregated_condition_node_ranking": [
            {
                "rank": 1,
                "line": 12,
                "condition": "a < b",
                "risk_score": 1.2,
            },
        ],
        "aggregated_interval_rankings": {
            "edge_divergence_gated": [
                interval_record(rank=1, statement_lines=[12, 13, 14]),
            ],
        },
    }

    metrics = evaluate_reports(record, aggregated_report=aggregated, top_k=[1])["metrics"]
    composite = metrics["aggregated.composite.condition_or_interval"]

    assert composite["hit"]
    assert composite["region_size"]["top1"] == 3
    assert composite["hit_item_region_size"] == 3
    assert composite["region_size"]["hit"] == 3
    assert composite["inspection_region"]["at_first_hit"] == 3
    assert composite["hit_prediction"]["predicted_lines"] == [12, 13, 14]


def test_aggregated_composite_hit_item_region_is_only_the_first_hit_rank_item():
    record = mutant_record("Subject_M1", 50)
    aggregated = {
        "summary": {},
        "aggregated_condition_node_ranking": [
            {
                "rank": 1,
                "line": 10,
                "condition": "a < b",
                "risk_score": 1.2,
            },
            {
                "rank": 2,
                "line": 50,
                "condition": "c < d",
                "risk_score": 1.1,
            },
        ],
        "aggregated_interval_rankings": {
            "edge_divergence_gated": [
                interval_record(rank=1, statement_lines=[20, 21]),
                interval_record(rank=2, statement_lines=[50, 51]),
            ],
        },
    }

    metrics = evaluate_reports(record, aggregated_report=aggregated, top_k=[1, 2])["metrics"]
    composite = metrics["aggregated.composite.condition_or_interval"]

    assert composite["hit"]
    assert composite["best_rank"] == 2
    assert composite["hit_item_region_size"] == 2
    assert composite["region_size"]["hit"] == 2
    assert composite["inspection_region"]["at_first_hit"] == 5


def test_write_evaluation_report(tmp_path):
    output = tmp_path / "eval.json"
    write_evaluation_report({"ok": True}, output)

    assert json.loads(output.read_text(encoding="utf-8"))["ok"]


def test_evaluate_fault_localization_tool_smoke(tmp_path):
    manifest = tmp_path / "mutants_manifest.jsonl"
    manifest.write_text(json.dumps(mutant_record("Subject_M1", 38)) + "\n", encoding="utf-8")
    aggregated = {
        "summary": {},
        "aggregated_condition_node_ranking": [],
        "aggregated_interval_rankings": {
            "statement_presence": [
                interval_record(rank=1, statement_lines=[36, 37, 38]),
            ],
        },
    }
    aggregated_path = tmp_path / "cct_failure_localization_aggregated.json"
    aggregated_path.write_text(json.dumps(aggregated), encoding="utf-8")
    output_path = tmp_path / "fault_localization_eval.json"
    tool_path = os.path.join(os.path.dirname(__file__), "..", "evaluate_fault_localization.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--manifest",
            str(manifest),
            "--mutant-id",
            "Subject_M1",
            "--aggregated-report",
            str(aggregated_path),
            "--output",
            str(output_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Fault localization evaluation complete" in completed.stdout
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["metrics"]["aggregated.interval.statement_presence"]["topk"]["top1"]
    assert report["metrics"]["aggregated.interval.statement_presence"]["region_size"]["hit"] == 3


def mutant_record(mutant_id, line):
    return {
        "mutant_id": mutant_id,
        "mutant_file": "Subject/Subject_M1.java",
        "operator": "AOR",
        "fault_kind": "data-flow",
        "ground_truth": {
            "primary_file": "Subject/Subject_M1.java",
            "primary_line": line,
            "acceptable_files": ["Subject/Subject_M1.java"],
            "acceptable_lines": [line],
            "acceptable_line_window": {
                "start": line,
                "end": line,
            },
        },
    }


def raw_report(condition_records, interval_records):
    return {
        "summary": {},
        "condition_node_ranking": condition_records,
        "interval_rankings": interval_records,
    }


def interval_record(rank,
                    statement_lines,
                    from_line=35,
                    to_line=41):
    return {
        "rank": rank,
        "risk_score": 1.0,
        "from_line": from_line,
        "from_condition": "c > d",
        "outcome": "TRUE",
        "to_line": to_line,
        "to_condition": "a > b",
        "line_interval": [from_line, to_line],
        "condition_anchor_span": [from_line, to_line],
        "condition_anchor_kind": "forward",
        "statement_lines": statement_lines,
    }
