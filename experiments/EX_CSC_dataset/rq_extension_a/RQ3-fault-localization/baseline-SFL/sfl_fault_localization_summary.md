# SFL Baseline Fault Localization Summary

- Manifest mutants: 48
- Evaluated: 43
- No metrics: 5 (no TBFV failures / could not run)
- Errors: 0
- Total time: 0.62s

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 43 | 1.000 | 0.070 | 0.419 | 0.674 | 0.953 | 4.767 | 1.000 | 4.767 |
| SFL DStar (e=2) | 43 | 1.000 | 0.093 | 0.488 | 0.698 | 0.977 | 4.372 | 1.000 | 4.372 |
| SFL Ochiai | 43 | 1.000 | 0.093 | 0.488 | 0.698 | 0.977 | 4.372 | 1.000 | 4.372 |
| SFL Op2 | 43 | 1.000 | 0.116 | 0.535 | 0.698 | 0.977 | 4.233 | 1.000 | 4.233 |
| SFL Tarantula | 43 | 1.000 | 0.070 | 0.419 | 0.674 | 0.953 | 4.767 | 1.000 | 4.767 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 21
- Strategy rows: 105

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 21 | 1.000 | 0.000 | 0.476 | 0.714 | 0.905 | 4.667 | 1.000 | 4.667 |
| SFL DStar (e=2) | 21 | 1.000 | 0.000 | 0.571 | 0.714 | 0.952 | 4.381 | 1.000 | 4.381 |
| SFL Ochiai | 21 | 1.000 | 0.000 | 0.571 | 0.714 | 0.952 | 4.381 | 1.000 | 4.381 |
| SFL Op2 | 21 | 1.000 | 0.000 | 0.619 | 0.714 | 0.952 | 4.286 | 1.000 | 4.286 |
| SFL Tarantula | 21 | 1.000 | 0.000 | 0.476 | 0.714 | 0.905 | 4.667 | 1.000 | 4.667 |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 22
- Strategy rows: 110

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 22 | 1.000 | 0.136 | 0.364 | 0.636 | 1.000 | 4.864 | 1.000 | 4.864 |
| SFL DStar (e=2) | 22 | 1.000 | 0.182 | 0.409 | 0.682 | 1.000 | 4.364 | 1.000 | 4.364 |
| SFL Ochiai | 22 | 1.000 | 0.182 | 0.409 | 0.682 | 1.000 | 4.364 | 1.000 | 4.364 |
| SFL Op2 | 22 | 1.000 | 0.227 | 0.455 | 0.682 | 1.000 | 4.182 | 1.000 | 4.182 |
| SFL Tarantula | 22 | 1.000 | 0.136 | 0.364 | 0.636 | 1.000 | 4.864 | 1.000 | 4.864 |


## No-Metrics Mutants

| Mutant ID | Reason |
|---|---|
| BoundedAbundantNumber_M4 | no TBFV failures for SFL spectrum |
| BoundedIntPower_M3 | no TBFV failures for SFL spectrum |
| BoundedPronicNumber_M2 | no TBFV failures for SFL spectrum |
| BoundedPronicNumber_M4 | no TBFV failures for SFL spectrum |
| SaturatedIntPower_M3 | no TBFV failures for SFL spectrum |
