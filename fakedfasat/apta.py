from typing import Dict, List, Tuple


class APTA:
    """Transform the incoming examples of labeled traces into an augmented prefix tree
    acceptor (APTA)
    """

    def __init__(self, traces: Dict[str, List[str]]):
        """Here we assume that a set of labeled traces is a dictionary to separate
        positives traces from the negatives.

        Args:
            traces (Dict[str, List[str]]): Set of example labeled traces.
        """
        self.traces = traces
        self.alphabet = set(
            [
                letter
                for sgn in ["pos", "neg"]
                for trace in traces[sgn]
                for letter in trace
            ]
        )
        self.root = 0
        self.nodes = {
            0,
        }
        self.transitions = dict()
        self.accepting_nodes = set()
        self.rejecting_nodes = set()

        self._generate()

    def _generate(self):
        """Compute the actual tree based in the structure of this and the given traces"""
        for sgn in ["pos", "neg"]:
            for trace in self.traces[sgn]:
                current_node = self.root
                for symbol in trace:
                    next_node = self.transitions.get((current_node, symbol))
                    if next_node is None:
                        next_node = len(self.nodes)
                        self.nodes.add(next_node)
                        self.transitions[(current_node, symbol)] = next_node
                    current_node = next_node

                if sgn == "pos":
                    self.accepting_nodes.add(current_node)
                else:
                    self.rejecting_nodes.add(current_node)

    def label_trace(self, trace):
        """Return the label of a trace

        Args:
            trace (list): Given trace to be processed
        """
        print(trace)  # process trace TODO
        return "pos"

    def parent(self, node: int) -> int:
        """Get the parent of the node

        Args:
            node (int): input node
        """
        return self.parent_label(node)[0]

    def label(self, node: int) -> str:
        """Get the needed label to reach the input node from their parent

        Args:
            node (int): input node

        Returns:
            str: label
        """
        return self.parent_label(node)[1]

    def parent_label(self, node: int) -> Tuple[int, str]:
        """Get the parent of he input node and the label needed to reach it

        Args:
            node (int): input node
        """
        reversed_transitions = {v: k for k, v in self.transitions.items()}
        return reversed_transitions.get(node, (None, None))


if __name__ == "__main__":
    pass
