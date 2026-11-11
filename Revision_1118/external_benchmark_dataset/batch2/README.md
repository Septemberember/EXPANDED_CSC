# Batch 2: Ten Additional External Program Cores

This batch contains ten cores that passed acceptance checks, bringing
the dataset to **20 cores** across both batches. Batch 1 source files
and validation records remain separate. Each core has its own entry
point and FSF; the 20 cores are not 20 independent software systems.

## Sources and Adaptations

- **SV-Benchmarks Java**: commit
  `2e1723fde6aa65a250dcb677efa45edaa4b6b631`.
  Six distinct cores were selected from MinePump, Java Ranger, and
  algorithm examples. Multiple configurations of one product were not
  counted as separate cores.
- **Defects4J project snapshots**: index commit
  `8c16da8230843cdc918eaf4ddb449637f02b83c6`.
  Three methods were selected from Commons Lang
  `d1a45e9738de5b3e299bb51e987565dcce55fee6` (Lang-1f), and one from
  Commons Math `86545dab3ed57872ad98b23e46924d67ddad03fc` (Math-1f).
  These snapshots provide program cores. They are not four historical
  defect reproductions, and the selected methods are not asserted to
  be the defective locations associated with those versions.

The final column preserves selection notes from the acceptance stage.
All ten cores subsequently entered the supplementary evaluation.

| Core | Retained functionality and adaptations | Differential inputs | Executed tests | FSF scenarios | Acceptance-stage selection notes |
|---|---|---:|---:|---:|---|
| SvMinePumpStep | One mine-pump time step; environmental enumerations, state, and nested feature wrappers scalarized or inlined | 24 | 15 | 25 | State interactions; small input domain |
| SvTcasClimb | TCAS non-crossing climb decision; four threshold levels, relative separation, and helper calls | 1,200 | 56 | 3 | Priority candidate; scope limited to the climb predicate |
| SvBellmanFord3 | Three-node shortest paths; fixed edge scan unrolled, relaxation rounds and early termination retained | 625 | 11 | 4 | Priority graph-algorithm candidate |
| SvTokenIdentifier | PrintTokens three-character identifier recognition; ASCII classification and loops | 857,375 | 11 | 3 | Lexical-processing core, not a complete lexer |
| SvReplaceAtom | Single pattern-atom matching; literals, wildcards, and positive/negative character classes | 10,648 | 24 | 3 | Priority candidate with multiple branches and character-class scanning |
| SvCliOption | Apache CLI option-character validation and exceptions | 128 | 12 | 3 | Small reserve candidate |
| D4jLevenshtein23 | Edit distance for strings of lengths two and three; two working rows scalarized, nested dynamic-programming loops retained | 243 | 44 | 4 | Priority dynamic-programming candidate |
| D4jCharSqueeze | Duplicate-character compression over four characters; character ranges expanded, complete output encoded | 486 | 41 | 9 | Priority candidate with stateful loops and string output |
| D4jArrayLastIndex | Reverse search over a three-element array from a clamped starting index | 3,750 | 24 | 5 | Reserve array-scanning candidate |
| D4jMonotonicOrder | Strict/non-strict ascending/descending order checks; exact integer-to-double mapping | 1,372 | 18 | 3 | Reserve order-checking candidate |

## Completed Acceptance Checks

- Exhaustive differential checks agreed on all **875,851 in-domain
  inputs**. Ten additional checks exercised out-of-domain rejection.
- All ten cores completed CSC+Boundary generation, producing **256
  executed inputs** in total. Infeasible solver records are excluded
  from executed-input counts.
- All **62 FSF scenarios** had a matching passing path, with
  `failed=0` and `unsupported=0`.
- Z3 checks established coverage of the declared input domains,
  pairwise disjointness, and satisfiability of the FSF input scenarios.
- `validation/audit.json` records summaries and tool hashes.
  `manifest.json` and the per-core `provenance.md` files document
  sources, input domains, and adaptations.

Differential reference runs execute the saved upstream Java methods,
retaining their objects, arrays, and strings. For large Commons classes,
the reference build extracts unmodified method text and the required
upstream helper classes. Method-text hashes are recorded. Compatibility
declarations are supplied for the Verifier driver and Math exception
types; the affected branches are not invoked within the declared input
domains. Details appear in `validation/differential/report.json`.
The reference is based on upstream code rather than a separately
rewritten copy of the adapted implementation.

All out-of-domain inputs return `-99`. Normal functional outcomes,
such as unsuccessful searches or matches, may return `-1`. The checks
cover the observations declared for each core. Full upstream input
domains, dynamic structures, concurrency, I/O, and driver assertions
are outside this acceptance scope.

## Reproducing the Acceptance Checks

Run from the repository root:

```sh
python3 Revision_1118/external_benchmark_dataset/batch2/scripts/validate_differential.py
python3 Revision_1118/external_benchmark_dataset/batch2/scripts/validate_tools.py
python3 Revision_1118/external_benchmark_dataset/batch2/scripts/audit_dataset.py
```

The tool runner accepts optional class names. It reuses the Batch 1
runner with batch-local directories, fresh sessions, and the iteration
limits recorded in the manifest. `build_subjects.py` rebuilds this
batch's source files, FSFs, and initial manifest; acceptance checks
must be repeated after rebuilding. Prerequisites are Java 17, Python
`z3-solver`, and a built CSC bridge. Large logs use lossless gzip
compression, and the audit scripts support compressed reports.

This page records Batch 2 acceptance checks. All ten cores subsequently
entered the supplementary evaluation together with Batch 1; see the
[RQ1–RQ3 results](../experiments/paper_config_once_20261024/RESULTS.md).
Acceptance statistics, selection notes, and reproduction commands are
retained here. Acceptance-stage parallel smoke-test timings are excluded
from the formal performance results.
