# EX_CSC_dataset

`EX_CSC_dataset` stores subjects used to study bounded CSC expansion and
range-excluded mutant survival. It is maintained independently from the
exploratory `EX_CSC_BOUNDARY_STRESS` directory.

Current contents:

- `BoundaryStressCounter`: one original program, its FSF, and six single-line
  mutants. M1--M3 are condition/control-flow mutants; M4, M5, and M8 are
  statement/data-flow mutants. M8 is the validated range-excluded mutant.
- `BoundaryStressMeter`: one original program, its FSF, and the same balanced
  3+3 mutant structure. Its M8 is independently validated as the second
  range-excluded mutant.

A range-excluded mutant is retained only when all of the following hold:

1. the original passes Refined TBFV;
2. CSC-only and CSC+Boundary with the configured range bound do not kill it;
3. the Boundary CCT contains `RANGE_EXCLUDED` leaves;
4. the FSF covers a concrete input outside the configured expansion range;
5. the original satisfies the FSF for that input and the mutant violates it.

The supporting experiment for the current subject is stored under
`experiments/EX_CSC_dataset/boundary_stress/RangeExcludedCandidate-M8`.
