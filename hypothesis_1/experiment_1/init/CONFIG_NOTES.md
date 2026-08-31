# 试点配置生成记录

```json
{
  "seed": 42,
  "pool_n": 140,
  "pool_is_meme": 28,
  "pool_theme_counts": {
    "悼念颂扬": 28,
    "泛议论杂谈": 16,
    "巧乐兹雪碧梗": 20,
    "人生语录": 14,
    "死因健康科普": 12,
    "家庭教育观点": 12,
    "志愿填报干货": 10,
    "学习方法观点": 10,
    "公司接班后事": 8,
    "借势营销": 10
  },
  "agents_n": 100,
  "low_familiarity_n": 59,
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

- 供给池：`supply_pool.json`（真实文本采样，dup 加权，seed=42；删除该文件可重采样）
- 推荐臂：基线 `chronological`（臂 A）；Q1 三臂对照复制本配置仅改 `recommendation_algorithm`
  （臂 B 个性化需 `douyin_space.py` 二期实现；臂 C `random`）
- 试点简化：producer 不作为 LLM agent（静态存量供给池），详见 DATA_DRIVEN_DESIGN.md §2.3
