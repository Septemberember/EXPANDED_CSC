# Fault Localization Summary

## Overview

- Manifest mutants: 48
- Evaluation reports discovered: 48
- Evaluated mutants: 42
- Missing-result mutants: 0
- Invalid reports: 0
- Orphan reports: 0

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 42 | 1.000 | 0.524 | 0.762 | 0.929 | 1.000 | 2.167 | 11.430 | 3.000 | 6.976 |
| aggregated.condition_node | 42 | 0.476 | 0.262 | 0.381 | 0.452 | 0.476 | 2.000 | 1.000 | 1.000 | 2.000 |
| aggregated.interval.cct_only | 42 | 0.786 | 0.381 | 0.595 | 0.595 | 0.786 | 2.879 | 3.867 | 4.576 | 8.970 |
| aggregated.interval.edge_divergence_gated | 42 | 0.524 | 0.262 | 0.381 | 0.476 | 0.524 | 2.318 | 0.977 | 2.182 | 5.182 |
| aggregated.interval.statement_presence | 42 | 0.524 | 0.262 | 0.381 | 0.476 | 0.524 | 2.409 | 0.977 | 2.045 | 5.000 |
| raw.condition_node | 42 | 0.476 | 0.286 | 0.333 | 0.357 | 0.476 | 3.050 | 1.000 | 1.000 | 2.000 |
| raw.interval.cct_only | 42 | 0.786 | 0.405 | 0.429 | 0.452 | 0.500 | 13.485 | 3.143 | 4.242 | 8.939 |
| raw.interval.edge_divergence_gated | 42 | 0.524 | 0.262 | 0.262 | 0.310 | 0.333 | 11.273 | 1.038 | 2.182 | 5.182 |
| raw.interval.statement_presence | 42 | 0.524 | 0.262 | 0.262 | 0.262 | 0.262 | 15.864 | 1.038 | 1.909 | 4.909 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 20
- Strategy rows: 180

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 20 | 1.000 | 0.550 | 0.800 | 0.950 | 1.000 | 2.000 | 9.837 | 2.800 | 6.650 |
| aggregated.condition_node | 20 | 1.000 | 0.550 | 0.800 | 0.950 | 1.000 | 2.000 | 1.000 | 1.000 | 2.000 |
| aggregated.interval.cct_only | 20 | 1.000 | 0.750 | 0.850 | 0.850 | 1.000 | 1.850 | 3.390 | 2.450 | 5.950 |
| aggregated.interval.edge_divergence_gated | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.878 | - | - |
| aggregated.interval.statement_presence | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.878 | - | - |
| raw.condition_node | 20 | 1.000 | 0.600 | 0.700 | 0.750 | 1.000 | 3.050 | 1.000 | 1.000 | 2.000 |
| raw.interval.cct_only | 20 | 1.000 | 0.750 | 0.750 | 0.800 | 0.850 | 4.000 | 2.846 | 1.900 | 5.950 |
| raw.interval.edge_divergence_gated | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.830 | - | - |
| raw.interval.statement_presence | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.830 | - | - |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 22
- Strategy rows: 198

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 22 | 1.000 | 0.500 | 0.727 | 0.909 | 1.000 | 2.318 | 12.878 | 3.182 | 7.273 |
| aggregated.condition_node | 22 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| aggregated.interval.cct_only | 22 | 0.591 | 0.045 | 0.364 | 0.364 | 0.591 | 4.462 | 4.301 | 7.846 | 13.615 |
| aggregated.interval.edge_divergence_gated | 22 | 1.000 | 0.500 | 0.727 | 0.909 | 1.000 | 2.318 | 1.067 | 2.182 | 5.182 |
| aggregated.interval.statement_presence | 22 | 1.000 | 0.500 | 0.727 | 0.909 | 1.000 | 2.409 | 1.067 | 2.045 | 5.000 |
| raw.condition_node | 22 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| raw.interval.cct_only | 22 | 0.591 | 0.091 | 0.136 | 0.136 | 0.182 | 28.077 | 3.412 | 7.846 | 13.538 |
| raw.interval.edge_divergence_gated | 22 | 1.000 | 0.500 | 0.500 | 0.591 | 0.636 | 11.273 | 1.227 | 2.182 | 5.182 |
| raw.interval.statement_presence | 22 | 1.000 | 0.500 | 0.500 | 0.500 | 0.500 | 15.864 | 1.227 | 1.909 | 4.909 |
