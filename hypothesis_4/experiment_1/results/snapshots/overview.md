# 多 Run 总览（CurationDynamics 3 臂 × 3 seed = 9 runs）

- 生成时间：2026-09-13T04:41:38

| run | 状态 | 进程 | 周进度 | 当前周 | 涌现G | Agent帖累计 | 供给前二(combined) | 帖池 |
|---|---|---|---|---|---|---|---|---|
| chronological_s0 | completed |  | 11/11 | 2026-W22 | 1.303 | 300 | 玩梗71.7%、营销15.2% | 550 |
| chronological_s1 | completed |  | 11/11 | 2026-W22 | 1.317 | 343 | 玩梗69.6%、营销17.4% | 593 |
| chronological_s2 | completed |  | 11/11 | 2026-W22 | 1.300 | 297 | 玩梗55.6%、营销33.3% | 547 |
| interest_s0 | completed |  | 11/11 | 2026-W22 | 1.312 | 359 | 玩梗60.4%、营销28.3% | 609 |
| interest_s1 | completed |  | 11/11 | 2026-W22 | 1.316 | 361 | 玩梗60.4%、营销28.3% | 611 |
| interest_s2 | completed |  | 11/11 | 2026-W22 | 1.310 | 345 | 玩梗60.0%、营销29.1% | 595 |
| random_s0 | completed |  | 11/11 | 2026-W22 | 1.301 | 335 | 玩梗63.3%、营销24.5% | 585 |
| random_s1 | completed |  | 11/11 | 2026-W22 | 1.314 | 359 | 玩梗58.9%、营销23.2% | 609 |
| random_s2 | completed |  | 11/11 | 2026-W22 | 1.300 | 315 | 玩梗58.3%、营销27.1% | 565 |

**字段说明**：
- `status`：run 当前状态（pid.json 心跳）：running=运行中 / completed=完成 / failed=失败。
- `pid`：引擎进程号（pid.json）。
- `alive`：进程当前是否存活（kill(pid,0) 探测；completed/failed 后自然为否）。
- `step_count`：引擎已完成 step 数（SOCIETY_STEP.json；本实验 11 步=11 周）。
- `week`：ISO 周标签（2026-W12…W22）。模拟 1 tick = 1 真实周，共 11 周。
- `涌现G`：[仅观测·不参与决策] 涌现增益 G_t = clamp(B^β·S^σ, 0.2, 3.0)，β=σ=1 起步。2026-09-12 用户裁定：G 与 agent 侧 θ 一并退役（原经玩梗型效用影响决策），本序列仅作描述性时间轴与审计。
- `Agent帖累计`：该 run 各周 Agent 产出帖数之和（≈内容 LLM 调用总量）。
- `供给前二(combined)`：最近完结周 combined 口径（注入+产出，分母含噪音）份额最高的两个类型。
- `exposure_count`：该帖累计被推荐进 feed 的次数（生命周期曝光量）。
- `周进度`：已完结的周数 / 总周数（11 周 = W12…W22）。
- `帖池`：ENV_STATE.json 帖池中的帖子总数（含注入与 agent 产出）。
