# BoundedAbundantNumber Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/AbundantNumber.java`
- Method: `isAbundant(int number)` with helper `sumOfDivisors(int n)`

The original implementation computes the sum of divisors and checks whether the
sum is greater than `2 * number`.  The dataset version keeps the divisor loop
and abundance predicate while adapting helper and validation behavior to the CSC
tooling constraints.

Adaptation notes:

- The input is bounded to `1 <= number <= 30`.
- Out-of-range inputs return `-1`.
- Abundant numbers return `1`; non-abundant numbers return `0`.
- The helper method and exception-based validation are inlined into one
  scalar-only method.
- No arrays, strings, objects, exceptions, or library calls are used.
