## Data Overview

- **Data path**: /Users/easylife/Project/AgentSociety/runs/2026-10-15-02-timestamp-bdr-ablation/analysis/hypothesis_4/experiment_3/run/replay
- **Tables**: 2
- **Total Rows**: 1111

### Dataset: `curation_dynamics.env_state` (11 rows)
- Table: `curation_dynamics_env_state`
- Title: CurationDynamicsSpace Environment State
- Description: Per-step environment snapshots exported by CurationDynamicsSpace.
Sample data (first rows):
  Row 1:
  - step: 1
  - t: 2026-03-22T22:00:00
  - week: 2026-W12
  - meme_env_stock: 17
  - meme_env_flow: 17
  Row 2:
  - step: 2
  - t: 2026-03-29T22:00:00
  - week: 2026-W13
  - meme_env_stock: 78
  - meme_env_flow: 61
  Row 3:
  - step: 3
  - t: 2026-04-05T22:00:00
  - week: 2026-W14
  - meme_env_stock: 137
  - meme_env_flow: 59

**Numeric Stats**:
  - `step` (`step`): min=1, max=11, avg=None
    meaning: Simulation step for this environment snapshot row.
  - `meme_env_stock` (`meme_env_stock`): min=17, max=209, avg=None
    meaning: 涌现环境存量 Stock_t：过去 emergence_window_stock 周（含本周）供给总数（注入+agent 帖）
  - `meme_env_flow` (`meme_env_flow`): min=17, max=61, avg=None
    meaning: 涌现环境流量（arena 口径）：本 tick 新增供给总数（注入+agent 帖）
  - `meme_env_flow_world` (`meme_env_flow_world`): min=1246, max=11394, avg=None
    meaning: 涌现环境流量（现实口径）：本周真实新增帖量镜像调度值
  - `meme_env_abundance` (`meme_env_abundance`): min=1.0, max=3.8032, avg=None
    meaning: 丰沛度 B_t = f(Stock_t)/f(Stock_base)，f(x)=x/(x+K_a)；基线周=1
  - `meme_env_emptiness` (`meme_env_emptiness`): min=0.1972, max=1.0, avg=None
    meaning: 空旷度 S_t = h(Flow_t)/h(Flow_base)，h(x)=K_f/(K_f+x)；基线周=1；sustained_hot 臂事件周后冻结
  - `meme_env_gain` (`meme_env_gain`): min=0.5292, max=3.0, avg=None
    meaning: 涌现增益 G_t = clamp(B_t^β·S_t^σ, gain_min, gain_max)；**观测序列**（2026-09-12 起不进入任何类型的决策）
  - `total_supply` (`total_supply`): min=17, max=64, avg=None
    meaning: 本 tick 新增供给总数（agent 产出+注入）
  - `agent_supply` (`agent_supply`): min=0, max=29, avg=None
    meaning: 本 tick Agent 产出帖数
  - `injected_count` (`injected_count`): min=17, max=35, avg=None
    meaning: 本 tick 注入帖数
  - `supply_share_meme` (`supply_share_meme`): min=0.0, max=1.0, avg=None
    meaning: Agent 产出口径供给份额（分母=五类 agent 帖）
  - `supply_share_mourning` (`supply_share_mourning`): min=0.0, max=0.7241379310344828, avg=None
    meaning: Agent 产出口径供给份额
  - `supply_share_education` (`supply_share_education`): min=0.0, max=0.5, avg=None
    meaning: Agent 产出口径供给份额
  - `supply_share_marketing` (`supply_share_marketing`): min=0.0, max=0.7307692307692307, avg=None
    meaning: Agent 产出口径供给份额
  - `supply_share_other` (`supply_share_other`): min=0.0, max=0.6666666666666666, avg=None
    meaning: Agent 产出口径供给份额
  - `supply_share_all_meme` (`supply_share_all_meme`): min=0.0, max=0.7222222222222222, avg=None
    meaning: combined 口径供给份额（注入+产出，分母含 noise，对齐 benchmark total）
  - `supply_share_all_mourning` (`supply_share_all_mourning`): min=0.0, max=0.5625, avg=None
    meaning: combined 口径供给份额
  - `supply_share_all_education` (`supply_share_all_education`): min=0.05555555555555555, max=0.25925925925925924, avg=None
    meaning: combined 口径供给份额
  - `supply_share_all_marketing` (`supply_share_all_marketing`): min=0.09375, max=0.7441860465116279, avg=None
    meaning: combined 口径供给份额
  - `supply_share_all_other` (`supply_share_all_other`): min=0.0, max=0.2647058823529412, avg=None
    meaning: combined 口径供给份额
  - `supply_share_all_noise` (`supply_share_all_noise`): min=0.027777777777777776, max=0.13043478260869565, avg=None
    meaning: combined 口径供给份额
  - `agent_supply_meme` (`agent_supply_meme`): min=0, max=14, avg=None
    meaning: 本 tick Agent 产出（按类型）
  - `agent_supply_mourning` (`agent_supply_mourning`): min=0, max=21, avg=None
    meaning: 本 tick Agent 产出（按类型）
  - `agent_supply_education` (`agent_supply_education`): min=0, max=7, avg=None
    meaning: 本 tick Agent 产出（按类型）
  - `agent_supply_marketing` (`agent_supply_marketing`): min=0, max=19, avg=None
    meaning: 本 tick Agent 产出（按类型）
  - `agent_supply_other` (`agent_supply_other`): min=0, max=2, avg=None
    meaning: 本 tick Agent 产出（按类型）
  - `injected_meme` (`injected_meme`): min=0, max=16, avg=None
    meaning: 本 tick 注入（按类型）
  - `injected_mourning` (`injected_mourning`): min=0, max=15, avg=None
    meaning: 本 tick 注入（按类型）
  - `injected_education` (`injected_education`): min=2, max=6, avg=None
    meaning: 本 tick 注入（按类型）
  - `injected_marketing` (`injected_marketing`): min=4, max=13, avg=None
    meaning: 本 tick 注入（按类型）
  - `injected_other` (`injected_other`): min=0, max=8, avg=None
    meaning: 本 tick 注入（按类型）
  - `injected_noise` (`injected_noise`): min=1, max=3, avg=None
    meaning: 本 tick 注入（按类型）
  - `total_exposures` (`total_exposures`): min=1000, max=1000, avg=None
    meaning: 本 tick 全部 Agent 的 feed 槽位总数（1 槽=1 次曝光）
  - `exposure_share_meme` (`exposure_share_meme`): min=0.0, max=0.585, avg=None
    meaning: 推荐服务口径曝光份额
  - `exposure_share_mourning` (`exposure_share_mourning`): min=0.0, max=0.38, avg=None
    meaning: 推荐服务口径曝光份额
  - `exposure_share_education` (`exposure_share_education`): min=0.069, max=0.25, avg=None
    meaning: 推荐服务口径曝光份额
  - `exposure_share_marketing` (`exposure_share_marketing`): min=0.165, max=0.815, avg=None
    meaning: 推荐服务口径曝光份额
  - `exposure_share_other` (`exposure_share_other`): min=0.0, max=0.246, avg=None
    meaning: 推荐服务口径曝光份额
  - `exposure_share_noise` (`exposure_share_noise`): min=0.03, max=0.116, avg=None
    meaning: 推荐服务口径曝光份额
  - `exposure_meme` (`exposure_meme`): min=0, max=585, avg=None
    meaning: 本 tick 曝光槽位（按类型）
  - `exposure_mourning` (`exposure_mourning`): min=0, max=380, avg=None
    meaning: 本 tick 曝光槽位（按类型）
  - `exposure_education` (`exposure_education`): min=69, max=250, avg=None
    meaning: 本 tick 曝光槽位（按类型）
  - `exposure_marketing` (`exposure_marketing`): min=165, max=815, avg=None
    meaning: 本 tick 曝光槽位（按类型）
  - `exposure_other` (`exposure_other`): min=0, max=246, avg=None
    meaning: 本 tick 曝光槽位（按类型）
  - `exposure_noise` (`exposure_noise`): min=30, max=116, avg=None
    meaning: 本 tick 曝光槽位（按类型）
  - `official_posts_count` (`official_posts_count`): min=0, max=0, avg=None
    meaning: 本 tick 置顶集合中的官方帖数
  - `official_exposure_slots` (`official_exposure_slots`): min=0, max=11, avg=None
    meaning: 本 tick 官方帖占据的 feed 槽位数
  - `feed_live_pool` (`feed_live_pool`): min=34, max=137, avg=None
    meaning: 算法实际候选池帖数：random=截至当周全部历史帖；chronological=截至行动时刻全部已发布帖；interest=未退场活帖
  - `feed_sample_temp` (`feed_sample_temp`): min=4.0, max=4.0, avg=None
    meaning: interest 臂比例抽样的温度（<=0 表示确定性 top-k 消融档）
  - `feed_half_life_weeks` (`feed_half_life_weeks`): min=1.5, max=1.5, avg=None
    meaning: 帖子时间生命的半衰期（周）
  - `feed_saturation_scale` (`feed_saturation_scale`): min=20.0, max=20.0, avg=None
    meaning: 曝光饱和尺度：累计曝光达该值时生命折半
  - `exposure_slots_age0` (`exposure_slots_age0`): min=113, max=378, avg=None
    meaning: 本 tick 曝光槽位中帖龄 0 周（本周新帖）的槽位数
  - `exposure_slots_age1` (`exposure_slots_age1`): min=309, max=756, avg=None
    meaning: 本 tick 曝光槽位中帖龄 1 周的槽位数
  - `exposure_slots_age2` (`exposure_slots_age2`): min=0, max=568, avg=None
    meaning: 本 tick 曝光槽位中帖龄 2 周的槽位数
  - `exposure_slots_age3plus` (`exposure_slots_age3plus`): min=0, max=0, avg=None
    meaning: 本 tick 曝光槽位中帖龄 ≥3 周的槽位数（老帖霸屏的直接指标）
  - `event_floor_slots` (`event_floor_slots`): min=0, max=5, avg=None
    meaning: 议程设置：本 tick 事件周保底哀悼帖集合的条数（全员各占同样多槽位；非事件周=0）
**Categorical Stats**:
  - `week` (`week`): 11 unique, top: '2026-W12'(None), '2026-W13'(None), '2026-W14'(None)
    meaning: 当前 tick 的 ISO 周标签

### Dataset: `curation_dynamics.agent_state` (1100 rows)
- Table: `curation_dynamics_agent_state`
- Title: CurationDynamicsSpace Agent State
- Description: Per-agent replay snapshots exported by CurationDynamicsSpace.
Sample data (first rows):
  Row 1:
  - agent_id: 1
  - step: 1
  - t: 2026-03-22T22:00:00
  - agent_type: marketing
  - spoke: 1
  Row 2:
  - agent_id: 2
  - step: 1
  - t: 2026-03-22T22:00:00
  - agent_type: marketing
  - spoke: 0
  Row 3:
  - agent_id: 3
  - step: 1
  - t: 2026-03-22T22:00:00
  - agent_type: other
  - spoke: 0

**Numeric Stats**:
  - `agent_id` (`agent_id`): min=1, max=100, avg=None
    meaning: Agent identifier for this snapshot row.
  - `step` (`step`): min=1, max=11, avg=None
    meaning: Simulation step for this snapshot row.
  - `spoke` (`spoke`): min=0, max=1, avg=None
    meaning: 本 tick 是否发言
  - `type_mismatch` (`type_mismatch`): min=0, max=1, avg=None
    meaning: 判类结果与产出类型是否不一致
  - `exposure_meme` (`exposure_meme`): min=0, max=10, avg=None
    meaning: 本 tick 该 Agent feed 中类型槽位数
  - `exposure_mourning` (`exposure_mourning`): min=0, max=8, avg=None
    meaning: 本 tick 该 Agent feed 中类型槽位数
  - `exposure_education` (`exposure_education`): min=0, max=6, avg=None
    meaning: 本 tick 该 Agent feed 中类型槽位数
  - `exposure_marketing` (`exposure_marketing`): min=0, max=10, avg=None
    meaning: 本 tick 该 Agent feed 中类型槽位数
  - `exposure_other` (`exposure_other`): min=0, max=5, avg=None
    meaning: 本 tick 该 Agent feed 中类型槽位数
  - `exposure_noise` (`exposure_noise`): min=0, max=5, avg=None
    meaning: 本 tick 该 Agent feed 中类型槽位数
  - `climate_meme` (`climate_meme`): min=0.0, max=1.0, avg=None
    meaning: 该 Agent 所见意见气候（feed 类型分布）
  - `climate_mourning` (`climate_mourning`): min=0.0, max=0.8, avg=None
    meaning: 该 Agent 所见意见气候
  - `climate_education` (`climate_education`): min=0.0, max=0.6, avg=None
    meaning: 该 Agent 所见意见气候
  - `climate_marketing` (`climate_marketing`): min=0.0, max=1.0, avg=None
    meaning: 该 Agent 所见意见气候
  - `climate_other` (`climate_other`): min=0.0, max=0.5, avg=None
    meaning: 该 Agent 所见意见气候
  - `climate_noise` (`climate_noise`): min=0.0, max=0.5, avg=None
    meaning: 该 Agent 所见意见气候
  - `meme_env_abundance_seen` (`meme_env_abundance_seen`): min=1.0, max=1.0, avg=None
    meaning: 本 tick 该 Agent 所见丰沛度 B_t
  - `meme_env_emptiness_seen` (`meme_env_emptiness_seen`): min=1.0, max=1.0, avg=None
    meaning: 本 tick 该 Agent 所见空旷度 S_t
  - `meme_env_gain_seen` (`meme_env_gain_seen`): min=1.0, max=1.0, avg=None
    meaning: 本 tick 该 Agent 所见涌现增益 G_t
  - `feed_slots` (`feed_slots`): min=10, max=10, avg=None
    meaning: 本 tick 该 Agent feed 槽位数
**Categorical Stats**:
  - `agent_type` (`agent_type`): 5 unique, top: 'education'(None), 'marketing'(None), 'meme'(None)
    meaning: Agent 固定类型（全程不变）
  - `produced_type` (`produced_type`): 5 unique, top: 'education'(None), 'marketing'(None), 'meme'(None)
    meaning: 发言时的产出类型（=agent_type；沉默为 NULL）
  - `assigned_type` (`assigned_type`): 3 unique, top: 'marketing'(None), 'meme'(None), 'mourning'(None)
    meaning: 发言内容的四词表判类结果
