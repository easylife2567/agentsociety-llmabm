# Experiment 1

**Group Name:** control_no_intervention

**Group Type:** control

## Description

基线组：全程不干预，观察认知偏移自然涌现过程

## Status

Configured（100-agent 试点配置已生成并通过 check）

## 配置参数

### 规模

- **Agents**: 100 个 `PersonAgent`（试点规模）
- **环境**: 1 个 `SocialMediaSpace`
- **开始时间**: 2026-08-20T20:00:00（张雪峰去世事件时刻）
- **步骤**: `run` 12 ticks × tick=1（1 小时/步，覆盖认知偏移形成链 6 环节 × 2）

### Agent 选择（4 类角色，100 人）

| 角色 | 数量 | id 范围 | 熟悉度 | 人设要点 |
|------|------|---------|--------|---------|
| 雪峰考研学员 | 25 | 1-25 | 高 | 张老师学生，有感情 |
| 教育圈观察员 | 25 | 26-50 | 中 | 关注教育资讯，非粉丝 |
| 刷视频的路人 | 40 | 51-90 | 低 | 听说过头衔，了解不深 |
| 热点吐槽君 | 10 | 91-100 | 低但高产 | 二创玩梗，流量导向 |

### 初始供给（事件注入，4 类帖子）

| post_id | 作者 | 框架 | 作用 |
|---------|------|------|------|
| 1 | 901 教育新闻联播 | 事实讣告 | 权威事实基线 |
| 2 | 902 考研界扛把子 | 悼念 | 哀悼框架 |
| 3 | 903 行业深扒 | 内幕猜测（去语境化） | 未证实信息，认知偏移原料 |
| 4 | 904 快乐小狗 | 玩梗二创 | 娱乐化/嘲讽框架 |

作者账号（901-904）为供给账号，不参与 agent 调度。

### 环境参数

- `feed_source: global`（全平台候选池）
- `polarization_mode: none`（不启用极化混合）
- `random_seed: 42`
- Agent 参数：`max_react_turns=6`，`enable_memory=True`，`enable_todo_list=False`

### 试点检验目标（checklist）

1. 流程跑通：100 节点配置正确、12 ticks 完成
2. 涌现初检：发帖/互动是否发生；事件讨论是否扩散
3. 数据产出：replay（posts/comments/events）可用于 P1 三阶段时序分析

## 生成文件

- `init/init_config.json`：100 agents + SocialMediaSpace
- `init/steps.yaml`：run 12 ticks

## 后续

试点通过后：敏感性分析（5 个关键参数 ±50%）→ 正式反事实实验（H1: 4 组、H2: 2 组、H3: 2 组）
