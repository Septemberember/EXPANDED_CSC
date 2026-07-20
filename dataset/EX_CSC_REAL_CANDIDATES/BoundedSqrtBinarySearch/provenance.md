# BoundedSqrtBinarySearch Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/searches/SquareRootBinarySearch.java`
- Method: `squareRoot(long num)`

The original method computes the floor of the square root by binary search.  The
dataset version keeps the same control-flow structure and loop update rules,
but adapts the method to the current CSC tool constraints.

Adaptation notes:

- The `long` input and return type are changed to `int`.
- The accepted input range is bounded to `0 <= num <= 80`.
- Unsupported negative and out-of-range inputs return `-1` instead of relying
  on unbounded behavior.
- No arrays, strings, objects, exceptions, or library calls are used.
- The FSF specifies the mathematical floor-square-root result by contiguous
  input intervals.
