# Budget-Matched Top-1 SFL-Win Cases for Condition + PER

This document lists the cases where `aggregated.composite.condition_or_partitioned_edge_region` misses at CSC Top-1, while SFL hits under the same line budget.

## Filter

- Source rows: `partitioned_edge_region_budget_matched_analysis/budget_matched_rows.jsonl`
- CSC strategy: `aggregated.composite.condition_or_partitioned_edge_region`
- CSC Top-r: `1`
- Condition: `cct_hit == false` and `sfl_budget_hit == true`
- `N` means `inspection_budget_lines`, i.e., the number of unique source lines in the CSC Top-1 region. SFL is allowed to inspect exactly its Top-N ranked lines.

## Summary

- Total cases: 31
- By fault category: `condition`=11, `statement`=20
- By experiment: `FL-060701-EX_CSC_dataset`=6, `FL-061001-EX_CSC_dataset`=14, `fault_localization_core_b`=11

## Cases

| # | Experiment | Subject | Mutant | Category | Operator | N | Ground Truth | CSC Top-1 Lines | SFL Top-N Lines |
| ---: | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | `FL-060701-EX_CSC_dataset` | `LoopBubbleSortFive` | `LoopBubbleSortFive_M1` | `condition` | `ROR` | 4 | 10 | `4, 6, 7, 8` | `3, 4, 5, 10` |
| 2 | `FL-060701-EX_CSC_dataset` | `OddEvenSortFive` | `OddEvenSortFive_M4` | `statement` | `SUR` | 5 | 19 | `4, 12, 13, 14, 28` | `12, 13, 18, 19, 20` |
| 3 | `FL-060701-EX_CSC_dataset` | `SelectionSort` | `SelectionSortFive_M1` | `condition` | `ROR` | 5 | 5 | `20, 40, 41, 42, 53` | `3, 4, 5, 6, 11` |
| 4 | `FL-060701-EX_CSC_dataset` | `WaterBillCaculator` | `WaterBillCaculator_M3` | `condition` | `ROR` | 2 | 11 | `8, 16` | `11, 14` |
| 5 | `FL-060701-EX_CSC_dataset` | `WaterBillCaculator` | `WaterBillCaculator_M4` | `statement` | `CR` | 2 | 10 | `9, 16` | `9, 10` |
| 6 | `FL-060701-EX_CSC_dataset` | `WaterBillCaculator` | `WaterBillCaculator_M5` | `statement` | `CR` | 2 | 12 | `11, 16` | `11, 12` |
| 7 | `FL-061001-EX_CSC_dataset` | `GradePolicy` | `GradePolicy_M3` | `condition` | `BOR` | 3 | 13 | `12, 16, 18` | `13, 16, 27` |
| 8 | `FL-061001-EX_CSC_dataset` | `GradePolicy` | `GradePolicy_M5` | `statement` | `AOR` | 2 | 22 | `12, 27` | `22, 27` |
| 9 | `FL-061001-EX_CSC_dataset` | `GradePolicy` | `GradePolicy_M6` | `statement` | `RVR` | 3 | 27 | `12, 14, 18` | `10, 11, 27` |
| 10 | `FL-061001-EX_CSC_dataset` | `InventoryReorder` | `InventoryReorder_M3` | `condition` | `BOR` | 3 | 13 | `12, 14, 18` | `13, 14, 18` |
| 11 | `FL-061001-EX_CSC_dataset` | `InventoryReorder` | `InventoryReorder_M5` | `statement` | `CR` | 2 | 22 | `12, 27` | `22, 27` |
| 12 | `FL-061001-EX_CSC_dataset` | `InventoryReorder` | `InventoryReorder_M6` | `statement` | `RVR` | 3 | 27 | `10, 11, 12` | `10, 11, 27` |
| 13 | `FL-061001-EX_CSC_dataset` | `MedianOfSix` | `MedianOfSix_M1` | `condition` | `ROR` | 4 | 3 | `51, 56, 57, 58` | `3, 14, 15, 16` |
| 14 | `FL-061001-EX_CSC_dataset` | `MedianOfSix` | `MedianOfSix_M2` | `condition` | `ROR` | 4 | 19 | `3, 4, 5, 6` | `3, 8, 13, 19` |
| 15 | `FL-061001-EX_CSC_dataset` | `MedianOfSix` | `MedianOfSix_M4` | `statement` | `SUR` | 4 | 25 | `51, 56, 57, 58` | `20, 24, 25, 26` |
| 16 | `FL-061001-EX_CSC_dataset` | `MedianOfSix` | `MedianOfSix_M5` | `statement` | `SUR` | 2 | 37 | `51, 67` | `36, 37` |
| 17 | `FL-061001-EX_CSC_dataset` | `PairSortCheck` | `PairSortCheck_M2` | `condition` | `ROR` | 4 | 13 | `3, 19, 20, 21` | `3, 8, 13, 18` |
| 18 | `FL-061001-EX_CSC_dataset` | `PairSortCheck` | `PairSortCheck_M4` | `statement` | `SUR` | 2 | 5 | `43, 48` | `4, 5` |
| 19 | `FL-061001-EX_CSC_dataset` | `PairSortCheck` | `PairSortCheck_M5` | `statement` | `SUR` | 4 | 40 | `3, 4, 5, 6` | `39, 40, 41, 44` |
| 20 | `FL-061001-EX_CSC_dataset` | `TaxBracket` | `TaxBracket_M5` | `statement` | `AOR` | 3 | 30 | `10, 11, 12` | `10, 11, 30` |
| 21 | `fault_localization_core_b` | `MarginAdjustLoop` | `MarginAdjustLoop_M3` | `condition` | `BOR` | 3 | 18 | `17, 19, 23` | `18, 19, 23` |
| 22 | `fault_localization_core_b` | `MarginAdjustLoop` | `MarginAdjustLoop_M4` | `statement` | `CR` | 2 | 13 | `18, 23` | `13, 18` |
| 23 | `fault_localization_core_b` | `MedianWindowFive` | `MedianWindowFive_M4` | `statement` | `SUR` | 4 | 15 | `23, 29, 30, 31` | `14, 15, 16, 29` |
| 24 | `fault_localization_core_b` | `MedianWindowFive` | `MedianWindowFive_M5` | `statement` | `SUR` | 4 | 30 | `3, 4, 5, 6` | `3, 29, 30, 31` |
| 25 | `fault_localization_core_b` | `RewardCapLoop` | `RewardCapLoop_M3` | `condition` | `BOR` | 3 | 18 | `17, 19, 23` | `13, 18, 19` |
| 26 | `fault_localization_core_b` | `RewardCapLoop` | `RewardCapLoop_M4` | `statement` | `CR` | 3 | 13 | `17, 19, 23` | `13, 18, 19` |
| 27 | `fault_localization_core_b` | `RewardCapLoop` | `RewardCapLoop_M6` | `statement` | `RVR` | 3 | 29 | `10, 11, 12` | `10, 11, 29` |
| 28 | `fault_localization_core_b` | `SaturatingPenaltyLoop` | `SaturatingPenaltyLoop_M6` | `statement` | `RVR` | 2 | 24 | `12, 18` | `10, 24` |
| 29 | `fault_localization_core_b` | `TwoBucketLoop` | `TwoBucketLoop_M3` | `condition` | `BOR` | 3 | 13 | `12, 14, 18` | `13, 14, 27` |
| 30 | `fault_localization_core_b` | `TwoBucketLoop` | `TwoBucketLoop_M5` | `statement` | `AOR` | 2 | 22 | `12, 18` | `22, 27` |
| 31 | `fault_localization_core_b` | `TwoBucketLoop` | `TwoBucketLoop_M6` | `statement` | `RVR` | 3 | 27 | `10, 11, 12` | `10, 11, 27` |

## Reading Notes

- These are not all failures of the CSC-based strategy; they are specifically the budget-matched cases where SFL wins at Top-1.
- Cases with small `N` are especially useful because the comparison is strict: SFL had only a small number of lines and still hit.
- Cases where CSC Top-1 lines are concentrated around a different late-stage region may indicate that PER is over-weighting downstream failure density.
- Cases where SFL hits the exact mutated statement but CSC selects nearby condition/context lines may suggest that the edge-region score needs better statement-level discrimination.
