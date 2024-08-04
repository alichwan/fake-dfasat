from src.fakedfasat_Alichwan.apta import APTA

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

for k, v in tree.__dict__.items():
    print(k, v)
