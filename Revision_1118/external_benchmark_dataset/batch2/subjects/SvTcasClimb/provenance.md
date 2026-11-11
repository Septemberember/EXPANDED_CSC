# SvTcasClimb

Source: SV-Benchmarks Java; https://github.com/sosy-lab/sv-benchmarks, commit `2e1723fde6aa65a250dcb677efa45edaa4b6b631`.

Snapshot: `sv-benchmarks/java/java-ranger-regression/TCAS_prop1/Main.java`; selected method(s): Non_Crossing_Biased_Climb; ALIM; Inhibit_Biased_Climb; Own_Above_Threat.

Domain and mapping: four altitude layers; up/down = ALIM(layer)+100*delta, delta -2..2; vertical separation 500/600/700; own/other altitude 1/0 if above else 0/0; inhibit bool

Adaptations and retained observable: Extract non-crossing climb predicate (not full advisory); inline helpers and expose fields. Preserve original comparison order and return boolean encoded 0/1.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
