# 迁移自测 · 平滑绝对偏差之后，何时得到原目标精度？

本任务在[主示范](../acc02_end_to_end/README.md)及[通用入口](../../knowledge/RESEARCH_TO_DRAFT.md)固定后提出。沿同一入口先选 [ACC04 关于原目标与平滑偏差的研究卡](../../papers/ACC04/RESEARCH.md)，固定题面与数值见[协议](protocol.json)。在 $\mathbb R^3$ 上令 $F(x)=\sum_i|x_i-b_i|+\lambda\|x\|_1$，$0<\lambda<1$。只平滑第一项，第二项保留精确近端。这是独立构造的小任务。ACC04 的时变平滑惯性率不作为此固定参数近端梯度法的结论。

**预定问题。** 从零出发，分别用两个固定 $\mu$，在同一原目标差 0.02 下记录首次达标步，并继续到第一次近端固定点来比较。所有接受点做原目标评估；固定点测试实际调用梯度及近端，包含最后一次未移动的试算。用最多 600 次推进，无调参。全程仅需 Python 标准库。

**从原目标到可检验的两个量。** 三角不等式给
$F(x)\ge\lambda\|b\|_1+(1-\lambda)\|x-b\|_1$，等号在 $x=b$ 达到最小值。原目标差可直接测。对标量残差 $r$ 取 Huber 平滑 $\phi_\mu(r)=r^2/(2\mu)$ 当 $|r|\le\mu$，否则为 $|r|-\mu/2$。于是 $0\le |r|-\phi_\mu(r)\le\mu/2$，光滑部分梯度为 $p_i=\operatorname{clip}((x_i-b_i)/\mu,-1,1)$，Lipschitz 常数为 $1/\mu$。记平滑复合目标为 $F_\mu$。近端最小化的最优性条件给
$z=\mathrm{soft}(x-\mu p,\mu\lambda)$；
固定点等价于 $0\in p+\lambda\partial\|x\|_1$，故为 $F_\mu$ 的全局最优点。分坐标求解该包含式得 $x_{\mu,i}^*=\mathrm{sign}(b_i)(|b_i|-\lambda\mu)_+$。非零坐标代入有 $p_i=-\lambda\,\mathrm{sign}(x_i)$；零坐标的 $|p_i|\le\lambda$ 可由次梯度抵消。原目标误差满足
$F(x)-F^*\le F_\mu(x)-F_\mu^*+3\mu/2$。当 $x=x_\mu^*$ 时，更精确的原差是 $(1-\lambda)\sum_i\min(|b_i|,\lambda\mu)$。这一步说明为何近端固定点可已达到，原问题仍有可观误差。

**复跑。** 在本目录执行 `python transfer.py --config protocol.json --out new_result.json`。实现用标准库的精确有理数重建原目标、Huber 值、近端映射及上述闭式，不用浮点零阈值判断最优。已运行的数值与英文段落见[迁移结果](RESULT.md)。
