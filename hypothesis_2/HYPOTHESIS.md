# Hypothesis

## Description

算法推荐贡献度假设：平台算法热度推荐（reddit_hot 加权）显著加剧公众人物死亡事件中的认知偏移——移除算法推荐改用时间线排序（chronological）后，圈外群体最终认知偏移程度显著下降。因变量：圈外群体最终认知偏移程度；自变量：推荐算法模式（热度加权 vs 时间线排序）。

## Rationale

认知偏移形成链的算法曝光期机制表明：平台按内容热度加权推送，高互动量的梗/二创内容获得更高曝光权重，单一符号化内容持续挤压完整信息空间。反事实设计（移除算法推荐）可量化算法在认知偏移中的因果贡献，对应文献索引中算法推荐/信息茧房/个性化推送主题。

## Experiment Groups

### Group 1: control_hotness

**Type:** control

**Description:** 基线组：启用热度加权推荐（reddit_hot），模拟真实平台推送逻辑


### Group 2: treatment_timeline

**Type:** treatment

**Description:** 反事实组：移除算法推荐，改用时间线排序（chronological），内容按时间先后展示

