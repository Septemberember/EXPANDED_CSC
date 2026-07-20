# Boundary Stress RQ1 Full Review

Status: exploratory sandbox; not merged into existing experiments or paper tables.

- Repeats: 3
- Range bound: 200
- Normal completions: 24/24
- Fully paired subjects: 4/4

| Subject | LOC | CSC Tests | Boundary Tests | CSC Ancestor-Stopped (empty) | Boundary Ancestor-Stopped (empty) | Boundary Expanded Leaves | Boundary Range-Excluded | Boundary Nodes | Boundary Time (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BoundaryStressCounter | 35 | 15.0 | 74.0 | 22.0 | 0.0 | 66.0 | 10.0 | 751.0 | 51.86 |
| BoundaryStressLedger | 42 | 15.0 | 74.0 | 22.0 | 0.0 | 66.0 | 10.0 | 913.0 | 64.62 |
| BoundaryStressMeter | 42 | 15.0 | 74.0 | 22.0 | 0.0 | 66.0 | 10.0 | 913.0 | 64.45 |
| BoundaryStressQuota | 42 | 15.0 | 74.0 | 22.0 | 0.0 | 66.0 | 10.0 | 913.0 | 67.57 |

## Notes

- `Ancestor-Stopped (empty)` uses `empty_leaves`, matching existing RQ1 terminology for original CSC ancestor-stopped leaves.
- `Range-Excluded` uses `out_of_range_leaves` / `RANGE_EXCLUDED` leaves.
- This report is isolated and has not been merged into paper tables.
