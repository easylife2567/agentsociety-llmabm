# 实验运行清单

日期：2026-09-27。设计阶段；所有仿真均未运行。用户预算选择：均衡。

[完整方案](EXPERIMENT_PLAN.md) · [机器可读运行表](injection_timing_20260927/planned_runs.json)

## 先行任务

| 任务 | 状态 | 验收条件 |
|---|---|---|
| 源码依赖与冻结输入审计 | COMPLETE | 24项审计、可复现JSON及源文件哈希 |
| v2数据口径、通用调度、知识边界及测量实现 | TODO | 方案B0全部不变量通过 |
| 200条无LLM迁移诊断 | TODO | 五种状态×I/R×20诊断seed；仅诊断，不冒充完整仿真 |
| 训练窗校准及真实文本一致性检查 | TODO | 参数、代理近似及来源冻结 |
| 短烟测测时/费用与manifest冻结 | TODO | 训练窗负控、恢复及发布日志通过 |
| B4盲标与测量敏感性 | TODO | 复用全部生成文本；不计入仿真条数 |

## 运行矩阵

I=兴趣；M=去兴趣匹配控制；R=共同候选池均匀；C=共同候选池时序。正式每条100人×11周，每人每周一次机会。

| Run ID | 实验块 | 输入 | q | seed | 周窗 | 优先级 | 状态 |
|---|---|---|---:|---:|---|---|---|
| arrival_v2_smoke_I_s0 | B0 | full | 0.005 | 0 | W12-W14 | MUST | PLANNED |
| arrival_v2_smoke_M_s0 | B0 | full | 0.005 | 0 | W12-W14 | MUST | PLANNED |
| arrival_v2_smoke_R_s0 | B0 | full | 0.005 | 0 | W12-W14 | MUST | PLANNED |
| arrival_v2_I_full_q005_s0 | B1 | full | 0.005 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_q005_s1 | B1 | full | 0.005 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_q005_s2 | B1 | full | 0.005 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_cutoff_W19_q005_s0 | B1 | cutoff_W19 | 0.005 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_cutoff_W19_q005_s1 | B1 | cutoff_W19 | 0.005 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_cutoff_W19_q005_s2 | B1 | cutoff_W19 | 0.005 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q005_s0 | B1 | full | 0.005 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q005_s1 | B1 | full | 0.005 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q005_s2 | B1 | full | 0.005 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_cutoff_W19_q005_s0 | B1 | cutoff_W19 | 0.005 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_cutoff_W19_q005_s1 | B1 | cutoff_W19 | 0.005 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_cutoff_W19_q005_s2 | B1 | cutoff_W19 | 0.005 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_R_full_q005_s0 | B1 | full | 0.005 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_R_full_q005_s1 | B1 | full | 0.005 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_R_full_q005_s2 | B1 | full | 0.005 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_R_cutoff_W19_q005_s0 | B1 | cutoff_W19 | 0.005 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_R_cutoff_W19_q005_s1 | B1 | cutoff_W19 | 0.005 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_R_cutoff_W19_q005_s2 | B1 | cutoff_W19 | 0.005 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_C_full_q005_s0 | B1 | full | 0.005 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_C_full_q005_s1 | B1 | full | 0.005 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_C_full_q005_s2 | B1 | full | 0.005 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_C_cutoff_W19_q005_s0 | B1 | cutoff_W19 | 0.005 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_C_cutoff_W19_q005_s1 | B1 | cutoff_W19 | 0.005 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_C_cutoff_W19_q005_s2 | B1 | cutoff_W19 | 0.005 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_q0025_s0 | B2 | full | 0.0025 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_q0025_s1 | B2 | full | 0.0025 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_q0025_s2 | B2 | full | 0.0025 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_q010_s0 | B2 | full | 0.01 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_q010_s1 | B2 | full | 0.01 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_q010_s2 | B2 | full | 0.01 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q0025_s0 | B2 | full | 0.0025 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q0025_s1 | B2 | full | 0.0025 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q0025_s2 | B2 | full | 0.0025 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q010_s0 | B2 | full | 0.01 | 0 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q010_s1 | B2 | full | 0.01 | 1 | W12-W22 | MUST | PLANNED |
| arrival_v2_M_full_q010_s2 | B2 | full | 0.01 | 2 | W12-W22 | MUST | PLANNED |
| arrival_v2_I_full_fixed_hour_s0 | B3 | full | 0.005 | 0 | W12-W22 | OPTIONAL | PLANNED |
| arrival_v2_I_full_fixed_hour_s1 | B3 | full | 0.005 | 1 | W12-W22 | OPTIONAL | PLANNED |
| arrival_v2_I_full_fixed_hour_s2 | B3 | full | 0.005 | 2 | W12-W22 | OPTIONAL | PLANNED |
| arrival_v2_M_full_fixed_hour_s0 | B3 | full | 0.005 | 0 | W12-W22 | OPTIONAL | PLANNED |
| arrival_v2_M_full_fixed_hour_s1 | B3 | full | 0.005 | 1 | W12-W22 | OPTIONAL | PLANNED |
| arrival_v2_M_full_fixed_hour_s2 | B3 | full | 0.005 | 2 | W12-W22 | OPTIONAL | PLANNED |

必跑：24条B1＋12条B2＝36条完整逻辑轨迹，另3个短烟测。独立全跑合计40,500次行动机会；B1复用前缀后为32,100次。可选B3另6条、6,600次。以上仅正文初次生成上限，工具路由、重试与盲标另计。

失败规则：工程故障修复后重跑；合法的阴性、低供给和低发帖结果必须保留。不得因I不优于M而重新选seed、调q或剔除运行。
