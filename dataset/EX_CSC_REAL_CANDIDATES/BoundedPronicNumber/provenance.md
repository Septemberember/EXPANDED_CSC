# BoundedPronicNumber Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/PronicNumber.java`
- Method: `isPronic(int inputNumber)`

The original method checks whether a number is pronic by iterating over integer
candidates and comparing `i * (i + 1)` with the input.  The dataset version keeps
that loop and early-return structure while adapting the interface to current CSC
constraints.

Adaptation notes:

- The input is bounded to `0 <= number <= 30`.
- Out-of-range inputs return `-1`.
- Pronic numbers return `1`; non-pronic numbers return `0`.
- The boolean result from the original method is represented as an `int` result.
- No arrays, strings, objects, exceptions, or library calls are used.
