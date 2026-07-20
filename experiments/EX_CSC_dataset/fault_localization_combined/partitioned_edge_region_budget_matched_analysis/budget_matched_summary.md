# Budget-Matched Fault Localization Summary

- Combined experiment: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/fault_localization_combined`
- Replay predictions: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/fault_localization_combined/seed_replay_analysis`, `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/fault_localization_combined/seed_shared_replay_analysis`
- CSC Top-r values: 1, 2, 3
- Definition: for each mutant and CSC Top-r, SFL receives the same number of unique source lines as the CSC Top-r region.
- SEED composite strategy: `aggregated.composite.condition_or_seed_interval` uses condition-node predictions plus `aggregated.interval.edge_divergence_sibling_exclusive`.
- SEED-S composite strategy: `aggregated.composite.condition_or_seed_shared_interval` uses condition-node predictions plus `aggregated.interval.edge_divergence_sibling_shared`.
- Partitioned composite strategy: `aggregated.composite.condition_or_seed_partitioned_interval` uses condition-node predictions plus both SEED-X and SEED-S interval predictions.
- Partitioned Edge-Region strategy: `aggregated.interval.partitioned_edge_region` merges non-empty SEED-X and SEED-S statement regions into one risk-score-ordered edge-region ranking.
- Condition + Partitioned Edge-Region strategy: `aggregated.composite.condition_or_partitioned_edge_region` uses condition-node predictions plus the unified partitioned edge-region ranking.

## overall

| CSC Strategy | SFL Strategy | CSC Top-r | Cases | Mean Budget Lines | CSC Hit Rate | SFL Budget Hit Rate | Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| aggregated.composite.condition_or_interval | sfl.ochiai | 1 | 126 | 3.214 | 0.516 | 0.706 | -0.190 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 2 | 126 | 5.849 | 0.675 | 0.825 | -0.151 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 3 | 126 | 8.302 | 0.722 | 0.937 | -0.214 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 1 | 126 | 2.976 | 0.500 | 0.675 | -0.175 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 2 | 126 | 5.063 | 0.643 | 0.778 | -0.135 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 3 | 126 | 7.056 | 0.714 | 0.865 | -0.151 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 1 | 126 | 3.151 | 0.516 | 0.706 | -0.190 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 2 | 126 | 5.770 | 0.659 | 0.817 | -0.159 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 3 | 126 | 8.214 | 0.706 | 0.921 | -0.214 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 1 | 126 | 3.603 | 0.571 | 0.730 | -0.159 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 2 | 126 | 6.151 | 0.714 | 0.825 | -0.111 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 3 | 126 | 8.619 | 0.762 | 0.944 | -0.183 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 1 | 126 | 1.659 | 0.294 | 0.349 | -0.056 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 2 | 126 | 2.484 | 0.373 | 0.460 | -0.087 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 3 | 126 | 3.397 | 0.413 | 0.603 | -0.190 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 1 | 126 | 2.214 | 0.302 | 0.397 | -0.095 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 2 | 126 | 4.040 | 0.381 | 0.579 | -0.198 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 3 | 126 | 5.675 | 0.389 | 0.651 | -0.262 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 1 | 126 | 2.151 | 0.302 | 0.389 | -0.087 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 2 | 126 | 3.960 | 0.365 | 0.571 | -0.206 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 3 | 126 | 5.587 | 0.373 | 0.643 | -0.270 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 1 | 126 | 0.659 | 0.079 | 0.175 | -0.095 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 2 | 126 | 0.675 | 0.079 | 0.183 | -0.103 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 3 | 126 | 0.770 | 0.079 | 0.190 | -0.111 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 1 | 126 | 1.976 | 0.286 | 0.357 | -0.071 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 2 | 126 | 3.254 | 0.349 | 0.476 | -0.127 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 3 | 126 | 4.429 | 0.381 | 0.579 | -0.198 |

## condition

| CSC Strategy | SFL Strategy | CSC Top-r | Cases | Mean Budget Lines | CSC Hit Rate | SFL Budget Hit Rate | Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| aggregated.composite.condition_or_interval | sfl.ochiai | 1 | 61 | 3.049 | 0.443 | 0.672 | -0.230 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 2 | 61 | 5.164 | 0.607 | 0.787 | -0.180 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 3 | 61 | 7.213 | 0.689 | 0.918 | -0.230 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 1 | 61 | 2.787 | 0.443 | 0.623 | -0.180 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 2 | 61 | 4.230 | 0.607 | 0.689 | -0.082 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 3 | 61 | 5.836 | 0.689 | 0.852 | -0.164 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 1 | 61 | 3.000 | 0.443 | 0.672 | -0.230 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 2 | 61 | 5.098 | 0.607 | 0.770 | -0.164 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 3 | 61 | 7.148 | 0.689 | 0.885 | -0.197 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 1 | 61 | 3.426 | 0.443 | 0.689 | -0.246 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 2 | 61 | 5.492 | 0.607 | 0.787 | -0.180 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 3 | 61 | 7.574 | 0.689 | 0.934 | -0.246 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 1 | 61 | 1.574 | 0.443 | 0.098 | 0.344 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 2 | 61 | 2.197 | 0.607 | 0.230 | 0.377 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 3 | 61 | 2.984 | 0.689 | 0.459 | 0.230 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 1 | 61 | 2.049 | 0.000 | 0.148 | -0.148 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 2 | 61 | 3.557 | 0.000 | 0.377 | -0.377 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 3 | 61 | 4.885 | 0.000 | 0.393 | -0.393 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 1 | 61 | 2.000 | 0.000 | 0.131 | -0.131 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 2 | 61 | 3.492 | 0.000 | 0.361 | -0.361 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 3 | 61 | 4.820 | 0.000 | 0.393 | -0.393 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 1 | 61 | 0.574 | 0.000 | 0.016 | -0.016 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 2 | 61 | 0.590 | 0.000 | 0.016 | -0.016 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 3 | 61 | 0.656 | 0.000 | 0.033 | -0.033 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 1 | 61 | 1.787 | 0.000 | 0.098 | -0.098 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 2 | 61 | 2.623 | 0.000 | 0.213 | -0.213 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 3 | 61 | 3.508 | 0.000 | 0.295 | -0.295 |

## statement

| CSC Strategy | SFL Strategy | CSC Top-r | Cases | Mean Budget Lines | CSC Hit Rate | SFL Budget Hit Rate | Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| aggregated.composite.condition_or_interval | sfl.ochiai | 1 | 65 | 3.369 | 0.585 | 0.738 | -0.154 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 2 | 65 | 6.492 | 0.738 | 0.862 | -0.123 |
| aggregated.composite.condition_or_interval | sfl.ochiai | 3 | 65 | 9.323 | 0.754 | 0.954 | -0.200 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 1 | 65 | 3.154 | 0.554 | 0.723 | -0.169 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 2 | 65 | 5.846 | 0.677 | 0.862 | -0.185 |
| aggregated.composite.condition_or_partitioned_edge_region | sfl.ochiai | 3 | 65 | 8.200 | 0.738 | 0.877 | -0.138 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 1 | 65 | 3.292 | 0.585 | 0.738 | -0.154 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 2 | 65 | 6.400 | 0.708 | 0.862 | -0.154 |
| aggregated.composite.condition_or_seed_interval | sfl.ochiai | 3 | 65 | 9.215 | 0.723 | 0.954 | -0.231 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 1 | 65 | 3.769 | 0.692 | 0.769 | -0.077 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 2 | 65 | 6.769 | 0.815 | 0.862 | -0.046 |
| aggregated.composite.condition_or_seed_partitioned_interval | sfl.ochiai | 3 | 65 | 9.600 | 0.831 | 0.954 | -0.123 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 1 | 65 | 1.738 | 0.154 | 0.585 | -0.431 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 2 | 65 | 2.754 | 0.154 | 0.677 | -0.523 |
| aggregated.composite.condition_or_seed_shared_interval | sfl.ochiai | 3 | 65 | 3.785 | 0.154 | 0.738 | -0.585 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 1 | 65 | 2.369 | 0.585 | 0.631 | -0.046 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 2 | 65 | 4.492 | 0.738 | 0.769 | -0.031 |
| aggregated.interval.edge_divergence_gated | sfl.ochiai | 3 | 65 | 6.415 | 0.754 | 0.892 | -0.138 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 1 | 65 | 2.292 | 0.585 | 0.631 | -0.046 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 2 | 65 | 4.400 | 0.708 | 0.769 | -0.062 |
| aggregated.interval.edge_divergence_sibling_exclusive | sfl.ochiai | 3 | 65 | 6.308 | 0.723 | 0.877 | -0.154 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 1 | 65 | 0.738 | 0.154 | 0.323 | -0.169 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 2 | 65 | 0.754 | 0.154 | 0.338 | -0.185 |
| aggregated.interval.edge_divergence_sibling_shared | sfl.ochiai | 3 | 65 | 0.877 | 0.154 | 0.338 | -0.185 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 1 | 65 | 2.154 | 0.554 | 0.600 | -0.046 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 2 | 65 | 3.846 | 0.677 | 0.723 | -0.046 |
| aggregated.interval.partitioned_edge_region | sfl.ochiai | 3 | 65 | 5.292 | 0.738 | 0.846 | -0.108 |
