"""Independent finite checks of received 2a117fc; no optimization trajectories."""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform

SHA = "2a117fc0199e437d3b799af8ef899ea30b6b6d16"

def d(q):
    q = F(q)
    return Decimal(q.numerator) / Decimal(q.denominator)

def network(a):
    m, n, mu = len(a), 16, F(1)
    total = m*n
    avg, largest = sum(map(F,a))/m, F(max(a))
    with localcontext() as ctx:
        ctx.prec = 80
        kappa, kmax = d(avg/mu), d(largest/mu)
        b = (d(total)*kmax/kappa).sqrt()
        p = max(1/(2*kappa.sqrt()), kmax/(2*kappa*b))
        qs = [min(Decimal(1), b*d(ai)/(d(total)*d(largest))) for ai in a]
        snapshot = d(total)*p*kappa.sqrt()
        expected = max(d(F(total,2)), (d(total)*kmax).sqrt()/2)
        assert abs(snapshot-expected) <= Decimal('1e-70')
        assert 0 < p <= 1 and all(0 < qi <= 1 for qi in qs)
        samples = 2*d(n)*sum(qs)*kappa.sqrt()
        return dict(m=m,n=n,mu=str(mu),a=a,Lbar=str(avg),Lbar_max=str(largest),
                    b=str(b),p=str(p),sample_cost_scaled=str(samples),
                    snapshot_cost_scaled=str(snapshot),
                    average_target_half_term=str((d(total)*d(avg/mu)).sqrt()/2),
                    interpretation='coefficients on sqrt(kappa) scale; excludes initialization/log factors; not measured runtime')

def lift():
    x,beta = F(1),F(1,4)
    q = [x-beta,2*x-beta]
    z = (q[0]+2*q[1])/5
    residual=[z-q[0],2*z-q[1]]
    assert q == [F(3,4),F(7,4)]
    assert q[1]-2*q[0] == F(1,4)
    assert z==F(17,20) and sum(v*v for v in residual)==F(1,80)
    prox_composite=max(x-3*beta,F(0))
    assert prox_composite==F(1,4)
    return dict(q=[str(v) for v in q],least_squares_point=str(z),
                residual_squared=str(sum(v*v for v in residual)),
                original_composite_prox=str(prox_composite),
                identity_case_has_lift=all(-2<=v<=2 for v in q),
                interpretation='no exact lift for this T; one-dimensional composite prox is cheap, so this is not a research-value witness')

def eigen():
    eigenvalues=[-1,1]; v=[0,1]
    gv=[e*x for e,x in zip(eigenvalues,v)]
    rq=sum(x*y for x,y in zip(v,gv))
    res=sum((y-rq*x)**2 for x,y in zip(v,gv))
    shift=max(-rq,0)
    assert rq==1 and res==0 and min(e+shift for e in eigenvalues)==-1
    return dict(rayleigh=rq,residual_squared=res,rayleigh_shift=shift,
                minimum_after_rayleigh_shift=-1,certified_shift=1,minimum_after_certified_shift=0,
                interpretation='residual of an arbitrary eigenpair is not a lower certificate for the minimum eigenvalue')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=dict(reviewed_sha=SHA,executed_at_utc=datetime.now(timezone.utc).isoformat(),
                python=platform.python_version(),arithmetic='Fraction and Decimal(80)',
                scope='Independent reconstruction of finite algebra/cost examples, not original script rerun, not convergence or novelty certification',
                heterogeneous=network([4096]+[1]*15),uniform=network([4096]*16),
                no_lift=lift(),minimum_eigenvalue=eigen(),passed=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
