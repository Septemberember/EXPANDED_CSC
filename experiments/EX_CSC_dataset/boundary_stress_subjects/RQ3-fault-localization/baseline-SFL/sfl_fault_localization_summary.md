# SFL Baseline Fault Localization Summary

- Manifest mutants: 12
- Evaluated: 10
- No metrics: 2 (no TBFV failures / could not run)
- Errors: 0
- Total time: 0.84s

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 10 | 1.000 | 0.200 | 0.500 | 0.000 | 0.000 | 4.300 | 1.000 | 4.300 |
| SFL DStar (e=2) | 10 | 1.000 | 0.200 | 0.700 | 0.000 | 0.000 | 2.700 | 1.000 | 2.700 |
| SFL Ochiai | 10 | 1.000 | 0.200 | 0.700 | 0.000 | 0.000 | 2.700 | 1.000 | 2.700 |
| SFL Op2 | 10 | 1.000 | 0.200 | 0.700 | 0.000 | 0.000 | 2.700 | 1.000 | 2.700 |
| SFL Tarantula | 10 | 1.000 | 0.200 | 0.500 | 0.000 | 0.000 | 4.300 | 1.000 | 4.300 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 6
- Strategy rows: 30

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 6 | 1.000 | 0.000 | 0.500 | 0.000 | 0.000 | 4.000 | 1.000 | 4.000 |
| SFL DStar (e=2) | 6 | 1.000 | 0.000 | 0.833 | 0.000 | 0.000 | 2.667 | 1.000 | 2.667 |
| SFL Ochiai | 6 | 1.000 | 0.000 | 0.833 | 0.000 | 0.000 | 2.667 | 1.000 | 2.667 |
| SFL Op2 | 6 | 1.000 | 0.000 | 0.833 | 0.000 | 0.000 | 2.667 | 1.000 | 2.667 |
| SFL Tarantula | 6 | 1.000 | 0.000 | 0.500 | 0.000 | 0.000 | 4.000 | 1.000 | 4.000 |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 4
- Strategy rows: 20

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 4 | 1.000 | 0.500 | 0.500 | 0.000 | 0.000 | 4.750 | 1.000 | 4.750 |
| SFL DStar (e=2) | 4 | 1.000 | 0.500 | 0.500 | 0.000 | 0.000 | 2.750 | 1.000 | 2.750 |
| SFL Ochiai | 4 | 1.000 | 0.500 | 0.500 | 0.000 | 0.000 | 2.750 | 1.000 | 2.750 |
| SFL Op2 | 4 | 1.000 | 0.500 | 0.500 | 0.000 | 0.000 | 2.750 | 1.000 | 2.750 |
| SFL Tarantula | 4 | 1.000 | 0.500 | 0.500 | 0.000 | 0.000 | 4.750 | 1.000 | 4.750 |


## No-Metrics Mutants

| Mutant ID | Reason |
|---|---|
| BoundaryStressCounter_M8 | no TBFV failures for SFL spectrum |
| BoundaryStressMeter_M8 | no TBFV failures for SFL spectrum |
