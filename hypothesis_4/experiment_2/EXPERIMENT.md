# Experiment 2

**Group Name:** treatment_decuration_chrono

**Group Type:** treatment

## Description

去策展化：时间线排序（chronological），移除热度加权与策展信号。与策展基线（experiment_1，即 hypothesis_3/experiment_1 的 reddit_hot run）比较，检验算法策展是否为数字表征转移的核心机制。

判读：去策展化 run 的表征转移幅度（宏观：曝光/互动向迷因内容集中度）与认知偏移（微观：印象词集中度变化）显著低于基线 → 支持"策展主体"命题；不显著低于 → 备择情形成立（供给端与自选择自行驱动，算法定位修正为"放大器"）。

## Configuration Parameters

| 项 | 值 |
|---|---|
| 模块 | 100 PersonAgent + SocialMediaSpace（与基线完全一致） |
| 供给池 | 同一 `supply_pool.json`（140 条真实文本，seed=42） |
| agent/persona/问卷 | 与基线逐项一致（已核验：除 recommendation_algorithm 外配置全同） |
| **推荐算法** | **chronological**（唯一实验操纵） |
| 时间窗 | 2026-03-24T08:00 起，12 ticks |

## Agent Selection Criteria

all 100 agents; recommendation_algorithm=chronological

## Status

Configured（config check 通过，2026-08-31；尚未运行）
