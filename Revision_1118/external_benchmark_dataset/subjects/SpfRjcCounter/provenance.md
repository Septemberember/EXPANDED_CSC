# SpfRjcCounter

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/rjc/SimpleCounter.java`, Init; Main; state entry/exit methods.

License: Apache-2.0 (retained in sources).

Domain: 0..8 Main calls after Init

Adaptation: Flatten one-element state/output arrays; inline state dispatch and transitions; bound repeated controller ticks.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
