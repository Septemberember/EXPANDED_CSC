# SvTokenIdentifier

Source: SV-Benchmarks Java; https://github.com/sosy-lab/sv-benchmarks, commit `2e1723fde6aa65a250dcb677efa45edaa4b6b631`.

Snapshot: `sv-benchmarks/java/java-ranger-regression/printtokens_eqchk/impl/PrintTokens2.java`; selected method(s): isIdentifier; isalpha; isdigit.

Domain and mapping: exactly three printable ASCII characters followed by NUL

Adaptations and retained observable: Flatten token array and inline character classification; preserve scan and early rejection. Does not tokenize streams or recognize other token classes.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
