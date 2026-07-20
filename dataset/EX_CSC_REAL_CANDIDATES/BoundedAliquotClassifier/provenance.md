# BoundedAliquotClassifier Provenance

This subject is adapted from the aliquot/proper-divisor utilities in:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/AliquotSum.java`
- File: `src/main/java/com/thealgorithms/maths/SociableNumber.java`
- Source behavior: compute the sum of proper divisors using a divisor loop.

The dataset version preserves the proper-divisor accumulation behavior and
turns it into a compact semantic classifier:

- `-1`: out of accepted range;
- `0`: deficient number;
- `1`: perfect number;
- `2`: abundant number.

Adaptation notes:

- The input is bounded to `1 <= number <= 50`.
- The loop uses `divisor < number` to avoid unsupported floating-point square
  root calls and helper methods.
- No arrays, strings, objects, exceptions, floating-point operations, or library
  calls are used.
