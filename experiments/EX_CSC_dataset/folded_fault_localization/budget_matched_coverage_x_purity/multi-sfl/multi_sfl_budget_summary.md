# Multi-SBFL Budget-Matched Comparison

- Scope: experimental analysis only; no paper text is changed.
- Folded method: existing folded composite.
- Budget: the same folded Top-K source-line region size used in the current RQ3 budget-matched comparison.
- SFL formulas: `ochiai`, `tarantula`, `dstar`, `barinel`, `op2`.

## Best Three SFL Formulas by Overall Mean Top-K Hit Rate

| Rank | Formula | Mean Top-K Rate | Top Rates |
| ---: | --- | ---: | --- |
| 1 | `op2` | 0.762 | top1=0.643, top2=0.770, top3=0.873 |
| 2 | `dstar` | 0.757 | top1=0.627, top2=0.770, top3=0.873 |
| 3 | `ochiai` | 0.754 | top1=0.627, top2=0.762, top3=0.873 |

## overall (N=126)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.8 | 84/126 (0.667) | 79/126 (0.627) | 72/126 (0.571) | 79/126 (0.627) | 72/126 (0.571) | 81/126 (0.643) |
| 2 | 4.9 | 102/126 (0.810) | 96/126 (0.762) | 86/126 (0.683) | 97/126 (0.770) | 86/126 (0.683) | 97/126 (0.770) |
| 3 | 7.1 | 108/126 (0.857) | 110/126 (0.873) | 91/126 (0.722) | 110/126 (0.873) | 91/126 (0.722) | 110/126 (0.873) |

## condition (N=61)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.5 | 38/61 (0.623) | 35/61 (0.574) | 29/61 (0.475) | 35/61 (0.574) | 29/61 (0.475) | 36/61 (0.590) |
| 2 | 4.1 | 41/61 (0.672) | 42/61 (0.689) | 34/61 (0.557) | 43/61 (0.705) | 34/61 (0.557) | 43/61 (0.705) |
| 3 | 6.0 | 45/61 (0.738) | 52/61 (0.852) | 36/61 (0.590) | 52/61 (0.852) | 36/61 (0.590) | 52/61 (0.852) |

## statement (N=65)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 3.0 | 46/65 (0.708) | 44/65 (0.677) | 43/65 (0.662) | 44/65 (0.677) | 43/65 (0.662) | 45/65 (0.692) |
| 2 | 5.6 | 61/65 (0.938) | 54/65 (0.831) | 52/65 (0.800) | 54/65 (0.831) | 52/65 (0.800) | 54/65 (0.831) |
| 3 | 8.2 | 63/65 (0.969) | 58/65 (0.892) | 55/65 (0.846) | 58/65 (0.892) | 55/65 (0.846) | 58/65 (0.892) |