# ACC02 写作蒸馏

本篇是理论论文，无数值实验段。分析依据全文；英文练习是执行者自行改写，不是摘抄。

## 片段一：引言如何给贡献留出准确位置

PDF2–3 §1按“固定L梯度→两点自适应梯度→Nesterov→已有自适应加速→新的收敛对象”推进。式(2)–(5)不是装饰：每个公式使下一段能明确说究竟改了步长、惯性系数还是结论。作者承认已有O(k⁻²)工作，再把弱迭代收敛及强凸线性率作为本篇位置，避免把整个领域的已有成果重说成首次贡献。

可复用：背景段末用缺失的**结论对象**连接贡献段，比“仍有很多问题”具体。近邻[19]的历史最小梯度平方O(k⁻³)只属于该近邻，写自己的定理时不能顺手继承。引用原作未回查时，本知识库的叙述须保留“作者转述”。

### 事实校准示例（保留原例，不作为同事实组织测试）

校准前（执行者构造的欠限定概括，含待纠正主张）：

> We propose a parameter-free accelerated method that achieves optimal convergence without line search.

校准后（执行者改写）：

> The method uses function values and gradients at consecutive iterates to select the next step size without a line search. For convex smooth objectives, the analysis establishes a quadratic decay bound for the objective gap and weak convergence of the iterates. Under strong convexity, it gives a linear factor whose contraction parameter scales with μ/L, without requiring μ as an algorithm input.

前句是需要纠正的概括，不是原文引语。校准后去掉原文未支持的“无参数”和强凸最优性，并补上信息调用、收敛拓扑和条件数范围，事实集合发生改变。另有m,t₀,β,γ,η,ω等参数，详见研究卡。

### 同事实组织改写（新增受控练习；英文为自行改写）

以下两版用于独立介绍算法及结论的段落，共同事实先固定如下。

| 事实ID | 两版必须共同保留的事实 | 原文定位 |
|---|---|---|
| B1 | f在实Hilbert空间上凸且L光滑，最优集非空；式(6)从x₀=y₀出发并遵守Hypothesis2.1 | PDF1–2模型与最优点约定；PDF3式(6)，PDF9–10 Hypothesis2.1，PDF11/14定理前提 |
| B2 | 相邻迭代点的函数值和梯度用于选择下一步步长，不进行线搜索 | PDF4局部曲率定义，PDF9–10步长规则；式(6)依赖顺序 |
| B3 | 目标函数差有O(k⁻²)上界 | PDF11–13，Theorem3.1、步长下界与Remark3.1 |
| B4 | x_k和y_k弱收敛到同一个最优点 | PDF14–15，Theorem3.2 |

**组织修改前（准确，但结果与信息要求交错）：**

<!-- controlled-rewrite-before -->
> Let f be convex and L-smooth on a real Hilbert space, with a nonempty set of minimizers, and consider (6) initialized with x₀=y₀ under Hypothesis 2.1. Both iterate sequences converge weakly to the same minimizer. Function values and gradients at consecutive iterates determine the next step size without a line search. The objective gap has an O(k⁻²) bound.
<!-- controlled-rewrite-before-end -->

**组织修改后（条件—信息机制—两种结论）：**

<!-- controlled-rewrite-after -->
> Let f be convex and L-smooth on a real Hilbert space, with a nonempty set of minimizers, and consider (6) initialized with x₀=y₀ under Hypothesis 2.1. Using function values and gradients at consecutive iterates, the method determines the next step size without a line search. The objective gap is O(k⁻²), and both iterate sequences converge weakly to the same minimizer.
<!-- controlled-rewrite-after-end -->

内部事实核对：前版B1→B4→B2→B3，后版B1→B2→B3→B4；条件句逐字符一致，函数值率与两序列的弱收敛均保留。后版按信息机制接分析结论，读者不用在结果与信息调用之间切换。

**自然性反向审查。** 这一独立段落保留凸性、光滑性、最优点存在、初始化及Hypothesis2.1；若前文已设定这些条件，正文后续可直接从“The method…”开始。前版将“Both iterate sequences converge weakly to the same minimizer.”与“The objective gap has an O(k⁻²) bound.”隔开；后版合为“The objective gap is O(k⁻²), and both iterate sequences converge weakly to the same minimizer.”。合并后两个收敛对象及弱收敛含义仍完整，读者可在同一句比较两种结论，无须额外加“The analysis establishes two conclusions”之类引导语。固定初值和参数的O记号按该上下文使用；强凸最优性、性能及常数风险留在研究卡，正文不反复排除未提出的主张。

## 片段二：算法规则从证明需求中出现

PDF5式(8)先给能量；PDF5–7 Lemma2.1展开差分；PDF7–10 §2.2把问题收敛成“让R_k≤0”，再分别生成A、B、C三个门，最后在Hypothesis2.1汇总。这样的顺序让长公式有目的：读者知道每一个min分量消去什么，而非先背算法再读十页推导。

PDF10–17继续分层：能量下降→步长下界→函数值界→有界与两点距离→弱极限唯一；强凸章另加能量上界获得线性耗散。弱收敛不是函数值收敛的自动同义词；线性结论也需要η,ω严格正。这种层次适合未来论文把“主结果”分成不同对象与额外假设。

写作改进建议（执行者）：在式(6)后放一个时序框，说明x_new先用旧步长生成，新L只定下一步；在Thm4.1直接写η,ω∈(0,1)以保证ρ>0；在Prop2.3附近保留实际幂指数而少用全参数“次线性增长”的口头概括。这里是清晰性建议，未声称重证或否定其他定理。

## 可迁移的英文论证练习（自行改写）

> We first separate the energy increment into dissipative terms and a remainder. The three step-size bounds control the objective weight, the equal-gradient case, and the quadratic form in successive gradients, respectively. Their minimum can be evaluated after the new iterate has been formed. This ordering explains both why the update requires no line search and why exact function and gradient differences remain part of its information requirements.

何时用：算法设计确实由能量剩余项推出，且计算依赖已核对时。检查每个“control”对应一个不等式，不能仅模仿句型。非凸、随机或网络迁移必须重新建立剩余项，不能沿用措辞暗示已解决。对应P00 PDF15/印19集中到分布式路线中的基础论证要求。

修订自查：两处可定位的论证链保留；旧例改标事实校准，新增四事实受控组织练习，两版条件及信息集合逐句核对。原文与改写、历史工作与本篇贡献、函数率与点收敛均已区分。此处是执行者修订自查，仍待Manager复验。
