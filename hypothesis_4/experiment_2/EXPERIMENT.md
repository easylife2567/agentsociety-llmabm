# Experiment 2

**Group Name:** treatment_decuration_chrono

**Group Type:** treatment

## Description

去策展化：时间线排序（chronological），移除热度加权与策展信号。与策展基线（experiment_1，即 hypothesis_3/experiment_1 的 reddit_hot run）对照，检验主假设（H4）——算法策展选择性放大迷因表征并驱动数字表征转移。

## 判读（主假设的备择分支）

| 结果组合 | 判定 |
|---|---|
| 选择性放大成立（基线中迷因曝光/互动份额 > 供给份额、专业份额 < 供给份额；去策展化后回归）且转移涌现（基线复现三阶段轨迹、幅度 > 去策展化） | 支持主假设：算法策展是表征转移的核心机制 |
| (a) 选择性放大成立，但转移未涌现 | 策展是表征分配的"放大器"而非转移的充分驱动 → 检验供给端与互动再生产环节 |
| (b) 选择性放大不成立，但转移仍涌现（去策展化下迷因仍被过度放大） | 用户自选择与再生产内生驱动 → 命题修正为"算法×用户合谋策展" |
| (c) 两者均不成立 | 算法策展非核心机制 → 核心命题退回"数字哀悼+模因竞争"解释 |

生成性验证前提：策展基线 run 须先复现真实三阶段表征转移形态（拟合 data_mining_report 曲线），否则返回调整规则而非下因果结论。

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
