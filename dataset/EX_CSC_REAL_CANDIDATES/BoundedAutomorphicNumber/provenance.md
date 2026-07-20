# BoundedAutomorphicNumber Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/AutomorphicNumber.java`
- Method: `isAutomorphic(long n)`

The original method checks whether a number appears in the final digits of its
square.  The dataset version preserves the digit-counting loop and final suffix
comparison while replacing `Math.pow` with an integer multiplier loop.

Adaptation notes:

- The input is bounded to `0 <= number <= 99`.
- Out-of-range inputs return `-1`.
- Automorphic numbers in the accepted range return `1`; all other accepted
  inputs return `0`.
- The original boolean result is represented as an `int` result.
- No arrays, strings, objects, exceptions, floating-point operations, or library
  calls are used.
