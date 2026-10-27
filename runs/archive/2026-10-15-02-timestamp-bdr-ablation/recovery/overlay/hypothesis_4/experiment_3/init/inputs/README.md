# 配对冻结输入

| 文件系列（各有s0、s1、s2） | 来源及用途 |
|---|---|
| injection_sample_s*.json | 主实验同名250条窗口真实帖，保持发布时间和原文 |
| initial_sample_weekly_lag_s*.json | 主实验同名17条历史池，保留历史命名，不更改当前timestamp语义 |
| population_s*.json | 主实验同名100人人口快照，用于来源核对；实际变体profile在configs内 |
| action_schedule_s*.json | 主实验同名行动表及五人W13共同顺延映射 |

十二份文件逐字节复制，哈希由[source_lock](../source_lock.json)冻结。没有重新抽样、重新标定或使用其他run候选数据。
