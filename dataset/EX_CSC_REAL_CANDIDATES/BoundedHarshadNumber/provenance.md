# BoundedHarshadNumber Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/HarshadNumber.java`
- Method: `isHarshad(long n)`

The original method checks whether a positive integer is divisible by the sum
of its decimal digits.  The dataset version preserves the digit-sum loop and
final divisibility check while adapting exceptions and boolean output for CSC.

Adaptation notes:

- The input is bounded to `1 <= number <= 100`.
- Out-of-range inputs return `-1`.
- Harshad numbers return `1`; non-Harshad numbers return `0`.
- The original boolean result is represented as an `int` result.
- No arrays, strings, objects, exceptions, floating-point operations, or library
  calls are used.
