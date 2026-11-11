# D4jMonotonicOrder

Source: Defects4J Math-1f project snapshot; https://github.com/apache/commons-math, commit `86545dab3ed57872ad98b23e46924d67ddad03fc`.

Snapshot: `commons-math/MathArrays.java`; selected method(s): checkOrder(double[], OrderDirection, boolean, boolean).

Domain and mapping: three exact integer-valued doubles -3..3; both directions/strictness; abort=false

Adaptations and retained observable: Flatten array and enum, specialize abort=false, replace labeled early-break with equivalent return. Integer mapping exact on finite domain; no claim for NaN, infinities or rounding.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
