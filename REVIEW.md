# 第二批交付与独立验收入口

**加速专题第二批完成，待Manager独立验收。** 对照[tasks/STAGE02.md](tasks/STAGE02.md)；继承的任务基线为`91ba65b40857b33912200a32efd1ba993f7c83a5`。本文件应按交付完整SHA的GitHub blob链接审阅，固定SHA及push/远端回读凭证由会话交付提供，避免在提交内自引用尚未产生的SHA。

## 两篇三类成果

| 来源 | 研究 | 写作 | 实验 |
|---|---|---|---|
| ACC03 | [RESEARCH](papers/ACC03/RESEARCH.md)：第3/4/5章独立建模、更新/参数、证明链、结论对象和使用限制；可执行的分裂选择与能量方法 | [WRITING](papers/ACC03/WRITING.md)：证明承接与指标取舍两片段；NMF同事实组织改写、事实校准、自然性反向删减和英文练习 | [EXPERIMENTS](papers/ACC03/EXPERIMENTS.md)：信号/去噪/NMF、QP/Poisson、logistic两数据集，全部图表；6单元新协议未执行 |
| ACC04 | [RESEARCH](papers/ACC04/RESEARCH.md)：平滑族、μ/t抵消、三算法、定理4原目标实际式与证明依赖；正向原gap误差分解 | [WRITING](papers/ACC04/WRITING.md)：偏差到原目标、辅助引理到主证明；同事实改写、自然性审查和英文练习 | [EXPERIMENTS](papers/ACC04/EXPERIMENTS.md)：三模型六图、凸性/参考值/回溯成本；8单元新协议未执行 |

## 实际核验与候选判断

[V02结果](checks/stage02/RESULT.md)、[预定协议](checks/stage02/PROTOCOL.md)、[推导](checks/stage02/DERIVATION.md)、[配置](checks/stage02/config.json)、[源码](checks/stage02/verify_smoothing.py)、[全部真实输出](checks/stage02/results.json)、[stdout](checks/stage02/stdout.txt)。Python3.12.14标准库Fraction，退出0，62条精确断言；包括24偏差点、9同参数点对、3漂移情形及合法prox/模型边界。没有新增性能实验。

正向结果：同参数平滑偏差和原目标证书成立，一步prox降低原gap；重评旧点恢复两点接口。边界：变化μ的混合L=8/15不能替代同ν量L=2，代入得到1/16>1/60；同点也产生混合L=1/7。另核ReLU/max模型族非普遍凸，生成参考值非普遍最优。其影响见[候选](scope/CANDIDATES.md)：C2收缩到凸线性复合模型和漂移证书/调用成本，下一证据是完整时变能量差及同精度成本比较；C1保留可选定位，本批未深挖。没有新增候选或创新认定。

[六篇地图](scope/ACCELERATION_MAP.md)、[P00对应](scope/P00_ALIGNMENT.md)、[方法卡](knowledge/METHODS.md)、[写作卡](knowledge/WRITING.md)、[实验卡](knowledge/EXPERIMENTS.md)同步更新。P00 PDF11–15完整限定已回核；两篇不覆盖真实网络、一般非凸弱凸和高阶目标，凸集中式结果只作基础。ACC05/06仍是导航。

## 检查与真实限制

[阶段检查脚本](checks/stage02/audit_stage02.py)与[机器结果](checks/stage02/audit.json)核来源身份/页数、manifest身份字段、Manager祖先、历史字节保全、Markdown链接、UTF-8/LF/语法/凭据模式、受控写作数字/公式及6/8个未执行协议的参数与参考值。人工语义、自然性与研究/实验分项检查见[执行者自查](reviews/STAGE02_EXECUTOR_CHECK.md)；机器通过不替代Manager独立验收。

实际阅读覆盖及页图范围见[READING_LOG](sources/READING_LOG.md)。没有复制原件、全文、页图、旧库内容或无关个人资料。首批[Manager复验](reviews/STAGE01_REVISION_172f260_MANAGER_REVIEW.md)、[V01](checks/RESULT.md)与[Manager机制核验](reviews/STAGE01_4285cde_MANAGER_REVIEW.md)原样保留、未重跑，归属不混用。

限制会影响调用：ACC03 IASAPL全序列收敛并未在论文建立，Burg例与强核/对称系数条件不一致，第5章VR/随机度量印刷实现及平均点索引有缺口；ACC04原目标率不是O(k⁻²)，原证明端点/存在性等接口与非线性实验凸性有限制。本批只准确记录并检验决定性小关系，不修好全部证明。未运行性能协议、未广泛查新、未完成新算法势能或最终定题。

停止于“加速专题第二批完成，待Manager独立验收”。后续批次由Manager在验收后直接下达。
