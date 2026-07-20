# ShippingCost

Original source:

- `ShippingCost.java`

Target method:

- `calculateShipping(int weight, int distance, boolean express)`

Bound FSF:

- `../fsf_dir/ShippingCost_FSF.txt`

Suggested legal bootstrap:

```text
weight=3,distance=250,express=true
```

Mutants:

- `ShippingCost_M1.java`: BOR, shipping distance upper bound.
- `ShippingCost_M2.java`: CR, express surcharge.
- `ShippingCost_M3.java`: AOR, distance-band fee update.
