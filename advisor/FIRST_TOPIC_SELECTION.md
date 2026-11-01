# 优化加速研究 · 首次选题

**导师初选讨论稿，待Manager验收**

五个课题从一个具体问题出发：达到有数学意义的精度时，哪一部分计算最值得省下来？网络中可能是一次全网往返，约束问题中可能是一次高精度内解，高阶模型中则可能是对全部样本重新计算曲率。下表按研究兴趣列出五个平行入口，编号只用于对应文献和内部研究记录。

| 课题 | 想节省什么 | 从哪里学起 | 路线可往哪里调 |
|---|---|---|---|
| [1 · 分布式几何优化](#t04-1) | 达到同一驻点精度的邻居通信轮数 | 单位球面上的非光滑下降与局部一致性 | 调整混合方式或各步通信轮数 |
| [2 · 非光滑矩阵分解](#t04-2) | 得到可核实驻点的近端与谱运算 | 从单列相邻差分到多列共享的融合段 | 修复分段，或在选定分段上直接求解 |
| [3 · 容量流的内解精度](#t04-3) | 达到可行解目标精度的内迭代与流求解 | 从两路径分流理解上下界 | 改用全程可行的更新，调整下界计算频率 |
| [4 · 非凸有限和的曲率计算](#t04-4) | 达到二阶驻点所需的样本与谱运算 | 曲率差分误差与负曲率检测 | 分阶段切换近似和精确曲率 |
| [5 · 球面多项式松弛](#t04-5) | 达到原目标精度的半定子问题规模与谱运算 | 三变量四次式、平方和与最小特征值 | 扩大谱空间、改进可行点或换下界算法 |

<a id="t04-1"></a>

## T04-1 分布式几何优化——估计同一超平面需要多少轮通信？

多个节点各自保存带离群点的样本，希望合力拟合一个经过原点的超平面。以单位向量作法向量、以样本到平面的绝对距离衡量误差，就得到一个有球面约束的非光滑问题。它把计划书中的分布式加速落到一个可比较的问题上：要让法向量达到相同驻点精度，各节点究竟需要交换多少轮信息？精度用球面上一次近端更新产生的位移来衡量。

从固定连通无向图和共同初值出发，先比较普通多轮平均与加速混合。平均后的向量要拉回球面，带负权的混合还可能使个别节点离开下降分析所需的邻域。第一步是把这项偏移与通信轮数联系起来，并和沿树汇总、广播一次全网更新的办法比较，同时记录本地次梯度次数。若加速混合难以保持邻域，仍可研究普通平均在不同迭代阶段各需要几轮。

- Jinxin Wang、Jiang Hu、Shixiang Chen、Zengde Deng、Anthony Man-Cho So（2023，初稿 v1）给出稳健子空间模型及局部一致邻域中的次梯度分析。[Decentralized Weakly Convex Optimization Over the Stiefel Manifold](https://arxiv.org/abs/2303.17779v1)
- Yilong Song、Peijin Li、Bin Gao、Kun Yuan（2025，修订稿 v2）给出光滑正交约束下免回缩、可压缩通信的近邻方法。[Distributed Retraction-Free and Communication-Efficient Optimization on the Stiefel Manifold](https://arxiv.org/abs/2506.02879v2)

<a id="t04-2"></a>

## T04-2 非光滑矩阵分解——相邻行何时可以合并求解？

在有噪声的矩阵分解中，希望一个因子的每列沿相邻行分段保持常数。已有方法限制两个因子的谱范数，在行差分上施加 MCP 非凸惩罚，再用平滑函数方便迭代。两行几乎相等时，细微的差异很重要。差分很小与差分恰为零对应不同的次梯度，重构误差相近的两个解，用原目标检验时驻点残差可能相差很大。这给计划书中的特殊结构非凸非光滑优化提供了切入点。

拟先用单列总变差的直接近端解作参照，再研究多列共享分段的情形。把拟合并段换成均值后，可在新点重算所有差分的次梯度条件，并检查两个谱约束。目标是看这种修复比直接分裂求解少做多少近端与谱运算，比较时要求返回点达到相同的原问题驻点精度。若均值修复仍不够准，可在已识别的分段上直接求解，再放开不满足驻点条件的边。

- Antonio Silveti-Falls、Cesare Molinari、Zev Woodstock（2026，初稿 v1）给出谱约束、行差分惩罚的矩阵模型及平滑算法。[Frank-Wolfe with Moreau Envelope Smoothing for Nonsmooth Nonconvex Problems](https://arxiv.org/abs/2606.00853v1)
- Yiming Zhou、Wei Dai（2026，初稿 v1）分析可分折点的结构识别与局部加速，为判断何时缩小求解空间提供参照。[Joint Structure Identification and Newton Acceleration via Proximal Line Search for Nonconvex Optimization](https://arxiv.org/abs/2609.18021v1)

<a id="t04-3"></a>

## T04-3 约束优化的内解精度——容量流何时值得多算一步？

在满足供需平衡和边容量的网络中分配流量，使若干条边的组合流量尽量接近给定目标。一个可行方案给出成本上界，线性化和约束乘子可以给出下界。上下界之间的距离足够小时即可交付方案。作为计划书约束加速方向的集中凸起点，本题关心怎样决定继续求准当前子问题，还是换一个可行流更划算。

先在只有两条替代路径时直接算出最优分流，用它校准停止判断，再转向有多个独立回路、边上损失相互耦合的网络。以相同的可行解成本与下界之差为终点，比较多做一次内迭代和求解一次线性费用流带来的改善，把矩阵乘法、恢复可行流和计算下界的工作都计入。若恢复可行性过于昂贵，可始终沿可行流更新，转而研究隔多少步重算下界，才能较早识别已经够好的解。

- Matthew X. Burns、Jiaming Liang（2026，初稿 v1）用累积的下模型构造加速凸算法的精度证书。[Accuracy Certificates for Convex Optimization at Accelerated Rates via Primal-Dual Averaging](https://arxiv.org/abs/2604.18321v1)
- Iyad Walwil、Olivier Fercoq（2024，初稿 v1）分析等式约束下平滑对偶间隙的计算及其与原问题精度的关系。[The Smoothed Duality Gap as a Stopping Criterion](https://arxiv.org/abs/2403.12579v1)

<a id="t04-4"></a>

## T04-4 低阶信息与高阶加速——曲率何时可以少算？

在有限样本的非凸拟合中，每次精确计算曲率都要访问全部样本。计划书提出比较低阶和高阶方法的复杂度，这里选取一个具体目标：当返回的点同时满足梯度小、最小曲率不显著为负两个条件时，各方法总共做了多少分量计算？先对线性残差 t 取有界损失 t²/(1+t²)，逐个样本求导就能估计遗漏样本引起的曲率误差。

已有工作说明模型精度如何决定抽样规模。接下来拟研究两次近似曲率计算相减后，差分步长会把误差放大多少，以及这种误差能否同时满足模型更新和最终二阶判据。先固定两种驻点容差，推算可用的差分步长和样本量，再与直接使用精确曲率向量积的办法比较，计入拒绝步和末次核验。若最后必须用全体样本，可转向研究前期近似何时值得切换为精确计算。

- Chang He、Shuzhong Zhang（2026，初稿 v1）给出利用高阶光滑性进行二阶更新和负曲率检测的参照。[Proximal Point Newton Methods for Nonconvex Optimization](https://arxiv.org/abs/2610.36256v1)
- Coralia Cartis、Sadok Jerad、Karl Welzel（2026，修订稿 v2）分析以导数差分构造高阶正则化模型的误差与复杂度。[On Global Rates for Regularization Methods based on Secant Derivative Approximations](https://arxiv.org/abs/2509.07580v2)
- S. Bellavia、G. Gurioli、B. Morini、Ph. L. Toint（2019，修订稿 v3）给出导数精度、有限和抽样规模与分量工作量的已有关系。[Adaptive Regularization Algorithms with Inexact Evaluations for Nonconvex Optimization](https://arxiv.org/abs/1811.03831v3)

<a id="t04-5"></a>

## T04-5 多项式松弛的降维——求球面最小值要保留哪些谱方向？

求球面上多项式的最小值时，一个球面点就能给上界，平方和松弛则可给下界。松弛产生的半定问题可能很大，只保留部分特征向量能缩小子问题，遗漏重要方向却会削弱下界。这直接对应计划书对松弛模型降维的研究：少算的谱方向，能否换来更低的总成本，同时保持原问题所需的精度？

拟从三维单位球面出发，让三个坐标的平方分别接近给定比例，再加入四次交叉项耦合坐标符号。这个算例可在球面上齐次化，由三元四次式的平方和定理，完整二阶松弛已能达到真实最小值。因此区间仍宽时，可以分别检查下界求得多准、恢复的球面点有多好，再决定该扩充谱空间还是改善可行点。先将降维方案同完整谱束及直接特征值下界作比较。相邻特征值难以分开时可整簇保留；转向更高维模型后，还要单独判断松弛本身留下的间隙。

- Feng-Yi Liao、Lijun Ding、Yang Zheng（2026，修订稿 v2）给出球面多项式松弛的谱束算法、收敛条件和矩阵迹界。[An Overview and Comparison of Spectral Bundle Methods for Primal and Dual Semidefinite Programs](https://arxiv.org/abs/2307.07651v2)
- Benjamin Lovitz、Nathaniel Johnston（2025，修订稿 v3）用一系列广义最小特征值给出球面齐次多项式的下界。[A hierarchy of eigencomputations for polynomial optimization on the sphere](https://arxiv.org/abs/2310.17827v3)
- Albrecht Pfister、Claus Scheiderer（2010，初稿 v1）证明非负三元四次齐次式的平方和表示，为起步算例提供精确参照。[An elementary proof of Hilbert's theorem on ternary quartics](https://arxiv.org/abs/1009.3144v1)

## 五题怎样联系

第 3、5 题值得对照阅读。在容量流里，要分清一次内解找到的可行值和它能保证的下界；在多项式松弛里，同样要分清一个试探向量给出的值和全空间最小特征值的下界。前者练习如何据此决定是否继续内解，后者还需处理谱误差和可行点恢复，两题均可独立开始。第 4 题也用最小特征值，但它服务于判断一个点附近是否还存在下降方向。

原六篇提供不同的起步工具。ACC01 的网络混合与本地计算分账可用于第 1 题。ACC03 的分块近端与 ACC04 对平滑误差的追踪有助于第 2 题。ACC05 的约束子问题、ACC06 的非精确乘子法可作第 3 题的参照。ACC02 用相邻点信息调节步长的思想，则有助于理解第 4 题为何要管理差分误差。第 5 题另需学习矩与平方和对偶。可以按最想深入的数学对象选择起点，再决定哪些工具值得共用。
