# 完整模型来源

| 资产 | 用途 |
|---|---|
| timestamp_v1_interest_s0.json、timestamp_v1_interest_s1.json、timestamp_v1_interest_s2.json | 主批原Full配置的字节副本；保留其历史路径，仅作来源，不直接在隔离区启动 |
| main_runtime_plan.json | 主批实际模型、授权边界、源码/配置哈希和运行顺序；其授权不覆盖新消融 |

Full原始结果不复制进本恢复包。方案期冻结的三个结果状态哈希及主批完成核对保留在run的baseline.json；本轮不生成消融效应或重算主实验结果。
