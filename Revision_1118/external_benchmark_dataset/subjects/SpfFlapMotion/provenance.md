# SpfFlapMotion

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/FlapController.java`, EmergencySensor.run; FlapMovement.run.

License: Apache-2.0 (retained in sources).

Domain: goal and initial position 0..40; emergency flag

Adaptation: Execute sensor before motion; preserve movement and time>1 assertion as -2; -1 rejects domain. No interleavings or concurrency claim.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
