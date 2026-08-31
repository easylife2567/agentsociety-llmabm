# Hypothesis

## Description

去策展化因果假设：算法策展（热度加权推荐）是公众人物死亡事件中数字表征转移的核心机制——移除热度加权策展（改为时间线排序）后，舆论场向迷因化表征的转移显著减弱：宏观上曝光与互动向迷因内容的集中度显著低于策展基线，微观上 agent 层认知偏移程度显著低于策展基线；备择情形：若去策展化不减弱表征转移，则表明表征转移可由供给端逻辑与用户自选择自行驱动，算法应重新定位为'放大器'而非'策展主体'，核心命题需修正。因变量：舆论场表征构成转移幅度（宏观，主）；各群体认知偏移程度（微观，次）。分组变量：推荐机制（热度加权 reddit_hot vs 时间线 chronological）。

## Rationale

理论框架第三层（算法策展/算法放大）将推荐系统定位为信息环境组织者与核心机制变量：高互动内容获得更高曝光，形成'注意力→再生产→更高注意力'的策展回路，理论上加速复杂对象向少数高情绪符号的社会表征收敛（Moscovici）与高复制、高情绪模因的传播竞争优势（模因理论）。移除该回路（时间线排序=无热度放大）应削弱迷因表征对专业表征的挤压；若不削弱，则表征转移的主要驱动力在供给端与受众自选择，核心命题需修正。数据实证基础：真实曲线显示梗内容占比在 W19-W22 从 9% 升至 63% 的表征转移（data_mining_report）。对应文献索引中算法策展/平台研究主题。

## Experiment Groups

### Group 1: control_curation_hot

**Type:** control

**Description:** 策展基线：热度加权推荐（reddit_hot），完整算法策展环境；与 hypothesis_3 experiment_1 共用同一 run（同供给池、同 agent 种子、同 12 ticks），不单独重复运行

**Agent Selection Criteria:** all 100 agents; recommendation_algorithm=reddit_hot


### Group 2: treatment_decuration_chrono

**Type:** treatment

**Description:** 去策展化：时间线排序（chronological），移除热度加权与策展信号；同供给同用户池同种子（与基线唯一差异是 recommendation_algorithm）

**Agent Selection Criteria:** all 100 agents; recommendation_algorithm=chronological

