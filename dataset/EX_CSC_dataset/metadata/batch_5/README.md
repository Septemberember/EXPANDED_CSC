# EX_CSC_dataset

`EX_CSC_dataset` is a repository-derived original-program dataset built from local
open-source Java candidates.

The subjects follow the current CSC constraints:

- scalar integer inputs and return values;
- no arrays, objects, strings, recursion, collections, floating point, or helper
  calls in the final subject;
- at least one bounded loop;
- compact, mutually exclusive FSF classes;
- batch CSC can finish under `max-iter=50`;
- Refined TBFV passes with `0` failed cases against the bound FSF.

This directory currently contains original subjects only.  Mutants have not yet
been generated.

## Validation Settings

- CSC command: `csc_tool.py`
- Strategy: `batch`
- Workers: `4`
- Max iterations: `50`
- TBFV command: `refined_tbfv_tool.py`
- Validation sessions:
  - `csc_tmp/ex_csc_dataset_final_candidate_validation`
  - `csc_tmp/ex_csc_dataset_final_candidate_validation_v2`
  - `csc_tmp/ex_csc_dataset_final_candidate_validation_v3`

## Selected Subjects

| Subject | Source family | Loop role | CSC executable | TBFV passed | TBFV failed | Decision |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `BoundedAliquotClassifier` | TheAlgorithms divisor-sum utilities | proper-divisor classification | 52 | 52 | 0 | kept |
| `BoundedBinaryPalindromeClassifier` | TheAlgorithms bit/palindrome utilities | fixed-width bit comparison | 66 | 66 | 0 | kept |
| `BoundedBitTransitionClassifier` | TheAlgorithms bit-counting utilities | fixed-width bit transition counting | 66 | 66 | 0 | kept |
| `BoundedDivisorCountClassifier` | TheAlgorithms divisor/prime utilities | divisor-count classification | 52 | 52 | 0 | kept |
| `BoundedPerfectSquareLoop` | TheAlgorithms perfect-square utilities | bounded square search | 103 | 103 | 0 | kept |
| `BoundedPopcountDensity` | TheAlgorithms bit-counting utilities | popcount density classification | 130 | 130 | 0 | kept |
| `BoundedProperDivisorParity` | TheAlgorithms proper-divisor utilities | proper-divisor sum parity | 52 | 52 | 0 | kept |
| `BoundedSquareFreeClassifier` | TheAlgorithms square-free integer | square-divisor classification | 40 | 40 | 0 | kept |

## Rejected During Construction

The following candidates were generated or considered but not retained:

- Large enumerated sequence FSFs such as Lucas, Leonardo, Tribonacci, Climbing
  Stairs, Padovan, Perrin, and Jacobsthal: CSC was fast, but TBFV became too
  expensive because each index required a separate FSF unit.
- `BoundedAdditivePersistence`: clean but too few executable testcases.
- `BoundedMultiplicativePersistence`: clean but too few executable testcases.
- `BoundedGermainPrimeClassifier`: did not produce a usable TBFV input shape in
  the attempted version.
- `BoundedSafePrimeClassifier`: CSC exceeded the 3-minute budget.
- `BoundedHappyNumberClassifier`: CSC exceeded the 3-minute budget.

## Next Step

If this dataset is promoted for fault-localization experiments, generate six
single-fault mutants per subject:

- three condition/control-flow mutants;
- three statement/data-flow mutants;
- canonical `mutants_manifest.jsonl` with ground-truth line metadata.
