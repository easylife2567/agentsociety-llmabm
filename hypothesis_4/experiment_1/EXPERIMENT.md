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

**发言决策**（数值算法，无 LLM；用户 2026-09-10 裁定改**表达效用模型**（方案 B），
Kuran 1995《Private Truths, Public Lies》偏好伪装的成本-收益框架；Castillo & Cozzo 2025
（arXiv:2510.14098）螺旋之沉默 ABM 同框架；Bicchieri 2006 规范凸显 × 偏差成本）：

```
U = D·R − c·v·P_t                                  （表达效用 = 收益 − 规范成本）
D = 1 + s·(share_own − base)/base, clamp[0.05,2]   （沉默的螺旋：收益侧气候共振）
R = exp(−λ·cum_own/50)                             （注意力衰减：收益侧疲劳折减）
C = c·v·P_t                                        （悼念规范表达成本，c=1.0 全局尺度）
发言当且仅当 U ≥ activity
```

收益与成本不可通约地相乘/相减进入效用，杜绝线性等权平均的**补偿性稀释**（线性规则下
高收益项可被低收益项平均拉平，sustained 压力臂的操纵会被稀释——识别性关键缺陷）。
`v` = norm_dev 结构性规范偏离成本系数：玩梗 1.0 > 营销 0.8 > 其他 0.7 > 教育 0.15；
**悼念 −0.5 = 与悼念规范同向**（压力反成表达补贴——压力高的时期正是悼念表达最盛的时期）。
`activity` = **个体表达门槛**：效用低于门槛则保持沉默，高于则必然发言；**活跃的 agent
门槛低、容易发言**。中性状态（D≈R≈1、P_t≈0）下 U≈1.0。决策完全确定（无随机数）：
给定环境快照与参数，行为唯一，跨 cell 可比性最强；种子差异仅通过注入样本→环境状态
传导。参数随 profile 下发，individual = 均值×U[0.8,1.2] 抖动。LLM 仅负责内容生成
（含类型词表词融入，每 agent 40 词个人词库）。

**activity 门槛语义与锚定（用户 2026-09-10 裁定）**：类型均值统一 = 0.95（校准值，
见下），个体门槛 ∈ [0.76, 1.14]。类型间不设门槛差异：发帖人口径下各类型人均发帖强度
（内容份额/作者份额，W12-W22 注入池 48,360 帖）实证 meme 0.82 / mourning 0.89 /
marketing 1.00 / education 1.02 / other 0.88 ≈ 1；类型行为分化由 spiral/decay/norm_dev
三机制参数承载（锚定数据挖掘实证，不变；旧内容口径"营销 0.90 概率最高"锚定废弃）。

**发言基于所见（用户 2026-09-10 裁定）**：内容生成提示词包含本周 feed 前 5 条
（`feed_context_n=5`，官方置顶/算法排序在前）的作者与正文摘录（单条截 120 字），
要求 Agent 回应、补充、反驳、二创、玩其中的梗或接话跟帖式发言，与所见帖子高度相关的优先展开。

**快速校准**（表达效用模型；`calibrate_speak.py` 留档可复跑：真实周构成气候代理
[benchmark 周度矩阵剔除爬取噪音] + P_t=0.4·M_t+0.3·V_t 近似 + 群体 seed=42 +
cum_own += feed_size×本类份额 的期望曝光代理）：
门槛基数扫描 1.0/0.95/0.9/0.85/0.8/0.7 → decay 臂总量 307/352/411/464/520/622 帖/run，
sustained 臂 218/251/293/322/360/496；取 **0.95**（decay 352 帖/run，agent 供给 ~58%
> 注入 250 ✓，即 ≈350 次内容 LLM 调用/run；与线性规则旧定标 ≈330@57% 同位）。
decay 模式形态：W12 营销前置主导（26 帖 + 教育 6）、W13 悼念冲击 21 帖→注意力疲劳
快速衰减（8→1→0）；玩梗 W12-W19 被规范成本压制 ≈0、W20-22 回潮 18/18/18 帖
（对齐真实 W20-22 梗份额 30%→56%→60% 的形态）；教育稳定 3-15/周；其他/营销随
P_t 衰减在 W14-W19 逐步恢复。sustained 模式（P_t 冻结 W13 峰值）：总发言 ≈251
（decay−sustained = +101；线性规则仅 +28——效用模型下压力臂操纵不再被平均稀释，
机制对比显著增强）：营销 W14-W19 被成本压至 ≈0（decay 臂 1-17/周，"先致哀再带货"
的策略性收敛可见），悼念尾部反而更长（W13-15 45 vs 30 帖，规范与悼念表达同向的
补贴效应可见），玩梗回潮几乎不受影响（53 vs 54 帖，梗的反抗性由气候共振承载而非
压力路径）——两压力模式的机制对比可见。
确定性门槛的行为学注记：效用一旦越过全部个体门槛，该类型整周全员发言（饱和）；
一旦跌落则趋锁定沉默，周间翻转比概率规则更陡——这是门槛模型的固有性质，
个体门槛 U[0.8,1.2] 抖动使其在类型层面仍呈渐变。

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
- **口径区分（用户 2026-09-10 确认）**：注入分层只依据**各周帖子（内容）类型占比**，
  与 agent 群体构成（18/21/26/15/20，**发帖人口径**，仅用于群体装配与沉默螺旋基线
  base）相互独立、互不混用
- env 侧 `sampling_ratio=1.0`：样本文件即全量注入，不再二次抽样
- 样本文件：init/injection_sample_s{0,1,2}.json（meta 含 weekly_type_counts 审计
  与官方讣告帖说明）

## 配置产物（init/）

- `config_params.py` — 生成脚本（stdlib-only），`experiment-config run` 执行
- `configs/{algorithm}_{pressure}_s{seed}.json` — 18 个 init_config 变体
- `configs/manifest.json` — 批次清单（因子、共享群体、样本、运行命令）
- `init_config.json` — 默认配置（= interest_decay_s0，供标准 CLI / 冒烟）
- `steps.yaml` — start_t=2026-03-16（W12 周一），11 steps × 604800s（1 tick = 1 周）

固定 kwargs：feed_size=10（用户 2026-09-10 裁定，每 agent 每周 10 条信息流），
start_week=2026-W12，event_week=2026-W13，num_ticks=11，
agent_types 映射（100 agents），vocab_path=custom/envs/curation_assets/vocabs.json，
**w_official=0.0 与 official_pin_extend_weeks=0（议程重设计，见上节）**。
其余（α/γ=1.0/0.5、P_t 权重 M/V=0.4/0.3、β 废弃等）取 DesignSpec 默认值，
待校准与敏感性分析（U2）。

## 运行方式

**多 run 编排（2026-09-10 源码核实）**：平台约定一个 experiment 只有一个固定 `run/`
槽位（`agentsociety2/skills/experiment/config.py:96`），扩展 skill 的 `--run-id` 不影响
run 目录且重复跑同一 `run/` 会把 replay 追加混写（`replay_sink.py` O_APPEND）。
引擎 CLI 原生支持任意 `--run-dir`（`agentsociety2/society/cli.py`），故 18 个 run
各自独立目录放在 `runs/<run_id>/`；`ags.py run-experiment status` 只看固定 `run/`，
18 个 run 的状态由监视器总览承担。

```bash
# 冒烟 1 run（标准入口，落固定 run/）
$PYTHON_PATH .agentsociety/bin/ags.py run-experiment start \
  --hypothesis-id 4 --experiment-id 1 \
  --init-config hypothesis_4/experiment_1/init/configs/interest_decay_s0.json

# 18 runs（引擎 CLI 直启，各自独立 run 目录；顺序或 ≤3 并发，控 LLM 速率）
for cfg in hypothesis_4/experiment_1/init/configs/{algorithm}_{pressure}_s{seed}.json; do
  run_id=$(basename "$cfg" .json)
  $PYTHON_PATH -m agentsociety2.society.cli \
    --config "$cfg" \
    --steps  hypothesis_4/experiment_1/init/steps.yaml \
    --run-dir hypothesis_4/experiment_1/runs/$run_id \
    --experiment-id h4e1_$run_id \
    --log-file hypothesis_4/experiment_1/runs/$run_id/engine.log
done

# 中断恢复（引擎原生：从 run_dir/SOCIETY.json 续跑）
# 在上述命令末尾追加 --resume
```

## 监视器（实时状态快照，零侵入）

引擎每 tick 立即落盘（replay JSONL 追加写、ENV_STATE.json 原子重写、pid.json ~1s 心跳），
`monitor.py` 纯读这些文件、把每个 run 的最新状态刷新为快照（无 watch 循环，
想看最新就再跑一次；零 LLM 调用）：

```bash
$PYTHON_PATH hypothesis_4/experiment_1/monitor.py                  # 自动发现 run/ 与 runs/*，刷新全部快照
$PYTHON_PATH hypothesis_4/experiment_1/monitor.py --week 2026-W13  # 只看某周
```

- 输出：`monitor/<run_id>/status.md`（人读周报）+ `status.json`（机读全量）；
  `monitor/overview.md|json`（18+1 run 总览）
- 内容：进程/进度、周度指标（P_t、供给/曝光构成、官方槽位）、Agent 行为聚合
  （发言率/判类不一致）、机制透视（U、门槛、收益/成本分量）、帖子流（帖池按周 +
  进行中新帖）、派生视图（策展偏差 = 曝光−供给、模拟 vs 真实基准）
- 每张表附字段说明，`status.json` 内嵌 `field_docs` 全量词汇表

先冒烟 1 run（interest_decay_s0）确认管线与 LLM 预算（≈350 次内容调用/run），
再跑全部 18 runs。

## 判类与指标口径

- 帖子主类型 = 作者类型（by construction）；env 判类器（悼念>营销>教育>玩梗>噪音>其他，
  仅用 main + meme 四列表）产出 assigned_type / type_mismatch 诊断。
- 主基准：benchmark_curves.json 周度类型矩阵 vs 模拟供给/曝光份额。
