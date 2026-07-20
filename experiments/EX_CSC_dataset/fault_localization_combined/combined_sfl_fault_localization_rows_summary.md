# Fault Localization Summary

## Overview

- Manifest mutants: 144
- Evaluation reports discovered: 126
- Evaluated mutants: 126
- Missing-result mutants: 0
- Invalid reports: 0
- Orphan reports: 0

## Strategy Summary

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sfl.barinel | 126 | 0.984 | 0.190 | 0.595 | 0.683 | 0.754 | 7.331 | 1.000 | 1.000 | 7.331 |
| sfl.dstar | 126 | 0.984 | 0.230 | 0.667 | 0.754 | 0.913 | 4.081 | 1.000 | 1.000 | 4.081 |
| sfl.ochiai | 126 | 0.984 | 0.230 | 0.667 | 0.754 | 0.921 | 3.968 | 1.000 | 1.000 | 3.968 |
| sfl.op2 | 126 | 0.984 | 0.238 | 0.667 | 0.778 | 0.913 | 4.016 | 1.000 | 1.000 | 4.016 |
| sfl.tarantula | 126 | 0.984 | 0.190 | 0.595 | 0.683 | 0.754 | 7.331 | 1.000 | 1.000 | 7.331 |

## Strategy Summary by Fault Category

### Condition/Control-Flow Mutants

- Fault category: `condition`
- Mutants: 61
- Strategy rows: 305

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sfl.barinel | 61 | 0.984 | 0.016 | 0.492 | 0.574 | 0.656 | 9.150 | 1.000 | 1.000 | 9.150 |
| sfl.dstar | 61 | 0.984 | 0.033 | 0.590 | 0.705 | 0.902 | 4.700 | 1.000 | 1.000 | 4.700 |
| sfl.ochiai | 61 | 0.984 | 0.033 | 0.590 | 0.705 | 0.902 | 4.750 | 1.000 | 1.000 | 4.750 |
| sfl.op2 | 61 | 0.984 | 0.066 | 0.607 | 0.738 | 0.902 | 4.567 | 1.000 | 1.000 | 4.567 |
| sfl.tarantula | 61 | 0.984 | 0.016 | 0.492 | 0.574 | 0.656 | 9.150 | 1.000 | 1.000 | 9.150 |

### Statement/Data-Flow Mutants

- Fault category: `statement`
- Mutants: 65
- Strategy rows: 325

| Strategy | Rows | Hit Rate | Top-1 | Top-3 | Top-5 | Top-10 | Mean Best Rank | Mean Region Size | Mean Hit Item Region | Mean Cumulative Region at First Hit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sfl.barinel | 65 | 0.985 | 0.354 | 0.692 | 0.785 | 0.846 | 5.625 | 1.000 | 1.000 | 5.625 |
| sfl.dstar | 65 | 0.985 | 0.415 | 0.738 | 0.800 | 0.923 | 3.500 | 1.000 | 1.000 | 3.500 |
| sfl.ochiai | 65 | 0.985 | 0.415 | 0.738 | 0.800 | 0.938 | 3.234 | 1.000 | 1.000 | 3.234 |
| sfl.op2 | 65 | 0.985 | 0.400 | 0.723 | 0.815 | 0.923 | 3.500 | 1.000 | 1.000 | 3.500 |
| sfl.tarantula | 65 | 0.985 | 0.354 | 0.692 | 0.785 | 0.846 | 5.625 | 1.000 | 1.000 | 5.625 |
