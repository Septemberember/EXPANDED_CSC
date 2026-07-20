# Multi-SBFL Budget-Matched Comparison

- Scope: experimental analysis only; no paper text is changed.
- Folded method: existing folded composite.
- Budget: the same folded Top-K source-line region size used in the current RQ3 budget-matched comparison.
- SFL formulas: `ochiai`, `tarantula`, `dstar`, `barinel`, `op2`.

## Best Three SFL Formulas by Overall Mean Top-K Hit Rate

| Rank | Formula | Mean Top-K Rate | Top Rates |
| ---: | --- | ---: | --- |
| 1 | `op2` | 0.826 | top1=0.696, top2=0.826, top3=0.957 |
| 2 | `dstar` | 0.804 | top1=0.696, top2=0.826, top3=0.891 |
| 3 | `ochiai` | 0.804 | top1=0.696, top2=0.826, top3=0.891 |

## overall (N=46)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.2 | 32/46 (0.696) | 32/46 (0.696) | 28/46 (0.609) | 32/46 (0.696) | 28/46 (0.609) | 32/46 (0.696) |
| 2 | 4.2 | 43/46 (0.935) | 38/46 (0.826) | 36/46 (0.783) | 38/46 (0.826) | 36/46 (0.783) | 38/46 (0.826) |
| 3 | 6.0 | 45/46 (0.978) | 41/46 (0.891) | 39/46 (0.848) | 41/46 (0.891) | 39/46 (0.848) | 44/46 (0.957) |

## condition (N=23)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.1 | 17/23 (0.739) | 14/23 (0.609) | 12/23 (0.522) | 14/23 (0.609) | 12/23 (0.522) | 14/23 (0.609) |
| 2 | 3.8 | 22/23 (0.957) | 19/23 (0.826) | 18/23 (0.783) | 19/23 (0.826) | 18/23 (0.783) | 19/23 (0.826) |
| 3 | 5.2 | 22/23 (0.957) | 20/23 (0.870) | 20/23 (0.870) | 20/23 (0.870) | 20/23 (0.870) | 23/23 (1.000) |

## statement (N=23)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.4 | 15/23 (0.652) | 18/23 (0.783) | 16/23 (0.696) | 18/23 (0.783) | 16/23 (0.696) | 18/23 (0.783) |
| 2 | 4.5 | 21/23 (0.913) | 19/23 (0.826) | 18/23 (0.783) | 19/23 (0.826) | 18/23 (0.783) | 19/23 (0.826) |
| 3 | 6.8 | 23/23 (1.000) | 21/23 (0.913) | 19/23 (0.826) | 21/23 (0.913) | 19/23 (0.826) | 21/23 (0.913) |