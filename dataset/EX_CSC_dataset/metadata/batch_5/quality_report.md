# EX_CSC_dataset Quality Report

Generated on 2026-07-04.

## Scope

This report validates the original programs and their bound FSF files.

## Settings

- CSC strategy: `batch`
- CSC workers: `4`
- CSC max iteration budget: `50`
- Refined TBFV: original subject with bound FSF

## Original Validation Summary

| Subject | LOC | Conditions | Loops | CSC executable | FSF units | TBFV passed | TBFV failed | Skipped | Unsupported | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `BoundedAliquotClassifier` | 22 | 5 | 1 | 52 | 4 | 52 | 0 | 156 | 0 | accepted |
| `BoundedBinaryPalindromeClassifier` | 29 | 6 | 1 | 66 | 3 | 66 | 0 | 132 | 0 | accepted |
| `BoundedBitTransitionClassifier` | 27 | 5 | 1 | 66 | 4 | 66 | 0 | 198 | 0 | accepted |
| `BoundedDivisorCountClassifier` | 22 | 5 | 1 | 52 | 4 | 52 | 0 | 156 | 0 | accepted |
| `BoundedPerfectSquareLoop` | 15 | 3 | 1 | 103 | 3 | 103 | 0 | 206 | 0 | accepted |
| `BoundedPopcountDensity` | 22 | 5 | 1 | 130 | 4 | 130 | 0 | 390 | 0 | accepted |
| `BoundedProperDivisorParity` | 19 | 4 | 1 | 52 | 3 | 52 | 0 | 104 | 0 | accepted |
| `BoundedSquareFreeClassifier` | 19 | 4 | 1 | 40 | 3 | 40 | 0 | 80 | 0 | accepted |

## Selection Rationale

These subjects were retained because:

- each one has at least `40` executable testcases;
- each one has exact `passed == executable` Refined TBFV behavior;
- each one has `0` TBFV failures on the original program;
- FSF units are compact semantic classes rather than large per-index
  enumerations;
- each subject is adapted from an open-source Java algorithm family with
  documented provenance.

## Construction Lessons

- Large sequence-index FSFs are not suitable even when CSC generation is fast:
  they make TBFV too expensive.
- Early-return divisor loops often need to be rewritten as full bounded scans to
  expose useful path diversity.
- Fixed-width bit classifiers are productive because they provide several
  branch-visible loop iterations without arrays or helper calls.
- Divisor-loop upper bounds should be kept near `50` when the loop scans all
  divisors; larger bounds can exceed the batch budget.

## Current Dataset Status

`EX_CSC_dataset` is ready as an original-program dataset.  It is not yet a full fault
localization dataset because no mutants have been generated in this directory.
