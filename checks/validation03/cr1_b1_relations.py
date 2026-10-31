"""Closed-form local checks for C-R1 and B1, not full algorithm executions."""
from decimal import Decimal as D, localcontext
import json
from pathlib import Path


def main():
    with localcontext() as ctx:
        ctx.prec = 80
        one = D(1)
        rho, diameter, eps, eps0, decay = one, D(4), D("0.01"), one, D("0.25")
        gp, gd, sigma = eps/(2*diameter), D("0.001"), D("0.25")
        anchor, center, test_multiplier = D("0.5"), one, D("0.7")
        B, tau, lam, nu = D(0), one, D(0), D(0)
        weighted_q, weighted_error = D(0), D(0)
        rows = []
        for k in range(3):
            b = (rho*tau+(rho*rho*tau*tau+4*rho*tau*B).sqrt())/2
            next_B, next_tau = B+b, tau+b*gd
            tilde = (B*lam+b*nu)/next_B
            inner_budget = (7*eps0*decay**k+sigma*rho*eps**2)/8
            r = (one if k % 2 == 0 else -one)*inner_budget/(8*diameter)
            # f(x)=1/2*(x-1)^2, h=indicator[-2,2], A=1, equality x=0.
            x = (center+gp*anchor-tilde+r)/(1+gp+rho)
            next_lam = tilde+rho*x
            next_nu = (tau*nu+b*x)/next_tau
            actual_residual = x-center+gp*(x-anchor)+next_lam
            assert abs(actual_residual-r) < D("1e-75")
            assert abs(r) <= inner_budget/diameter and abs(x) < 2
            # Backsolve the post-gradient point to check the listed inner gate.
            step = 1/(4+gp+inner_budget/(4*diameter**2))
            mapping = r/(1-step*(1+gp+rho))
            assert abs(mapping) <= inner_budget/(2*diameter)
            gap = x*x/2-x  # f(x)-f(0)
            primal_perturbation = gp/2*(anchor**2-(x-anchor)**2-x**2)
            dual_identity = ((test_multiplier-tilde)**2-(test_multiplier-next_lam)**2
                             -(next_lam-tilde)**2)/(2*rho)
            right = r*x+primal_perturbation+dual_identity
            left = gap+test_multiplier*x
            assert left <= right+D("1e-70")
            assert abs(right-left-x*x/2) < D("1e-70")
            cross = b*(next_nu-next_lam)*x
            telescope = (tau*(test_multiplier-nu)**2/2
                         - next_tau*(test_multiplier-next_nu)**2/2
                         - tau*(next_nu-nu)**2/2
                         + b*gd*(test_multiplier**2-next_nu**2)/2 + cross)
            assert abs(telescope-b*(test_multiplier-next_lam)*x) < D("1e-70")
            weighted_q += b*x
            weighted_error += b*abs(r)*diameter
            assert abs(weighted_q-next_tau*next_nu) < D("1e-70")
            rows.append({"k": k, "b": b, "B_next": next_B, "tau_next": next_tau,
                         "tilde_nu": tilde, "x_next": x, "lambda_next": next_lam,
                         "nu_next": next_nu, "inner_budget": inner_budget, "residual": r,
                         "gradient_mapping": mapping, "one_step_lhs": left,
                         "one_step_rhs": right, "uncontrolled_cross": cross,
                         "original_stop_gate": abs(mapping) <= eps/4 and abs(x) <= eps})
            B, tau, lam, nu = next_B, next_tau, next_lam, next_nu
        assert any(row["uncontrolled_cross"] > 0 for row in rows)
        # Separate analytic perturbation-bias example, not an I-FALM run.
        bias_D, bias_gp = D(4), D("0.00125")
        curvature, linear = bias_gp/2, bias_gp*bias_D/4
        minimizer = (bias_gp*bias_D-linear)/(curvature+bias_gp)
        original_gap = linear*minimizer+curvature*minimizer**2/2
        assert minimizer == bias_D/2 and original_gap == 3*bias_gp*bias_D**2/16

        b1_rows = []
        for delta in [D(1)/8, D(1)/64, D(1)/512]:
            # R02 matrix model: one column, U=(-delta/2,delta/2), V=0, Xobs=0.
            # D U=delta; auxiliary q=0; TV dual w=delta/a, with lambda=1,a=2.
            a, w = D(2), delta/2
            v_off_graph = w-delta/a
            true_mcp = 1-delta/a
            actual_gap = true_mcp*(delta+D(2).sqrt())
            assert v_off_graph == 0 and abs(w) <= 1
            assert actual_gap > 1
            b1_rows.append({"delta": delta, "U": [-delta/2, delta/2], "V": D(0),
                            "Xobs": D(0), "auxiliary_q": D(0), "TV_dual_w": w,
                            "primal_coupling_residual": delta, "split_stationarity": D(0),
                            "selected_off_graph_v": v_off_graph, "true_MCP_derivative": true_mcp,
                            "true_original_FW_gap": actual_gap,
                            "distance_to_zero_point": delta/D(2).sqrt(),
                            "zero_point_true_gap": D(0)})
        stable_t, stable_q = D("0.5"), D("0.51")
        stable_difference = abs((1-stable_q/2)-(1-stable_t/2))
        assert stable_difference == abs(stable_q-stable_t)/2
        result = {
            "date": "2026-10-31", "kind": "closed_form_relation_checks_not_performance",
            "decimal_precision": 80,
            "CR1": {"parameters": {"rho": rho, "D": diameter, "eps": eps, "eps0": eps0,
                     "decay": decay, "gamma_p": gp, "gamma_d": gd, "sigma": sigma,
                     "x0": anchor, "f_center": center, "test_multiplier": test_multiplier},
                    "steps": rows, "weighted_feasibility": weighted_q/B,
                    "identity_value": tau*nu/B, "weighted_residual_upper": weighted_error/B,
                    "bias_example": {"D": bias_D, "gamma_p": bias_gp, "f_curvature": curvature,
                                     "f_linear": linear, "regularized_minimizer": minimizer,
                                     "original_gap": original_gap}},
            "B1": {"lambda": 1, "a": 2, "spectral_ball_radius": 1, "cases": b1_rows,
                   "same_sign": {"t": stable_t, "q": stable_q,
                                 "derivative_difference": stable_difference}},
            "assertions": "passed",
            "limits": "Three analytic I-FALM-shaped states and MCP graph checks. "
                      "No complete I-FALM run, activity-identification theorem, or optimizer comparison."}
    Path(__file__).with_name("cr1_b1_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str)+"\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({"assertions": "passed", "CR1_cross_terms": [
        r["uncontrolled_cross"] for r in rows], "bias_gap": original_gap,
        "B1_actual_gaps": [r["true_original_FW_gap"] for r in b1_rows]}, default=str))


if __name__ == "__main__":
    main()
