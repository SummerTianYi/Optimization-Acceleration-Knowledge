# 首批定向修订交付

本次基于Manager提交`e53d9271e89b832a6996e2eff225be94416e547f`完成R1—R3，并落实用户追加的自然学术表达与防御性写作审查。**首批定向修订完成，待Manager复验。** 研究/数学主体、原实验审查及V01已有分项通过结论；本次自查不替代复验。

| 项目 | 修订前 | 修订后与入口 |
|---|---|---|
| R1 写作 | 两组例子主要纠正事实，未做到同事实组织；ACC01摘要页码误指目录 | 保留旧例并标“事实校准”，每篇另固定四条有原文定位的共同事实，两版准确且信息相同。ACC01按目标—网络—更新组织；ACC02按条件—机制—函数率/弱收敛组织。摘要改为PDF6/印I。两篇均有具体反向删减对照，必要条件按语境保留，内部审查与范例分开。见[ACC01](papers/ACC01/WRITING.md)、[ACC02](papers/ACC02/WRITING.md)、[写作方法](knowledge/WRITING.md) |
| R2 实验协议 | ACC01调参机会不对称且选参规则未闭合；ACC02敏感性组合、相对量与回溯细节未定义 | [E01](papers/ACC01/EXPERIMENTS.md)主比较每法30次训练，明确选择/平手/失败、样本Lf与全局μ，分开消融和敏感性；[E02](papers/ACC02/EXPERIMENTS.md)固定参数，定义相对函数差、16个计划性能单元及回溯/成本/失败规则。**全部性能协议继续未执行** |
| R3 方向边界 | C1被当成网络方向前置门；P00联系过宽 | [候选](scope/CANDIDATES.md)将C1保留为可选集中凸前置，§2.3(3)仅潜在联系；网络研究不依赖C1先通过。C2等ACC03/04，未增候选或先做C1。同步[地图](scope/ACCELERATION_MAP.md)与[方法卡](knowledge/METHODS.md) |

核对记录见[修订自查](reviews/STAGE01_REVISION_EXECUTOR_CHECK.md)、[检查脚本](checks/check_stage01_revision.py)及[真实结果](checks/results/stage01_revision_audit.json)。检查涉及三份相关原件身份/页数、两组事实锚点、公式/条件句、调参计划组合、四种选择边界、相对链接及历史字节保全；没有生成优化轨迹。事实等价与自然性另作人工逐项核对。

历史与归属：[Manager审核](reviews/STAGE01_4285cde_MANAGER_REVIEW.md)、[原修订任务](tasks/STAGE01_REVISION.md)、[Manager脚本](checks/manager_check_4285cde.py)和[结果](checks/results/manager_stage01_4285cde.json)保持原样。Manager新增的是八配置、160条80位ACC02有限机制检查，未计为执行者性能运行；[V01](checks/RESULT.md)及其输入输出未改写、未重跑。[原首批固定交付](https://github.com/SummerTianYi/Optimization-Acceleration-Knowledge/blob/4285cde36d8efa3f870bae95f4080249fba3f2c2/REVIEW.md)保留。

本次没有重蒸馏两篇、修复ACC01整篇、运行性能或候选实验、扩大查新、访问旧库或制作导师汇报。候选新颖性尚未确认，ACC03—06仍未完整蒸馏。复验通过后默认由Manager下达ACC03/ACC04，当前不自行启动。

当前状态见[STATE](STATE.md)，来源增量见[阅读日志](sources/READING_LOG.md)。提交和远端回读后，以最终回执完整SHA对应的本页为固定REVIEW；仓库保持私有、非fork、默认main，原件和交接包在Git之外。
