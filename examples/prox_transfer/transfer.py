"""Exact small Huber/L1 transfer exercise. Python standard library only."""
import argparse
from fractions import Fraction as R
import json
from pathlib import Path


def soft(v, threshold):
    return max(v-threshold, 0) + min(v+threshold, 0)


def huber(r, mu):
    return r*r/(2*mu) if abs(r)<=mu else abs(r)-mu/2


def solve(cfg, mu):
    b = [R(str(i)) for i in cfg["b"]]
    lam, target = R(str(cfg["lambda"])), R(str(cfg["original_gap_target"]))
    x = [R(str(i)) for i in cfg["x0"]]
    if not (0 < lam < 1 and mu > 0 and len(x) == len(b) == 3):
        raise ValueError("incompatible transfer problem")
    ref = [soft(v,lam*mu) for v in b]
    best = lam*sum(map(abs,b))
    def values(point):
        g = lam*sum(map(abs,point))
        return (sum(abs(v-u) for v,u in zip(point,b))+g,
                sum(huber(v-u,mu) for v,u in zip(point,b))+g)
    _, smooth_best = values(ref)
    first = None
    trace = []
    status = "budget"
    for k in range(cfg["max_updates"]+1):
        f, fm = values(x)
        gap, sgap = f-best, fm-smooth_best
        gradient = [max(-1,min(1,(v-u)/mu)) for v,u in zip(x,b)]
        z = [soft(v-mu*p,mu*lam) for v,p in zip(x,gradient)]
        residual=max(abs(v-u)/mu for v,u in zip(x,z))
        if not (0<=gap<=sgap+len(b)*mu/2 and sgap>=0):
            raise ArithmeticError("invalid error decomposition")
        if first is None and gap<=target:
            first=k
        trace.append(dict(k=k,x=list(map(str,x)),original_gap=str(gap),surrogate_gap=str(sgap),
                          prox_mapping_inf=str(residual)))
        if residual==0:
            exact_gap=(1-lam)*sum(min(abs(v),lam*mu) for v in b)
            if x!=ref or gap!=exact_gap or sgap!=0:
                raise ArithmeticError("closed-form certificate mismatch")
            status="fixed_point"
            break
        if k<cfg["max_updates"]:
            x=z
    return dict(mu=str(mu),status=status,accepted_updates=k,gradient_evaluations=k+1,
                prox_evaluations=k+1,output_evaluations_each_objective=k+1,
                first_original_target=first,terminal=trace[-1],trace=trace)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    cfg=json.loads(args.config.read_text(encoding="utf8"))
    results=[solve(cfg,R(str(mu))) for mu in cfg["mu"]]
    with args.out.open("x",encoding="utf8") as out:
        json.dump(results,out,indent=2)
        out.write("\n")
    for cell in results:
        print(cell["mu"],cell["status"],cell["accepted_updates"],cell["first_original_target"],cell["terminal"])


if __name__=="__main__":
    main()
