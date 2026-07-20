# EX_CSC_dataset RQ1/RQ2/RQ3 Experiment Summary

## RQ1: CSC-Only vs CSC+Boundary

The standard RQ1 bounded-completion comparison was rerun for all 8
EX_CSC_dataset original programs. Both sides use `max_iter=100`; the Boundary side uses
`mode=expanded`, `strategy=batch`, `workers=1`, and `range_bound=200`.

- CSC-only runs: 8/8 completed, 0 timeouts
- CSC+Boundary runs: 8/8 completed, 0 timeouts

| Mode | Subjects | Mean Tests | Mean Total Nodes | Mean Covered | Mean Infeasible | Mean Empty | Mean Expanded | Mean Wall Time (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CSC-only | 8 | 5.375 | 20.000 | 5.375 | 3.750 | 2.750 | 0.000 | 2.346 |
| CSC+Boundary | 8 | 70.125 | 1507.500 | 70.125 | 684.125 | 0.000 | 66.625 | 61.606 |

Interpretation: this subset now has the same RQ1 evidence structure as the
unified EX_CSC_dataset:
Boundary expansion removes all empty leaves and substantially increases
concrete covered leaves, at the expected cost of larger CCTs and longer
generation time.

See: `RQ1-boundary/rq1_comparison.md`

Original programs were also checked with Refined TBFV:
561 generated executable test cases passed, with 0 failed and 0 unsupported
checks.  See: `originals/original_rq1_report.md`

## RQ2: Batch Parallel CSC

The full paper-facing RQ2 package was rerun so that this subset uses the same
summary schema as the unified EX_CSC_dataset, including frontier-width metrics
and quantile representative-case tables.

| Workers | Completed | Mean Time(s) | Median Time(s) | Mean Testcases | Mean CCT Nodes | Mean Speedup | Median Speedup |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 8/8 | 48.648 | 55.209 | 70.125 | 1507.500 | 1.000 | 1.000 |
| 2 | 8/8 | 41.262 | 48.045 | 70.125 | 1507.500 | 1.258 | 1.161 |
| 4 | 8/8 | 38.156 | 42.890 | 70.125 | 1507.500 | 1.395 | 1.323 |
| 8 | 8/8 | 37.061 | 40.447 | 70.125 | 1507.500 | 1.482 | 1.319 |

Interpretation: all worker settings complete successfully. Parallelism helps,
but the gain saturates on these compact scalar-loop subjects, which is useful
negative evidence for RQ2: speedup depends on available frontier width and does
not scale linearly with worker count.

Valid paper-facing RQ2 output: `RQ2-parallel/parallel_generation_summary.md`

The earlier lightweight run has been moved to
`invalid_attempts/rq2_parallel_incomplete_no_frontier_metrics/` because it did
not preserve `mean_frontier_width`, `max_frontier_width`, or the full
`parallel_generation_summary.json` schema required by the paper tables.

## Mutant Detection Before RQ3

- Mutants: 48 total, 24 condition/control-flow and 24 statement/data-flow.
- TBFV-detected mutants: 46/48.
- No-failure mutants: 2/48.
- Total failed testcase-FSF checks among detected mutants: 1090.
- Condition mutants: 23/24 detected, 347 failed checks.
- Statement mutants: 23/24 detected, 743 failed checks.

No-failure mutants:

| mutant | category | note |
| --- | --- | --- |
| `BoundedAliquotClassifier_M3` | condition | boundary change did not trigger a generated FSF failure |
| `BoundedProperDivisorParity_M5` | statement | loop increment change did not trigger a generated FSF failure |

See: `FL/mutant_tbfv_detection_report.md`

## RQ3: Fault Localization

CCT reports were produced for all 48 mutants; 46 mutants had evaluable failure metrics.

The raw tool summaries `FL/fault_localization_summary.md` and
`FL/baseline-SFL/sfl_fault_localization_summary.md` still contain the legacy
diagnostic top-k set (`Top-1/3/5/10`).  For the paper-facing RQ3 comparison, we
use the budget-matched `Top-1/2/3` protocol below.

### Regenerated Fold-the-Tree and Budget-Matched Results

The missing folded reports and budget-matched SBFL comparison were regenerated
from the archived RQ3 artifacts.  No CSC/TBFV execution was rerun.

Folded composite results:

| Strategy | Evaluated | Top-1 | Top-2 | Top-3 |
| --- | ---: | ---: | ---: | ---: |
| aggregated.composite.folded_condition_or_edge_partition | 46 | 0.696 | 0.935 | 0.978 |

Budget-matched folded composite vs SFL:

| Category | Top-R | Mean Budget | Folded | Best SBFL |
| --- | ---: | ---: | ---: | ---: |
| overall | 1 | 2.2 | 32/46 (0.696) | 32/46 (0.696) |
| overall | 2 | 4.2 | 43/46 (0.935) | 38/46 (0.826) |
| overall | 3 | 6.0 | 45/46 (0.978) | 44/46 (0.957) |
| condition | 1 | 2.1 | 17/23 (0.739) | 14/23 (0.609) |
| condition | 2 | 3.8 | 22/23 (0.957) | 19/23 (0.826) |
| condition | 3 | 5.2 | 22/23 (0.957) | 23/23 (1.000) |
| statement | 1 | 2.4 | 15/23 (0.652) | 18/23 (0.783) |
| statement | 2 | 4.5 | 21/23 (0.913) | 19/23 (0.826) |
| statement | 3 | 6.8 | 23/23 (1.000) | 21/23 (0.913) |

Interpretation:

- Folded composite is excellent on EX_CSC_dataset: it reaches 93.5% by Top-2 and
  97.8% by Top-3.
- Under equal source-line budget, folded ties the best SBFL at Top-1 overall,
  and outperforms SBFL at Top-2 and Top-3 overall.
- The only nuance is condition faults at Top-3, where Op2 reaches 23/23 while
  folded reaches 22/23.  Statement faults strongly favor folded by Top-2/Top-3.

See: `FL/rq3_folded_budget_regenerated_report.md`.

## Artifacts

- Dataset with mutants: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/dataset/EX_CSC_dataset`
- Original RQ1 outputs: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/rq_extension_b/originals`
- RQ2 outputs: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/rq_extension_b/RQ2-parallel`
- RQ2 invalid lightweight attempt: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/rq_extension_b/invalid_attempts/rq2_parallel_incomplete_no_frontier_metrics`
- RQ3 outputs: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/rq_extension_b/FL`
