# BoundedRightmostSetBit Provenance

This subject is adapted from:

- Repository: `TheAlgorithms/Java`
- File: `src/main/java/com/thealgorithms/bitmanipulation/IndexOfRightMostSetBit.java`
- Method: `indexOfRightMostSetBit(int n)`

The original method finds the zero-based index of the rightmost set bit.  The
dataset version keeps the repeated shift/divide loop while replacing bit
operators with modulo and integer division for the current CSC toolchain.

Adaptation notes:

- The input is bounded to `0 <= number <= 100`.
- Out-of-range inputs return `-2`.
- Zero returns `-1`, matching the original no-set-bit case.
- Positive accepted inputs return the index of the rightmost set bit.
- No arrays, strings, objects, exceptions, floating-point operations, or library
  calls are used.
