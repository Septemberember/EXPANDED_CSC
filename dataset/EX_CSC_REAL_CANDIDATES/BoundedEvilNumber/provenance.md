# BoundedEvilNumber Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/maths/EvilNumber.java`
- Method: `isEvilNumber(int number)` and helper `countOneBits(int number)`

The original method checks whether the binary representation of a non-negative
integer has an even number of one bits.  The dataset version preserves the bit
counting loop but uses division and modulo instead of bit shifts so that the
current CSC toolchain can process it more predictably.

Adaptation notes:

- The input is bounded to `0 <= number <= 100`.
- Out-of-range inputs return `-1`.
- Evil numbers return `1`; odious numbers return `0`.
- The original boolean result is represented as an `int` result.
- No arrays, strings, objects, exceptions, floating-point operations, or library
  calls are used.
