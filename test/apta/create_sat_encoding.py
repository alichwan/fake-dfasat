from src.fakedfasat_Alichwan.apta import APTA
from src.fakedfasat_Alichwan.sat_encoding import SATEncoding

# example provided by Heule & Verwer (2013)
ex_sample = {
    "pos": [
        [
            "a",
        ],
        ["a", "b", "a", "a"],
        ["b", "b"],
    ],
    "neg": [
        ["a", "b", "b"],
        [
            "b",
        ],
    ],
}

tree = APTA(ex_sample)
print(f"delta: {tree.transitions}")
print(f"acc: {tree.accepting_nodes}")
print(f"rej: {tree.rejecting_nodes}")
enc = SATEncoding(tree, 5)

print(enc.solve().__dict__)
