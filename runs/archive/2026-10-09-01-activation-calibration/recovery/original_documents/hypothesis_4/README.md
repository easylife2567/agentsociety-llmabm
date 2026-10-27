# hypothesis_4：算法策展主研究

主研究承接[TOPIC.md](../TOPIC.md)中的问题（2）（3）：解释算法与发帖行为的循环如何塑造表征，并比较完整策展制度是否差异化推动悼念向玩梗转变。问题（1）主要由原始数据挖掘与分析回答，提供时序和平台差异参照；本目录的仿真不代替该项现实分析。总体理论为传播反馈回路视角与策展流框架，U模型负责选择性表达的操作化。

本目录保存主假设、正式实验设计、配置及相关分析。后续主方案采用timestamp_v1；方案采用、配置验收和实际运行分开记录。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 主假设资产与实验入口 |
| [HYPOTHESIS.md](HYPOTHESIS.md) | 主假设、三臂研究对象和已接受的时间规则 |
| [SIM_SETTINGS.json](SIM_SETTINGS.json) | 正式Agent/环境类选择：CurationDiscourseAgent、CurationDynamicsSpace |
| [benchmark_curves.json](benchmark_curves.json) | 冻结真实数据UTC周级效标，上海周对照另行派生，不覆盖 |
| [experiment_1/](experiment_1/EXPERIMENT.md) | 既有配置、历史设计与完成批次 |

| [experiment_2/](experiment_2/README.md) | 当前timestamp_v1主设计、九配置与离线验收；未启动LLM |

## 设计与证据身份

后续主实验从[experiment_2](experiment_2/README.md)推进：三臂×3 seeds、100人、11周；五人W13共同顺延、行为参数、17条历史池及各臂回流保持。官方按共同20:00取得资格，在interest中不置顶或保底，正常参与兴趣评分/抽样；三臂均允许官方漏读。正式源码在custom，配置在官方init；本轮实现和离线验收，不启动LLM。此前到达时机探索已交接结束；当前U标定与文稿讨论run仍保持活跃，实验运行状态以experiment_2 README为准。

实际官方单run入口仍指向既有anchored_v1_interest_s0；anchored_v1的9个已完成run继续保留。weekly_lag1是已完成的信息延迟敏感性批，weekly_lag1_event_v2是未运行且撤回设计。到达时机四格是独立单seed诊断，不改称新三臂主实验。归档路径与打包边界见[根归档清单](../ARCHIVE_MANIFEST_H4E1.md)。

保留官方run符号链接及旧派生图的兼容路径；打包时确认链接和所引用原始资产可用，不把尚未运行的主设计写成完成结果。
