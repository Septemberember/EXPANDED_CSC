# LoanRisk

Original source:

- `LoanRisk.java`

Target method:

- `classifyRisk(int income, int debt, boolean stableJob)`

Bound FSF:

- `../fsf_dir/LoanRisk_FSF.txt`

Suggested legal bootstrap:

```text
income=120,debt=130,stableJob=true
```

Mutants:

- `LoanRisk_M1.java`: BOR, high-income threshold.
- `LoanRisk_M2.java`: AOR, debt risk update.
- `LoanRisk_M3.java`: SUR, debt loop update.
