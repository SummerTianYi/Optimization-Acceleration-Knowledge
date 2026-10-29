"""V02 exact, finite smoothing checks. No optimizer and no network or input mutation."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform


def smooth(x, mu):
    if mu <= 0:
        raise ValueError("mu must be positive")
    return abs(x) if abs(x) >= mu else x*x/(2*mu) + mu/2


def grad(x, mu):
    if mu <= 0:
        raise ValueError("mu must be positive")
    return min(Q(1), max(Q(-1), x/mu))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def run(config):
    assertion_count = 0

    def require(test, label):
        nonlocal assertion_count
        assertion_count += 1
        if not test:
            raise AssertionError(label)

    bias = []
    for mu in map(Q, config["mu_grid"]):
        for x in map(Q, config["x_grid"]):
            error = smooth(x, mu) - abs(x)
            require(0 <= error <= mu/2, "uniform one-sided bias")
            bias.append(dict(mu=mu, x=x, smoothed=smooth(x, mu), original=abs(x), error=error, bound=mu/2))
        require(smooth(Q(0), mu) == mu/2, "tight bias at zero")
        for sign in (-1, 1):
            x = sign*mu
            require(x*x/(2*mu)+mu/2 == abs(x) and x/mu == sign, "C1 branch join")
    fixed = []
    for mu in map(Q, config["mu_grid"]):
        for xx, yy in config["fixed_pairs"]:
            x, y = Q(xx), Q(yy)
            d = grad(y, mu)*(y-x) - (smooth(y, mu)-smooth(x, mu))
            dg = grad(y, mu)-grad(x, mu)
            lhs, rhs = dg*dg, 2*d/mu
            require(d >= 0 and lhs <= rhs, "same-parameter convex smooth relation")
            fixed.append(dict(mu=mu, x=x, y=y, D=d, gradient_difference=dg, lhs=lhs, rhs=rhs))

    cases = []
    for row in config["drift_cases"]:
        x, y, mu, nu = (Q(row[key]) for key in ("x", "y", "old_mu", "new_mu"))
        dsame = grad(y, nu)*(y-x)-(smooth(y, nu)-smooth(x, nu))
        dmix = grad(y, nu)*(y-x)-(smooth(y, nu)-smooth(x, mu))
        gsame, gmix = grad(y, nu)-grad(x, nu), grad(y, nu)-grad(x, mu)
        fd, gd = smooth(x, mu)-smooth(x, nu), grad(x, nu)-grad(x, mu)
        require(dmix-dsame == fd, "function drift identity")
        require(gmix-gsame == gd, "gradient drift identity")
        require(abs(fd) <= abs(mu-nu)/2, "parameter Lipschitz bound")
        lsame = gsame**2/(2*dsame) if dsame else None
        lmix = gmix**2/(2*dmix) if dmix else None
        substitution_rhs = 2*lmix*dsame if lmix is not None else None
        substitution_valid = substitution_rhs is not None and gsame**2 <= substitution_rhs
        if row["name"] == "moving_inside":
            require((dsame, gsame, lsame, dmix, gmix, lmix) ==
                    (Q(1,64), Q(1,4), Q(2), Q(15,64), Q(1,2), Q(8,15)), "moving hand derivation")
            require(not substitution_valid and (gsame**2, substitution_rhs) == (Q(1,16), Q(1,60)), "mixed substitution fails")
        elif row["name"] == "same_point_boundary":
            require(dsame == gsame == 0 and dmix == Q(7,32) and lmix == Q(1,7), "zero-movement boundary")
        elif row["name"] == "unchanged_parameter_control":
            require(dsame == dmix and gsame == gmix and lsame == lmix and substitution_valid, "same parameter control")
        else:
            raise ValueError("unrecognized case")
        cases.append(dict(name=row["name"], x=x, y=y, old_mu=mu, new_mu=nu,
                          old_f_at_x=smooth(x,mu), new_f_at_x=smooth(x,nu), new_f_at_y=smooth(y,nu),
                          old_grad_at_x=grad(x,mu), new_grad_at_x=grad(x,nu), new_grad_at_y=grad(y,nu),
                          D_same=dsame, D_mix=dmix, delta_g_same=gsame, delta_g_mix=gmix,
                          function_drift=fd, gradient_drift=gd, L_same=lsame, L_mix=lmix,
                          same_relation_lhs=gsame**2, mixed_substitution_rhs=substitution_rhs,
                          mixed_substitution_valid=substitution_valid))

    pp = config["prox_positive"]
    y, mu, ell = (Q(pp[key]) for key in ("y", "mu", "L"))
    low, high = map(Q, pp["box"])
    p = min(high, max(low, y-mu*grad(y,mu)/ell))
    majorant = smooth(y,mu)+grad(y,mu)*(p-y)+ell*(p-y)**2/(2*mu)
    surrogate_gap, original_gap = smooth(y,mu)-mu/2, abs(y)
    require(smooth(p,mu) <= majorant and abs(p) < abs(y), "positive prox and original descent")
    require(original_gap <= surrogate_gap+mu, "two-sided original certificate")
    require(original_gap <= surrogate_gap+mu/2, "one-sided original certificate")
    positive = dict(y=y, mu=mu, p=p, majorant=majorant, smooth_at_p=smooth(p,mu),
                    original_gap_before=original_gap, original_gap_after=abs(p), surrogate_gap=surrogate_gap,
                    general_gap_bound=surrogate_gap+mu, one_sided_gap_bound=surrogate_gap+mu/2)
    rejected = []
    for function in (smooth, grad):
        try:
            function(Q(0), Q(0))
        except ValueError:
            rejected.append(function.__name__)
    require(len(rejected) == 2, "zero smoothing parameter rejected")

    bb = config["model_boundaries"]
    a, b, lam = (Q(bb[key]) for key in ("A", "b", "lambda"))
    def relu_loss(x):
        return abs(max(a*x, Q(0))-b)+lam*abs(x)
    def max_loss(x):
        return abs(max(2*a*x, -a*x)-b)+lam*abs(x)
    boundaries = []
    for name, function, points, weight in (
        ("relu_nonconvex", relu_loss, bb["relu_points"], Q(1,2)),
        ("max_nonconvex", max_loss, bb["max_points"], Q(bb["max_left_weight"]))):
        left, right = map(Q, points)
        mid = weight*left+(1-weight)*right
        avg = weight*function(left)+(1-weight)*function(right)
        require(-1 <= left <= 1 and -1 <= right <= 1 and function(mid) > avg, name)
        boundaries.append(dict(name=name, left=left, right=right, left_weight=weight, mid=mid,
                               f_left=function(left), f_right=function(right), f_mid=function(mid), weighted_average=avg))
    rr = config["reference_boundary"]
    a, xs, lam, x = (Q(rr[key]) for key in ("A", "generated_x", "lambda", "comparison_x"))
    b = a*xs
    fxs, fx = abs(a*xs-b)+lam*abs(xs), abs(a*x-b)+lam*abs(x)
    require(0 <= x <= 5 and 0 <= xs <= 5 and fx < fxs, "generated reference not optimum")
    return dict(bias_grid=bias, fixed_parameter_pairs=fixed, drift_cases=cases, positive_prox=positive,
                invalid_mu_rejected_by=rejected, model_boundaries=boundaries,
                reference_boundary=dict(A=a, b=b, generated_x=xs, comparison_x=x, f_generated=fxs, f_comparison=fx),
                assertion_count=assertion_count, passed=True, performance_protocols_executed=False)


def encode(value):
    if isinstance(value, Q):
        return str(value)
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.config.read_bytes()
    config = json.loads(raw)
    result = run(config)
    result.update(config=config, executed_at_utc=datetime.now(timezone.utc).isoformat(),
                  environment=dict(python=platform.python_version(), system=platform.system(), arithmetic="Fraction", dependencies="standard library only"),
                  config_sha256=digest(raw), script_sha256=digest(Path(__file__).read_bytes()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2, default=encode)+"\n")
    print(json.dumps(dict(verification="V02", passed=result["passed"], assertions=result["assertion_count"],
                         bias_cases=len(result["bias_grid"]), fixed_pairs=len(result["fixed_parameter_pairs"]),
                         drift_cases=len(result["drift_cases"]), performance_protocols_executed=False)))


if __name__ == "__main__":
    main()
