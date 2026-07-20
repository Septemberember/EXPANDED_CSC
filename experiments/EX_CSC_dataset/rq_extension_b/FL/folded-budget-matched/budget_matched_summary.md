# Budget-Matched Comparison: Folded Composite vs SFL

- SFL formula: `ochiai`
- Top-R: 1, 2, 3
- Method: folded composite inspection budget = union of condition[:R] and edge_partition[:R] lines.  SFL receives the same number of unique source lines.

## overall (N=46)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.2 | 32/46 (0.696) | 32/46 (0.696) |
| 2 | 4.2 | 43/46 (0.935) | 38/46 (0.826) |
| 3 | 6.0 | 45/46 (0.978) | 41/46 (0.891) |

## condition (N=23)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.1 | 17/23 (0.739) | 14/23 (0.609) |
| 2 | 3.8 | 22/23 (0.957) | 19/23 (0.826) |
| 3 | 5.2 | 22/23 (0.957) | 20/23 (0.870) |

## statement (N=23)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.4 | 15/23 (0.652) | 18/23 (0.783) |
| 2 | 4.5 | 21/23 (0.913) | 19/23 (0.826) |
| 3 | 6.8 | 23/23 (1.000) | 21/23 (0.913) |
