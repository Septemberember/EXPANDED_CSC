# SvBellmanFord3

Source: SV-Benchmarks Java; https://github.com/sosy-lab/sv-benchmarks, commit `2e1723fde6aa65a250dcb677efa45edaa4b6b631`.

Snapshot: `sv-benchmarks/java/algorithms/BellmanFord-FunSat01/Main.java`; selected method(s): runBellmanFord.

Domain and mapping: N=3, source=0; edges 1->0 and 2->0 fixed to 4; other four weights 0..4; diagonal ignored

Adaptations and retained observable: Scalarize distances; unfold fixed 3x3 edge scans in original order; retain pass loop and early exit. All nodes become finite in first row so infinite guards are provably true at subsequent edges. Encode distances to nodes1/2 as 10*d1+d2; d0 remains0. No negative cycles.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
