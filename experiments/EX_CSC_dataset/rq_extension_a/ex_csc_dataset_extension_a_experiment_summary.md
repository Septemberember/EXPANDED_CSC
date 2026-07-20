# EX_CSC_dataset Experiment Summary

Generated at: 2026-07-04 12:05:24 CST

## Scope

- Dataset root: `dataset/EX_CSC_dataset`
- Subjects: 8 original programs
- Mutants: 48 mutant programs
- Dataset validation: passed, 0 errors, 0 warnings
- Experiment root: `experiments/EX_CSC_dataset/rq_extension_a`

## Configuration

Common CSC configuration:

- Mode: `expanded` for Boundary-enabled runs
- Range bound: `200`
- Batch max iterations: `100`
- Fault localization generation strategy: `batch`
- Fault localization workers: `4`

RQ1 CSC-only comparison:

- Mode: `original`
- Strategy: `sequential`
- Max iterations: `100`

RQ2 parallel comparison:

- Workers: `1,2,4,8`
- Mode: `expanded`
- Range bound: `200`
- Max iterations: `100`

RQ3/RQ4 fault localization:

- Full mutant set: 48 mutants
- SFL baseline: enabled
- Fold-the-tree replay: enabled after archived CSC/TBFV artifacts were generated
- Budget-matched comparison: folded composite vs SFL formulas

## Outputs

- Dataset validation:
  - `experiments/EX_CSC_dataset/rq_extension_a/dataset_validation/dataset_validation.md`
  - `experiments/EX_CSC_dataset/rq_extension_a/dataset_validation/dataset_validation.json`
- RQ1 Boundary comparison:
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ1-boundary/rq1_comparison.md`
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ1-boundary/rq1_comparison.csv`
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ1-boundary/rq1_comparison.json`
- RQ2 parallel generation:
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ2-parallel/parallel_generation_summary.md`
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ2-parallel/parallel_generation_summary.json`
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ2-parallel/parallel_generation_runs.jsonl`
- RQ3 fault localization:
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/fault_localization_summary.md`
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/fault_localization_rows.jsonl`
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/baseline-SFL/sfl_fault_localization_summary.md`
- Fold-the-tree replay:
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/folded-replay-v2/folded_replay_summary.json`
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/folded-replay-v2/folded_replay_rows.jsonl`
- Budget-matched folded vs SFL:
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/folded-budget-matched/budget_matched_summary.md`
  - `experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/folded-budget-matched/multi-sfl/multi_sfl_budget_summary.md`

## RQ1 Observation

All 8 CSC-only runs and all 8 Boundary-enabled W=1 runs completed successfully.

Aggregate comparison:

| Mode | Subjects | Mean Tests | Mean Total Nodes | Mean Leaf Nodes | Mean Covered | Mean Infeasible | Mean Empty | Mean Expanded | Mean Wall Time (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CSC-only | 8 | 6.125 | 18.750 | 9.000 | 6.125 | 2.875 | 1.750 | 0.000 | 2.102 |
| CSC+Boundary | 8 | 68.625 | 1163.250 | 582.125 | 68.625 | 513.375 | 0.000 | 63.500 | 35.086 |

Interpretation: Boundary expansion substantially increases covered leaves and generated test cases while eliminating empty leaves under the same max-iteration budget.

## RQ2 Observation

All 32 parallel generation runs completed successfully; no timeout or failed run was observed.

Overall parallel summary:

| Workers | Completed | Mean Time (s) | Median Time (s) | Mean Testcases | Mean CCT Nodes | Mean Time/Testcase (s) | Mean Speedup | Median Speedup |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 8/8 | 35.086 | 27.447 | 68.750 | 1163.250 | 0.585 | 1.000 | 1.000 |
| 2 | 8/8 | 28.222 | 19.423 | 68.750 | 1163.250 | 0.481 | 1.347 | 1.360 |
| 4 | 8/8 | 26.297 | 17.766 | 68.750 | 1163.250 | 0.453 | 1.473 | 1.464 |
| 8 | 8/8 | 26.178 | 18.754 | 68.750 | 1163.250 | 0.453 | 1.491 | 1.390 |

Interpretation: worker count does not change generated artifacts, and speedup is positive but sublinear. The long-tail subjects include large CCTs such as `BoundedPrimeClassifier` and `BoundedPerfectNumber`.

## RQ3/RQ4 Observation

Fault localization completed for all 8 subjects. The framework discovered 48 evaluation reports; 43 mutants were evaluated and 5 had no TBFV-detected failures.

Main CCT localization summary:

| Strategy | Rows | Top-1 | Top-3 | Top-5 | Top-10 | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggregated.condition_node | 43 | 0.302 | 0.442 | 0.488 | 0.512 | 1.000 | 1.818 |
| aggregated.interval.edge_divergence_sibling_exclusive | 43 | 0.093 | 0.209 | 0.302 | 0.465 | 1.762 | 3.571 |
| aggregated.interval.statement_presence | 43 | 0.116 | 0.395 | 0.442 | 0.488 | 1.714 | 3.571 |

SFL baseline summary:

| Formula | Rows | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Op2 | 43 | 0.116 | 0.535 | 0.698 | 0.977 | 4.233 |
| Ochiai | 43 | 0.093 | 0.488 | 0.698 | 0.977 | 4.372 |
| DStar | 43 | 0.093 | 0.488 | 0.698 | 0.977 | 4.372 |

Fold-the-tree replay summary:

| Strategy | Evaluated | Top-1 | Top-3 | Top-5 | Top-10 |
| --- | ---: | ---: | ---: | ---: | ---: |
| aggregated.condition_node | 43 | 0.279 | 0.488 | 0.512 | 0.512 |
| aggregated.interval.folded_edge_partition | 43 | 0.163 | 0.419 | 0.488 | 0.488 |
| aggregated.composite.folded_condition_or_edge_partition | 43 | 0.442 | 0.907 | 1.000 | 1.000 |

Budget-matched folded composite vs SFL:

| Category | Top-R | Mean Budget | Folded Hit Rate | Best SFL Hit Rate |
| --- | ---: | ---: | ---: | ---: |
| overall | 1 | 2.2 | 18/43 (0.419) | 17/43 (0.395) |
| overall | 2 | 3.9 | 29/43 (0.674) | 28/43 (0.651) |
| overall | 3 | 5.9 | 39/43 (0.907) | 36/43 (0.837) |
| condition | 3 | 4.9 | 20/21 (0.952) | 16/21 (0.762) |
| statement | 3 | 7.0 | 19/22 (0.864) | 20/22 (0.909) |

Interpretation: EX_CSC_dataset is favorable to the folded composite strategy overall and especially on condition/control-flow mutants. For statement/data-flow mutants, SFL remains slightly stronger at Top-2 and Top-3 under the same region budget.

## Notes

- `folded-replay/` is a failed first attempt caused by missing `aggregation_ready/mutants_manifest.jsonl`; it is superseded by `folded-replay-v2/`.
- `aggregation_ready/mutants_manifest.jsonl` was copied from `dataset_snapshot/mutants_manifest.jsonl` to satisfy the folded replay tool's expected input layout.
- No existing EX_CSC, EX_CSC_dataset, or EX_CSC_dataset experiment directory was modified.
