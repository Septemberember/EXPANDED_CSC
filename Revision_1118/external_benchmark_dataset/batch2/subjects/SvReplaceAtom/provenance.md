# SvReplaceAtom

Source: SV-Benchmarks Java; https://github.com/sosy-lab/sv-benchmarks, commit `2e1723fde6aa65a250dcb677efa45edaa4b6b631`.

Snapshot: `sv-benchmarks/java/java-ranger-regression/replace5_eqchk/impl/Replace.java`; selected method(s): omatch; locate.

Domain and mapping: kind 0 literal,1 any,2 two-member class,3 negated class; codes 0..10, index0/1

Adaptations and retained observable: Scalarize one pattern atom and class contents; inline locate reverse scan; return updated index on match, -1 on failure. Exclude anchors/closure and complete replace pipeline.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
