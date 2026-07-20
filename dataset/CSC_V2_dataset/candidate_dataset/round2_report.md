# Candidate Dataset Round 2 Report

Round 2 generated two original Java subjects and six single-fault mutants.

## Subjects

### ParkingFee

Original:

- `ParkingFee/ParkingFee.java`

Target method:

- `public static int computeFee(int hours, int entryHour, boolean weekend)`

Program features:

- invalid input guards,
- hourly fee accumulation,
- weekend and evening branch logic,
- surcharge threshold,
- return-value clamp.

Mutants:

- `ParkingFee_M1.java`: BOR, `entryHour > 23` to `entryHour >= 23`
- `ParkingFee_M2.java`: CR, weekend long-stay surcharge `5` to `3`
- `ParkingFee_M3.java`: SUR, loop update `extraHours--` to `extraHours -= 2`

Smoke status:

- Original passed `csc_tool.py` with `--max-iter 2`.
- All three mutants passed `csc_tool.py` with `--max-iter 2`.
- `ParkingFee_M3` passed a legal-input bootstrap smoke test with
  `hours=8,entryHour=19,weekend=true`.

### LoanRisk

Original:

- `LoanRisk/LoanRisk.java`

Target method:

- `public static int classifyRisk(int income, int debt, boolean stableJob)`

Program features:

- invalid input guards,
- income threshold branches,
- bounded debt loop,
- stable-job adjustment,
- lower and upper return clamps.

Mutants:

- `LoanRisk_M1.java`: BOR, `income >= 100` to `income > 100`
- `LoanRisk_M2.java`: AOR, debt penalty `risk += 8` to `risk -= 8`
- `LoanRisk_M3.java`: SUR, debt loop update `debtLeft -= 50` to
  `debtLeft -= 40`

Smoke status:

- Original passed `csc_tool.py` with `--max-iter 2`.
- All three mutants passed `csc_tool.py` with `--max-iter 2`.
- `LoanRisk_M3` passed a legal-input bootstrap smoke test with
  `income=120,debt=130,stableJob=true`.

## Notes

This round used low-noise validation: full command output was redirected to
temporary logs under `/private/tmp`, and only failures would be inspected. This
is much cheaper in context tokens than keeping every CCT printout in the
conversation.
