# ParkingFee

Original source:

- `ParkingFee.java`

Target method:

- `computeFee(int hours, int entryHour, boolean weekend)`

Bound FSF:

- `../fsf_dir/ParkingFee_FSF.txt`

Suggested legal bootstrap:

```text
hours=8,entryHour=19,weekend=true
```

Mutants:

- `ParkingFee_M1.java`: BOR, entry-hour upper bound.
- `ParkingFee_M2.java`: CR, weekend long-stay surcharge.
- `ParkingFee_M3.java`: SUR, parking-hour loop update.
