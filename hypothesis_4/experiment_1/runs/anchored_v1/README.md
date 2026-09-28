# anchored_v1 当前正式批的派生结果兼容包

本批采用锚定式效用 `U_i=B_i+R_i(D_i-B_i)`，包含 random / chronological / interest 三种推荐制度 × 3 seeds，共 9 个完整 run。

2026-09-28 经注入时机复核，anchored_v1 恢复为当前主方案。周级臂把本周真实帖视为外部刺激，在 Agent 决策前进入环境并冻结全部 feed；本周 Agent 帖使用 pending buffer，在全部 Agent 完成后统一提交，从下一周起对其他 Agent 可见。这个口径消除了同一步内的 Agent 执行顺序偏差，也与论文中的“周级刺激—响应”表述一致。

9 个原始 run 位于 `archive/hypothesis_4_experiment_1_batches/formal_current/anchored_v1/raw/`。本目录保留 Git 跟踪的 `_derived/` 副本，供论文、审阅记录和图表链接稳定引用。

## 完成状态

- random：3/3 run 完成，每个 11/11 周；
- interest：3/3 run 完成，每个 11/11 周；
- chronological：3/3 run 完成，每个 693/693 小时批次；
- 每个 run 均有 1100 行 Agent 状态和 11 行环境状态。

AgentSociety 官方单 run 兼容入口 `../../run` 指向归档中的 `anchored_v1_interest_s0`。完整配置、原始 replay、冻结派生结果、清单和校验和见根目录归档索引。
