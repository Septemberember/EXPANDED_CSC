# SvCliOption

Source: SV-Benchmarks Java; https://github.com/sosy-lab/sv-benchmarks, commit `2e1723fde6aa65a250dcb677efa45edaa4b6b631`.

Snapshot: `sv-benchmarks/java/java-ranger-regression/apachecli_eqchk/OptionValidator.java`; selected method(s): validateOption; isValidOpt; isValidChar.

Domain and mapping: ASCII codes0..127

Adaptations and retained observable: Inline option validation helper chain; exception -> -1 and success ->1. Preserve dot/underscore acceptance present in implementation despite narrower prose comments. Small reserve subject; not full CLI parsing.

Input outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.
