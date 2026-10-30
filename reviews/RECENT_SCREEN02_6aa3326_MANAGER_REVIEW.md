# 候选证据补齐02：Manager独立验收

日期2026-10-31。受审固定SHA：`6aa33260e8f3024a7184ced18c0fa37514ae3d2c`；直接父提交为`f440b2f6d5fd52b785d0de6a85edbe61eb767609`。

## 结论

**本轮证据补齐通过，六项升降级的主要依据成立；不另开全批返工。** 通过的是原文比较、必要性筛查和有限关系的核验，不是确认一项可投稿创新。当前C-R1只保留为条件性的分析候选；A2、A1、B1为潜在候选；B2、D1降为方法/实施线索。16条历史记录完整保留，不能把它们说成16个课题。最终选题由导师决定。

下一任务：[候选价值与主线验证03](../tasks/CANDIDATE_VALIDATION_03.md)。不因仅剩一个候选标签就默认选择集中凸I-FALM，不为凑4—6项降低门槛；也不把本次排除等同于所有相关方向无价值。

|条目|本轮复验判断|
|---|---|
|A2|接受收缩。R24已有弱凸网络的有限Moreau关系；通信依赖和真实局部非光滑结构值得继续有限核验，但多轮混合本身是成熟替代。|
|D1|接受降级。最小特征值概率区间、近似LMO误差与停止证书的代数及经典FW接口成立。整体HALLaR改写版的全部原常数与浮点实现并未被独立认证。|
|B2|接受降级。在线定理不能直接用二阶矩代替逐点界，但离线强凸二次内解与FTRL误差账可以组合；明确的几何成本不能隐藏。这是方法适配，未发现通用新题的必要性。|
|C-R1|保留为限范围、可行性待证的分析候选。2026原文明确讨论D及乘子半径依赖的分析损失；非精确直接gap关系仍未建立。输出、停机和参数合同须进一步固定，见下文。|
|A1|接受降为潜在。所选共同强凸正则子类已有小批量Katyusha和显式树聚合替代；仅整体强凸的完整归约尚未核清，不扩大关闭范围。|
|B1|接受降为潜在。谱球矩阵趋势滤波确有可行lift障碍，但LMO与投影同用薄SVD，凸内问题有成熟分裂；恢复收益尚未成立。|

## 具体效果与独立核查

### A1：不能把“需要新刷新算法”当作前提

回查R34 JMLR正式版PDF21 Theorem5.2及PDF23 Corollary5.7。Theorem5.2的强凸性确在共同psi上，mini-batch总梯度界使用全局L与平均Lbar两种常数。交付保留了这一限制，没有把它直接套到所有仅整体强凸问题。

令a=sqrt(kappa)、S=sqrt(N*kappa_bar)。交付的b至少为N/a和S/a，因此批次系数N/b+a+S/b<=3a；取整后总工作N+ba+S<=2(N+S)+a。独立80位计算复核五组边界，均一致。这是公式成本，不是测得加速。树聚合的通信、抽样调度、初始化与最终广播须照计；不允许为保留候选而临时禁止成熟聚合。

图直径短推导可用：degree-s的W多项式不能连接s跳外节点；若其到J的算子误差小于1/m，则所有元素非零，故图直径不大于s。谱隙收缩给s=O(log(m)/sqrt(gamma))。它依赖所列固定对称PSD混合图，不自动提供最慢节点时间最优性。一般整体强凸是否经重启/正则化也满足联合合同，留给一次明确归约，不再研发异质快照。

### B1：障碍存在，不等于绕过它就有收益

回查R02 Section7.2.2式(7.5)：四次低秩拟合、MCP差分正则与两个谱范数球确为文献模型。D满行秩并不保证在球内能提升prox点。独立分数计算得到U=(-5,4,1)/3、DU=(3,-1)、prox=(3,0)；所有提升的最小范数平方为6，而原球半径平方14/3，差4/3，阻碍成立。

谱球的精确LMO需要矩阵符号，精确投影需要截断奇异值；两者在此薄矩阵模型中都用薄SVD，不能把“投影自由”直接当便宜。MCP可写成l1减光滑凸项；R35 Algorithm3.1/Theorem3.1可用于凸prox内问题，不能用于整个非凸四次目标。已核其步长条件与算法结构。恢复与直接分裂必须使用同一点/精度证书计费，尚无s(epsilon,delta)关系，降级合理。

### D1：将已知工具接起来，比先发明算法更合理

独立检查r为Ritz上界、ell=r-eta为成功事件上的下界，得到d_dir<=d<=d_hat<=d_dir+eta。交付数值r=-478/625、eta=147/625、d=d_hat=3/2、d_dir=1581/1250均一致；另检查36组跨零/零误差区间。失败预算的有限和100/101也一致。

Jaggi2013 Algorithm2及Theorems1/2确实容许随迭代衰减的加性LMO误差。Royer–O'Neill–Wright的随机Lanczos Lemma9及式(47)给所需概率误差界；本轮NSF出版稿入口失败，改核同作arXiv1803.02924v4 PDF26，未声称两个文件逐字相同。HALLaR采用2025-09-10作者稿，终稿差异仍未核。概率区间可供算法控制失败率，不等于独立的确定性浮点PSD认证。本轮支持成熟方法链的可用性，不宣布整个改写版已复证。

### B2：核的是可用的具体证明，不是相同关键词

回查R12 Proposition8.10的FTRL路径不等式，以及R30 Theorem2的离线线性收敛入口。若每个二次子问题误差e=delta^2/(2*alpha*M)，强凸性给点误差delta/sqrt(M)。保持alpha=delta/(G*sqrt(M))，对二阶矩界取期望，三项之和不超过2*delta*G*sqrt(M)。不需将在线Th3的逐点G界冒充二阶矩界。独立有限代数检查了四个M的权重关系。

所用多面体表示、局部线性oracle、几何常数、活跃顶点分解及存储是额外信息和成本；所以不能说它突破一般域、维数无关的LMO下界，也不能说所有特定几何研究均已完成。当前泛化提法降级为方法线索恰当。

### C-R1：有出处的分析问题，但不能靠固定算法人为保存价值

回查R01 PDF14 Corollary3.5和紧随讨论：作者确实指出原始gap经stationarity转换后对D和乘子距离的依赖可能偏大。R37 PDF11 Remark2.10也明确区分精确增广子问题的外层率与未建立的非精确同率。R32的一般约束结果及R33下界只在各自模型、oracle和输出下使用；不据此断言新分析已成立。

接下来需要新增两项明确化，而非本轮整体返工：
1. “返回单个向量”不等于“非遍历最后迭代点”。加权平均也能输出一个向量；若要求最后点或固定罚参数，应说明该要求的理论/应用意义，不能只用于排除竞争结果。
2. “固定I-FALM”究竟固定更新式，还是连参数、内精度和停机都固定？原算法以stationarity门停机，Cor3.5又用epsilon_g/[2(D+Rhat)]设精度。若新gap界只在更早点成立，却仍执行旧停止门，不能据此声称实际总ACG调用已减少。允许改变输出/停机时需显式定义，并说明所需常数如何取得；若只改分析，则明确改善的是可证明界。

Manager另在作者主页和arXiv发现同作者2026-04-20的2604.18321v1《Accuracy Certificates for Convex Optimization at Accelerated Rates via Primal-Dual Averaging》。只核摘要、Section1模型和Section2证书定义：它针对光滑凸复合及可计算正则化线性oracle，未证明直接覆盖等式约束I-FALM。可定向核其证书是否提供简单替代，不因题名相似就宣称覆盖，也不自动增加完整蒸馏。

## 实际范围和可复核记录

- 读取固定SHA的REVIEW、短名单、问题证据增量、来源增量日志、有限推导/代码和AGENTS；比较基线到受审提交的15个改动文件，确认直接父提交。未独立核39份原件哈希、72份本地文件或Codex工作区，未冒充执行者完整回读。
- 原文重点核R34批量定理、R24 Moreau有限关系、R02具体矩阵模型、R35分裂、R01 gap讨论/算法停机、R37精确内解限制、R12 FTRL、R30离线方法、R29近似FW、R08A及R28替代版本。部分原页截图失败，成功视觉核R24 PDF5、R34 PDF21、R01 PDF14的官方镜像、R35 PDF6、R37 PDF11、R28预印本PDF26、R29 PDF3–4；其余上述内容据原文可读正文核查。没有全文复证这批论文。
- 本机直接下载受DNS限制，未重新计算新原件哈希；使用web原文与上述截图，不把无法取得的本地PDF说成已持有。
- 独立脚本：[manager_recent02_6aa3326.py](../checks/manager_recent02_6aa3326.py)，实际结果：[manager_recent02_6aa3326.json](../checks/results/manager_recent02_6aa3326.json)。命令`python checks/manager_recent02_6aa3326.py --output <新文件路径>`。Python3.13.5，标准库Fraction及80位Decimal；没有运行原优化器、随机Lanczos、性能基准或改写Codex结果。

原文入口：
- R34 https://jmlr.org/papers/volume18/16-410/16-410.pdf
- R24 https://arxiv.org/pdf/2004.13233
- R01 https://arxiv.org/pdf/2602.17878v1 ；镜像 https://optimization-online.org/wp-content/uploads/2026/02/Restart_Nesterov.pdf
- R02 https://arxiv.org/pdf/2606.00853v1
- R35 https://lcondat.github.io/publis/Condat-optim-JOTA-2013.pdf
- R37 https://xu-yangyang.github.io/papers/AcceleratedLALM.pdf
- R32 https://arxiv.org/pdf/1401.6607
- R33另读同作预印本 https://arxiv.org/pdf/1808.02901 ，未核NSF稿字节一致
- R12 https://arxiv.org/pdf/2610.13787v1
- R30 https://arxiv.org/pdf/1301.4666v6
- R29 https://proceedings.mlr.press/v28/jaggi13.pdf
- R28替代版本 https://arxiv.org/pdf/1803.02924
- R08A https://asujanani6.github.io/assets/pdf/HALLAR.pdf
- 新近邻线索 https://arxiv.org/abs/2604.18321 ；HTML模型 https://arxiv.org/html/2604.18321v1

本轮最主要进展是排除不必要研发并把剩余目标变得可检验；尚未形成4—6个可交导师的合格题目。下一轮要有明确的数学/价值增量，不重复以“再查几篇”结束，也不让唯一较成熟的集中凸分析自动取代P00主线。
