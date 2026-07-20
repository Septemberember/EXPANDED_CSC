# RQ2 Parallel Generation Summary

- Runs: 288
- Subjects: 24
- Workers: 1, 2, 4, 8

## Overall Parallel Summary

| Workers | Completed | Fresh | Mean Time(s) | Median Time(s) | Mean Testcases | Mean New Testcases | Mean CCT Nodes | Mean Batch Verify(s) | Mean Time/Testcase(s) | Mean Speedup | Median Speedup | Mean Efficiency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 72/72 | 72/72 | 68.675 | 55.307 | 165.792 | 165.792 | 926.167 | 60.646 | 0.430 | 0.837 | 0.914 | 0.837 |
| 2 | 72/72 | 72/72 | 48.051 | 38.971 | 165.792 | 165.792 | 926.167 | 40.245 | 0.298 | 1.176 | 1.213 | 0.588 |
| 4 | 72/72 | 72/72 | 36.652 | 29.584 | 165.792 | 165.792 | 926.167 | 28.418 | 0.231 | 1.544 | 1.607 | 0.386 |
| 8 | 72/72 | 72/72 | 33.517 | 27.596 | 165.792 | 165.792 | 926.167 | 25.378 | 0.212 | 1.663 | 1.644 | 0.208 |

## Speedup Quantile Cases

| Role | Subject | T1 | T2 | T4 | T8 | S2 | S4 | S8 | Testcases | CCT Nodes | Mean Frontier | Max Frontier | Max Depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | EX_CSC__WaterBillCaculator | 20.137 | 17.008 | 15.764 | 15.422 | 1.184 | 1.277 | 1.306 | 31 | 1137 | 7.500 | 19 | 87 |
| q1 | EX_CSC_dataset__SubtractLoop | 71.395 | 49.968 | 41.382 | 39.942 | 1.429 | 1.725 | 1.787 | 205 | 415 | 34 | 128 | 106 |
| median | EX_CSC_dataset__TicketPrice | 61.013 | 40.658 | 32.918 | 30.736 | 1.501 | 1.854 | 1.985 | 206 | 423 | 25.625 | 104 | 57 |
| q3 | EX_CSC_dataset__MaxOfFive | 61.515 | 41.496 | 29.985 | 28.284 | 1.482 | 2.052 | 2.175 | 219 | 685 | 27.250 | 60 | 9 |
| max | EX_CSC_dataset__GradePolicy | 41.311 | 24.943 | 18.297 | 17.070 | 1.656 | 2.258 | 2.420 | 148 | 539 | 24.500 | 57 | 48 |

## Frontier Width Quantile Cases

| Role | Subject | T1 | T2 | T4 | T8 | S2 | S4 | S8 | Testcases | CCT Nodes | Mean Frontier | Max Frontier | Max Depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | EX_CSC__WaterBillCaculator | 20.137 | 17.008 | 15.764 | 15.422 | 1.184 | 1.277 | 1.306 | 31 | 1137 | 7.500 | 19 | 87 |
| q1 | EX_CSC_dataset__TailRotateSortFive | 36.814 | 27.084 | 21.822 | 25.394 | 1.359 | 1.687 | 1.450 | 120 | 1641 | 14.875 | 39 | 16 |
| median | EX_CSC__ScoreNormalizer | 47.276 | 28.618 | 21.740 | 20.326 | 1.652 | 2.175 | 2.326 | 167 | 705 | 23.714 | 62 | 49 |
| q3 | EX_CSC__LoopSelectionSortFive | 87.388 | 58.365 | 42.805 | 38.378 | 1.497 | 2.042 | 2.277 | 226 | 3527 | 32.143 | 72 | 24 |
| max | EX_CSC_dataset__TaxBracket | 101.207 | 66.241 | 54.802 | 53.615 | 1.528 | 1.847 | 1.888 | 326 | 655 | 46.429 | 142 | 87 |
