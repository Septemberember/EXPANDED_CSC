# Fault Localization Summary

## Overview

- Manifest mutants: 12
- Evaluation reports discovered: 12
- Evaluated mutants: 10
- Missing-result mutants: 0
- Invalid reports: 0
- Orphan reports: 0

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-2 | Top-3 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 10 | 0.600 | 0.400 | 0.000 | 0.400 | 2.167 | 4.364 | 1.000 | 2.167 |
| aggregated.condition_node | 10 | 0.600 | 0.400 | 0.000 | 0.400 | 2.167 | 1.000 | 1.000 | 2.167 |
| aggregated.interval.cct_only | 10 | 1.000 | 0.700 | 0.000 | 0.800 | 3.500 | 4.405 | 9.800 | 13.000 |
| aggregated.interval.edge_divergence_sibling_exclusive | 10 | 0.400 | 0.200 | 0.000 | 0.300 | 2.250 | 0.429 | 1.000 | 1.500 |
| aggregated.interval.edge_divergence_sibling_shared | 10 | 0.100 | 0.000 | 0.000 | 0.100 | 3.000 | 0.033 | 1.000 | 1.000 |
| aggregated.interval.statement_presence | 10 | 0.400 | 0.200 | 0.000 | 0.400 | 1.500 | 0.429 | 1.000 | 1.500 |
| raw.condition_node | 10 | 0.600 | 0.400 | 0.000 | 0.400 | 3.333 | 1.000 | 1.000 | 2.167 |
| raw.interval.cct_only | 10 | 1.000 | 0.800 | 0.000 | 0.800 | 46.300 | 5.886 | 10.500 | 13.100 |
| raw.interval.edge_divergence_sibling_exclusive | 10 | 0.400 | 0.100 | 0.000 | 0.200 | 3.250 | 0.469 | 1.000 | 1.500 |
| raw.interval.edge_divergence_sibling_shared | 10 | 0.100 | 0.000 | 0.000 | 0.000 | 89.000 | 0.001 | 1.000 | 1.000 |
| raw.interval.statement_presence | 10 | 0.400 | 0.200 | 0.000 | 0.400 | 1.500 | 0.470 | 1.000 | 1.500 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 6
- Strategy rows: 66

| Strategy | Rows | Hit Rate | Top-1 | Top-2 | Top-3 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 6 | 1.000 | 0.667 | 0.000 | 0.667 | 2.167 | 3.803 | 1.000 | 2.167 |
| aggregated.condition_node | 6 | 1.000 | 0.667 | 0.000 | 0.667 | 2.167 | 1.000 | 1.000 | 2.167 |
| aggregated.interval.cct_only | 6 | 1.000 | 0.833 | 0.000 | 1.000 | 1.333 | 3.784 | 5.500 | 6.833 |
| aggregated.interval.edge_divergence_sibling_exclusive | 6 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.449 | - | - |
| aggregated.interval.edge_divergence_sibling_shared | 6 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.027 | - | - |
| aggregated.interval.statement_presence | 6 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.449 | - | - |
| raw.condition_node | 6 | 1.000 | 0.667 | 0.000 | 0.667 | 3.333 | 1.000 | 1.000 | 2.167 |
| raw.interval.cct_only | 6 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 4.981 | 6.667 | 7.000 |
| raw.interval.edge_divergence_sibling_exclusive | 6 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.474 | - | - |
| raw.interval.edge_divergence_sibling_shared | 6 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.001 | - | - |
| raw.interval.statement_presence | 6 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.475 | - | - |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 4
- Strategy rows: 44

| Strategy | Rows | Hit Rate | Top-1 | Top-2 | Top-3 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 4 | 0.000 | 0.000 | 0.000 | 0.000 | - | 5.205 | - | - |
| aggregated.condition_node | 4 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| aggregated.interval.cct_only | 4 | 1.000 | 0.500 | 0.000 | 0.500 | 6.750 | 5.337 | 16.250 | 22.250 |
| aggregated.interval.edge_divergence_sibling_exclusive | 4 | 1.000 | 0.500 | 0.000 | 0.750 | 2.250 | 0.401 | 1.000 | 1.500 |
| aggregated.interval.edge_divergence_sibling_shared | 4 | 0.250 | 0.000 | 0.000 | 0.250 | 3.000 | 0.042 | 1.000 | 1.000 |
| aggregated.interval.statement_presence | 4 | 1.000 | 0.500 | 0.000 | 1.000 | 1.500 | 0.401 | 1.000 | 1.500 |
| raw.condition_node | 4 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| raw.interval.cct_only | 4 | 1.000 | 0.500 | 0.000 | 0.500 | 114.250 | 7.242 | 16.250 | 22.250 |
| raw.interval.edge_divergence_sibling_exclusive | 4 | 1.000 | 0.250 | 0.000 | 0.500 | 3.250 | 0.461 | 1.000 | 1.500 |
| raw.interval.edge_divergence_sibling_shared | 4 | 0.250 | 0.000 | 0.000 | 0.000 | 89.000 | 0.001 | 1.000 | 1.000 |
| raw.interval.statement_presence | 4 | 1.000 | 0.500 | 0.000 | 1.000 | 1.500 | 0.462 | 1.000 | 1.500 |
