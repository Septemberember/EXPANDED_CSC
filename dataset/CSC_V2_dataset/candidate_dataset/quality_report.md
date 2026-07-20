# Candidate Dataset Quality Report

This report summarizes the current completeness checks for the candidate
dataset.

## Current Scope

Main candidate subjects:

- `ShippingCost`
- `DiscountCalculator`
- `ParkingFee`
- `LoanRisk`
- `LoopBubbleSortFive`
- `OddEvenSortFive`
- `LoopSelectionSortFive`

Main original programs:

- 7

Mutants:

- 12

Canonical manifest:

- `../mutants_manifest.jsonl`

Subject FSF directory:

- `fsf_dir/`

## Added Supporting Files

Each subject now has:

- an original Java source,
- a subject-local `README.md`,
- a bound FSF in `candidate_dataset/fsf_dir`.

The first four main candidates also have three single-fault mutant sources each.
The loop-sorting candidates were added as original+FSF subjects first; mutants
should be generated after selecting the preferred operators for loop-aware
sorting faults.

The FSF files follow `dataset/FSF_Generation_Guide.md`:

- section ids use `[fsf_i]` numbering,
- `T` classifies inputs,
- `D` defines expected output through `return_value`,
- invalid-input scenarios are partitioned to avoid overlap,
- legal scenarios include formula-style regions where simple, plus bounded
  bug-revealing or business-critical inputs where the full formula would be too
  cumbersome for the current lightweight FSF tooling.

FSF files:

- `fsf_dir/ShippingCost_FSF.txt`
- `fsf_dir/DiscountCalculator_FSF.txt`
- `fsf_dir/ParkingFee_FSF.txt`
- `fsf_dir/LoanRisk_FSF.txt`
- `fsf_dir/LoopBubbleSortFive_FSF.txt`
- `fsf_dir/OddEvenSortFive_FSF.txt`
- `fsf_dir/LoopSelectionSortFive_FSF.txt`
- `fsf_dir/ApplianceWarranty_FSF.txt`
- `fsf_dir/CoursePlacement_FSF.txt`

## Original TBFV Checks

Each original was checked with a legal bootstrap input and refined TBFV:

| Subject | Bootstrap | TBFV result |
| --- | --- | --- |
| `ShippingCost` | `weight=3,distance=250,express=true` | pass |
| `DiscountCalculator` | `price=500,customerYears=12,coupon=true` | pass |
| `ParkingFee` | `hours=8,entryHour=19,weekend=true` | pass |
| `LoanRisk` | `income=120,debt=130,stableJob=true` | pass |
| `LoopBubbleSortFive` | `a=5,b=1,c=4,d=2,e=3` | pass |
| `OddEvenSortFive` | `a=5,b=1,c=4,d=2,e=3` | pass |
| `LoopSelectionSortFive` | `a=5,b=1,c=4,d=2,e=3` | pass |
| `ApplianceWarranty` | batch-50 generated 724 executable testcases | pass: 15 passed, 0 failed, 0 unsupported |
| `CoursePlacement` | batch-50 generated 630 executable testcases | pass: 19 passed, 0 failed, 0 unsupported |

For subjects that already have mutants, the original TBFV checks are reflected
in `mutants_manifest.jsonl` through `validation.original_tbfv_passed=true`.
For original-only main subjects, checks are recorded in this report until
mutants are generated and added to the manifest.

## Loop-Sorting Subjects

Three BubbleSort-like subjects were added as main candidates with controlled
loops:

- `LoopBubbleSortFive`: four-pass adjacent compare-swap loop.
- `OddEvenSortFive`: five-round odd-even compare-swap loop.
- `LoopSelectionSortFive`: four-position scalar selection-sort loop.

These subjects preserve the useful properties of `BubbleSortFive`: fixed scalar
inputs, clear compare-swap regions, boolean sortedness output, and good
condition-to-statement locality. Unlike `BubbleSortFive`, they include bounded
loops, making them better candidates for evaluating loop-aware CSC and
fault-localization behavior without turning the experiment into a path-explosion
case.

## Larger Controlled-Frontier Subjects

Two larger original-only candidates were added after calibrating the 3-minute
batch-50 admission rule:

- `ApplianceWarranty`: 101 source lines, about 16 condition sites, 724
  executable CSC records, original TBFV passed.
- `CoursePlacement`: 99 source lines, about 16 condition sites, 630 executable
  CSC records, original TBFV passed.

Earlier 120-140 line drafts with roughly 30 condition sites exceeded the
3-minute CSC budget. The retained versions keep a larger source-line space for
fault-localization ranking, but use fewer independent branches and more straight
line state updates to avoid frontier explosion.

## Manifest Checks

The canonical manifest records, for each mutant:

- original file,
- mutant file,
- operator,
- fault kind,
- original line and source text,
- mutant line and source text,
- ground-truth primary line,
- acceptable line window,
- bound FSF,
- validation status.

The manifest line/code pairs were checked against the current Java source files.

## Remaining Work Before Final Benchmark Use

The current candidate dataset is ready for further mutant-level TBFV and fault
localization experiments, but it is not yet a final benchmark. Before using it
for final tables, run and record:

- mutant TBFV failure status,
- failed FSF ids,
- fault localization outputs,
- `fault_localization_eval.jsonl` metrics for each strategy.
