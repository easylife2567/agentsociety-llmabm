# 消融变体

| seed | 去B：baseline_utility=0 | 去D：spiral_scale=0 | 去R：decay=0 |
|---|---|---|---|
| 0 | [no_b_s0](timestamp_bdr_v1_interest_no_b_s0.json) | [no_d_s0](timestamp_bdr_v1_interest_no_d_s0.json) | [no_r_s0](timestamp_bdr_v1_interest_no_r_s0.json) |
| 1 | [no_b_s1](timestamp_bdr_v1_interest_no_b_s1.json) | [no_d_s1](timestamp_bdr_v1_interest_no_d_s1.json) | [no_r_s1](timestamp_bdr_v1_interest_no_r_s1.json) |
| 2 | [no_b_s2](timestamp_bdr_v1_interest_no_b_s2.json) | [no_d_s2](timestamp_bdr_v1_interest_no_d_s2.json) | [no_r_s2](timestamp_bdr_v1_interest_no_r_s2.json) |

每份100人、W12—W22、每人每周一次机会；均为timestamp兴趣制度，九次LLM均已完成并获接受；当前配置不授权重跑。完整输出哈希与配对关系见[manifest](../manifest.json)。

## 新增seed3–9（仅准备，未启动）

| seed | 去B | 去D | 去R |
|---|---|---|---|
| 3 | [no_b_s3](timestamp_bdr_v1_interest_no_b_s3.json) | [no_d_s3](timestamp_bdr_v1_interest_no_d_s3.json) | [no_r_s3](timestamp_bdr_v1_interest_no_r_s3.json) |
| 4 | [no_b_s4](timestamp_bdr_v1_interest_no_b_s4.json) | [no_d_s4](timestamp_bdr_v1_interest_no_d_s4.json) | [no_r_s4](timestamp_bdr_v1_interest_no_r_s4.json) |
| 5 | [no_b_s5](timestamp_bdr_v1_interest_no_b_s5.json) | [no_d_s5](timestamp_bdr_v1_interest_no_d_s5.json) | [no_r_s5](timestamp_bdr_v1_interest_no_r_s5.json) |
| 6 | [no_b_s6](timestamp_bdr_v1_interest_no_b_s6.json) | [no_d_s6](timestamp_bdr_v1_interest_no_d_s6.json) | [no_r_s6](timestamp_bdr_v1_interest_no_r_s6.json) |
| 7 | [no_b_s7](timestamp_bdr_v1_interest_no_b_s7.json) | [no_d_s7](timestamp_bdr_v1_interest_no_d_s7.json) | [no_r_s7](timestamp_bdr_v1_interest_no_r_s7.json) |
| 8 | [no_b_s8](timestamp_bdr_v1_interest_no_b_s8.json) | [no_d_s8](timestamp_bdr_v1_interest_no_d_s8.json) | [no_r_s8](timestamp_bdr_v1_interest_no_r_s8.json) |
| 9 | [no_b_s9](timestamp_bdr_v1_interest_no_b_s9.json) | [no_d_s9](timestamp_bdr_v1_interest_no_d_s9.json) | [no_r_s9](timestamp_bdr_v1_interest_no_r_s9.json) |

21份新配置与同seed Full仅差指定参数和独立账本路径，execution_authorized=false，清单见../manifest_seed3_9.json。旧九配置保持原字节。
