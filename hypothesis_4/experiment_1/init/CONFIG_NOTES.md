# 试点配置生成记录(v0.3, reddit_hot(策展基线))

```json
{
  "design": "DESIGN_V0.3.md(6 类群代表/周级/媒体归env/背景互动当量)",
  "scale": 0.01041,
  "target_pool": 500,
  "window_total_real": 48019,
  "pool_n": 521,
  "media_n": 23,
  "media_week": {
    "2026-W12": 1,
    "2026-W13": 6,
    "2026-W14": 4,
    "2026-W15": 3,
    "2026-W16": 2,
    "2026-W17": 1,
    "2026-W18": 1,
    "2026-W19": 1,
    "2026-W20": 1,
    "2026-W21": 2,
    "2026-W22": 1
  },
  "week_counts": {
    "2026-W12": 14,
    "2026-W13": 124,
    "2026-W14": 93,
    "2026-W15": 54,
    "2026-W16": 41,
    "2026-W17": 26,
    "2026-W18": 19,
    "2026-W19": 19,
    "2026-W20": 29,
    "2026-W21": 47,
    "2026-W22": 55
  },
  "category_counts": {
    "marketing": 131,
    "mourning": 101,
    "general": 96,
    "edu": 83,
    "meme": 74,
    "noise": 36
  },
  "initial_like_rule": "likes0 = lognorm(mu=ln(cat_base*(0.3+0.7*week_attn)*12), sigma=0.8), cap 400; views0=likes0*25*(1+U(0,0.5)); reposts/comments 初始为 0(由模拟内生成)",
  "cat_base_like": {
    "marketing": 1.0,
    "mourning": 1.6,
    "general": 0.8,
    "edu": 1.2,
    "meme": 1.1,
    "noise": 0.3
  },
  "media_oversample": 3.0,
  "agents_n": 6,
  "recommendation_algorithm": "reddit_hot",
  "start_t": "2026-03-16T00:00:00",
  "event_start": "2026-03-24T08:00:00",
  "tick_seconds": 604800,
  "run_ticks_total": 12,
  "questionnaires": [
    "T0@W12",
    "T1@W15",
    "T2@W19",
    "T3@W22"
  ]
}
```

## 设计依据
- 设计总纲: [../../DESIGN_V0.3.md](../../DESIGN_V0.3.md)(2026-09-07 用户裁定版)
- 效标: [../../benchmark_curves.json](../../benchmark_curves.json)
- 生成器: `config_params.py`(可复现;E2 由同一脚本产出,仅 `recommendation_algorithm` 不同)

## 关键设定
- **Agent**: 6 类群代表(1 agent = 1 内容类群,全量占比划行动预算);权威媒体(id=999)为 env 侧供给源,非问卷对象
- **供给池**: xlsx 周×类群采样 521 条(真实宇宙 48019 条,scale≈0.01041),created_at 按真实发表时间错峰(时间门控依赖)
- **媒体**: 周 verified×scale×3 过采样(保议程可见性),重指派给 999,仅非噪音类
- **初始互动**: 机制规则合成(类群底数×周注意力×对数正态,seed 固定),非黑箱
- **时间**: start_t=2026-03-16T00:00:00(W12 周一),tick=604800s=1 周,12 ticks 覆盖 W12→W23;死亡事件 2026-03-24T08:00:00(W13)经 S(t) 与媒体/供给帖注入
- **问卷**: T0@W12 生前基线 / T1@W15 悼念退潮 / T2@W19 二波启动 / T3@W22 玩梗峰值
- **唯一实验操纵**: `recommendation_algorithm=reddit_hot(策展基线)`
