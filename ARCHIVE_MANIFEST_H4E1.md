# H4-E1 实验归档总索引

更新日期：2026-09-28。

AgentSociety 官方工作区约定提供 `hypothesis_{id}/experiment_{id}/run` 单 run 目录，没有规定多批次历史归档结构。本项目保留该兼容入口，并按实验的证据地位组织本地 `archive/`。

## A. 当前正式批：anchored_v1

路径：`archive/hypothesis_4_experiment_1_batches/formal_current/anchored_v1/`

- 设计：random / chronological / interest × 3 seeds。
- 完成性：9/9 完整；周级臂 11/11 步，chronological 693/693 批次。
- replay：每个 run 有 1100 行 Agent 状态、11 行环境状态。
- 周级顺序：本周真实帖先作为外部刺激进入并冻结全部 Agent 的 feed；本周 Agent 帖在全部 Agent 行动结束后统一提交，从下一周起对其他 Agent 可见。
- 证据地位：恢复为当前主分析输入。该顺序与周级刺激—响应解释一致，并避免 Agent 在同一步内因执行先后互相影响。
- 内容：`raw/` 原始 run、`_derived/` 冻结派生结果、`config/` 自包含配置、`inventory.json` 和 `checksums.sha256`。

为保持既有论文和图表链接可读，Git 跟踪的派生结果副本仍位于 `hypothesis_4/experiment_1/runs/anchored_v1/_derived/`。官方单 run 兼容入口 `hypothesis_4/experiment_1/run` 指向本批 `anchored_v1_interest_s0`。

## B. 已完成的注入时机敏感性批：weekly_lag1

路径：`archive/hypothesis_4_experiment_1_batches/formal_superseded/weekly_lag1/`

- 设计：普通真实帖与 Agent 帖都严格延迟一期；W13 官方讣告保持同周可见；interest / random × 3 seeds。
- 完成性：6/6 完整；每个 run 11/11 周、1100 行 Agent 状态、11 行环境状态。
- 归档原因：严格一期滞后把原 W13 响应拆到 W13–W15，改变了研究对象，实际估计的是“信息延迟效应”，不再适合作为主方案。
- 证据用途：保留为注入时机敏感性检验，不与当前主结果混用。
- 内容：`raw/` 原始 run、`_derived/` 冻结派生结果、`config/` 配置与样本、`tools/` 复现实用脚本、清单与校验和。

活动目录 `hypothesis_4/experiment_1/runs/weekly_lag1/` 只保留旧链接所需的派生结果兼容副本和归档指针，不含原始 run。

## C. 未运行且已撤回的设计：weekly_lag1_event_v2

路径：`archive/hypothesis_4_experiment_1_batches/design_superseded/weekly_lag1_event_v2/`

该设计原计划在严格一期滞后的基础上补充 W23 drain/readout 周。它没有启动正式实验，现仅保留配置、工具和设计记录用于审计，不列为待运行方案。相关预测和时序诊断继续保存在 `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/`。

## D. 更早的历史实验

路径：`archive/hypothesis_4_experiment_1_history_20260915/`。

其中保存旧公式正式批、探针与烟测、writer 事故样本、中断 run 及对应配置和派生产物。细目见 `ARCHIVE_MANIFEST_H4E1_history_20260915.md`。
