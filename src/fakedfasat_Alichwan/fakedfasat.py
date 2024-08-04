from typing import Dict, List

from src.fakedfasat_Alichwan.apta import APTA
from src.fakedfasat_Alichwan.dfa import DFA
from src.fakedfasat_Alichwan.sat_encoding import SATEncoding


def fakedfasat(
    sample: Dict[str, List], lower_boud: int = 1, upper_boud: int = 5
) -> DFA:
    """Based in the algorithm 4 of Heule & Verwer (2013) but not considering
    the greedy algorithm (so no need of a bound m)

    Args:
        sample (Dict[str, List]): Group of traces to train the model
        test_sample (Iterable): Group of traces to be label
        n_solutions (int): Number of solutions that will be voting to label each trace
        acc_pct (float): accepting vote percentage. Between 0 and 1.
    """
    apta = APTA(sample)

    for n_colors in range(lower_boud, upper_boud + 1):  # Incremental part
        apta_encoded = SATEncoding(apta, n_colors)
        automaton = apta_encoded.solve()
        if automaton is not None:
            return automaton
        # TODO: implement timeout
    print("Model couldn't be found")
    return None


if __name__ == "__main__":
    pass
