# Batch 2 Search and Adaptation History

## 1. Additional Sources

Batch 1 came from JPF-Symbc. This round queried the SV-Benchmarks Java
subtree rather than the truncated recursive repository tree and obtained
a complete Java listing (`truncated=false`). Candidates included MinePump,
Java Ranger TCAS/lexer/replacement/scheduler examples, and algorithms.
Distinct cores were selected; MinePump's 64 product configurations and
multiple TCAS property drivers were not counted as new programs.

Pinned Defects4J `active-bugs.csv` records were downloaded. The
`revision.id.fixed` values for Lang-1f and Math-1f identified the Apache
source snapshots. Both version records and sources were saved. The four
cores come from two project snapshots, not four independent defect tasks.

The original 42-program provenance records contained none of these source
methods; none duplicates a specific Batch 1 source method. ArrayLastIndex
and Batch 1 DelimiterSearch both scan inputs, but the former retains
starting-index clamping and reverse last-occurrence search, while the
latter finds the earliest match across two collections. Later selection
could consider this structural overlap to avoid excessive search examples.

## 2. Mappings and Scope Restrictions

- MinePump retains single-step execution order and all three water levels.
  Explicit state inputs do not establish reachability in the original program.
- TCAS uses `Non_Crossing_Biased_Climb`, not the complete advisory workflow.
  Separation values are offsets relative to ALIM, preserving the actual
  thresholds 400/500/640/740.
- Bellman-Ford uses three nodes and nonnegative weights; two edges returning
  to the source have weight four. The original i/j scan is unrolled in the
  same order, retaining outer relaxation rounds. Differential checks execute
  the complete original array algorithm.
- Levenshtein uses lengths two and three, retaining the dynamic-programming
  recurrence and nested loops while scalarizing working rows; it is not
  replaced by an exhaustive lookup table.
- CharSqueeze's complete string output is reversibly encoded using nonzero
  digits, rather than compared only by output length.
- Math `checkOrder` uses integers from -3 to 3 represented exactly as doubles;
  NaN and floating-point rounding are outside its scope.
- Preserve formal input initial values and update local copies. FSFs use
  `-99` for out-of-domain inputs to distinguish original functional `-1` statuses.

## 3. A Differential Counterexample and Correction

The first differential run failed on MinePump input seven:
`water=low`, `running=true`, `active=true`, `methane=false`.
The adaptation returned 0 while the original returned 10.

The initial interpretation followed the name `isLowWaterLevel`, but its
implementation was `!env.isLowWaterSensorDry()`, with
`isLowWaterSensorDry` defined as `water==low`. The actual predicate was
therefore `water!=low`. This counterintuitive upstream behavior was
preserved rather than repaired. The adaptation and its initially incorrect
FSF were corrected, followed by complete differential checks and fresh
independent tool sessions. Earlier source, FSF, failure output, and
reference-build records remain under `validation/history/MinePump_round1/`.

Tool verification alone cannot establish acceptance: an incorrect adaptation
and incorrect specification can agree with each other. Upstream differential
checking is required. Names and comments aid understanding, but executable
source determines the mapping.

## 4. Deferred or Excluded Candidates

| Candidate | Decision | Reason |
|---|---|---|
| SV WBS / BinaryTreeSearch / SortedListInsert | Not counted as additional cores | Same source family or substantial functional overlap with Batch 1; prioritize new structures. |
| Other MinePump product configurations | Not counted as additional cores | Product-line variants; suitable for later configuration studies rather than independent subjects. |
| TCAS prop2/prop3 | Not counted as additional cores | Mainly different properties or drivers rather than new algorithm cores. |
| Tsp-FunSat01 | Deferred; source retained | A shortest-path core was already selected. Recursion, matrices, and bit sets require further adaptation effort; do not replace the algorithm merely to increase the count. |
| Schedule2 | Deferred; source retained | Queue operations and multiple state categories require a more complex observation mapping; a candidate for later exploration. |
| Complete CLI parser | Deferred; source retained | Substantial option, exception, and collection dependencies. This round accepted only standalone character validation as a small reserve candidate. |
| General Commons Math double paths | Excluded from this scope | The tool abstracts double as Real, which does not establish full IEEE-754 behavior. Only exact integer embeddings are retained. |

## 5. Lessons for Subsequent Collection

1. Check source provenance, licenses, and shared origins at subtree level
   before reading methods; avoid unnecessary full-repository downloads.
2. Prefer cores whose unmodified upstream methods can execute independently,
   avoiding unrelated dependencies from large containing classes.
3. Expand actual return expressions before inlining helpers. Enumerations,
   state names, and comments may not match executable predicate semantics.
4. Perform upstream differential checks and FSF/tool validation independently.
   Both are required; MinePump demonstrates why.
5. Consider functionality, loop/branch structure, input domains, and shared
   origins when selecting formal subjects. Do not rank by test counts:
   TokenIdentifier's 857,375 differential combinations do not establish greater
   complexity than the dynamic-programming core's 243 combinations.
6. Retain small reserve candidates while prioritizing structurally diverse
   cores such as TCAS, Bellman-Ford, Replace, Levenshtein, and CharSqueeze.
