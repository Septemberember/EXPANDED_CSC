# CSC Engine and Experimental Artifact

This repository contains the implementation and reproducibility materials for
the Condition Sequence Coverage (CSC) engine, the expanded CSC variant, and the
CCT-based fault localization experiments used in the accompanying JSS
submission.

The repository is organized as a public artifact rather than as a polished
application package. Most top-level scripts correspond to one experiment,
analysis pass, or reporting step used in the paper.

## Repository Map

### Core CSC Implementation

- `csc_engine/`: main Python package.
  - `cct.py`: Condition Case Tree data structures, CSC traversal, persistence,
    and DOT visualization.
  - `csc.py`: high-level CSC generation workflow.
  - `execution_trace.py`: parser for Java execution traces produced by the
    instrumentation bridge.
  - `z3_helpers.py`: Java-like expression translation and Z3 solving helpers.
  - `java_exec.py`: Java compilation and execution utilities.
  - `refined_tbfv.py`: refined TBFV pass/fail oracle logic.
  - `failure_localization*.py`: CCT-based fault localization, aggregation,
    evaluation, folding, and report generation.
  - `subject_experiment.py`: subject-level orchestration.
  - `parallel_generation_experiment.py`: shared support for parallel CSC
    generation experiments.
- `java_bridge/`: Java instrumentation bridge.
  - `pom.xml`: Maven build file.
  - `src/main/java/csc/bridge/Instrumenter.java`: inserts trace-printing
    statements into Java subjects.
  - `src/main/java/csc/bridge/CSCTrace.java`: runtime trace helpers.
- `csc_tool.py`: all-in-one command-line entry point for a Java file.

### Datasets and Benchmarks

- `dataset/EX_CSC_dataset/`: the unified public EX_CSC dataset. Subject
  directories live directly under this root, together with public Java subjects,
  mutants, FSF files, provenance notes, validation reports, and one merged
  `mutants_manifest.jsonl`.
- `dataset/EX_CSC_BOUNDARY_STRESS/`: boundary-sensitive subjects and mutants
  used for the boundary stress follow-up experiments.
- `dataset/EX_CSC_REAL_CANDIDATES/`: curated candidate subjects retained to
  document how later EX_CSC subjects were selected.
- `dataset/RQ1_SCREENING_FAILURES/`: small excluded examples used to document
  RQ1 screening and boundary-completion failure cases.
- `dataset/CSC_V2_dataset/`: earlier dataset and candidate subjects retained
  for traceability.
- `dataset/Readme.md` and `dataset/FSF_Generation_Guide.md`: dataset-level
  documentation.

Generated runtime directories such as `dataset/runnable/` and
`dataset/instrumented/` are excluded from the public repository. They are
recreated by the scripts when needed.

### Experiment Scripts

The top-level scripts are grouped by purpose:

- Core generation and subject execution:
  - `run_subject_experiment.py`
  - `run_parallel_generation_experiment.py`
  - `rq2_parallel_experiment.py`
  - `summarize_parallel_generation_experiment.py`
  - `build_rq2_fingerprint_validation.py`
- Fault-localization pipeline:
  - `run_fault_localization_experiment.py`
  - `evaluate_fault_localization.py`
  - `validate_fault_localization_dataset.py`
  - `summarize_fault_localization_results.py`
  - `failure_localization_tool.py`
  - `failure_localization_aggregate_tool.py`
  - `aggregate_fault_localization_experiment_rows.py`
- Fault-localization analysis and replay:
  - `replay_fault_localization_strategy.py`
  - `replay_fault_localization_folded.py`
  - `folded_composite_budget_compare_sfl.py`
  - `folded_composite_multi_sfl_budget_compare.py`
  - `unified_folded_budget_compare_sfl.py`
  - `analyze_budget_matched_fl.py`
  - `analyze_fl_poor_rank_tasks.py`
  - `compare_aggregation_strategies.py`
  - `compare_max_vs_sum_aggregation.py`
- Paper table construction:
  - `build_rq3_paper_tables_dataset.py`
  - `build_ex_csc_dataset_pooled_tables.py`
- RQ1 support:
  - `rq1_experiment/`

### Baselines

- `baseline/SFL/`: spectrum-based fault localization implementation.
- `baseline/run_sfl_baseline_experiment.py`: dataset-level SFL baseline runner.

### Results and Reports

- `experiments/`: lightweight experiment outputs kept for reproducibility:
  configurations, summaries, CSV/JSONL result tables, and selected reports.
- `FAULT_LOCALIZATION_EXPERIMENT_KIT_GUIDE.html` and `USAGE_GUIDE.html`:
  rendered usage guides kept from the working artifact.

Large per-run traces, compiled classes, `csc_tmp/`, Maven targets, Python
caches, and archived artifacts are intentionally excluded.

### Tests and Examples

- `tests/`: unit tests for CCT construction, CSC behavior, Java trace parsing,
  refined TBFV, failure localization, dataset validation, and experiment
  helpers.
- `examples/basic_usage.py`: a small Python-only CSC example.
- `dataset/EX_CSC_dataset/MaxOfFive/MaxOfFive.java`: small Java subject that
  works well as an all-in-one CSC smoke test.

## Requirements

- Python 3.10 or newer
- Java 16 or newer for Java subject instrumentation and execution
- Maven for building `java_bridge/`
- Graphviz is optional, but enables PNG rendering from DOT CCT files

Install the Python package in editable mode:

```bash
python3 -m pip install -e ".[dev]"
```

Build the optional Java bridge:

```bash
cd java_bridge
mvn clean package
cd ..
```

Run the test suite:

```bash
python3 -m pytest
```

## Example 1: Python-Only CSC Walkthrough

This example does not require Java or Maven. It manually constructs two
execution paths for a simple largest-proper-divisor style program, inserts them
into a CCT, asks CSC for the next uncovered branch, solves the path constraint
with Z3, and writes a DOT visualization.

Run:

```bash
python3 examples/basic_usage.py
```

What it demonstrates:

- Creating a `CCT(use_bounded_range=True, range_bound=200)`.
- Adding observed condition-result sequences with `add_sequence`.
- Calling `check_for_csc` to find an uncovered branch.
- Constructing and solving the resulting path constraint.
- Comparing original CSC and expanded CSC behavior.
- Emitting `example_cct.dot`, plus `example_cct.png` when Graphviz is installed.

The example is a compact starting point if you want to understand the core data
structures before running the larger Java-based artifact.

## Example 2: Run CSC on a Java Program

Build the Java bridge first:

```bash
cd java_bridge
mvn clean package
cd ..
```

Then run a short all-in-one CSC workflow:

```bash
python3 csc_tool.py dataset/EX_CSC_dataset/MaxOfFive/MaxOfFive.java \
  --session readme_maxofive_smoke \
  --max-iter 5
```

This command instruments the Java file, compiles the instrumented program,
executes generated test inputs, parses the printed traces, updates the CCT, and
stops after at most five CSC iterations. In a working environment, it should
write generated tests to
`csc_tmp/readme_maxofive_smoke/MaxOfFive/testcases.json`.

Runtime files are written under ignored working directories such as `csc_tmp/`
and `dataset/runnable/`.

## Example 3: Dataset-Level Fault Localization

The portable experiment wrapper expects a dataset with this shape:

```text
DATASET_ROOT/
  mutants_manifest.jsonl
  SubjectName/
    SubjectName.java
    SubjectName_M1.java
    ...
    FSF/
      SubjectName_FSF.txt
```

For a quick smoke test, run one subject and one mutant:

```bash
python3 run_fault_localization_experiment.py \
  --dataset-root dataset/EX_CSC_dataset \
  --experiment-root tmp_readme_fl_smoke \
  --session-prefix readme_fl_smoke \
  --mode expanded \
  --range-bound 200 \
  --strategy batch \
  --workers 1 \
  --max-iter 5 \
  --subjects MaxOfFive \
  --mutants MaxOfFive_M1 \
  --run-sfl-baseline
```

For a full expanded-CSC fault-localization run over the unified EX_CSC dataset,
use:

```bash
python3 run_fault_localization_experiment.py \
  --dataset-root dataset/EX_CSC_dataset \
  --experiment-root experiments/FL-EX_CSC_dataset \
  --session-prefix fl_ex_csc_dataset \
  --mode expanded \
  --range-bound 200 \
  --strategy batch \
  --workers 4 \
  --max-iter 100 \
  --run-sfl-baseline
```

Important outputs include:

- `experiment_config.json`
- `dataset_validation.json` and `dataset_validation.md`
- `subject_run_records.jsonl`
- `fault_localization_rows.csv`
- `fault_localization_rows.jsonl`
- `fault_localization_summary.md`
- `baseline-SFL/`, when `--run-sfl-baseline` is enabled

See `fault_localization_experiment_kit/README.md` for detailed options and
output schema.

## Reproducing Paper Tables

The `experiments/` directory already includes compact result tables and
summaries used during paper preparation. They are organized under one unified
experiment root:

- Final compact paper tables:
  `experiments/EX_CSC_dataset/paper_tables/`
- RQ1 bounded-completion summaries:
  `experiments/EX_CSC_dataset/rq1_bounded_completion/`
- RQ2 parallel generation summaries:
  `experiments/EX_CSC_dataset/rq2_parallel_generation/`
- Additional unified-dataset RQ summaries:
  `experiments/EX_CSC_dataset/rq_extension_a/`,
  `experiments/EX_CSC_dataset/rq_extension_b/`, and
  `experiments/EX_CSC_dataset/boundary_stress_subjects/`
- Boundary stress and mutant-killing summaries:
  `experiments/EX_CSC_dataset/boundary_kill_core/`,
  `experiments/EX_CSC_dataset/boundary_stress/`, and
  `experiments/EX_CSC_dataset/boundary_kill_with_boundary_stress/`
- Fault-localization summaries:
  `experiments/EX_CSC_dataset/fault_localization_core_a/`,
  `experiments/EX_CSC_dataset/fault_localization_core_b/`, and
  `experiments/EX_CSC_dataset/fault_localization_combined/`
- Budget-matched and folded analyses:
  `experiments/EX_CSC_dataset/folded_fault_localization/` and the
  `budget_matched_analysis/` subdirectories under
  `experiments/EX_CSC_dataset/fault_localization_combined/`

The analysis scripts listed above can regenerate or inspect these summaries
from the CSV/JSONL files. New reproductions should use
`dataset/EX_CSC_dataset` as the dataset root and place outputs under
`experiments/EX_CSC_dataset/` or a temporary directory.

## Reproducibility Notes

The public artifact keeps source code, datasets, experiment configurations, and
result summaries. It intentionally excludes generated runtime directories such
as `csc_tmp/`, `dataset/runnable/`, Maven targets, Python caches, compiled Java
classes, and large per-mutant trace archives. These files are regenerated by the
scripts above.

No license has been added yet. Add one before making the repository public if
you want to grant reuse rights beyond viewing the artifact.
