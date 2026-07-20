# Budget-Matched Comparison: Folded Composite vs SFL

- SFL formula: `ochiai`
- Top-R: 1, 2, 3
- Method: folded composite inspection budget = union of condition[:R] and edge_partition[:R] lines.  SFL receives the same number of unique source lines.

## overall (N=43)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.2 | 19/43 (0.442) | 18/43 (0.419) |
| 2 | 4.1 | 31/43 (0.721) | 29/43 (0.674) |
| 3 | 6.0 | 39/43 (0.907) | 37/43 (0.860) |

## condition (N=22)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.2 | 12/22 (0.545) | 11/22 (0.500) |
| 2 | 3.7 | 17/22 (0.773) | 16/22 (0.727) |
| 3 | 4.9 | 21/22 (0.955) | 18/22 (0.818) |

## statement (N=21)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.3 | 7/21 (0.333) | 7/21 (0.333) |
| 2 | 4.6 | 14/21 (0.667) | 13/21 (0.619) |
| 3 | 7.1 | 18/21 (0.857) | 19/21 (0.905) |
