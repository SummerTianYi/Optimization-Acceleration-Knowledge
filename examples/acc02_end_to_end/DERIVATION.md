# 三个步长门怎样推出函数差界

**问题和归属。** 在有限维欧氏空间取 $f(x)=(x-c)^TH(x-c)/2,\ H=H^T\succeq0,\ L=\lambda_{\max}(H)>0$。用同一函数的精确值与梯度计算下一步。希望得到每个输出 $x_k$ 的原目标差界，并识别降秩后点趋向哪里。作者的更新、能量和假设定位于 [Wang–Peypouquet，期刊版，式 (6)、(8)–(19)，命题 2.1–2.2、定理 3.1](https://doi.org/10.1007/s10957-026-03086-z)。此处移植独立审查 TEST_A §§2–5 的二次特化和 Manager 的行列式抽查，补写交叉项消去及步长下界。原审查的高精度轨迹仍归审查者。[输入归属](../../reviews/UPGRADE07_INPUTS.md)

### 输入、顺序与可计算性

取 $x_0=y_0$，$0<m<1,\ t_0\ge1,\ \beta>0,\ 0<\gamma<2,\ \eta,\omega\in[0,1)$，及 $(1+\beta)\gamma/2\le1-1/(t_0+m/2)$。记 $t=t_k,\ s=s_k,\ u=t_{k+1},\ h=s_{k+1},\ g=\nabla f(x),\ g'=\nabla f(x')$。一步先生成
$$
u=(m+\sqrt{m^2+4t^2})/2,\quad y'=x-sg,\quad
x'=y'+(t-1)(y'-y)/u+(\gamma-1)t(y'-x)/u .
$$
令 $d=x'-x,\ D=\langle g',d\rangle-(f'-f)=d^THd/2$。若 $Hd\ne0$，则 $\ell=\|g'-g\|^2/(2D)=d^TH^2d/(d^THd)\in(0,L]$，由逐特征值 $\lambda^2\le L\lambda$ 得上界；若同梯度则令 $\ell=0$。计算
$$
 A={t^2\over u(u-1)},\quad B={2(u-1)\over(1+\beta)\gamma u},\quad
 a=\beta\gamma(1-\eta),\quad C={1-\omega\over 2/B+1/(aA)},\quad
 h=\min(As,Bs,C/\ell).
$$
$\ell=0$ 时省略第三门。两点探测同式求 $\ell_0>0$，以 $s_0=M/\ell_0,\ M=(1-\omega)/(2+1/a)$ 起步。也可从合法有限正步长开始，此时统一下界改为 $\min(s_0,M/L)$。本文选择非退化探测；初点即达到函数精度时直接返回。$c,f^*,L,\mu=\lambda_{\min}(H)$ 只用于构造模型、证明或基准核证，ACC02 的步长不读谱常数。实验用已知 $f^*=0$ 实现停止。

### 展开一步再选步长

记 $F=f-f^*=f,\ Z=t x-(t-1)y-\gamma ts g,\ E=\|Z-c\|^2/2+\beta\gamma^2t^2s^2\|g\|^2/2+\gamma t^2sF$。代入更新式得 $Z=u x'-(u-1)y'$，故 $Z'=Z-\gamma uhg'$，且 $Z-c=(x'-c)+(u-1)(d+sg)$。记 $T=hu(u-1),\, b=(1+\beta)\gamma/2$。于是
$$
\Delta E=-\gamma uh\langle g',x'-c\rangle-\gamma T\langle g',d\rangle
-\gamma sT\langle g',g\rangle+b\gamma u^2h^2\|g'\|^2
-\beta\gamma^2t^2s^2\|g\|^2/2+\gamma(u^2hF'-t^2sF).
$$
二次型给 $\langle g',x'-c\rangle=2F'\ge F'+\mu\|x'-c\|^2/2$；$\langle g',d\rangle=F'-F+D$。代入后 $F'$ 的系数为 $\gamma(u^2h-uh-T)=0$。又 $D\ge\mu\|d\|^2/2$，异梯度时它还等于 $\|g'-g\|^2/(2\ell)$。按权重 $\omega,1-\omega$ 分配这两界，并拆开旧梯度的平方项，得到
$$
\Delta E\le R-\tfrac12\omega\mu\gamma T\|d\|^2
-\tfrac12\mu\gamma uh\|x'-c\|^2-\tfrac12\beta\eta\gamma^2t^2s^2\|g\|^2 ,
$$
$$
R/\gamma=(T-st^2)F+b u^2h^2\|g'\|^2-a t^2s^2\|g\|^2/2
-sT\langle g',g\rangle-(1-\omega)T\|g'-g\|^2/(2\ell).
$$
同梯度时 $Hd=0,D=0$，最后一项取零。第一门给 $T\le st^2$，且 $F\ge0$。同梯度时余下项至多为 $(bu^2h^2-sT)\|g\|^2$，第二门使其非正。

异梯度时令 $q=h\ell/(1-\omega)>0,\ r=s/h$。去掉非正的函数项，将余量除以正数 $\gamma(1-\omega)T/(2\ell)$ 后得到作用于 $(g',g)$ 的二次型
$$
K=\begin{pmatrix}-1+2q/B&1-rq\\1-rq&-1-ar^2Aq\end{pmatrix}.
$$
第三门给 $q\le aAB/(B+2aA)<B/2$，故两个对角项均负。展开得
$$
-\det K=q(-2r+2/B-ar^2A)+r^2q^2(1+2aA/B).
$$
第二门给 $r\ge1/B$，故右侧至多 $r^2q[-aA+q(1+2aA/B)]\le0$。于是 $K\preceq0$、$R\le0$，从而 $E_{k+1}\le E_k$。

### 从证书到输出

由 $u^2=t^2+mu$ 有 $A=(u-m)/(u-1)>1$ 且 $u\ge t+m/2$。初始参数条件与 $u\ge t_0+m/2$ 给 $B\ge1$，代回得 $C\ge M$。用 $\ell\le L$ 归纳得到 $s_k\ge M/L$（上述探测初始化）。能量中每项非负，故
$$
 0\le f(x_k)-f^*\le {LE_0\over\gamma M(t_0+mk/2)^2}.
$$
正定时 $\|x_k-c\|^2\le2F_k/\mu$。半正定时梯度属于 ${\rm ran}(H)$；把两步更新投影到核上，用 $x_0=y_0$ 归纳得 $P_0x_k=P_0y_k=P_0x_0$。正谱分量由函数差控制，极限为 $c+P_0(x_0-c)$。这给出的是该二次型族的有限维点收敛；作者的一般 Hilbert 空间定理保留其自身证明和条件。

**可手算边界。** $c=(1/2,-1),\,x_0=(2,1),\,x_{-1}=0$，给 $H=\left(\begin{smallmatrix}3&1\\1&2\end{smallmatrix}\right)$ 时，谱为 $(5\pm\sqrt5)/2$，$D_0=9,\ell_0=65/18$。所选 $m=\beta=\gamma=\eta=\omega=1/2,t_0=2$ 满足 $3/8\le5/9$，$M=1/20,s_0=9/650$。换成全一矩阵后，$\mu=0,\ell_0=2$，核分量不动，极限为 $(1/4,-3/4)$。若 $H={\rm diag}(-1,2), d=(1,0)$，则 $D=-1/2$，正曲率与最优点前提同时失效。以上是解析推论；新运行的浮点检验见[实际结果](results.json)。
