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
参数随 profile 下发，individual = 均值×U[0.8,1.2] 抖动。LLM 仅负责内容生成
（含类型词表词融入，每 agent 40 词个人词库）。

**activity 重锚（用户 2026-09-10 发帖人口径）**：activity_mean = 0.60 × (该类型内容份额/
作者份额)，实证比值（W12-W22 注入池 48,360 帖）meme 0.82 / mourning 0.89 / marketing 1.00 /
education 1.02 / other 0.88 → 均值 0.49 / 0.53 / 0.60 / 0.61 / 0.53（各类型接近均匀，
类型分化主要由 spiral/decay/pressure 三机制承载；旧内容口径"营销 0.90 最高"锚定废弃）。

**发言基于所见（用户 2026-09-10 裁定）**：内容生成提示词包含本周 feed 前 5 条
（`feed_context_n=5`，官方置顶/算法排序在前）的作者与正文摘录（单条截 120 字），
要求 Agent 回应、补充、反驳、二创、玩其中的梗或接话跟帖式发言，与所见帖子高度相关的优先展开。

**快速校准**（真实周构成气候代理 + P_t=0.4·M_t+0.3·V_t 近似，类型均值参数）：
decay 模式期望总发言 ≈395 帖/run（>250 ✓，即 ≈395 次内容 LLM 调用/run）；
W12 营销前置主导（20/周）、W13 悼念冲击 20.6 帖→快速衰减（8.4→2.9）；
玩梗 W13-W18 被规范压力压制 ≈0.3/周、W20-22 回潮 12.2/11.8/9.9 帖（对齐真实
W20-22 梗份额 30%→56%→60% 的形态）；教育稳定 5-10.5/周；其他类型后期沉默螺旋收敛。
sustained 模式（P_t 冻结 W13 峰值 0.465）：总发言 ≈362（decay-sustained = +32），
后期玩梗回潮弱 ≈30%（7.3-8.7 vs 9.9-12.2）、营销持续受抑（≈9.7-12 vs 11.2-14.2）
——两压力模式的机制对比可见。

## 群体（全部 18 runs 共享）

用户 2026-09-10 裁定：按**发帖人类型占比**统计（不再按内容划分口径）——
**玩梗 18 / 悼念 21 / 营销 26 / 讨论教育 15 / 其他 20**（100 人）。
由 `curation_personas.build_population(seed=42)` 生成，id-类型打散；人设含沉默螺旋 /
注意力衰减 / 规范压力三机制的类型化表现（锚定数据挖掘实证）。

**类型词表约束**（用户 2026-09-09 裁定）：agent 发言须用本类型词表中的词组织语言。
每个非 other agent 在配置期从 env 判类器同口径列表抽 40 词注入 profile（`type_vocab`，
`Random(43)` 确定性抽样）：meme=linkage 全量+strong 抽样，其余主类=main 抽样，other 无约束。
内容 prompt 要求自然选用 1-3 个词融入正文，使 agent 话语锚定实证词表，
同时让 env 判类标签（assigned_type）与作者类型（pool_type）保持对齐。

## 议程设置（用户 2026-09-10 裁定：官方媒体全程仅一条帖子）

- 官方媒体在 **W13 注入唯一一条讣告帖**（原文给定，pid=official_w13_announcement，
  type=mourning），并对**全员置顶可见**（feed 前部，所有 Agent、所有算法臂一致）
- **除此之外官方媒体无任何其他作用**：
  - 其余真实数据帖一律按普通内容处理（`is_official=False`，不再有官方/非官方分层）
  - P_t 的官方项权重显式置 0（`w_official=0.0`）：`P_t = 0.4·M_t + 0.3·V_t`（上限 0.7）
  - 置顶不延伸（`official_pin_extend_weeks=0`）：讣告帖仅 W13 置顶，W14 起按算法自然竞争
- 讣告帖计入当周 M_t 的悼念供给（1/35），触发后续悼念氛围的内生演化

## 真实帖子注入（用户裁定：全程约 250 条）

- 源：custom/envs/curation_assets/injection_posts.json（52,716 行 W05–W22，剔除存疑）
- 每 seed 预抽样 250 条（`Random(seed+777)`，W12–W22 池）：保底 15/周 + 85 条按真实周量比例
  → W12=17, W13=35（34 普通 + 1 讣告）, W14=30, W15=24, W16=22, W17=19, W18=18,
  W19=18, W20=20, W21=23, W22=24
- **类型分层比例抽样**：每周池内按帖子类型最大余数法分配配额，
  样本类型构成确定性贴合当周真实分布（仅整数取整误差），
  杜绝简单随机抽样的偶发偏斜；随机性只在"组内抽哪几条"
- env 侧 `sampling_ratio=1.0`：样本文件即全量注入，不再二次抽样
- 样本文件：init/injection_sample_s{0,1,2}.json（meta 含 weekly_type_counts 审计
  与官方讣告帖说明）

## 配置产物（init/）

- `config_params.py` — 生成脚本（stdlib-only），`experiment-config run` 执行
- `configs/{algorithm}_{pressure}_s{seed}.json` — 18 个 init_config 变体
- `configs/manifest.json` — 批次清单（因子、共享群体、样本、运行命令）
- `init_config.json` — 默认配置（= interest_decay_s0，供标准 CLI / 冒烟）
- `steps.yaml` — start_t=2026-03-16（W12 周一），11 steps × 604800s（1 tick = 1 周）

固定 kwargs：feed_size=20，start_week=2026-W12，event_week=2026-W13，num_ticks=11，
agent_types 映射（100 agents），vocab_path=custom/envs/curation_assets/vocabs.json，
**w_official=0.0 与 official_pin_extend_weeks=0（议程重设计，见上节）**。
其余（α/γ=1.0/0.5、P_t 权重 M/V=0.4/0.3、β 废弃等）取 DesignSpec 默认值，
待校准与敏感性分析（U2）。

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
