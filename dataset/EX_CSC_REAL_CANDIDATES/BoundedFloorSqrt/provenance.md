# BoundedFloorSqrt Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/searches/SquareRootBinarySearch.java`
- Method: `squareRoot(long num)`

The original method computes the floor of the square root using binary search.
The dataset version preserves the binary-search loop and branch structure while
adapting the interface to scalar `int` input/output.

Adaptation notes:

- The input is bounded to `0 <= number <= 120`.
- Out-of-range inputs return `-1`.
- The returned value is `floor(sqrt(number))`.
- The original `long` implementation is converted to `int` because this bounded
  domain cannot overflow.
- No arrays, strings, objects, exceptions, floating-point operations, or library
  calls are used.
