"""Independent offline reconstruction from exported inputs. Does not import run.py."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def check(ok, what):
    if not ok:
        raise ValueError(what)


def audit(directory, cfg):
    load = lambda name: json.loads((directory/name).read_text(encoding="utf8"))
    d, summary = load("input.json"), load("summary.json")
    with (directory/"trajectory.csv").open(encoding="utf8") as file:
        rows = list(csv.DictReader(file))
    Q, lam, c, probe = [np.array(d[k]) for k in ("Q", "eigenvalues", "c", "probe")]
    X = np.array([[float(row[f"x{j}"]) for j in range(len(c))] for row in rows])
    check(len(X) == summary["steps"] + 1 and np.array_equal(X[0], d["x0"]), "trajectory endpoints")
    def f(x):
        u = Q.T @ (x-c)
        return float(.5*np.dot(lam*u, u))
    def grad(x):
        return Q @ (lam*(Q.T @ (x-c)))
    method = d["method"]
    m,b,g,e,w = [cfg[k] for k in ("m","beta","gamma","eta","omega")]
    t = cfg["t0"] if method == "ACC02" else 1.
    ell = cfg["backtrack_start"]
    y, v = X[0], X[0]
    denom = max(1., f(X[0]))
    counts = {p+"_"+k: 0 for p in ("update","stop","monitor") for k in ("f","g")}
    cache = {}
    def book(x, k, purpose):
        key = x.tobytes()
        if k not in cache.get(key, set()):
            if key not in cache:
                if len(cache) == 8:
                    del cache[next(iter(cache))]
                cache[key] = set()
            cache[key].add(k)
            counts[purpose+"_"+k] += 1
    book(X[0], "f", "stop")
    Eprev = None
    max_step_error = max_curvature_identity = 0.
    eq19 = []
    rejected = 0
    for i, (x,row) in enumerate(zip(X, rows)):
        val = f(x)
        check(int(row["k"])==i and math.isclose(float(row["f"]),val,rel_tol=1e-12,abs_tol=1e-13), "f")
        check(abs(float(row["relative_gap"])-val/denom)<1e-12 and abs(float(row["t"])-t)<1e-10, "rate index")
        if row["monitor_norm"]:
            check(d["monitor"] and math.isclose(float(row["monitor_norm"]),np.linalg.norm(grad(x)),rel_tol=1e-12,abs_tol=1e-13), "monitor")
            book(x, "g", "monitor")
        elif d["monitor"]:
            check(sum(counts.values())==d["budget"], "unexpected monitoring omission")
        check(all(int(row[k])==n for k,n in counts.items()), ("physical calls",directory.name,i))
        if i == len(X)-1:
            break
        check(val/denom>cfg["tolerance"], "continued after success")
        xn = X[i+1]
        nextrow = rows[i+1]
        if method == "ACC02":
            gx = grad(x)
            book(x, "g", "update")
            ref = X[i-1] if i else probe
            if not i:
                book(probe, "f", "update")
                book(probe, "g", "update")
            dx = x-ref
            dg = gx-grad(ref)
            diff = float(gx@dx)-(val-f(ref))
            uu = Q.T @ dx
            exact_D = float(np.dot(lam*uu,uu)/2)
            max_curvature_identity=max(max_curvature_identity,abs(diff-exact_D)/max(1.,abs(f(ref)),abs(val)))
            local = float(dg@dg)/(2*diff) if np.any(dg) else 0.
            if i:
                A=previous_t**2/(t*(t-1))
                B=2*(t-1)/((1+b)*g*t)
                C=(1-w)/(2/B+1/(b*g*(1-e)*A))
                step=min(A*previous_s,B*previous_s,C/local if local else math.inf)
            else:
                step=(1-w)/((2+1/(b*g*(1-e)))*local)
            check(math.isclose(step,float(nextrow["step_used"]),rel_tol=1e-11,abs_tol=1e-15),"three gates")
            # Use the logged step for the coordinate reconstruction after checking it.
            step=float(nextrow["step_used"])
            z=t*x-(t-1)*y-g*t*step*gx
            E=np.dot(z-c,z-c)/2+b*g*g*t*t*step*step*np.dot(gx,gx)/2+g*t*t*step*val
            if Eprev is not None:
                mu=float(np.min(lam))
                residual=(E-Eprev+w*mu*g*step*t*(t-1)*np.dot(dx,dx)/2
                          +mu*g*t*step*np.dot(x-c,x-c)/2+b*e*g*g*previous_t**2*previous_s**2*np.dot(grad(ref),grad(ref))/2)
                eq19.append(float(residual)/max(1.,Eprev))
            Eprev=E
            tn=(m+math.sqrt(m*m+4*t*t))/2
            yn=x-step*gx
            predicted=yn+(t-1)/tn*(yn-y)+(g-1)*t/tn*(yn-x)
            previous_t,previous_s,y,t=t,step,yn,tn
        elif method == "GD":
            book(x, "g", "update")
            predicted=x-grad(x)/d["kappa"]
            check(float(nextrow["step_used"])==1/d["kappa"],"GD step")
        else:
            book(v,"g","update")
            gv=grad(v)
            if method=="Nesterov_backtrack":
                book(v,"f","update")
                trials=int(nextrow["trials"])
                check(1<=trials<=cfg["backtrack_trials"],"trial range")
                for j in range(trials):
                    candidate=v-gv/ell
                    book(candidate,"f","update")
                    change=candidate-v
                    rhs=f(v)+float(gv@change)+ell*float(change@change)/2
                    check((f(candidate)<=rhs)==(j==trials-1),"backtracking decision")
                    if j<trials-1:
                        ell*=cfg["backtrack_factor"]
                        rejected+=1
            else:
                ell=d["kappa"]
            predicted=v-gv/ell
            check(float(nextrow["step_used"])==1/ell,"Nesterov step")
            tn=(1+math.sqrt(1+4*t*t))/2
            v=xn+(t-1)/tn*(xn-x)
            t=tn
        max_step_error=max(max_step_error,float(np.linalg.norm(predicted-xn)))
        book(xn,"f","stop")
    check(max_step_error<1e-11 and max_curvature_identity<1e-12 and max(eq19,default=0.)<1e-11,"trajectory algebra")
    check((f(X[-1])/denom<=cfg["tolerance"])==(summary["status"]=="success"),"terminal gap")
    check(summary["relative_gap"]==float(rows[-1]["relative_gap"]), "summary gap")
    check(summary["calls"]==counts and sum(counts.values())==summary["cost"]<=d["budget"],"end counts")
    check(summary["status"]=="success" or (summary["status"]=="oracle_budget" and summary["cost"]==d["budget"]),"end reason")
    check(rejected==summary["rejected"] and summary["factor_matvecs"]==summary["N_f"]+2*summary["N_g"],"work")
    return dict(rows=len(rows),energy_transitions=len(eq19),max_scaled_eq19=max(eq19,default=None),
                max_update_error=max_step_error,max_scaled_D_error=max_curvature_identity),X


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    cfg=json.loads((args.run/"config.json").read_text(encoding="utf8"))
    cells=json.loads((args.run/"summary.json").read_text(encoding="utf8"))
    results, tracks={},{}
    for cell in cells:
        name=cell["cell"]
        results[name],tracks[name]=audit(args.run/name,cfg)
    fixed=tracks["PSD_10000_Nesterov_fixed"]
    for name in ("monitor","tight_off","tight_on"):
        check(np.array_equal(tracks[name],fixed[:len(tracks[name])]),name+" trajectory or prefix")
    check(np.array_equal(tracks["gd_monitor"],tracks["SPD_100_GD"]), "GD monitor trajectory")
    invalid=json.loads((args.run/"invalid_m.json").read_text(encoding="utf8"))
    check(invalid=={"status":"invalid_step_parameters"}, "invalid m")
    states={c["cell"]:c["status"] for c in cells}
    check(states["zero_start"]=="success" and states["one_call"]==states["tight_on"]=="oracle_budget","edge cases")
    check(len(results)==22 and all(states[f"{k}_{c}_{m}"]=="success" for k in cfg["kinds"] for c in cfg["kappas"] for m in cfg["methods"]), "protocol coverage")
    hashes={str(p.relative_to(args.run).as_posix()):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.run.rglob("*")) if p.is_file()}
    receipt=dict(total_rows=sum(x["rows"] for x in results.values()),cells=results,matching_trajectory_or_prefix=["monitor","tight_off","tight_on","gd_monitor"],sha256=hashes)
    with args.out.open("x",encoding="utf8") as file:
        json.dump(receipt,file,indent=2,allow_nan=False)
        file.write("\n")
    print(receipt["total_rows"],"rows checked")


if __name__=="__main__":
    main()
