# Fault Localization Summary

## Overview

- Manifest mutants: 48
- Evaluation reports discovered: 48
- Evaluated mutants: 43
- Missing-result mutants: 0
- Invalid reports: 0
- Orphan reports: 0

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 43 | 0.512 | 0.302 | 0.442 | 0.488 | 0.512 | 1.955 | 2.673 | 1.000 | 1.818 |
| aggregated.condition_node | 43 | 0.512 | 0.302 | 0.442 | 0.488 | 0.512 | 1.955 | 1.000 | 1.000 | 1.818 |
| aggregated.interval.cct_only | 43 | 0.907 | 0.349 | 0.581 | 0.698 | 0.884 | 3.359 | 2.913 | 4.949 | 8.513 |
| aggregated.interval.edge_divergence_sibling_exclusive | 43 | 0.488 | 0.093 | 0.209 | 0.302 | 0.465 | 4.571 | 0.797 | 1.762 | 3.571 |
| aggregated.interval.edge_divergence_sibling_shared | 43 | 0.093 | 0.000 | 0.093 | 0.093 | 0.093 | 2.750 | 0.151 | 1.000 | 1.000 |
| aggregated.interval.statement_presence | 43 | 0.488 | 0.116 | 0.395 | 0.442 | 0.488 | 2.619 | 0.846 | 1.714 | 3.571 |
| raw.condition_node | 43 | 0.512 | 0.326 | 0.395 | 0.395 | 0.419 | 23.409 | 1.000 | 1.000 | 1.818 |
| raw.interval.cct_only | 43 | 0.907 | 0.326 | 0.535 | 0.558 | 0.581 | 23.103 | 2.105 | 4.359 | 8.385 |
| raw.interval.edge_divergence_sibling_exclusive | 43 | 0.488 | 0.093 | 0.163 | 0.209 | 0.279 | 27.381 | 0.751 | 1.714 | 3.619 |
| raw.interval.edge_divergence_sibling_shared | 43 | 0.093 | 0.000 | 0.047 | 0.047 | 0.070 | 9.250 | 0.078 | 1.000 | 1.000 |
| raw.interval.statement_presence | 43 | 0.488 | 0.140 | 0.279 | 0.279 | 0.326 | 13.524 | 0.829 | 1.714 | 3.571 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 21
- Strategy rows: 231

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 21 | 1.000 | 0.571 | 0.857 | 0.952 | 1.000 | 2.000 | 2.135 | 1.000 | 1.857 |
| aggregated.condition_node | 21 | 1.000 | 0.571 | 0.857 | 0.952 | 1.000 | 2.000 | 1.000 | 1.000 | 1.857 |
| aggregated.interval.cct_only | 21 | 1.000 | 0.714 | 0.762 | 0.857 | 1.000 | 2.143 | 2.366 | 2.619 | 4.524 |
| aggregated.interval.edge_divergence_sibling_exclusive | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.788 | - | - |
| aggregated.interval.edge_divergence_sibling_shared | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.106 | - | - |
| aggregated.interval.statement_presence | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.805 | - | - |
| raw.condition_node | 21 | 1.000 | 0.619 | 0.762 | 0.762 | 0.810 | 24.476 | 1.000 | 1.000 | 1.857 |
| raw.interval.cct_only | 21 | 1.000 | 0.667 | 0.762 | 0.762 | 0.810 | 18.857 | 1.741 | 1.571 | 4.286 |
| raw.interval.edge_divergence_sibling_exclusive | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.693 | - | - |
| raw.interval.edge_divergence_sibling_shared | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.053 | - | - |
| raw.interval.statement_presence | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.745 | - | - |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 22
- Strategy rows: 242

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggregated.composite.condition_or_interval | 22 | 0.045 | 0.045 | 0.045 | 0.045 | 0.045 | 1.000 | 3.186 | 1.000 | 1.000 |
| aggregated.condition_node | 22 | 0.045 | 0.045 | 0.045 | 0.045 | 0.045 | 1.000 | 1.000 | 1.000 | 1.000 |
| aggregated.interval.cct_only | 22 | 0.818 | 0.000 | 0.409 | 0.545 | 0.773 | 4.778 | 3.435 | 7.667 | 13.167 |
| aggregated.interval.edge_divergence_sibling_exclusive | 22 | 0.955 | 0.182 | 0.409 | 0.591 | 0.909 | 4.571 | 0.805 | 1.762 | 3.571 |
| aggregated.interval.edge_divergence_sibling_shared | 22 | 0.182 | 0.000 | 0.182 | 0.182 | 0.182 | 2.750 | 0.194 | 1.000 | 1.000 |
| aggregated.interval.statement_presence | 22 | 0.955 | 0.227 | 0.773 | 0.864 | 0.955 | 2.619 | 0.884 | 1.714 | 3.571 |
| raw.condition_node | 22 | 0.045 | 0.045 | 0.045 | 0.045 | 0.045 | 1.000 | 1.000 | 1.000 | 1.000 |
| raw.interval.cct_only | 22 | 0.818 | 0.000 | 0.318 | 0.364 | 0.364 | 28.056 | 2.454 | 7.611 | 13.167 |
| raw.interval.edge_divergence_sibling_exclusive | 22 | 0.955 | 0.182 | 0.318 | 0.409 | 0.545 | 27.381 | 0.807 | 1.714 | 3.619 |
| raw.interval.edge_divergence_sibling_shared | 22 | 0.182 | 0.000 | 0.091 | 0.091 | 0.136 | 9.250 | 0.102 | 1.000 | 1.000 |
| raw.interval.statement_presence | 22 | 0.955 | 0.273 | 0.545 | 0.545 | 0.636 | 13.524 | 0.909 | 1.714 | 3.571 |
