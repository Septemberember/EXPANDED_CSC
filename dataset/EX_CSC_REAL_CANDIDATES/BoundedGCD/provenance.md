# BoundedGCD Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/GCD.java`
- Method: `gcd(int num1, int num2)`

The original method computes the greatest common divisor using the Euclidean
algorithm.  The dataset version preserves the same loop update logic while
adapting exceptional and library-call behavior for CSC experiments.

Adaptation notes:

- Inputs are bounded to `0 <= a <= 12` and `0 <= b <= 12`.
- Out-of-range inputs return `-1` instead of throwing an exception.
- The original `Math.abs(num1 - num2)` zero-case behavior is rewritten as a
  scalar comparison because library calls are avoided.
- No arrays, strings, objects, exceptions, or library calls are used.
