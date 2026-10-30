# 小时回流兴趣组件消融配置

本目录是小时回流候选配置，no_b/no_d/no_r各10seed；Full引用同seed新兴趣主实验，不新增Full运行。全部配置显式声明`arrival_agent_return_policy=next_batch`：同小时批末统一入池，从后续行动批次可见。每人每周一次、外部输入、人口、行为、提示、周龄生命周期和步骤保持来源版本。

| 直接资产 | 用途 |
|---|---|
| [configs/](configs/README.md) | 30份候选配置及逐文件索引 |
| [manifest.json](manifest.json) | 来源/机制/输出哈希、配对、未来输出与预算准备上界 |
| [README.md](README.md) | 本级索引和准备边界 |

生成器为[prepare_hourly_return.py](../../../experiment_2/init/prepare_hourly_return.py)，从项目根执行`$PYTHON_PATH hypothesis_4/experiment_2/init/prepare_hourly_return.py --check`只读重算核对。默认生成也拒绝覆盖不一致文件，不调用旧生成器。steps引用旧冻结字节，没有复制或改写。

未来输出根为`hypothesis_4/experiment_3/runs/hourly_return_bdr_v1`，本次不创建引擎输出或账本。新批独立额外请求准备上界为3300，不借用或清零旧批账本；所有execution_authorized均为false，运行时限、费用和实际模型尚未冻结。生成成功不代表运行通过，时序复用与Full可用性均以manifest中的待验状态为准。

旧周回流结果和checkpoint保持，不用于新小时回流条件中途接续。消融仅改变一个组件参数与独立预算账本，并与同seed新Full配对；不将旧周回流消融直接减去新Full。
