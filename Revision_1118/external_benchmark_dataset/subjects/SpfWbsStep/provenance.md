# SpfWbsStep

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/WBS.java`, update.

License: Apache-2.0 (retained in sources).

Domain: pedal 0..4; previous mode 0..1, command 0..4, pressure 0..5; all flags; other inputs return -1

Adaptation: Expose previous state as inputs; retain complete update control flow; encode outputs normal + 10*alternate + 100*mode. Does not model multi-step reachability.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
