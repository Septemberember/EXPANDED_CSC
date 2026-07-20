# RQ2 Parallel Generation Summary

- Runs: 32
- Subjects: 8
- Workers: 1, 2, 4, 8

## Overall Parallel Summary

| Workers | Completed | Fresh | Mean Time(s) | Median Time(s) | Mean Testcases | Mean New Testcases | Mean CCT Nodes | Mean Batch Verify(s) | Mean Time/Testcase(s) | Mean Speedup | Median Speedup | Mean Efficiency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 8/8 | 8/8 | 48.648 | 55.209 | 70.125 | 70.125 | 1507.500 | 22.217 | 0.775 | 1.000 | 1.000 | 1.000 |
| 2 | 8/8 | 8/8 | 41.262 | 48.045 | 70.125 | 70.125 | 1507.500 | 14.889 | 0.665 | 1.258 | 1.161 | 0.629 |
| 4 | 8/8 | 8/8 | 38.156 | 42.890 | 70.125 | 70.125 | 1507.500 | 11.450 | 0.619 | 1.395 | 1.323 | 0.349 |
| 8 | 8/8 | 8/8 | 37.061 | 40.447 | 70.125 | 70.125 | 1507.500 | 10.113 | 0.606 | 1.482 | 1.319 | 0.185 |

## Speedup Quantile Cases

| Role | Subject | T1 | T2 | T4 | T8 | S2 | S4 | S8 | Testcases | CCT Nodes | Mean Frontier | Max Frontier | Max Depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | BoundedProperDivisorParity | 69.635 | 65.037 | 62.884 | 62.614 | 1.071 | 1.107 | 1.112 | 52 | 2923 | 6.375 | 14 | 102 |
| q1 | BoundedDivisorCountClassifier | 71.775 | 61.700 | 59.694 | 59.268 | 1.163 | 1.202 | 1.211 | 52 | 3127 | 7.286 | 14 | 105 |
| median | BoundedSquareFreeClassifier | 17.634 | 15.205 | 12.611 | 12.760 | 1.160 | 1.398 | 1.382 | 40 | 265 | 6.500 | 16 | 22 |
| q3 | BoundedPopcountDensity | 44.277 | 35.381 | 29.739 | 25.515 | 1.251 | 1.489 | 1.735 | 130 | 1095 | 9.214 | 23 | 19 |
| max | BoundedBitTransitionClassifier | 26.918 | 16.840 | 14.744 | 13.364 | 1.598 | 1.826 | 2.014 | 66 | 627 | 9.286 | 20 | 17 |

## Frontier Width Quantile Cases

| Role | Subject | T1 | T2 | T4 | T8 | S2 | S4 | S8 | Testcases | CCT Nodes | Mean Frontier | Max Frontier | Max Depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | BoundedAliquotClassifier | 66.141 | 60.709 | 56.042 | 55.378 | 1.089 | 1.180 | 1.194 | 52 | 3019 | 6.375 | 17 | 103 |
| q1 | BoundedSquareFreeClassifier | 17.634 | 15.205 | 12.611 | 12.760 | 1.160 | 1.398 | 1.382 | 40 | 265 | 6.500 | 16 | 22 |
| median | BoundedPerfectSquareLoop | 70.508 | 61.054 | 56.519 | 56.168 | 1.155 | 1.248 | 1.255 | 103 | 407 | 8.500 | 29 | 203 |
| q3 | BoundedPopcountDensity | 44.277 | 35.381 | 29.739 | 25.515 | 1.251 | 1.489 | 1.735 | 130 | 1095 | 9.214 | 23 | 19 |
| max | BoundedBitTransitionClassifier | 26.918 | 16.840 | 14.744 | 13.364 | 1.598 | 1.826 | 2.014 | 66 | 627 | 9.286 | 20 | 17 |
