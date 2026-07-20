#!/usr/bin/env python3
"""Compare folded-composite budgets against multiple SFL formulas.

This is an experimental, read-only analysis helper.  It reuses an existing
folded-composite budget-matched result file and recomputes the SFL hit rate for
multiple SFL formulas under the same source-line budgets.

The script does not change the folded localization pipeline.  It only reads:

* budget_matched_rows.jsonl, which already contains Top-K folded budgets;
* mutants_manifest.jsonl, which provides ground-truth lines;
* sfl_localization.json files, which contain rankings for SFL formulas.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_FORMULAS = ["ochiai", "tarantula", "dstar", "barinel", "op2"]
DEFAULT_TOP_K = [1, 2, 3]


def main() -> int:
    args = _build_parser().parse_args()
    budget_rows_path = args.budget_rows.resolve()
    experiment_dirs = [Path(p).resolve() for p in args.experiment_dir]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    formulas = _parse_text_list(args.formulas)
    top_k = _parse_int_list(args.top_k)
    budget_rows = _read_jsonl(budget_rows_path)
    manifests = _load_manifests(experiment_dirs)

    rows = [
        _evaluate_row(row, manifests, experiment_dirs, formulas, top_k)
        for row in budget_rows
    ]
    evaluated = [row for row in rows if row.get("status") == "evaluated"]
    summary = _build_summary(evaluated, formulas, top_k)
    best_three = _select_best_formulas(summary, formulas, top_k, category="overall")

    _write_outputs(
        output_dir=output_dir,
        rows=rows,
        summary=summary,
        best_three=best_three,
        budget_rows_path=budget_rows_path,
        experiment_dirs=experiment_dirs,
        formulas=formulas,
        top_k=top_k,
    )

    print(f"Multi-SFL budget-matched comparison complete: {output_dir}")
    print(f"  Rows:      {len(rows)}")
    print(f"  Evaluated: {len(evaluated)}")
    print(f"  Formulas:  {', '.join(formulas)}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare folded-composite budgets against multiple SFL formulas.",
    )
    parser.add_argument(
        "--budget-rows",
        required=True,
        type=Path,
        help="Existing folded-composite budget_matched_rows.jsonl.",
    )
    parser.add_argument(
        "--experiment-dir",
        action="append",
        required=True,
        help="Archived FL experiment directory. Repeat for multiple datasets.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Output directory for multi-SFL rows and summaries.",
    )
    parser.add_argument(
        "--formulas",
        default=",".join(DEFAULT_FORMULAS),
        help="Comma-separated SFL formulas to evaluate.",
    )
    parser.add_argument(
        "--top-k",
        default=",".join(str(v) for v in DEFAULT_TOP_K),
        help="Comma-separated Top-K values from the folded budget rows.",
    )
    return parser


def _evaluate_row(
    budget_row: dict[str, Any],
    manifests: dict[str, dict[str, Any]],
    experiment_dirs: list[Path],
    formulas: list[str],
    top_k: list[int],
) -> dict[str, Any]:
    base = {
        "mutant_id": budget_row.get("mutant_id"),
        "subject": budget_row.get("subject"),
        "operator": budget_row.get("operator"),
        "fault_kind": budget_row.get("fault_kind"),
        "fault_category": budget_row.get("fault_category"),
        "primary_line": budget_row.get("primary_line"),
        "scoring_strategy": budget_row.get("scoring_strategy"),
        "F_total": budget_row.get("F_total"),
        "P_total": budget_row.get("P_total"),
    }
    if budget_row.get("status") != "evaluated":
        return base | {
            "status": budget_row.get("status", "skipped"),
            "reason": "budget_row_not_evaluated",
        }

    mutant_id = str(budget_row.get("mutant_id", ""))
    manifest = manifests.get(mutant_id, {})
    ground_truth = manifest.get("ground_truth", {})
    if not ground_truth:
        return base | {"status": "skipped", "reason": "missing_ground_truth"}

    sfl_report = _find_sfl_report(experiment_dirs, mutant_id)
    if sfl_report is None:
        return base | {"status": "skipped", "reason": "missing_sfl_report"}

    sfl_data = json.loads(sfl_report.read_text(encoding="utf-8"))
    rankings = sfl_data.get("rankings", {})
    acceptable = _acceptable_line_set(ground_truth)
    window = _acceptable_window(ground_truth)

    def hit(lines: set[int]) -> bool:
        if acceptable.intersection(lines):
            return True
        if window is not None:
            start, end = window
            return any(start <= line <= end for line in lines)
        return False

    result = base | {
        "status": "evaluated",
        "sfl_report": str(sfl_report),
        "primary_file": ground_truth.get("primary_file"),
    }

    for k in top_k:
        budget = int(budget_row.get(f"top{k}_budget", 0) or 0)
        result[f"top{k}_budget"] = budget
        result[f"top{k}_folded_hit"] = bool(budget_row.get(f"top{k}_folded_hit"))
        for formula in formulas:
            ranking = rankings.get(formula)
            if not isinstance(ranking, list):
                result[f"top{k}_{formula}_hit"] = None
                result[f"top{k}_{formula}_region_lines"] = []
                continue
            region = _sfl_budget_lines(ranking, budget)
            result[f"top{k}_{formula}_hit"] = hit(region)
            result[f"top{k}_{formula}_region_lines"] = sorted(region)

    return result


def _build_summary(
    evaluated: list[dict[str, Any]],
    formulas: list[str],
    top_k: list[int],
) -> list[dict[str, Any]]:
    categories = ["overall"]
    for row in evaluated:
        category = str(row.get("fault_category") or "<missing>")
        if category not in categories:
            categories.append(category)

    summary: list[dict[str, Any]] = []
    for category in categories:
        rows = evaluated if category == "overall" else [
            row for row in evaluated if str(row.get("fault_category")) == category
        ]
        if not rows:
            continue
        item: dict[str, Any] = {
            "fault_category": category,
            "cases": len(rows),
        }
        for k in top_k:
            budgets = [int(row.get(f"top{k}_budget", 0) or 0) for row in rows]
            folded_hits = sum(1 for row in rows if row.get(f"top{k}_folded_hit"))
            item[f"top{k}_mean_budget"] = mean(budgets) if budgets else 0.0
            item[f"top{k}_folded_hits"] = folded_hits
            item[f"top{k}_folded_rate"] = folded_hits / len(rows)
            for formula in formulas:
                hits = sum(1 for row in rows if row.get(f"top{k}_{formula}_hit"))
                item[f"top{k}_{formula}_hits"] = hits
                item[f"top{k}_{formula}_rate"] = hits / len(rows)
        summary.append(item)
    return summary


def _select_best_formulas(
    summary: list[dict[str, Any]],
    formulas: list[str],
    top_k: list[int],
    category: str,
) -> list[dict[str, Any]]:
    overall = next((row for row in summary if row["fault_category"] == category), None)
    if overall is None:
        return []

    scored: list[dict[str, Any]] = []
    for formula in formulas:
        rates = [float(overall.get(f"top{k}_{formula}_rate", 0.0)) for k in top_k]
        scored.append({
            "formula": formula,
            "mean_rate": mean(rates) if rates else 0.0,
            "top_rates": {f"top{k}": rates[i] for i, k in enumerate(top_k)},
        })
    scored.sort(
        key=lambda item: (
            -float(item["mean_rate"]),
            *[-float(item["top_rates"][f"top{k}"]) for k in reversed(top_k)],
            str(item["formula"]),
        )
    )
    return scored[:3]


def _write_outputs(
    output_dir: Path,
    rows: list[dict[str, Any]],
    summary: list[dict[str, Any]],
    best_three: list[dict[str, Any]],
    budget_rows_path: Path,
    experiment_dirs: list[Path],
    formulas: list[str],
    top_k: list[int],
) -> None:
    _write_jsonl(output_dir / "multi_sfl_budget_rows.jsonl", rows)
    _write_csv(output_dir / "multi_sfl_budget_rows.csv", rows)
    (output_dir / "multi_sfl_budget_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "multi_sfl_best_three.json").write_text(
        json.dumps(best_three, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "multi_sfl_budget_summary.md").write_text(
        "\n".join(_build_markdown(summary, best_three, formulas, top_k)),
        encoding="utf-8",
    )
    metadata = {
        "budget_rows": str(budget_rows_path),
        "experiment_dirs": [str(path) for path in experiment_dirs],
        "formulas": formulas,
        "top_k": top_k,
        "note": (
            "Experimental analysis only. Folded budgets are read from the "
            "existing budget_matched_rows.jsonl; only SFL formula hit rates "
            "are recomputed under the same budgets."
        ),
    }
    (output_dir / "multi_sfl_budget_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _build_markdown(
    summary: list[dict[str, Any]],
    best_three: list[dict[str, Any]],
    formulas: list[str],
    top_k: list[int],
) -> list[str]:
    lines = [
        "# Multi-SBFL Budget-Matched Comparison",
        "",
        "- Scope: experimental analysis only; no paper text is changed.",
        "- Folded method: existing folded composite.",
        "- Budget: the same folded Top-K source-line region size used in the "
        "current RQ3 budget-matched comparison.",
        f"- SFL formulas: {', '.join(f'`{formula}`' for formula in formulas)}.",
        "",
        "## Best Three SFL Formulas by Overall Mean Top-K Hit Rate",
        "",
        "| Rank | Formula | Mean Top-K Rate | Top Rates |",
        "| ---: | --- | ---: | --- |",
    ]
    for rank, item in enumerate(best_three, start=1):
        top_rates = ", ".join(
            f"{key}={value:.3f}" for key, value in item["top_rates"].items()
        )
        lines.append(
            f"| {rank} | `{item['formula']}` | {item['mean_rate']:.3f} | {top_rates} |"
        )

    for item in summary:
        category = item["fault_category"]
        lines.extend([
            "",
            f"## {category} (N={item['cases']})",
            "",
        ])
        header = ["Top-K", "Mean Budget", "Folded"] + [formula for formula in formulas]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---:"] * len(header)) + " |")
        for k in top_k:
            cells = [
                str(k),
                f"{item[f'top{k}_mean_budget']:.1f}",
                _format_hits(item, k, "folded", item["cases"]),
            ]
            cells.extend(_format_hits(item, k, formula, item["cases"]) for formula in formulas)
            lines.append("| " + " | ".join(cells) + " |")
    return lines


def _format_hits(item: dict[str, Any], k: int, formula: str, cases: int) -> str:
    hits = item[f"top{k}_{formula}_hits"]
    rate = item[f"top{k}_{formula}_rate"]
    return f"{hits}/{cases} ({rate:.3f})"


def _load_manifests(experiment_dirs: list[Path]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for exp_dir in experiment_dirs:
        manifest = exp_dir / "aggregation_ready" / "mutants_manifest.jsonl"
        if not manifest.exists():
            continue
        for row in _read_jsonl(manifest):
            mutant_id = str(row.get("mutant_id", ""))
            if mutant_id:
                records[mutant_id] = row
    return records


def _find_sfl_report(experiment_dirs: list[Path], mutant_id: str) -> Path | None:
    for exp_dir in experiment_dirs:
        for base in ("baseline-SFL-v2", "baseline-SFL"):
            sfl_dir = exp_dir / base
            if not sfl_dir.exists():
                continue
            for candidate in _mutant_dir_candidates(sfl_dir, mutant_id):
                report = candidate / "sfl_localization.json"
                if report.exists():
                    return report
    return None


def _mutant_dir_candidates(base: Path, mutant_id: str) -> list[Path]:
    candidates: list[Path] = []
    for candidate in sorted(base.glob(f"**/{mutant_id}")):
        if candidate.is_dir():
            candidates.append(candidate)
    for candidate in sorted(base.glob(f"**/*_{mutant_id}")):
        if candidate.is_dir():
            candidates.append(candidate)
    return candidates


def _sfl_budget_lines(ranking: list[dict[str, Any]], budget: int) -> set[int]:
    lines: set[int] = set()
    for item in ranking:
        if len(lines) >= budget:
            break
        line = item.get("line")
        if line is not None:
            lines.add(int(line))
    return lines


def _acceptable_line_set(ground_truth: dict[str, Any]) -> set[int]:
    lines: set[int] = set()
    for line in ground_truth.get("acceptable_lines", []) or []:
        lines.add(int(line))
    primary = ground_truth.get("primary_line")
    if primary is not None:
        lines.add(int(primary))
    return lines


def _acceptable_window(ground_truth: dict[str, Any]) -> tuple[int, int] | None:
    window = ground_truth.get("acceptable_line_window")
    if isinstance(window, dict):
        start = window.get("start")
        end = window.get("end")
    elif isinstance(window, list) and len(window) == 2:
        start, end = window
    else:
        return None
    if start is None or end is None:
        return None
    return int(start), int(end)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _parse_text_list(raw: str) -> list[str]:
    values = [part.strip() for part in raw.split(",") if part.strip()]
    if not values:
        raise ValueError("At least one formula is required.")
    return values


def _parse_int_list(raw: str) -> list[int]:
    values = sorted({int(part.strip()) for part in raw.split(",") if part.strip()})
    if not values or any(value <= 0 for value in values):
        raise ValueError(f"Top-K values must be positive: {raw!r}")
    return values


if __name__ == "__main__":
    raise SystemExit(main())
