"""Exact feasibility checks for row fusion on a spectral-norm ball."""
from fractions import Fraction as F
import json


def squared_norm(vector):
    return sum(x * x for x in vector)


def mean_first_pair(vector):
    mean = (vector[0] + vector[1]) / 2
    return [mean, mean, *vector[2:]]


def strings(values):
    return [str(x) for x in values]


def run():
    # Start with a single column. Only the first difference is set to zero.
    u = [F(3, 8), F(5, 8), F(-1, 4)]
    fixed = mean_first_pair(u)
    shift = squared_norm([x - y for x, y in zip(u, fixed)])
    assert squared_norm(fixed) + shift == squared_norm(u) <= 1
    assert fixed[0] == fixed[1] and fixed[1] != fixed[2]

    # For I_2, average the rows of the first column alone or of both columns.
    e1, e2 = [F(1), F(0)], [F(0), F(1)]
    first = mean_first_pair(e1)
    common = mean_first_pair(e2)
    witness = [F(1), F(1)]

    def rayleigh(col1, col2):
        product = [x * witness[0] + y * witness[1] for x, y in zip(col1, col2)]
        return squared_norm(product) / squared_norm(witness)

    separate = rayleigh(first, e2)
    shared = rayleigh(first, common)
    assert separate == F(5, 4) and shared == 1
    return {
        "arithmetic": "rational", "radius": 1,
        "one_column": {"input": strings(u), "output": strings(fixed),
                       "input_squared_norm": str(squared_norm(u)),
                       "output_squared_norm": str(squared_norm(fixed)),
                       "squared_displacement": str(shift)},
        "two_columns": {"input_columns": [strings(e1), strings(e2)],
                        "column_specific_output": [strings(first), strings(e2)],
                        "common_output": [strings(first), strings(common)],
                        "test_vector": strings(witness),
                        "column_specific_squared_norm_lower_bound": str(separate),
                        "common_squared_norm_on_witness": str(shared)},
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
