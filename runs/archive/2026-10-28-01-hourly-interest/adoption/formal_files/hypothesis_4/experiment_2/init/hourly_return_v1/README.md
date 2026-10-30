# 已采用的统一小时回流主实验配置

本级接收已经验收的主实验30份准备配置：random/chronological/interest各seed0–9，全部显式`arrival_agent_return_policy=next_batch`。只接收experiment_2；未运行双实验准备器，也没有生成或修改experiment_3消融。

| 直接资产 | 用途 |
|---|---|
| configs/ | 30份机制配置；其他科学参数与对应timestamp配置一致 |
| manifest.json | 本级接收清单及配置SHA，指向正式实际结果矩阵；不授权重跑 |
| preparation_manifest.json | 探索准备期manifest的原字节副本；其中planned/pending、60条件和预算是当时的规划，不代表实际运行范围 |

实际随机/兴趣来自两批独立操作配置，预算字段与准备版不同，见[实际结果及执行记录](../../runs/hourly_return_v1/README.md)中的SOCIETY与原计划；时序复用原完整10seed，不声称运行了本级时序配置。步骤表与冻结输入继续使用父级已有steps_s0–9.yaml、inputs/，不重抽、不覆写旧manifest、默认init入口或旧配置。

本次仅采用已完成的新版主实验，不授权新的模型请求、其他seed或组件消融。下一次启动须根据新授权另行冻结操作预算，不能复用已结束批次的剩余额度。
