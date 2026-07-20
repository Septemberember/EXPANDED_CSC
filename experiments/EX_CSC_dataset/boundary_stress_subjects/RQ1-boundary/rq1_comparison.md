# RQ1 Bounded Completion Summary

- RQ1 CSC-only runs: 2 completed
- RQ2 CSC+Boundary W=1 runs: 6 completed
- Subjects: 2

## Per-Subject Comparison

| Subject | Mode | Tests | Total Nodes | Leaf Nodes | Covered | Infeasible | Out-of-Range | Empty | Expanded | Max Depth | Wall Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BoundaryStressCounter | CSC-only | 15 | 73 | 26 | 15 | 11 | 0 | 22 | 0 | 14 | 5.247 |
| BoundaryStressMeter | CSC-only | 15 | 105 | 42 | 15 | 27 | 0 | 22 | 0 | 16 | 5.460 |
| BoundaryStressCounter | CSC+Boundary | 74 | 751 | 376 | 74 | 292 | 10 | 0 | 66 | 276 | 50.540 |
| BoundaryStressMeter | CSC+Boundary | 74 | 913 | 457 | 74 | 373 | 10 | 0 | 66 | 343 | 84.731 |
| BoundaryStressCounter | CSC+Boundary | 74 | 751 | 376 | 74 | 292 | 10 | 0 | 66 | 276 | 61.845 |
| BoundaryStressMeter | CSC+Boundary | 74 | 913 | 457 | 74 | 373 | 10 | 0 | 66 | 343 | 78.970 |
| BoundaryStressCounter | CSC+Boundary | 74 | 751 | 376 | 74 | 292 | 10 | 0 | 66 | 276 | 62.160 |
| BoundaryStressMeter | CSC+Boundary | 74 | 913 | 457 | 74 | 373 | 10 | 0 | 66 | 343 | 82.420 |

## Aggregate Comparison

| Mode | Subjects | Mean Tests | Mean Total Nodes | Mean Leaf Nodes | Mean Covered | Mean Infeasible | Mean Out-of-Range | Mean Empty | Mean Expanded | Mean Max Depth | Mean Wall Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CSC-only | 2 | 15 | 89 | 34 | 15 | 19 | 0 | 22 | 0 | 15 | 5.353 |
| CSC+Boundary | 6 | 74 | 832 | 416.500 | 74 | 332.500 | 10 | 0 | 66 | 309.500 | 70.111 |

## Leaf Distribution Delta (CSC+Boundary - CSC-only)

| Metric | CSC-only | CSC+Boundary | Delta |
| --- | --- | --- | --- |
| Tests | 15 | 74 | +59.0 (+393.3%) |
| Total Nodes | 89 | 832 | +743.0 (+834.8%) |
| Leaf Nodes | 34 | 416.500 | +382.5 (+1125.0%) |
| Covered Leaves | 15 | 74 | +59.0 (+393.3%) |
| Infeasible Leaves | 19 | 332.500 | +313.5 (+1650.0%) |
| Out-of-Range Leaves | 0 | 10 | +10.0 |
| Empty Leaves | 22 | 0 | -22.0 (-100.0%) |
| Expanded Leaves | 0 | 66 | +66.0 |
| Wall Time (s) | 5.353 | 70.111 | +64.8 (+1209.7%) |
