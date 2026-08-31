# Experiment 1

**Group Name:** insider_vs_outsider（单 run 双组）

**Group Type:** control（高熟/圈内）+ treatment（低熟/圈外），共存于同一 run

## Description

假设 3 群体差异检验：圈外群体（初始不熟悉逝者）与圈内群体（初始熟悉逝者）在同一环境、同一供给池、同一推荐器下的认知偏移程度比较。两组必须共存于同一 run（同供给同用户池），组间唯一系统差异是初始熟悉度。

设计详见 [DATA_DRIVEN_DESIGN.md](DATA_DRIVEN_DESIGN.md)（v0.2）：agent 为 5 特征族 × 个体特征权重交叉（平台无关），熟悉度与特征族正交（族内分层等比分配）。

## Agent Selection Criteria

- 圈内组（对照）：`agent_profiles.json` 中 `familiarity == "high"`（50 名）
- 圈外组（干预）：`agent_profiles.json` 中 `familiarity == "low"`（50 名）

## Configuration Parameters

| 项 | 值 |
|---|---|
| 规模 | 100 PersonAgent（lean 档位）+ SocialMediaSpace |
| 特征族配额 | 玩梗 23 / 悼念 29 / 教育 27 / 反思 8 / 吃瓜 13（数据占比 23.1/28.8/26.8/7.7/13.6%） |
| 风味 | 15 个（最大余数法配额），个体特征权重向量交叉（100% agent 含 1–2 个次级族） |
| 熟悉度分组 | 低 50 / 高 50，与特征族正交 |
| 供给池 | 140 条真实文本（10 主题簇，dup 加权采样，seed=42） |
| 推荐算法 | reddit_hot（现象拟合：高互动梗内容获更高曝光） |
| 时间窗 | 2026-03-24T08:00 起，12 ticks（=12 仿真日），tick=1 日 |
| 测量 | T0 基线 → 4 ticks → T1 → 4 ticks → T2 → 4 ticks → T3，各 4 题（印象词/熟悉度/来源/职业印象） |

## Operationalization

- 因变量（认知偏移程度）：印象词编码后集中度（HHI/Top-1 份额）相对 T0 的变化 + 职业印象事实层偏差
- 分组变量：初始熟悉度（低熟=圈外 / 高熟=圈内），T0 自评熟悉度作分组效度检验
- 判定：圈外偏移 > 圈内 → 支持原假设；圈内 ≥ 圈外 → 备择情形成立（既有完整认知同样被重构）

## Status

Configured（config check 通过，2026-08-31；尚未运行）
