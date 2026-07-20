# Experimental Unified Folded Ranking vs SFL

- Unified strategy: `experimental.unified_folded_source_candidate`
- SFL formula: `ochiai`
- Scope: experimental analysis only; existing folded composite, condition, and edge-partition strategies are not changed.
- Ranking: source-level condition candidates and folded edge-partition candidates are merged and sorted by the existing folded risk score.
- Budget matching: for unified Top-K, SFL receives the same number of unique source lines as the unified region.

## overall (N=126)

| Top-K | Mean Budget | Median Budget | Unified Hit Rate | SFL Hit Rate | Delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1.7 | 1.0 | 44/126 (0.349) | 46/126 (0.365) | -0.016 |
| 2 | 3.0 | 2.0 | 78/126 (0.619) | 81/126 (0.643) | -0.024 |
| 3 | 4.1 | 3.5 | 96/126 (0.762) | 91/126 (0.722) | +0.040 |
| 4 | 5.1 | 5.0 | 104/126 (0.825) | 96/126 (0.762) | +0.063 |
| 5 | 5.8 | 5.0 | 111/126 (0.881) | 100/126 (0.794) | +0.087 |

## condition (N=61)

| Top-K | Mean Budget | Median Budget | Unified Hit Rate | SFL Hit Rate | Delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1.5 | 1.0 | 3/61 (0.049) | 5/61 (0.082) | -0.033 |
| 2 | 2.7 | 2.0 | 28/61 (0.459) | 35/61 (0.574) | -0.115 |
| 3 | 3.4 | 3.0 | 37/61 (0.607) | 38/61 (0.623) | -0.016 |
| 4 | 4.1 | 4.0 | 43/61 (0.705) | 43/61 (0.705) | +0.000 |
| 5 | 4.7 | 5.0 | 49/61 (0.803) | 47/61 (0.770) | +0.033 |

## statement (N=65)

| Top-K | Mean Budget | Median Budget | Unified Hit Rate | SFL Hit Rate | Delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1.9 | 2.0 | 41/65 (0.631) | 41/65 (0.631) | +0.000 |
| 2 | 3.4 | 3.0 | 50/65 (0.769) | 46/65 (0.708) | +0.062 |
| 3 | 4.7 | 4.0 | 59/65 (0.908) | 53/65 (0.815) | +0.092 |
| 4 | 6.0 | 5.0 | 61/65 (0.938) | 53/65 (0.815) | +0.123 |
| 5 | 6.9 | 6.0 | 62/65 (0.954) | 53/65 (0.815) | +0.138 |

## Brief Observations

- Top-1: unified folded is behind SFL by 0.016 hit-rate points under a mean budget of 1.7 lines.
- Top-2: unified folded is behind SFL by 0.024 hit-rate points under a mean budget of 3.0 lines.
- Top-3: unified folded is ahead of SFL by 0.040 hit-rate points under a mean budget of 4.1 lines.
- Top-4: unified folded is ahead of SFL by 0.063 hit-rate points under a mean budget of 5.1 lines.
- Top-5: unified folded is ahead of SFL by 0.087 hit-rate points under a mean budget of 5.8 lines.