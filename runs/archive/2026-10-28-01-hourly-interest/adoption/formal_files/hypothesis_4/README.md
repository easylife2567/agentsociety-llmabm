# hypothesis_4：算法策展主研究

主研究承接[TOPIC.md](../TOPIC.md)中的问题（2）（3）：解释算法与发帖行为的循环如何塑造表征，并比较完整策展制度是否差异化推动悼念向玩梗转变。问题（1）主要由原始数据挖掘与分析回答，提供时序和平台差异参照；本目录的仿真不代替该项现实分析。总体理论为传播反馈回路视角与策展流框架，U模型负责选择性表达的操作化。

本目录保存主假设、正式实验设计、配置及相关分析。当前主方案为hourly_return_v1：沿用timestamp信息时钟，三臂生成帖统一小时批末回流；2026-10-29已获用户授权落地，新随机/兴趣各10seed及复用时序10seed均已核验。原timestamp_v1结果保留为旧回流制度。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 主假设资产与实验入口 |
| [HYPOTHESIS.md](HYPOTHESIS.md) | 主假设、三臂研究对象和已接受的时间规则 |
| [SIM_SETTINGS.json](SIM_SETTINGS.json) | 正式Agent/环境类选择：CurationDiscourseAgent、CurationDynamicsSpace |
| [benchmark_curves.json](benchmark_curves.json) | 冻结真实数据UTC周级效标，上海周对照另行派生，不覆盖 |
| [experiment_1/](experiment_1/EXPERIMENT.md) | 既有配置、历史设计与完成批次 |

| [experiment_2/](experiment_2/README.md) | 当前hourly_return_v1：新随机/兴趣20次及复用时序10次；原始矩阵、均值图、DTW与稳定性已落地；旧timestamp结果保留 |
| [experiment_3/](experiment_3/README.md) | timestamp-interest B/D/R已补齐seed0–9；新增21次全部完成并逐次完整验收，原失败证据保留、定时汇报结束；新增种子暂未分析，旧九次分析保持 |

## 设计与证据身份

当前主实验从[experiment_2](experiment_2/README.md)推进：三臂×10 seeds、100人、11周；五人W13共同顺延、行为参数及17条历史池保持，生成帖统一批末入池、后续行动小时具备推荐资格。官方按共同20:00取得资格，在interest中不置顶或保底，正常参与兴趣评分/抽样；三臂均允许官方漏读。候选池、生命周期和选择规则仍不同。当前平均DTW兴趣最低，晚期玩梗量仍时序较高，不代表普遍最优。正式源码在custom、配置在init、原始矩阵在experiment_2/runs、分析在presentation；旧B/D/R属于旧回流制度，不与新版Full混搭。实验状态以experiment_2 README为准。

实际官方单run入口仍指向既有anchored_v1_interest_s0；anchored_v1的9个已完成run继续保留。weekly_lag1是已完成的信息延迟敏感性批，weekly_lag1_event_v2是未运行且撤回设计。到达时机四格是独立单seed诊断，不改称新三臂主实验。归档路径与打包边界见[根归档清单](../ARCHIVE_MANIFEST_H4E1.md)。

保留官方run符号链接及旧派生图的兼容路径；打包时确认链接和所引用原始资产可用，不把尚未运行的主设计写成完成结果。
