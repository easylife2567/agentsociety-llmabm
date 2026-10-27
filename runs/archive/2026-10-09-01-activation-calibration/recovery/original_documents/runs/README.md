# 显式探索与历史决策入口

根级 `runs/` 用于用户明确开启的隔离探索，并保留已有对话决策与探索资产索引。普通任务直接在正式项目中按授权推进，不自动创建或续接 run。新 run 按“隔离探索 → 验证 → 授权采用 → 选择性落地 → 归档”处理，详细规则见[AGENTS.md](../AGENTS.md)。

当前活跃探索见下表。正式研究从[experiment_2](../hypothesis_4/experiment_2/README.md)进入；它的引擎运行目录与本目录的探索 run 含义不同。

## 活跃探索

| run | 目标 | 状态 |
|---|---|---|
| [2026-10-09-01-activation-calibration/](2026-10-09-01-activation-calibration/README.md) | 核查U/B标定、对齐作者文稿；在本run组织两研究写作 | 两研究结构已采用；最新逐段写作报告与最小补充安排完成，保留原主设计，不再扩展U实验；两份报告已落实paper，新版LLM主批已启动，正文尚未重写 |

## 一级资产

| 资产 | 用途 |
|---|---|
| [README.md](README.md) | 活跃探索与使用约定 |
| [archive/](archive/README.md) | 已归档run索引、历史证据和恢复说明 |

## 使用约定

- 只有用户明确要求创建新 run，才创建 `YYYY-MM-DD-NN-NAME/` 及README并更新索引；继续已有 run 需明确的用户指向或连续任务上下文。仅创建run的请求不自动授权实施、运行或正式落地。
- 新 run README维护目标、边界、探索状态、本级资产及证据、待办和交接；需要试改现有项目时使用隔离workspace，忽略workspace和可丢弃tmp，保全重要证据。
- 已归档run从archive入口查阅，其文档记载的是当时的规则和决定；现行规则以根AGENTS为准，历史README不构成自动续跑授权。
- 同主题报告持续维护，不按对话、seed或参数点拆新run。正式成果采用后回指正式资产，不复制一套正式实验工作区。
- 归档不等于采用；未授权不落地、不commit、不push。归档目录只在已选定run的归档操作需要时创建，不自动搬动现有历史目录。
- `hypothesis_*/experiment_*/runs/` 仍保存引擎批次；`data/` 和`data/runs/` 仍保存预处理材料，本规范不改变它们。
