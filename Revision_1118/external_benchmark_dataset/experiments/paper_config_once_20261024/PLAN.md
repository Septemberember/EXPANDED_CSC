# One-Run RQ1–RQ3 Experiment Plan for 20 External Programs

This file records the original experiment plan. Run each program once under
the selected CSC configuration. Retain all failures, errors, timeouts, and
budget exhaustion; do not repair subjects, tools, or FSFs or tune parameters
and retry. Environment differences do not block this experiment.

1. Freeze 20 original programs, FSFs, and source hashes. Copy them into this
   experiment's `dataset`, leaving the collected dataset unchanged. Check the
   manuscript protocol and execution settings; each configuration has one run.
2. RQ1 original programs: one fresh sequential pair per subject,
   original / expanded (`bound=200`), `R=2000`, for 40 runs. Record
   completion/partial/error status, leaf classifications, tree size, test count,
   generation time, and paired overhead.
3. RQ2: fresh batch expanded runs per subject, `bound=200`, `R=100`,
   `W=1/2/4/8`, once per configuration, for 80 runs. Execute configurations
   sequentially to avoid timing interference from program-level parallelism.
   Check three canonical output fingerprints and calculate valid paired
   speedups and frontier widths.
4. Prepare six predefined single-fault candidates per program: three condition
   faults and three statement faults, preferably at distinct locations. Use
   BOR/ROR/LOR/CR/AOR/SUR/RVR operators. Do not replace candidates based on
   detection or localization performance. Reuse the original FSF and record
   the unique edited token and ground-truth line. Skip compilation,
   instrumentation, or execution failures without replacement candidates.
5. RQ1 mutant detection: run each mutant in batch mode with `W=4`, `R=100`,
   original/expanded, and `bound=200`. Each mode generates its own test set;
   an FSF verification failure defines a kill. Aggregate loop-bearing mutants
   for the corresponding comparison; retain loop-free records separately.
6. RQ3: reuse the expanded mutants' CSC/TBFV execution evidence. Compare
   Fold-the-Tree `coverage_x_purity` with five SBFL formulas at Top-1/2/3
   using matched source-line inspection budgets. Only valid runs with failure
   evidence enter the localization denominator; record undetected and
   exceptional cases separately.
7. Produce a per-program ledger covering all three RQs, per-run JSONL,
   per-mutant detection/localization records, an exception ledger, and a report.
   Check completeness and explicit denominators. Unexecuted, timed-out, or
   partial runs must not be counted as undetected or localization misses.

Generation timeout is 240 seconds, following the existing RQ2 configuration;
each postprocessing step has a 180-second limit. On timeout, terminate the
process group, record status, and continue. Bootstrap uses the tool default,
as in the original experiment commands, rather than per-subject acceptance
settings. Preserve source input domains and existing guards, including their
intersection with `b=200`.

Protocol references at planning time: Baselines and Configurations / Execution
Protocol in `JSS2026/overleaf/main.tex`,
`CORE_rerun/experiment_config.json`, and
`rq_extension_b/RQ2-parallel/experiment_config.json`. Parsed settings and tool
hashes are recorded in `config.json`.

This independent external group does not modify the original 42-program data
or manuscript results. The newly constructed single-fault mutants need not
have the same difficulty distribution as the original 252 mutants.
