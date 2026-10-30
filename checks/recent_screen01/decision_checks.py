"""Small deterministic decision checks, not algorithm/performance experiments.

Run from repository root: python checks/recent_screen01/decision_checks.py
Uses only the standard library; writes results.json beside this file.
"""
from fractions import Fraction as F
from pathlib import Path
from math import sqrt, isclose
import json
import platform


def cesar_cost(a):
    # f_ij(x) = (a_i*x_1**2+x_2**2)/2, n identical components per node.
    m, n, mu = len(a), 16, 1
    lbar = sum(a) / m
    lmax = max(a)
    kappa = lbar / mu
    b = sqrt(m * n * lmax / lbar)
    p = max(1 / (2 * sqrt(kappa)), lmax / (2 * kappa * b))
    q = [min(1, b * ai / (m * n * lmax)) for ai in a]
    assert 0 < p <= 1 and all(0 < qi <= 1 for qi in q)
    qsum = n * sum(q)
    snapshot = m * n * p * sqrt(kappa)
    expected_snapshot = max(m * n / 2, sqrt(m * n * lmax / mu) / 2)
    assert isclose(snapshot, expected_snapshot, rel_tol=1e-12)
    assert qsum <= b * lbar / lmax + 1e-12
    return dict(m=m, n=n, mu=mu, a=a, L=lbar, Lbar=lbar, Lbar_max=lmax,
                b=b, p=p, sum_q=qsum,
                # These are coefficients scaled by sqrt(kappa), not runtime.
                sampled_gradient_cost_scaled=2*qsum*sqrt(kappa),
                snapshot_cost_scaled=snapshot,
                average_condition_target_scaled=sqrt(m*n*lbar/mu)/2,
                initialization_gradients=m*n)


def lift_check():
    beta, x = F(1, 4), F(1)
    tx = [x, 2*x]
    q = [v-beta for v in tx]  # soft-thresholding, both entries positive
    zls = (q[0]+2*q[1])/5
    residual = [zls-q[0], 2*zls-q[1]]
    distance2 = sum(v*v for v in residual)
    assert q[1]-2*q[0] == F(1,4)
    assert zls == F(17,20) and distance2 == F(1,80)
    direct_prox = max(x-3*beta, F(0))
    assert direct_prox == F(1,4) and -2 <= direct_prox <= 2
    # Boundary with T=I: the same q is feasible in [-2,2]^2 and is a lift.
    return dict(beta=str(beta), x=str(x), C="[-2,2]", T="z -> (z,2z)",
                g="abs(y1)+abs(y2)", q=list(map(str,q)),
                incompatibility_q2_minus_2q1=str(q[1]-2*q[0]),
                least_squares_z=str(zls), residual=list(map(str,residual)),
                residual_squared=str(distance2), direct_composite_prox=str(direct_prox),
                identity_T_box_boundary_has_exact_lift=all(-2 <= v <= 2 for v in q))


def eigen_check():
    # G=diag(-1,1), v=e2; residual zero does not certify the minimum eigenvalue.
    G = [[-1,0],[0,1]]
    v = [0,1]
    gv = [sum(row[j]*v[j] for j in range(2)) for row in G]
    rayleigh = sum(v[j]*gv[j] for j in range(2))
    residual2 = sum((gv[j]-rayleigh*v[j])**2 for j in range(2))
    theta = max(-rayleigh,0)
    assert residual2 == 0 and min(-1+theta,1+theta) == -1
    return dict(G=G, v=v, rayleigh=rayleigh, residual_squared=residual2,
                rayleigh_based_shift=theta, shifted_min_eigenvalue=-1,
                certified_shift=1, certified_shifted_min_eigenvalue=0)


def main():
    result = dict(executed_date="2026-10-31", timezone="Asia/Shanghai",
                  python=platform.python_version(), kind="algebra_and_cost_accounting_only",
                  cesar_heterogeneous=cesar_cost([4096]+[1]*15),
                  cesar_uniform_boundary=cesar_cost([4096]*16),
                  no_lift=lift_check(), eigen_certificate=eigen_check(),
                  assertions="passed")
    out = Path(__file__).with_name("results.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
