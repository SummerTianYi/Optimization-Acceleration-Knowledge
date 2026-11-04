# What does it cost to stop an adaptive accelerated gradient method?

## Abstract

Adaptive step sizes and stopping tests draw on the same oracle. We study this interaction for the accelerated method of Wang and Peypouquet on shifted convex quadratics. A spectral expression for local curvature makes it possible to follow the energy proof from its three step-size bounds to an $O(k^{-2})$ objective gap. When the Hessian is singular, the initial null-space component selects the limiting minimizer. In a comparison with gradient descent and two accelerated baselines, the fixed-step accelerated method reached the target on a singular example in 400 iterations and 801 calls. Measuring the output gradient at every iterate preserved the trajectory but increased the cost to 1,200 calls. With a budget of 900 calls, the monitored run stopped after 300 iterations. These observations distinguish the information needed to compute an update from the information needed to recognize a satisfactory output.

## 1. Introduction

A global smoothness constant can set a safe gradient step, although obtaining a useful bound may itself take work. Backtracking replaces this information with trial function values. Wang and Peypouquet instead use successive function and gradient observations to select the *next* step of an inertial method [1]. Their analysis establishes objective acceleration for smooth convex functions and studies convergence of the iterates. The fixed and backtracking accelerated baselines used here follow the smooth specialization of the proximal acceleration schedule of Beck and Teboulle [2].

Two questions motivate the choice of quadratics. First, which part of the adaptive guarantee survives rank loss, where objective convergence alone does not identify a particular solution? Second, how much work does an implementation actually use when it must return the first accepted point meeting a common objective tolerance? Quadratic models expose the curvature and the minimizer set exactly. They also allow an independent reconstruction of every returned point, so an optional measurement can be separated from a change in the iterates.

## 2. Model and update

Let $f(x)=(x-c)^TH(x-c)/2$ on $\mathbb R^n$, where $H=H^T\succeq0$, $L=\lambda_{\max}(H)>0$, and $\mu=\lambda_{\min}(H)$. Then $f^*=0$ and $g=\nabla f(x)=H(x-c)$. Start at $x_0=y_0$. At iteration $k$ write $t=t_k,\ s=s_k$, with primes denoting new points. The method computes
$$
 u=(m+\sqrt{m^2+4t^2})/2,\quad y'=x-sg,\quad
 x'=y'+(t-1)(y'-y)/u+(\gamma-1)t(y'-x)/u .
$$
For $d=x'-x$, put $D=\langle g',d\rangle-(f(x')-f(x))$ and $\ell=\|g'-g\|^2/(2D)$ if $g'\ne g$. Set $\ell=0$ otherwise. The next step $h=s_{k+1}$ is
$$
 A=\frac{t^2}{u(u-1)},\quad B=\frac{2(u-1)}{(1+\beta)\gamma u},\quad
 a=\beta\gamma(1-\eta),\quad
 C=\frac{1-\omega}{2/B+1/(aA)},\qquad h=\min\{As,Bs,C/\ell\}.
$$
The last bound is omitted for equal gradients. We take $0<m<1,\ t_0\ge1,\ \beta>0,\ 0<\gamma<2,\ 0\le\eta,\omega<1$, and $(1+\beta)\gamma/2\le1-1/(t_0+m/2)$. An initial pair with unequal gradients sets $s_0=M/\ell_0$ by the same local curvature formula, with $M=(1-\omega)/(2+1/a)$. The update uses neither spectral bound nor a minimizer. The benchmark uses the known optimal value to stop.

## 3. Why the energy decreases

**Proposition.** With this initialization, the objective gap satisfies
$$
 f(x_k)\le LE_0/\{\gamma M(t_0+mk/2)^2\}.
$$
If $P_0$ is the orthogonal projection onto $\ker H$, then $x_k\to c+P_0(x_0-c)$.

**Proof.** Expanding the quadratic gives $D=d^THd/2$. For unequal gradients the quotient is $d^TH^2d/(d^THd)$, positive and at most $L$ by the scalar inequalities $\lambda^2\le L\lambda$ on the spectrum. Equal gradients imply $Hd=0$ and $D=0$.

Set $Z=t x-(t-1)y-\gamma ts g$ and
$$
 E=\tfrac12\|Z-c\|^2+\tfrac12\beta\gamma^2t^2s^2\|g\|^2+\gamma t^2s f(x).
$$
The update gives $Z=u x'-(u-1)y'$, so $Z'=Z-\gamma uhg'$. In the norm difference, substitute
$Z-c=x'-c+(u-1)(d+sg)$. With $T=hu(u-1)$, $b=(1+\beta)\gamma/2$, the cross terms are
$-\gamma uh\langle g',x'-c\rangle-\gamma T\langle g',d\rangle-\gamma sT\langle g',g\rangle$.
The two new squared-gradient terms combine into $b\gamma u^2h^2\|g'\|^2$.
Use $\langle g',x'-c\rangle=2f(x')\ge f(x')+\mu\|x'-c\|^2/2$ and $\langle g',d\rangle=f(x')-f(x)+D$. The coefficient of $f(x')$ cancels because $u^2h=uh+T$. Splitting $D$ between its curvature expression and $D\ge\mu\|d\|^2/2$ yields
$$
 E'-E\le R-\tfrac12\omega\mu\gamma T\|d\|^2
 -\tfrac12\mu\gamma uh\|x'-c\|^2-\tfrac12\beta\eta\gamma^2t^2s^2\|g\|^2,
$$
where
$$
 R/\gamma=(T-st^2)f(x)+bu^2h^2\|g'\|^2-\tfrac12at^2s^2\|g\|^2
 -sT\langle g',g\rangle-\frac{(1-\omega)T}{2\ell}\|g'-g\|^2 .
$$
The curvature term is zero for equal gradients. Gate $A$ makes the first term nonpositive. For equal gradients gate $B$ gives $bu^2h^2\le sT$, which settles the remaining terms.

For unequal gradients let $q=h\ell/(1-\omega)$ and $r=s/h$. Scaling the remaining quadratic form by $2\ell/[(1-\omega)T]$ gives diagonal coefficients $-1+2q/B,\ -1-ar^2Aq$ and off-diagonal coefficient $1-rq$. Gate $C$ gives $q\le aAB/(B+2aA)<B/2$, so both diagonal coefficients are negative. For the resulting matrix $K$,
$$
 -\det K=q(-2r+2/B-ar^2A)+r^2q^2(1+2aA/B)
 \le r^2q[-aA+q(1+2aA/B)]\le0 .
$$
The first inequality uses $r\ge1/B$, the second the bound on $q$. Thus $K\preceq0$, which proves $E'\le E$.

Finally $u^2=t^2+mu$ gives $A=(u-m)/(u-1)>1$ and $u\ge t+m/2$. The initial parameter condition ensures $B\ge1$, hence $C\ge M$. Induction using $\ell\le L$ gives $s_k\ge M/L$. Keeping the objective term of $E_k\le E_0$ proves the gap bound. In the range of $H$, the smallest positive eigenvalue controls the squared distance to the solution set through $f(x_k)$. In the kernel, each gradient vanishes after projection and the two updates preserve $P_0x_k=P_0y_k=P_0x_0$. Combining the components gives the stated limit. ∎

For example, with $c=(1/2,-1),x_0=(2,1)$, and the zero probe, the positive definite matrix with rows $(3,1),(1,2)$ gives $\ell_0=65/18$. Replacing it by the all-ones matrix preserves the gap guarantee but selects $(1/4,-3/4)$ as the limit. The null-space component accounts for the difference from $c$.

## 4. Numerical design and results

We use four twelve-dimensional quadratics. A Householder reflection about the normal $(1,\ldots,12)$ rotates geometrically spaced eigenvalues from 1 to $\kappa$. The singular models have three additional zero directions in place of three positive eigenvalues, leaving nine positive values. The shift alternates $1/4,-1/4$, and the initial point is the all-ones vector. We set $m=\beta=\gamma=\eta=\omega=1/2,\ t_0=2$ for the adaptive method. Gradient descent (GD) and fixed acceleration use the supplied $L=\kappa$. Backtracking acceleration starts with curvature 1, doubles it after rejection and carries forward the accepted curvature. Both accelerated baselines start with inertial parameter 1 and use $t'=(1+\sqrt{1+4t^2})/2$.

We stop at the first accepted output with $f(x)/\max(1,f(x_0))\le10^{-8}$, including the initial point. The primary runs request no additional output gradients. A repeated request at the same point reuses a cached value. Each physical function call uses one multiplication by a dense orthogonal factor and each gradient call uses two. Initialization, failed trials and stopping calls count against a budget of 200,000. The fixed model construction and offline reconstruction are separate from these oracle counts.

**Function / gradient calls at first success.** Each cell reports the two counts separately. All sixteen runs reached the target.

| Hessian | Positive spectral ratio | Adaptive [1] | GD | Fixed acceleration | Backtracking acceleration |
|---|---:|---:|---:|---:|---:|
| Positive definite | 100 | 198 / 197 | 526 / 525 | 131 / 130 | 302 / 148 |
| Positive definite | 10,000 | 567 / 566 | 31,245 / 31,244 | 657 / 656 | 1,693 / 840 |
| Singular | 100 | 156 / 155 | 471 / 470 | 162 / 161 | 374 / 184 |
| Singular | 10,000 | 529 / 528 | 25,782 / 25,781 | 401 / 400 | 1,845 / 916 |

Under unit weights, fixed acceleration used 261 calls against 395 for the adaptive method on the first model. On the second model the corresponding counts were 1,313 and 1,133. Changing the positive spectral ratio thus changed the ordering even within the positive definite pair. Backtracking incurred seven rejected trials per model at ratio 100 and fourteen at ratio 10,000.

The large-ratio singular model isolates the effect of monitoring. Fixed acceleration reached the target in the same 400 steps with or without an output-gradient measurement. The measurement raised the count from 801 to 1,200 because gradients at accepted points rarely coincided with the extrapolated gradients required for the next update. In a second pair of runs capped at 900 calls, the unmonitored method still reached the target. The monitored run exhausted its budget after 300 steps at a relative gap of $3.84\times10^{-7}$. In contrast, on the positive definite model at ratio 100, monitoring increased the GD count from 1,051 to 1,052. Its accepted-point gradient supplies the next update; only the terminal gradient was extra.

## 5. Discussion

The curvature quotient explains how a method without the global smoothness constant can still enforce an energy bound. Rank loss changes the interpretation of point convergence while leaving the gap estimate intact. In computation, the oracle comparison depends on the required output and on whether one query can serve two purposes. Replaying the cache and the measured trajectories preserves this distinction. Subtracting every call first labelled as monitoring would discard almost all of the gradients GD actually used.

These examples use exact analytic reference values, small dense factors and deterministic starts. A problem with unknown optimal value needs an implementable stopping certificate and a fresh accounting of its cost. Comparing wall-clock performance would also require a model of the actual evaluation kernels. The present results locate the effect of the measurement policy at a fixed accuracy and show how a hard budget can turn that effect into a different returned point.

## References

1. Z. Wang and J. Peypouquet (2026). Adaptive Accelerated Gradient Method for Smooth Convex Optimization. *Journal of Optimization Theory and Applications* 210, 52. [Published paper](https://doi.org/10.1007/s10957-026-03086-z)
2. A. Beck and M. Teboulle (2009). A Fast Iterative Shrinkage-Thresholding Algorithm for Linear Inverse Problems. *SIAM Journal on Imaging Sciences* 2, 183–202. [Published paper](https://doi.org/10.1137/080716542)
