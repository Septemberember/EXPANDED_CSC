# FSF Generation Guide

This guide summarizes practical rules for writing Functional Scenario Form
(FSF) files for the CSC dataset. It is based on the FSF definition in
`paper/TBFVfirst.pdf` and the existing FSF examples under
`CSC_V2_dataset/fsf_dir`.

## 1. What an FSF Describes

An FSF is not a summary of the current program path. It is a scenario-based
specification of the expected behavior.

Each FSF unit has the following format:

```text
[fsf_i]
    T: input scenario condition
    D: expected output defining condition
```

`T` is the guard or test condition. It describes which inputs belong to this
functional scenario.

`D` is the defining condition. It describes what the correct output must satisfy
when `T` holds.

For ordinary Java methods with a return value, use `return_value` in `D`.

```text
[fsf_1]
    T: n <= 1
    D: return_value == -1
```

## 2. Write the Specification, Not the Implementation

The most important rule is: FSF should describe the correct intended behavior,
not merely what the current code happens to do.

If the implementation contains a suspicious branch, magic constant, or defect,
do not copy that defect into the FSF. The FSF should help TBFV expose such
errors.

For example, if a method should return the largest proper factor of `n`, then
for `n == 100000` the expected result is `50000`. Even if the implementation
skips `50000`, the FSF should still say:

```text
[fsf_2]
    T: n == 100000
    D: return_value == 50000
```

## 3. Keep Scenario Conditions Mutually Exclusive

The paper's well-formed FSF condition requires different guard conditions to be
mutually exclusive and collectively cover the intended input domain.

Avoid overlapping scenarios such as:

```text
[fsf_1]
    T: n > 1
    D: return_value >= 1

[fsf_2]
    T: n % 2 == 0
    D: return_value == n / 2
```

For even `n > 1`, both scenarios match.

Prefer explicit partitioning:

```text
[fsf_1]
    T: n <= 1
    D: return_value == -1

[fsf_2]
    T: n > 1 && n % 2 == 0
    D: return_value == n / 2

[fsf_3]
    T: n > 1 && n % 2 != 0
    D: ...
```

## 4. Let `T` Classify Inputs and `D` Define Outputs

`T` should mainly use input variables. `D` should use output variables such as
`return_value`, `fee`, or another explicitly produced result.

Good:

```text
[fsf_2]
    T: tons > 0 && tons < 3
    D: fee == 3 * tons
```

Avoid putting the output definition into `T`:

```text
[fsf_2]
    T: tons > 0 && fee == 3 * tons
    D: true
```

## 5. Split by Distinct Output Formulas

When different input regions have different output formulas, write one FSF unit
for each region.

For a tiered water-fee calculation, write:

```text
[fsf_1]
    T: tons <= 0
    D: fee == 0

[fsf_2]
    T: tons > 0 && tons < 3
    D: fee == 3 * tons

[fsf_3]
    T: tons >= 3 && tons < 10
    D: fee == 3 * 2 + 4 * (tons - 2)
```

This gives TBFV a precise expected formula for every functional scenario.

## 6. Prefer Tool-Friendly Expressions

A mathematically complete specification may require quantifiers, sets, or helper
functions. The current FSF tooling is intentionally lightweight, so prefer
expressions that the parser and Z3 conversion can handle:

- integer comparisons: `>`, `>=`, `<`, `<=`, `==`, `!=`
- arithmetic: `+`, `-`, `*`, `/`, `%`
- boolean operators: `&&`, `||`, `!`
- variables already known to the tool, especially inputs and `return_value`

Avoid quantifiers and unsupported helper functions in FSF files.

For example, instead of writing a fully quantified largest-factor property, use
finite, tool-friendly scenarios:

```text
[fsf_3]
    T: n > 1 && n % 2 == 0
    D: return_value == n / 2

[fsf_4]
    T: n > 1 && n % 2 != 0 && n % 3 == 0
    D: return_value == n / 3
```

## 7. Use Special Scenarios for Important Boundary or Bug-Revealing Inputs

If a particular input is important for the intended behavior or likely to expose
a defect, make it a separate scenario.

Examples:

```text
[fsf_1]
    T: n <= 1
    D: return_value == -1

[fsf_2]
    T: n == 100000
    D: return_value == 50000
```

This prevents a broad scenario from hiding the exact behavior that should be
checked.

## 8. Use Bounded Scenarios When Necessary

If the full input domain is too difficult to express with the current tooling,
it is acceptable to write bounded scenarios for the experiment.

Example:

```text
[fsf_9]
    T: n > 1 && n < 200 && n % 2 != 0 && n % 3 != 0 && n % 5 != 0 && n % 7 != 0 && n % 11 != 0 && n % 13 != 0
    D: return_value == 1
```

This expresses a useful bounded prime-like scenario without requiring
quantifiers.

## 9. Recommended Workflow

1. Read the method signature and identify input variables and output variables.
2. Write the intended behavior in natural language before relying on the code.
3. Identify input regions that produce different output formulas.
4. Convert those regions into mutually exclusive `T` conditions.
5. Write the expected output formula for each region as `D`.
6. Add separate scenarios for boundary values and bug-revealing constants.
7. Check that all expressions use syntax supported by the current FSF tooling.
8. Re-read the FSF and ask: does this describe correct behavior, or just the
   current implementation?

## 10. Quick Checklist

- `T` uses input variables to classify the scenario.
- `D` uses output variables to define the expected result.
- Different `T` conditions do not overlap.
- The intended input domain is covered, or the experimental bound is explicit.
- Suspicious implementation details are not copied as specification.
- Important boundary values have their own scenarios when useful.
- Expressions are simple enough for the current parser and solver.

In short: FSF is a piecewise specification. `T` partitions the input space, and
`D` defines the correct output for each partition.
