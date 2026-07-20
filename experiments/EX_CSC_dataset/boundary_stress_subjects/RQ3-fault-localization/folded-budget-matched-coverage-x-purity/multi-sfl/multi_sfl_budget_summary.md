# Multi-SBFL Budget-Matched Comparison

- Scope: experimental analysis only; no paper text is changed.
- Folded method: existing folded composite.
- Budget: the same folded Top-K source-line region size used in the current RQ3 budget-matched comparison.
- SFL formulas: `op2`, `dstar`, `ochiai`, `tarantula`, `barinel`.

## Best Three SFL Formulas by Overall Mean Top-K Hit Rate

| Rank | Formula | Mean Top-K Rate | Top Rates |
| ---: | --- | ---: | --- |
| 1 | `dstar` | 0.833 | top1=0.600, top2=0.900, top3=1.000 |
| 2 | `ochiai` | 0.833 | top1=0.600, top2=0.900, top3=1.000 |
| 3 | `op2` | 0.833 | top1=0.600, top2=0.900, top3=1.000 |

## overall (N=10)

| Top-K | Mean Budget | Folded | op2 | dstar | ochiai | tarantula | barinel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.0 | 8/10 (0.800) | 6/10 (0.600) | 6/10 (0.600) | 6/10 (0.600) | 4/10 (0.400) | 4/10 (0.400) |
| 2 | 3.8 | 10/10 (1.000) | 9/10 (0.900) | 9/10 (0.900) | 9/10 (0.900) | 6/10 (0.600) | 6/10 (0.600) |
| 3 | 5.6 | 10/10 (1.000) | 10/10 (1.000) | 10/10 (1.000) | 10/10 (1.000) | 7/10 (0.700) | 7/10 (0.700) |

## condition (N=6)

| Top-K | Mean Budget | Folded | op2 | dstar | ochiai | tarantula | barinel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.0 | 6/6 (1.000) | 4/6 (0.667) | 4/6 (0.667) | 4/6 (0.667) | 2/6 (0.333) | 2/6 (0.333) |
| 2 | 3.7 | 6/6 (1.000) | 6/6 (1.000) | 6/6 (1.000) | 6/6 (1.000) | 4/6 (0.667) | 4/6 (0.667) |
| 3 | 5.3 | 6/6 (1.000) | 6/6 (1.000) | 6/6 (1.000) | 6/6 (1.000) | 5/6 (0.833) | 5/6 (0.833) |

## statement (N=4)

| Top-K | Mean Budget | Folded | op2 | dstar | ochiai | tarantula | barinel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.0 | 2/4 (0.500) | 2/4 (0.500) | 2/4 (0.500) | 2/4 (0.500) | 2/4 (0.500) | 2/4 (0.500) |
| 2 | 4.0 | 4/4 (1.000) | 3/4 (0.750) | 3/4 (0.750) | 3/4 (0.750) | 2/4 (0.500) | 2/4 (0.500) |
| 3 | 6.0 | 4/4 (1.000) | 4/4 (1.000) | 4/4 (1.000) | 4/4 (1.000) | 2/4 (0.500) | 2/4 (0.500) |