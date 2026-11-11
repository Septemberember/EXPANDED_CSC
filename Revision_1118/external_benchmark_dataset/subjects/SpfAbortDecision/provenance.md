# SpfAbortDecision

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/ExampleAbort.java`, abort; setNextState.

License: Apache-2.0 (retained in sources).

Domain: offset -1000..1000 and flags; original altitude = 120000 + altitudeOffset

Adaptation: Translate altitude around its threshold (no overflow on domain); flatten EnumSet to failure flag, state strings to tags; inline setNextState; preserve ambiguous transition assertion at offset=0 as -2. Original defect is retained and specified, not repaired.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
