# Budget-Matched Comparison: Folded Composite vs SFL

- SFL formula: `ochiai`
- Top-R: 1, 2, 3
- Method: folded composite inspection budget = union of condition[:R] and edge_partition[:R] lines.  SFL receives the same number of unique source lines.

## overall (N=46)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.3 | 34/46 (0.739) | 32/46 (0.696) |
| 2 | 4.2 | 44/46 (0.957) | 38/46 (0.826) |
| 3 | 6.0 | 45/46 (0.978) | 41/46 (0.891) |

## condition (N=23)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.1 | 17/23 (0.739) | 15/23 (0.652) |
| 2 | 3.9 | 22/23 (0.957) | 19/23 (0.826) |
| 3 | 5.2 | 22/23 (0.957) | 20/23 (0.870) |

## statement (N=23)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.4 | 17/23 (0.739) | 17/23 (0.739) |
| 2 | 4.6 | 22/23 (0.957) | 19/23 (0.826) |
| 3 | 6.9 | 23/23 (1.000) | 21/23 (0.913) |
