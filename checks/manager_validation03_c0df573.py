"""Independent finite/algebra review of c0df573. Not an optimizer or novelty test."""
from __future__ import annotations
from fractions import Fraction as F
from decimal import Decimal as D, localcontext, ROUND_CEILING
from pathlib import Path
import argparse, json, platform
import numpy as np
import sympy as sp


def run():
    # A1: analytic quadratic instance of the conditional contraction argument.
    H, opt, start, mu = [F(1), F(9)], [F(2), F(-1)], [F(0), F(3)], F(1)
    z = [(h*a+mu*b/4)/(h+mu/4) for h,a,b in zip(H,opt,start)]
    end = [(a+b)/2 for a,b in zip(z,start)]
    gap = lambda x: sum(h*(u-v)**2/2 for h,u,v in zip(H,x,opt))
    Q = lambda x: gap(x)+mu*sum((u-v)**2 for u,v in zip(x,start))/8
    assert Q(end)-Q(z) == (Q(start)-Q(z))/4
    assert gap(end) <= gap(start)/2
    a1 = {'initial_gap':str(gap(start)), 'final_gap':str(gap(end)),
          'ratio':str(gap(end)/gap(start)), 'Q_contraction':'1/4',
          'scope':'one exact quadratic witness; general contraction also checked by inequalities'}
    budgets = []
    with localcontext() as ctx:
        ctx.prec=80
        for N in (1,16,256):
            for k in (1,16,65536):
                for ratio in sorted(set((F(1), F(N+1,2), F(N)))):
                    kp=D(4*k); kb=kp*D(ratio.numerator)/D(ratio.denominator)
                    s=(D(N)*kb).sqrt()
                    b=min(N,int(max(D(1),D(N)/kp.sqrt(),s/kp.sqrt()).to_integral_value(rounding=ROUND_CEILING)))
                    work=D(N)+D(b)*kp.sqrt()+s
                    depth=D(N)/D(b)+kp.sqrt()+s/D(b)
                    assert work<=2*(D(N)+s)+kp.sqrt()+D('1e-60')
                    assert depth<=3*kp.sqrt()+D('1e-60')
                    budgets.append({'N':N,'kappa':k,'kbar_over_kappa':str(ratio),'batch':b})
    # A2: reconstruct mixing and scalar Moreau proximal points independently.
    Wf=[[F(3,4),F(1,4),F(0),F(0)],[F(1,4),F(1,2),F(1,4),F(0)],
        [F(0),F(1,4),F(1,2),F(1,4)],[F(0),F(0),F(1,4),F(3,4)]]
    bnd=F(9,10)
    Pf=[[(2*sum(Wf[i][k]*Wf[k][j] for k in range(4))-(bnd*bnd if i==j else 0))/(2-bnd*bnd) for j in range(4)] for i in range(4)]
    P=np.array(Pf,dtype=float); q=float(bnd*bnd/(2-bnd*bnd))
    assert np.linalg.norm(P-np.ones((4,4))/4,2)<=q+1e-12
    rho,L,t,alpha=2.,2.,.125,.05
    measurement=np.array([1/16,1/4,9/16,1.])
    breaks=sorted(set([-1.,1.]+list(np.sqrt(measurement))+list(-np.sqrt(measurement))))
    obj=lambda x:float(np.mean(np.abs(x*x-measurement)))
    def prox(anchor):
        pts=list(breaks)
        for lo,hi in zip(breaks[:-1],breaks[1:]):
            curvature=float(np.mean(np.sign(((lo+hi)/2)**2-measurement)))
            pts.append(float(np.clip(anchor/(1+2*t*curvature),lo,hi)))
        return min(pts,key=lambda x:obj(x)+(x-anchor)**2/(2*t))
    env=lambda x:obj(prox(x))+(x-prox(x))**2/(2*t)
    c1=L*(2-t*rho)/(1-t*rho); c2=2*rho*(1+(1-t*rho)**-2)
    rt=rho/(1-t*rho); Mt=(1+(1-t*rho)**-1)/t
    a2=[]
    for scale in [F(1,4),F(1)]:
        xf=[scale,-scale,scale,scale]
        uf=[sum(Pf[i][j]*xf[j] for j in range(4)) for i in range(4)]
        x=np.array(xf,float); u=np.array(uf,float); v=np.clip(u,-1,1)
        mean=x.mean(); e=np.linalg.norm(x-mean); g=2*v*np.sign(v*v-measurement)
        nxt=np.clip(v-alpha*g,-1,1); ps=np.array([prox(z) for z in v]); p0=prox(mean)
        h0=np.mean([env(z) for z in x]); hv=np.mean([env(z) for z in v]); hn=np.mean([env(z) for z in nxt])
        lhs=np.sum((nxt-ps)**2)
        rhs=np.sum((v-ps)**2)+2*alpha*(4*(rho-1/(2*t))*(mean-p0)**2+c1*np.sum(abs(v-mean))+c2*np.sum((v-mean)**2))+4*L*L*alpha*alpha
        cap=h0+(rt+Mt*q*q)*e*e/8
        descent=cap-alpha*(1-2*t*rho)*((mean-p0)/t)**2/2+alpha*c1*q*e/(2*t)+alpha*c2*q*q*e*e/(4*t)+L*L*alpha*alpha/(2*t)
        assert lhs<=rhs+1e-10 and hv<=cap+1e-10 and hn<=descent+1e-10
        assert all(env(a)<=env(b)+1e-12 for a,b in zip(v,u))
        assert np.linalg.norm(nxt-nxt.mean())<=q*e+alpha*2*L+1e-12
        a2.append({'scale':str(scale),'raw_mix':[str(z) for z in uf], 'mean_drift':float(v.mean()-mean),
                   'A22_slack':float(rhs-lhs),'A24_slack':float(cap-hv),'A25_slack':float(descent-hn),
                   'raw_second':str(uf[1]),'local_bound_after_projection':float(np.max(abs(g)))})
    assert a2[1]['raw_second']=='131/119'
    # C.5: exact symbolic identity for scalar coordinates; summation yields vector version.
    tau,b,gd,qv,nu,ell,lp=sp.symbols('tau b gd q nu ell lp', real=True)
    tn=tau+b*gd; nn=(tau*nu+b*qv)/tn
    telesc=tau*(ell-nu)**2/2-tn*(ell-nn)**2/2-tau*(nn-nu)**2/2+b*gd*(ell**2-nn**2)/2+b*(nn-lp)*qv
    symbolic=sp.factor(telesc-b*(ell-lp)*qv)
    assert symbolic==0
    cr=[]; mcp=[]
    with localcontext() as ctx:
        ctx.prec=80
        eps=D('.01'); diameter=D(4); gp=eps/(2*diameter); gd=D('.001'); sig=D('.25')
        rho=D(1); B=D(0); tau=D(1); lam=D(0); nu=D(0); anchor=D('.5'); test=D('.7'); cumulative=D(0)
        for k in range(3):
            w=(rho*tau+(rho*rho*tau*tau+4*rho*tau*B).sqrt())/2
            BN=B+w; TN=tau+w*gd; vt=(B*lam+w*nu)/BN
            budget=(7*D('.25')**k+sig*rho*eps**2)/8
            r=(1 if k%2==0 else -1)*budget/(8*diameter)
            point=(1+gp*anchor-vt+r)/(1+gp+rho)
            ln=vt+rho*point; nn=(tau*nu+w*point)/TN
            lhs=point**2/2-point+test*point
            rhs=r*point+gp*(anchor**2-(point-anchor)**2-point**2)/2+((test-vt)**2-(test-ln)**2-(ln-vt)**2)/(2*rho)
            cross=w*(nn-ln)*point
            assert abs((rhs-lhs)-point**2/2)<D('1e-70')
            cumulative+=w*point
            assert abs(cumulative-TN*nn)<D('1e-70')
            cr.append({'k':k,'gap_slack':str(rhs-lhs),'cross_term':str(cross)})
            B,tau,lam,nu=BN,TN,ln,nn
        assert D(cr[1]['cross_term'])>0 and D(cr[2]['cross_term'])>0
        bias=3*gp*D(4)**2/16
        assert bias==D('.00375')
        for delta in (D(1)/8,D(1)/64,D(1)/512):
            true=1-delta/2; gap=true*(delta+D(2).sqrt())
            assert gap>1
            mcp.append({'delta':str(delta),'true_gap':str(gap),'distance_to_zero':str(delta/D(2).sqrt())})
    return {'reviewed_sha':'c0df5732da2ae72d16380824854ca26e147b27b0',
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'sympy':sp.__version__, 'arithmetic':'Fraction, float64 and 80-digit Decimal'},
            'A1':a1,'A1_budget_cases':budgets,'A2':a2,'C5_symbolic_difference':str(symbolic),'CR1':cr,
            'bias_gap':str(bias),'B1':mcp,'passed':True,
            'limits':'Finite relations and one symbolic identity only; no general convergence proof, novelty assessment by code, or performance run.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=run();a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'passed':out['passed'],'A1_budget_cases':len(out['A1_budget_cases']),'A2':out['A2'],'CR1_cross_signs':[D(r['cross_term'])>0 for r in out['CR1']],'bias':out['bias_gap'],'C5':out['C5_symbolic_difference']},ensure_ascii=False))
