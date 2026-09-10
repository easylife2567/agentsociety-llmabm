# Experiment 1：算法策展 × 悼念规范压力对逝者数字表征转移的影响

## 设计

全因子 **3 × 2 = 6 cells，每 cell 3 seeds，共 18 runs**：

| 因子 | 水平 |
|------|------|
| 推荐算法 `recommendation_algorithm` | random / chronological / interest（纯兴趣匹配，无热度项） |
| 悼念规范压力 `mourning_norm_pressure` | decay（内生逐周衰减）/ sustained（冻结 W13 峰值） |
| 种子 `random_seed` | 0 / 1 / 2 |

- 环境：`CurationDynamicsSpace`（custom/envs/curation_dynamics_space.py）
- Agent：`CurationDiscourseAgent`（custom/agents/，固定内容类型，0-1 次 LLM 调用/agent-tick）
- 规模：100 agents × 11 ticks（2026-W12→W22，事件周 W13）× 18 runs ≈ 1.98 万 agent-ticks

## 发言决策数字化与帖子倾向分（用户 2026-09-09 裁定）

**帖子倾向分**：每帖（注入 + agent 产出）计算四类倾向分
`tendency_T = 词表命中次数 / max(1, 字数/50)`（命中/50 字密度，与判类器同口径两层匹配；
meme = linkage + 死因词替换「□」后的 strong 命中）。用于 interest 臂匹配
（score = α·本类倾向分 + γ·时新近度 + ε，β 硬命中+词表重合项废弃）
并随 feed item 下发。不使用 LLM 解析帖子类型。

**发言决策**（数值算法，无 LLM）：

```
p = activity × spiral × decay × pressure          （clamp [0, 0.98]）
spiral   = 1 + s·(share_own − base)/base          （沉默的螺旋，clamp[0.05,2]）
decay    = exp(−λ·cum_own/50)                     （注意力衰减，本类累计曝光半饱和）
pressure = 1 − s·P_t                              （mourning 参数为负→同向增益）
```

发言当且仅当 `u < p`，`u = Random(f"{agent_id}:{tick}")`（公共随机数，跨 cell/seed 可比）。
参数按类型锚定实证（marketing 0.90 / education 0.55 / meme 0.50 / mourning 0.55 / other 0.25
活动率；individual = 均值×U[0.8,1.2] 抖动），随 profile 下发。LLM 仅负责内容生成
（含类型词表词融入，每 agent 40 词个人词库）。

**快速校准**（真实周构成 + P_t 公式近似）：decay 模式期望总发言 ≈333 帖/run（>250 ✓）；
W13 悼念冲击 20 帖→快速衰减（9→4）；玩梗前期被压 0-2/周、W20-22 回升至 7-21 帖；
营销稳定 10-13/周。sustained 模式后期玩梗持续受抑（W21/22 ≈15/10 vs 21/15）、
悼念表达更持久——两压力模式的机制对比可见。

## 群体（全部 18 runs 共享）

用户口径类型比例（xlsx author_handle，n=14,313）：**玩梗 41 / 悼念 21 / 营销 13 / 教育 13 / 其他 12**。
由 `curation_personas.build_population(seed=42)` 生成，id-类型打散；人设含沉默螺旋 /
注意力衰减 / 规范压力三机制的类型化表现（锚定数据挖掘实证）。

**类型词表约束**（用户 2026-09-09 裁定）：agent 发言须用本类型词表中的词组织语言。
每个非 other agent 在配置期从 env 判类器同口径列表抽 40 词注入 profile（`type_vocab`，
`Random(43)` 确定性抽样）：meme=linkage 全量+strong 抽样，其余主类=main 抽样，other 无约束。
内容 prompt 要求自然选用 1-3 个词融入正文，使 agent 话语锚定实证词表，
同时让 env 判类标签（assigned_type）与作者类型（pool_type）保持对齐。

## 真实帖子注入（用户裁定：全程约 250 条）

- 源：custom/envs/curation_assets/injection_posts.json（52,716 行 W05–W22，剔除存疑）
- 每 seed 预抽样 250 条（`Random(seed+777)`，W12–W22 池）：保底 15/周 + 85 条按真实周量比例
  → W12=17, W13=35, W14=30, W15=24, W16=22, W17=19, W18=18, W19=18, W20=20, W21=23, W22=24
- **分层比例抽样**：每周池内按 官方/非官方 × 帖子类型 两级最大余数法分配配额，
  样本类型构成确定性贴合当周真实分布（实测各周份额偏差 ≤3.3pp，仅整数取整误差），
  杜绝简单随机抽样的偶发偏斜；随机性只在"组内抽哪几条"
- W13/W14 保证 ≥1 条官方帖（官方议程置顶处理的载体）
- env 侧 `sampling_ratio=1.0`：样本文件即全量注入，不再二次抽样
- 样本文件：init/injection_sample_s{0,1,2}.json（meta 含 weekly_type_counts 审计）

## 配置产物（init/）

- `config_params.py` — 生成脚本（stdlib-only），`experiment-config run` 执行
- `configs/{algorithm}_{pressure}_s{seed}.json` — 18 个 init_config 变体
- `configs/manifest.json` — 批次清单（因子、共享群体、样本、运行命令）
- `init_config.json` — 默认配置（= interest_decay_s0，供标准 CLI / 冒烟）
- `steps.yaml` — start_t=2026-03-16（W12 周一），11 steps × 604800s（1 tick = 1 周）

固定 kwargs：feed_size=20，start_week=2026-W12，event_week=2026-W13，num_ticks=11，
agent_types 映射（100 agents），vocab_path=custom/envs/curation_assets/vocabs.json。
其余（α/β/γ=1.0/1.0/0.5、P_t 权重 0.3/0.4/0.3、official_pin_extend_weeks=1 等）
取 DesignSpec 默认值，待校准与敏感性分析（U2）。

## 运行方式

```bash
# 单个 run
$PYTHON_PATH .agentsociety/bin/ags.py run-experiment start \
  --hypothesis-id 4 --experiment-id 1 \
  --init-config hypothesis_4/experiment_1/init/configs/<run_id>.json \
  --run-id <run_id>
```

先冒烟 1 run（interest_decay_s0）确认管线与 LLM 预算，再跑全部 18 runs。

## 判类与指标口径

- 帖子主类型 = 作者类型（by construction）；env 判类器（悼念>营销>教育>玩梗>噪音>其他，
  仅用 main + meme 四列表）产出 assigned_type / type_mismatch 诊断。
- 主基准：benchmark_curves.json 周度类型矩阵 vs 模拟供给/曝光份额。
