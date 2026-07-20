# EX_CSC_REAL_CANDIDATES Quality Report

Generated on 2026-07-03.

## Batch CSC / Refined TBFV Settings

- CSC strategy: `batch`
- CSC workers: `4`
- CSC max iteration budget: `50`
- Refined TBFV: original subject with bound FSF

## Candidate Summary

| Subject | Source inspiration | LOC | Conditions | Loops | CSC executable | TBFV passed | TBFV failed | Unsupported | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `BoundedIntPower` | Guava `IntMath.pow`, Commons Numbers `ArithmeticUtils.pow` | 24 | 8 | 1 | 24 | 24 | 0 | 0 | keep as strong candidate |
| `BoundedBinomial` | Guava `IntMath.binomial` | 18 | 5 | 1 | 10 | 10 | 0 | 0 | reserve; correct but small |
| `SaturatedIntPower` | Guava `IntMath.saturatedPow` | 28 | 11 | 1 | 30 | 30 | 0 | 0 | keep as strongest current candidate |
| `BoundedProductRange` | Guava `IntMath.factorial`, arithmetic product kernels | 24 | 7 | 1 | 15 | 34 | 0 | 0 | reject for main set; FSF/testcase ratio is not clean |
| `BoundedSqrtBinarySearch` | TheAlgorithms `SquareRootBinarySearch.squareRoot` | 24 | 8 | 1 | 27 | 37 | 0 | 0 | usable but not ideal; broad FSF intervals produce extra passes |
| `BoundedPerfectNumber` | TheAlgorithms `PerfectNumber.isPerfectNumber` | 19 | 5 | 1 | 32 | 32 | 0 | 0 | keep as strong candidate |
| `BoundedPronicNumber` | TheAlgorithms `PronicNumber.isPronic` | 18 | 7 | 1 | 33 | 33 | 0 | 0 | keep as strong candidate |
| `BoundedAbundantNumber` | TheAlgorithms `AbundantNumber.isAbundant` | 19 | 5 | 1 | 30 | 30 | 0 | 0 | keep as strong candidate |
| `BoundedGCD` | TheAlgorithms `GCD.gcd` | 18 | 8 | 1 | 11 | 54 | 0 | 0 | reject for main set; too few testcases and broad path/spec overlap |
| `BoundedFloorSqrt` | TheAlgorithms `SquareRootBinarySearch.squareRoot` | 26 | 6 | 1 | 33 | 46 | 0 | 0 | reject for main set; interval FSF still overlaps generated paths |
| `BoundedAutomorphicNumber` | TheAlgorithms `AutomorphicNumber.isAutomorphic` | 22 | 4 | 1 | 7 | 7 | 0 | 0 | reject for main set; clean but too few executable testcases |
| `BoundedAliquotClassifier` | TheAlgorithms `AliquotSum`, `SociableNumber` divisor-sum kernels | 22 | 5 | 1 | 52 | 52 | 0 | 0 | keep as strong candidate |
| `BoundedPrimeClassifier` | TheAlgorithms `PrimeCheck.isPrime` | 19 | 4 | 1 | 51 | 51 | 0 | 0 | keep as strong candidate after bounding to 50 |
| `BoundedHarshadNumber` | TheAlgorithms `HarshadNumber.isHarshad` | 18 | 3 | 1 | 6 | 6 | 0 | 0 | reject for main set; clean but too few executable testcases |
| `BoundedEvilNumber` | TheAlgorithms `EvilNumber.isEvilNumber` | 22 | 5 | 1 | 103 | 103 | 0 | 0 | keep as strong candidate |
| `BoundedRightmostSetBit` | TheAlgorithms `IndexOfRightMostSetBit.indexOfRightMostSetBit` | 17 | 3 | 1 | 10 | 10 | 0 | 0 | reject for main set; clean but path classes are too few |
| `BoundedKrishnamurthyNumber` | TheAlgorithms `KrishnamurthyNumber.isKrishnamurthy` | 24 | 3 | 2 | 173 | 173 | 0 | 0 | keep as strong candidate |

## Observations

- `BoundedIntPower` is a good first repository-derived scalar arithmetic-loop
  subject.  It has enough FSF partitions, clean executable count, and zero TBFV
  failures.
- `BoundedBinomial` initially used a mirror optimization inspired by Guava, but
  that caused several symbolic paths to match multiple FSF units.  The mirror
  branch was removed, after which TBFV became clean: `10` testcases and `10`
  passes.
- The revised `BoundedBinomial` is technically valid but probably too small for
  the main benchmark.  It can remain as a reserve or be expanded later with
  additional scalar branch structure.
- `SaturatedIntPower` is the best real-source candidate so far.  The first
  version saturated inside the loop and produced several TBFV failures because
  the FSF described final mathematical saturation.  After moving saturation to
  the post-loop decision, CSC produced `30` executable testcases and TBFV passed
  exactly `30` units with zero failures.
- `BoundedProductRange` was an attempted scalar-loop rewrite of factorial-style
  range multiplication.  It runs successfully, but the result is not benchmark
  quality: CSC produced only `15` executable testcases and Refined TBFV counted
  `34` passed FSF matches, so the FSF partition is not clean enough for the main
  dataset.
- `BoundedSqrtBinarySearch` is a realistic scalar loop subject from
  TheAlgorithms.  It completes CSC quickly and has zero TBFV failures, but the
  interval-style FSF produces `37` passed checks for `27` testcases because some
  CCT leaf path regions intersect more than one floor-square-root interval.
- `BoundedPerfectNumber` is a strong new candidate.  It keeps the divisor-sum
  loop from TheAlgorithms, generates `32` executable testcases, and has a clean
  one-to-one Refined TBFV result: `32` passed and `0` failed.
- `BoundedPronicNumber` is another strong TheAlgorithms candidate.  It generates
  `33` executable testcases and has a clean `33` passed, `0` failed TBFV result.
- `BoundedAbundantNumber` completes the same number-theory predicate family:
  `30` executable testcases, `30` TBFV passes, and `0` failures.
- `BoundedGCD` is not suitable as a main subject in its current form.  The
  Euclidean loop is real and scalar-only, but batch CSC produced only `11`
  executable testcases and the gcd-result FSF yielded `54` passed matches.
- `BoundedFloorSqrt` revisits the earlier square-root candidate with a more
  precise non-overlapping mathematical FSF.  It still produces more passed FSF
  matches than executable testcases (`46` vs. `33`), which suggests the generated
  CCT path constraints remain too broad for interval-style square-root
  specifications.
- `BoundedAutomorphicNumber` is semantically clean and repository-derived, but
  it produces only `7` executable testcases because the loop mainly exposes
  digit-count structure rather than many independent branch choices.
- `BoundedAliquotClassifier` is a strong new candidate.  It keeps the
  proper-divisor accumulation behavior from TheAlgorithms and classifies each
  accepted input as deficient, perfect, or abundant.  CSC produced `52`
  executable testcases and Refined TBFV passed exactly `52` with no failures.
- `BoundedPrimeClassifier` initially used an early-return trial-division
  structure and produced only `12` executable testcases.  Rewriting it as a
  bounded divisor-count loop and limiting the input to `2..50` produced `51`
  executable testcases with `51` TBFV passes and zero failures.
- `BoundedHarshadNumber` is a useful negative example.  It is semantically clean
  and repository-derived, but the digit-sum loop has no branch-visible update,
  so CSC produced only `6` executable testcases.
- `BoundedEvilNumber` is a strong bit/counting candidate.  Replacing bit shifts
  with division/modulo and making the one-bit update explicit produced `103`
  executable testcases with exact one-to-one TBFV matching.
- `BoundedRightmostSetBit` has a clean FSF and real source provenance, but its
  path structure is essentially just the number of trailing zero bits, giving
  only `10` executable testcases under the current range.
- `BoundedKrishnamurthyNumber` is a strong multi-loop candidate.  Replacing the
  repository's precomputed factorial array with a small bounded factorial loop
  produced `173` executable testcases, exact one-to-one TBFV matching, and zero
  failures.

## Next Collection Guidance

- Keep `BoundedIntPower` as an example of successful arithmetic-loop extraction.
- Keep `SaturatedIntPower` as the preferred template for repository-derived
  scalar loop subjects: bounded inputs, one deterministic loop, post-loop
  decision region, and FSF units aligned with final semantic outcomes.
- For future real-source candidates, prefer methods that naturally expose at
  least 20 executable testcases under batch `max-iter=50`.
- Treat range-product/factorial rewrites carefully: they may be mathematically
  clean but can collapse many concrete source scenarios into a small number of
  CCT path shapes.
- TheAlgorithms is more productive than general application repositories for
  the current tool constraints.  It contains many scalar-only loop kernels, but
  each candidate still needs dynamic filtering because broad FSF intervals can
  inflate TBFV pass counts.
- Prefer TheAlgorithms-style predicates with compact semantic classes, such as
  perfect/non-perfect, when the class boundary is easy to express in FSF and
  the loop still yields enough distinct CSC paths.
- Keep `BoundedPerfectNumber`, `BoundedPronicNumber`, and
  `BoundedAbundantNumber` together as a coherent real-source number-theory
  predicate group.  They are similar enough to explain, but their loop
  predicates and mutant opportunities differ.
- Avoid using Euclidean GCD as a main subject unless the program is redesigned
  to expose more executable cases and a cleaner FSF/testcase relationship.
- Square-root or binary-search kernels need special care: even mathematically
  disjoint interval FSF units can overlap at the symbolic-path level.
- Digit-conversion and suffix-property kernels often look attractive but may
  produce too few branch-distinct executable testcases unless the loop body has
  a meaningful conditional update.
- A loop body with an explicit conditional update is a strong signal.  `Evil`
  style bit counting worked much better than `Harshad` style unconditional digit
  summation.
- Path-class cardinality matters: even a clean loop such as rightmost-set-bit can
  be too small if the number of possible loop outcomes is bounded to a handful
  of semantic classes.
- Nested loops should not be rejected automatically.  They are suitable when the
  inner loop has a very small fixed semantic bound, as in digit factorial
  computation.
- Divisor-count/divisor-sum classifiers remain the most productive real-source
  pattern under the current no-array constraint, especially when the final
  semantic class has compact enumerable boundaries.
- Avoid optimizations that collapse several source-level scenarios into one
  symbolic path unless the FSF is intentionally written at that coarser level.
- Continue searching for scalar loop kernels in arithmetic, scoring, pricing,
  quota, and bounded resource-consumption code.
