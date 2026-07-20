# Boundary Stress TBFV Kill Experiment

- Dataset: `EX_CSC_BOUNDARY_STRESS`
- Kill definition: a mutant is killed iff its `refined_tbfv_report.json` has `summary.failed > 0`.
- CSC-only: `--mode original --max-iter 1200 --strategy batch --workers 4`.
- CSC+Boundary: `--mode expanded --range-bound 200 --max-iter 1200 --strategy batch --workers 4`.
- FSF note: summary regenerated after tightening normal scenarios to avoid overlap with `input > 200` stress scenarios.
- Status: exploratory sandbox; not merged into paper tables.

## Overall

| Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Both killed | Neither killed |
|---:|---:|---:|---:|---:|---:|
| 24 | 23 (95.8%) | 23 (95.8%) | 0 (0.0%) | 23 | 1 |

## Original Sanity

| Subject | Mode | Status | Testcases | Failed Results |
|---|---|---|---:|---:|
| BoundaryStressCounter | csc_only | ok | 15 | 0 |
| BoundaryStressCounter | boundary | ok | 81 | 0 |
| BoundaryStressLedger | csc_only | ok | 15 | 0 |
| BoundaryStressLedger | boundary | ok | 81 | 0 |
| BoundaryStressMeter | csc_only | ok | 15 | 0 |
| BoundaryStressMeter | boundary | ok | 81 | 0 |
| BoundaryStressQuota | csc_only | ok | 15 | 0 |
| BoundaryStressQuota | boundary | ok | 81 | 0 |

## By Subject

| Group | Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Neither killed |
|---|---:|---:|---:|---:|---:|
| BoundaryStressCounter | 6 | 5 (83.3%) | 5 (83.3%) | 0 | 1 |
| BoundaryStressLedger | 6 | 6 (100.0%) | 6 (100.0%) | 0 | 0 |
| BoundaryStressMeter | 6 | 6 (100.0%) | 6 (100.0%) | 0 | 0 |
| BoundaryStressQuota | 6 | 6 (100.0%) | 6 (100.0%) | 0 | 0 |

## By Operator

| Group | Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Neither killed |
|---|---:|---:|---:|---:|---:|
| AOR | 4 | 4 (100.0%) | 4 (100.0%) | 0 | 0 |
| BOR | 8 | 8 (100.0%) | 8 (100.0%) | 0 | 0 |
| ROR | 4 | 4 (100.0%) | 4 (100.0%) | 0 | 0 |
| RVR | 4 | 3 (75.0%) | 3 (75.0%) | 0 | 1 |
| SUR | 4 | 4 (100.0%) | 4 (100.0%) | 0 | 0 |

## By Category

| Group | Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Neither killed |
|---|---:|---:|---:|---:|---:|
| condition | 12 | 12 (100.0%) | 12 (100.0%) | 0 | 0 |
| statement | 12 | 11 (91.7%) | 11 (91.7%) | 0 | 1 |

## Boundary-only Killed Mutants

None.

## Non-killed By Boundary

| Subject | Mutant | Operator | Category | CSC-only killed | Boundary killed |
|---|---|---|---|---:|---:|
| BoundaryStressCounter | BoundaryStressCounter_M6 | RVR | statement | N | N |
