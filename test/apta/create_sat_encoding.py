from fakedfasat.apta import APTA
from fakedfasat.sat_encoding import SATEncoding

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
enc = SATEncoding(tree, 5)
# print(enc)
# print(enc.variables)
# print(enc.tokens)
# print(enc.svar_to_uvar)
enc.acc_rej_no_same_color()
print(enc.clauses)
# print(enc.colors)
# print(enc.states)
# print(enc.acc_states)
# print(enc.rej_states)
# print(enc.tokens)
print(enc.solve())
