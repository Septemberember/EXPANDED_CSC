# Search and Adaptation History

## Round 1: Sources and Selection

Symbolic PathFinder (jpf-symbc) was pinned to commit
`c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`. Its examples include controllers,
strings, and dynamic structures suitable for controlled adaptations.
The ten subjects are program cores, not ten large industrial systems.

- The recursive GitHub tree for SV-Benchmarks returned `truncated=true`.
  This did not establish the absence of Java candidates; subsequent searches
  should query the Java subtree.
- Save the pinned version, original sources, and licenses before adaptation.
  Adaptations belong under `subjects`.
- Scalarization, fixed-size structures, method inlining, and core extraction
  are allowed. The earlier mining restriction treating arrays only as
  inspiration does not apply.
- State fields may become explicit inputs without claiming reachability from
  initialization. WBS represents a single-step state transition.
- Fixed-size string matching, list insertion, and tree search should retain
  loops and decisions. Reversible scalar encodings preserve complete list outputs.
- Preserve deliberate upstream assertion outcomes. Abort's ambiguous assertion
  at `altitude=120000` and Flap's `time>1` assertion are represented by `-2`.
- Ten initial candidates required differential checks and actual tool validation;
  compilation alone was not an acceptance criterion.

## Deferred or Excluded Candidates

| Candidate | Decision | Reason and follow-up |
|---|---|---|
| Rational.gcd/simplify | Deferred | Overlaps the arithmetic group; termination for negative inputs and assertion bounds require explicit scope. Do not substitute a different GCD algorithm and describe it as direct extraction. |
| MasterMind main loop | Deferred | The snapshot sets target=0 but reads four characters, causing an out-of-bounds access. A valid game core must be defined in addition to handling I/O and randomness. |
| ObserverAutomata | Deferred | Initialization enters the absorbing Bad state. Complete initial executions and arbitrary intermediate states have different coverage meanings; prioritize the executable SimpleCounter tick core. |
| Complete concurrent FlapController | Excluded as a complete system | Only the sensor-before-motion sequential core is evaluated; thread interleavings are excluded. |
| Arbitrary linked-list Stack | Excluded as a complete structure | Fix three pushes and at most four pops, retaining exception observations. |
| Defects4J | Reserved for expansion | The version database was located; first establish one pinned source. Arbitrary current library methods cannot stand in for Defects4J subjects. |

## Round 2: Mapping Checks Before Tool Checks

Actual upstream Java was compared with adapted Java. Objects, strings,
assertions, and exceptions were retained. Reference build copies removed
JPF annotations/imports, diagnostic output, and random choices in unused
main methods. Java assertions were enabled with `-ea`. Exhaustive checks
covered 1,189,549 mapped inputs across the ten declared finite domains,
with no differences, plus ten out-of-domain rejection checks.

Findings:

1. **Preserve input parameters as initial values; use local mutable state.**
   The bank adaptation initially updated `balance` directly. Differential
   checks passed, but TBFV also substituted this variable in the FSF output
   constraint, producing expressions such as
   `balance-amount == (balance-amount)-amount`. Introducing `currentBalance`
   removed three failures without changing the FSF to hide the issue or
   modifying the tool. Earlier sources and reports are retained under
   `validation/history/SpfBankWithdrawal_round1`.
2. **Check matching records for every FSF scenario.** Zero failures or
   `CCT FULL` alone is insufficient. Abort initially passed the low-altitude
   branches and threshold assertion, but two high-altitude scenarios had no
   matching path. Ordinary solving used the fixed integer range
   `[-32768,32767]`; `--range-bound` affected only some expanded paths.
   Using an input offset in `[-1000,1000]` with original altitude
   `120000+offset` made all six scenarios reachable and passing. This mapping
   is explicit; the tool's global bounds were unchanged.
3. **Iteration requirements depend on source control flow.** WBS retained the
   complete single-step controller. A limit of 160 was insufficient; with a
   limit of 1000 it reported completion at iteration 841, with 840 solver
   records and 58 actual executions. Infeasible records are not test cases.
   All 41 FSF scenarios had matching paths.
4. **Distinguish skipped scenario matches from missing coverage.** For mutually
   exclusive scenarios, a path can legitimately skip other scenarios.
   Acceptance requires at least one passing match for each scenario rather
   than treating the total skipped count as failure.
5. **Include size restrictions in the FSF.** Out-of-domain inputs return `-1`,
   assertion/exception outcomes return `-2`, and no-pop outcomes return `-3`.
   These are adaptation-interface conventions, not original Java return values.
6. **Describe simple components at their actual scale.** SimpleCounter
   illustrates scalarized controller state and inlined calls, but has only
   nine in-domain inputs. It does not establish large-system scalability.
   A later collection could prioritize a more complex controller from another source.

## Follow-up Search Guidelines

- Identify source methods, observable outputs, and controlled input domains
  before scalarization; do not rank candidates solely by lines of code.
- Prefer independently executable upstream Java for differential checking.
  Do not replace it with a rewritten reference algorithm.
- Search the SV-Benchmarks Java subtree and pinned Defects4J project versions;
  check the original 42 programs' provenance to avoid duplicate cores.
- Follow the sequence: save sources, define mappings, construct adaptations
  and FSFs, run upstream differential checks, run CSC/TBFV, audit matches
  per FSF scenario, then accept.
- Document capability losses from scalarization, fixed containers, and output
  encodings: variable sizes, aliasing, concurrent schedules, arbitrary call
  sequences, and reachability across steps.
- These checks concern compatibility and behavior preservation. Formal
  RQ1–RQ3 experiments require fresh sessions, explicit configurations, and
  mutants; acceptance smoke-test timings are not final performance results.

## Batch 2 Expansion

Ten additional cores completed independent acceptance audits. Sources,
adaptation counterexamples, exclusions, and lessons are recorded in the
[Batch 2 search history](batch2/SEARCH_LOG.md). The two batches total
20 cores; see `catalog.json`.
