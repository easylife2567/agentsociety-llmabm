# Experiment 1：算法策展 × 玩梗涌现环境对逝者数字表征转移的影响

## 设计

全因子 **3 × 2 = 6 cells，每 cell 3 seeds，共 18 runs**：

| 因子 | 水平 |
|------|------|
| 推荐算法 `recommendation_algorithm` | random / chronological / interest（纯兴趣匹配，无热度项） |
| 玩梗涌现模式 `meme_emergence_mode` | normal（S 逐周调度）/ sustained_hot（事件周后冻结 S） |
| 种子 `random_seed` | 0 / 1 / 2 |

- 环境：`CurationDynamicsSpace`（custom/envs/curation_dynamics_space.py）
- Agent：`CurationDiscourseAgent`（custom/agents/，固定内容类型，0-1 次 LLM 调用/agent-tick）
- 规模：100 agents × 11 ticks（2026-W12→W22，事件周 W13）× 18 runs ≈ 1.98 万 agent-ticks

## 发言决策数字化与帖子倾向分（用户 2026-09-09 裁定）

**帖子倾向分**：每帖（注入 + agent 产出）计算四类倾向分
`tendency_T = 词表命中次数 / max(1, 字数/50)`（命中/50 字密度，与判类器同口径两层匹配；
meme = linkage + 死因词替换「□」后的 strong 命中）。用于 interest 臂匹配
（2026-09-12 起 `score = (α·本类倾向分 + γ) · 生命力`，β 硬命中+词表重合项废弃；
旧加性时新项 `γ·max(0,1−age/8)` 退役，见"feed 机制"节）
并随 feed item 下发。不使用 LLM 解析帖子类型。

**发言决策**（数值算法，无 LLM；2026-09-10 机制重设计裁定：**涌现增益表达效用模型**，
取代悼念规范成本项；锚定注意力经济——Simon 1971「信息的丰裕造成注意力的稀缺」、
生态位/logistic 增长——meme 需要未饱和空间才能指数扩张、模因论——Dawkins 1976
模因在丰宿主池中复制变异）：

```
U = D·R·G^θ                                        （表达效用 = 三因子乘法）
D = 1 + s·(share_own − base)/base, clamp[0.05,2]   （沉默的螺旋：收益侧气候共振）
R = exp(−λ·cum_own/50)                             （注意力衰减：收益侧疲劳折减）
G = clamp(B^β·S^σ, 0.2, 3.0)                       （玩梗涌现环境增益，env 侧逐周计算）
发言当且仅当 U ≥ activity
```

**玩梗涌现环境的存量/流量语义（用户 2026-09-10 裁定）**：总帖子越丰沛越易诞生 meme
（存量 B），当期新增帖子越少越空旷、越宜 meme 传播（流量 S）：

```
Stock_t = 过去 6 周 arena 供给总数（内生：注入 + agent 帖，滚动窗口）
B_t = f(Stock_t)/f(Stock_base),  f(x)=x/(x+K_a)    （丰沛度；基线周 W12=1）
Flow_t = 现实口径周新增帖量（外生调度 emergence_flow_by_week = 真实数据各周全量帖数）
S_t = h(Flow_t)/h(Flow_base),  h(x)=K_f/(K_f+x)    （空旷度；基线周=1）
K_a 默认 = 注入计划事件周窗口存量（17+35=52）；K_f 默认 = 调度基线周值（1246）
```

**实现裁定（S 外生 / B 内生）**：sim arena 的流量被 250 条注入预算压缩（保底 15/周
托底谷值、洪峰仅 ~2×、agent 供给又平稳 → arena 总流量峰谷比 ~1.6×，远弱于现实 ~9×），
单靠内生计数表达不出真实洪峰/退潮节律，S 会失去臂间对比度；故 **S 读外生现实口径调度
（完全体现裁定中的"空旷度"语义），B 保持内生**（arena 供给驱动，保留 meme 再拥挤
反哺存量、G 回落自限的反馈回路）。`θ` = emergence 结构系数：仅玩梗型 1.0
（洪峰期新表达被淹没、退潮期才被看见），其余类型 0（G^0≡1，环境不影响其决策）。

**反事实臂 sustained_hot（用户 2026-09-10 裁定）**：事件周（W13）记录 S，之后冻结
（维持高热 = 洪峰不退）；B 保持内生。normal 臂 S 随现实调度逐周回落 → 玩梗 W19-20
起量；sustained_hot 臂 S 压在 W13 洪峰的低空旷值 → 玩梗起量被推迟/抑制。两臂与三种
算法全因子交叉：interest 臂的选择性曝光可让玩梗 agent 在同温层内部分突破环境压制
（算法 × 涌现交互项）。

三因子全部乘法进入效用，杜绝线性等权平均的**补偿性稀释**。`activity` = **个体表达
门槛**：效用低于门槛则保持沉默，高于则必然发言；**活跃的 agent 门槛低、容易发言**。
中性状态（D≈R≈1、G=1）下 U≈1.0。给定环境快照与参数，**发言决策本身仍然确定**
（agent 侧无随机数）：gate 由 fetch 到的 feed 快照唯一决定；随机性只存在于
**平台的 feed 选址**（interest 臂比例抽样，见"feed 机制"节，独立 RNG 流
`seed+3000`，同 seed 跨 cell 抽出同一序列，故臂间/seed 间可比性不变）。参数随 profile
下发，individual = 均值×U[0.8,1.2] 抖动。LLM 仅负责内容生成（含类型词表词融入，
每 agent 40 词个人词库）。

> **2026-09-12 机制修订（用户裁定）**：D 因子的输入 `share_own` = 该 agent 本周 feed 中
> 本类内容占比。烟测发现旧实现下"同类型 agent 拿到同一份 top-10"，使 share_own 只能取
> {0,1} 两个端点、D 退化成 0.05↔2.0 的开关（W18→W19 发言率因此从 0 一步到 1.0）。
> 修复放在**推荐算法侧**（帖子生命周期 + 兴趣比例抽样），D 的公式与
> `activity` 门槛本轮未动 —— 诊断与裁定见 `SMOKE_DIAGNOSIS_w19_cliff.md`。

**activity 门槛语义与锚定（用户 2026-09-10 裁定）**：类型均值统一 = 0.95（校准值，
见下），个体门槛 ∈ [0.76, 1.14]。类型间不设门槛差异：发帖人口径下各类型人均发帖强度
（内容份额/作者份额，W12-W22 注入池 48,360 帖）实证 meme 0.82 / mourning 0.89 /
marketing 1.00 / education 1.02 / other 0.88 ≈ 1；类型行为分化由 spiral/decay/emergence
三机制参数承载（锚定数据挖掘实证，不变）。

**发言基于所见（用户 2026-09-10 裁定）**：内容生成提示词包含本周 feed 前 5 条
（`feed_context_n=5`，官方置顶/算法排序在前）的作者与正文摘录（单条截 120 字），
要求 Agent 回应、补充、反驳、二创、玩其中的梗或接话跟帖式发言，与所见帖子高度相关的优先展开。

**快速校准**（涌现增益模型；`calibrate_speak.py` 留档可复跑：与 env 同构的端到端
代理推演——agent 发言滞后 1 tick 入池反哺 Stock、S 读现实口径调度、sustained_hot
事件周后冻结、cum_own += 该 agent 本 tick 实际见到的本类槽位数）。

**2026-09-12 重写（口径修正）**：气候输入不再是"benchmark 周度矩阵剔除爬取噪音"的
外生代理（该口径与真实 sim 的"agent 本人 feed 类型分布"不一致，正是"校准说 W19 温和起量、
sim 却一步到顶"的来源），改为**按与 env 相同的机制推演 feed**：候选池 = 真实注入样本
（带正文 → 共享函数算真倾向分）+ agent 帖（按烟测实测的类型中位数倾向分画像入池），
再走生命周期 / 曝光饱和 / 退场 / 兴趣打分 / softmax 抽样得到 share_own → D。
机制同构由代码保证（`custom/envs/curation_mechanisms.py` 被 env 与校准脚本同时 import），
另加 `--assert-replay <run_dir>`：用 replay 逐周供给计数复算 B/S/G 并与落盘值逐值比对
（容差 1e-4，replay 存 4 位小数）——已通过（11 周全部一致）。

复核定标（2026-09-12）：门槛基数维持 **0.95**（用户裁定"本轮不动"）。基准下 normal 臂
代理总量 525-580 帖/run（旧机制定标 463，上移主因气候从 {0,1} 变为有梯度后多数类型的 D
抬升），agent 供给仍 > 注入 250。若按旧"300-350 帖/run"目标则对应门槛基数 1.15
（代理总量 337、玩梗轨迹 0/0/0/0/2/2/6/13/15/17 更平缓）——**留作后续裁定项**。

normal 臂形态（base=0.95，代理）：环境轨迹 G = W12 1.0 → W13 0.51（洪峰淹没）→ W15 1.33
→ W18-W19 3.0（退潮见顶，触上限）→ W20 2.29 → W22 1.38（meme 再拥挤自限回落）；
玩梗 share_own（D 的输入）0.00/0.00/0.01/0.01/0.02/0.03/**0.11/0.31/0.46/0.56/0.54**
（W12→W22，逐 agent sd 0.02→0.16），即玩梗型 agent 由"看不到玩梗内容"逐周过渡到
"feed 中过半是玩梗"，恰是"轻度玩梗者更晚越过门槛"的机制来源。

**确定性门槛的行为学注记（2026-09-12 修订）**：旧版此处写"个体门槛 U[0.8,1.2] 抖动
使其在类型层面仍呈渐变"——**该判断已被烟测反证**：真实的陡峭度不来自门槛抖动，而来自
D 的输入退化（share_own 只能取 {0,1} → D 成为 40 倍开关 → 全类型同步翻转）。修正后
share_own 逐 agent 有梯度（sd ≈0.05-0.16），门槛的确定性不再导致同步翻转；但仍存在
"高分组先越过门槛、组内随后全员饱和"的台阶性质，其陡度由 G 的量级（本轮未动）决定。

反事实臂 sustained_hot（S 冻结在 W13 值 0.20）：G 压平在 0.50-0.72，代理玩梗轨迹
0/0/0/0/1/3/1/2/14/27/41 vs normal 的 0/0/0/0/1/3/9/17/18/18/18 —— **臂间差集中在
W18 起的起量时点与幅度**（W20-22 代理总量 27 vs 54）；两臂总供应接近（523 vs 580），
更强的对比预期出现在算法 × 涌现交互（interest 选择性曝光的同温层突破）。

OAT 敏感性（base=0.95，代理）：normal 臂总量对 K_a/K_f/β/σ/抽样温度/半衰期总体稳健
（545-590），但**玩梗起步幅度（W18-W19）对 K_a 与 β/σ 敏感**（K_a×0.5 → 起步 5 帖、
K_a×2 → 35 帖；β=0.5 → 起步 0 帖）——因为起步期 G 由 B^β·S^σ 决定、而玩梗 U 恰在
门槛附近；sustained_hot 臂对同一组参数更敏感（S 冻结后 G 常年贴近玩梗 U 门槛）。
起步值维持 env 默认（β=σ=1、K_a/K_f 自动），留待 U2 敏感性分析统一处理。

### feed 机制（用户 2026-09-12 裁定，诊断见 `SMOKE_DIAGNOSIS_w19_cliff.md`）

烟测暴露两个机制缺陷，修复集中在"**内容可得性 + 选择**"两步，**打分函数本身不变**
（仍无帖子级热度/互动项，纯兴趣匹配的最小机制）：

1. **帖子生命周期**（平台级内容可得性，**三算法臂共用同一候选池**）：
   每帖 `life`（创建 1.0，每周 × `0.5**(1/half_life)`，half_life=1.5 周）；
   打分用 `生命力 = life × 0.5**(累计曝光 / saturation_scale)`（尺度 20，
   即"被推给约 20 人后吸引力减半"）；`life < retire_floor`（0.35 ≈ **3 周流通窗口**）
   的帖**退出候选池**，等效于一个自适应候选窗口。退场只按时间生命判、不按曝光饱和判。
2. **兴趣比例抽样**（interest 臂的选择实现）：把"按分数排序取前 feed_size 条"换成
   "按 `exp(score/temperature)`（温度 4.0）**无放回抽** feed_size 条"，
   独立 RNG 流 `Random(seed+3000)`；`temperature<=0` 退化为确定性 top-k（消融档）。

**三臂可比性约定**：生命周期/退场是**平台级**规则（三臂候选池完全相同、同周
`feed_live_pool` 与置顶槽位数必须相等），算法差异只体现在"如何从同一候选池选出
feed_size 条"：random = 均匀抽样；chronological = 时间倒序取最新；interest = 按兴趣分
比例抽样。此约定使"interest vs random"的差异可归因于**排序/选择**而非池子不同。

**为什么"曝光上限"以饱和衰减落地而非硬上限**：预飞实测硬性"每帖每周最多推给 C 个
agent"会饿死早期 feed（W12 仅 47 帖，C=2 只供 94 槽位而当周需求 1000 槽位），
且 C=1/2/3 会把五类气候一起压到 0.1-0.3、沉默螺旋机制失效。

**被实测排除的改法**（记录以防重走）：寿命衰减单独使用、以及 ±20%/±30%/±50% 的
逐 (agent,帖) 排序抖动，均**无法**改变"同类型 agent 共享同一份 top-10"——因为只要
"取分数最高的 k 条"这个操作还在、而高分帖数量 ≥ k（W20 有 19 条、W22 有 68 条），
选出的集合就与 agent 无关。

## 群体（全部 18 runs 共享）

用户 2026-09-10 裁定：按**发帖人类型占比**统计（不再按内容划分口径）——
**玩梗 18 / 悼念 21 / 营销 26 / 讨论教育 15 / 其他 20**（100 人）。
由 `curation_personas.build_population(seed=42)` 生成，id-类型打散；人设含沉默螺旋 /
注意力衰减 / 玩梗涌现环境三机制的类型化表现（锚定数据挖掘实证；仅玩梗型人设描述
涌现环境敏感性，其余类型人设明确"环境冷热影响不大"，与 θ=0 一致）。

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
  - 官方置顶不延伸（`official_pin_extend_weeks=0`）：讣告帖仅 W13 置顶，W14 起按算法自然竞争
- 讣告帖作为普通注入帖计入当周 arena 供给（1/35），进入存量/流量的环境统计，
  触发后续涌现环境的内生演化

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

- `config_params.py` — 生成脚本（stdlib-only），`experiment-config run` 执行；
  内含涌现流量调度 `EMERGENCE_FLOW_BY_WEEK`（= 真实数据各周全量帖数，与注入同源）
- `configs/{algorithm}_{mode}_s{seed}.json` — 18 个 init_config 变体
  （mode ∈ normal / sustained_hot）
- `configs/manifest.json` — 批次清单（因子、共享群体、样本、涌现环境语义与调度、运行命令）
- `init_config.json` — 默认配置（= interest_normal_s0，供标准 CLI / 冒烟）
- `steps.yaml` — start_t=2026-03-16（W12 周一），11 steps × 604800s（1 tick = 1 周）

固定 kwargs：feed_size=10（用户 2026-09-10 裁定，每 agent 每周 10 条信息流），
start_week=2026-W12，event_week=2026-W13，num_ticks=11，
agent_types 映射（100 agents），vocab_path=custom/envs/curation_assets/vocabs.json，
**emergence_flow_by_week（现实口径周新增调度）与 official_pin_extend_weeks=0
（议程重设计，见上节）**。其余涌现参数（emergence_window_stock=6 / emergence_ka /
emergence_kf / emergence_beta=1.0 / emergence_sigma=1.0 / gain clamp[0.2,3.0]）与
α/γ=1.0/0.5 取 env 默认值，待校准与敏感性分析（U2）。

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
  --init-config hypothesis_4/experiment_1/init/configs/interest_normal_s0.json

# 18 runs（引擎 CLI 直启，各自独立 run 目录；顺序或 ≤3 并发，控 LLM 速率）
for cfg in hypothesis_4/experiment_1/init/configs/{random,chronological,interest}_{normal,sustained_hot}_s{0,1,2}.json; do
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
- 内容：进程/进度、周度指标（涌现环境 B/S/G、存量/新增、供给/曝光构成、官方槽位）、
  Agent 行为聚合（发言率/判类不一致）、机制透视（U、门槛、收益/环境乘子分量）、
  帖子流（帖池按周 + 进行中新帖）、派生视图（策展偏差 = 曝光−供给、模拟 vs 真实基准）
- 每张表附字段说明，`status.json` 内嵌 `field_docs` 全量词汇表

先冒烟 1 run（interest_normal_s0）确认管线与 LLM 预算（≈460 次内容调用/run），
再跑全部 18 runs。

## 判类与指标口径

- 帖子主类型 = 作者类型（by construction）；env 判类器（悼念>营销>教育>玩梗>噪音>其他，
  仅用 main + meme 四列表）产出 assigned_type / type_mismatch 诊断。
- 主基准：benchmark_curves.json 周度类型矩阵 vs 模拟供给/曝光份额。
