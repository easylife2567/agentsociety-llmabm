# 当前实验清单：仅真实帖子注入时机

日期：2026-09-27。用户已收窄范围；本清单替代v1的36条广泛重设计运行。尚未启动仿真。

[当前最小方案](EXPERIMENT_PLAN.md)；原24项审计仅为背景，不要求全部修复。

| 任务 | 状态 | 范围 |
|---|---|---|
| 时间与样本静态审计 | COMPLETE | 已有JSON和源hash |
| interest/random分时到达与行动调度 | TODO | 原250条、原推荐/行为规则；Agent帖继续次周回流 |
| 计数、恢复、监控适配 | TODO | 只改新时间调度必需部分 |
| 无LLM边界及恢复验证 | TODO | 按最小方案验收不变量 |

| Run ID | 周窗 | 行动机会上限 | 状态 |
|---|---|---:|---|
| arrival_timing_only_smoke_interest_s0 | W12-W14 | 300 | PLANNED |
| arrival_timing_only_interest_s0 | W12-W22 | 1100 | PLANNED |
| arrival_timing_only_interest_s1 | W12-W22 | 1100 | PLANNED |
| arrival_timing_only_interest_s2 | W12-W22 | 1100 | PLANNED |
| arrival_timing_only_smoke_random_s0 | W12-W14 | 300 | PLANNED |
| arrival_timing_only_random_s0 | W12-W22 | 1100 | PLANNED |
| arrival_timing_only_random_s1 | W12-W22 | 1100 | PLANNED |
| arrival_timing_only_random_s2 | W12-W22 | 1100 | PLANNED |

6次完整运行（6,600次行动机会）＋2个短烟测（600次）。chronological沿用既有结果。参数不重拟合，不调整250条，不新增算法臂。
