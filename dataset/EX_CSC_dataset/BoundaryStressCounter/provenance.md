# BoundaryStressCounter Provenance

- Source dataset: `dataset/EX_CSC_BOUNDARY_STRESS`.
- Original source: `BoundaryStressCounter/BoundaryStressCounter.java`.
- Mutants M1--M5 are copied from the source dataset without semantic changes.
- M8 is the validated range-excluded mutant.
- FSF: `BoundaryStressCounter/FSF/BoundaryStressCounter_FSF.txt`.
- Validation experiment: `experiments/EX_CSC_dataset/boundary_stress/RangeExcludedCandidate-M8`.

With `range-bound=200`, M8 is not killed by either CSC-only or
CSC+Boundary. The Boundary CCT contains 10 `RANGE_EXCLUDED` leaves. For the
FSF-covered witness `steps=3, quota=500, boost=0`, the original returns 5 and
M8 returns 6, violating `fsf_4`.
