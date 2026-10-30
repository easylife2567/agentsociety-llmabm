# 三臂各10seed机制配置

本级30份JSON显式采用next_batch，三臂新生成帖统一批末入池、后续行动批次可推荐，同批互不可见。相同seed共享人口、行为、输入和行动表，各臂评分/候选池/生命周期规则仍不同。

文件名hourly_return_v1_{random,chronological,interest}_s0–9.json。配置哈希与准备/实际运行的区别见[上级README](../README.md)。本级存在不代表新增运行授权，不直接据此接续旧checkpoint。
