# RQ4 Fold-the-Tree Replay — Comparison Summary

- Folded scoring: `density_log`
- Top-K: 1, 2, 3
- Evaluated: 126 / 144 total tasks
- Old baseline: `/Users/jiazedong/WorkSpace/ZedResearch/CSC_EXT/project/CSC_EXPANDED/experiments/EX_CSC_dataset/fault_localization_combined/combined_cct_fault_localization_rows.jsonl`

## Folded Composite (cond ∪ edge-part) vs Old Composite (cond ∪ gated)

### overall (old N=126, folded N=126)

| Metric | Old | Folded |
|--------|-----|--------|
| hit | 125/126  (0.992) | 108/126  (0.857) |
| top-1 |  65/126  (0.516) |  84/126  (0.667) |
| top-2 | — | 102/126  (0.810) |
| top-3 |  91/126  (0.722) | 108/126  (0.857) |

### condition (old N=61, folded N=61)

| Metric | Old | Folded |
|--------|-----|--------|
| hit |  60/61   (0.984) |  45/61   (0.738) |
| top-1 |  27/61   (0.443) |  38/61   (0.623) |
| top-2 | — |  41/61   (0.672) |
| top-3 |  42/61   (0.689) |  45/61   (0.738) |

### statement (old N=65, folded N=65)

| Metric | Old | Folded |
|--------|-----|--------|
| hit |  65/65   (1.000) |  63/65   (0.969) |
| top-1 |  38/65   (0.585) |  46/65   (0.708) |
| top-2 | — |  61/65   (0.938) |
| top-3 |  49/65   (0.754) |  63/65   (0.969) |

## Folded Edge-Partition vs Old Edge-Divergence-Gated

### overall (old N=126, folded N=126)

| Metric | Old | Folded |
|--------|-----|--------|
| hit |  65/126  (0.516) |  65/126  (0.516) |
| top-1 |  38/126  (0.302) |  46/126  (0.365) |
| top-2 | — |  61/126  (0.484) |
| top-3 |  49/126  (0.389) |  63/126  (0.500) |

### condition (old N=61, folded N=61)

| Metric | Old | Folded |
|--------|-----|--------|
| hit |   0/61   (0.000) |   0/61   (0.000) |
| top-1 |   0/61   (0.000) |   0/61   (0.000) |
| top-2 | — |   0/61   (0.000) |
| top-3 |   0/61   (0.000) |   0/61   (0.000) |

### statement (old N=65, folded N=65)

| Metric | Old | Folded |
|--------|-----|--------|
| hit |  65/65   (1.000) |  65/65   (1.000) |
| top-1 |  38/65   (0.585) |  46/65   (0.708) |
| top-2 | — |  61/65   (0.938) |
| top-3 |  49/65   (0.754) |  63/65   (0.969) |

## Folded Condition vs Old Condition

### overall (old N=126, folded N=126)

| Metric | Old | Folded |
|--------|-----|--------|
| hit |  60/126  (0.476) |  60/126  (0.476) |
| top-1 |  27/126  (0.214) |  38/126  (0.302) |
| top-3 |  42/126  (0.333) |  45/126  (0.357) |

### condition (old N=61, folded N=61)

| Metric | Old | Folded |
|--------|-----|--------|
| hit |  60/61   (0.984) |  60/61   (0.984) |
| top-1 |  27/61   (0.443) |  38/61   (0.623) |
| top-3 |  42/61   (0.689) |  45/61   (0.738) |

### statement (old N=65, folded N=65)

| Metric | Old | Folded |
|--------|-----|--------|
| hit |   0/65   (0.000) |   0/65   (0.000) |
| top-1 |   0/65   (0.000) |   0/65   (0.000) |
| top-3 |   0/65   (0.000) |   0/65   (0.000) |
