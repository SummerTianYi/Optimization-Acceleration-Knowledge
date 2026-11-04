"""Small reproduction adapted from the independent audit's run_tests.py (see README)."""
import argparse
import csv
import json
import math
import platform
from pathlib import Path

import numpy as np


METHODS = ("ACC02", "GD", "Nesterov_fixed", "Nesterov_backtrack")
ROLES = ("update", "stop", "monitor")


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf8")


def validate(cfg):
    m, t, b, g, e, w = [cfg[k] for k in ("m", "t0", "beta", "gamma", "eta", "omega")]
    if not (0 < m < 1 and t >= 1 and b > 0 and 0 < g < 2 and 0 <= e < 1 and 0 <= w < 1
            and (1 + b) * g / 2 <= (2 * (t - 1) + m) / (2 * t + m)):
        raise ValueError("invalid_step_parameters")
    if (cfg["dimension"] < 5 or cfg["budget"] < 1 or not 0 < cfg["tolerance"] < 1
            or cfg["backtrack_start"] <= 0 or cfg["backtrack_factor"] <= 1
            or cfg["backtrack_trials"] < 1):
        raise ValueError("invalid_experiment_parameters")


class Oracle:
    """FIFO point cache shared by all purposes; only physical f/g calls cost."""
    def __init__(self, Q, lam, c, budget):
        self.Q, self.lam, self.c, self.budget = Q, lam, c, budget
        self.cache = {}
        self.count = {role + "_" + kind: 0 for role in ROLES for kind in ("f", "g")}
        self.hits = {role: 0 for role in ROLES}

    def get(self, x, kind, role):
        key = x.tobytes()
        if kind in self.cache.get(key, {}):
            self.hits[role] += 1
            return self.cache[key][kind]
        if sum(self.count.values()) >= self.budget:
            raise ArithmeticError("oracle_budget")
        u = self.Q.T @ (x - self.c)
        value = float(.5 * np.dot(self.lam * u, u)) if kind == "f" else self.Q @ (self.lam * u)
        self.count[role + "_" + kind] += 1
        if not np.all(np.isfinite(value)):
            raise ArithmeticError("nonfinite_oracle")
        if key not in self.cache:
            if len(self.cache) == 8:
                self.cache.pop(next(iter(self.cache)))
            self.cache[key] = {}
        self.cache[key][kind] = value
        return value


def curvature(x, f, g, old, old_f, old_g):
    dg = g - old_g
    norm_sq = float(dg @ dg)
    if norm_sq == 0:
        return 0.
    D = float(g @ (x - old)) - (f - old_f)
    if not D > 0:
        raise ArithmeticError("nonpositive_D")
    return norm_sq / (2 * D)


def run_cell(root, name, cfg, kind, kappa, method, monitor=False, budget=None, zero=False, inputs=None):
    if kind not in ("SPD", "PSD") or kappa < 1 or method not in METHODS:
        raise ValueError("invalid_model_or_method")
    n = cfg["dimension"]
    if inputs is None:
        v = np.arange(1, n + 1, dtype=float)
        Q = np.eye(n) - 2 * np.outer(v, v) / np.dot(v, v)
        c = np.array([(-1.) ** j / 4 for j in range(n)])
        nullity = 0 if kind == "SPD" else 3
        rank = n - nullity
        lam = np.r_[np.zeros(nullity), np.power(float(kappa), np.arange(rank) / (rank - 1))]
        x, probe = np.ones(n), np.zeros(n)
    else:
        Q, c, x, probe = [np.asarray(inputs[k], dtype=float) for k in ("Q", "c", "x0", "probe")]
        lam = np.asarray(inputs["spectra"][f"{kind}_{kappa:g}"], dtype=float)
        if (Q.shape != (n,n) or any(v.shape != (n,) for v in (c,x,probe,lam))
                or not all(np.all(np.isfinite(v)) for v in (Q,c,x,probe,lam))
                or not np.allclose(Q.T @ Q, np.eye(n), rtol=0, atol=1e-12)
                or np.any(lam < 0) or max(lam) != kappa
                or np.count_nonzero(lam == 0) != (0 if kind == "SPD" else 3)
                or min(lam[lam > 0]) != 1):
            raise ValueError("incompatible_quadratic_inputs")
    if zero:
        x = c.copy()
    y, extrap = x.copy(), x.copy()
    budget = cfg["budget"] if budget is None else budget
    if not isinstance(budget, int) or budget < 1:
        raise ValueError("invalid_cell_budget")
    oracle = Oracle(Q, lam, c, budget)
    d = root / name
    d.mkdir()
    save(d / "input.json", dict(kind=kind, kappa=kappa, method=method, monitor=monitor, budget=budget,
                                x0=x.tolist(), probe=probe.tolist(), Q=Q.tolist(),
                                c=c.tolist(), eigenvalues=lam.tolist(), f_star=0,
                                knows_L=method in ("GD", "Nesterov_fixed")))
    keys = ["k", "f", "relative_gap", "step_used", "t", "trials", "monitor_norm", *oracle.count,
            *[f"x{j}" for j in range(n)]]
    m, b, g, e, w = [cfg[k] for k in ("m", "beta", "gamma", "eta", "omega")]
    M = (1 - w) / (2 + 1 / (b * g * (1 - e)))
    k, total_trials, rejected = 0, 0, 0
    t = cfg["t0"] if method == "ACC02" else 1.
    ell = cfg["backtrack_start"]
    used, trials, monitor_norm = None, 0, None
    status = "running"
    with (d / "trajectory.csv").open("w", encoding="utf8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        try:
            f = oracle.get(x, "f", "stop")
            denom = max(1., f)
            while True:
                ratio = f / denom
                success = ratio <= cfg["tolerance"]
                monitor_norm = None
                if monitor and (sum(oracle.count.values()) < budget or "g" in oracle.cache.get(x.tobytes(), {})):
                    monitor_norm = float(np.linalg.norm(oracle.get(x, "g", "monitor")))
                writer.writerow(dict(k=k, f=f, relative_gap=ratio, step_used=used, t=t, trials=trials,
                                     monitor_norm=monitor_norm, **oracle.count,
                                     **{f"x{j}": float(a) for j, a in enumerate(x)}))
                if success:
                    status = "success"
                    break
                trials = 0
                if method == "ACC02":
                    grad = oracle.get(x, "g", "update")
                    if k == 0:
                        fp = oracle.get(probe, "f", "update")
                        gp = oracle.get(probe, "g", "update")
                        local = curvature(x, f, grad, probe, fp, gp)
                        if not local:
                            raise ArithmeticError("degenerate_initial_probe")
                        s = M / local
                    else:
                        local = curvature(x, f, grad, old, old_f, old_g)
                        A = old_t**2 / (t * (t - 1))
                        B = 2 * (t - 1) / ((1 + b) * g * t)
                        C = (1 - w) / (2 / B + 1 / (b * g * (1 - e) * A))
                        s = min(A * used, B * used, C / local if local else math.inf)
                    tn = (m + math.sqrt(m*m + 4*t*t)) / 2
                    yn = x - s * grad
                    xn = yn + (t - 1) / tn * (yn - y) + (g - 1) * t / tn * (yn - x)
                    old, old_f, old_g, old_t = x, f, grad, t
                    next_y, next_t, step = yn, tn, s
                elif method == "GD":
                    step = 1 / kappa
                    xn = x - oracle.get(x, "g", "update") / kappa
                    next_t = t
                else:
                    gv = oracle.get(extrap, "g", "update")
                    if method == "Nesterov_backtrack":
                        fv = oracle.get(extrap, "f", "update")
                        for trials in range(1, cfg["backtrack_trials"] + 1):
                            xn = extrap - gv / ell
                            candidate_f = oracle.get(xn, "f", "update")
                            total_trials += 1
                            dx = xn - extrap
                            if candidate_f <= fv + float(gv @ dx) + ell * float(dx @ dx) / 2:
                                break
                            rejected += 1
                            ell *= cfg["backtrack_factor"]
                        else:
                            raise ArithmeticError("trial_limit")
                    else:
                        ell = kappa
                        xn = extrap - gv / ell
                    step = 1 / ell
                    next_t = (1 + math.sqrt(1 + 4*t*t)) / 2
                    next_extrap = xn + (t - 1) / next_t * (xn - x)
                if not np.all(np.isfinite(xn)) or np.linalg.norm(xn) > 1e12:
                    raise ArithmeticError("invalid_iterate")
                fn = oracle.get(xn, "f", "stop")
                if method == "ACC02":
                    y = next_y
                elif method != "GD":
                    extrap = next_extrap
                x, f, used, t, k = xn, fn, step, next_t, k + 1
        except ArithmeticError as err:
            status = str(err)
    nf = sum(oracle.count[role+"_f"] for role in ROLES)
    ng = sum(oracle.count[role+"_g"] for role in ROLES)
    summary = dict(cell=name, status=status, steps=k, f=f, relative_gap=f/denom, N_f=nf, N_g=ng,
                   cost=nf+ng, factor_matvecs=nf+2*ng, prox=0, trials=total_trials, rejected=rejected,
                   calls=oracle.count, cache_hits=oracle.hits)
    save(d / "summary.json", summary)
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--inputs", type=Path, help="explicit quadratic factors; otherwise generate from config")
    args = p.parse_args()
    inputs = json.loads(args.inputs.read_text(encoding="utf8")) if args.inputs else None
    cfg = json.loads(args.config.read_text(encoding="utf8"))
    validate(cfg)
    args.out.mkdir(parents=True, exist_ok=False)
    save(args.out/"config.json", cfg)
    save(args.out/"environment.json", dict(python=platform.python_version(), numpy=np.__version__))
    results = []
    for kind in cfg["kinds"]:
        for kappa in cfg["kappas"]:
            for method in cfg["methods"]:
                results.append(run_cell(args.out, f"{kind}_{kappa}_{method}", cfg, kind, kappa, method, inputs=inputs))
    for case in cfg["sensitivity"]:
        results.append(run_cell(args.out, cfg=cfg, inputs=inputs, **case))
    cases = {"zero_start": {"zero": True}, "one_call": {"budget": 1}}
    for case in cfg["boundaries"]:
        if case == "invalid_m":
            try:
                validate(dict(cfg, m=0))
            except ValueError as err:
                save(args.out/"invalid_m.json", dict(status=str(err)))
            else:
                raise RuntimeError("invalid m accepted")
        else:
            results.append(run_cell(args.out, case, cfg, "SPD", 100, "ACC02", inputs=inputs, **cases[case]))
    save(args.out/"summary.json", results)
    for result in results:
        print(result["cell"], result["status"], result["steps"], result["N_f"], result["N_g"])


if __name__ == "__main__":
    main()
