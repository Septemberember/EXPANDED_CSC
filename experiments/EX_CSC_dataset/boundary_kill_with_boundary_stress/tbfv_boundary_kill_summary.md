# TBFV Boundary Kill Experiment with Boundary-Stress Subjects

- Experiment ID: `boundary_kill_with_boundary_stress`.
- Composition: 194 tasks retained from `boundary_kill_core` and four validated Boundary-sensitive stress mutants.
- The pool size remains fixed at 198 tasks by excluding four low-discrimination statement mutants that were killed by the first CSC-only test.
- All rows are derived from completed TBFV artifacts; no source experiment files are overwritten.

## Overall Comparison

| Pool | Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Both killed | Neither killed |
|---|---:|---:|---:|---:|---:|---:|
| Reference pool | 198 | 153 (77.3%) | 184 (92.9%) | 31 (15.7%) | 153 | 14 |
| Current experiment collection | 198 | 149 (75.3%) | 184 (92.9%) | 35 (17.7%) | 149 | 14 |
| Delta | +0 | -4 | +0 | +4 | -4 | +0 |

## Selection Log

Excluded low-discrimination mutants:
| Dataset | Subject | Mutant | Operator | Category | CSC-only first failure | CSC failed | Boundary failed |
|---|---|---|---|---|---:|---:|---:|
| EX_CSC_dataset | TaxBracket | TaxBracket_M5 | AOR | statement | 1 | 2 | 161 |
| EX_CSC_dataset | InventoryReorder | InventoryReorder_M6 | RVR | statement | 1 | 7 | 87 |
| EX_CSC_dataset | TwoBucketLoop | TwoBucketLoop_M6 | RVR | statement | 1 | 6 | 84 |
| EX_CSC_dataset | RewardCapLoop | RewardCapLoop_M6 | RVR | statement | 1 | 8 | 68 |

Included Boundary-sensitive mutants:
| Dataset | Subject | Mutant | CSC-only killed | Boundary killed | Boundary failed | Boundary first failure |
|---|---|---|---:|---:|---:|---|
| EX_CSC_BOUNDARY_STRESS | BoundaryStressCounter | BoundaryStressCounter_M7 | N | Y | 12 | tc_5_b51 / fsf_2 |
| EX_CSC_BOUNDARY_STRESS | BoundaryStressMeter | BoundaryStressMeter_M7 | N | Y | 12 | tc_5_b36 / fsf_2 |
| EX_CSC_BOUNDARY_STRESS | BoundaryStressLedger | BoundaryStressLedger_M7 | N | Y | 9 | tc_6_b23 / fsf_2 |
| EX_CSC_BOUNDARY_STRESS | BoundaryStressQuota | BoundaryStressQuota_M7 | N | Y | 10 | tc_5_b15 / fsf_2 |

## By Dataset

| Dataset | Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Neither killed |
|---|---:|---:|---:|---:|---:|
| EX_CSC | 36 | 28 (77.8%) | 34 (94.4%) | 6 (16.7%) | 2 |
| EX_CSC_dataset | 28 | 23 (82.1%) | 25 (89.3%) | 2 (7.1%) | 3 |
| EX_CSC_dataset | 34 | 29 (85.3%) | 32 (94.1%) | 3 (8.8%) | 2 |
| EX_CSC_dataset | 48 | 33 (68.8%) | 43 (89.6%) | 10 (20.8%) | 5 |
| EX_CSC_dataset | 48 | 36 (75.0%) | 46 (95.8%) | 10 (20.8%) | 2 |
| EX_CSC_BOUNDARY_STRESS | 4 | 0 (0.0%) | 4 (100.0%) | 4 (100.0%) | 0 |

## By Category

| Category | Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Neither killed |
|---|---:|---:|---:|---:|---:|
| condition | 100 | 79 (79.0%) | 90 (90.0%) | 11 (11.0%) | 10 |
| statement | 98 | 70 (71.4%) | 94 (95.9%) | 24 (24.5%) | 4 |
