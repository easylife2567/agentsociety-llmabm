# hypothesis_4：算法策展主研究

本目录保存主假设、正式实验设计、配置及相关分析。后续主方案采用timestamp_v1；方案采用、配置验收和实际运行分开记录。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 主假设资产与实验入口 |
| [HYPOTHESIS.md](HYPOTHESIS.md) | 主假设、三臂研究对象和已接受的时间规则 |
| [SIM_SETTINGS.json](SIM_SETTINGS.json) | 正式Agent/环境类选择：CurationDiscourseAgent、CurationDynamicsSpace |
| [benchmark_curves.json](benchmark_curves.json) | 冻结真实数据UTC周级效标，上海周对照另行派生，不覆盖 |
| [experiment_1/](experiment_1/EXPERIMENT.md) | 已采用timestamp_v1设计、既有配置与历史批次 |

## 设计与证据身份

2026-10-08用户采用timestamp方案，当前设计以EXPERIMENT.md开头的timestamp_v1章节为准。三臂×3 seeds、100人、11周，保持行为参数及各臂回流。新版本尚未生成冻结配置或运行结果，后续从[主项目研究入口](../runs/2026-09-29-01-research-roadmap/README.md)推进。

实际官方单run入口仍指向既有anchored_v1_interest_s0；anchored_v1的9个已完成run继续保留。weekly_lag1是已完成的信息延迟敏感性批，weekly_lag1_event_v2是未运行且撤回设计。到达时机四格是独立单seed诊断，不改称新三臂主实验。归档路径与打包边界见[根归档清单](../ARCHIVE_MANIFEST_H4E1.md)。

保留官方run符号链接及旧派生图的兼容路径；打包时确认链接和所引用原始资产可用，不把尚未运行的主设计写成完成结果。
