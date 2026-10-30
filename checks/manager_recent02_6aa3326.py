"""Independent finite checks for fixed 6aa3326; no optimizer or performance run."""
from __future__ import annotations
import argparse, json, platform
from fractions import Fraction as F
from decimal import Decimal as D, localcontext, ROUND_CEILING
from pathlib import Path


def calculate() -> dict:
    rows=[]
    with localcontext() as ctx:
        ctx.prec=80
        for N,k,kb in [(256,16,4096),(256,1,1),(256,65536,65536),(256,16,16),(1,1,1)]:
            n,a,s=D(N),D(k).sqrt(),(D(N)*D(kb)).sqrt()
            b=min(N,int(max(D(1),n/a,s/a).to_integral_value(rounding=ROUND_CEILING)))
            work=n+D(b)*a+s; depth=n/D(b)+a+s/D(b); target=n+s
            assert work<=2*target+a and depth<=3*a
            rows.append(dict(N=N,kappa=k,kappa_bar=kb,batch=b,work=str(work),depth=str(depth),target=str(target)))
    u=[F(-5,3),F(4,3),F(1,3)]
    diff=[u[1]-u[0],u[2]-u[1]]
    def mcp_prox(s:F) -> F:
        v=abs(s)
        return F(0) if v<=1 else (1 if s>=0 else -1)*(2*(v-1) if v<=2 else v)
    q=list(map(mcp_prox,diff)); c=-(2*q[0]+q[1])/3
    z=[c,c+q[0],c+q[0]+q[1]]
    radius=sum(v*v for v in u); norm=sum(v*v for v in z)
    assert q==[F(3),F(0)] and radius==F(14,3) and norm==6
    # D D^T has determinant 3, so the obstruction is the ball, not surjectivity.
    det_DDT=2*2-(-1)**2
    assert det_DDT==3 and norm-radius==F(4,3)
    lam,top=F(-1),F(2); v=[F(24,25),F(7,25)]
    r=lam*v[0]**2+top*v[1]**2; eta=r-lam; gz=(lam+top)/2
    d=gz+max(-lam,0); dh=gz+max(-(r-eta),0); dd=gz-min(r,0)
    assert r==F(-478,625) and eta==F(147,625) and dd==F(1581,1250)
    assert dd<=d<=dh<=dd+eta and eta<F(1,4) and dd>F(3,4)
    intervals=[]
    for low in [F(-2),F(-1),F(0),F(1)]:
        for width in [F(0),F(1,4),F(2)]:
            for frac in [F(0),F(1,2),F(1)]:
                rr=low+frac*width; GZ=low+2
                a=GZ-min(rr,0); b=GZ+max(-low,0); c=GZ+max(-(rr-width),0)
                assert a<=b<=c<=a+width
                intervals.append([str(low),str(width),str(frac)])
    budget=sum(F(1,j*(j+1)) for j in range(1,101))
    assert budget==F(100,101)
    # Algebra for the B2 proposed inner tolerance: error -> distance -> regret.
    ftrl=[]
    for M in [1,4,16,100]:
        rt=int(M**.5); delta,G=F(2),F(3); alpha=delta/(G*rt)
        e=delta**2/(2*alpha*M)
        assert 2*alpha*e==delta**2/M
        total=delta**2/(2*alpha)+alpha*M*G**2/2+delta*G*rt
        assert total==2*delta*G*rt
        ftrl.append(dict(M=M,alpha=str(alpha),inner_gap=str(e),regret_bound=str(total)))
    return {
      'reviewed_sha':'6aa33260e8f3024a7184ced18c0fa37514ae3d2c',
      'environment':{'python':platform.python_version(),'arithmetic':'80-digit Decimal and Fraction','dependencies':'standard library'},
      'A1_cost_rows':rows,
      'B1':{'u':list(map(str,u)),'q':list(map(str,q)),'minimum_norm_lift':list(map(str,z)),'DDT_determinant':det_DDT,'radius_sq':str(radius),'lift_norm_sq':str(norm),'excess':str(norm-radius)},
      'D1':{'ritz':str(r),'eta':str(eta),'true_gap':str(d),'upper_gap':str(dh),'direction_gap':str(dd),'additional_interval_cases':len(intervals),'failure_budget_partial_sum':str(budget)},
      'B2_ftrl_algebra':ftrl,
      'status':'all finite checks passed',
      'scope':'Independently reconstructed algebra and cost coefficients; no random Lanczos, network algorithm, FRAMES, performance run, new convergence theorem or novelty verification.'
    }

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    data=calculate();args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(data,ensure_ascii=False,indent=2))
