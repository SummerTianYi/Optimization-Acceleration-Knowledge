# Optimization-Acceleration-Knowledge

独立私有研究知识库，依据导师计划书P00及新六篇加速论文开展蒸馏、方向筛选与候选课题准备。当前不制作导师汇报材料。

**首批ACC01/ACC02已通过Manager验收；第二批ACC03/ACC04完整蒸馏、V02小核验及候选更新已完成，待Manager独立验收。** 先读[STATE](STATE.md)、[REVIEW](REVIEW.md)、[STAGE02](tasks/STAGE02.md)。范围与通用标准见[MASTER_PLAN](tasks/MASTER_PLAN.md)、[AGENTS](AGENTS.md)。

- [P00范围](scope/P00_ALIGNMENT.md)、[六篇地图](scope/ACCELERATION_MAP.md)、[候选](scope/CANDIDATES.md)
- [材料清单](sources/manifest.json)、[阅读日志](sources/READING_LOG.md)
- ACC01：[研究](papers/ACC01/RESEARCH.md) / [写作](papers/ACC01/WRITING.md) / [实验](papers/ACC01/EXPERIMENTS.md)
- ACC02：[研究](papers/ACC02/RESEARCH.md) / [写作](papers/ACC02/WRITING.md) / [实验](papers/ACC02/EXPERIMENTS.md)
- ACC03：[研究](papers/ACC03/RESEARCH.md) / [写作](papers/ACC03/WRITING.md) / [实验](papers/ACC03/EXPERIMENTS.md)
- ACC04：[研究](papers/ACC04/RESEARCH.md) / [写作](papers/ACC04/WRITING.md) / [实验](papers/ACC04/EXPERIMENTS.md)
- [V02实际核验](checks/stage02/RESULT.md)、[第二批分项自查](reviews/STAGE02_EXECUTOR_CHECK.md)、[阶段检查](checks/stage02/audit.json)
- [V01实际核验](checks/RESULT.md)、[首次Manager审核](reviews/STAGE01_4285cde_MANAGER_REVIEW.md)、[修订自查](reviews/STAGE01_REVISION_EXECUTOR_CHECK.md)
- [方法](knowledge/METHODS.md)、[写作](knowledge/WRITING.md)、[实验](knowledge/EXPERIMENTS.md)

STAGE01/STAGE01_REVISION及对应检查为历史轮次，后批不机械重跑旧文件白名单。原件、CAJ、ZIP、全文提取、页图、大数据在仓库之外；只提交元数据、短定位、原创分析、代码和小复算结果。旧库不访问、不继承其研究内容。性能协议未执行，候选创新未确认。

V01历史复算入口（不要覆盖正式输出，可传另一路径）：

```sh
python checks/verify_acc01_relation.py --config checks/config.json --output <独立复算输出路径>
```

该命令退出码0表示复算与本例断言完成，不表示原论文定理通过。新轮次按实际任务接受固定SHA验收。
