# Optimization-Acceleration-Knowledge

独立私有研究知识库，用于依据导师计划书P00及六篇加速论文开展文献蒸馏、方向筛选和候选课题准备。当前不制作导师汇报材料。

先读 [当前状态](STATE.md) 和 [本批交付索引 REVIEW](REVIEW.md)。有效任务为 [STAGE01](tasks/STAGE01.md)，完整规划与验收标准为 [MASTER_PLAN](tasks/MASTER_PLAN.md)。科学自查不代表Manager独立验收。

- [P00范围](scope/P00_ALIGNMENT.md)、[六篇地图](scope/ACCELERATION_MAP.md)、[候选初版](scope/CANDIDATES.md)
- [材料清单](sources/manifest.json)与[实际阅读日志](sources/READING_LOG.md)
- ACC01：[研究](papers/ACC01/RESEARCH.md) / [写作](papers/ACC01/WRITING.md) / [实验](papers/ACC01/EXPERIMENTS.md)
- ACC02：[研究](papers/ACC02/RESEARCH.md) / [写作](papers/ACC02/WRITING.md) / [实验](papers/ACC02/EXPERIMENTS.md)
- [实际核验V01](checks/RESULT.md)：精确计算ACC01局部递推及边界，含代码、配置、命令和真实结果
- 可复用[研究方法](knowledge/METHODS.md)、[写作方法](knowledge/WRITING.md)、[实验方法](knowledge/EXPERIMENTS.md)

原件、CAJ、ZIP、全文提取、页图和大数据保存在仓库之外。只提交元数据、短定位、原创蒸馏与小复算结果。未fork、clone、导入或修改旧研究仓库；科学判断不继承旧候选或旧验收。

V01复跑（Python3.9+标准库，无第三方包）：

```sh
python checks/verify_acc01_relation.py --config checks/config.json --output checks/results/acc01_relation.json
```

该命令预期报告原局部关系失效，退出码0表示复算和本例断言完成，**不表示论文定理通过**。协议、运行环境和输出哈希在checks目录。
