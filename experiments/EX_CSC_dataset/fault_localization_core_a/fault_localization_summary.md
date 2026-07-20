# Fault Localization Summary

## Overview

- Manifest mutants: 48
- Evaluation reports discovered: 48
- Evaluated mutants: 39
- Missing-result mutants: 0
- Invalid reports: 0
- Orphan reports: 0

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 39 | 1.000 | 0.538 | 0.718 | 0.846 | 0.974 | 2.641 | 13.701 | 2.846 | 8.487 |
| aggregated.condition_node | 39 | 0.462 | 0.308 | 0.410 | 0.436 | 0.462 | 1.889 | 1.000 | 1.000 | 1.889 |
| aggregated.interval.cct_only | 39 | 0.718 | 0.385 | 0.538 | 0.615 | 0.692 | 2.821 | 3.666 | 4.750 | 10.643 |
| aggregated.interval.edge_divergence_gated | 39 | 0.538 | 0.231 | 0.308 | 0.410 | 0.513 | 3.286 | 0.940 | 2.048 | 7.619 |
| aggregated.interval.statement_presence | 39 | 0.538 | 0.231 | 0.333 | 0.410 | 0.538 | 3.190 | 0.940 | 2.048 | 7.381 |
| raw.condition_node | 39 | 0.462 | 0.308 | 0.359 | 0.410 | 0.410 | 3.500 | 1.000 | 1.000 | 1.889 |
| raw.interval.cct_only | 39 | 0.718 | 0.385 | 0.410 | 0.410 | 0.462 | 19.536 | 2.642 | 4.393 | 10.643 |
| raw.interval.edge_divergence_gated | 39 | 0.538 | 0.231 | 0.256 | 0.256 | 0.308 | 38.238 | 1.111 | 2.048 | 7.619 |
| raw.interval.statement_presence | 39 | 0.538 | 0.231 | 0.256 | 0.256 | 0.308 | 38.048 | 1.111 | 2.048 | 7.524 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 18
- Strategy rows: 162

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 18 | 1.000 | 0.667 | 0.889 | 0.944 | 1.000 | 1.889 | 11.847 | 2.611 | 6.056 |
| aggregated.condition_node | 18 | 1.000 | 0.667 | 0.889 | 0.944 | 1.000 | 1.889 | 1.000 | 1.000 | 1.889 |
| aggregated.interval.cct_only | 18 | 1.000 | 0.778 | 0.833 | 0.944 | 0.944 | 2.000 | 3.072 | 3.389 | 8.333 |
| aggregated.interval.edge_divergence_gated | 18 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.846 | - | - |
| aggregated.interval.statement_presence | 18 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.846 | - | - |
| raw.condition_node | 18 | 1.000 | 0.667 | 0.778 | 0.889 | 0.889 | 3.500 | 1.000 | 1.000 | 1.889 |
| raw.interval.cct_only | 18 | 1.000 | 0.778 | 0.778 | 0.778 | 0.833 | 8.778 | 2.276 | 2.833 | 8.333 |
| raw.interval.edge_divergence_gated | 18 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.833 | - | - |
| raw.interval.statement_presence | 18 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.833 | - | - |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 21
- Strategy rows: 189

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 21 | 1.000 | 0.429 | 0.571 | 0.762 | 0.952 | 3.286 | 15.290 | 3.048 | 10.571 |
| aggregated.condition_node | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| aggregated.interval.cct_only | 21 | 0.476 | 0.048 | 0.286 | 0.333 | 0.476 | 4.300 | 4.175 | 7.200 | 14.800 |
| aggregated.interval.edge_divergence_gated | 21 | 1.000 | 0.429 | 0.571 | 0.762 | 0.952 | 3.286 | 1.020 | 2.048 | 7.619 |
| aggregated.interval.statement_presence | 21 | 1.000 | 0.429 | 0.619 | 0.762 | 1.000 | 3.190 | 1.020 | 2.048 | 7.381 |
| raw.condition_node | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| raw.interval.cct_only | 21 | 0.476 | 0.048 | 0.095 | 0.095 | 0.143 | 38.900 | 2.956 | 7.200 | 14.800 |
| raw.interval.edge_divergence_gated | 21 | 1.000 | 0.429 | 0.476 | 0.476 | 0.571 | 38.238 | 1.349 | 2.048 | 7.619 |
| raw.interval.statement_presence | 21 | 1.000 | 0.429 | 0.476 | 0.476 | 0.571 | 38.048 | 1.349 | 2.048 | 7.524 |
