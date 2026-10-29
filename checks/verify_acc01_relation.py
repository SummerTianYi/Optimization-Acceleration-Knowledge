"""Exact local check of ACC01 (4.1); not an implementation of Algorithm 3.1."""
import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def sqnorm(xs):
    return sum((x * x for x in xs), F(0))


def disagreement(xs):
    mean = sum(xs, F(0)) / len(xs)
    return sqnorm([x - mean for x in xs])


def encoded(value):
    if isinstance(value, F):
        return {"exact": str(value), "decimal": float(value)}
    if isinstance(value, dict):
        return {k: encoded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(v) for v in value]
    return value


def run(cfg):
    sigma, mu, lf, p, pmax, beta = (F(cfg[k]) for k in
        ("sigma", "mu", "Lf", "p", "P", "beta"))
    q = lf / mu
    gap = 1 - sigma * sigma
    alpha = (p / pmax) * gap**2 / (560 * q * lf)
    x = list(map(F, cfg["x0"]))
    previous = list(map(F, cfg["x_previous"]))
    centers = list(map(F, cfg["local_minimizers"]))
    assert len(x) == len(previous) == len(centers) == 2
    assert 0 <= sigma < 1 and 0 < mu < lf
    assert mu == 1 and p == pmax == 1  # the specified quadratic instance
    weights = [[(1 + sigma) / 2, (1 - sigma) / 2],
               [(1 - sigma) / 2, (1 + sigma) / 2]]
    assert all(sum(row) == 1 for row in weights)
    assert all(sum(weights[i][j] for i in range(2)) == 1 for j in range(2))
    # Symmetric eigenvalues are 1 and sigma: exact spectral gate, no eigensolver.
    assert weights[0][0] - weights[0][1] == sigma
    tracker = [x[i] - centers[i] for i in range(2)]
    xnext = [sum(weights[i][j] * x[j] for j in range(2))
             - alpha * tracker[i] + beta * (x[i] - previous[i])
             for i in range(2)]
    c0, c1 = disagreement(x), disagreement(xnext)
    t0, d0 = disagreement(tracker), sqnorm([a - b for a, b in zip(x, previous)])
    extra = 4 * alpha**2 * t0 / gap + 4 * beta**2 * d0 / gap
    printed = gap * c0 / 2 + extra
    derived = (1 + sigma**2) * c0 / 2 + extra
    # Squared bounds avoid square-root rounding, all positive quantities.
    beta_bounds_squared = [
        9 * 47 * gap**2 * p / (56**2 * 34 * pmax),
        1259 * gap**2 * p / (280**2 * 17 * pmax),
        pmax * q**2 * 59 / (p * 1122),
        gap**4 * 69 * p**2 / (560**2 * 68 * pmax**2 * q**2),
    ]
    gates = {
        "alpha_main_statement": alpha < (p / pmax) * gap**2 / (549 * q * lf),
        "alpha_le_1_over_Lf": alpha <= 1 / lf,
        "alpha_le_1_over_4sqrt2Lf_squared": alpha**2 <= 1 / (32 * lf**2),
        "alpha_le_1_over_2mu": alpha <= 1 / (2 * mu),
        "alpha_le_mu_m_over_8Lf_squared": alpha <= mu * 2 / (8 * lf**2),
        "beta_below_all_four_bounds": all(beta**2 < b for b in beta_bounds_squared),
    }
    assert all(gates.values())
    assert c1 == F(32, 25) and printed == F(9, 25) and derived == F(41, 25)
    assert c1 > printed and c1 <= derived
    boundaries = []
    for s_text in cfg["boundary_sigmas"]:
        s = F(s_text)
        if s == 1:
            boundaries.append({"sigma": s, "domain": "excluded: denominator zero; swap matrix",
                               "connected_doubly_stochastic": True, "strict_spectral_gate": False})
            continue
        lhs = s**2 * c0
        minus_rhs = (1 - s**2) * c0 / 2
        plus_rhs = (1 + s**2) * c0 / 2
        boundaries.append({"sigma": s, "domain": "pure mixing",
                           "lhs": lhs, "printed_rhs": minus_rhs,
                           "derived_rhs": plus_rhs, "printed_holds": lhs <= minus_rhs,
                           "derived_holds": lhs <= plus_rhs})
        assert lhs <= plus_rhs
        assert (lhs <= minus_rhs) == (3 * s**2 <= 1)
    threshold_difference = (3 * F(1, 3) - 1) * c0 / 2
    assert threshold_difference == 0
    return encoded({
        "check": "V01", "deterministic": True, "random_seed": None,
        "scope": "one vector-update step with explicit x_previous completion; no full reproduction",
        "W": weights, "mu": mu, "Lf": lf, "Q": q, "alpha": alpha, "beta": beta,
        "beta_upper_bounds_squared": beta_bounds_squared, "parameter_gates": gates,
        "x0": x, "tracker0": tracker, "x1": xnext, "C0": c0, "T0": t0, "D0": d0,
        "lhs": c1, "printed_rhs": printed, "derived_rhs": derived,
        "violation_margin": c1 - printed, "derived_slack": derived - c1,
        "verdict": "printed local relation falsified; full algorithm convergence not decided",
        "boundaries": boundaries, "algebraic_threshold_r": F(1, 3),
        "algebraic_threshold_difference": threshold_difference,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print("V01 exact arithmetic completed; parameter gates satisfied.")
    print("C1=32/25; printed RHS=9/25; derived RHS=41/25.")
    print("Printed relation fails by 23/25. Boundary threshold: sigma^2 <= 1/3.")
    print("sigma=1 excluded; no conclusion about full algorithm divergence or acceleration.")
