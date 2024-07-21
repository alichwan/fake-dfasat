# fake-dfasat

Implementation of part of the technique described by Heule and Verwer in [Software model synthesis using satisfiability solvers (2013)](https://link.springer.com/article/10.1007/s10664-012-9222-z).

It is "fake" because the original method included a reduction of the original APTA size by greedy techniques, while this approach is just considering the exact methods (from traces to APTA, and from APTA to SAT problem).
