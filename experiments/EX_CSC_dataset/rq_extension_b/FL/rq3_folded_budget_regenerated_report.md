# EX_CSC_dataset RQ3 Folded and Budget-Matched Report

Generated at: 2026-07-06

This report records the regenerated RQ3 fault-localization artifacts for
`EX_CSC_dataset`.  It complements the existing CCT localization and SFL baseline
reports by adding:

- fold-the-tree replay results;
- folded composite vs SBFL budget-matched comparison;
- multi-SBFL budget-matched comparison.

## Inputs

- Dataset: `dataset/EX_CSC_dataset`
- Experiment root: `experiments/EX_CSC_dataset/rq_extension_b/FL`
- Manifest: `experiments/EX_CSC_dataset/rq_extension_b/FL/dataset_snapshot/mutants_manifest.jsonl`
- Folded replay input layout:
  `experiments/EX_CSC_dataset/rq_extension_b/FL/aggregation_ready/mutants_manifest.jsonl`

The `aggregation_ready` manifest is a copy of the dataset snapshot manifest,
added to satisfy the replay scripts' expected input layout.

## Regenerated Commands

```bash
python3 replay_fault_localization_folded.py \
  --experiment-dir experiments/EX_CSC_dataset/rq_extension_b/FL \
  --output-dir experiments/EX_CSC_dataset/rq_extension_b/FL/folded-replay \
  --scoring-strategy density_log \
  --top-k 1,2,3
```

```bash
python3 folded_composite_budget_compare_sfl.py \
  --experiment-dir experiments/EX_CSC_dataset/rq_extension_b/FL \
  --output-dir experiments/EX_CSC_dataset/rq_extension_b/FL/folded-budget-matched \
  --top-r 1,2,3 \
  --scoring-strategy density_log
```

```bash
python3 folded_composite_multi_sfl_budget_compare.py \
  --budget-rows experiments/EX_CSC_dataset/rq_extension_b/FL/folded-budget-matched/budget_matched_rows.jsonl \
  --experiment-dir experiments/EX_CSC_dataset/rq_extension_b/FL \
  --output-dir experiments/EX_CSC_dataset/rq_extension_b/FL/folded-budget-matched/multi-sfl \
  --top-k 1,2,3
```

## Scale

- Manifest mutants: 48
- Evaluation reports discovered: 48
- Folded replay tasks: 48
- Folded evaluated mutants: 46
- Folded skipped mutants: 2

Skipped/no-failure mutants:

| Mutant | Category | Reason |
| --- | --- | --- |
| `BoundedAliquotClassifier_M3` | condition | no TBFV failure |
| `BoundedProperDivisorParity_M5` | statement | no TBFV failure |

## Fold-the-Tree Summary

| Strategy | Evaluated | Top-1 | Top-2 | Top-3 |
| --- | ---: | ---: | ---: | ---: |
| `aggregated.condition_node` | 46 | 17/46 (0.370) | 22/46 (0.478) | 22/46 (0.478) |
| `aggregated.interval.folded_edge_partition` | 46 | 15/46 (0.326) | 21/46 (0.457) | 23/46 (0.500) |
| `aggregated.composite.folded_condition_or_edge_partition` | 46 | 32/46 (0.696) | 43/46 (0.935) | 45/46 (0.978) |

Interpretation:

- The composite folded ranking is much stronger than either condition-only or
  edge-partition-only ranking.
- This confirms the paper-facing design choice that condition candidates and
  state-update edge partitions should be used as complementary views.

## Budget-Matched Folded Composite vs SFL

The folded method receives the union of the top-R condition and edge-partition
regions.  SFL receives the same number of unique source lines as its inspection
budget.

### Overall

| Top-R | Mean Budget | Folded | Ochiai SFL |
| ---: | ---: | ---: | ---: |
| 1 | 2.2 | 32/46 (0.696) | 32/46 (0.696) |
| 2 | 4.2 | 43/46 (0.935) | 38/46 (0.826) |
| 3 | 6.0 | 45/46 (0.978) | 41/46 (0.891) |

### Condition/Control-Flow Mutants

| Top-R | Mean Budget | Folded | Ochiai SFL |
| ---: | ---: | ---: | ---: |
| 1 | 2.1 | 17/23 (0.739) | 14/23 (0.609) |
| 2 | 3.8 | 22/23 (0.957) | 19/23 (0.826) |
| 3 | 5.2 | 22/23 (0.957) | 20/23 (0.870) |

### Statement/Data-Flow Mutants

| Top-R | Mean Budget | Folded | Ochiai SFL |
| ---: | ---: | ---: | ---: |
| 1 | 2.4 | 15/23 (0.652) | 18/23 (0.783) |
| 2 | 4.5 | 21/23 (0.913) | 19/23 (0.826) |
| 3 | 6.8 | 23/23 (1.000) | 21/23 (0.913) |

Interpretation:

- Folded and Ochiai tie at Top-1 overall.
- Folded is substantially stronger at Top-2 and Top-3 overall.
- For condition faults, folded is stronger at all three budgets.
- For statement faults, SFL is stronger at Top-1, but folded becomes stronger
  by Top-2 and Top-3.

## Multi-SBFL Budget-Matched Comparison

Best three SBFL formulas by overall mean Top-K hit rate:

| Rank | Formula | Mean Top-K Rate | Top Rates |
| ---: | --- | ---: | --- |
| 1 | `op2` | 0.826 | top1=0.696, top2=0.826, top3=0.957 |
| 2 | `dstar` | 0.804 | top1=0.696, top2=0.826, top3=0.891 |
| 3 | `ochiai` | 0.804 | top1=0.696, top2=0.826, top3=0.891 |

Overall comparison:

| Top-K | Mean Budget | Folded | Ochiai | Tarantula | DStar | Barinel | Op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.2 | 32/46 (0.696) | 32/46 (0.696) | 28/46 (0.609) | 32/46 (0.696) | 28/46 (0.609) | 32/46 (0.696) |
| 2 | 4.2 | 43/46 (0.935) | 38/46 (0.826) | 36/46 (0.783) | 38/46 (0.826) | 36/46 (0.783) | 38/46 (0.826) |
| 3 | 6.0 | 45/46 (0.978) | 41/46 (0.891) | 39/46 (0.848) | 41/46 (0.891) | 39/46 (0.848) | 44/46 (0.957) |

Interpretation:

- Op2 is the strongest SBFL formula on EX_CSC_dataset.
- Folded still beats Op2 at Top-2 and Top-3, and ties it at Top-1.
- EX_CSC_dataset therefore strengthens the paper's budget-matched FL evidence.

## Output Files

- Folded replay rows:
  `experiments/EX_CSC_dataset/rq_extension_b/FL/folded-replay/folded_replay_rows.jsonl`
- Folded replay summary:
  `experiments/EX_CSC_dataset/rq_extension_b/FL/folded-replay/folded_replay_summary.json`
- Budget-matched summary:
  `experiments/EX_CSC_dataset/rq_extension_b/FL/folded-budget-matched/budget_matched_summary.md`
- Multi-SBFL summary:
  `experiments/EX_CSC_dataset/rq_extension_b/FL/folded-budget-matched/multi-sfl/multi_sfl_budget_summary.md`
