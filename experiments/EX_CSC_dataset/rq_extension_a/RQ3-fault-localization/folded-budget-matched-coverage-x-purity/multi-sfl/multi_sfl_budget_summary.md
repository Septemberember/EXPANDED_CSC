# Multi-SBFL Budget-Matched Comparison

- Scope: experimental analysis only; no paper text is changed.
- Folded method: existing folded composite.
- Budget: the same folded Top-K source-line region size used in the current RQ3 budget-matched comparison.
- SFL formulas: `ochiai`, `tarantula`, `dstar`, `barinel`, `op2`.

## Best Three SFL Formulas by Overall Mean Top-K Hit Rate

| Rank | Formula | Mean Top-K Rate | Top Rates |
| ---: | --- | ---: | --- |
| 1 | `op2` | 0.659 | top1=0.419, top2=0.674, top3=0.884 |
| 2 | `dstar` | 0.651 | top1=0.419, top2=0.674, top3=0.860 |
| 3 | `ochiai` | 0.651 | top1=0.419, top2=0.674, top3=0.860 |

## overall (N=43)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.2 | 19/43 (0.442) | 18/43 (0.419) | 16/43 (0.372) | 18/43 (0.419) | 16/43 (0.372) | 18/43 (0.419) |
| 2 | 4.1 | 31/43 (0.721) | 29/43 (0.674) | 28/43 (0.651) | 29/43 (0.674) | 28/43 (0.651) | 29/43 (0.674) |
| 3 | 6.0 | 39/43 (0.907) | 37/43 (0.860) | 34/43 (0.791) | 37/43 (0.860) | 34/43 (0.791) | 38/43 (0.884) |

## condition (N=22)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.2 | 12/22 (0.545) | 11/22 (0.500) | 9/22 (0.409) | 11/22 (0.500) | 9/22 (0.409) | 11/22 (0.500) |
| 2 | 3.7 | 17/22 (0.773) | 16/22 (0.727) | 16/22 (0.727) | 16/22 (0.727) | 16/22 (0.727) | 16/22 (0.727) |
| 3 | 4.9 | 21/22 (0.955) | 18/22 (0.818) | 17/22 (0.773) | 18/22 (0.818) | 17/22 (0.773) | 18/22 (0.818) |

## statement (N=21)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.3 | 7/21 (0.333) | 7/21 (0.333) | 7/21 (0.333) | 7/21 (0.333) | 7/21 (0.333) | 7/21 (0.333) |
| 2 | 4.6 | 14/21 (0.667) | 13/21 (0.619) | 12/21 (0.571) | 13/21 (0.619) | 12/21 (0.571) | 13/21 (0.619) |
| 3 | 7.1 | 18/21 (0.857) | 19/21 (0.905) | 17/21 (0.810) | 19/21 (0.905) | 17/21 (0.810) | 20/21 (0.952) |