# EX_CSC_dataset Paper Inclusion Record

Generated at: 2026-07-04

This note records whether and how the `EX_CSC_dataset` dataset should be included
with the previous 24-program experimental results when writing the paper.
It is intended as a paper-facing experiment memo, not as a replacement for the
raw experiment artifacts.

## Data Sources

Previous 24-program results:

- RQ1: `experiments/EX_CSC_dataset/rq1_bounded_completion/rq1_summary.md`
- RQ2: `experiments/EX_CSC_dataset/rq2_parallel_generation/parallel_generation_summary.md`
- RQ3/RQ4 budget-matched FL: `experiments/EX_CSC_dataset/folded_fault_localization/multi_sfl_budget_matched/multi_sfl_budget_summary.md`

EX_CSC_dataset results:

- Experiment memo: `experiments/EX_CSC_dataset/rq_extension_a/EX_CSC_dataset_experiment_summary.md`
- RQ1: `experiments/EX_CSC_dataset/rq_extension_a/RQ1-boundary/rq1_comparison.md`
- RQ2: `experiments/EX_CSC_dataset/rq_extension_a/RQ2-parallel/parallel_generation_summary.md`
- RQ3/RQ4 budget-matched FL:
  `experiments/EX_CSC_dataset/rq_extension_a/RQ3-fault-localization/folded-budget-matched/multi-sfl/multi_sfl_budget_summary.md`

## Recommendation

`EX_CSC_dataset` is suitable for inclusion in the paper, but it should not be
merged silently.  It is best presented as part of a 32-program overall
benchmark, with a short note that the last 8 programs form a bounded numeric /
loop-heavy validation set.

The reason is simple: `EX_CSC_dataset` strengthens some conclusions and weakens
others.  This is useful scientifically, because it makes the evaluation less
cherry-picked, but it requires category-aware interpretation.

## RQ1: Boundary Completion

`EX_CSC_dataset` strengthens the RQ1 conclusion.

EX_CSC_dataset alone:

| Mode | Subjects | Mean Tests | Mean Total Nodes | Mean Leaf Nodes | Mean Covered | Mean Infeasible | Mean Empty | Mean Expanded | Mean Wall Time (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CSC-only | 8 | 6.125 | 18.750 | 9.000 | 6.125 | 2.875 | 1.750 | 0.000 | 2.102 |
| CSC+Boundary | 8 | 68.625 | 1163.250 | 582.125 | 68.625 | 513.375 | 0.000 | 63.500 | 35.086 |

Interpretation:

- Boundary expansion increases the average number of generated tests by about
  `+62.5` per program in EX_CSC_dataset.
- CSC-only leaves empty leaves in these programs, while CSC+Boundary removes
  them under the same max-iteration budget.
- This is consistent with the paper claim that Boundary makes CSC more
  complete for loop-bearing or bounded numeric programs.

Paper impact:

- Positive.
- The result makes RQ1 stronger, especially for programs where original CSC
  otherwise stops early with unresolved empty leaves.

## RQ2: Parallel Generation

`EX_CSC_dataset` slightly weakens the speedup magnitude but preserves the core RQ2
conclusion.

Previous 24-program RQ2 summary:

| Workers | Mean Time (s) | Mean Testcases | Mean CCT Nodes | Mean Speedup |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 68.675 | 165.792 | 926.167 | 1.000 baseline |
| 2 | 48.051 | 165.792 | 926.167 | 1.176 |
| 4 | 36.652 | 165.792 | 926.167 | 1.544 |
| 8 | 33.517 | 165.792 | 926.167 | 1.663 |

EX_CSC_dataset RQ2 summary:

| Workers | Mean Time (s) | Mean Testcases | Mean CCT Nodes | Mean Speedup |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 35.086 | 68.750 | 1163.250 | 1.000 |
| 2 | 28.222 | 68.750 | 1163.250 | 1.347 |
| 4 | 26.297 | 68.750 | 1163.250 | 1.473 |
| 8 | 26.178 | 68.750 | 1163.250 | 1.491 |

Approximate 32-program combined direction:

| Workers | Approx. Combined Mean Time (s) | Approx. Combined Mean Speedup |
| ---: | ---: | ---: |
| 1 | 65.316 | 1.000 baseline |
| 2 | 46.068 | 1.193 |
| 4 | 35.617 | 1.537 |
| 8 | 32.783 | 1.646 |

Interpretation:

- The generated artifacts remain stable across worker counts.
- Speedup remains positive and sublinear.
- `EX_CSC_dataset` slightly lowers the overall speedup because several programs have
  smaller frontier parallelism or heavier non-parallelizable overhead.

Paper impact:

- Slightly negative for raw speedup magnitude.
- Still acceptable and arguably healthier, because it demonstrates that the
  parallel extension works beyond the earlier 24-program set.

## RQ3/RQ4: Fault Localization

`EX_CSC_dataset` changes the fault-localization story in a useful way.  It weakens
Top-1, improves or preserves Top-3, and makes category-aware reporting more
important.

### Previous 24-program budget-matched results

Overall, N = 126:

| Top-K | Mean Budget | Folded | Best SFL |
| ---: | ---: | ---: | ---: |
| 1 | 2.8 | 84/126 (0.667) | Op2: 80/126 (0.635) |
| 2 | 5.0 | 99/126 (0.786) | Op2: 99/126 (0.786) |
| 3 | 7.3 | 106/126 (0.841) | Op2: 112/126 (0.889) |

Condition/control-flow mutants, N = 61:

| Top-K | Folded | Best SFL |
| ---: | ---: | ---: |
| 1 | 38/61 (0.623) | Op2: 35/61 (0.574) |
| 2 | 41/61 (0.672) | DStar/Op2: 43/61 (0.705) |
| 3 | 45/61 (0.738) | Op2: 53/61 (0.869) |

Statement/data-flow mutants, N = 65:

| Top-K | Folded | Best SFL |
| ---: | ---: | ---: |
| 1 | 46/65 (0.708) | Op2: 45/65 (0.692) |
| 2 | 58/65 (0.892) | Op2: 56/65 (0.862) |
| 3 | 61/65 (0.938) | Ochiai/DStar/Op2: 59/65 (0.908) |

### EX_CSC_dataset budget-matched results

Overall, N = 43:

| Top-K | Mean Budget | Folded | Best SFL |
| ---: | ---: | ---: | ---: |
| 1 | 2.2 | 18/43 (0.419) | Ochiai/DStar/Op2: 17/43 (0.395) |
| 2 | 3.9 | 29/43 (0.674) | Ochiai/DStar/Op2: 28/43 (0.651) |
| 3 | 5.9 | 39/43 (0.907) | Ochiai/DStar/Op2: 36/43 (0.837) |

Condition/control-flow mutants, N = 21:

| Top-K | Folded | Best SFL |
| ---: | ---: | ---: |
| 1 | 11/21 (0.524) | Ochiai/DStar/Op2: 10/21 (0.476) |
| 2 | 16/21 (0.762) | all SFL formulas: 14/21 (0.667) |
| 3 | 20/21 (0.952) | all SFL formulas: 16/21 (0.762) |

Statement/data-flow mutants, N = 22:

| Top-K | Folded | Best SFL |
| ---: | ---: | ---: |
| 1 | 7/22 (0.318) | all SFL formulas: 7/22 (0.318) |
| 2 | 13/22 (0.591) | Ochiai/DStar/Op2: 14/22 (0.636) |
| 3 | 19/22 (0.864) | Ochiai/DStar/Op2: 20/22 (0.909) |

### Approximate 32-program combined results

Overall, N = 169:

| Top-K | Folded | Op2 SFL | Direction |
| ---: | ---: | ---: | --- |
| 1 | 102/169 (0.604) | 97/169 (0.574) | Folded remains better |
| 2 | 128/169 (0.757) | 127/169 (0.751) | nearly tied, folded slightly better |
| 3 | 145/169 (0.858) | 148/169 (0.876) | SFL slightly better |

Condition/control-flow mutants, N = 82:

| Top-K | Folded | Op2 SFL | Direction |
| ---: | ---: | ---: | --- |
| 1 | 49/82 (0.598) | 45/82 (0.549) | Folded better |
| 2 | 57/82 (0.695) | 57/82 (0.695) | tied |
| 3 | 65/82 (0.793) | 69/82 (0.841) | SFL better |

Statement/data-flow mutants, N = 87:

| Top-K | Folded | Op2 SFL | Direction |
| ---: | ---: | ---: | --- |
| 1 | 53/87 (0.609) | 52/87 (0.598) | Folded slightly better |
| 2 | 71/87 (0.816) | 70/87 (0.805) | Folded slightly better |
| 3 | 80/87 (0.920) | 79/87 (0.908) | Folded slightly better |

Interpretation:

- Adding `EX_CSC_dataset` lowers the overall Top-1 folded hit rate compared with the
  original 24-program result.
- It improves the overall Top-3 folded result from `106/126 (0.841)` to
  approximately `145/169 (0.858)`.
- It makes the comparison with SFL more nuanced: folded remains competitive at
  small inspection budgets, while Op2 remains a very strong baseline at Top-3.
- `EX_CSC_dataset` especially strengthens the condition/control-flow story at Top-3
  within that dataset, but statement/data-flow mutants in EX_CSC_dataset are more
  challenging for folded localization than the previous 24-program set.

Paper impact:

- Mixed but acceptable.
- It is better to include `EX_CSC_dataset` if the paper emphasizes robustness and
  category-aware interpretation.
- It is risky to include it if the paper only wants a simple “our method beats
  SFL at every top-k” message, because that is not what the combined data says.

## Suggested Paper Presentation

Recommended structure:

1. Use a 32-program overall table for RQ1 and RQ2.
2. For RQ3/RQ4, show:
   - overall budget-matched comparison;
   - condition/control-flow category;
   - statement/data-flow category.
3. Avoid presenting only a single overall Top-1 number for fault localization.
   That would understate what the CCT method is doing.
4. In the analysis paragraph, explicitly say that `EX_CSC_dataset` increases the
   diversity of bounded numeric and loop-heavy programs, making the evaluation
   less favorable but more reliable.

## Final Decision

Recommended: include `EX_CSC_dataset` in the paper-facing experimental corpus.

Rationale:

- RQ1 becomes stronger.
- RQ2 remains stable and credible.
- RQ3/RQ4 becomes more nuanced but still defensible.
- The combined result is scientifically healthier than reporting only the
  easier or more favorable 24-program set.
