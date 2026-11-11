# D4jArrayLastIndex

Source: Defects4J Lang-1f project snapshot; https://github.com/apache/commons-lang, commit `d1a45e9738de5b3e299bb51e987565dcce55fee6`.

Snapshot: `commons-lang/ArrayUtils.java`; selected method(s): lastIndexOf(int[], int, int).

Domain and mapping: three-element non-null int array, values/key0..4; startIndex -1..4

Adaptations and retained observable: Flatten array, preserve backward scan and start-index clamping. Distinct from prior delimiter earliest-match scan.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
