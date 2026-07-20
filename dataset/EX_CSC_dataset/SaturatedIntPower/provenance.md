# SaturatedIntPower Provenance

- Source family: repository-derived scalar arithmetic loop.
- Primary source inspiration: Google Guava `IntMath.saturatedPow(int b, int k)`
  from `guava/src/com/google/common/math/IntMath.java`.
- Adaptation:
  - removed exception checks, bitwise overflow logic, and helper calls;
  - bounded `base` to `[-5, 5]` and `exponent` to `[0, 7]`;
  - preserved repeated multiplication plus saturation behavior;
  - applies saturation after the bounded multiplication loop so the FSF can
    describe final mathematical power instead of early-overflow order;
  - added `highCap` to create two explicit cap regimes.
- Final subject constraints:
  - no arrays;
  - no objects;
  - no helper calls;
  - deterministic scalar return.
