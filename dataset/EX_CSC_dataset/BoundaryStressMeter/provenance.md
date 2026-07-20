# BoundaryStressMeter Provenance

- Source dataset: `dataset/EX_CSC_BOUNDARY_STRESS`.
- Original source: `BoundaryStressMeter/BoundaryStressMeter.java`.
- Mutants M1--M5 are copied from the source dataset without semantic changes.
- M8 is constructed as the candidate range-excluded mutant.
- FSF: `BoundaryStressMeter/FSF/BoundaryStressMeter_FSF.txt`.
- Validation experiment: `experiments/EX_CSC_dataset/boundary_stress_subjects/RangeExcluded-BoundaryStressMeter-M8`.

With `range-bound=200`, M8 is not killed by either CSC-only or CSC+Boundary.
The Boundary CCT contains 10 `RANGE_EXCLUDED` leaves. For the FSF-covered
witness `days=3, limit=500, surge=0`, the expected and original return value is
6; M8 returns 7, violating `fsf_4`.
