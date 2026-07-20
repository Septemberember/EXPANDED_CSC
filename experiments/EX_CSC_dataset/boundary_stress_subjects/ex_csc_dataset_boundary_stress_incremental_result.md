# EX_CSC_dataset Incremental Experiment Report

- **Git commit**: `af328b27f5db0cb5392256bfbcc45d5881fc0bf4`
- **Date**: 2026-07-18
- **Environment**: macOS 15.6, Apple M4, 16GB, Python 3.13.3, Java 17.0.18

## Dataset

| Subjects | Mutants | Condition | Statement |
|---|---:|---:|---:|
| 2 | 12 | 6 | 6 |

## RQ1: CSC-only vs CSC+Boundary

| Subject | Mode | Tests | Nodes | Infeasible | Out-of-Range | Empty | Wall Time (s) |
|---|---|---|---|---:|---:|---:|---:|---:|
| BoundaryStressCounter | CSC-only | 15 | 73 | 11 | 0 | 22 | 5.2 |
| BoundaryStressMeter | CSC-only | 15 | 105 | 27 | 0 | 22 | 5.5 |
| BoundaryStressCounter | CSC+Boundary | 74 | 751 | 292 | 10 | 0 | 50.5 |
| BoundaryStressMeter | CSC+Boundary | 74 | 913 | 373 | 10 | 0 | 84.7 |

Key: Both subjects have exactly 10 RANGE_EXCLUDED leaves in CSC+Boundary.

## RQ1 Kill Analysis

| Scope | Mutants | CSC-only | Boundary | Both | Boundary-only | Neither |
|---|---:|---:|---:|---:|---:|---:|
| EX_CSC_dataset | 12 | 10 | 10 | 10 | 0 | 2 |

M8 mutants (BoundaryStressCounter_M8, BoundaryStressMeter_M8) survive both modes — validated_range_excluded_survivor.

## RQ2: Parallel Scaling

| W | Mean Time (s) | Median Time (s) | Tests | Nodes | S_mean | S_median |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 70.11 | 70.11 | 81.0 | 832.0 | 1.00 | 1.00 |
| 2 | 56.79 | 56.79 | 81.0 | 832.0 | 1.24 | 1.24 |
| 4 | 52.80 | 52.80 | 81.0 | 832.0 | 1.33 | 1.33 |
| 8 | 54.16 | 54.16 | 81.0 | 832.0 | 1.29 | 1.29 |

Fingerprints: 2/2 invariant across all workers.

## RQ3: Budget-Matched Fault Localization (N=10)

| Top-K | Folded | SBFL DStar | SBFL Ochiai | SBFL Op2 |
|---:|---:|---:|---:|---:|
| 1 | 8/10 (80.0%) | 6/10 (60.0%) | 6/10 (60.0%) | 6/10 (60.0%) |
| 2 | 10/10 (100.0%) | 9/10 (90.0%) | 9/10 (90.0%) | 9/10 (90.0%) |
| 3 | 10/10 (100.0%) | 10/10 (100.0%) | 10/10 (100.0%) | 10/10 (100.0%) |

Condition (N=6): Folded Top-1 = 6/6 (100%)
Statement (N=4): Folded Top-1 = 2/4 (50%), Top-2 = 4/4 (100%)

## Deviations

None. All acceptance criteria met.
