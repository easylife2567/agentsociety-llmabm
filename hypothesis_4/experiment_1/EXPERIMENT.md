# Experiment 1

**Group Name:** control_curation_hot

**Group Type:** control

## Description

策展基线：热度加权推荐（reddit_hot），完整算法策展环境。主假设（H4）的机制层与结果层 DV 均以本 run 为"有策展"侧：表征类别的曝光/互动份额偏移、舆论场表征转移轨迹，与 experiment_2（去策展化）对照。

本 run 同时兼任**生成性验证**：须先复现真实"专业→悼念→迷因"三阶段周级形态（效标 = [benchmark_curves.json](../benchmark_curves.json)），未涌现则返回调整规则而非下因果结论。

> 2026-09-07 v0.3：原"与 hypothesis_3 共享 run"安排作废（H3 已删除），本实验持有独立 init 配置。

## Agent Selection Criteria

all 6 类群代表 agents（借势营销/事件悼念/其他讨论/教育观点/梗文化/水军低质号）; recommendation_algorithm=reddit_hot

## Status

needs_reconfig（v0.3 重设计：6 类群 agent + 周级 12 ticks + 自定义 env 扩展 + 周级供给池；init 配置待重新生成，2026-09-07）
