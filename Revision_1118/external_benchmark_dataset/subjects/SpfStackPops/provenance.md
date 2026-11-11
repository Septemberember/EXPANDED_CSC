# SpfStackPops

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/sequences/Stack.java`, push; pop; isEmpty.

License: Apache-2.0 (retained in sources).

Domain: push three digits then pop 0..4 times

Adaptation: Flatten three nodes to slots and depth; inline pop/isEmpty; return last popped value, -3 for no pop and -2 for empty-stack exception; remove diagnostic printing. Annotation preconditions are not enforced by ordinary Java; zero values deliberately retained.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
