# hypothesis_4：算法策展主研究

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

2026-10-08用户采用timestamp方案，当前主实验从[experiment_2](experiment_2/README.md)推进。三臂×3 seeds、100人、11周，保持行为参数及各臂回流；现有配置的技术离线验收已完成。用户明确interest保留官方置顶，random/chronological允许漏读，17条历史池暂时接受；已按用户采纳的方案共同顺延5个过早的W13悼念决策，三臂三seed共表，其余人/周保持；interest原10槽官方首位，22人均在事件后决策；30项禁网离线验收通过，LLM尚未启动。根级runs探索已交接结束。

实际官方单run入口仍指向既有anchored_v1_interest_s0；anchored_v1的9个已完成run继续保留。weekly_lag1是已完成的信息延迟敏感性批，weekly_lag1_event_v2是未运行且撤回设计。到达时机四格是独立单seed诊断，不改称新三臂主实验。归档路径与打包边界见[根归档清单](../ARCHIVE_MANIFEST_H4E1.md)。

保留官方run符号链接及旧派生图的兼容路径；打包时确认链接和所引用原始资产可用，不把尚未运行的主设计写成完成结果。
