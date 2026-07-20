# EX_CSC_dataset Quality Report

Generated from a fresh rerun of the EX_CSC_dataset originals using batch CSC generation and Refined TBFV.

Workflow:

- CSC: `python3 csc_tool.py <Subject.java> --strategy batch --workers 4 --max-iter 50`
- TBFV: `python3 refined_tbfv_tool.py <testcases.json> --java-file <Subject.java> --fsf <Subject_FSF.txt>`
- Output sessions: `csc_tmp/ex2_full_rerun_<subject>/`
- Median replacement probe: `csc_tmp/ex2_medianofsix_probe/`

Each subject directory contains:

```text
Subject/
  Subject.java
  FSF/
    Subject_FSF.txt
```

## Summary

| Metric | Value |
| --- | ---: |
| Subjects | 8 |
| Total executable testcases | 1816 |
| Average executable testcases | 227.000 |
| Total TBFV passed checks | 1841 |
| Total TBFV failed checks | 0 |
| Total unsupported checks | 0 |

## Subjects

| Subject | Shape | CSC records | Executable | TBFV passed | TBFV failed | Skipped | Unsupported |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `SubtractLoop` | bounded loop arithmetic | 205 | 205 | 205 | 0 | 205 | 0 |
| `MaxOfFive` | five-element max network | 219 | 219 | 219 | 0 | 0 | 0 |
| `MedianOfSix` | six-input lower median | 384 | 384 | 384 | 0 | 0 | 0 |
| `TicketPrice` | signed offset loop | 206 | 206 | 206 | 0 | 412 | 0 |
| `TaxBracket` | bounded deduction loop | 326 | 326 | 326 | 0 | 1304 | 0 |
| `GradePolicy` | penalty normalization loop | 148 | 148 | 171 | 0 | 1013 | 0 |
| `InventoryReorder` | capped reorder normalization loop | 109 | 109 | 111 | 0 | 870 | 0 |
| `PairSortCheck` | five-element sorting network | 219 | 219 | 219 | 0 | 0 | 0 |

## Notes

- The dataset satisfies the current quality threshold: average executable testcases are above 50.
- All originals pass Refined TBFV with zero failed and zero unsupported checks.
- `MedianOfSix` replaces the smaller `MedianOfThree` subject. It computes the lower median, i.e. the third-smallest value among six inputs.
- `MedianOfEight` was tested as a candidate, but both full sorting-network and lower-median selection-network versions exceeded the 3-minute CSC budget, so it was not included as a main subject.
- `GradePolicy` and `InventoryReorder` have TBFV passed counts slightly above executable counts because a few symbolic paths overlap more than one FSF partition.
