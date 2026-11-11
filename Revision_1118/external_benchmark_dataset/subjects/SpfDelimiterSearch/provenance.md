# SpfDelimiterSearch

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/strings/DelimSearch.java`, search.

License: Apache-2.0 (retained in sources).

Domain: three character text and two delimiters, each code 0..9

Adaptation: Flatten fixed-length strings into scalar character codes, preserve nested search loops and earliest match; replace continue with equivalent fall-through.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
