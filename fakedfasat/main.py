from copy import deepcopy
from typing import Iterable

from fakedfasat.apta import APTA
from fakedfasat.solvers import Solver


def fakedfasat(sample: Iterable):
    """Based in the algorithm 4 of Heule & Verwer (2013) but not considering
    the greedy algorithm (so no need of a bound m)

    Args:
        sample (Iterable): Group of traces to train the model
        test_sample (Iterable): Group of traces to be label
        n_solutions (int): Number of solutions that will be voting to label each trace
        acc_pct (float): accepting vote percentage. Between 0 and 1.
    """
    # size_bound = int(1e10)  # In the paper is infinity
    apta = APTA(sample)

    apta_encode = apta.to_sat()  # solve, not sure how  # TODO
    solver = Solver()
    automaton = solver.solve(apta_encoded)
    if automaton is not None:  # the solver reeturns a DFA solution autom TODO
        return automaton
    elif "TIMEOUT":
        return None
    else:
        i += 1
