# 原目标与固定点的两组实算

|平滑参数|到平滑固定点的推进步数|梯度 / 向量近端调用|首次原目标差 ≤ 0.02|终点原目标差|终点平滑目标差 / 近端映射范数|
|---|---:|---:|---:|---:|---:|
|1/2|7|8 / 8|未达到|5/16|0 / 0|
|1/64|255|256 / 256|253|3/256|0 / 0|

每个输出点各评价一次原目标与平滑目标，另用闭式参考点作一次性离线核准。第二组在第 253 步原目标差为 5/256，近端映射无穷范数仍为 1/2。两组的 264 行均使用有理数验过偏差界，两终点均等于分坐标解析解。[配置与推导](README.md) · [小型汇总、运行和冻结哈希](results.json)

**English results.** Both smoothing levels reached a proximal fixed point. With smoothing parameter 1/2, the original objective gap at that point was 5/16, above the target of 0.02. Reducing the parameter to 1/64 brought the original gap below target at update 253, two updates before the proximal mapping vanished. A fixed-point test and an original-objective test can therefore return different answers on the same iterate. The smaller smoothing parameter also reduced the gradient step, increasing the number of proximal evaluations from 8 to 256.

**迁移记录。** 直接复用了固定输出、对齐两种证书、先推导再运行及主张到原始数字的检查。必须改掉的是光滑梯度更新和单一函数差：软阈值来自保留的非光滑项，平滑偏差进入原目标；每次近端（含终止检查）单列计费。难点出在坐标跨零处，必须用区间次梯度而不能把符号函数当处处可导。原函数这里有可计算的全局下界，推广到无已知参考的耦合问题仍需另建下界。主示范与通用入口执行前已冻结，迁移后逐文件核对一致。终稿随后仅将两个主示范数学文档及迁移推导的公式分隔符转换为 GitHub 渲染格式，并清理了复跑说明的一处重复标点。调整前后哈希见汇总；通用方法、源码、协议和结果保持冻结版本。此为同一执行者的跨结构自测；不同模型或无库对照的表现仍待独立测试。
