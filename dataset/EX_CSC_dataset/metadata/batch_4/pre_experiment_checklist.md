# EX_CSC_dataset Pre-Experiment Checklist

Generated on 2026-07-04.

## Completed

- Original subjects promoted and validated: `8`.
- Bound FSF files present for every original subject.
- Provenance notes present for every original subject.
- Mutants generated: `48`.
- Mutants per subject: `6`.
- Condition/control-flow mutants: `24`.
- Statement/data-flow mutants: `24`.
- Canonical manifest written: `mutants_manifest.jsonl`.
- Static dataset validation passed:
  - `dataset_validation.json`
  - `dataset_validation.md`

## Mutant Policy

Each subject has:

- `M1`-`M3`: condition/control-flow mutants.
- `M4`-`M6`: statement/data-flow mutants.

Every mutant is a single-line, single-fault replacement.  The manifest records
the original line, mutant line, operator, fault category, bound FSF, and ground
truth localization target.

## Not Yet Performed

No experiment-stage execution has been performed after mutant generation.

The following manifest fields are intentionally left as `null` until the next
stage:

- `validation.compiles`
- `validation.instrumentable`
- `validation.csc_smoke_passed`
- `validation.legal_bootstrap_smoke_passed`
- `validation.mutant_tbfv_failed`

The following files should be generated only after the actual experiment runs:

- mutant CSC outputs;
- mutant Refined TBFV reports;
- failure-localization reports;
- `fault_localization_eval.jsonl`;
- final aggregated experiment tables.

## Next Step

Run a controlled mutant validation pass.  For each mutant, check whether it can
be processed by the toolchain and whether Refined TBFV produces failed cases
against the original FSF.
