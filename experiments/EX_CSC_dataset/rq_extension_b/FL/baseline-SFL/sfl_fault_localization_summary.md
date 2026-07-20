# SFL Baseline Fault Localization Summary

- Manifest mutants: 48
- Evaluated: 46
- No metrics: 2 (no TBFV failures / could not run)
- Errors: 0
- Total time: 0.85s

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 46 | 1.000 | 0.174 | 0.696 | 0.804 | 0.935 | 3.543 | 1.000 | 3.543 |
| SFL DStar (e=2) | 46 | 1.000 | 0.217 | 0.783 | 0.826 | 1.000 | 3.109 | 1.000 | 3.109 |
| SFL Ochiai | 46 | 1.000 | 0.217 | 0.783 | 0.826 | 1.000 | 3.109 | 1.000 | 3.109 |
| SFL Op2 | 46 | 1.000 | 0.239 | 0.783 | 0.826 | 1.000 | 2.978 | 1.000 | 2.978 |
| SFL Tarantula | 46 | 1.000 | 0.174 | 0.696 | 0.804 | 0.935 | 3.500 | 1.000 | 3.500 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 23
- Strategy rows: 115

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 23 | 1.000 | 0.000 | 0.652 | 0.783 | 0.957 | 3.783 | 1.000 | 3.783 |
| SFL DStar (e=2) | 23 | 1.000 | 0.043 | 0.739 | 0.826 | 1.000 | 3.391 | 1.000 | 3.391 |
| SFL Ochiai | 23 | 1.000 | 0.043 | 0.739 | 0.826 | 1.000 | 3.391 | 1.000 | 3.391 |
| SFL Op2 | 23 | 1.000 | 0.087 | 0.739 | 0.826 | 1.000 | 3.174 | 1.000 | 3.174 |
| SFL Tarantula | 23 | 1.000 | 0.000 | 0.652 | 0.783 | 0.957 | 3.783 | 1.000 | 3.783 |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 23
- Strategy rows: 115

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Hit Item Region | Mean Cumulative Region at First Hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SFL Barinel | 23 | 1.000 | 0.348 | 0.739 | 0.826 | 0.913 | 3.304 | 1.000 | 3.304 |
| SFL DStar (e=2) | 23 | 1.000 | 0.391 | 0.826 | 0.826 | 1.000 | 2.826 | 1.000 | 2.826 |
| SFL Ochiai | 23 | 1.000 | 0.391 | 0.826 | 0.826 | 1.000 | 2.826 | 1.000 | 2.826 |
| SFL Op2 | 23 | 1.000 | 0.391 | 0.826 | 0.826 | 1.000 | 2.783 | 1.000 | 2.783 |
| SFL Tarantula | 23 | 1.000 | 0.348 | 0.739 | 0.826 | 0.913 | 3.217 | 1.000 | 3.217 |


## No-Metrics Mutants

| Mutant ID | Reason |
|---|---|
| BoundedAliquotClassifier_M3 | no TBFV failures for SFL spectrum |
| BoundedProperDivisorParity_M5 | no TBFV failures for SFL spectrum |
