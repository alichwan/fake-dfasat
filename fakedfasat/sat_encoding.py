from typing import Iterable

from pysat.formula import CNF
from pysat.solvers import Solver

from fakedfasat.apta import APTA


## stringify vars ################
def x(v, i):
    return f"x_[{v},{i}]"


def y(a, i, j):
    return f"y_[{a},{i},{j}]"


def z(i):
    return f"z_[{i}]"


##################################


class SATEncoding:
    """Encoding to convert the input automaton into a SAT problem
    The functions that are used are based on the paper
    'Software model synthesis by indentifying DFAs using satisfiability solvers'
    (Heule & Verwer, 2013)
    """

    def __init__(self, apta: APTA, n_colors: int):
        """Creates the encoding based on tne input APTA

        Args:
            apta (APTA): Tree with all the sample information
            n_colors (int): Number of colors to be used.
        """
        self.apta = apta
        # Domain
        self.colors = sorted(list(range(1, n_colors + 1)))  # C
        self.states = sorted(list(apta.nodes))  # V
        self.acc_states = sorted(list(apta.accepting_nodes))  # V+
        self.rej_states = sorted(list(apta.rejecting_nodes))  # V-
        self.tokens = sorted(list(apta.alphabet))  # Sigma/alphabet
        # self.conflict_edges = None # E, from the consistency graph. Redundant clasuses

        # Variables
        self.x_vars = self._gen_x_vars(self.states, self.colors)
        self.y_vars = self._gen_y_vars(self.tokens, self.colors)
        self.z_vars = self._gen_z_vars(self.colors)
        self.variables = self.x_vars + self.y_vars + self.z_vars
        # Creating mapping between string variables and unique variables
        self.uvar_to_svar = {
            k: v for (k, v) in enumerate(self.variables, start=1)
        }  # TODO arreglar cuando la key es negativa
        self.svar_to_uvar = {v: k for k, v in self.uvar_to_svar.items()}

        self.clauses = []
        self.at_least_one_color()
        self.acc_rej_no_same_color()
        self.set_parent_relation()
        self.parent_must_target_at_most_one_color()

    def _gen_x_vars(self, states: Iterable[int], colors: Iterable[int]):
        """
        x_[v,i] ≡ 1 iff state v has color i
        """
        return [x(v, i) for v in states for i in colors]

    def _gen_y_vars(self, tokens: Iterable[str], colors: Iterable[int]):
        """
        y_[a,i,j] ≡ 1 iff parents of states with color j
        and incoming label a have color i
        """
        return [y(a, i, j) for a in tokens for i in colors for j in colors]

    def _gen_z_vars(self, colors: Iterable[int]):
        """
        z_[i] ≡ 1 iff an accepting state has color i
        """
        return [z(i) for i in colors]

    def at_least_one_color(self):
        """First clause
        Every state has at least one color
        """
        str2unq = lambda svar: self.svar_to_uvar[svar]

        for v in self.states:
            self.clauses.append([str2unq(x(v, i)) for i in self.colors])

    def acc_rej_no_same_color(self):
        """Second clause
        Accepting states cannot have the same color as rejecting states
        """

        str2unq = lambda svar: self.svar_to_uvar[svar]

        for i in self.colors:
            for acc_v in self.acc_states:
                self.clauses.append([-1 * str2unq(x(acc_v, i)), str2unq(z(i))])
            for rej_v in self.rej_states:
                self.clauses.append([-1 * str2unq(x(rej_v, i)), -1 * str2unq(z(i))])

    def set_parent_relation(self):
        """Third clause
        A parent relation is set when a state and its parent are colored
        """
        str2unq = lambda svar: self.svar_to_uvar[svar]

        for v in self.states:
            if v == 0:
                continue
            for i in self.colors:
                for j in self.colors:
                    l_v = self.apta.label(v)
                    p_v = self.apta.parent(v)
                    self.clauses.append(
                        [
                            str2unq(y(l_v, i, j)),
                            -1 * str2unq(x(p_v, i)),
                            -1 * str2unq(x(v, i)),
                        ]
                    )

    def parent_must_target_at_most_one_color(self):
        """Fouth clause
        Each parent relation can target at most one color
        """
        str2unq = lambda svar: self.svar_to_uvar[svar]

        for a in self.tokens:
            for h in self.colors:
                for i in self.colors:
                    for j in self.colors:
                        if h >= j:
                            continue
                        self.clauses.append(
                            [-1 * str2unq(y(a, i, h)), -1 * str2unq(y(a, i, j))]
                        )

    def at_most_one_color(self):
        """Fifth clause. First redundant
        Every state has at most one color
        """

    def parent_must_target_at_least_one_color(self):
        """Sixth clause. Second redundant
        Each parent relation must target at least one color
        """

    def parent_color_forces(self):
        """Seventh clause. Third redundant
        A parent relation forces a state once the parent is colored
        """

    def conflicts(self):
        """Eighth clause. Fourth redundant
        All determinization conflicts explicitly added as clauses
        """

    def solve(self, solver_name: str = "g4"):
        """Apply sat solver to get an automaton or False

        Args:
            solver_name (str, optional): Solver used. Defaults to "g4".
            https://pysathq.github.io/docs/html/api/solvers.html#pysat.solvers.SolverNames

        Raises:
            ValueError: If there are no clauses, this is, if there were no construction
            of the problem

        Returns:
            model: _description_
        """
        if len(self.clauses) == 0:
            raise ValueError("No clauses to solve")
        cnf = CNF(from_clauses=self.clauses)
        with Solver(name=solver_name, bootstrap_with=cnf) as solver:
            return solver.get_model() if solver.solve() else None


if __name__ == "__main__":
    pass
