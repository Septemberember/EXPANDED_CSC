# LoopSelectionSortFive

Original source:

- `LoopSelectionSortFive.java`

Target method:

- `selectionSortCheck(int a, int b, int c, int d, int e)`

Bound FSF:

- `../fsf_dir/LoopSelectionSortFive_FSF.txt`

Suggested bootstrap:

```text
a=5,b=1,c=4,d=2,e=3
```

Program features:

- fixed five-scalar sorting subject,
- controlled four-position loop,
- suffix-minimum compare-swap regions,
- clear line-level mutation targets.
