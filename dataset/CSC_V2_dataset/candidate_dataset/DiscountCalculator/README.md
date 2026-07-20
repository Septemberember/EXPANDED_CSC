# DiscountCalculator

Original source:

- `DiscountCalculator.java`

Target method:

- `computeDiscount(int price, int customerYears, boolean coupon)`

Bound FSF:

- `../fsf_dir/DiscountCalculator_FSF.txt`

Suggested legal bootstrap:

```text
price=500,customerYears=12,coupon=true
```

Mutants:

- `DiscountCalculator_M1.java`: BOR, high-price threshold.
- `DiscountCalculator_M2.java`: LOR, coupon condition.
- `DiscountCalculator_M3.java`: SUR, customer-year loop update.
