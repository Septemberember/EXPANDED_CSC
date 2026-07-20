# EX_CSC_dataset

`EX_CSC_dataset` is a repository-derived original-program dataset selected from
`EX_CSC_REAL_CANDIDATES`.

The subjects in this directory are adapted from real Java algorithm/library
kernels under the current CSC constraints:

- scalar integer inputs and return values;
- no arrays, objects, recursion, collections, or library helper calls;
- at least one bounded loop;
- enough branches to create non-trivial CCT structure;
- batch CSC can finish under `max-iter=50`;
- Refined TBFV passes with `0` failed cases against the bound FSF.

This directory contains validated original subjects and a prepared mutant
manifest.  Experiment-stage validation of mutants has not been run yet.

## Validation Settings

- CSC command: `csc_tool.py`
- Strategy: `batch`
- Workers: `4`
- Max iterations: `50`
- TBFV command: `refined_tbfv_tool.py`
- Validation session: `csc_tmp/ex_csc_dataset_expanded_bounds_final` for the original
  five subjects; `csc_tmp/ex_csc_dataset_8_subject_validation` for the three promoted
  subjects added later.

## Selected Subjects

| Subject | Source family | Loop role | CSC executable | TBFV passed | TBFV failed | Decision |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `BoundedIntPower` | Guava / Commons integer power | repeated multiplication | 30 | 30 | 0 | kept |
| `SaturatedIntPower` | Guava saturated power | repeated multiplication plus cap | 38 | 38 | 0 | kept |
| `BoundedPerfectNumber` | TheAlgorithms perfect number | divisor accumulation | 52 | 52 | 0 | kept |
| `BoundedPronicNumber` | TheAlgorithms pronic number | bounded factor search | 53 | 53 | 0 | kept |
| `BoundedAbundantNumber` | TheAlgorithms abundant number | divisor accumulation | 50 | 50 | 0 | kept |
| `BoundedPrimeClassifier` | TheAlgorithms prime check | divisor-count classification | 51 | 51 | 0 | kept |
| `BoundedEvilNumber` | TheAlgorithms evil number | bit-count classification | 103 | 103 | 0 | kept |
| `BoundedKrishnamurthyNumber` | TheAlgorithms Krishnamurthy number | digit-factorial nested loop | 173 | 173 | 0 | kept |

## Excluded Candidates

The following candidates were not promoted into `EX_CSC_dataset`:

- `BoundedBinomial`: correct but too small for the main benchmark
  (`10` executable testcases).
- `BoundedSqrtBinarySearch`: zero TBFV failures, but some generated testcases
  match multiple broad FSF regions (`27` executable, `37` passed).
- `BoundedProductRange`: FSF/testcase relationship is not clean enough
  (`15` executable, `34` passed).
- `BoundedGCD`: too few executable testcases and too much FSF overlap
  (`11` executable, `54` passed).
- `BoundedAliquotClassifier`: strong candidate but not promoted because
  `EX_CSC_dataset` needed exactly three additional subjects and divisor-sum behavior
  was already represented by perfect/abundant subjects.
- `BoundedFloorSqrt`: interval FSF still overlaps generated symbolic paths
  (`33` executable, `46` passed).
- `BoundedAutomorphicNumber`: clean but too small (`7` executable).
- `BoundedHarshadNumber`: clean but too small (`6` executable).
- `BoundedRightmostSetBit`: clean but too few path classes (`10` executable).

## Next Step

For fault localization experiments, run a controlled mutant validation pass:

- process each mutant with the CSC/TBFV toolchain;
- update or report compile/instrumentation/TBFV status;
- retain the generated failure reports for localization;
- then run CCT-based localization and evaluation against
  `mutants_manifest.jsonl`.
