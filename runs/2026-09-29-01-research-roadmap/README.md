# 课题推进与工作入口

## 目标与范围

将用户提供的工作规范落实到本课题，让已有尝试可查、后续实验有明确决策顺序。本任务负责规则、导航与主项目研究推进方案；2026-10-08接收已采用timestamp设计的交接，不执行时间诊断或新LLM实验。遵照用户澄清，保留 AgentSociety2 官方目录；根级 runs 管研究思路，用户新增的 data 存实验预处理数据。

## 一级资产

| 资产 | 职责与用法 |
|---|---|
| [README.md](README.md) | 本任务目标、实时进度、待决策事项和交接入口 |
| [2026-09-29-01-research-roadmap.md](2026-09-29-01-research-roadmap.md) | 已有实验脉络、依据、推进流程及验收标准；同主题持续更新 |
| `tmp/` | 临时检查输出；Git 忽略，不存唯一结果证据 |

## 实时进度

- 已完成：工作规范与官方目录导航落地；2026-10-08按用户裁定接收timestamp方案，官方EXPERIMENT.md新增完整主设计，TOPIC及假设/实验导航同步。
- 当前：本目录为主项目活动研究入口；到达时机任务已完成并退出。新版本设计标识timestamp_v1，配置和运行结果尚未生成；既有anchored_v1仍是实际兼容run来源。
- 下一步：按官方主设计准备三臂配对配置、预算接线与离线验收，尤其核对chronological的小时回流和现有ArrivalSchedule只支持两臂的实现边界；已有代码通过本任务patch落实。
- 授权边界：已采用timestamp和既有内容修复要求，保留行为参数及各臂回流制度。9-run是既有主研究矩阵，本次没有启动授权；新模型调用与费用冻结后再运行，不使用诊断旧预算或checkpoint。

## 待决策与后续交接

方案选择已完成，不重复询问是否采用timestamp。主实验当前设计见[EXPERIMENT.md](../../hypothesis_4/experiment_1/EXPERIMENT.md)，本任务报告维护接入依据与验收方法，细节不复制到README。45条额外内容筛查的人工确认、正文测量桥接及新批运行费用仍需后续处理；这些不撤销已采用的到达规则。

历史来源冲突按实际入口处理：hypothesis_4/README.md及HYPOTHESIS.md的weekly_lag1/event_v2状态已纠正。`presentation/hypothesis_4/data/analysis_sources.json`仍属于旧分析上下文，不能用作尚未运行的timestamp_v1数据源；新批分析就绪前不替换实际兼容入口或伪造分析来源。

控制agent已通过CLI完成analysis→experiment_config的reroute，revision_round=8，状态needs_revision，配置验收尚未完成。规范阶段推送的工作簿仍保留原用途，不自动替换冻结主样本或标签。

## 审查与验证

2026-10-08主设计接入经独立timing_review审查PASS；确认保留原行为参数、完整制度及回流差异、配对行动表和新批预算边界。按意见纠正anchored_v1导航身份，将到达任务的旧拒答阻断要求显式标为历史；点明chronological自增pid并列排序与未接共享额外请求预算这两项真实实施差异。文档本地链接与git diff --check通过，未修改正式代码、冻结配置或原始结果；配置准备和新实验验收尚未完成。

独立子 agent 已完成一次关键方案审查，通过；确认历史分类、CLI 单写者、README 状态职责及运行授权边界，无阻塞问题。随后按用户澄清显式保留官方目录并区分 runs/data 职责。已检查5份文档的本地链接、AGENTS.md 符号链接及文档可跟踪性；根级任务 tmp 忽略生效，git diff --check 通过。提交范围限定 CLAUDE.md、根 README、.gitignore 和本次新增 runs 文档；不包含既有 Excel 修改。提交记录由 Git 按这些路径查询，不另建提交台账。
