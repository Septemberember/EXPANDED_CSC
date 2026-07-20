# Boundary-sensitive Mutant Screening

- Goal: retain mutants killed by Boundary but not by CSC-only.
- CSC-only: `--mode original --max-iter 1200 --strategy batch --workers 4`.
- Boundary: `--mode expanded --range-bound 200 --max-iter 1200 --strategy batch --workers 4`.

## Overall

| Mutants | CSC-only killed | Boundary killed | Boundary-only killed | Both killed | Neither killed | Original failed results |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 0 | 4 | 4 | 0 | 0 | 0 |

## Per Mutant

| Subject | Mutant | CSC-only killed | Boundary killed | Boundary-only | CSC failed | Boundary failed | Boundary first failure |
|---|---|---:|---:|---:|---:|---:|---|
| BoundaryStressCounter | BoundaryStressCounter_M7 | N | Y | Y | 0 | 12 | tc_5_b51 / fsf_2 |
| BoundaryStressMeter | BoundaryStressMeter_M7 | N | Y | Y | 0 | 12 | tc_5_b36 / fsf_2 |
| BoundaryStressLedger | BoundaryStressLedger_M7 | N | Y | Y | 0 | 9 | tc_6_b23 / fsf_2 |
| BoundaryStressQuota | BoundaryStressQuota_M7 | N | Y | Y | 0 | 10 | tc_5_b15 / fsf_2 |

## Original Sanity

| Subject | Mode | Failed Results | Testcases |
|---|---|---:|---:|
| BoundaryStressCounter | csc_only | 0 | 15 |
| BoundaryStressCounter | boundary | 0 | 81 |
| BoundaryStressLedger | csc_only | 0 | 15 |
| BoundaryStressLedger | boundary | 0 | 81 |
| BoundaryStressMeter | csc_only | 0 | 15 |
| BoundaryStressMeter | boundary | 0 | 81 |
| BoundaryStressQuota | csc_only | 0 | 15 |
| BoundaryStressQuota | boundary | 0 | 81 |