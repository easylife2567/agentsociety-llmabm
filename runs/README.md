# 显式探索与历史决策入口

根级 `runs/` 用于用户明确开启的隔离探索，并保留已有对话决策与探索资产索引。普通任务直接在正式项目中按授权推进，不自动创建或续接 run。新 run 按“隔离探索 → 验证 → 授权采用 → 选择性落地 → 归档”处理，详细规则见[AGENTS.md](../AGENTS.md)。

当前无活跃的根级探索 run。正式研究继续从[experiment_2](../hypothesis_4/experiment_2/README.md)进入；它的引擎运行目录与本目录的探索 run 含义不同。

## 一级资产与历史导航

| 资产 | 职责 | 状态与导航 |
|---|---|---|
| [README.md](README.md) | 显式探索入口、历史主题索引与使用约定 | 当前入口 |
| [2026-09-29-01-research-roadmap/](2026-09-29-01-research-roadmap/README.md) | 工作规范与课题推进决策；附历史实验脉络 | 历史记录；现行规范查AGENTS，正式执行进入experiment_2 |
| [2026-09-29-02-injection-timing/](2026-09-29-02-injection-timing/README.md) | timestamp采纳与内容修复决策；附历史四格探索资产 | 已完成并退出，后续进入官方experiment_2 |
| [2026-10-06-01-baseline-anchor/](2026-10-06-01-baseline-anchor/README.md) | 常态锚点未采纳的决策依据；附历史数值探索资产 | 已结束留档，候选锚点未采纳 |

## 使用约定

- 只有用户明确要求创建新 run，才创建 `YYYY-MM-DD-NN-NAME/` 及README并更新索引；继续已有 run 需明确的用户指向或连续任务上下文。仅创建run的请求不自动授权实施、运行或正式落地。
- 新 run README维护目标、边界、探索状态、本级资产及证据、待办和交接；需要试改现有项目时使用隔离workspace，忽略workspace和可丢弃tmp，保全重要证据。
- 既有目录维持历史位置，其文档记载的是当时的规则和决定；规则变化以根AGENTS和工作方式记录为准，不把历史README当作自动续跑授权。
- 同主题报告持续维护，不按对话、seed或参数点拆新run。正式成果采用后回指正式资产，不复制一套正式实验工作区。
- 归档不等于采用；未授权不落地、不commit、不push。归档目录只在已选定run的归档操作需要时创建，不自动搬动现有历史目录。
- `hypothesis_*/experiment_*/runs/` 仍保存引擎批次；`data/` 和`data/runs/` 仍保存预处理材料，本规范不改变它们。
