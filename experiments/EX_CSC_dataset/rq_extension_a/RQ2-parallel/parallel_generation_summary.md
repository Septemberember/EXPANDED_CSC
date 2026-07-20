# RQ2 Parallel Generation Summary

- Runs: 32
- Subjects: 8
- Workers: 1, 2, 4, 8

## Overall Parallel Summary

| Workers | Completed | Fresh | Mean Time(s) | Median Time(s) | Mean Testcases | Mean New Testcases | Mean CCT Nodes | Mean Batch Verify(s) | Mean Time/Testcase(s) | Mean Speedup | Median Speedup | Mean Efficiency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 8/8 | 8/8 | 35.086 | 27.447 | 68.750 | 68.750 | 1163.250 | 19.355 | 0.585 | 1.000 | 1.000 | 1.000 |
| 2 | 8/8 | 8/8 | 28.222 | 19.423 | 68.750 | 68.750 | 1163.250 | 12.430 | 0.481 | 1.347 | 1.360 | 0.674 |
| 4 | 8/8 | 8/8 | 26.297 | 17.766 | 68.750 | 68.750 | 1163.250 | 10.361 | 0.453 | 1.473 | 1.464 | 0.368 |
| 8 | 8/8 | 8/8 | 26.178 | 18.754 | 68.750 | 68.750 | 1163.250 | 9.890 | 0.453 | 1.491 | 1.390 | 0.186 |

## Speedup Quantile Cases

| Role | Subject | T1 | T2 | T4 | T8 | S2 | S4 | S8 | Testcases | CCT Nodes | Mean Frontier | Max Frontier | Max Depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | BoundedPronicNumber | 21.153 | 17.812 | 18.050 | 19.548 | 1.188 | 1.172 | 1.082 | 53 | 225 | 7.429 | 33 | 106 |
| q1 | BoundedPerfectNumber | 62.807 | 56.030 | 53.517 | 52.917 | 1.121 | 1.174 | 1.187 | 52 | 2923 | 7.286 | 20 | 102 |
| median | BoundedAbundantNumber | 24.157 | 18.806 | 17.278 | 17.207 | 1.284 | 1.398 | 1.404 | 50 | 1161 | 4.455 | 15 | 52 |
| q3 | BoundedEvilNumber | 30.738 | 20.040 | 17.482 | 17.959 | 1.534 | 1.758 | 1.712 | 103 | 735 | 8.500 | 20 | 19 |
| max | BoundedIntPower | 9.737 | 5.804 | 4.906 | 4.286 | 1.678 | 1.985 | 2.272 | 30 | 71 | 7.250 | 14 | 17 |

## Frontier Width Quantile Cases

| Role | Subject | T1 | T2 | T4 | T8 | S2 | S4 | S8 | Testcases | CCT Nodes | Mean Frontier | Max Frontier | Max Depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | BoundedAbundantNumber | 24.157 | 18.806 | 17.278 | 17.207 | 1.284 | 1.398 | 1.404 | 50 | 1161 | 4.455 | 15 | 52 |
| q1 | BoundedPrimeClassifier | 64.055 | 60.127 | 57.122 | 56.370 | 1.065 | 1.121 | 1.136 | 51 | 3057 | 6.250 | 14 | 104 |
| median | BoundedPerfectNumber | 62.807 | 56.030 | 53.517 | 52.917 | 1.121 | 1.174 | 1.187 | 52 | 2923 | 7.286 | 20 | 102 |
| q3 | BoundedPronicNumber | 21.153 | 17.812 | 18.050 | 19.548 | 1.188 | 1.172 | 1.082 | 53 | 225 | 7.429 | 33 | 106 |
| max | BoundedKrishnamurthyNumber | 52.445 | 36.558 | 31.830 | 29.804 | 1.435 | 1.648 | 1.760 | 173 | 1027 | 17.200 | 71 | 26 |
