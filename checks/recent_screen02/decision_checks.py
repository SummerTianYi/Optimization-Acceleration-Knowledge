"""Limited algebra checks for candidate decisions; no optimizer or benchmark.

Run: python checks/recent_screen02/decision_checks.py
Writes deterministic, exact-rational results beside this file.
"""
from fractions import Fraction as F
from pathlib import Path
import json
import math


def main():
    # A1: explicit cost coefficients from R34 Th5.2, not iteration measurements.
    inputs = [(256, 16, 4096), (256, 1, 1), (256, 65536, 65536),
              (256, 16, 16), (1, 1, 1)]
    cost_rows = []
    for count, kappa, kbar in inputs:
        assert kappa >= 1 and kappa <= kbar <= count * kappa
        batch = min(count, math.ceil(max(1, count / math.sqrt(kappa),
                                        math.sqrt(count * kbar / kappa))))
        work = count + batch * math.sqrt(kappa) + math.sqrt(count * kbar)
        depth = count / batch + math.sqrt(kappa) + math.sqrt(count * kbar) / batch
        target = count + math.sqrt(count * kbar)
        # Ceiling contributes at most sqrt(kappa) if b is not capped.
        assert work <= 2 * target + math.sqrt(kappa) + 1e-10
        assert depth <= 3 * math.sqrt(kappa) + 1e-10
        cost_rows.append(dict(N=count, kappa=kappa, kbar=kbar, batch=batch,
                              work_coefficient=work, depth_coefficient=depth,
                              target_work_coefficient=target))

    # B1: one-column instance of the literature's MCP trend-filtered model.
    u = [F(-5, 3), F(4, 3), F(1, 3)]
    differences = [u[1] - u[0], u[2] - u[1]]
    lam, a, beta = F(1), F(2), F(1)

    def prox_mcp(value):
        magnitude = abs(value)
        if magnitude <= beta * lam:
            return F(0)
        if magnitude <= a * lam:
            return (1 if value >= 0 else -1) * (magnitude-beta*lam)/(1-beta/a)
        return value

    q = [prox_mcp(t) for t in differences]
    # Every lift is (c,c+q0,c+q0+q1). Mean zero minimizes squared norm.
    c = -(2*q[0]+q[1])/3
    lift = [c, c+q[0], c+q[0]+q[1]]
    radius_sq = sum(t*t for t in u)
    lift_norm_sq = sum(t*t for t in lift)
    assert differences == [3, -1] and q == [3, 0]
    assert radius_sq == F(14, 3) and lift_norm_sq == 6
    assert lift_norm_sq > radius_sq and beta/a < 1
    # Boundary: enlarging the ball to radius sqrt(6) makes this lift feasible.
    assert sum(t*t for t in lift) == 6

    # D1: interval-to-certificate algebra, not a Lanczos execution.
    eig_min, eig_max = F(-1), F(2)
    direction = [F(24, 25), F(7, 25)]
    assert sum(t*t for t in direction) == 1
    ritz = eig_min*direction[0]**2 + eig_max*direction[1]**2
    eta = ritz-eig_min
    trace_gz = (eig_min+eig_max)/2  # Z=I/2, feasible in spectraplex
    true_gap = trace_gz+max(-eig_min, 0)
    certified_gap = trace_gz+max(-(ritz-eta), 0)
    direction_gap = trace_gz-min(ritz, 0)
    tolerance = F(1)
    assert direction_gap <= true_gap <= certified_gap <= direction_gap+eta
    assert eta <= tolerance/4 and certified_gap > tolerance
    assert direction_gap > 3*tolerance/4
    delta_total = sum(F(1, i*(i+1)) for i in range(1, 101))
    assert delta_total == F(100, 101)

    result = {
        'date': '2026-10-31', 'kind': 'algebra_and_cost_accounting_only',
        'A1': {'scope': 'R34 regularized convex subclass only; no performance data',
               'inputs_and_outputs': cost_rows},
        'B1': {'model': 'R02 section 7.2.2 one column MCP differences and spectral ball',
               'u': u, 'differences': differences, 'lambda': lam, 'a': a, 'beta': beta,
               'prox': q, 'radius_squared': radius_sq, 'minimum_norm_lift': lift,
               'lift_squared_norm': lift_norm_sq, 'minimum_lift_excess': lift_norm_sq-radius_sq,
               'boundary_feasible_radius_squared': F(6)},
        'D1': {'matrix_diagonal': [eig_min, eig_max], 'direction': direction,
               'ritz': ritz, 'eta': eta, 'true_gap': true_gap,
               'certified_gap': certified_gap, 'direction_gap': direction_gap,
               'tolerance': tolerance, 'failure_budget_partial_sum_over_delta': delta_total},
        'assertions': 'passed',
        'limits': 'No Lanczos, FRAMES, network optimizer, or performance protocol executed.'}
    out = Path(__file__).with_name('results.json')
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str)+'\n',
                   encoding='utf-8', newline='\n')
    print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == '__main__':
    main()
