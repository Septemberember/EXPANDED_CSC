# Budget-Matched Comparison: Folded Composite vs SFL

- SFL formula: `ochiai`
- Top-R: 1, 2, 3
- Method: folded composite inspection budget = union of condition[:R] and edge_partition[:R] lines.  SFL receives the same number of unique source lines.

## overall (N=43)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.2 | 18/43 (0.419) | 17/43 (0.395) |
| 2 | 3.9 | 29/43 (0.674) | 28/43 (0.651) |
| 3 | 5.9 | 39/43 (0.907) | 36/43 (0.837) |

## condition (N=21)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.1 | 11/21 (0.524) | 10/21 (0.476) |
| 2 | 3.4 | 16/21 (0.762) | 14/21 (0.667) |
| 3 | 4.9 | 20/21 (0.952) | 16/21 (0.762) |

## statement (N=22)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.3 | 7/22 (0.318) | 7/22 (0.318) |
| 2 | 4.4 | 13/22 (0.591) | 14/22 (0.636) |
| 3 | 7.0 | 19/22 (0.864) | 20/22 (0.909) |
