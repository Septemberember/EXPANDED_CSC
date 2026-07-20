# RQ1 Bounded Completion Summary

- RQ1 CSC-only runs: 8 completed
- RQ2 CSC+Boundary W=1 runs: 8 completed
- Subjects: 8

## Per-Subject Comparison

| Subject | Mode | Tests | Total Nodes | Leaf Nodes | Covered | Infeasible | Out-of-Range | Empty | Expanded | Max Depth | Wall Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BoundedAbundantNumber | CSC-only | 5 | 15 | 6 | 5 | 1 | 0 | 4 | 0 | 6 | 1.894 |
| BoundedEvilNumber | CSC-only | 5 | 17 | 8 | 5 | 3 | 0 | 2 | 0 | 7 | 1.753 |
| BoundedIntPower | CSC-only | 12 | 29 | 15 | 12 | 3 | 0 | 0 | 0 | 10 | 3.713 |
| BoundedKrishnamurthyNumber | CSC-only | 5 | 15 | 7 | 5 | 2 | 0 | 2 | 0 | 6 | 1.763 |
| BoundedPerfectNumber | CSC-only | 4 | 13 | 6 | 4 | 2 | 0 | 2 | 0 | 6 | 1.467 |
| BoundedPrimeClassifier | CSC-only | 4 | 13 | 7 | 4 | 3 | 0 | 0 | 0 | 6 | 1.497 |
| BoundedPronicNumber | CSC-only | 4 | 15 | 7 | 4 | 3 | 0 | 2 | 0 | 8 | 1.506 |
| SaturatedIntPower | CSC-only | 10 | 33 | 16 | 10 | 6 | 0 | 2 | 0 | 11 | 3.221 |
| BoundedAbundantNumber | CSC+Boundary | 50 | 1161 | 581 | 50 | 531 | 0 | 0 | 45 | 52 | 24.157 |
| BoundedEvilNumber | CSC+Boundary | 103 | 735 | 368 | 103 | 265 | 0 | 0 | 99 | 19 | 30.738 |
| BoundedIntPower | CSC+Boundary | 30 | 71 | 36 | 30 | 6 | 0 | 0 | 21 | 17 | 9.737 |
| BoundedKrishnamurthyNumber | CSC+Boundary | 172 | 1027 | 514 | 172 | 341 | 1 | 0 | 169 | 26 | 52.445 |
| BoundedPerfectNumber | CSC+Boundary | 52 | 2923 | 1462 | 52 | 1410 | 0 | 0 | 48 | 102 | 62.807 |
| BoundedPrimeClassifier | CSC+Boundary | 51 | 3057 | 1529 | 51 | 1478 | 0 | 0 | 49 | 104 | 64.055 |
| BoundedPronicNumber | CSC+Boundary | 53 | 225 | 113 | 53 | 60 | 0 | 0 | 49 | 106 | 21.153 |
| SaturatedIntPower | CSC+Boundary | 38 | 107 | 54 | 38 | 16 | 0 | 0 | 28 | 17 | 15.595 |

## Aggregate Comparison

| Mode | Subjects | Mean Tests | Mean Total Nodes | Mean Leaf Nodes | Mean Covered | Mean Infeasible | Mean Out-of-Range | Mean Empty | Mean Expanded | Mean Max Depth | Mean Wall Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CSC-only | 8 | 6.125 | 18.750 | 9 | 6.125 | 2.875 | 0 | 1.750 | 0 | 7.500 | 2.102 |
| CSC+Boundary | 8 | 68.625 | 1163.250 | 582.125 | 68.625 | 513.375 | 0.125 | 0 | 63.500 | 55.375 | 35.086 |

## Leaf Distribution Delta (CSC+Boundary - CSC-only)

| Metric | CSC-only | CSC+Boundary | Delta |
| --- | --- | --- | --- |
| Tests | 6.125 | 68.625 | +62.5 (+1020.4%) |
| Total Nodes | 18.750 | 1163.250 | +1144.5 (+6104.0%) |
| Leaf Nodes | 9 | 582.125 | +573.1 (+6368.1%) |
| Covered Leaves | 6.125 | 68.625 | +62.5 (+1020.4%) |
| Infeasible Leaves | 2.875 | 513.375 | +510.5 (+17756.5%) |
| Out-of-Range Leaves | 0 | 0.125 | +0.1 |
| Empty Leaves | 1.750 | 0 | -1.8 (-100.0%) |
| Expanded Leaves | 0 | 63.500 | +63.5 |
| Wall Time (s) | 2.102 | 35.086 | +33.0 (+1569.3%) |
