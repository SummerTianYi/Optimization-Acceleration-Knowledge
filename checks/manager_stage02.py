"""Independent finite checks for stage02 f5769de. No optimization benchmark."""
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path
import platform


def theta(x, t):
    assert t > 0
    return abs(x) if abs(x) >= t else (x*x+t*t)/(2*t)


def gradient(x, t):
    assert t > 0
    return x/t if abs(x) < t else (F(1) if x > 0 else F(-1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    x,y,mu,nu=F(1,4),F(3,8),F(1),F(1,2)
    D=gradient(y,nu)*(y-x)-theta(y,nu)+theta(x,nu)
    dg=gradient(y,nu)-gradient(x,nu)
    Dmix=gradient(y,nu)*(y-x)-theta(y,nu)+theta(x,mu)
    dgmix=gradient(y,nu)-gradient(x,mu)
    L=dg*dg/(2*D); Lmix=dgmix*dgmix/(2*Dmix)
    assert (D,dg,Dmix,dgmix,L,Lmix)==(F(1,64),F(1,4),F(15,64),F(1,2),F(2),F(8,15))
    assert dg*dg==F(1,16) and 2*Lmix*D==F(1,60)
    fd=theta(x,mu)-theta(x,nu); gd=gradient(x,nu)-gradient(x,mu)
    assert Dmix-D==fd and dgmix-dg==gd
    same_D=theta(x,mu)-theta(x,nu)
    same_dg=gradient(x,nu)-gradient(x,mu)
    assert same_dg**2/(2*same_D)==F(1,7)
    e03={'LF':F(6,5),'LG':F(1),'tau':F(5,12),'sigma':F(1,2),
         'hessian_at_x_pi':[[F(1,5),F(-1)],[F(-1),F(2)]],
         'hessian_determinant_at_x_pi':F(-3,5), 'units':6}
    assert e03['tau']==1/(2*e03['LF']) and e03['sigma']==1/(2*e03['LG'])
    assert F(1,2)**2 < F(2,3) and F(4,5)**2 < F(2,3)
    assert e03['hessian_at_x_pi'][0][0]*2-1==F(-3,5)
    a=list(map(F,['-1','-3/4','-1/2','-1/4','1/4','1/2','3/4','1']))
    fstar=F(1,10)*sum(map(abs,a)); assert fstar==F(1,2)
    # Old-point residual can be reused exactly after a smoothing change.
    A=[[F(1),F(2)],[F(-1),F(1)]]; xx=[F(1,4),F(1,4)]; b=[F(1,2),F(0)]
    def residual():
        return [sum(v*z for v,z in zip(row,xx))-bi for row,bi in zip(A,b)]
    def evaluate_from_residual(r,t):
        q=[gradient(z,t) for z in r]
        return sum(theta(z,t) for z in r),[sum(A[i][j]*q[i] for i in range(2)) for j in range(2)]
    r=residual(); fresh=evaluate_from_residual(residual(),nu); cached=evaluate_from_residual(r,nu)
    assert fresh==cached
    output={
        'reviewed_sha':'f5769deab4f4bf0311a56963494eeafaa73c1909',
        'environment':{'python':platform.python_version(),'system':platform.system(),'arithmetic':'fractions.Fraction'},
        'scope':'Independent finite algebra and protocol checks, not performance or general theorem verification.',
        'moving_case':{'D_same':D,'delta_gradient_same':dg,'D_mix':Dmix,'delta_gradient_mix':dgmix,
                       'L_same':L,'L_mix':Lmix,'lhs':dg*dg,'mixed_rhs':2*Lmix*D,'function_drift':fd,'gradient_drift':gd},
        'same_point_case':{'L_mix':same_dg**2/(2*same_D)},
        'E03_protocol':e03,'E04_protocol':{'units':8,'reference_x':a,'Fstar':fstar},
        'ACC03_table3_3_differences':{'50_iterations':F('23.74')-F('21.52'),'500_iterations':F('32.87')-F('32.84')},
        'cached_residual_check':{'A':A,'x':xx,'b':b,'residual':r,'new_mu':nu,'f_new':cached[0],
            'gradient_new':cached[1],'equals_fresh_evaluation':fresh==cached,
            'general_linear_model_cost_note':'Cached Ax-b avoids another A*x for the old point; a new A^T*v may still be needed. This is an operation-accounting fact, not a speed measurement.'},
        'performance_protocols_executed':False,'passed':True,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2,default=lambda z:str(z) if isinstance(z,F) else str(z))+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'moving_case_lhs':str(dg*dg),'mixed_rhs':str(2*Lmix*D),'protocol_units':[6,8],'cache_equal':True}))

if __name__=='__main__':
    main()
