# Budget-Matched Fault Localization Summary

- Combined experiment: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/fault_localization_combined`
- CSC Top-r values: 1, 2, 3
- Definition: for each mutant and CSC Top-r, SFL receives the same number of unique source lines as the CSC Top-r region.

## overall

| CSC Strategy | SFL Strategy | CSC Top-r | Cases | Mean Budget Lines | CSC Hit Rate | SFL Budget Hit Rate | Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| aggregated.composite.condition_or_interval | sfl.ochiai | 1 | 126 | 3.214 | 0.516 | 0.706 | -0.190 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 2 | 126 | 5.849 | 0.675 | 0.825 | -0.151 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 3 | 126 | 8.302 | 0.722 | 0.937 | -0.214 |
| aggregated.condition_node | sfl.ochiai | 1 | 126 | 1.000 | 0.214 | 0.230 | -0.016 |
| aggregated.condition_node | sfl.ochiai | 2 | 126 | 1.810 | 0.294 | 0.397 | -0.103 |
| aggregated.condition_node | sfl.ochiai | 3 | 126 | 2.627 | 0.333 | 0.571 | -0.238 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 1 | 126 | 2.214 | 0.302 | 0.397 | -0.095 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 2 | 126 | 4.040 | 0.381 | 0.579 | -0.198 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 3 | 126 | 5.675 | 0.389 | 0.651 | -0.262 |
| aggregated.interval.statement_presence | sfl.ochiai | 1 | 126 | 2.095 | 0.286 | 0.381 | -0.095 |
| aggregated.interval.statement_presence | sfl.ochiai | 2 | 126 | 3.770 | 0.373 | 0.556 | -0.183 |
| aggregated.interval.statement_presence | sfl.ochiai | 3 | 126 | 5.389 | 0.397 | 0.651 | -0.254 |

## condition

| CSC Strategy | SFL Strategy | CSC Top-r | Cases | Mean Budget Lines | CSC Hit Rate | SFL Budget Hit Rate | Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| aggregated.composite.condition_or_interval | sfl.ochiai | 1 | 61 | 3.049 | 0.443 | 0.672 | -0.230 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 2 | 61 | 5.164 | 0.607 | 0.787 | -0.180 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 3 | 61 | 7.213 | 0.689 | 0.918 | -0.230 |
| aggregated.condition_node | sfl.ochiai | 1 | 61 | 1.000 | 0.443 | 0.033 | 0.410 |
| aggregated.condition_node | sfl.ochiai | 2 | 61 | 1.607 | 0.607 | 0.115 | 0.492 |
| aggregated.condition_node | sfl.ochiai | 3 | 61 | 2.328 | 0.689 | 0.393 | 0.295 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 1 | 61 | 2.049 | 0.000 | 0.148 | -0.148 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 2 | 61 | 3.557 | 0.000 | 0.377 | -0.377 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 3 | 61 | 4.885 | 0.000 | 0.393 | -0.393 |
| aggregated.interval.statement_presence | sfl.ochiai | 1 | 61 | 1.967 | 0.000 | 0.131 | -0.131 |
| aggregated.interval.statement_presence | sfl.ochiai | 2 | 61 | 3.230 | 0.000 | 0.361 | -0.361 |
| aggregated.interval.statement_presence | sfl.ochiai | 3 | 61 | 4.623 | 0.000 | 0.393 | -0.393 |

## statement

| CSC Strategy | SFL Strategy | CSC Top-r | Cases | Mean Budget Lines | CSC Hit Rate | SFL Budget Hit Rate | Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| aggregated.composite.condition_or_interval | sfl.ochiai | 1 | 65 | 3.369 | 0.585 | 0.738 | -0.154 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 2 | 65 | 6.492 | 0.738 | 0.862 | -0.123 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 3 | 65 | 9.323 | 0.754 | 0.954 | -0.200 |
| aggregated.condition_node | sfl.ochiai | 1 | 65 | 1.000 | 0.000 | 0.415 | -0.415 |
| aggregated.condition_node | sfl.ochiai | 2 | 65 | 2.000 | 0.000 | 0.662 | -0.662 |
| aggregated.condition_node | sfl.ochiai | 3 | 65 | 2.908 | 0.000 | 0.738 | -0.738 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 1 | 65 | 2.369 | 0.585 | 0.631 | -0.046 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 2 | 65 | 4.492 | 0.738 | 0.769 | -0.031 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 3 | 65 | 6.415 | 0.754 | 0.892 | -0.138 |
| aggregated.interval.statement_presence | sfl.ochiai | 1 | 65 | 2.215 | 0.554 | 0.615 | -0.062 |
| aggregated.interval.statement_presence | sfl.ochiai | 2 | 65 | 4.277 | 0.723 | 0.738 | -0.015 |
| aggregated.interval.statement_presence | sfl.ochiai | 3 | 65 | 6.108 | 0.769 | 0.892 | -0.123 |
