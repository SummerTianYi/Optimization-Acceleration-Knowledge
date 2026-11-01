"""Independent algebra review of topic04; no optimization/performance experiment."""
from __future__ import annotations
import argparse
import json
import platform
from pathlib import Path
import sympy as s


def check() -> dict:
    u = s.Matrix([s.Rational(3,8),s.Rational(5,8),-s.Rational(1,4)])
    P = s.Matrix([[s.Rational(1,2),s.Rational(1,2),0],
                  [s.Rational(1,2),s.Rational(1,2),0],[0,0,1]])
    v = P*u
    original, repaired, movement = (a.dot(a) for a in (u,v,u-v))
    assert P*P == P and P.T == P
    assert (original,repaired,movement)==(s.Rational(19,32),s.Rational(9,16),s.Rational(1,32))
    A = s.Matrix([[s.Rational(1,2),0],[s.Rational(1,2),1]])
    w = s.Matrix([1,1])
    witness = (A*w).dot(A*w)/w.dot(w)
    exact = (3+s.sqrt(5))/4
    assert witness == s.Rational(5,4)
    assert s.simplify((A.T*A-exact*s.eye(2)).det()) == 0
    common = s.ones(2,2)/2
    assert common*common == common
    # The scalar error-budget calculation is for a single directional difference.
    # A full tensor construction may require additional dimension factors.
    h,L,eta,tau=s.symbols('h L eta tau', positive=True)
    bound=L*h/2+2*eta/h
    hstar=2*s.sqrt(eta/L)
    assert s.simplify(s.diff(bound,h).subs(h,hstar)) == 0
    best=s.simplify(bound.subs(h,hstar))
    assert s.simplify(best-2*s.sqrt(L*eta)) == 0
    return {'reviewed_sha':'14b35df06fa1ab6a742e3989352e5cace8195b7f',
            'environment':{'python':platform.python_version(),'sympy':s.__version__},
            'fusion_single':{'input':list(map(str,u)),'output':list(map(str,v)),
                             'input_norm_squared':str(original),'output_norm_squared':str(repaired),
                             'displacement_squared':str(movement)},
            'fusion_separate_columns':{'matrix':[[str(x) for x in row] for row in A.tolist()],
                                      'witness_squared_norm_lower_bound':str(witness),
                                      'exact_squared_spectral_norm':str(exact)},
            'fusion_common_projection':{'spectral_norm':1,'projection_idempotent':True},
            'directional_difference_budget':{'bound':str(bound),'minimizer':str(hstar),
                'minimum_bound':str(best),'existence_condition':'eta <= tau**2/(4*L)',
                'scope':'scalar directional bound only; not full-tensor or algorithm complexity'},
            'passed':True,
            'limits':'Independent algebra only; no paper-wide proof, speed measurement, or novelty certification.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=check();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
