# SvMinePumpStep

Source: SV-Benchmarks Java; https://github.com/sosy-lab/sv-benchmarks, commit `2e1723fde6aa65a250dcb677efa45edaa4b6b631`.

Snapshot: `sv-benchmarks/java/MinePump/spec1-5_product64/MinePumpSystem/MinePump.java`; selected method(s): timeShift; processEnvironment; Environment.lowerWaterLevel.

Domain and mapping: water enum 0/1/2=low/normal/high, all state flags; explicit arbitrary prior state

Adaptations and retained observable: Inline feature-wrapper calls and enum switches; preserve water lowering before environment processing and the counterintuitive original !isLowWaterSensorDry test (water!=low); encode pump*10+water. No reachability claim.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
