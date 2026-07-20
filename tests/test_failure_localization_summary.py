import csv
import json
import os
import subprocess
import sys

from csc_engine import (
    discover_evaluation_reports,
    summarize_fault_localization_results,
    write_csv_rows,
    write_jsonl_rows,
    write_markdown_summary,
)


def test_discover_evaluation_reports(tmp_path):
    report = tmp_path / "session" / "Subject_M1" / "fault_localization_eval.json"
    report.parent.mkdir(parents=True)
    report.write_text("{}", encoding="utf-8")
    (tmp_path / "other.json").write_text("{}", encoding="utf-8")

    discovered = discover_evaluation_reports(tmp_path)

    assert discovered == [report]


def test_summarize_fault_localization_results_flattens_strategy_rows(tmp_path):
    manifest = [
        mutant_record("Subject_M1", 12, fault_category="condition"),
        mutant_record("Subject_M2", 20, fault_category="statement"),
    ]
    report_path = tmp_path / "run" / "Subject_M1" / "fault_localization_eval.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(
        json.dumps(eval_report("Subject_M1", {
            "aggregated.condition_node": metric(
                target_type="condition",
                top1=True,
                top3=True,
                best_rank=1,
                region_hit=1,
            ),
            "aggregated.interval.edge_divergence_gated": metric(
                target_type="interval",
                top1=False,
                top3=True,
                best_rank=3,
                region_hit=2,
            ),
        })),
        encoding="utf-8",
    )

    summary = summarize_fault_localization_results(manifest, [report_path], top_k=[1, 3])
    rows = summary["rows"]

    assert len(rows) == 3
    condition = next(row for row in rows if row["strategy"] == "aggregated.condition_node")
    assert condition["status"] == "evaluated"
    assert condition["fault_category"] == "condition"
    assert condition["top1_hit"]
    assert condition["region_size_hit"] == 1
    assert condition["hit_item_region_size"] == 1
    assert condition["cumulative_inspection_region_at_first_hit"] == 1
    missing = next(row for row in rows if row["mutant_id"] == "Subject_M2")
    assert missing["status"] == "missing_result"
    assert summary["summary"]["missing_result_count"] == 1
    assert summary["summary"]["strategies"]["aggregated.condition_node"]["top1_hit_rate"] == 1.0
    condition_category = summary["summary"]["fault_categories"]["condition"]
    assert condition_category["mutant_count"] == 1
    assert condition_category["strategies"]["aggregated.condition_node"]["top1_hit_rate"] == 1.0


def test_summarize_marks_orphan_and_invalid_reports(tmp_path):
    manifest = [mutant_record("Subject_M1", 12)]
    orphan = tmp_path / "orphan" / "fault_localization_eval.json"
    orphan.parent.mkdir()
    orphan.write_text(json.dumps(eval_report("Unknown_M1", {
        "aggregated.condition_node": metric(target_type="condition", top1=True),
    })), encoding="utf-8")
    invalid = tmp_path / "bad" / "fault_localization_eval.json"
    invalid.parent.mkdir()
    invalid.write_text("{bad json", encoding="utf-8")

    summary = summarize_fault_localization_results(manifest, [orphan, invalid], top_k=[1])

    statuses = {row["status"] for row in summary["rows"]}
    assert {"missing_result", "orphan_result", "invalid_report"} == statuses
    assert summary["summary"]["orphan_result_count"] == 1
    assert summary["summary"]["invalid_report_count"] == 1


def test_write_summary_outputs(tmp_path):
    report = {
        "summary": {
            "manifest_count": 1,
            "evaluation_report_count": 1,
            "row_count": 1,
            "evaluated_row_count": 1,
            "evaluated_mutant_count": 1,
            "missing_result_count": 0,
            "invalid_report_count": 0,
            "orphan_result_count": 0,
            "top_k": [1],
            "strategies": {
                "aggregated.condition_node": {
                    "row_count": 1,
                    "hit_rate": 1.0,
                    "top1_hit_rate": 1.0,
                    "mean_best_rank": 1.0,
                    "mean_region_size_average": 1.0,
                    "mean_hit_item_region_size": 1.0,
                    "mean_cumulative_inspection_region_at_first_hit": 1.0,
                },
            },
            "fault_categories": {
                "condition": {
                    "label": "Condition/Control-Flow Mutants",
                    "mutant_count": 1,
                    "row_count": 1,
                    "strategies": {
                        "aggregated.condition_node": {
                            "row_count": 1,
                            "hit_rate": 1.0,
                            "top1_hit_rate": 1.0,
                            "mean_best_rank": 1.0,
                            "mean_region_size_average": 1.0,
                            "mean_hit_item_region_size": 1.0,
                            "mean_cumulative_inspection_region_at_first_hit": 1.0,
                        },
                    },
                },
            },
        },
        "rows": [
            {
                "status": "evaluated",
                "mutant_id": "Subject_M1",
                "strategy": "aggregated.condition_node",
                "hit_lines": [12],
                "top1_hit": True,
            },
        ],
    }
    jsonl = tmp_path / "out.jsonl"
    csv_path = tmp_path / "out.csv"
    md = tmp_path / "out.md"

    write_jsonl_rows(report["rows"], jsonl)
    write_csv_rows(report["rows"], csv_path)
    write_markdown_summary(report, md)

    assert json.loads(jsonl.read_text(encoding="utf-8").splitlines()[0])["mutant_id"] == "Subject_M1"
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["hit_lines"] == "[12]"
    markdown = md.read_text(encoding="utf-8")
    assert "aggregated.condition_node" in markdown
    assert "Mean Hit Item Region" in markdown
    assert "Mean Cumulative Region at First Hit" in markdown
    assert "Strategy Summary by Fault Category" in markdown
    assert "Condition/Control-Flow Mutants" in markdown
    assert "Mean Hit Region" not in markdown


def test_summarize_fault_localization_results_cli_smoke(tmp_path):
    manifest = tmp_path / "mutants_manifest.jsonl"
    manifest.write_text(
        json.dumps(mutant_record("Subject_M1", 12)) + "\n",
        encoding="utf-8",
    )
    eval_dir = tmp_path / "results" / "session" / "Subject_M1"
    eval_dir.mkdir(parents=True)
    (eval_dir / "fault_localization_eval.json").write_text(
        json.dumps(eval_report("Subject_M1", {
            "aggregated.condition_node": metric(target_type="condition", top1=True),
        })),
        encoding="utf-8",
    )
    jsonl = tmp_path / "summary.jsonl"
    csv_path = tmp_path / "summary.csv"
    md = tmp_path / "summary.md"
    tool_path = os.path.join(os.path.dirname(__file__), "..", "summarize_fault_localization_results.py")

    completed = subprocess.run(
        [
            sys.executable,
            tool_path,
            "--manifest",
            str(manifest),
            "--results-root",
            str(tmp_path / "results"),
            "--output-jsonl",
            str(jsonl),
            "--output-csv",
            str(csv_path),
            "--output-md",
            str(md),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Fault localization summary complete" in completed.stdout
    assert jsonl.exists()
    assert csv_path.exists()
    assert md.exists()


def mutant_record(mutant_id, line, fault_category=None):
    record = {
        "mutant_id": mutant_id,
        "subject": "Subject",
        "mutant_file": f"Subject/{mutant_id}.java",
        "operator": "ROR",
        "fault_kind": "control-flow",
        "ground_truth": {
            "primary_file": f"Subject/{mutant_id}.java",
            "primary_line": line,
            "acceptable_files": [f"Subject/{mutant_id}.java"],
            "acceptable_lines": [line],
            "acceptable_line_window": {
                "start": line,
                "end": line,
            },
        },
    }
    if fault_category:
        record["fault_category"] = fault_category
        record["ground_truth"]["fault_category"] = fault_category
    return record


def eval_report(mutant_id, metrics):
    return {
        "mutant_id": mutant_id,
        "mutant_file": f"Subject/{mutant_id}.java",
        "operator": "ROR",
        "fault_kind": "control-flow",
        "ground_truth": {
            "primary_file": f"Subject/{mutant_id}.java",
            "primary_line": 12,
        },
        "summary": {
            "prediction_strategies": sorted(metrics),
            "top_k": [1, 3],
        },
        "metrics": metrics,
    }


def metric(target_type, top1=False, top3=False, best_rank=None, region_hit=1):
    if best_rank is None and (top1 or top3):
        best_rank = 1 if top1 else 3
    return {
        "strategy": "unused",
        "target_type": target_type,
        "prediction_count": 3,
        "hit": top1 or top3,
        "best_rank": best_rank,
        "hit_lines": [12] if top1 or top3 else [],
        "hit_prediction": None,
        "hit_item_region_size": region_hit if top1 or top3 else None,
        "region_size": {
            "average": 1.5,
            "max": 2,
            "top1": 1,
            "hit": region_hit if top1 or top3 else None,
            "topk_average": {
                "top1": 1,
                "top3": 1.5,
            },
        },
        "inspection_region": {
            "at_first_hit": region_hit if top1 or top3 else None,
            "topk": {
                "top1": 1,
                "top3": 2,
            },
        },
        "topk": {
            "top1": top1,
            "top3": top1 or top3,
        },
    }
