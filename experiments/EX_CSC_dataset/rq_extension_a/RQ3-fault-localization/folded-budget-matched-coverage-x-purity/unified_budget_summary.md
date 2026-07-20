# Experimental Unified Folded Ranking vs SFL

- Unified strategy: `experimental.unified_folded_source_candidate`
- SFL formula: `ochiai`
- Scope: experimental analysis only; existing folded composite, condition, and edge-partition strategies are not changed.
- Ranking: source-level condition candidates and folded edge-partition candidates are merged and sorted by the existing folded risk score.
- Budget matching: for unified Top-K, SFL receives the same number of unique source lines as the unified region.

## overall (N=43)

| Top-K | Mean Budget | Median Budget | Unified Hit Rate | SFL Hit Rate | Delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1.2 | 1.0 | 7/43 (0.163) | 5/43 (0.116) | +0.047 |
| 2 | 2.2 | 2.0 | 20/43 (0.465) | 17/43 (0.395) | +0.070 |
| 3 | 3.0 | 3.0 | 25/43 (0.581) | 22/43 (0.512) | +0.070 |

## condition (N=22)

| Top-K | Mean Budget | Median Budget | Unified Hit Rate | SFL Hit Rate | Delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1.1 | 1.0 | 1/22 (0.045) | 0/22 (0.000) | +0.045 |
| 2 | 2.2 | 2.0 | 11/22 (0.500) | 11/22 (0.500) | +0.000 |
| 3 | 2.8 | 3.0 | 16/22 (0.727) | 13/22 (0.591) | +0.136 |

## statement (N=21)

| Top-K | Mean Budget | Median Budget | Unified Hit Rate | SFL Hit Rate | Delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1.2 | 1.0 | 6/21 (0.286) | 5/21 (0.238) | +0.048 |
| 2 | 2.2 | 2.0 | 9/21 (0.429) | 6/21 (0.286) | +0.143 |
| 3 | 3.1 | 3.0 | 9/21 (0.429) | 9/21 (0.429) | +0.000 |

## Brief Observations

- Top-1: unified folded is ahead of SFL by 0.047 hit-rate points under a mean budget of 1.2 lines.
- Top-2: unified folded is ahead of SFL by 0.070 hit-rate points under a mean budget of 2.2 lines.
- Top-3: unified folded is ahead of SFL by 0.070 hit-rate points under a mean budget of 3.0 lines.