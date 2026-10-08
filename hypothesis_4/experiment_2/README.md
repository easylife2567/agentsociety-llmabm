# Experiment 2：timestamp策展三臂主实验

## 目标与范围

落实已采用的timestamp方案：三臂真实信息时钟、配对行动表、原行为参数和各臂回流制度，继承保留发言内容修复。100人×11周×3算法×3 seeds，共9 runs、9900次行动机会。本轮只准备及离线验收，不调用LLM、不启动实验。

根级runs探索工作已交接，本目录为当前官方实验工作入口；不另建研究任务目录。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 目标、一级资产、实时进度与交接 |
| [EXPERIMENT.md](EXPERIMENT.md) | 完整主设计、基线代码证据、落地方案、patch解释、验收及结论边界 |
| [init/](init/README.md) | 标准库生成器、冻结输入、九份配置、每seed步骤及manifest |
| [2026-10-08-01-timestamp.patch](2026-10-08-01-timestamp.patch) | 三个既有正式模块的最终补丁；基线d4a8319a6477d818dc5efbcc1d475625f14a42fc |
| [2026-10-08-02-functional-verification.json](2026-10-08-02-functional-verification.json) | 24项禁网功能验收结果，0模型调用 |
| [2026-10-08-03-configuration-verification.json](2026-10-08-03-configuration-verification.json) | 官方工作流结果、九配置/900工作区核验、54份源码及资产哈希、干净基线应用证据 |

## 实时进度

- 已完成：核对原设计已采用timestamp、旧主配置尚未接线的差距；通过官方scan-modules、experiment-config prepare/validate/info/run/check；九配置与输入独立冻结。
- 正式代码：三臂均激活arrival路径；chronological使用稳定时间排序、批末入池及当周供给记账，random/interest保持次周回流；共享额外请求990次与新ledger实际接线。原行为参数不变。
- 功能验证：24项通过、0失败；九窗环境演练各693批、1100行动、11周，未来曝光0；同批隔离、分臂回流、跨周供给守恒、恢复一致性和额度耗尽兜底通过。历史20必查样本覆盖两类行动入口；网络连接尝试0、LLM调用0。
- 审查：方案冻结前独立timing_review通过；实现后发现并修正时序周观测遗漏，新增实际发布跨周检查，修正可见词提示说明。最终patch和冻结证据独立终审PASS。
- 机器阶段：控制agent通过CLI将experiment_config登记completed、verification complete；current_stage自动进入run_experiment，继承reroute状态needs_revision、verification not_started。该状态表示尚待新批运行，并非新批执行失败。阶段metadata明确hypothesis_id=4、experiment_id=2；where-am-i顶层ID仍为空，启动时须显式指定，不手改机器JSON。
- 授权：本轮只完成准备及离线验收；manifest execution_authorized=false、active_wall_seconds=null。没有新LLM结果、监督器、checkpoint或定时器。
- 下一步：用户确定新批模型/发送范围、活动时长或费用预算后，按官方run-experiment入口显式选择experiment_2，并按manifest逐run执行九格矩阵；本轮到此交付准备结果。

## 交接边界

行为参数、B和各臂回流保留；baseline-anchor候选未采纳，B的W13尺度/floor限制见方案。45条额外筛查命中未全人工确认，正文与作者分类仍需分别解释。本轮功能成功不代表新生成质量或曲线已经改善。旧四格预算、checkpoint、兼容run链接及旧分析来源不复用；原始结果保持历史位置。
