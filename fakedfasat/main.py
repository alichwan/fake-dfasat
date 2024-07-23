from copy import deepcopy
from typing import Iterable

from fakedfasat.apta import APTA


def fakedfasat(
    sample: Iterable, test_sample: Iterable, n_solutions: int, acc_pct: float
):
    """Based in the algorithm 4 of Heule & Verwer (2013) but not considering
    the greedy algorithm (so no need of a bound m)

    Args:
        sample (Iterable): Group of traces to train the model
        test_sample (Iterable): Group of traces to be label
        n_solutions (int): Number of solutions that will be voting to label each trace
        acc_pct (float): accepting vote percentage. Between 0 and 1.
    """
    size_bound = int(1e10)  # In the paper is infinity
    dfas = set()
    apta = APTA(sample)

    while len(dfas) < n_solutions:
        apta2 = deepcopy(apta)  # create copy of A, but this is thinking in A as a dict

        #####################################
        # Here would be the original merge states algorithm
        # apta2 -> mid_dfa
        #####################################

        if len(apta2.red_states) > size_bound:
            continue

        size_bound = apta2.red_states

        i = 0
        while True:
            autom = apta2.to_sat()  # solve, not sure how  # TODO
            if autom is not None:  # the solver reeturns a DFA solution autom TODO
                dfas.add(autom)
                break
            elif "TIMEOUT":
                break
            else:
                i += 1

        labeling = list()
        for s in test_sample:
            if (
                len({autom for autom in dfas if autom.label_trace(s) == "pos"})
                > n_solutions * acc_pct
            ):
                labeling.append(1)
            else:
                labeling.append(0)
        return labeling
