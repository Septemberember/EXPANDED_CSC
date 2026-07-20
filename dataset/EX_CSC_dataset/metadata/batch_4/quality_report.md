# EX_CSC_dataset Quality Report

Generated on 2026-07-04.

## Scope

This report validates the original programs and their bound FSF files after
promotion from `EX_CSC_REAL_CANDIDATES` into `EX_CSC_dataset`.

## Settings

- CSC strategy: `batch`
- CSC workers: `4`
- CSC max iteration budget: `50`
- Refined TBFV: original subject with bound FSF
- Result directories:
  - `project/CSC_EXPANDED/csc_tmp/ex_csc_dataset_expanded_bounds_final`
  - `project/CSC_EXPANDED/csc_tmp/ex_csc_dataset_8_subject_validation`

## Original Validation Summary

| Subject | LOC family | CSC executable | FSF units | TBFV passed | TBFV failed | Skipped | Unsupported | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `BoundedIntPower` | scalar arithmetic loop | 30 | 19 | 30 | 0 | 540 | 0 | accepted |
| `SaturatedIntPower` | scalar arithmetic loop | 38 | 33 | 38 | 0 | 1216 | 0 | accepted |
| `BoundedPerfectNumber` | number-theory predicate loop | 52 | 3 | 52 | 0 | 104 | 0 | accepted |
| `BoundedPronicNumber` | number-theory predicate loop | 53 | 3 | 53 | 0 | 106 | 0 | accepted |
| `BoundedAbundantNumber` | number-theory predicate loop | 50 | 3 | 50 | 0 | 100 | 0 | accepted |
| `BoundedPrimeClassifier` | divisor-count classifier loop | 51 | 3 | 51 | 0 | 102 | 0 | accepted |
| `BoundedEvilNumber` | bit-count classifier loop | 103 | 3 | 103 | 0 | 206 | 0 | accepted |
| `BoundedKrishnamurthyNumber` | digit-factorial nested loop | 173 | 3 | 173 | 0 | 346 | 0 | accepted |

## Selection Rationale

These eight subjects satisfy the current main-dataset threshold:

- each subject contains a bounded loop;
- each subject avoids arrays and object-heavy constructs unsupported by the
  current tool chain;
- each subject produces at least `30` executable testcases under batch
  `max-iter=50`;
- each subject has a clean `passed == executable` relationship in Refined TBFV;
- each subject has `0` TBFV failures on the original program.

The `passed == executable` relationship is especially useful here: it indicates
that each executable testcase is covered by exactly one effective FSF scenario,
so later mutant failures can be interpreted without excessive TD/FSF overlap.

## Current Dataset Status

`EX_CSC_dataset` is ready as an original-program dataset.  It is not yet a full fault
localization dataset because no mutants have been generated in this directory.
The next formal step is to create condition and statement mutants and write a
canonical `mutants_manifest.jsonl`.

## Bound Expansion Note

The original candidate version used narrower input bounds.  The promoted
version expands those bounds while preserving `0` TBFV failures:

- `BoundedIntPower`: `base` expanded to `[-5, 5]`, `exponent` to `[0, 8]`.
- `SaturatedIntPower`: `base` expanded to `[-5, 5]`, `exponent` to `[0, 7]`.
- `BoundedPerfectNumber`: `number` expanded to `[1, 50]`.
- `BoundedPronicNumber`: `number` expanded to `[0, 50]`.
- `BoundedAbundantNumber`: `number` expanded to `[1, 50]`.

## Promotion Note

Three additional repository-derived candidates were promoted after dynamic
validation:

- `BoundedPrimeClassifier`: selected as a divisor-count classifier that differs
  from the existing divisor-sum subjects.
- `BoundedEvilNumber`: selected as a bit-count classifier with a branch-visible
  loop update and high testcase yield.
- `BoundedKrishnamurthyNumber`: selected as a compact nested-loop subject; its
  inner factorial loop is small and bounded by one decimal digit.

`BoundedAliquotClassifier` was also strong, but it was not promoted because
`EX_CSC_dataset` needed exactly three additional subjects and already included several
divisor-sum style programs.
