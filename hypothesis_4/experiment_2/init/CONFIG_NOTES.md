# 试点配置生成记录（v0.2）

```json
{
  "design": "DATA_DRIVEN_DESIGN.md v0.2（H3 单 run 双组，5 特征族 × 个体交叉）",
  "seed": 42,
  "pool_n": 140,
  "agents_n": 100,
  "familiarity": {
    "low": 50,
    "high": 50
  },
  "family_counts": {
    "meme": 23,
    "mourning": 29,
    "edu": 27,
    "reflect": 8,
    "casual": 13
  },
  "flavor_counts": {
    "meme/重度玩梗": 17,
    "meme/轻度玩梗": 6,
    "mourning/严肃追思": 6,
    "mourning/悼念加教育": 5,
    "mourning/个人惋惜": 13,
    "mourning/学子惋惜": 5,
    "edu/教育关怀": 7,
    "edu/实用主义": 2,
    "edu/专业就业": 5,
    "edu/基础课业": 2,
    "edu/大学学校": 4,
    "edu/观点讨论": 7,
    "reflect/健康过劳反思": 8,
    "casual/日常杂谈": 12,
    "casual/新闻议论": 1
  },
  "agents_with_secondary_traits": 1.0,
  "meme_band_counts": {
    "high": 23,
    "mid": 24,
    "low": 53
  },
  "recommendation_algorithm": "chronological",
  "start_t": "2026-03-24T08:00:00",
  "run_ticks_total": 12,
  "questionnaires": [
    "T0_baseline",
    "T1_day4",
    "T2_day8",
    "T3_day12"
  ]
}
```

- persona：5 特征族 × 个体特征权重交叉（无平台维度），详见 ../DATA_DRIVEN_DESIGN.md
- 供给池：`supply_pool.json`（自 hypothesis_1 原样迁移，140 条真实文本，seed=42）
- 分组：`agent_profiles.json` 的 `familiarity` 字段（低熟=圈外 / 高熟=圈内），
  与特征族正交（族内分层等比分配）
- 推荐算法：`chronological`（H4 去策展化处理臂；基线见 hypothesis_3/experiment_1）
