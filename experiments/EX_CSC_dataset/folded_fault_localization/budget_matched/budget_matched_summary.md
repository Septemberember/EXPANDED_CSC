# Budget-Matched Comparison: Folded Composite vs SFL

- SFL formula: `ochiai`
- Top-R: 1, 2, 3
- Method: folded composite inspection budget = union of condition[:R] and edge_partition[:R] lines.  SFL receives the same number of unique source lines.

## overall (N=126)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.8 | 84/126 (0.667) | 78/126 (0.619) |
| 2 | 5.0 | 99/126 (0.786) | 97/126 (0.770) |
| 3 | 7.3 | 106/126 (0.841) | 111/126 (0.881) |

## condition (N=61)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.6 | 38/61 (0.623) | 34/61 (0.557) |
| 2 | 4.3 | 41/61 (0.672) | 42/61 (0.689) |
| 3 | 6.1 | 45/61 (0.738) | 52/61 (0.852) |

## statement (N=65)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 3.0 | 46/65 (0.708) | 44/65 (0.677) |
| 2 | 5.7 | 58/65 (0.892) | 55/65 (0.846) |
| 3 | 8.3 | 61/65 (0.938) | 59/65 (0.908) |
