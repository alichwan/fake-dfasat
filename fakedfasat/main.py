from typing import Iterable

from fakedfasat.apta import apta


def fakedfasat(
    sample: Iterable, test_sample: Iterable, n_solutions: int, acc_pct: float
):
    """
    Based in the algorithm 4 of Heule & Verwer (2013) but not considering
    the greedy algorithm (so no need of a bound m)
    """
    t = int(1e10)  # In the paper is infinity
    D = set()
    A = apta(sample)
