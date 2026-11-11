# SpfSortedInsertion

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/compositional/SortedListInt.java`, insert.

License: Apache-2.0 (retained in sources).

Domain: sorted three-node list with values 0..9; inserted digit 0..9

Adaptation: Replace next pointers by cursor and scalar fields; preserve search for insertion location; encode all four output digits, including leading zeros. Fixed length makes encoding injective.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
