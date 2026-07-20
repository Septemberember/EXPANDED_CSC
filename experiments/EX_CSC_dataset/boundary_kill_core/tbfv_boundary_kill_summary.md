# TBFV Boundary Kill Experiment: EX_CSC_dataset Loop Subjects

- Kill definition: a mutant is killed iff its `refined_tbfv_report.json` has `summary.failed > 0`.
- CSC-only uses `--mode original --max-iter 100 --strategy batch --workers 4`.
- CSC+Boundary reports are reused from existing Boundary fault-localization experiments.
- Rows are aggregation-ready under `aggregate_ready/tbfv_boundary_kill_rows.jsonl`.

## Overall

| Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Both killed | Neither killed |
|---:|---:|---:|---:|---:|---:|
| 198 | 153 (77.3%) | 184 (92.9%) | 31 (15.7%) | 153 | 14 |

## By Dataset

| Dataset | Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Neither killed |
|---|---:|---:|---:|---:|---:|
| EX_CSC_dataset | 36 | 28 (77.8%) | 34 (94.4%) | 6 | 2 |
| EX_CSC_dataset | 30 | 25 (83.3%) | 27 (90.0%) | 2 | 3 |
| EX_CSC_dataset | 36 | 31 (86.1%) | 34 (94.4%) | 3 | 2 |
| EX_CSC_dataset | 48 | 33 (68.8%) | 43 (89.6%) | 10 | 5 |
| EX_CSC_dataset | 48 | 36 (75.0%) | 46 (95.8%) | 10 | 2 |

## By Subject

| Dataset | Subject | Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Neither killed |
|---|---|---:|---:|---:|---:|---:|
| EX_CSC_dataset | AddLoop | 6 | 5 | 5 | 0 | 1 |
| EX_CSC_dataset | BoundedAbundantNumber | 6 | 2 | 5 | 3 | 1 |
| EX_CSC_dataset | BoundedAliquotClassifier | 6 | 3 | 5 | 2 | 1 |
| EX_CSC_dataset | BoundedBinaryPalindromeClassifier | 6 | 6 | 6 | 0 | 0 |
| EX_CSC_dataset | BoundedBitTransitionClassifier | 6 | 3 | 6 | 3 | 0 |
| EX_CSC_dataset | BoundedDivisorCountClassifier | 6 | 5 | 6 | 1 | 0 |
| EX_CSC_dataset | BoundedEvilNumber | 6 | 6 | 6 | 0 | 0 |
| EX_CSC_dataset | BoundedIntPower | 6 | 5 | 5 | 0 | 1 |
| EX_CSC_dataset | BoundedKrishnamurthyNumber | 6 | 6 | 6 | 0 | 0 |
| EX_CSC_dataset | BoundedPerfectNumber | 6 | 3 | 6 | 3 | 0 |
| EX_CSC_dataset | BoundedPerfectSquareLoop | 6 | 5 | 6 | 1 | 0 |
| EX_CSC_dataset | BoundedPopcountDensity | 6 | 3 | 6 | 3 | 0 |
| EX_CSC_dataset | BoundedPrimeClassifier | 6 | 5 | 6 | 1 | 0 |
| EX_CSC_dataset | BoundedPronicNumber | 6 | 3 | 4 | 1 | 2 |
| EX_CSC_dataset | BoundedProperDivisorParity | 6 | 5 | 5 | 0 | 1 |
| EX_CSC_dataset | BoundedSquareFreeClassifier | 6 | 6 | 6 | 0 | 0 |
| EX_CSC_dataset | GradePolicy | 6 | 5 | 6 | 1 | 0 |
| EX_CSC_dataset | InventoryReorder | 6 | 6 | 6 | 0 | 0 |
| EX_CSC_dataset | LoopBubbleSortFive | 6 | 5 | 6 | 1 | 0 |
| EX_CSC_dataset | LoopSelectionSortFive | 6 | 6 | 6 | 0 | 0 |
| EX_CSC_dataset | MarginAdjustLoop | 6 | 6 | 6 | 0 | 0 |
| EX_CSC_dataset | OddEvenSortFive | 6 | 5 | 5 | 0 | 1 |
| EX_CSC_dataset | RewardCapLoop | 6 | 5 | 6 | 1 | 0 |
| EX_CSC_dataset | SaturatedIntPower | 6 | 3 | 5 | 2 | 1 |
| EX_CSC_dataset | SaturatingPenaltyLoop | 6 | 4 | 5 | 1 | 1 |
| EX_CSC_dataset | ScoreNormalizer | 6 | 2 | 6 | 4 | 0 |
| EX_CSC_dataset | SubtractLoop | 6 | 5 | 5 | 0 | 1 |
| EX_CSC_dataset | TailRotateSortFive | 6 | 5 | 6 | 1 | 0 |
| EX_CSC_dataset | TaxBracket | 6 | 4 | 5 | 1 | 1 |
| EX_CSC_dataset | TicketPrice | 6 | 5 | 5 | 0 | 1 |
| EX_CSC_dataset | TwoBucketLoop | 6 | 6 | 6 | 0 | 0 |
| EX_CSC_dataset | WaterBillCaculator | 6 | 5 | 6 | 1 | 0 |
| EX_CSC_dataset | WeightedAddLoop | 6 | 5 | 5 | 0 | 1 |

## Boundary-only Killed Mutants

| Dataset | Subject | Mutant | Operator | Category | CSC-only tests | Boundary tests | Boundary first failure |
|---|---|---|---|---|---:|---:|---|
| EX_CSC_dataset | LoopBubbleSortFive | LoopBubbleSortFive_M4 | SUR | statement | 17 | 55 | tc_4_b0 / fsf_1 |
| EX_CSC_dataset | ScoreNormalizer | ScoreNormalizer_M3 | ROR | condition | 10 | 165 | tc_3_b2 / fsf_6 |
| EX_CSC_dataset | ScoreNormalizer | ScoreNormalizer_M4 | AOR | statement | 10 | 168 | tc_3_b2 / fsf_2 |
| EX_CSC_dataset | ScoreNormalizer | ScoreNormalizer_M5 | AOR | statement | 10 | 157 | tc_4_b0 / fsf_6 |
| EX_CSC_dataset | ScoreNormalizer | ScoreNormalizer_M6 | SUR | statement | 10 | 98 | tc_3_b2 / fsf_2 |
| EX_CSC_dataset | WaterBillCaculator | WaterBillCaculator_M1 | BOR | condition | 6 | 32 | tc_3_b0 / fsf_5 |
| EX_CSC_dataset | GradePolicy | GradePolicy_M3 | BOR | condition | 10 | 148 | tc_3_b15 / fsf_2 |
| EX_CSC_dataset | TaxBracket | TaxBracket_M6 | RVR | statement | 10 | 326 | tc_3_b9 / fsf_4 |
| EX_CSC_dataset | RewardCapLoop | RewardCapLoop_M3 | BOR | condition | 10 | 86 | tc_3_b2 / fsf_6 |
| EX_CSC_dataset | SaturatingPenaltyLoop | SaturatingPenaltyLoop_M5 | AOR | statement | 7 | 77 | tc_3_b15 / fsf_2 |
| EX_CSC_dataset | TailRotateSortFive | TailRotateSortFive_M4 | SUR | statement | 18 | 87 | tc_3_b4 / fsf_1 |
| EX_CSC_dataset | BoundedAbundantNumber | BoundedAbundantNumber_M2 | BOR | condition | 6 | 48 | tc_4_b8 / fsf_2 |
| EX_CSC_dataset | BoundedAbundantNumber | BoundedAbundantNumber_M5 | AOR | statement | 6 | 50 | tc_4_b8 / fsf_2 |
| EX_CSC_dataset | BoundedAbundantNumber | BoundedAbundantNumber_M6 | SUR | statement | 7 | 38 | tc_5_b14 / fsf_2 |
| EX_CSC_dataset | BoundedPerfectNumber | BoundedPerfectNumber_M3 | ROR | condition | 6 | 52 | tc_4_b9 / fsf_3 |
| EX_CSC_dataset | BoundedPerfectNumber | BoundedPerfectNumber_M5 | AOR | statement | 6 | 52 | tc_4_b8 / fsf_2 |
| EX_CSC_dataset | BoundedPerfectNumber | BoundedPerfectNumber_M6 | SUR | statement | 5 | 49 | tc_5_b3 / fsf_2 |
| EX_CSC_dataset | BoundedPrimeClassifier | BoundedPrimeClassifier_M5 | AOR | statement | 4 | 51 | tc_4_b1 / fsf_2 |
| EX_CSC_dataset | BoundedPronicNumber | BoundedPronicNumber_M6 | RVR | statement | 4 | 53 | tc_3_b0 / fsf_3 |
| EX_CSC_dataset | SaturatedIntPower | SaturatedIntPower_M2 | ROR | condition | 10 | 38 | tc_4_b0 / fsf_14 |
| EX_CSC_dataset | SaturatedIntPower | SaturatedIntPower_M4 | CR | statement | 10 | 38 | tc_5_b2 / fsf_14 |
| EX_CSC_dataset | BoundedAliquotClassifier | BoundedAliquotClassifier_M4 | AOR | statement | 6 | 52 | tc_4_b8 / fsf_2 |
| EX_CSC_dataset | BoundedAliquotClassifier | BoundedAliquotClassifier_M5 | AOR | statement | 5 | 49 | tc_4_b19 / fsf_3 |
| EX_CSC_dataset | BoundedBitTransitionClassifier | BoundedBitTransitionClassifier_M2 | BOR | condition | 5 | 130 | tc_2_b1 / fsf_2 |
| EX_CSC_dataset | BoundedBitTransitionClassifier | BoundedBitTransitionClassifier_M3 | BOR | condition | 5 | 66 | tc_3_b2 / fsf_3 |
| EX_CSC_dataset | BoundedBitTransitionClassifier | BoundedBitTransitionClassifier_M6 | CR | statement | 5 | 66 | tc_4_b3 / fsf_4 |
| EX_CSC_dataset | BoundedDivisorCountClassifier | BoundedDivisorCountClassifier_M2 | BOR | condition | 6 | 52 | tc_4_b3 / fsf_3 |
| EX_CSC_dataset | BoundedPerfectSquareLoop | BoundedPerfectSquareLoop_M6 | CR | statement | 4 | 103 | tc_3_b0 / fsf_3 |
| EX_CSC_dataset | BoundedPopcountDensity | BoundedPopcountDensity_M3 | BOR | condition | 6 | 130 | tc_7_b1 / fsf_3 |
| EX_CSC_dataset | BoundedPopcountDensity | BoundedPopcountDensity_M4 | AOR | statement | 6 | 130 | tc_4_b0 / fsf_2 |
| EX_CSC_dataset | BoundedPopcountDensity | BoundedPopcountDensity_M6 | CR | statement | 6 | 130 | tc_9_b1 / fsf_4 |

## Non-killed By Boundary

| Dataset | Subject | Mutant | Operator | Category | CSC-only killed | Boundary killed |
|---|---|---|---|---|---:|---:|
| EX_CSC_dataset | AddLoop | AddLoop_M3 | ROR | condition | N | N |
| EX_CSC_dataset | OddEvenSortFive | OddEvenSortFive_M6 | SUR | statement | N | N |
| EX_CSC_dataset | SubtractLoop | SubtractLoop_M3 | ROR | condition | N | N |
| EX_CSC_dataset | TaxBracket | TaxBracket_M3 | ROR | condition | N | N |
| EX_CSC_dataset | TicketPrice | TicketPrice_M3 | ROR | condition | N | N |
| EX_CSC_dataset | SaturatingPenaltyLoop | SaturatingPenaltyLoop_M3 | BOR | condition | N | N |
| EX_CSC_dataset | WeightedAddLoop | WeightedAddLoop_M3 | ROR | condition | N | N |
| EX_CSC_dataset | BoundedAbundantNumber | BoundedAbundantNumber_M4 | CR | statement | N | N |
| EX_CSC_dataset | BoundedIntPower | BoundedIntPower_M3 | ROR | condition | N | N |
| EX_CSC_dataset | BoundedPronicNumber | BoundedPronicNumber_M2 | BOR | condition | N | N |
| EX_CSC_dataset | BoundedPronicNumber | BoundedPronicNumber_M4 | CR | statement | N | N |
| EX_CSC_dataset | SaturatedIntPower | SaturatedIntPower_M3 | BOR | condition | N | N |
| EX_CSC_dataset | BoundedAliquotClassifier | BoundedAliquotClassifier_M3 | BOR | condition | N | N |
| EX_CSC_dataset | BoundedProperDivisorParity | BoundedProperDivisorParity_M5 | AOR | statement | N | N |
