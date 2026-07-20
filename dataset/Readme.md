# CSC Dataset and Mutant Generation Guide

This document records the dataset requirements and mutation rules used for
building Java subjects for the CSC and refined TBFV workflow. It is intended as
a working guide for extending `CSC_V2_dataset` and for creating fault
localization benchmark data.

## Dataset Goal

Each dataset subject should contain an original Java program that is compatible
with the current toolchain:

1. auto-instrumentation by `java_bridge`,
2. compilation and execution by `csc_tool.py`,
3. execution trace collection through `CSCTrace` JSONL,
4. condition sequence and CCT construction,
5. refined TBFV verification against a bound FSF,
6. optional fault localization on failed mutant runs.

The preferred dataset unit is therefore a small, deterministic Java program
with one clearly identifiable target method and a functional scenario
specification that the original program fully satisfies.

## Main Benchmark Admission

Not every tool-compatible program should be used as a main experimental
subject. The main benchmark should demonstrate CSC expansion, boundary handling,
parallelization, refined TBFV, and CCT-based fault localization. It should not
be dominated by uncontrolled path explosion.

Use two practical categories during dataset construction:

- `main_subject`: used in primary experimental tables and discussion.
- `excluded_candidate`: generated or inspected during exploration, but not used
  in the planned benchmark.

Large multi-loop programs should normally become `excluded_candidate` for this
project. The planned experiments should not depend on programs whose main
behavior is path explosion.

### Main Subject Admission Criteria

A program should be admitted as a main subject only if it is experimentally
complete under a reasonable budget.

Recommended budget checks:

```text
original/batch:    --max-iter 100
expanded/sequential: --max-iter 500
```

For the current benchmark construction workflow, also apply the following
wall-clock admission budget:

```text
CSC testcase generation: strategy=batch, max-iter=50, workers=4, finish within 3 minutes
Refined TBFV/localization: no global wall-clock cap, but each testcase verification should respect a 30 second budget
```

The CSC budget is a subject-level admission rule. A candidate that cannot finish
testcase generation within 3 minutes under the batch-50 setting should not enter
the main benchmark, even if the source code looks realistic or has many lines.
The TBFV/localization budget is testcase-level: long total runtime is acceptable
when it comes from many valid test cases, but a single testcase should not
consume unbounded verification time.

When increasing subject size for fault-localization experiments, prefer longer
statement regions and mutually exclusive decision layers over many independent
boolean branches. A program with 120-150 source lines can still be unsuitable if
those lines are created by independent conditions whose frontiers multiply under
batch mode. Good large subjects should make top-k line rankings meaningful while
keeping the batch frontier count controlled.

Within these budgets, a main subject should:

- finish stably and write `testcases.json`,
- write `cct_stats.json`,
- produce a refined TBFV report for the original,
- avoid spending most runtime in CCT merge, loop expansion, or frontier
  explosion,
- generate enough executable test cases for meaningful analysis.

Suggested empirical thresholds:

- at least 10%-20% of generated records should be executable test cases, or
- the run should cover several distinct FSF scenarios, and
- failures or skipped branches should not dominate the entire run.

These thresholds are guidelines, not theorem-level requirements. If a subject
misses them, mark it as `excluded_candidate` unless there is a clear reason to
keep it in the main benchmark.

### FSF Reachability Requirement

FSF scenarios should be naturally reachable by CSC-generated paths under the
chosen budget. A subject with many FSF units is not useful for refined TBFV if
almost all units are always skipped.

For main subjects, require that:

- multiple FSF scenarios can be matched by generated paths, or
- each selected mutant has a targeted, documented bootstrap/path-generation
  setup that reaches the relevant FSF scenario.

If a program has rich FSFs but CSC only reaches one scenario in practice, it is
better excluded from the main benchmark or used only as a manually targeted
debugging case.

### Loop and Frontier Requirements

Loops in main subjects should be experiment-friendly:

- prefer zero or one primary loop,
- keep loop bounds small,
- avoid several independent loops whose branch combinations multiply,
- avoid loop conditions that repeatedly create many infeasible frontier
  branches,
- avoid path structures where most iterations produce no new executable test
  case.

Multiple independent loops should be called out explicitly and excluded from
primary effectiveness claims unless they meet the admission criteria above.

### Batch-Friendliness Requirement

Because parallelization is one of the extensions being evaluated, main subjects
should allow batch mode to complete within the selected budget.

A good batch subject has several independent frontier branches that can be
solved and executed in parallel, but does not generate hundreds of loop-expanded
frontiers in one round.

If batch mode times out or is dominated by frontier explosion, classify the
subject as `excluded_candidate`.

### Fault Localization Suitability

Main fault-localization subjects should have clear condition-to-statement
regions. The injected fault should map to a small source interval or a clear CCT
condition node.

Avoid using a program as a main localization subject if:

- paths are very deep,
- repeated loop conditions dominate the suspicious ranking,
- the same condition appears many times with high loop counts,
- the fault location is consistently obscured by loop structure rather than by
  meaningful semantic evidence.

Such programs should not be used for the planned main fault-localization
evaluation.

## Original Program Requirements

Use these requirements when adding new original programs.

### Required Shape

- Use a single Java source file.
- Do not declare a `package`.
- Avoid external dependencies.
- Keep the public class name identical to the file name.
- Provide one clear `public static` target method.
- Do not require `System.in`, files, network, time, randomness, or command-line
  parsing inside the target method.

Recommended form:

```java
public class SubjectName {
    public static int targetMethod(int x, int y, boolean flag) {
        ...
    }
}
```

The current tool can synthesize a `main` method that calls this target method
with generated inputs.

### Supported Data Types

Preferred input and output types:

- `int`
- `boolean`
- `char`

Acceptable but less preferred:

- `float`
- `double`

Avoid as target method parameters or return values:

- arrays,
- objects,
- strings,
- collections,
- maps,
- custom classes.

Arrays can often be rewritten as fixed scalar parameters. For example, a
five-element sorting subject should prefer `int a, int b, int c, int d, int e`
over `int[] values`.

### Expression Requirements

Conditions and postconditions should use Java expressions that can be translated
to Z3. Prefer:

```text
>, >=, <, <=, ==, !=
&&, ||, !
+, -, *, /, %
++, --, +=, -=
```

Use `++` and `--` only as simple standalone updates or direct loop updates.
They should be kept on scalar local variables and should not create
non-terminating loops. Avoid `++` or `--` inside complex expressions, on fields,
on array elements, or on object references.

Avoid:

- method calls inside path-critical conditions,
- object field conditions,
- array indexing in conditions,
- string operations,
- exceptions as normal control flow,
- bit shifts and complex bit-level formulas,
- complex casts,
- side effects inside boolean expressions.

### Loop Requirements

Loops are allowed and useful, but they should be small and analyzable.

Recommended:

- input-guarded loops,
- simple integer or character loop counters,
- clear monotonic updates,
- bounded business loops such as fee accumulation, score normalization, or
  factor search with an explicit guard.

Avoid:

- unbounded loops,
- loops whose termination depends on external state,
- update-direction changes that may cause non-termination,
- nested loops with large path spaces.

For main subjects, prefer loops that affect a small number of path levels. A
single bounded loop with simple branch logic is usually acceptable. Several
independent loops, each with internal branches, should normally be excluded
unless budget checks show that CSC and batch mode still complete with useful
testcase yield.

### FSF Requirements

Each original program should have an FSF that passes refined TBFV verification.
Use the simple text format:

```text
[fsf_1]
T: x >= 0 && x <= 10
D: return_value >= 0

[fsf_2]
T: x < 0
D: return_value == -1
```

`T` describes the functional scenario or input region. `D` describes the
required postcondition. Keep both expressions within the supported Z3-friendly
expression subset.

The original program should be verified before mutant generation. Mutants are
then generated under the assumption that the original program already matches
the FSF.

## Subject Directory Layout

Recommended subject layout:

```text
CSC_V2_dataset/
  SubjectName/
    SubjectName.java
    SubjectName_M1.java
    SubjectName_M2.java
    ...
```

For FSF files, use either subject-local FSF directories or the existing shared
`fsf_dir` convention. The TBFV loader accepts class-named files such as:

```text
SubjectName_FSF.txt
SubjectName_fsf.txt
```

## Mutant Strategy

The recommended strategy is FSF-sensitive mutation. The goal is not to generate
every possible traditional mutation, but to generate mutants that are likely to
violate the FSF while keeping a clean single-fault ground truth for fault
localization.

Each mutant should contain exactly one atomic edit.

The original program should satisfy the FSF. A mutant changes one local semantic
element. The mutated program is then expected to violate at least one FSF
scenario in refined TBFV verification.

## Recommended Mutation Operators

### BOR: Boundary Operator Replacement

Replace boundary-sensitive relational operators:

```text
<  -> <=
<= -> <
>  -> >=
>= -> >
```

Purpose:

- models off-by-one errors,
- models incorrect inclusive/exclusive business boundaries,
- often changes which FSF scenario applies or which result is produced.

Example:

```java
if (rawScore < 0 || rawScore > 100)
```

to:

```java
if (rawScore <= 0 || rawScore > 100)
```

This is a primary mutation operator because FSFs frequently describe boundary
regions.

### ROR: Relational Operator Replacement

Replace relational operators more aggressively:

```text
== -> !=
!= -> ==
<  -> >
>  -> <
<= -> >=
>= -> <=
```

Purpose:

- models reversed predicates,
- models wrong branch selection,
- primarily creates control-flow faults visible in CSC/CCT paths.

Example:

```java
if (score > 100)
```

to:

```java
if (score < 100)
```

Use this operator carefully because it can create large semantic changes.

### LOR: Logical Operator Replacement

Replace one logical connector in a compound condition:

```text
&& -> ||
|| -> &&
```

Purpose:

- models incorrect combination of business constraints,
- is useful for invalid-input checks and multi-clause functional scenarios,
- changes the path condition structure.

Example:

```java
if (distance > 30 || waitMinutes < 0 || waitMinutes > 60)
```

to a mutant where one `||` is changed to `&&`.

Only mutate one connector per mutant. Preserve the original surrounding
structure where possible so the fault location remains clear.

### CR: Constant Replacement

Change a business constant or threshold to a nearby value:

```text
c -> c + 1
c -> c - 1
c -> another nearby domain value
```

Purpose:

- models copied or misread business rules,
- affects thresholds, fees, scores, limits, and sentinel return values,
- often directly violates FSF postconditions.

Examples:

```java
if (distance > 30)
```

to:

```java
if (distance > 29)
```

or:

```java
fare += 5;
```

to:

```java
fare += 4;
```

This is a primary mutation operator because functional specifications are often
defined by constants.

### AOR: Arithmetic Operator Replacement

Replace arithmetic operators in calculations:

```text
+ -> -
- -> +
* -> /
/ -> *
% -> /
```

Purpose:

- models formula mistakes,
- may preserve the same execution path while changing the returned value,
- demonstrates the value of refined TBFV beyond path coverage.

Example:

```java
fare += 2;
```

to:

```java
fare -= 2;
```

Avoid arithmetic replacements that make division by zero likely.

### SUR: State Update Replacement

Modify assignment or update statements:

```text
x += c -> x += c + 1
x -= c -> x -= c + 1
i--    -> i -= 2
i++    -> i += 2
```

Purpose:

- models incorrect state propagation,
- affects loop counters, accumulators, and intermediate variables,
- is useful for fault localization because the faulty statement is often a
  single assignment or update.

Example:

```java
remainingBonus--;
```

to:

```java
remainingBonus -= 2;
```

Avoid update mutations that can make the program non-terminating, such as
turning a decreasing loop counter into an increasing one without a guard.

### RVR: Return Value Replacement

Change a return expression:

```text
return -1    -> return 0
return 100   -> return score
return value -> return value + 1
return true  -> return false
```

Purpose:

- models wrong error codes, default values, clamps, or boolean decisions,
- is stable and easy to interpret,
- provides simple baseline faults for fault localization.

This operator should be used as an auxiliary category. It is often easy to kill,
so it should not dominate the dataset.

## Recommended Operator Mix

Primary operators:

```text
BOR, CR, AOR, SUR
```

Auxiliary operators:

```text
ROR, LOR, RVR
```

The operators also cover two broad fault classes:

```text
Control-flow faults:
  BOR, ROR, LOR

Data-flow and semantic faults:
  CR, AOR, SUR, RVR
```

This distinction is useful for experiments. Control-flow mutants test path
exploration and CCT behavior. Data-flow mutants test whether refined TBFV can
detect postcondition violations even when the observed path is unchanged.

## Mutant Filtering Rules

Discard a generated mutant if any of the following holds:

- it does not compile,
- it cannot be instrumented,
- it times out during execution,
- it appears non-terminating,
- it is equivalent to the original with respect to the current FSF,
- it does not violate any FSF scenario after verification,
- it modifies multiple semantic locations,
- its fault location is ambiguous,
- it uses language features outside the supported toolchain subset.

The last two rules are important for fault localization. A benchmark mutant is
useful only when its ground-truth faulty location is clear.

## Fault Localization Ground Truth

Fault localization experiments require more than the mutant source file. Each
kept mutant must preserve the exact mutation process so later results can be
checked against the real injected fault. In particular, record both the original
line and the mutant line.

Use two levels of records:

- `mutants_roundN.jsonl`: an append-only log for one generation round.
- `mutants_manifest.jsonl`: the canonical ground-truth file for all kept
  mutants in the dataset.

`mutants_manifest.jsonl` should be treated as the source of truth for fault
localization evaluation. Each line is one JSON object.

Recommended schema:

```json
{
  "mutant_id": "SubjectName_M1",
  "round": 1,
  "subject": "SubjectName",
  "operator": "BOR",
  "fault_kind": "control-flow",
  "original_file": "SubjectName/SubjectName.java",
  "mutant_file": "SubjectName/SubjectName_M1.java",
  "original_location": {
    "line": 7,
    "code": "if (rawScore < 0 || rawScore > 100) {"
  },
  "mutant_location": {
    "line": 7,
    "code": "if (rawScore <= 0 || rawScore > 100) {"
  },
  "change": {
    "type": "single-line-replacement",
    "from": "rawScore < 0",
    "to": "rawScore <= 0",
    "description": "Boundary operator replacement in lower score guard"
  },
  "ground_truth": {
    "primary_file": "SubjectName/SubjectName_M1.java",
    "primary_line": 7,
    "acceptable_files": ["SubjectName/SubjectName_M1.java"],
    "acceptable_lines": [7],
    "acceptable_line_window": {
      "start": 7,
      "end": 7
    },
    "operator": "BOR"
  },
  "validation": {
    "compiles": true,
    "instrumentable": true,
    "csc_smoke_passed": true,
    "legal_bootstrap_smoke_passed": null,
    "original_tbfv_passed": null,
    "mutant_tbfv_failed": null,
    "failed_fsf_ids": []
  }
}
```

Use `null` for validation fields that have not been run yet. Do not guess.

### Line Number Rules

Line numbers must be checked with `nl -ba`, not estimated by inspection.

Example command:

```bash
nl -ba CSC_V2_dataset/candidate_dataset/ParkingFee/ParkingFee_M1.java
```

Record the line in the mutant file as the primary fault line. Also record the
corresponding original line. For one-line replacements these are usually the
same line number, but the manifest should store both explicitly.

If a mutation touches a multi-line condition or statement, set
`acceptable_line_window` to the complete changed source span. For most current
mutants, `start == end`.

Fault localization can then be evaluated with:

```text
Top-1 hit: predicted file == primary_file and predicted line == primary_line
Top-k hit: any predicted location is in acceptable_files and acceptable_lines
Window hit: any predicted location falls inside acceptable_line_window
```

### Few-Shot Manifest Examples

The following examples are based on generated candidate subjects and illustrate
the expected level of detail.

#### Example 1: Boundary Fault in an Input Guard

Original `ParkingFee/ParkingFee.java` line 6:

```java
if (entryHour < 0 || entryHour > 23) {
```

Mutant `ParkingFee/ParkingFee_M1.java` line 6:

```java
if (entryHour < 0 || entryHour >= 23) {
```

Manifest record:

```json
{
  "mutant_id": "ParkingFee_M1",
  "round": 2,
  "subject": "ParkingFee",
  "operator": "BOR",
  "fault_kind": "control-flow",
  "original_file": "ParkingFee/ParkingFee.java",
  "mutant_file": "ParkingFee/ParkingFee_M1.java",
  "original_location": {
    "line": 6,
    "code": "if (entryHour < 0 || entryHour > 23) {"
  },
  "mutant_location": {
    "line": 6,
    "code": "if (entryHour < 0 || entryHour >= 23) {"
  },
  "change": {
    "type": "single-line-replacement",
    "from": "entryHour > 23",
    "to": "entryHour >= 23",
    "description": "Boundary operator replacement in entry-hour upper bound"
  },
  "ground_truth": {
    "primary_file": "ParkingFee/ParkingFee_M1.java",
    "primary_line": 6,
    "acceptable_files": ["ParkingFee/ParkingFee_M1.java"],
    "acceptable_lines": [6],
    "acceptable_line_window": {
      "start": 6,
      "end": 6
    },
    "operator": "BOR"
  },
  "validation": {
    "compiles": true,
    "instrumentable": true,
    "csc_smoke_passed": true,
    "legal_bootstrap_smoke_passed": null,
    "original_tbfv_passed": null,
    "mutant_tbfv_failed": null,
    "failed_fsf_ids": []
  }
}
```

#### Example 2: Arithmetic Fault in a State Update

Original `LoanRisk/LoanRisk.java` line 22:

```java
risk += 8;
```

Mutant `LoanRisk/LoanRisk_M2.java` line 22:

```java
risk -= 8;
```

Manifest record:

```json
{
  "mutant_id": "LoanRisk_M2",
  "round": 2,
  "subject": "LoanRisk",
  "operator": "AOR",
  "fault_kind": "data-flow",
  "original_file": "LoanRisk/LoanRisk.java",
  "mutant_file": "LoanRisk/LoanRisk_M2.java",
  "original_location": {
    "line": 22,
    "code": "risk += 8;"
  },
  "mutant_location": {
    "line": 22,
    "code": "risk -= 8;"
  },
  "change": {
    "type": "single-line-replacement",
    "from": "risk += 8;",
    "to": "risk -= 8;",
    "description": "Arithmetic operator replacement in debt risk penalty"
  },
  "ground_truth": {
    "primary_file": "LoanRisk/LoanRisk_M2.java",
    "primary_line": 22,
    "acceptable_files": ["LoanRisk/LoanRisk_M2.java"],
    "acceptable_lines": [22],
    "acceptable_line_window": {
      "start": 22,
      "end": 22
    },
    "operator": "AOR"
  },
  "validation": {
    "compiles": true,
    "instrumentable": true,
    "csc_smoke_passed": true,
    "legal_bootstrap_smoke_passed": null,
    "original_tbfv_passed": null,
    "mutant_tbfv_failed": null,
    "failed_fsf_ids": []
  }
}
```

#### Example 3: State Update Fault in a Loop Counter

Original:

```java
extraHours--;
```

Mutant:

```java
extraHours -= 2;
```

Recommended record choices:

```json
{
  "operator": "SUR",
  "fault_kind": "data-flow",
  "change": {
    "type": "single-line-replacement",
    "from": "extraHours--;",
    "to": "extraHours -= 2;",
    "description": "State update replacement that changes loop iteration count"
  },
  "ground_truth": {
    "acceptable_line_window": {
      "start": 18,
      "end": 18
    }
  }
}
```

This kind of mutation can affect both the number of loop iterations and the
returned value, but the ground-truth fault is still the update statement line.

## Suggested Generation Workflow

1. Add or select an original Java program.
2. Write or bind an FSF for that original program.
3. Run CSC and refined TBFV on the original.
4. Confirm all matched FSF scenarios pass.
5. Generate one atomic mutant using one mutation operator.
6. Immediately identify the changed line with `nl -ba` in both the original and
   mutant file.
7. Append a draft record to `mutants_roundN.jsonl` and
   `mutants_manifest.jsonl`.
8. Compile and instrument the mutant.
9. Run a short CSC smoke test on the mutant.
10. When the mutation targets deeper business logic or loops, run one legal
    bootstrap smoke test to confirm that the changed region can be exercised.
11. Run refined TBFV on the mutant when an FSF is available.
12. Keep the mutant only if it violates the FSF and has a clear ground-truth
    fault location.
13. Update the manifest validation fields after each check.
14. Use the failed TBFV report and known mutation location as fault localization
    benchmark data.

### Low-Noise Validation Workflow

When generating many candidates, redirect full tool output to temporary logs and
inspect logs only on failure:

```bash
python3 csc_tool.py dataset/CSC_V2_dataset/candidate_dataset/ParkingFee/ParkingFee_M1.java \
  --max-iter 2 \
  --session cand_parking_m1 \
  > /private/tmp/cand_parking_m1.log 2>&1
```

This keeps generation runs cheap in context while preserving enough information
to debug failures.

## Fault Localization Evaluation Output

After TBFV detects a mutant violation and the fault localization tool ranks
candidate locations, save the evaluation result separately from the ground-truth
manifest. The manifest describes injected faults. The evaluation output
describes how well a localization strategy recovered those faults.

Recommended inputs:

```text
mutants_manifest.jsonl
cct_failure_localization.json
```

Recommended output:

```text
fault_localization_eval.jsonl
```

Each line should record one mutant and one localization strategy.

Recommended schema:

```json
{
  "mutant_id": "ParkingFee_M1",
  "subject": "ParkingFee",
  "strategy": "interval_rankings.edge_divergence_gated",
  "ranking_target": "interval",
  "status": "evaluated",
  "failed_cases": 30,
  "ground_truth": {
    "primary_file": "candidate_dataset/ParkingFee/ParkingFee_M1.java",
    "primary_line": 6,
    "acceptable_lines": [6],
    "acceptable_line_window": {
      "start": 6,
      "end": 6
    }
  },
  "metrics": {
    "top1_hit": true,
    "top3_hit": true,
    "top5_hit": true,
    "best_rank": 1,
    "best_line_distance": 0,
    "best_interval_width": 1,
    "best_interval_start": 6,
    "best_interval_end": 6
  },
  "notes": ""
}
```

Use explicit non-success statuses instead of silently omitting a mutant:

```text
evaluated
no_failure
not_detected
unsupported
timeout
tool_error
```

Status meanings:

- `evaluated`: TBFV produced at least one failed case and the localization
  strategy produced a comparable ranking.
- `no_failure`: refined TBFV ran successfully for the mutant, but no failed
  case was produced in that run.
- `not_detected`: broader reporting label for mutants that are not detected by
  the verification stage. In aggregate paper tables, `no_failure` mutants may
  be grouped under `not_detected`.
- `unsupported`: the mutant or localization output cannot be compared under
  the current evaluator.
- `timeout`: the verification or localization run exceeded the configured time
  limit.
- `tool_error`: the tool failed unexpectedly.

Prefer writing the most specific status in raw JSONL output. For example, use
`no_failure` when TBFV completed but produced no failed cases, then map it to
`not_detected` only in summary tables if needed.

### Ranking Targets

Keep separate results for different localization targets. Do not mix these in
one undifferentiated ranking.

Recommended `strategy` values:

```text
condition_node_ranking
interval_rankings.statement_presence
interval_rankings.edge_divergence_gated
```

Recommended `ranking_target` values:

```text
condition_node
interval
statement
```

Current benchmark results should use `condition_node` or `interval`.
`statement` is reserved for future statement-level SFL baselines. The current
`interval_rankings.statement_presence` and
`interval_rankings.edge_divergence_gated` strategies both produce interval
rankings, so their `ranking_target` should be `interval`.

Suggested interpretation:

- `condition_node_ranking`: evaluates whether the suspicious CCT condition node
  points to the injected fault region.
- `interval_rankings.statement_presence`: evaluates ranked source intervals
  produced by statement-presence evidence.
- `interval_rankings.edge_divergence_gated`: evaluates ranked source intervals
  after gating by divergent CCT edges.

### Hit Metrics

Compute hit metrics against `mutants_manifest.jsonl`:

```text
top1_hit: the first ranked item hits the acceptable line or window
top3_hit: any of the first three ranked items hits
top5_hit: any of the first five ranked items hits
best_rank: first rank where a hit occurs, or null if no hit
best_line_distance: minimum absolute distance from a ranked line or interval to
  the primary_line, or null if no comparable rank exists
best_interval_width: width of the best matching interval, or null for
  non-interval rankings
```

For interval rankings, a hit occurs when the ranked interval overlaps
`acceptable_line_window` in an acceptable file. For single-line rankings, a hit
occurs when the ranked line is in `acceptable_lines` or inside the acceptable
window.

Current candidate subjects are single-file Java subjects. If a localization
report contains only line or interval numbers and omits the source file, the
evaluation script may default `predicted_file` to
`ground_truth.primary_file`. If future subjects span multiple source files,
localization reports must include file paths explicitly.

Do not manually guess validation outcomes in `mutants_manifest.jsonl`.
`validation.mutant_tbfv_failed`, `validation.failed_fsf_ids`, and related
fields should remain `null` or empty until an automated verification run updates
them or a separate validation report records the result.

### Example Evaluation Records

Successful interval localization:

```json
{
  "mutant_id": "LoanRisk_M2",
  "subject": "LoanRisk",
  "strategy": "interval_rankings.edge_divergence_gated",
  "ranking_target": "interval",
  "status": "evaluated",
  "failed_cases": 12,
  "ground_truth": {
    "primary_file": "candidate_dataset/LoanRisk/LoanRisk_M2.java",
    "primary_line": 22,
    "acceptable_lines": [22],
    "acceptable_line_window": {
      "start": 22,
      "end": 22
    }
  },
  "metrics": {
    "top1_hit": true,
    "top3_hit": true,
    "top5_hit": true,
    "best_rank": 1,
    "best_line_distance": 0,
    "best_interval_width": 1,
    "best_interval_start": 22,
    "best_interval_end": 22
  },
  "notes": ""
}
```

Mutant not detected by TBFV:

```json
{
  "mutant_id": "SubjectName_M4",
  "subject": "SubjectName",
  "strategy": "interval_rankings.edge_divergence_gated",
  "ranking_target": "interval",
  "status": "no_failure",
  "failed_cases": 0,
  "ground_truth": {
    "primary_file": "candidate_dataset/SubjectName/SubjectName_M4.java",
    "primary_line": 18,
    "acceptable_lines": [18],
    "acceptable_line_window": {
      "start": 18,
      "end": 18
    }
  },
  "metrics": {
    "top1_hit": false,
    "top3_hit": false,
    "top5_hit": false,
    "best_rank": null,
    "best_line_distance": null,
    "best_interval_width": null,
    "best_interval_start": null,
    "best_interval_end": null
  },
  "notes": "Refined TBFV completed but produced no failed case for this mutant."
}
```

## Writing Principle for Papers

In the paper, describe the mutants as FSF-sensitive single-fault mutants:

> We generate mutants by applying one atomic semantic edit to an original Java
> subject that has been verified against its functional scenario specification.
> The mutation operators target boundary predicates, relational predicates,
> logical connectors, business constants, arithmetic formulas, state updates,
> and return expressions. These operators create both control-flow faults and
> data-flow faults. Mutants that do not compile, cannot be instrumented, timeout,
> are equivalent with respect to the FSF, or do not yield a clear fault location
> are discarded.

This framing makes the mutant dataset directly connected to the refined TBFV
and fault localization evaluation.
