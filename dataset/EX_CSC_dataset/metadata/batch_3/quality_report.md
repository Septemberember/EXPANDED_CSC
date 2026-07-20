# EX_CSC_dataset Quality Report

`EX_CSC_dataset` is a regenerated follow-up dataset designed to avoid overlap with
`EX_CSC` and `EX_CSC_dataset` while preserving the program shapes where CCT-based
fault localization showed strong behavior.

Each subject follows the same structure:

```text
Subject/
  Subject.java
  FSF/
    Subject_FSF.txt
```

## Design Rationale

The regenerated subjects keep the original motivation for `EX_CSC_dataset`:

- clear condition-to-statement regions,
- loop-body arithmetic updates that can expose statement/data-flow faults,
- regular path partitions that CCT condition sequences can capture,
- sorting/selection-style compare-swap regions where SFL can be diluted by
  repeated common coverage,
- full-coverage or near-full-coverage FSFs so Refined TBFV produces useful
  checks rather than many skipped cases.

The previous version contained direct duplicates of `LoopBubbleSortFive`,
`OddEvenSortFive`, `PairwiseSortFive`, and several normalizer/offset variants
from `EX_CSC` or `EX_CSC_dataset`.  Those subjects have been replaced.

## Original Checks

All subjects were checked with batch CSC generation and Refined TBFV:

```text
python3 csc_tool.py <Subject.java> --strategy batch --workers 4 --max-iter 50
python3 refined_tbfv_tool.py <testcases.json> --java-file <Subject.java> --fsf <Subject_FSF.txt>
```

| Subject | Shape | CSC records | Executable | TBFV passed | TBFV failed | Skipped | Unsupported |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `WeightedAddLoop` | weighted signed update loop | 166 | 166 | 166 | 0 | 332 | 0 |
| `MarginAdjustLoop` | signed margin adjustment loop | 126 | 126 | 128 | 0 | 502 | 0 |
| `SaturatingPenaltyLoop` | saturating penalty loop | 77 | 77 | 78 | 0 | 307 | 0 |
| `RewardCapLoop` | capped reward loop | 86 | 86 | 88 | 0 | 514 | 0 |
| `GappedSwapFive` | insertion-style compare-swap network | 120 | 120 | 120 | 0 | 0 | 0 |
| `TailRotateSortFive` | looped adjacent compare-swap network | 120 | 120 | 120 | 0 | 0 | 0 |
| `MedianWindowFive` | five-input median selection network | 84 | 84 | 84 | 0 | 0 | 0 |
| `TwoBucketLoop` | two-bucket capped accumulation loop | 91 | 91 | 93 | 0 | 726 | 0 |

## Summary

| Metric | Value |
| --- | ---: |
| Subjects | 8 |
| Total executable testcases | 870 |
| Average executable testcases | 108.750 |
| Total TBFV passed checks | 877 |
| Total TBFV failed checks | 0 |
| Total unsupported checks | 0 |

## Duplicate Check

Normalized source hashing found no exact duplicate groups involving `EX_CSC_dataset`
against `EX_CSC` or `EX_CSC_dataset`.

## Notes

`WeightedAddLoop` and `MarginAdjustLoop` preserve the AddLoop-style localization
advantage: faults occur in compact branch-to-update regions, which gives CCT
edge and condition views a clear structural signal.

`GappedSwapFive`, `TailRotateSortFive`, and `MedianWindowFive` preserve the
sorting/selection flavor without copying the existing `BubbleSortFive`,
`LoopBubbleSortFive`, `OddEvenSortFive`, or `PairSortCheck` subjects.

`MarginAdjustLoop`, `SaturatingPenaltyLoop`, `RewardCapLoop`, and
`TwoBucketLoop` have small passed-count overlap caused by adjacent symbolic FSF
partitions, but all remain zero-fail and the overlap is limited.
