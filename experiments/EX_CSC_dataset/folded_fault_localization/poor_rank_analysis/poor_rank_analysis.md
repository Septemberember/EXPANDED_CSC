# Poor-Rank Fault Localization Analysis

- Folded rows: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/folded_fault_localization/fl_combined_3exp_144tasks/folded_replay_rows.jsonl`
- Budget rows: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/folded_fault_localization/budget_matched/budget_matched_rows.jsonl`
- Evaluated records: 126
- Poor-ranked records: 29
- Poor criterion: composite miss within Top-3, category-specific miss within Top-K, or budget-matched SFL hit while folded misses

## Poor Reasons

| Reason | Count |
|--------|------:|
| `composite_no_hit` | 18 |
| `condition_fault_condition_miss_top3` | 16 |
| `top3_sfl_hits_folded_misses` | 11 |
| `top2_sfl_hits_folded_misses` | 10 |
| `top1_sfl_hits_folded_misses` | 5 |
| `statement_fault_edge_miss_top3` | 2 |

## Poor Records by Fault Category

| Category | Count | Mean F_total | Mean P_total |
|----------|------:|-------------:|-------------:|
| condition | 20 | 70.95 | 36.85 |
| statement | 9 | 73.00 | 39.56 |

## Worst Tasks

| Mutant | Category | Op | Fault Line | F/P | Composite Rank | Cond Rank | Edge Rank | Reasons |
|--------|----------|----|-----------:|-----|---------------:|----------:|----------:|---------|
| AddLoop_M3 | condition | ROR | 14 | 2/203 | — | — | — | `composite_no_hit`, `condition_fault_condition_miss_top3` |
| BubbleSortFive_M2 | condition | ROR | 30 | 60/48 | — | 6 | — | `composite_no_hit`, `condition_fault_condition_miss_top3` |
| GappedSwapFive_M2 | condition | ROR | 18 | 60/6 | — | 4 | — | `composite_no_hit`, `condition_fault_condition_miss_top3`, `top2_sfl_hits_folded_misses`, `top3_sfl_hits_folded_misses` |
| LoopBubbleSortFive_M1 | condition | ROR | 10 | 24/0 | — | 4 | — | `composite_no_hit`, `condition_fault_condition_miss_top3`, `top3_sfl_hits_folded_misses` |
| LoopBubbleSortFive_M2 | condition | CR | 20 | 24/24 | — | 8 | — | `composite_no_hit`, `condition_fault_condition_miss_top3` |
| LoopBubbleSortFive_M3 | condition | ROR | 15 | 24/0 | — | 6 | — | `composite_no_hit`, `condition_fault_condition_miss_top3` |
| LoopSelectionSortFive_M1 | condition | ROR | 21 | 127/23 | — | 6 | — | `composite_no_hit`, `condition_fault_condition_miss_top3`, `top3_sfl_hits_folded_misses` |
| LoopSelectionSortFive_M3 | condition | ROR | 32 | 74/49 | — | 9 | — | `composite_no_hit`, `condition_fault_condition_miss_top3` |
| MedianOfSix_M2 | condition | ROR | 19 | 120/72 | — | 4 | — | `composite_no_hit`, `condition_fault_condition_miss_top3`, `top2_sfl_hits_folded_misses`, `top3_sfl_hits_folded_misses` |
| MedianOfSix_M6 | statement | RVR | 67 | 384/0 | — | — | 5 | `composite_no_hit`, `statement_fault_edge_miss_top3`, `top2_sfl_hits_folded_misses`, `top3_sfl_hits_folded_misses` |
| MedianWindowFive_M2 | condition | ROR | 18 | 44/22 | — | 4 | — | `composite_no_hit`, `condition_fault_condition_miss_top3`, `top3_sfl_hits_folded_misses` |
| OddEvenSortFive_M2 | condition | ROR | 22 | 48/0 | — | 6 | — | `composite_no_hit`, `condition_fault_condition_miss_top3`, `top3_sfl_hits_folded_misses` |
| SelectionSortFive_M1 | condition | ROR | 5 | 87/141 | — | 4 | — | `composite_no_hit`, `condition_fault_condition_miss_top3`, `top2_sfl_hits_folded_misses`, `top3_sfl_hits_folded_misses` |
| SelectionSortFive_M2 | condition | ROR | 35 | 216/48 | — | 8 | — | `composite_no_hit`, `condition_fault_condition_miss_top3` |
| SelectionSortFive_M3 | condition | ROR | 72 | 255/40 | — | 13 | — | `composite_no_hit`, `condition_fault_condition_miss_top3` |
| TailRotateSortFive_M3 | condition | ROR | 20 | 48/0 | — | 5 | — | `composite_no_hit`, `condition_fault_condition_miss_top3`, `top3_sfl_hits_folded_misses` |
| TailRotateSortFive_M6 | statement | SUR | 25 | 24/64 | — | — | 4 | `composite_no_hit`, `statement_fault_edge_miss_top3` |
| WaterBillCaculator_M1 | condition | BOR | 5 | 1/31 | — | 4 | — | `composite_no_hit`, `condition_fault_condition_miss_top3` |
| LoopBubbleSortFive_M5 | statement | SUR | 25 | 24/12 | 2 | — | 2 | `top3_sfl_hits_folded_misses` |
| MedianWindowFive_M6 | statement | RVR | 38 | 76/8 | 2 | — | 2 | `top2_sfl_hits_folded_misses` |
| OddEvenSortFive_M4 | statement | SUR | 19 | 24/40 | 2 | — | 2 | `top1_sfl_hits_folded_misses`, `top2_sfl_hits_folded_misses`, `top3_sfl_hits_folded_misses` |
| RewardCapLoop_M4 | statement | CR | 13 | 22/66 | 2 | — | 2 | `top1_sfl_hits_folded_misses` |
| ScoreNormalizer_M4 | statement | AOR | 14 | 60/108 | 2 | — | 2 | `top1_sfl_hits_folded_misses` |
| WaterBillCaculator_M2 | condition | ROR | 9 | 27/4 | 2 | 2 | — | `top1_sfl_hits_folded_misses` |
| WaterBillCaculator_M5 | statement | CR | 12 | 27/4 | 2 | — | 2 | `top1_sfl_hits_folded_misses` |
| MaxOfFive_M2 | condition | ROR | 13 | 62/16 | 3 | 3 | — | `top2_sfl_hits_folded_misses` |
| OddEvenSortFive_M3 | condition | ROR | 6 | 48/0 | 3 | 3 | — | `top2_sfl_hits_folded_misses` |
| PairSortCheck_M2 | condition | ROR | 13 | 68/10 | 3 | 3 | — | `top2_sfl_hits_folded_misses` |
| TailRotateSortFive_M5 | statement | SUR | 17 | 16/54 | 3 | — | 3 | `top2_sfl_hits_folded_misses` |

## Concrete Case Snapshots

### AddLoop_M3

- Category/operator: `condition` / `ROR`
- Ground-truth line: `14`
- Failed/passed tests: `2` / `203`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 3 | `x < -100` | 0.0098 | 2/203 | 0.0098 |
| 2 | 3 | `x > 100` | 0.0025 | 1/203 | 0.0049 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[5]` | `3:x > 100` | `true` | `None:None` | 1.0000 | 2/0 | 1.0000 |

### BubbleSortFive_M2

- Category/operator: `condition` / `ROR`
- Ground-truth line: `30`
- Failed/passed tests: `60` / `48`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 4 | `a > b` | 0.5556 | 60/48 | 0.5556 |
| 2 | 9 | `b > c` | 0.5556 | 60/48 | 0.5556 |
| 3 | 14 | `c > d` | 0.5556 | 60/48 | 0.5556 |
| 4 | 19 | `d > e` | 0.5556 | 60/48 | 0.5556 |
| 5 | 25 | `a > b` | 0.5556 | 60/48 | 0.5556 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[20, 21, 22]` | `19:d > e` | `true` | `25:a > b` | 0.8000 | 60/15 | 0.8000 |
| 2 | `None` | `[47, 48, 49]` | `46:b > c` | `true` | `52:a > b` | 0.6667 | 60/30 | 0.6667 |
| 3 | `None` | `[57]` | `52:a > b` | `false` | `None:None` | 0.5818 | 48/30 | 0.7273 |
| 4 | `None` | `[36, 37, 38]` | `35:c > d` | `true` | `41:a > b` | 0.5143 | 36/6 | 0.8571 |
| 5 | `None` | `[31, 32, 33]` | `30:b < c` | `true` | `35:c > d` | 0.4500 | 36/12 | 0.7500 |

### GappedSwapFive_M2

- Category/operator: `condition` / `ROR`
- Ground-truth line: `18`
- Failed/passed tests: `60` / `6`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`, `top2_sfl_hits_folded_misses`, `top3_sfl_hits_folded_misses`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 3 | `a > b` | 0.9091 | 60/6 | 0.9091 |
| 2 | 8 | `b > c` | 0.9091 | 60/6 | 0.9091 |
| 3 | 13 | `a > b` | 0.9091 | 60/6 | 0.9091 |
| 4 | 18 | `c < d` | 0.9091 | 60/6 | 0.9091 |
| 5 | 23 | `b > c` | 0.9091 | 60/6 | 0.9091 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[39, 40, 41]` | `38:c > d` | `true` | `43:b > c` | 1.0000 | 60/0 | 1.0000 |
| 2 | `None` | `[9, 10, 11]` | `8:b > c` | `true` | `13:a > b` | 0.6061 | 40/4 | 0.9091 |
| 3 | `None` | `[34, 35, 36]` | `33:d > e` | `true` | `38:c > d` | 0.6000 | 36/0 | 1.0000 |
| 4 | `None` | `[44, 45, 46]` | `43:b > c` | `true` | `48:a > b` | 0.6000 | 36/0 | 1.0000 |
| 5 | `None` | `[53]` | `48:a > b` | `false` | `None:None` | 0.6000 | 36/6 | 1.0000 |

### LoopBubbleSortFive_M1

- Category/operator: `condition` / `ROR`
- Ground-truth line: `10`
- Failed/passed tests: `24` / `0`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`, `top3_sfl_hits_folded_misses`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 4 | `pass < 4` | 1.0000 | 24/0 | 1.0000 |
| 2 | 5 | `pass <= 3` | 1.0000 | 24/0 | 1.0000 |
| 3 | 5 | `a > b` | 1.0000 | 24/0 | 1.0000 |
| 4 | 10 | `pass <= 2` | 1.0000 | 24/0 | 1.0000 |
| 5 | 10 | `b < c` | 1.0000 | 24/0 | 1.0000 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[25]` | `20:pass == 0` | `false` | `4:pass < 4` | 1.0000 | 24/0 | 1.0000 |
| 2 | `None` | `[25]` | `20:d > e` | `false` | `4:pass < 4` | 1.0000 | 24/0 | 1.0000 |
| 3 | `None` | `[27]` | `4:pass < 4` | `false` | `None:None` | 1.0000 | 24/0 | 1.0000 |
| 4 | `None` | `[16, 17, 18]` | `15:c > d` | `true` | `20:pass == 0` | 0.6667 | 16/0 | 1.0000 |
| 5 | `None` | `[21, 22, 23]` | `20:d > e` | `true` | `4:pass < 4` | 0.6667 | 16/0 | 1.0000 |

### LoopBubbleSortFive_M2

- Category/operator: `condition` / `CR`
- Ground-truth line: `20`
- Failed/passed tests: `24` / `24`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 4 | `pass < 4` | 0.5000 | 24/24 | 0.5000 |
| 2 | 5 | `pass <= 3` | 0.5000 | 24/24 | 0.5000 |
| 3 | 5 | `a > b` | 0.5000 | 24/24 | 0.5000 |
| 4 | 10 | `pass <= 2` | 0.5000 | 24/24 | 0.5000 |
| 5 | 10 | `b > c` | 0.5000 | 24/24 | 0.5000 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[21, 22, 23]` | `20:d > e` | `true` | `4:pass < 4` | 1.0000 | 24/0 | 1.0000 |
| 2 | `None` | `[25]` | `20:pass == 1` | `false` | `4:pass < 4` | 0.5000 | 24/24 | 0.5000 |
| 3 | `None` | `[25]` | `20:d > e` | `false` | `4:pass < 4` | 0.5000 | 24/24 | 0.5000 |
| 4 | `None` | `[27]` | `4:pass < 4` | `false` | `None:None` | 0.5000 | 24/24 | 0.5000 |
| 5 | `None` | `[11, 12, 13]` | `10:b > c` | `true` | `15:pass <= 1` | 0.4167 | 20/20 | 0.5000 |

### LoopBubbleSortFive_M3

- Category/operator: `condition` / `ROR`
- Ground-truth line: `15`
- Failed/passed tests: `24` / `0`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 4 | `pass < 4` | 1.0000 | 24/0 | 1.0000 |
| 2 | 5 | `pass <= 3` | 1.0000 | 24/0 | 1.0000 |
| 3 | 5 | `a > b` | 1.0000 | 24/0 | 1.0000 |
| 4 | 10 | `pass <= 2` | 1.0000 | 24/0 | 1.0000 |
| 5 | 10 | `b > c` | 1.0000 | 24/0 | 1.0000 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[25]` | `20:pass == 0` | `false` | `4:pass < 4` | 1.0000 | 24/0 | 1.0000 |
| 2 | `None` | `[25]` | `20:d > e` | `false` | `4:pass < 4` | 1.0000 | 24/0 | 1.0000 |
| 3 | `None` | `[27]` | `4:pass < 4` | `false` | `None:None` | 1.0000 | 24/0 | 1.0000 |
| 4 | `None` | `[6, 7, 8]` | `5:a > b` | `true` | `10:pass <= 2` | 0.6667 | 16/0 | 1.0000 |
| 5 | `None` | `[11, 12, 13]` | `10:b > c` | `true` | `15:pass <= 1` | 0.6667 | 16/0 | 1.0000 |

### LoopSelectionSortFive_M1

- Category/operator: `condition` / `ROR`
- Ground-truth line: `21`
- Failed/passed tests: `127` / `23`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`, `top3_sfl_hits_folded_misses`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 4 | `position < 4` | 0.8467 | 127/23 | 0.8467 |
| 2 | 5 | `position == 0` | 0.8467 | 127/23 | 0.8467 |
| 3 | 6 | `b < a` | 0.8467 | 127/23 | 0.8467 |
| 4 | 11 | `c < a` | 0.8467 | 127/23 | 0.8467 |
| 5 | 16 | `d < a` | 0.8467 | 127/23 | 0.8467 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[60]` | `21:e > a` | `false` | `4:position < 4` | 0.8467 | 127/23 | 0.8467 |
| 2 | `None` | `[62]` | `4:position < 4` | `false` | `None:None` | 0.8467 | 127/23 | 0.8467 |
| 3 | `None` | `[22, 23, 24]` | `21:e > a` | `true` | `4:position < 4` | 0.5906 | 75/0 | 1.0000 |
| 4 | `None` | `[38, 39, 40, 60]` | `37:e < b` | `true` | `4:position < 4` | 0.4567 | 58/0 | 1.0000 |
| 5 | `None` | `[55, 56, 57, 60]` | `54:e < d` | `true` | `4:position < 4` | 0.4397 | 66/12 | 0.8462 |

### LoopSelectionSortFive_M3

- Category/operator: `condition` / `ROR`
- Ground-truth line: `32`
- Failed/passed tests: `74` / `49`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 4 | `position < 4` | 0.6016 | 74/49 | 0.6016 |
| 2 | 5 | `position == 0` | 0.6016 | 74/49 | 0.6016 |
| 3 | 6 | `b < a` | 0.6016 | 74/49 | 0.6016 |
| 4 | 11 | `c < a` | 0.6016 | 74/49 | 0.6016 |
| 5 | 16 | `d < a` | 0.6016 | 74/49 | 0.6016 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[44, 45, 46]` | `43:d < c` | `true` | `48:e < c` | 0.6187 | 68/33 | 0.6733 |
| 2 | `None` | `[60]` | `48:e < c` | `false` | `4:position < 4` | 0.6016 | 74/49 | 0.6016 |
| 3 | `None` | `[60]` | `21:e < a` | `false` | `4:position < 4` | 0.6016 | 74/49 | 0.6016 |
| 4 | `None` | `[62]` | `4:position < 4` | `false` | `None:None` | 0.6016 | 74/49 | 0.6016 |
| 5 | `None` | `[28, 29, 30]` | `27:c < b` | `true` | `32:d > b` | 0.3728 | 40/18 | 0.6897 |

### MedianOfSix_M2

- Category/operator: `condition` / `ROR`
- Ground-truth line: `19`
- Failed/passed tests: `120` / `72`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `condition_fault_condition_miss_top3`, `top2_sfl_hits_folded_misses`, `top3_sfl_hits_folded_misses`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 3 | `a > b` | 0.6250 | 120/72 | 0.6250 |
| 2 | 8 | `b > c` | 0.6250 | 120/72 | 0.6250 |
| 3 | 13 | `a > b` | 0.6250 | 120/72 | 0.6250 |
| 4 | 19 | `d > c` | 0.6250 | 120/72 | 0.6250 |
| 5 | 35 | `e < c` | 0.6250 | 120/72 | 0.6250 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[67]` | `51:f < c` | `false` | `None:None` | 0.4500 | 72/24 | 0.7500 |
| 2 | `None` | `[9, 10, 11]` | `8:b > c` | `true` | `13:a > b` | 0.4167 | 80/48 | 0.6250 |
| 3 | `None` | `[36, 37, 38]` | `35:e < c` | `true` | `39:b > c` | 0.4083 | 84/60 | 0.5833 |
| 4 | `None` | `[52, 53, 54]` | `51:f < c` | `true` | `55:b > c` | 0.4083 | 84/60 | 0.5833 |
| 5 | `None` | `[4, 5, 6]` | `3:a > b` | `true` | `8:b > c` | 0.3125 | 60/36 | 0.6250 |

### MedianOfSix_M6

- Category/operator: `statement` / `RVR`
- Ground-truth line: `67`
- Failed/passed tests: `384` / `0`
- Composite best rank: `—`
- Reasons: `composite_no_hit`, `statement_fault_edge_miss_top3`, `top2_sfl_hits_folded_misses`, `top3_sfl_hits_folded_misses`

Top condition candidates:

| Rank | Line | Condition | Risk | F/P | Density |
|-----:|-----:|-----------|-----:|-----|--------:|
| 1 | 3 | `a > b` | 1.0000 | 384/0 | 1.0000 |
| 2 | 8 | `b > c` | 1.0000 | 384/0 | 1.0000 |
| 3 | 13 | `a > b` | 1.0000 | 384/0 | 1.0000 |
| 4 | 19 | `d < c` | 1.0000 | 384/0 | 1.0000 |
| 5 | 35 | `e < c` | 1.0000 | 384/0 | 1.0000 |

Top edge-partition candidates:

| Rank | Kind | Lines | From | Outcome | To | Risk | F/P | Density |
|-----:|------|-------|------|---------|----|-----:|-----|--------:|
| 1 | `None` | `[20, 21, 22]` | `19:d < c` | `true` | `23:b > c` | 0.7500 | 288/0 | 1.0000 |
| 2 | `None` | `[36, 37, 38]` | `35:e < c` | `true` | `39:b > c` | 0.7500 | 288/0 | 1.0000 |
| 3 | `None` | `[52, 53, 54]` | `51:f < c` | `true` | `55:b > c` | 0.7500 | 288/0 | 1.0000 |
| 4 | `None` | `[9, 10, 11]` | `8:b > c` | `true` | `13:a > b` | 0.6667 | 256/0 | 1.0000 |
| 5 | `None` | `[67]` | `51:f < c` | `false` | `None:None` | 0.5000 | 192/0 | 1.0000 |
