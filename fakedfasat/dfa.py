from typing import Dict, Iterable, List, Tuple


class DFA:
    """Deterministic Finite Automaton"""

    def __init__(
        self,
        states: Iterable[int],
        alphabet: Iterable[str],
        initial_state: int,
        transitions: Dict[Tuple[int, str], int],
        accepting_states: Iterable[int],
    ) -> None:
        """
        Args:
            states (Iterable[int]): States of the automaton
            alphabet (Iterable[str]): Set of tokens to transition from states to state
            initial_state (int): The initial state of the automaton
            transitions (Dict[Tuple[int, str],  int]): Pairs of (source_state, token)
                and target_state
            accepting_states (Iterable[int]): Accepting states of the automaton
        """
        self.states = states
        self.alphabet = alphabet
        self.initial_state = initial_state
        self.transitions = transitions
        self.accepting_states = accepting_states

    def label(self, trace: List[str]):
        """Function that takes a trace and labels it

        Args:
            trace (List[str]): Trace, list of tokens

        Returns:
            int: 1 if the trace ends in an accepting state, 0 otherwise.
        """
        state = self.initial_state
        for step in trace:
            state = self.transitions.get((state, step), state)
        return 1 if state in self.accepting_states else 0


if __name__ == "__main__":
    pass
