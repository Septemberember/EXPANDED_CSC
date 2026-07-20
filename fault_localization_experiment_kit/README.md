# Fault Localization Experiment Kit

This kit provides a portable dataset-level wrapper for the existing CSC,
Refined TBFV, CCT-based failure localization, aggregation, and evaluation
pipeline.

The wrapper does not change the existing algorithms or report schemas. It only
coordinates validation, subject-level runs, summary generation, and artifact
archiving.

## Required Input

```text
DATASET_ROOT/
  mutants_manifest.jsonl
  quality_report.md              # optional, copied into the experiment snapshot
  SubjectName/
    SubjectName.java
    SubjectName_M1.java
    SubjectName_M2.java
    ...
    FSF/
      SubjectName_FSF.txt
```

The manifest must use the same JSONL schema already consumed by
`evaluate_fault_localization.py` and
`validate_fault_localization_dataset.py`.

## Main Command

Run from the `CSC_EXPANDED` project directory:

```bash
python run_fault_localization_experiment.py \
  --dataset-root dataset/EX_CSC_dataset \
  --experiment-root experiments/FL-EX_CSC_dataset \
  --session-prefix fl_ex_csc_dataset \
  --mode expanded \
  --range-bound 200 \
  --strategy batch \
  --workers 4 \
  --max-iter 100
```

By default, the dataset-level runner runs mutants only. Use
`--include-original` only when the original programs should also be executed.

## Optional SFL Baseline

Add `--run-sfl-baseline` when the experiment should also compute the line-level
SFL baseline over the same generated traces and Refined TBFV pass/fail labels:

```bash
python run_fault_localization_experiment.py \
  --dataset-root dataset/EX_CSC_dataset \
  --experiment-root experiments/FL-EX_CSC_dataset-sfl \
  --session-prefix fl_ex_csc_dataset_sfl \
  --mode expanded \
  --range-bound 200 \
  --strategy batch \
  --workers 4 \
  --max-iter 100 \
  --run-sfl-baseline
```

The SFL stage runs after CCT localization and artifact archiving. It is optional
because it is a baseline analysis, not part of the CCT localization algorithm.
By default SFL rankings are recomputed from the archived traces to avoid stale
or top-k-truncated reports. Pass `--reuse-existing-sfl` only when reusing old
per-mutant `sfl_localization.json` files is intentional. The runner first looks
for the bundled baseline at `CSC_EXPANDED/baseline/run_sfl_baseline_experiment.py`,
then falls back to the older source-checkout layout at `CSC_EXT/baseline/`.

## Output

```text
EXPERIMENT_ROOT/
  experiment_config.json
  experiment_run_summary.json
  dataset_validation.json
  dataset_validation.md
  subject_run_records.jsonl
  subject_logs/
  subject_summaries/
  fault_localization_rows.jsonl
  fault_localization_rows.csv
  fault_localization_summary.md
  baseline-SFL/                    # only when --run-sfl-baseline is used
    sfl_fault_localization_rows.jsonl
    sfl_fault_localization_rows.csv
    sfl_fault_localization_summary.md
  artifacts/
    csc_tmp/
  dataset_snapshot/
```

These files intentionally match the current manual workflow outputs.

## Post-Experiment Reporting Check

After each run, `fault_localization_summary.md` should report both the overall
category-agnostic result and fault-category results:

- overall CCT localization, using the composite workflow plus the official
  condition-node and edge-divergence-gated interval strategies;
- condition/control-flow mutants, where condition-node ranking is the main
  explanatory CCT view;
- statement/data-flow mutants, where edge-divergence-gated interval ranking is
  the main explanatory CCT view.

This split is required because the two CCT views target different fault
mechanisms. If the summary only contains the overall table, keep the generated
artifacts but regenerate the report from `fault_localization_rows.jsonl` or
`fault_localization_rows.csv`; rerunning CSC/TBFV is unnecessary.

## Useful Options

```bash
python run_fault_localization_experiment.py --check-env
python run_fault_localization_experiment.py --build-java-bridge
python run_fault_localization_experiment.py ... --subjects AddLoop,ScoreNormalizer
python run_fault_localization_experiment.py ... --mutants AddLoop_M1,AddLoop_M2
python run_fault_localization_experiment.py ... --run-sfl-baseline
python run_fault_localization_experiment.py ... --resume
python run_fault_localization_experiment.py ... --dry-run
```

## Portability Notes

Move or clone the whole `CSC_EXPANDED` project directory to another machine,
including its bundled `baseline/` directory, install the Python requirements,
build the Java bridge if needed, and then run the command above. The wrapper
uses Python `pathlib` and `shutil` for path handling and artifact copying, so it
avoids shell-specific commands.
