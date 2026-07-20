# Budget-Matched Comparison: Folded Composite vs SFL

- SFL formula: `ochiai`
- Top-R: 1, 2, 3
- Method: folded composite inspection budget = union of condition[:R] and edge_partition[:R] lines.  SFL receives the same number of unique source lines.

## overall (N=126)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.8 | 84/126 (0.667) | 79/126 (0.627) |
| 2 | 4.9 | 102/126 (0.810) | 96/126 (0.762) |
| 3 | 7.1 | 108/126 (0.857) | 110/126 (0.873) |

## condition (N=61)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 2.5 | 38/61 (0.623) | 35/61 (0.574) |
| 2 | 4.1 | 41/61 (0.672) | 42/61 (0.689) |
| 3 | 6.0 | 45/61 (0.738) | 52/61 (0.852) |

## statement (N=65)

| Top-R | Mean Budget | Folded Hit Rate | SFL Hit Rate (same budget) |
| --- | ---: | ---: | ---: |
| 1 | 3.0 | 46/65 (0.708) | 44/65 (0.677) |
| 2 | 5.6 | 61/65 (0.938) | 54/65 (0.831) |
| 3 | 8.2 | 63/65 (0.969) | 58/65 (0.892) |
