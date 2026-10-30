# 三臂各10seed的小时回流比较

> 2026-10-30已归档。当前状态、路径映射与复验入口见[run README](../README.md)。以下为当时的执行/分析记录；历史控制器及含旧绝对路径的命令不再作为启动入口，原始记录保持。

本级保存当前run的离线分析资产。随机、兴趣使用本次小时回流各seed0–9，时序读取正式主实验的完整seed0–9；撤回的pilot时序、旧周回流随机/兴趣、组件消融不纳入本次比较。

实时人工状态见[run README](../README.md)。[完整中文结果报告](report.md)说明图、DTW与稳定性。统计方法先冻结在contract.json，实际原始来源与核验结果见审计及结果文件；不更新正式研究流水线或论文。

| 直接资产 | 用途 |
|---|---|
| contract.json | 比较矩阵、原五类配色/比例尺、上海周DTW定义及稳定性检查约定 |
| report.md | 三臂均值图、逐seedDTW、稳定性、传播指标及限制的中文解释 |
| chronological_reuse_audit.json | 十个历史时序的实际完成、科学配置、输入、模型和回流复用审计 |
| analyze_seed10.py | 30run原始记录及官方replay核对、逐seedDTW和稳定性汇总；--check确定性复算 |
| plot_seed10.py | 原chart3b样式三臂均值图，以及逐seedDTW、均值±样本SD图 |
| [results/](results/README.md) | 330行周表、30run指标、配对差值、DTW汇总与完整对齐路径 |
| [assets/](assets/README.md) | PNG/SVG实际图件及作图来源哈希 |
| independent_verification.json | 独立实现从原始记录复算DTW和稳定性；已通过 |
| analyze.log、check.log、plot.log | 实际分析、确定性复算、绘图日志 |

方法约定：均值供给图按每seed每周五类成功发帖数先计数后等权取均值；DTW按每run五类周份额先计算，再汇总10seed均值、样本标准差和范围。均值轨迹的DTW另列，不与逐run DTW的均值混用。稳定性同时查看同seed胜出次数、去掉先导seed0、同实际模型版本子集、逐个剔除seed后的平均排名。

时序seed0–2的历史返回别名与新两臂不同，需透明保留；seed3–9同版判断以实际记录为准。现实效标与注入样本同源，作者固定类型不等于独立正文语义分类，结论仅限当前冻结设置的描述拟合与重复表现。

从本run目录使用已配置解释器复算（均为离线操作，不启动仿真）：

```bash
/Users/easylife/Project/AgentSociety/AgentSociety2/.venv/bin/python analysis/analyze_seed10.py --check
/Users/easylife/Project/AgentSociety/AgentSociety2/.venv/bin/python analysis/plot_seed10.py
```

分析会重读原始来源和官方replay，`--check`逐字节比较7份已保存数据且不覆盖；绘图从已核验结果读取并重写本级assets。独立核验JSON同时保存另一套标准库DTW函数、检查项、读取来源SHA及数值误差，不依赖生产分析函数给出结论。
