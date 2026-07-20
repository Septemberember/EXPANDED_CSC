# BoundedPerfectNumber Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/PerfectNumber.java`
- Method: `isPerfectNumber(int number)`

The original method checks whether a positive integer is perfect by summing its
proper divisors in a loop.  The dataset version preserves that loop and branch
structure while adapting the interface for CSC experiments.

Adaptation notes:

- The input is bounded to `1 <= number <= 30`.
- Out-of-range inputs return `-1`.
- Perfect numbers in the accepted range return `1`; non-perfect numbers return
  `0`.
- The boolean result from the original method is represented as an `int` result
  for compatibility with existing FSF and localization tooling.
- No arrays, strings, objects, exceptions, or library calls are used.
