# Controlled Adaptations of External Benchmark Programs

This dataset contains **20 Java program cores accepted as inputs to CSC
and refined TBFV**, maintained separately from the original 42-program
corpus.

- Batch 1: ten cores from JPF-Symbc, documented below.
- [Batch 2](batch2/README.md): ten cores from SV-Benchmarks Java and
  Defects4J project snapshots.
- `catalog.json`: the machine-readable catalog for both batches.
- All 20 cores are included in the supplementary evaluation. See the
  [RQ1–RQ3 results](experiments/paper_config_once_20261024/RESULTS.md)
  and [per-program results](experiments/paper_config_once_20261024/subject_results.csv).

The statistics and reproduction commands below describe Batch 1
acceptance checks. Batch 2 has its own manifest, validation reports,
and scripts.

## Batch 1 Sources and Adaptations

The source collection is
[Symbolic PathFinder / jpf-symbc](https://github.com/SymbolicPathFinder/jpf-symbc),
pinned to commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`.
Original source files and the Apache-2.0 license are retained under
`sources/jpf-symbc/`. Each core's `provenance.md` records its source
methods, input domain, adaptations, and limitations. File hashes are
recorded in `manifest.json`.

These are controlled adaptations of program cores from an external
symbolic-execution benchmark collection. The evaluation concerns the
adapted cores within their declared domains, rather than complete
upstream systems. Batch 1 shares one source collection; Batch 2 adds
other collections and project snapshots. The cores extend the
arithmetic and classification examples with state control, string
scanning, and fixed-size linked-list, tree, and stack operations.

| Input class | Retained functionality | Principal adaptations | Differential inputs | Executed tests | FSF scenarios |
|---|---|---|---:|---:|---:|
| SpfWbsStep | Complete single-step brake-controller update | State exposed as inputs; encoding of three outputs | 1,200 | 58 | 41 |
| SpfFlapMotion | Flap motion and timeout assertions | Fixed sensor-before-motion order; assertions represented as return statuses | 3,362 | 15 | 4 |
| SpfBankWithdrawal | Deposit followed by withdrawal and transaction limits | State exposed as inputs; calls inlined | 72,576 | 14 | 7 |
| SpfDelimiterSearch | Earliest delimiter search | Three-character text and two delimiters scalarized; both loops retained | 100,000 | 17 | 5 |
| SpfSubstringCount | Counting overlapping substring occurrences | Four-character text and two-character pattern scalarized; both loops retained | 1,000,000 | 20 | 9 |
| SpfSortedInsertion | Sorted linked-list insertion | Fixed three-node list; position traversal; complete result encoding | 2,200 | 12 | 5 |
| SpfTreeSearch | Binary-search-tree lookup | Fixed root and two leaves; references represented as indices | 1,200 | 13 | 3 |
| SpfAbortDecision | Spacecraft abort-state selection | Enumerations and strings scalarized; altitude-offset mapping | 4,002 | 8 | 6 |
| SpfRjcCounter | RJC counter-state updates | Single-element array scalarized; state calls inlined; at most eight ticks | 9 | 11 | 3 |
| SpfStackPops | Stack pops and empty-stack exceptions | Three pushes and at most four pops; nodes scalarized | 5,000 | 13 | 6 |

## Completed Acceptance Checks

- Exhaustive differential checks covered **1,189,549 in-domain inputs**.
  The adapted code and the upstream Java implementations agreed under
  the declared input mappings and output observations. Ten additional
  checks exercised out-of-domain rejection.
- CSC+Boundary reported `CCT FULL` for every subject. Solver records,
  execution traces, CCTs, and logs are retained.
- All **89 FSF scenarios** had a matching passing path.
  Refined TBFV reported `failed=0` and `unsupported=0`.
- Z3 checks established that the FSF input scenarios cover the declared
  input domain, are pairwise disjoint, and are individually satisfiable
  under Java int32/bool semantics.
- `validation/audit.json` records summaries, sessions, and tool
  source/JAR hashes. Executed-test counts include out-of-domain
  rejection paths; infeasible solver records are excluded.

`CCT FULL` is a tool completion status, not a claim that all upstream
program paths or states have been covered. Differential checking covers
the declared finite input domains and observed outputs. The single-step
WBS core does not establish historical-state reachability; the Flap core
does not verify concurrent interleavings; fixed structures do not cover
arbitrary lengths, shapes, or aliasing. Original Abort/Flap assertion
outcomes are retained as return statuses. Zero verification failures
therefore indicates conformance to the core's FSF, rather than a repair
of an upstream defect.

## File Layout

- `subjects/<Name>/<Name>.java`: tool input.
- `FSF/<Name>_FSF.txt`: functional-scenario specification.
- `sources/`: unmodified source snapshots and licenses, including
  deferred candidates.
- `scripts/`: deterministic construction, differential checking against
  upstream implementations, CSC/TBFV execution, and acceptance auditing.
- `validation/<Name>/`: latest acceptance runs, statuses, and artifacts;
  large logs are gzip-compressed.
- `validation/differential/`: reference builds, reports, and compatibility
  adaptation notes.
- `validation/history/`: failed or incomplete earlier attempts, retained
  separately from the latest results.
- `SEARCH_LOG.md`: search history, rejection reasons, and candidate
  selection notes.

## Reproducing the Acceptance Checks

Run from the repository root. Prerequisites are Java 17, Python
`z3-solver`, and a built CSC Java bridge.

```sh
python3 Revision_1118/external_benchmark_dataset/scripts/validate_differential.py
python3 Revision_1118/external_benchmark_dataset/scripts/validate_tools.py
python3 Revision_1118/external_benchmark_dataset/scripts/audit_dataset.py
```

`validate_tools.py` accepts optional class names to rerun selected
candidates, using fresh sessions. These acceptance checks use an iteration
limit of 1000 for WBS and 160 for the other cores, with `range-bound=40`.
The completed WBS run contains 840 solver records and 58 actual
executions; the earlier attempt with a limit of 160 is retained in the
history. Default timeouts are 300 seconds for generation and 180 seconds
for verification. A timeout fails acceptance; process termination or
the existence of output files alone does not establish completion.

`build_subjects.py` regenerates adapted source files, FSFs, and the
initial manifest. It resets acceptance status to unverified, so the
checks above must be repeated after rebuilding. The differential checker
uses Java from `JAVA_HOME` or `PATH`, with support for locally known JDK
locations. Saved tool artifacts contain absolute paths from their
original runs. For reproduction on another machine, rerun the scripts
to obtain fresh traces and results.

The supplementary evaluation covers all 20 cores from both batches;
its generation, mutant-detection, and localization results are linked
above. The statistics and commands on this page describe dataset
acceptance. Acceptance-stage parallel smoke-test timings are excluded
from the formal performance results.
