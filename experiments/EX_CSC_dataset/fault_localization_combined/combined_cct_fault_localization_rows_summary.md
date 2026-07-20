# Fault Localization Summary

## Overview

- Manifest mutants: 144
- Evaluation reports discovered: 126
- Evaluated mutants: 126
- Missing-result mutants: 0
- Invalid reports: 0
- Orphan reports: 0

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 126 | 0.992 | 0.516 | 0.722 | 0.849 | 0.960 | 2.760 | 14.518 | 3.064 | 8.768 |
| aggregated.condition_node | 126 | 0.476 | 0.214 | 0.333 | 0.389 | 0.452 | 3.250 | 1.000 | 1.000 | 3.133 |
| aggregated.interval.cct_only | 126 | 0.762 | 0.341 | 0.571 | 0.603 | 0.738 | 3.385 | 4.477 | 5.542 | 11.719 |
| aggregated.interval.edge_divergence_gated | 126 | 0.516 | 0.302 | 0.389 | 0.460 | 0.508 | 2.308 | 0.987 | 2.308 | 5.462 |
| aggregated.interval.statement_presence | 126 | 0.516 | 0.286 | 0.397 | 0.460 | 0.516 | 2.338 | 0.987 | 2.215 | 5.262 |
| raw.condition_node | 126 | 0.476 | 0.230 | 0.294 | 0.325 | 0.381 | 12.783 | 1.000 | 1.000 | 3.133 |
| raw.interval.cct_only | 126 | 0.762 | 0.357 | 0.421 | 0.452 | 0.492 | 18.104 | 3.853 | 5.240 | 11.396 |
| raw.interval.edge_divergence_gated | 126 | 0.516 | 0.294 | 0.302 | 0.333 | 0.373 | 17.215 | 1.023 | 2.308 | 5.477 |
| raw.interval.statement_presence | 126 | 0.516 | 0.286 | 0.294 | 0.302 | 0.333 | 19.262 | 1.023 | 2.169 | 5.262 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 61
- Strategy rows: 549

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 61 | 0.984 | 0.443 | 0.689 | 0.803 | 0.934 | 3.250 | 13.607 | 2.800 | 10.050 |
| aggregated.condition_node | 61 | 0.984 | 0.443 | 0.689 | 0.803 | 0.934 | 3.250 | 1.000 | 1.000 | 3.133 |
| aggregated.interval.cct_only | 61 | 0.984 | 0.590 | 0.770 | 0.820 | 0.934 | 3.083 | 4.169 | 3.583 | 9.833 |
| aggregated.interval.edge_divergence_gated | 61 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.929 | - | - |
| aggregated.interval.statement_presence | 61 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.929 | - | - |
| raw.condition_node | 61 | 0.984 | 0.475 | 0.607 | 0.672 | 0.787 | 12.783 | 1.000 | 1.000 | 3.133 |
| raw.interval.cct_only | 61 | 0.984 | 0.607 | 0.656 | 0.721 | 0.770 | 11.867 | 3.706 | 3.100 | 9.850 |
| raw.interval.edge_divergence_gated | 61 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.840 | - | - |
| raw.interval.statement_presence | 61 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.840 | - | - |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 65
- Strategy rows: 585

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 65 | 1.000 | 0.585 | 0.754 | 0.892 | 0.985 | 2.308 | 15.374 | 3.308 | 7.585 |
| aggregated.condition_node | 65 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| aggregated.interval.cct_only | 65 | 0.554 | 0.108 | 0.385 | 0.400 | 0.554 | 3.889 | 4.765 | 8.806 | 14.861 |
| aggregated.interval.edge_divergence_gated | 65 | 1.000 | 0.585 | 0.754 | 0.892 | 0.985 | 2.308 | 1.040 | 2.308 | 5.462 |
| aggregated.interval.statement_presence | 65 | 1.000 | 0.554 | 0.769 | 0.892 | 1.000 | 2.338 | 1.040 | 2.215 | 5.262 |
| raw.condition_node | 65 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| raw.interval.cct_only | 65 | 0.554 | 0.123 | 0.200 | 0.200 | 0.231 | 28.500 | 3.990 | 8.806 | 13.972 |
| raw.interval.edge_divergence_gated | 65 | 1.000 | 0.569 | 0.585 | 0.646 | 0.723 | 17.215 | 1.195 | 2.308 | 5.477 |
| raw.interval.statement_presence | 65 | 1.000 | 0.554 | 0.569 | 0.585 | 0.646 | 19.262 | 1.195 | 2.169 | 5.262 |
