# BoundedProductRange Provenance

This subject is derived from scalar arithmetic kernels in:

- Guava `com.google.common.math.IntMath.factorial`
- Guava `com.google.common.math.IntMath.pow`
- Apache Commons Numbers `org.apache.commons.numbers.core.ArithmeticUtils.pow`

The original Guava factorial implementation uses a precomputed array table for
small factorials, which is outside the current CSC tool's supported input model.
This dataset subject keeps the same mathematical theme, a bounded multiplicative
integer product with saturation, but rewrites it as a scalar-only range product.

Adaptation notes:

- No arrays, collections, objects, strings, exceptions, or library calls.
- The product range is bounded to `1 <= start <= end <= 5`.
- `highCap` selects a saturation threshold of `60` or `120`.
- The loop is deterministic and bounded by at most five iterations.
- The FSF partitions enumerate each valid scalar `(start, end, highCap)` region
  plus one invalid-input region.
