# SpfTreeSearch

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/sequences/BinTree.java`, find.

License: Apache-2.0 (retained in sources).

Domain: three-node BST with 0<=left<root<right<=9; key 0..9

Adaptation: Fix tree shape to root with two leaves; replace references/null by node indices/-1; preserve traversal.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
