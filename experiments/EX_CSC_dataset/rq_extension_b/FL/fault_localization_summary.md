# Fault Localization Summary

## Overview

- Manifest mutants: 48
- Evaluation reports discovered: 48
- Evaluated mutants: 46
- Missing-result mutants: 0
- Invalid reports: 0
- Orphan reports: 0

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 46 | 0.500 | 0.261 | 0.370 | 0.500 | 0.500 | 2.261 | 2.582 | 1.000 | 2.087 |
| aggregated.condition_node | 46 | 0.500 | 0.261 | 0.370 | 0.500 | 0.500 | 2.261 | 1.000 | 1.000 | 2.087 |
| aggregated.interval.cct_only | 46 | 0.804 | 0.413 | 0.500 | 0.522 | 0.783 | 3.243 | 2.989 | 5.595 | 7.784 |
| aggregated.interval.edge_divergence_sibling_exclusive | 46 | 0.478 | 0.065 | 0.217 | 0.391 | 0.478 | 3.773 | 0.792 | 1.455 | 3.909 |
| aggregated.interval.edge_divergence_sibling_shared | 46 | 0.109 | 0.065 | 0.109 | 0.109 | 0.109 | 1.800 | 0.169 | 1.200 | 1.200 |
| aggregated.interval.statement_presence | 46 | 0.500 | 0.130 | 0.370 | 0.478 | 0.500 | 2.609 | 0.857 | 1.565 | 4.261 |
| raw.condition_node | 46 | 0.500 | 0.261 | 0.326 | 0.370 | 0.370 | 19.217 | 1.000 | 1.000 | 2.000 |
| raw.interval.cct_only | 46 | 0.804 | 0.348 | 0.413 | 0.413 | 0.435 | 40.108 | 2.632 | 5.081 | 7.919 |
| raw.interval.edge_divergence_sibling_exclusive | 46 | 0.478 | 0.043 | 0.152 | 0.174 | 0.217 | 40.500 | 0.630 | 1.318 | 3.909 |
| raw.interval.edge_divergence_sibling_shared | 46 | 0.109 | 0.065 | 0.087 | 0.087 | 0.087 | 4.800 | 0.134 | 1.200 | 1.200 |
| raw.interval.statement_presence | 46 | 0.500 | 0.109 | 0.196 | 0.217 | 0.283 | 21.000 | 0.763 | 1.565 | 4.348 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 23
- Strategy rows: 253

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 23 | 1.000 | 0.522 | 0.739 | 1.000 | 1.000 | 2.261 | 2.267 | 1.000 | 2.087 |
| aggregated.condition_node | 23 | 1.000 | 0.522 | 0.739 | 1.000 | 1.000 | 2.261 | 1.000 | 1.000 | 2.087 |
| aggregated.interval.cct_only | 23 | 1.000 | 0.826 | 0.913 | 0.957 | 1.000 | 1.435 | 2.529 | 3.696 | 4.130 |
| aggregated.interval.edge_divergence_sibling_exclusive | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.756 | - | - |
| aggregated.interval.edge_divergence_sibling_shared | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.131 | - | - |
| aggregated.interval.statement_presence | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.813 | - | - |
| raw.condition_node | 23 | 1.000 | 0.522 | 0.652 | 0.739 | 0.739 | 19.217 | 1.000 | 1.000 | 2.000 |
| raw.interval.cct_only | 23 | 1.000 | 0.696 | 0.783 | 0.783 | 0.783 | 15.826 | 2.128 | 2.870 | 3.957 |
| raw.interval.edge_divergence_sibling_exclusive | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.639 | - | - |
| raw.interval.edge_divergence_sibling_shared | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.116 | - | - |
| raw.interval.statement_presence | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.755 | - | - |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 23
- Strategy rows: 253

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 2.896 | - | - |
| aggregated.condition_node | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| aggregated.interval.cct_only | 23 | 0.609 | 0.000 | 0.087 | 0.087 | 0.565 | 6.214 | 3.448 | 8.714 | 13.786 |
| aggregated.interval.edge_divergence_sibling_exclusive | 23 | 0.957 | 0.130 | 0.435 | 0.783 | 0.957 | 3.773 | 0.827 | 1.455 | 3.909 |
| aggregated.interval.edge_divergence_sibling_shared | 23 | 0.217 | 0.130 | 0.217 | 0.217 | 0.217 | 1.800 | 0.207 | 1.200 | 1.200 |
| aggregated.interval.statement_presence | 23 | 1.000 | 0.261 | 0.739 | 0.957 | 1.000 | 2.609 | 0.901 | 1.565 | 4.261 |
| raw.condition_node | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 1.000 | - | - |
| raw.interval.cct_only | 23 | 0.609 | 0.000 | 0.043 | 0.043 | 0.087 | 80.000 | 3.136 | 8.714 | 14.429 |
| raw.interval.edge_divergence_sibling_exclusive | 23 | 0.957 | 0.087 | 0.304 | 0.348 | 0.435 | 40.500 | 0.621 | 1.318 | 3.909 |
| raw.interval.edge_divergence_sibling_shared | 23 | 0.217 | 0.130 | 0.174 | 0.174 | 0.174 | 4.800 | 0.151 | 1.200 | 1.200 |
| raw.interval.statement_presence | 23 | 1.000 | 0.217 | 0.391 | 0.435 | 0.565 | 21.000 | 0.772 | 1.565 | 4.348 |
