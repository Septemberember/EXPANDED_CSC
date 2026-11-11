# Supplementary Evaluation of 20 External Program Cores

Recorded original-program configurations: 120/120.
Recorded mutation candidates: 120/120. Per-program results for RQ1–RQ3 are recorded
in `subject_results.csv`. The experiment plan, configuration, and
individual execution commands are retained.

The detailed supplementary results are provided in this artifact and
the response letter. The manuscript provides a brief pointer to the
supplementary evaluation.

## RQ1: Exploration, Generation Cost, and Mutant Detection

Normally completed original-program pairs: 20/20.
Valid mutant pairs in the loop-bearing group: 84/84.
Mutants killed by both modes: 69; only by CSC+Boundary: 9;
only by CSC-only: 0; by neither: 6.

The following table includes normally completed original-program pairs.
Counts and generation times are averaged across programs within each
group. The mean time ratio is calculated by first dividing CSC+Boundary
generation time by CSC-only generation time for each program, then
averaging those ratios.

| Group | Program pairs | Tests: CSC-only / CSC+Boundary | Ancestor-stopped empty leaves: CSC-only / CSC+Boundary | CCT nodes: CSC-only / CSC+Boundary | Generation time (s): CSC-only / CSC+Boundary | Mean time ratio |
|---|---:|---:|---:|---:|---:|---:|
| loop-free | 6 | 27.17 / 27.17 | 0 / 0 | 340.67 / 340.67 | 10.00 / 10.12 | 0.99 |
| loop-bearing | 14 | 12.57 / 19.79 | 5.21 / 0 | 47.64 / 172.86 | 4.61 / 7.28 | 1.58 |

Verification time measures the complete refined-TBFV process,
including default report generation, for all collected paths of each
program. Mean verification times for sequential CSC-only and
CSC+Boundary are 1.077 and 1.072 seconds for the six loop-free programs,
and 0.189 and 0.322 seconds for the fourteen loop-bearing programs.
Across all 20 programs, the corresponding means are 0.455 and
0.547 seconds.

## RQ2: Worker Scaling

Programs with all three canonical final-output fingerprints agreeing
across the four worker settings: 20/20.

Each configuration was run once. The times are observed generation
costs on the recorded machine. Speedup is calculated for each program
relative to batch W=1; the table reports the mean and median of those
program-level ratios.

| Workers | Valid programs | Mean generation time (s) | Mean speedup | Median speedup |
|---:|---:|---:|---:|---:|
| 1 | 20 | 7.88 | 1.00 | 1.00 |
| 2 | 20 | 6.16 | 1.28 | 1.26 |
| 4 | 20 | 5.42 | 1.45 | 1.44 |
| 8 | 20 | 5.32 | 1.48 | 1.45 |

For batch W=4, mean verification time is 0.562 seconds across all
20 programs. Verification completed normally for every program under
both sequential configurations and batch W=4. These means use
`verification.wall_time_s` in `original_results.jsonl`, with equal
weight for each program.

## RQ3: Fault Localization

Localization statuses: {"evaluated": 107, "not_detected": 13}.
Hit rates use all 107 candidates with failure
evidence and a successfully completed localization process, including
ranking misses. Undetected candidates and exceptional outcomes are
recorded separately.

All values in the method columns are hit rates (%). At depth k,
Fold-the-Tree inspects the union of source lines in its first k condition
candidates and first k edge-partition candidates. Each of the five SBFL
formulas receives the same number of unique source lines for that
candidate and depth. The condition/state-update breakdown and actual
inspection budgets are recorded in `rq3_summary.csv`.

| Top-k | Evaluated candidates | Folded | Ochiai | DStar | Tarantula | Barinel | Op2 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 107 | 71.96 | 58.88 | 58.88 | 58.88 | 58.88 | 58.88 |
| 2 | 107 | 81.31 | 71.96 | 71.96 | 67.29 | 67.29 | 71.96 |
| 3 | 107 | 87.85 | 78.50 | 78.50 | 74.77 | 74.77 | 78.50 |

An undetected mutant has no failure detected by the generated tests
and FSF checks in this evaluation; this status does not establish
mutant equivalence.

### Paired Comparison with Op2

The following results use two-sided exact McNemar tests on the
107 evaluated mutants. Holm correction is applied jointly to the
three comparisons at Top-1, Top-2, and Top-3 against Op2.

| Top-k | Fold-the-Tree-only hits | Op2-only hits | Exact p | Holm-adjusted p |
|---:|---:|---:|---:|---:|
| 1 | 19 | 5 | 0.00661 | 0.01322 |
| 2 | 12 | 2 | 0.01294 | 0.01322 |
| 3 | 10 | 0 | 0.00195 | 0.00586 |

For discordant counts b and c, the exact p-value is
min(1, 2 × sum(comb(b+c, i), i=0,...,min(b,c)) / 2^(b+c)).
The paired hit indicators are recorded in `rq3_mutants.csv`.
All three adjusted p-values are below 0.05. Mutants from the same
program may share evidence, so these mutant-level tests are
interpreted as exploratory.

## Per-Program Completion Status

Detailed times, CCT sizes, test counts, mutant-detection results, and
localization denominators are recorded in `subject_results.csv`.

| Program | RQ1 completion | RQ1 valid mutant pairs | RQ2 completion | RQ3 evaluated / undetected / skipped |
|---|---|---:|---|---|
| SpfWbsStep | completed | 6/6 | completed | 5/1/0 |
| SpfFlapMotion | completed | 6/6 | completed | 6/0/0 |
| SpfBankWithdrawal | completed | 6/6 | completed | 3/3/0 |
| SpfDelimiterSearch | completed | 6/6 | completed | 6/0/0 |
| SpfSubstringCount | completed | 6/6 | completed | 6/0/0 |
| SpfSortedInsertion | completed | 6/6 | completed | 5/1/0 |
| SpfTreeSearch | completed | 6/6 | completed | 6/0/0 |
| SpfAbortDecision | completed | 6/6 | completed | 6/0/0 |
| SpfRjcCounter | completed | 6/6 | completed | 6/0/0 |
| SpfStackPops | completed | 6/6 | completed | 6/0/0 |
| SvMinePumpStep | completed | 6/6 | completed | 6/0/0 |
| SvTcasClimb | completed | 6/6 | completed | 3/3/0 |
| SvBellmanFord3 | completed | 6/6 | completed | 2/4/0 |
| SvTokenIdentifier | completed | 6/6 | completed | 5/1/0 |
| SvReplaceAtom | completed | 6/6 | completed | 6/0/0 |
| SvCliOption | completed | 6/6 | completed | 6/0/0 |
| D4jLevenshtein23 | completed | 6/6 | completed | 6/0/0 |
| D4jCharSqueeze | completed | 6/6 | completed | 6/0/0 |
| D4jArrayLastIndex | completed | 6/6 | completed | 6/0/0 |
| D4jMonotonicOrder | completed | 6/6 | completed | 6/0/0 |

The exception ledger, `exceptions.csv`, contains 0 entries. The
protocol excludes repair or parameter tuning followed by retries.
Budget exhaustion and timeouts do not count as normal completion.

Original-program configurations reporting an FSF failure: 0.
RQ1 completion denotes normal generation completion; FSF outcomes are
recorded separately in `rq1_completion.csv`. Mutant experiments proceed
only after the corresponding original program's batch-W4 FSF check
completes normally without failures.

## Evaluation Scope

The group comprises 20 controlled program cores, including methods
from shared upstream projects. Its newly constructed single-fault
mutants need not have the same difficulty distribution as the original
252 mutants. One run per configuration provides observed timing
results but does not estimate run-to-run variation.

## Supporting Records

- `PLAN.md`: experiment plan.
- `config.json`: configuration and tool hashes.
- `subjects.json`: input hashes.
- `dataset/mutants_manifest.jsonl`: predefined mutation candidates.
- `rq1_mutant_killing.csv`: per-mutant detection results.
- `generation_runs.jsonl`: generation commands.
- `mutant_results.jsonl`: detection results and localization evidence paths.
- `exceptions.csv`: exception ledger.
- `completion_audit.json`: post-experiment completeness checks.
