# RQ1 Bounded Completion Summary

- RQ1 CSC-only runs: 8 completed
- RQ2 CSC+Boundary W=1 runs: 8 completed
- Subjects: 8

## Per-Subject Comparison

| Subject | Mode | Tests | Total Nodes | Leaf Nodes | Covered | Infeasible | Out-of-Range | Empty | Expanded | Max Depth | Wall Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BoundedAliquotClassifier | CSC-only | 4 | 15 | 7 | 4 | 3 | 0 | 2 | 0 | 6 | 1.840 |
| BoundedBinaryPalindromeClassifier | CSC-only | 11 | 58 | 25 | 11 | 14 | 0 | 9 | 0 | 10 | 3.655 |
| BoundedBitTransitionClassifier | CSC-only | 5 | 16 | 8 | 5 | 3 | 0 | 1 | 0 | 6 | 1.928 |
| BoundedDivisorCountClassifier | CSC-only | 5 | 15 | 8 | 5 | 3 | 0 | 0 | 0 | 6 | 2.506 |
| BoundedPerfectSquareLoop | CSC-only | 4 | 12 | 6 | 4 | 2 | 0 | 1 | 0 | 6 | 1.997 |
| BoundedPopcountDensity | CSC-only | 5 | 16 | 7 | 5 | 2 | 0 | 3 | 0 | 6 | 2.337 |
| BoundedProperDivisorParity | CSC-only | 4 | 13 | 6 | 4 | 2 | 0 | 2 | 0 | 6 | 2.066 |
| BoundedSquareFreeClassifier | CSC-only | 5 | 15 | 6 | 5 | 1 | 0 | 4 | 0 | 6 | 2.437 |
| BoundedAliquotClassifier | CSC+Boundary | 52 | 3019 | 1510 | 52 | 1458 | 0 | 0 | 48 | 103 | 84.109 |
| BoundedBinaryPalindromeClassifier | CSC+Boundary | 66 | 597 | 299 | 66 | 233 | 0 | 0 | 64 | 16 | 30.952 |
| BoundedBitTransitionClassifier | CSC+Boundary | 66 | 627 | 314 | 66 | 248 | 0 | 0 | 64 | 17 | 29.345 |
| BoundedDivisorCountClassifier | CSC+Boundary | 52 | 3127 | 1564 | 52 | 1512 | 0 | 0 | 49 | 105 | 94.692 |
| BoundedPerfectSquareLoop | CSC+Boundary | 103 | 407 | 204 | 103 | 101 | 0 | 0 | 99 | 203 | 89.998 |
| BoundedPopcountDensity | CSC+Boundary | 130 | 1095 | 548 | 130 | 418 | 0 | 0 | 126 | 19 | 58.650 |
| BoundedProperDivisorParity | CSC+Boundary | 52 | 2923 | 1462 | 52 | 1410 | 0 | 0 | 48 | 102 | 87.356 |
| BoundedSquareFreeClassifier | CSC+Boundary | 40 | 265 | 133 | 40 | 93 | 0 | 0 | 35 | 22 | 17.743 |

## Aggregate Comparison

| Mode | Subjects | Mean Tests | Mean Total Nodes | Mean Leaf Nodes | Mean Covered | Mean Infeasible | Mean Out-of-Range | Mean Empty | Mean Expanded | Mean Max Depth | Mean Wall Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CSC-only | 8 | 5.375 | 20 | 9.125 | 5.375 | 3.750 | 0 | 2.750 | 0 | 6.500 | 2.346 |
| CSC+Boundary | 8 | 70.125 | 1507.500 | 754.250 | 70.125 | 684.125 | 0 | 0 | 66.625 | 73.375 | 61.606 |

## Leaf Distribution Delta (CSC+Boundary - CSC-only)

| Metric | CSC-only | CSC+Boundary | Delta |
| --- | --- | --- | --- |
| Tests | 5.375 | 70.125 | +64.8 (+1204.7%) |
| Total Nodes | 20 | 1507.500 | +1487.5 (+7437.5%) |
| Leaf Nodes | 9.125 | 754.250 | +745.1 (+8165.8%) |
| Covered Leaves | 5.375 | 70.125 | +64.8 (+1204.7%) |
| Infeasible Leaves | 3.750 | 684.125 | +680.4 (+18143.3%) |
| Out-of-Range Leaves | 0 | 0 | +0.0 |
| Empty Leaves | 2.750 | 0 | -2.8 (-100.0%) |
| Expanded Leaves | 0 | 66.625 | +66.6 |
| Wall Time (s) | 2.346 | 61.606 | +59.3 (+2526.2%) |
