# Hypothesis

## Description

算法策展主假设：算法策展（热度加权推荐）作为非人类策展主体，选择性地塑造逝者的数字表征——同一供给池条件下，热度加权使迷因表征（死亡方式梗符号）的曝光与互动份额显著超过其供给份额（过度放大），专业表征（考研辅导等专业内容）的份额显著低于其供给份额（相对抑制），并由此驱动舆论场对逝者的数字表征沿'专业→悼念→迷因'轨迹转移，且转移幅度显著大于去策展化环境（时间线排序）。备择情形分支：(a) 选择性放大成立但表征转移未涌现 → 策展是表征分配的'放大器'而非转移的充分驱动，需检验供给端与互动再生产环节；(b) 选择性放大不成立但转移仍涌现 → 表征转移由用户自选择与再生产内生驱动，命题修正为'算法×用户合谋策展'；(c) 两者均不成立 → 算法策展非核心机制，核心命题退回'数字哀悼+模因竞争'解释。生成性验证前提：策展基线 run 须先复现真实三阶段表征转移形态（拟合真实曲线），否则返回调整规则而非下因果结论。因变量：各表征类别的曝光/互动份额相对供给份额的偏移（机制层，主）；舆论场表征类别份额轨迹与转移幅度（结果层）。分组变量：推荐机制（热度加权 reddit_hot vs 时间线 chronological）。

## Rationale

理论框架第三层（算法策展/算法放大）将推荐系统定位为信息环境组织者与核心机制变量：高互动内容获得更高曝光，形成'注意力→再生产→更高注意力'的策展回路；社会表征理论（Moscovici）与模因理论预测高情绪、高可复制符号在传播竞争中占优，而热度加权将这种占优制度化。数据实证：真实曲线显示'教育→悼念→玩梗'三阶段转移（W13 悼念 44% 峰值，W19-W22 玩梗 9%→63%，data_mining_report）。单一主假设结构由用户裁定（2026-08-31）：核心命题一步到位，备择分支按断点定位给出修正方向。对应文献索引中算法策展/平台研究主题。

## Experiment Groups

### Group 1: control_curation_hot

**Type:** control

**Description:** 策展基线：热度加权推荐（reddit_hot），完整算法策展环境；与 hypothesis_3 experiment_1 共用同一 run（同供给池、同 agent 种子、同 12 ticks），不单独重复运行

**Agent Selection Criteria:** all 100 agents; recommendation_algorithm=reddit_hot


### Group 2: treatment_decuration_chrono

**Type:** treatment

**Description:** 去策展化：时间线排序（chronological），移除热度加权与策展信号；同供给同用户池同种子（与基线唯一差异是 recommendation_algorithm）

**Agent Selection Criteria:** all 100 agents; recommendation_algorithm=chronological

