# Multi-SBFL Budget-Matched Comparison

- Scope: experimental analysis only; no paper text is changed.
- Folded method: existing folded composite.
- Budget: the same folded Top-K source-line region size used in the current RQ3 budget-matched comparison.
- SFL formulas: `ochiai`, `tarantula`, `dstar`, `barinel`, `op2`.

## Best Three SFL Formulas by Overall Mean Top-K Hit Rate

| Rank | Formula | Mean Top-K Rate | Top Rates |
| ---: | --- | ---: | --- |
| 1 | `dstar` | 0.628 | top1=0.395, top2=0.651, top3=0.837 |
| 2 | `ochiai` | 0.628 | top1=0.395, top2=0.651, top3=0.837 |
| 3 | `op2` | 0.628 | top1=0.395, top2=0.651, top3=0.837 |

## overall (N=43)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.2 | 18/43 (0.419) | 17/43 (0.395) | 16/43 (0.372) | 17/43 (0.395) | 16/43 (0.372) | 17/43 (0.395) |
| 2 | 3.9 | 29/43 (0.674) | 28/43 (0.651) | 27/43 (0.628) | 28/43 (0.651) | 27/43 (0.628) | 28/43 (0.651) |
| 3 | 5.9 | 39/43 (0.907) | 36/43 (0.837) | 34/43 (0.791) | 36/43 (0.837) | 34/43 (0.791) | 36/43 (0.837) |

## condition (N=21)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.1 | 11/21 (0.524) | 10/21 (0.476) | 9/21 (0.429) | 10/21 (0.476) | 9/21 (0.429) | 10/21 (0.476) |
| 2 | 3.4 | 16/21 (0.762) | 14/21 (0.667) | 14/21 (0.667) | 14/21 (0.667) | 14/21 (0.667) | 14/21 (0.667) |
| 3 | 4.9 | 20/21 (0.952) | 16/21 (0.762) | 16/21 (0.762) | 16/21 (0.762) | 16/21 (0.762) | 16/21 (0.762) |

## statement (N=22)

| Top-K | Mean Budget | Folded | ochiai | tarantula | dstar | barinel | op2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.3 | 7/22 (0.318) | 7/22 (0.318) | 7/22 (0.318) | 7/22 (0.318) | 7/22 (0.318) | 7/22 (0.318) |
| 2 | 4.4 | 13/22 (0.591) | 14/22 (0.636) | 13/22 (0.591) | 14/22 (0.636) | 13/22 (0.591) | 14/22 (0.636) |
| 3 | 7.0 | 19/22 (0.864) | 20/22 (0.909) | 18/22 (0.818) | 20/22 (0.909) | 18/22 (0.818) | 20/22 (0.909) |