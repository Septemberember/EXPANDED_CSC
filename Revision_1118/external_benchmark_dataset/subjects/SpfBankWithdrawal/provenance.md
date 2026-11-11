# SpfBankWithdrawal

Source: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/sequences/BankAccount.java`, deposit; withdraw.

License: Apache-2.0 (retained in sources).

Domain: balance 0..20; deposit -5..10; amount -5..30; count 0..5

Adaptation: Expose object state; keep input values immutable and copy balance to local currentBalance; inline deposit then withdraw; return final balance or -2 assertion. Preserve negative withdrawal behavior rather than silently fixing it.

This is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.
