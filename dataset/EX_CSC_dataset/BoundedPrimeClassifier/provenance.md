# BoundedPrimeClassifier Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/Prime/PrimeCheck.java`
- Method: `isPrime(int n)`

The original method checks primality using trial division.  The dataset version
keeps the divisor-testing behavior but counts all divisors in the accepted
bounded range instead of returning early, which gives CSC a richer loop body to
explore.

Adaptation notes:

- The input is bounded to `2 <= number <= 50`.
- Out-of-range inputs return `-1`.
- Prime numbers return `1`; composite numbers return `0`.
- The original boolean result is represented as an `int` result.
- The divisor loop is bounded by `divisor <= number` to avoid unsupported
  floating-point calls and to expose more feasible branch paths.
- No arrays, strings, objects, exceptions, floating-point operations, or library
  calls are used.
