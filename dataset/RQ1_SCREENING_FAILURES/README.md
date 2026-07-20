# RQ1 Screening Failures

This directory preserves two candidate subjects excluded during the common-corpus
screening step. It is intentionally separate from `EX_CSC` through `EX_CSC_dataset`,
which contain the 40 subjects used in all reported RQ aggregates.

- `ShiftBandClassifier` reaches a branch predicate containing Java's `<<`
  operator, which is outside the supported Java-to-SMT translation subset.
- `GuardedQuotient` bootstraps normally, but the next CSC-generated input is
  `value = 7`, which raises `ArithmeticException` before a complete trace can be
  committed to the CCT.
