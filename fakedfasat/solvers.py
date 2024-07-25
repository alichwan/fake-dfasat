from fakedfasat.dfa import DFA


class Solver:
    """
    Solver class to encapsulate different kinds of solvers
    """

    def __init__(self) -> None:
        self.solver = None

    def solve(self, encoding) -> DFA:
        dfa = DFA()
        return dfa
