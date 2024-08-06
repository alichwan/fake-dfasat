from typing import Dict, List

from src.fakedfasat.apta import APTA
from src.fakedfasat.dfa import DFA
from src.fakedfasat.sat_encoding import SATEncoding


def fakedfasat(
    sample: Dict[str, List], lower_bound: int = 1, upper_bound: int = 5
) -> DFA:
    """Based in the algorithm 4 of Heule & Verwer (2013) but not considering
    the greedy algorithm (so no need of a bound m)

    Args:
        sample (Dict[str, List]): Group of traces to train the model

    """
    apta = APTA(sample)

    for n_colors in range(lower_bound, upper_bound + 1):  # Incremental part
        apta_encoded = SATEncoding(apta, n_colors)
        automaton = apta_encoded.solve()
        if automaton is not None:
            return automaton
        # TODO: implement timeout
    print("Model couldn't be found")
    return None


if __name__ == "__main__":
    pass
