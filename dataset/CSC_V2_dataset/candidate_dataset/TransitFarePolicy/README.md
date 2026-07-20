# TransitFarePolicy

Medium-sized main benchmark candidate for CSC, refined TBFV, and fault
localization experiments.

- Shape: layered transit fare computation with one small bounded audit loop.
- Fault-localization value: many condition-to-statement regions, several
  boundary checks, and arithmetic state updates.
- Return value: fare in cents, or `-1` for invalid inputs.

