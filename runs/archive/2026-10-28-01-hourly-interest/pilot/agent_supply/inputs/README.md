# 三臂对比冻结输入

本级只为离线三臂比较保存必要来源，不启动或恢复仿真。来源路径与SHA256逐项见上一级`three_arm_contract.json`。

| 资产 | 用途 |
|---|---|
| [chronological_s0/](chronological_s0/README.md) | 历史完整时序seed0的100份Agent、环境、完成记录和环境replay快照 |
| reality_week_boundary.csv | 全量现实W12–W22×5类计数与UTC/上海周份额；主分析取上海周 |
| reality_measurement_audit.json | CSV对应的现实计数来源审计，包含全量上海周分类计数 |
| historical_chronological_config.json | 正式历史时序的配置副本 |
| pilot_chronological_config.json | 本次pilot时序配置副本，用于核对科学条件一致 |
| historical_dtw_source.txt | 既有DTW脚本原字节，保全来源；不执行旧main |
| dtw_method.py | 从上述脚本原样提取的DTW函数，独立导入，无旧main或预设结论 |

现实原始xlsx不在此重复复制，来源路径和SHA256在合约中；55行周表已逐数与冻结审计核对。随机/兴趣原始记录直接引用同一pilot已保存的results快照，不依赖活跃workspace。
