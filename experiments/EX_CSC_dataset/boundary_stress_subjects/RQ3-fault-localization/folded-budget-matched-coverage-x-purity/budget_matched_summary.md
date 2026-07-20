# Budget-Matched Comparison: Folded Composite vs SFL

- SFL formula: `ochiai`
- Top-R: 1, 2, 3
- Method: folded composite inspection budget = union of condition[:R] and edge_partition[:R] lines.  SFL receives the same number of unique source lines.

## overall (N=10)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.0 | 8/10 (0.800) | 6/10 (0.600) |
| 2 | 3.8 | 10/10 (1.000) | 9/10 (0.900) |
| 3 | 5.6 | 10/10 (1.000) | 10/10 (1.000) |

## condition (N=6)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.0 | 6/6 (1.000) | 4/6 (0.667) |
| 2 | 3.7 | 6/6 (1.000) | 6/6 (1.000) |
| 3 | 5.3 | 6/6 (1.000) | 6/6 (1.000) |

## statement (N=4)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.0 | 2/4 (0.500) | 2/4 (0.500) |
| 2 | 4.0 | 4/4 (1.000) | 3/4 (0.750) |
| 3 | 6.0 | 4/4 (1.000) | 4/4 (1.000) |
