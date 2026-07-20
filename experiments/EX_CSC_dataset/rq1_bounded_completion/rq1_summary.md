# RQ1 Bounded Completion — 24 Programs (corrected W=1)

## Table 1 — By Structural Class
| Class | N | Tests C/B | Empty C/B | ⊥ C/B | ⊥_B B | Nodes C/B | Wall C/B (s) |
|---|---|---|---|---|---|---|---|
| Loop-free | 7 | 207/207 | 0/0 | 213/213 | 0 | 839/839 | 61/58 |
| Loop-bearing | 17 | 15/149 | 12/0 | 12/333 | 0 | 66/962 | 5/47 |

## Per-Program
| Subject | Class | T CSC | T Bnd | E CSC | E Bnd | ⊥ CSC | ⊥ Bnd | ⊥_B | N CSC | N Bnd | W CSC | W Bnd |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AddLoop | loop-bearing | 8 | 205 | 1 | 0 | 1 | 3 | 0 | 18 | 415 | 3 | 74 |
| BubbleSortFive | loop-free | 120 | 120 | 0 | 0 | 194 | 194 | 0 | 627 | 627 | 35 | 34 |
| GappedSwapFive | loop-free | 120 | 120 | 0 | 0 | 164 | 164 | 0 | 567 | 567 | 36 | 34 |
| GradePolicy | loop-bearing | 10 | 148 | 4 | 0 | 2 | 122 | 0 | 27 | 539 | 3 | 41 |
| InventoryReorder | loop-bearing | 9 | 109 | 4 | 0 | 3 | 103 | 0 | 27 | 423 | 3 | 29 |
| LoopBubbleSortFive | loop-bearing | 22 | 120 | 69 | 0 | 91 | 1400 | 0 | 294 | 3039 | 6 | 41 |
| LoopSelectionSortFive | loop-bearing | 82 | 226 | 16 | 0 | 60 | 1538 | 0 | 299 | 3527 | 24 | 72 |
| MarginAdjustLoop | loop-bearing | 10 | 126 | 8 | 0 | 0 | 120 | 0 | 27 | 491 | 3 | 38 |
| MaxOfFive | loop-free | 219 | 219 | 0 | 0 | 124 | 124 | 0 | 685 | 685 | 63 | 60 |
| MedianOfSix | loop-free | 384 | 384 | 0 | 0 | 128 | 128 | 0 | 1023 | 1023 | 117 | 108 |
| MedianWindowFive | loop-free | 84 | 84 | 0 | 0 | 36 | 36 | 0 | 239 | 239 | 24 | 25 |
| OddEvenSortFive | loop-bearing | 16 | 120 | 4 | 0 | 6 | 662 | 0 | 47 | 1563 | 5 | 38 |
| PairSortCheck | loop-free | 219 | 219 | 0 | 0 | 124 | 124 | 0 | 685 | 685 | 61 | 60 |
| RewardCapLoop | loop-bearing | 10 | 86 | 8 | 0 | 2 | 114 | 0 | 31 | 399 | 3 | 25 |
| SaturatingPenaltyLoop | loop-bearing | 7 | 77 | 4 | 0 | 1 | 37 | 0 | 19 | 227 | 3 | 22 |
| ScoreNormalizer | loop-bearing | 10 | 167 | 4 | 0 | 5 | 186 | 0 | 33 | 705 | 3 | 48 |
| SelectionSortFive | loop-free | 304 | 304 | 0 | 0 | 719 | 719 | 0 | 2045 | 2045 | 92 | 88 |
| SubtractLoop | loop-bearing | 8 | 205 | 1 | 0 | 1 | 3 | 0 | 18 | 415 | 3 | 72 |
| TailRotateSortFive | loop-bearing | 23 | 120 | 65 | 0 | 26 | 701 | 0 | 162 | 1641 | 7 | 37 |
| TaxBracket | loop-bearing | 10 | 326 | 2 | 0 | 0 | 2 | 0 | 21 | 655 | 3 | 101 |
| TicketPrice | loop-bearing | 12 | 206 | 2 | 0 | 2 | 6 | 0 | 29 | 423 | 4 | 61 |
| TwoBucketLoop | loop-bearing | 8 | 91 | 4 | 0 | 2 | 117 | 0 | 23 | 415 | 3 | 26 |
| WaterBillCaculator | loop-bearing | 5 | 31 | 8 | 0 | 0 | 538 | 0 | 17 | 1137 | 2 | 21 |
| WeightedAddLoop | loop-bearing | 12 | 166 | 2 | 0 | 2 | 6 | 0 | 29 | 343 | 4 | 49 |