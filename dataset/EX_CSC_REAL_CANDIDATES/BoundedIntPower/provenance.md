# BoundedIntPower Provenance

- Source family: repository-derived scalar arithmetic loop.
- Primary source inspiration: Google Guava `IntMath.pow(int b, int k)` from `guava/src/com/google/common/math/IntMath.java`.
- Secondary source inspiration: Apache Commons Numbers `ArithmeticUtils.pow(int k, int e)` from `commons-numbers-core/src/main/java/org/apache/commons/numbers/core/ArithmeticUtils.java`.
- Adaptation:
  - removed exception-centered negative exponent and overflow behavior;
  - bounded `base` to `[-3, 3]` and `exponent` to `[0, 6]`;
  - kept the scalar multiplication loop as the core behavior;
  - added `signedMode` to create a clear branch partition for negative bases.
- Final subject constraints:
  - no arrays;
  - no objects;
  - no helper calls;
  - deterministic scalar return.
