# EX_CSC_dataset Coverage x Purity Validation

Date: 2026-07-13

## Scope

This validation replays only the fault-localization analysis from the archived
CCT, trace, and refined-TBFV artifacts. It does not rerun CSC generation, Java
execution, or refined TBFV.

The selected score is:

```text
Risk(c) = (F_c / F_total) * (F_c / (F_c + P_c))
```

## EX_CSC_dataset Result

| Top-k | Mean budget | Coverage x purity | Previous density log | Op2 under the new budget |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 2.3 | 34/46 (73.9%) | 32/46 (69.6%) | 33/46 (71.7%) |
| 2 | 4.2 | 44/46 (95.7%) | 43/46 (93.5%) | 38/46 (82.6%) |
| 3 | 6.0 | 45/46 (97.8%) | 45/46 (97.8%) | 44/46 (95.7%) |

## Combined Paper Result

Combining the existing coverage-x-purity results for EX_CSC_dataset--4 with the new
EX_CSC_dataset replay gives 215 evaluated mutants.

| Top-k | Mean budget | Folded composite | Op2 | DStar | Ochiai |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.6 | 136/215 (63.3%) | 130/215 (60.5%) | 127/215 (59.1%) | 127/215 (59.1%) |
| 2 | 4.6 | 172/215 (80.0%) | 165/215 (76.7%) | 164/215 (76.3%) | 163/215 (75.8%) |
| 3 | 6.7 | 190/215 (88.4%) | 192/215 (89.3%) | 188/215 (87.4%) | 188/215 (87.4%) |

The paper's qualitative conclusion is unchanged: the folded composite is
strongest at Top-1 and Top-2 and remains competitive at Top-3, where Op2 is
higher by 0.9 percentage points.

## Artifacts

- `folded-replay-coverage-x-purity/`
- `folded-budget-matched-coverage-x-purity/`
- `folded-budget-matched-coverage-x-purity/multi-sfl/`
