# 多 Run 总览（CurationDynamics 3 臂 × 3 seed = 9 runs）

- 生成时间：2026-09-28T02:27:34

| run | 状态 | 进程 | 周进度 | 当前周 | 涌现G | Agent帖累计 | 供给前二(combined) | 帖池 |
|---|---|---|---|---|---|---|---|---|
| weekly_lag1_interest_s0 | completed |  | 11/11 | 2026-W22 | 0.989 | 212 | 玩梗69.6%、营销15.2% | 455 |
| weekly_lag1_interest_s1 | completed |  | 11/11 | 2026-W22 | 0.982 | 196 | 玩梗69.8%、营销16.3% | 439 |
| weekly_lag1_interest_s2 | completed |  | 11/11 | 2026-W22 | 0.986 | 204 | 玩梗71.1%、营销15.6% | 447 |
| weekly_lag1_random_s0 | completed |  | 11/11 | 2026-W22 | 0.977 | 167 | 玩梗48.4%、营销22.6% | 410 |
| weekly_lag1_random_s1 | completed |  | 11/11 | 2026-W22 | 0.973 | 158 | 玩梗50.0%、营销23.3% | 401 |
| weekly_lag1_random_s2 | completed |  | 11/11 | 2026-W22 | 0.981 | 173 | 玩梗46.4%、营销25.0% | 416 |

**字段说明**：
- `status`：run 当前状态（pid.json 心跳）：running=运行中 / completed=完成 / failed=失败。
- `pid`：引擎进程号（pid.json）。
- `alive`：进程当前是否存活（kill(pid,0) 探测；completed/failed 后自然为否）。
- `step_count`：引擎已完成批次数（random/interest=11周级step；chronological=693个非空小时批次）。
- `week`：ISO 周标签（2026-W12…W22）。模拟 1 tick = 1 真实周，共 11 周。
- `涌现G`：[仅观测·不参与决策] 涌现增益 G_t = clamp(B^β·S^σ, 0.2, 3.0)，β=σ=1 起步。2026-09-12 用户裁定：G 与 agent 侧 θ 一并退役（原经玩梗型效用影响决策），本序列仅作描述性时间轴与审计。
- `Agent帖累计`：该 run 各周 Agent 产出帖数之和（≈内容 LLM 调用总量）。
- `供给前二(combined)`：最近完结周 combined 口径（注入+产出，分母含噪音）份额最高的两个类型。
- `exposure_count`：该帖累计被推荐进 feed 的次数（生命周期曝光量）。
- `周进度`：已完结的周数 / 总周数（11 周 = W12…W22）。
- `帖池`：ENV_STATE.json 帖池中的帖子总数（含注入与 agent 产出）。
