"""Manager independent checks for fixed 4285cde; not a performance replication."""
from __future__ import annotations
import json, sys, platform, argparse
from pathlib import Path
import sympy as sp
import mpmath as mp

BASE=Path(__file__).resolve().parent
mp.mp.dps=80

def exact_check():
    R=sp.Rational
    z=sp.symbols('z',real=True)
    f1=(z-1)**2/2; f2=(z+1)**2/2
    f=(f1+f2)/2
    W=sp.Matrix([[R(9,10),R(1,10)],[R(1,10),R(9,10)]])
    J=sp.ones(2,2)/2; x0=sp.Matrix([1,-1]); xm=x0.copy()
    y0=sp.Matrix([sp.diff(f1,z).subs(z,1),sp.diff(f2,z).subs(z,-1)])
    sigma=R(4,5); mu=sp.diff(f,z,2); L=sp.Integer(2); Q=L/mu
    alpha=(1-sigma**2)**2/(560*Q*L); beta=R(1,10**6)
    x1=W*x0-alpha*y0+beta*(x0-xm)
    norm2=lambda x:(x.T*x)[0]
    C0=norm2((sp.eye(2)-J)*x0); C1=norm2((sp.eye(2)-J)*x1)
    T0=norm2((sp.eye(2)-J)*y0);D0=norm2(x0-xm)
    rhs=(1-sigma**2)*C0/2+4*(alpha**2*T0+beta**2*D0)/(1-sigma**2)
    rhsplus=(1+sigma**2)*C0/2+4*(alpha**2*T0+beta**2*D0)/(1-sigma**2)
    gap=1-sigma**2
    b2=[9*47*gap**2/(56**2*34),1259*gap**2/(280**2*17),Q**2*59/1122,gap**4*69/(560**2*68*Q**2)]
    assert C1>rhs and C1<=rhsplus
    assert all(beta**2<t for t in b2)
    s=sp.symbols('s',positive=True)
    young=sp.simplify((1+(1-s**2)/(2*s**2))*s**2)
    assert young==(1+s**2)/2
    return {'functions':[str(f1),str(f2)],'aggregate':str(sp.expand(f)),
            'hessians':[str(sp.diff(f1,z,2)),str(sp.diff(f2,z,2))],
            'W':str(W),'eigenvalues_W_minus_J':{str(k):v for k,v in (W-J).eigenvals().items()},
            'alpha':str(alpha),'beta':str(beta),'x0':list(map(str,x0)),
            'y0':list(map(str,y0)),'x1':list(map(str,x1)),
            'C0':str(C0),'T0':str(T0),'D0':str(D0),'lhs':str(C1),
            'printed_rhs':str(rhs),'young_rhs':str(rhsplus),
            'all_beta_bounds_satisfied':True,'young_coefficient':str(young),
            'scope':'one legitimate first vector-update step; no statement of algorithm divergence'}

def quad_case(diag, eta_string, steps=20):
    H=mp.matrix([[mp.mpf(diag[0]),0],[0,mp.mpf(diag[1])]])
    dot=lambda a,b:(a.T*b)[0]
    f=lambda x:dot(x,H*x)/2
    grad=lambda x:H*x
    m=mp.mpf('0.5');beta=mp.mpf('0.5');gamma=mp.mpf('0.5')
    eta=omega=mp.mpf(eta_string);t=mp.mpf(2);x=mp.matrix([1,1]);y=x.copy()
    M=(1-omega)/(2+1/(beta*gamma*(1-eta)))
    assert (1+beta)*gamma/2 <= (2*(t-1)+m)/(2*t+m)
    zero=mp.matrix([0,0]);g=grad(x);L=mp.mpf(max(diag));mu=mp.mpf(min(diag))
    D0=dot(g,x)-(f(x)-f(zero))
    s=M/(dot(g,g)/(2*D0)) if dot(g,g)>0 else mp.mpf(1)
    states=[];max_Ddiff=mp.mpf(0);max_identity=mp.mpf(0)
    for k in range(steps+1):
        g=grad(x);oldf=f(x)
        tn=(m+mp.sqrt(m*m+4*t*t))/2
        yn=x-s*g
        xn=yn+(t-1)/tn*(yn-y)+(gamma-1)*t/tn*(yn-x)
        z=tn*(xn-yn)+yn
        E=dot(z,z)/2+(beta/2)*gamma**2*t*t*s*s*dot(g,g)+gamma*t*t*s*oldf
        gn=grad(xn); d=xn-x;dg=gn-g;D=dot(gn,d)-(f(xn)-oldf)
        stableD=dot(d,H*d)/2
        max_Ddiff=max(max_Ddiff,abs(D-stableD))
        if dot(dg,dg)==0:
            local=mp.mpf(0)
        else:
            assert D>0
            local=dot(dg,dg)/(2*D)
            max_identity=max(max_identity,abs(dot(gn,d)-(f(xn)-oldf)-dot(dg,dg)/(2*local)))
        A=t*t/(tn*(tn-1));B=2*(tn-1)/((1+beta)*gamma*tn)
        C=(1-omega)/(2/B+1/(beta*gamma*(1-eta)*A))
        sn=min(A*s,B*s,C/local if local else mp.inf)
        dissip=-(omega*mu*gamma/2)*sn*tn*(tn-1)*dot(d,d)-(mu*gamma/2)*tn*sn*dot(xn,xn)-(beta*eta*gamma**2/2)*t*t*s*s*dot(g,g)
        states.append(dict(k=k,E=E,dissip=dissip,s=s,t=t,local=local,gap=oldf))
        x,y,t,s=xn,yn,tn,sn
    residuals=[states[k+1]['E']-states[k]['E']-states[k]['dissip'] for k in range(steps)]
    assert max(residuals)<=mp.mpf('1e-65')
    out={
        'H_diagonal':diag,'eta':eta_string,'omega':eta_string,'steps':steps,
        'M':str(M),'max_prop21_residual':mp.nstr(max(residuals),35),
        'max_two_point_identity_error':mp.nstr(max_identity,20),
        'max_direct_vs_stable_D_error':mp.nstr(max_Ddiff,20),
        'initial_E':mp.nstr(states[0]['E'],35),'last_E':mp.nstr(states[-1]['E'],35),
        'all_prop21_checks_pass':True,'scope':'80-digit finite quadratic mechanism check; not general proof or performance evidence',
        'trace':[{key:(v if key=='k' else mp.nstr(v,35)) for key,v in state.items()} for state in states]}
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=BASE/'results'/'manager_stage01_4285cde.json')
    args=parser.parse_args()
    exact=exact_check()
    quads=[quad_case(h,eta) for h in [[1,10],[1,1000],[0,1],[0,0]] for eta in ['0','0.5']]
    summaries=[{k:v for k,v in r.items() if k!='trace'} for r in quads]
    result={'reviewed_sha':'4285cde36d8efa3f870bae95f4080249fba3f2c2',
            'scope':'Independent symbolic ACC01 first-step and new ACC02 80-digit mechanism checks. No performance runs.',
            'environment':{'python':sys.version,'platform':platform.platform(),'sympy':sp.__version__,'mpmath':mp.__version__,'mp_dps':mp.mp.dps},
            'ACC01':exact,'ACC02':summaries}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'ACC01':exact,'ACC02':summaries},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
