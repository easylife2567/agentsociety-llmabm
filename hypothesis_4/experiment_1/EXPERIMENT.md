# Experiment 1

**Group Name:** control_curation_hot

**Group Type:** control

## Description

策展基线：热度加权推荐（reddit_hot），完整算法策展环境。用于与 experiment_2（去策展化，chronological）比较，检验算法策展对数字表征转移的因果作用。

## Shared Run（重要）

本组**不单独运行**：与 [hypothesis_3/experiment_1](../../hypothesis_3/experiment_1/EXPERIMENT.md) 共用同一 run（同供给池 140 条真实文本、同 100 agent 种子与 persona、同 12 ticks、同问卷），唯一设定即 reddit_hot。运行与输出均以 hypothesis_3/experiment_1 为准；本目录不放置 init 配置，避免重复运行与配置漂移。

## Agent Selection Criteria

all 100 agents; recommendation_algorithm=reddit_hot（以 hypothesis_3/experiment_1 的 init_config.json 为准）

## Status

Shared with hypothesis_3/experiment_1（配置已生成并 check 通过，2026-08-31；尚未运行）
