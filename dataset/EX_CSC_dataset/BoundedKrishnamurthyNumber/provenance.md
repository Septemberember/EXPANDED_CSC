# BoundedKrishnamurthyNumber Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/KrishnamurthyNumber.java`
- Method: `isKrishnamurthy(int n)`

The original method checks whether a number equals the sum of the factorials of
its decimal digits.  The repository version uses a precomputed factorial array;
the dataset version replaces that array with a small bounded factorial loop for
each digit.

Adaptation notes:

- The input is bounded to `1 <= number <= 200`.
- Out-of-range inputs return `-1`.
- Krishnamurthy numbers in the accepted range return `1`; all others return
  `0`.
- The original boolean result is represented as an `int` result.
- No arrays, strings, objects, exceptions, floating-point operations, or library
  calls are used.
