# 先核主张，再写正文

|引言提出的问题|证据及归属|可兑现的正文结论|
|---|---|---|
|两点曲率为何足以控制下一步？|期刊版 PDF3–12 式 (6)、(8)–(19)、Thm 3.1；独立审查 Test A 的二次型特化，Manager 行列式抽查；[当前展开](DERIVATION.md)|三个门分别消去函数余项、同梯度项及异梯度二次型。凸二次族函数差 O(k⁻²)。|
|失去强凸性后，终点是什么？|核空间投影不变及正谱分量界；二维极限可手算。|PSD 保留函数率，点收敛至起点核分量选定的最优点。|
|同一停止要求下，四法的真实工作如何？|[本轮结果](results.json)的前 16 个 cells；输入、代码、主比较阈值均固定。|表格分列 f/g；已知 L 的优势随这四个实例改变。|
|监测何时改变可完成的工作？|monitor、tight_off、tight_on、gd_monitor 与各自主单元；核验器逐点比较。|400 步 801/1,200；900 预算时有/无监测分别停于 300/400 步。GD 预取的梯度可复用，只差终点一次。|

**证据使用顺序。** 按通用入口固定题面和配置后实施；依据保存的数值填本表后撰写 NOTE。角标和数值分别由局部代数和所有接受点重建。全一般 Hilbert 空间定理属作者；本文不估计条件数指数。四种模型覆盖正定/半正定分界；维数和单位计费使时间外推无依据。

**同事实组织练习（两版均为本轮写作）。**

- 理论。原序 “The determinant is nonnegative. Gate C makes the diagonal entries negative, and gate B bounds the step ratio from below in the determinant estimate.” 改为 “Gate C makes the diagonal entries negative. Substituting the step-ratio bound from gate B into the determinant estimate gives a nonnegative determinant.” 同一组符号事实按检查负半定性的步骤出现。
- 结果。原序 “Monitoring used 1,200 calls. Both runs took 400 steps. The run without monitoring used 801 calls.” 改为 “Both runs reached the target in the same 400 steps. Monitoring raised the call count from 801 to 1,200.” 先固定可比输出与步数，再给成本差。两版的同一终点承接相同实验语境。

整稿核对时将摘要的函数率对应到命题，降秩结论对应到核投影，比较数字对应到具名运行；实际停止依赖解析已知的最优值，步长门只依赖相邻两点。
