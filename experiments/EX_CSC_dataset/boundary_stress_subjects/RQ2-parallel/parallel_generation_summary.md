# RQ2 Parallel Generation Summary

- Runs: 24
- Subjects: 2
- Workers: 1, 2, 4, 8

## Overall Parallel Summary

| Workers | Normal/Total | Budget Stop | Fresh | Mean Time(s) | Median Time(s) | Mean Testcases | Mean New Testcases | Mean CCT Nodes | Mean Batch Verify(s) | Mean Time/Testcase(s) | Mean Speedup | Median Speedup | Mean Efficiency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 6/6 | 0 | 6/6 | 70.111 | 70.111 | 81.000 | 81.000 | 832.000 | 34.443 | 0.866 | 1.000 | 1.000 | 1.000 |
| 2 | 6/6 | 0 | 6/6 | 56.787 | 56.787 | 81.000 | 81.000 | 832.000 | 23.630 | 0.701 | 1.236 | 1.236 | 0.618 |
| 4 | 6/6 | 0 | 6/6 | 52.800 | 52.800 | 81.000 | 81.000 | 832.000 | 19.865 | 0.652 | 1.329 | 1.329 | 0.332 |
| 8 | 6/6 | 0 | 6/6 | 54.165 | 54.165 | 81.000 | 81.000 | 832.000 | 20.605 | 0.669 | 1.293 | 1.293 | 0.162 |

## Canonical Output Invariance

Complete fingerprints: 2/2; invariant fingerprints: 2/2.

| Subject | Fresh/Expected | Structure | Leaf Semantics | Input Set | All Invariant |
| --- | --- | --- | --- | --- | --- |
| BoundaryStressCounter | 12/12 | True | True | True | True |
| BoundaryStressMeter | 12/12 | True | True | True | True |

## Speedup Quantile Cases

| Role | Subject | T1 | T2 | T4 | T8 | S2 | S4 | S8 | Testcases | CCT Nodes | Mean Frontier | Max Frontier | Max Depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | BoundaryStressCounter | 58.182 | 46.851 | 43.668 | 45.409 | 1.242 | 1.332 | 1.281 | 81.000 | 751.000 | 10.000 | 53.000 | 276.000 |
| q1 | BoundaryStressCounter | 58.182 | 46.851 | 43.668 | 45.409 | 1.242 | 1.332 | 1.281 | 81.000 | 751.000 | 10.000 | 53.000 | 276.000 |
| median | BoundaryStressCounter | 58.182 | 46.851 | 43.668 | 45.409 | 1.242 | 1.332 | 1.281 | 81.000 | 751.000 | 10.000 | 53.000 | 276.000 |
| q3 | BoundaryStressMeter | 82.040 | 66.723 | 61.932 | 62.920 | 1.230 | 1.325 | 1.304 | 81.000 | 913.000 | 11.429 | 38.000 | 343.000 |
| max | BoundaryStressMeter | 82.040 | 66.723 | 61.932 | 62.920 | 1.230 | 1.325 | 1.304 | 81.000 | 913.000 | 11.429 | 38.000 | 343.000 |

## Frontier Width Quantile Cases

| Role | Subject | T1 | T2 | T4 | T8 | S2 | S4 | S8 | Testcases | CCT Nodes | Mean Frontier | Max Frontier | Max Depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | BoundaryStressCounter | 58.182 | 46.851 | 43.668 | 45.409 | 1.242 | 1.332 | 1.281 | 81.000 | 751.000 | 10.000 | 53.000 | 276.000 |
| q1 | BoundaryStressCounter | 58.182 | 46.851 | 43.668 | 45.409 | 1.242 | 1.332 | 1.281 | 81.000 | 751.000 | 10.000 | 53.000 | 276.000 |
| median | BoundaryStressCounter | 58.182 | 46.851 | 43.668 | 45.409 | 1.242 | 1.332 | 1.281 | 81.000 | 751.000 | 10.000 | 53.000 | 276.000 |
| q3 | BoundaryStressMeter | 82.040 | 66.723 | 61.932 | 62.920 | 1.230 | 1.325 | 1.304 | 81.000 | 913.000 | 11.429 | 38.000 | 343.000 |
| max | BoundaryStressMeter | 82.040 | 66.723 | 61.932 | 62.920 | 1.230 | 1.325 | 1.304 | 81.000 | 913.000 | 11.429 | 38.000 | 343.000 |
