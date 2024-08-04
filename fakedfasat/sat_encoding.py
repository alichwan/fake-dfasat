from typing import Iterable, List

from pysat.formula import CNF
from pysat.solvers import Solver

from fakedfasat.apta import APTA
from fakedfasat.dfa import DFA


def x(v, i):
    return f"x_[{v},{i}]"


def y(a, i, j):
    return f"y_[{a},{i},{j}]"


def z(i):
    return f"z_[{i}]"


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
        self.conflict_edges = None  # E, from the consistency graph. Redundant clasuses

        # Variables
        self.x_vars = self._gen_x_vars(self.states, self.colors)
        self.y_vars = self._gen_y_vars(self.tokens, self.colors)
        self.z_vars = self._gen_z_vars(self.colors)
        self.variables = self.x_vars + self.y_vars + self.z_vars
        # Creating mapping between string variables and unique variables
        self.uvar_to_svar = {k: v for (k, v) in enumerate(self.variables, start=1)}
        self.svar_to_uvar = {v: k for k, v in self.uvar_to_svar.items()}

        self.clauses = []
        # # minimal clauses
        self.at_least_one_color()  # clause 1
        self.acc_rej_no_same_color()  # clause 2
        self.set_parent_relation()  # clause 3
        self.parent_must_target_at_most_one_color()  # clause 4
        # # redundant clauses
        # self.at_most_one_color()  # clause 5
        # self.parent_must_target_at_least_one_color()  # clause 6
        # self.parent_color_forces()  # clause 7
        # self.conflicts()  # clause 8 # TODO: need the conflict graph

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
                            -1 * str2unq(x(v, j)),
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
                        if h < j:
                            self.clauses.append(
                                [-1 * str2unq(y(a, i, h)), -1 * str2unq(y(a, i, j))]
                            )

    def at_most_one_color(self):
        """Fifth clause. First redundant
        Every state has at most one color
        """
        str2unq = lambda svar: self.svar_to_uvar[svar]

        for v in self.states:
            for i in self.colors:
                for j in self.colors:
                    if i < j:
                        self.clauses.append(
                            [-1 * str2unq(x(v, i)), -1 * str2unq(x(v, j))]
                        )

    def parent_must_target_at_least_one_color(self):
        """Sixth clause. Second redundant
        Each parent relation must target at least one color
        """
        str2unq = lambda svar: self.svar_to_uvar[svar]

        for a in self.tokens:
            for i in self.colors:
                self.clauses.append([str2unq(y(a, i, j)) for j in self.colors])

    def parent_color_forces(self):
        """Seventh clause. Third redundant
        A parent relation forces a state once the parent is colored
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
                            -1 * str2unq(y(l_v, i, j)),
                            -1 * str2unq(x(p_v, i)),
                            str2unq(x(v, j)),
                        ]
                    )

    def conflicts(self):
        """Eighth clause. Fourth redundant
        All determinization conflicts explicitly added as clauses

        TODO: implement the conflict graph and take the edges as a base for construct
        the clauses.
        """

    def decode_literal(self, literal: int):
        """Decode the literal and get the information

        Args:
            literal (int): literal that return pysat solver

        Raises:
            ValueError: If the literal cannot be assigned to a known variable type

        Returns:
            Dict[str, Union(str, int, bool)]: Informationabout the variable associated
            with the input literal
        """
        is_true = literal > 0
        idx = abs(literal)
        str_var = self.uvar_to_svar[idx]
        var_type, var_info = str_var.split("_")
        var_info = var_info.strip("[]").split(",")
        if var_type == "x":  # mapping from v to i
            var_state, var_color = var_info
            return {
                "var_type": var_type,
                "is_true": is_true,
                "var_state": int(var_state),
                "var_color": int(var_color),
            }
        elif var_type == "y":  # transition from i to j reading token a
            var_token, var_color1, var_color2 = var_info
            return {
                "var_type": var_type,
                "is_true": is_true,
                "var_token": var_token,
                "var_color1": int(var_color1),
                "var_color2": int(var_color2),
            }
        elif var_type == "z":  # accepting states
            var_color = var_info[0]
            return {
                "var_type": var_type,
                "is_true": is_true,
                "var_color": int(var_color),
            }
        else:
            raise ValueError(f"Var type non existent: {str_var} (literal: {literal})")

    def decode_model(self, model: List[int]) -> DFA:
        """Takes the output model of the solver and re-transforms it into an dfa

        Args:
            model (List[int]): _description_

        Returns:
            DFA: Automaton tobe returned
        """
        true_vars = {
            "x": [],
            "y": [],
            "z": [],
        }
        for literal in model:
            literal_info = self.decode_literal(literal)
            if literal_info["is_true"]:
                true_vars[literal_info["var_type"]].append(literal_info)

        states = {xvar["var_color"] for xvar in true_vars["x"]}
        acc_states = {zvar["var_color"] for zvar in true_vars["z"]}
        alphabet = {yvar["var_token"] for yvar in true_vars["y"]}
        transitions = {
            (yvar["var_color1"], yvar["var_token"]): yvar["var_color2"]
            for yvar in true_vars["y"]
        }
        initial_state = [
            xvar for xvar in true_vars["x"] if xvar["var_state"] == self.apta.root
        ][0]["var_color"]

        return DFA(
            states=states,
            alphabet=alphabet,
            initial_state=initial_state,
            transitions=transitions,
            accepting_states=acc_states,
        )

    def solve(self, solver_name: str = "g4") -> DFA:
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
            if solver.solve():
                model = solver.get_model()
            else:
                return None
        return self.decode_model(model)


if __name__ == "__main__":
    pass
