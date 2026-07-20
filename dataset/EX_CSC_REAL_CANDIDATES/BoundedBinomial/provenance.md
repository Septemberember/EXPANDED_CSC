# BoundedBinomial Provenance

- Source family: repository-derived scalar arithmetic loop.
- Primary source inspiration: Google Guava `IntMath.binomial(int n, int k)` from `guava/src/com/google/common/math/IntMath.java`.
- Adaptation:
  - bounded `n` to `[0, 8]` and `k` to `[0, 4]`;
  - removed overflow tables and helper calls;
  - preserved the combinatorial multiplication/division loop;
  - removed the mirror optimization to keep path partitions and FSF units
    one-to-one for TBFV evaluation.
- Final subject constraints:
  - no arrays;
  - no objects;
  - no helper calls;
  - deterministic scalar return.
