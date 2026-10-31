"""Fixed four-node, two-input one-step check; no optimizer/performance run.

Run: python checks/validation03/a2_relation.py
Requires numpy. Scalar Moreau points are found by enumerating exact quadratic
pieces, not by an iterative optimization solver.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import numpy as np


def main():
    # Inputs fixed before execution: path4, W=I-L_path/4, degree2 Chebyshev,
    # spectral upper bound 9/10, radius1, four squared measurements, two scales.
    wf = [[F(3, 4), F(1, 4), F(0), F(0)],
          [F(1, 4), F(1, 2), F(1, 4), F(0)],
          [F(0), F(1, 4), F(1, 2), F(1, 4)],
          [F(0), F(0), F(1, 4), F(3, 4)]]
    bound = F(9, 10)
    pf = [[(2 * sum(wf[i][k]*wf[k][j] for k in range(4))
             - (bound**2 if i == j else 0))/(2-bound**2)
           for j in range(4)] for i in range(4)]
    W, P = np.array(wf, dtype=float), np.array(pf, dtype=float)
    J = np.ones((4, 4))/4
    q = float(bound**2/(2-bound**2))
    assert np.allclose(P.sum(axis=1), 1) and np.allclose(P.sum(axis=0), 1)
    assert np.linalg.norm(P-J, 2) <= q+1e-12
    assert min(min(row) for row in pf) < 0
    rho, lipschitz, t, alpha = 2.0, 2.0, 1/8, 1/20
    measurements = np.array([1/16, 1/4, 9/16, 1.0])
    knots = np.array([-1, -3/4, -1/2, -1/4, 1/4, 1/2, 3/4, 1.0])
    # There is no kink at 0; it is harmless to include as a candidate.
    candidates_at_knots = list(knots) + [0.0]

    def objective(y):
        return float(np.mean(np.abs(y*y-measurements)))

    def prox(z):
        candidates = list(candidates_at_knots)
        for lo, hi in zip(knots[:-1], knots[1:]):
            midpoint = (lo+hi)/2
            coefficient = float(np.mean(np.sign(midpoint*midpoint-measurements)))
            stationary = z/(1+2*t*coefficient)
            candidates.append(min(hi, max(lo, stationary)))
        return min(candidates, key=lambda y: objective(y)+(y-z)**2/(2*t))

    def envelope(z):
        y = prox(float(z))
        return objective(y)+(y-z)**2/(2*t)

    def subgradient(points):
        return 2*points*np.sign(points*points-measurements)

    rho_t = rho/(1-t*rho)
    smooth_t = (1+1/(1-t*rho))/t  # safe bound from prox Lipschitz
    c1 = lipschitz*(2-t*rho)/(1-t*rho)
    c2 = 2*rho*(1+1/(1-t*rho)**2)
    outputs = []
    for scale in [F(1, 4), F(1)]:
        xf = [scale, -scale, scale, scale]
        uf = [sum(pf[i][j]*xf[j] for j in range(4)) for i in range(4)]
        x, u = np.array(xf, float), np.array(uf, float)
        v = np.clip(u, -1, 1)
        xbar = float(np.mean(x))
        disagreement = float(np.linalg.norm(x-xbar))
        gv = subgradient(v)
        next_x = np.clip(v-alpha*gv, -1, 1)
        pv = np.array([prox(z) for z in v])
        s = prox(xbar)
        offset = float(np.linalg.norm(v-xbar))
        lhs = float(np.sum((next_x-pv)**2))
        rhs = (float(np.sum((v-pv)**2)) +
               2*alpha*(4*(rho-1/(2*t))*(xbar-s)**2 +
                        c1*np.sum(np.abs(v-xbar)) + c2*np.sum((v-xbar)**2)) +
               4*lipschitz**2*alpha**2)
        avg_phi_x = float(np.mean([envelope(z) for z in x]))
        avg_phi_v = float(np.mean([envelope(z) for z in v]))
        mixing_cap = avg_phi_x+(rho_t+smooth_t*q*q)*disagreement**2/8
        grad_moreau = (xbar-s)/t
        descent_cap = (avg_phi_x-alpha*(1-2*t*rho)*grad_moreau**2/2 +
                       (rho_t+smooth_t*q*q)*disagreement**2/8 +
                       alpha*c1*q*disagreement/(2*t) +
                       alpha*c2*q*q*disagreement**2/(4*t) +
                       lipschitz**2*alpha**2/(2*t))
        actual_next = float(np.mean([envelope(z) for z in next_x]))
        projection_decreases = all(envelope(vi) <= envelope(ui)+1e-12
                                   for vi, ui in zip(v, u))
        assert offset <= q*disagreement+1e-12
        assert np.max(np.abs(gv)) <= lipschitz+1e-12
        assert lhs <= rhs+1e-10 and avg_phi_v <= mixing_cap+1e-10
        assert actual_next <= descent_cap+1e-10 and projection_decreases
        assert np.linalg.norm(next_x-np.mean(next_x)) <= q*disagreement+2*alpha*lipschitz+1e-12
        outputs.append({
            "input_scale": str(scale), "x_exact": [str(z) for z in xf],
            "raw_mix_exact": [str(z) for z in uf], "raw_mix": u.tolist(),
            "projected_mix": v.tolist(), "projection_mean_drift": float(np.mean(v)-xbar),
            "raw_max_abs_subgradient": float(np.max(np.abs(subgradient(u)))),
            "projected_subgradient": gv.tolist(), "next_x": next_x.tolist(),
            "prox_at_mix": pv.tolist(), "prox_at_original_mean": s,
            "moreau_gradient_at_original_mean": grad_moreau,
            "projection_envelope_nonincrease": projection_decreases,
            "lemma_lhs": lhs, "lemma_rhs": float(rhs),
            "mix_envelope": avg_phi_v, "mix_envelope_upper": mixing_cap,
            "next_envelope": actual_next, "descent_upper": descent_cap,
        })
    assert max(abs(float(z)) for z in outputs[0]["raw_mix"]) < 1
    assert uf[1] == F(131, 119) and outputs[1]["raw_max_abs_subgradient"] > lipschitz
    result = {"date": "2026-10-31", "kind": "finite_one_step_relation_not_performance",
              "graph": "path4", "W_exact": [[str(v) for v in row] for row in wf],
              "P_exact": [[str(v) for v in row] for row in pf],
              "mixing_eigenvalues": np.linalg.eigvalsh(W).tolist(),
              "P_disagreement_norm": float(np.linalg.norm(P-J, 2)), "q_bound": q,
              "radius": 1, "measurements": measurements.tolist(), "rho": rho,
              "local_subgradient_bound": lipschitz, "t": t, "alpha": alpha,
              "rho_t": rho_t, "envelope_smoothness_bound": smooth_t,
              "cases": outputs, "assertions": "passed",
              "limits": "Two fixed scalar data configurations; no general theorem or speed claim."}
    Path(__file__).with_name("a2_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"assertions": "passed", "q": q, "cases": outputs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
