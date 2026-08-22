# Hypothesis

## Description

治理干预时机假设：在公众人物死亡事件认知偏移形成链中，平台治理介入越早（内容生产期/算法曝光期），对最终认知偏移程度的缓解效果越优于晚期介入（认知形成期）；同时检验干预效果是否存在非单调最优窗口（最优时点可能不在最早环节而在算法曝光期）。因变量：圈外群体最终认知偏移程度（认知与事实的符号化偏离度）；自变量：治理干预介入时点（3 个代表时点 vs 无干预基线）。

## Rationale

认知偏移形成链六环节（事件触发→内容生产→算法曝光→认知形成→认知偏移→记忆固化）中，信息异化从内容生产期开始、经算法曝光期放大、在认知形成期进入用户认知。传播学与平台治理文献表明，干预窗口越靠前，越能在异化内容被算法放大和用户吸收之前阻断；但过度早期（事件触发期）内容尚未爆发，干预可能无效，故同时检验最优窗口的非单调性（对应文献索引中平台治理/内容治理与信息异化主题）。

## Experiment Groups

### Group 1: control_no_intervention

**Type:** control

**Description:** 基线组：全程不干预，观察认知偏移自然涌现过程


### Group 2: treatment_early_production

**Type:** treatment

**Description:** 早期干预：内容生产期（阶段2）结束时对梗/二创内容启动限流降权


### Group 3: treatment_mid_exposure

**Type:** treatment

**Description:** 中期干预：算法曝光期（阶段3）结束时对梗/二创内容启动限流降权


### Group 4: treatment_late_formation

**Type:** treatment

**Description:** 晚期干预：认知形成期（阶段4）结束时对梗/二创内容启动限流降权

