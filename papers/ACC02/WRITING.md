# ACC02 写作蒸馏

本篇是理论论文，无数值实验段。分析依据全文；英文练习是执行者自行改写，不是摘抄。

## 片段一：引言如何给贡献留出准确位置

PDF2–3 §1按“固定L梯度→两点自适应梯度→Nesterov→已有自适应加速→新的收敛对象”推进。式(2)–(5)不是装饰：每个公式使下一段能明确说究竟改了步长、惯性系数还是结论。作者承认已有O(k⁻²)工作，再把弱迭代收敛及强凸线性率作为本篇位置，避免把整个领域的已有成果重说成首次贡献。

可复用：背景段末用缺失的**结论对象**连接贡献段，比“仍有很多问题”具体。近邻[19]的历史最小梯度平方O(k⁻³)只属于该近邻，写自己的定理时不能顺手继承。引用原作未回查时，本知识库的叙述须保留“作者转述”。

同事实修改前（执行者构造的欠限定概括）：

> We propose a parameter-free accelerated method that achieves optimal convergence without line search.

修改后（执行者改写）：

> The method uses function values and gradients at consecutive iterates to select the next step size without a line search. For convex smooth objectives, the analysis establishes a quadratic decay bound for the objective gap and weak convergence of the iterates. Under strong convexity, it gives a linear factor whose contraction parameter scales with μ/L, without requiring μ as an algorithm input.

前句是需要纠正的概括，不是原文引语。修改后保留同样的算法及定理事实，去掉原文未支持的“无参数”和强凸最优性，补上信息调用与收敛拓扑。另有m,t₀,β,γ,η,ω等参数，详见研究卡。

## 片段二：算法规则从证明需求中出现

PDF5式(8)先给能量；PDF5–7 Lemma2.1展开差分；PDF7–10 §2.2把问题收敛成“让R_k≤0”，再分别生成A、B、C三个门，最后在Hypothesis2.1汇总。这样的顺序让长公式有目的：读者知道每一个min分量消去什么，而非先背算法再读十页推导。

PDF10–17继续分层：能量下降→步长下界→函数值界→有界与两点距离→弱极限唯一；强凸章另加能量上界获得线性耗散。弱收敛不是函数值收敛的自动同义词；线性结论也需要η,ω严格正。这种层次适合未来论文把“主结果”分成不同对象与额外假设。

写作改进建议（执行者）：在式(6)后放一个时序框，说明x_new先用旧步长生成，新L只定下一步；在Thm4.1直接写η,ω∈(0,1)以保证ρ>0；在Prop2.3附近保留实际幂指数而少用全参数“次线性增长”的口头概括。这里是清晰性建议，未声称重证或否定其他定理。

## 可迁移的英文论证练习（自行改写）

> We first separate the energy increment into dissipative terms and a remainder. The three step-size bounds control the objective weight, the equal-gradient case, and the quadratic form in successive gradients, respectively. Their minimum can be evaluated after the new iterate has been formed. This ordering explains both why the update requires no line search and why exact function and gradient differences remain part of its information requirements.

何时用：算法设计确实由能量剩余项推出，且计算依赖已核对时。检查每个“control”对应一个不等式，不能仅模仿句型。非凸、随机或网络迁移必须重新建立剩余项，不能沿用措辞暗示已解决。对应P00 PDF15/印19集中到分布式路线中的基础论证要求。

写作自查：两处可定位的论证链；前后改写未加新结论；原文与改写、历史工作与本篇贡献、函数率与点收敛均已区分。无实验的论文以理论结论组织作分析，不制造实验讨论。
