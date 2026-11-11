# D4jLevenshtein23

Source: Defects4J Lang-1f project snapshot; https://github.com/apache/commons-lang, commit `d1a45e9738de5b3e299bb51e987565dcce55fee6`.

Snapshot: `commons-lang/StringUtils.java`; selected method(s): getLevenshteinDistance(CharSequence, CharSequence).

Domain and mapping: strings length2 and3 over codes1..3; non-null

Adaptations and retained observable: Scalarize two working distance arrays, inline Math.min and ternary; retain nested dynamic-programming loops and recurrence. Fixed nonempty dimensions remove null/empty/swap branches. Return edit distance.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
