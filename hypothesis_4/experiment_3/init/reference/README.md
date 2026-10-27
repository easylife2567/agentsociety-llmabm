# 完整模型来源

| 资产 | 用途 |
|---|---|
| timestamp_v1_interest_s0.json、timestamp_v1_interest_s1.json、timestamp_v1_interest_s2.json | 主批原Full配置的字节副本；保留其历史路径，仅作来源，不作为新启动授权 |
| main_runtime_plan.json | 主批实际模型、授权边界、源码/配置哈希和运行顺序；其授权不覆盖新消融 |

Full原始结果保留在experiment_2/runs/timestamp_v1；本实验离线配对读取该正式位置。历史哈希在../../provenance/exploration_baseline.json；采用不重新运行主批。

新增timestamp_v1_interest_s3至s9.json为主实验Full配置的原字节副本；实际配对结果见../manifest_seed3_9.json，seed6必须读取完成的resume1目录。Full不重跑，输入沿用原冻结路径，模型按用户确认等价处理并保留实际版本溯源。
