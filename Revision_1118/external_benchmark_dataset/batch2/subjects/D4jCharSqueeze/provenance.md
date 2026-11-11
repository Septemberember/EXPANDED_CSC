# D4jCharSqueeze

Source: Defects4J Lang-1f project snapshot; https://github.com/apache/commons-lang, commit `d1a45e9738de5b3e299bb51e987565dcce55fee6`.

Snapshot: `commons-lang/CharSetUtils.java`; selected method(s): squeeze; CharSet.contains.

Domain and mapping: four digits1..3 mapped to Java characters 1..3; charset inclusive range low..high within1..3

Adaptations and retained observable: Flatten text and replace charset range lookup with integer comparison; retain suppression loop and last-character state; encode complete output as nonzero decimal digits (injective).

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
