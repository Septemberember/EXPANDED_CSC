# Experimental Analysis: Unified Folded Source-Candidate Ranking

This experiment is intentionally exploratory.  It does not modify the existing
folded composite, condition-node, edge-partition, or SFL pipelines.

## Experimental Setup

- Input folded artifacts:
  `experiments/EX_CSC_dataset/folded_fault_localization/fl_combined_3exp_144tasks/folded_replay_rows.jsonl`
- Compared datasets:
  `FL-060701-EX_CSC_dataset`, `FL-061001-EX_CSC_dataset`, and `fault_localization_core_b`
- Evaluated tasks: 126 mutants with at least one refined-TBFV failure
- Excluded tasks: 18 mutants with no detected TBFV failure
- SFL baseline: Ochiai
- Top-K values: 1, 2, 3, 4, 5

## Unified Ranking Definition

The unified ranking merges two source-level candidate types:

- condition candidates, whose region is the single condition line;
- folded edge-partition candidates, whose region is the set of ASSIGN/RETURN
  statement lines represented by that edge partition.

The merged list is sorted by the existing folded `risk_score`.  Ties are
resolved using the same style of stable evidence-oriented ordering as the
aggregated folded reports: fewer passing tests, more support, earlier raw rank,
smaller region, and earlier source line.

For each unified Top-K, the inspection budget is the number of unique source
lines covered by the Top-K unified candidates.  SFL receives the same number of
unique source lines from its own ranked list.

## Main Result

| Category | Top-K | Mean Budget | Unified Hit Rate | SFL Hit Rate | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| Overall | 1 | 1.7 | 44/126 (0.349) | 46/126 (0.365) | -0.016 |
| Overall | 2 | 3.0 | 78/126 (0.619) | 81/126 (0.643) | -0.024 |
| Overall | 3 | 4.1 | 96/126 (0.762) | 91/126 (0.722) | +0.040 |
| Overall | 4 | 5.1 | 104/126 (0.825) | 96/126 (0.762) | +0.063 |
| Overall | 5 | 5.8 | 111/126 (0.881) | 100/126 (0.794) | +0.087 |

The unified ranking is slightly weaker than SFL at Top-1 and Top-2, but becomes
better from Top-3 onward under the same line budget.

## Category-Level Behavior

For condition faults, the unified ranking is weak at very small K:

- Top-1: 3/61 vs SFL 5/61
- Top-2: 28/61 vs SFL 35/61
- Top-3: 37/61 vs SFL 38/61
- Top-4: 43/61 vs SFL 43/61
- Top-5: 49/61 vs SFL 47/61

For statement faults, the unified ranking is clearly stronger after Top-1:

- Top-1: 41/65 vs SFL 41/65
- Top-2: 50/65 vs SFL 46/65
- Top-3: 59/65 vs SFL 53/65
- Top-4: 61/65 vs SFL 53/65
- Top-5: 62/65 vs SFL 53/65

This suggests that the unified ranking naturally benefits state-update
localization, while condition faults still suffer from repeated or tied
condition evidence.

## Comparison With Existing Folded Composite

The existing folded composite inspects one condition candidate and one
edge-partition candidate at each rank depth.  Its budgets are larger:

- Composite Top-1 mean budget: 2.8 lines
- Composite Top-2 mean budget: 5.0 lines
- Composite Top-3 mean budget: 7.3 lines

The unified ranking is more budget-efficient:

- Unified Top-1 mean budget: 1.7 lines
- Unified Top-2 mean budget: 3.0 lines
- Unified Top-3 mean budget: 4.1 lines

However, this lower budget changes the behavior.  The composite is stronger at
early ranks because it always carries both diagnostic views, while the unified
ranking lets high-scoring edge candidates dominate some early positions.

This explains the apparent trade-off:

- composite ranking is better when we want guaranteed dual-view inspection at a
  small rank depth;
- unified ranking is cleaner and more compact as a single evidence list, and it
  becomes competitive once Top-K reaches 3 or more.

## Current Interpretation

The unified strategy is worth keeping as an experimental comparison, but it
should not replace the existing composite yet.  It answers a different question:
whether condition and state-update candidates can be treated as one homogeneous
source-candidate ranking when their risk-score formulas are aligned.

The current result is mixed but useful:

- It validates that a single folded ranking can beat SFL under matched source
  line budgets at Top-3/4/5.
- It also exposes why the composite design is still meaningful: the explicit
  condition-plus-edge structure protects condition-fault inspection at the
  earliest ranks.

