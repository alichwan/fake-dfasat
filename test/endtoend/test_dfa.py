import json
from typing import Dict, List

from fakedfasat.fakedfasat import fakedfasat

examples = [
    {"name": "./test/data/50S_5L_0C_20T_5X.json", "min_states": 5},
    {"name": "./test/data/50S_10L_0C_20T_15X.json", "min_states": 4},
    {"name": "./test/data/50S_10L_0C_20T_5X.json", "min_states": 3},
    {"name": "./test/data/50S_5L_0C_5T_5X.json", "min_states": 2},
]


def get_traces_from_json(filename: str) -> Dict[str, List[List[List[str]]]]:
    """Read the traces of a configuration from a json file.

    Args:
        filename (str): string with the file to be parsed

    Returns:
        dict: traces of the form {'pos': [..], 'neg': [..]}.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            traces = json.load(file)
        return traces
    except Exception as e:
        print(e)


def adapt_traces(
    traces_dict: Dict[str, List[List[List[str]]]]
) -> Dict[str, List[List[str]]]:
    new_traces = {}
    for sgn in ["pos", "neg"]:
        alltraces = []
        for trace in traces_dict[sgn]:
            onetrace = []
            for step in trace:
                for unique_element in step:
                    onetrace.append(unique_element)
            alltraces.append(onetrace)
        new_traces[sgn] = alltraces
    return new_traces


def automaton_is_correct(automaton, traces: Dict[str, List[List[str]]]):
    for sgn in ["pos", "neg"]:
        for trace in traces[sgn]:
            label = "pos" if automaton.label(trace) else "neg"
            print(f"sgn: {sgn}, label: {label}")
            if sgn != label:
                print("trace:", trace)
                print("transitions:", automaton.transitions)
                print("accepting:", automaton.accepting_states)
                return False
    return True


for example in examples:
    # example provided by Heule & Verwer (2013)
    ex_sample = get_traces_from_json(example["name"])
    ex_sample = adapt_traces(ex_sample)
    automaton = fakedfasat(ex_sample, lower_boud=2, upper_boud=6)

    if automaton is not None:
        assert len(automaton.states) == example["min_states"]
        assert automaton_is_correct(automaton, ex_sample)
        print(
            f"Example {example['name']} get correctly the {example['min_states']} states"
        )
    else:
        print("F")
