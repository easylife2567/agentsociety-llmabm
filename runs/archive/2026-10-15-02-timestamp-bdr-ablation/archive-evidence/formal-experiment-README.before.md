# Experiment 3：timestamp-interest的B、D、R消融

用户于2026-10-16明确接受九次正式LLM消融、同seed配对结果及D/R过程解释，并授权落实主工作区。本目录是已采用成果的实时交接入口；来源探索run保留，不自动归档。本次落地不新增LLM调用、不改行为机制、不改主实验或论文正文、不提交Git。

九次消融已全部完成：每次693步、100人×11周=1100次机会；合计2652条成功发布、2657次模型请求、额外5次内容重写。主模型请求标识固定deepseek-v4-1-flash-260910。复用experiment_2三个同seed timestamp-interest Full，配对分析共12单元、13200次机会。定时器已暂停，没有运行或待启动任务；采用现有结果不构成新批授权。

| 直接资产 | 用途 |
|---|---|
| [EXPERIMENT.md](EXPERIMENT.md) | 已采用的条件、固定项、窗口、比较口径、预算历史与局限 |
| [init/](init/README.md) | 九份科学配置、冻结Full、输入、steps与原manifest，字节保持 |
| [runs/](runs/README.md) | 已完成第二批的独立正式副本，原始计划/日志/Agent/replay不改写 |
| [analysis/](analysis/README.md) | 正式路径的只读提取、绘图、报告及离线核验工具 |
| [payloads/](payloads/README.md) | 预设分析计划、用户已确认的三项结论与图契约 |
| [checks/](checks/README.md) | 在正式位置实际执行的配置、原始复算、机制和落地完整性检查 |
| [provenance/](provenance/README.md) | 原始失败、路径修正/并行交接、历史来源和新旧路径映射 |
| [adoption.json](adoption.json) | 用户接受与落地授权；独立模型审阅和正式harness签署仍为false |
| [.gitignore](.gitignore) | 原始引擎产物、可重建缓存的Git边界，不授权删除 |

正式报告和全套图表见[配对分析](../../presentation/hypothesis_4/timestamp_bdr_v1/README.md)，双语综合见[综合入口](../../synthesis/timestamp_bdr_v1/README.md)。预设差值均为消融−同seed Full：去B晚期周供给−7.00帖；去D晚期玩梗型作者发言率−30.70个百分点；去R事件后全体发言率+30.07个百分点。三个seed方向一致，保留实际配对值和范围，不报告显著性或置信区间。

去D前期释放表达，玩梗型作者W12–W18平均由1.33增至61.33条，晚期由36.33降至13.00条；去R的全窗口总量由219.00增至520.67条，但玩梗型作者由37.67降至25.67条。逐周轨迹、阅读/累计接触、原始Agent12记录及34次去R晚期发言损失核验均已保存；这是支持闭环解释的过程证据，不是独立中介分解。

作用结论仅限冻结interest配置、3个seed及相同人口/调度表。Full与消融分批运行，API路径/返回模型标识存在差异，无法确认后台完全相同；R=1同时消除B权重，三项差值不可相加为贡献率。固定作者类型、环境阅读标签、既有词表正文标签分别保留，均不冒充人工语义金标。

原始配置和运行计划中的历史路径不批量重写；当前实际复算来源由presentation中的source_index.json指向正式目录，映射见provenance/path_map.json。正式工具不依赖活跃探索run或其workspace。共享账本实际记录仍为第二批_extra_attempts.count=5；不重置预算或提供自动重跑入口。

离线重建及验证命令见analysis/README。主项目机器流水线状态本次保持原样：用户接受已如实登记，但未伪造独立模型review或validate-synthesis签署。未改论文正文，供后续按已接受证据写作。
