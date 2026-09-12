# Experiment 1：算法策展对逝者数字表征转移的影响

## 设计

**单因子 3 臂 × 3 seeds = 9 runs**（用户 2026-09-12 裁定：玩梗涌现环境增益 G 退役，
原 3×2 全因子的第二因子随之失效 → 降为单因子；见 `SMOKE_DIAGNOSIS_w19_cliff.md` §五之三/§五之四）：

| 因子 | 水平 |
|------|------|
| 推荐算法 `recommendation_algorithm` | random / chronological / interest（纯兴趣匹配，无热度项） |
| 种子 `random_seed` | 0 / 1 / 2 |

- 环境：`CurationDynamicsSpace`（custom/envs/curation_dynamics_space.py）
- Agent：`CurationDiscourseAgent`（custom/agents/，固定内容类型，0-1 次 LLM 调用/agent-tick）
- 规模：100 agents × 11 ticks（2026-W12→W22，事件周 W13）× **9 runs ≈ 0.99 万 agent-ticks**
- run_id 命名：`{algorithm}_s{seed}`（原 `{algorithm}_{mode}_s{seed}` 随第二因子退役）

## 发言决策数字化与帖子倾向分（用户 2026-09-09 裁定）

**帖子倾向分**：每帖（注入 + agent 产出）计算四类倾向分
`tendency_T = 词表命中次数 / max(1, 字数/50)`（命中/50 字密度，与判类器同口径两层匹配；
meme = linkage + 死因词替换「□」后的 strong 命中）。用于 interest 臂匹配
（2026-09-12 起 `score = (α·本类倾向分 + γ) · 生命力`，β 硬命中+词表重合项废弃；
旧加性时新项 `γ·max(0,1−age/8)` 退役，见"feed 机制"节）
并随 feed item 下发。不使用 LLM 解析帖子类型。

**发言决策**（数值算法，无 LLM；**2026-09-12 用户裁定：双规则表达效用模型** ——
原第三因子"玩梗涌现环境增益 G"退役，Agent 只由沉默螺旋与注意力衰减两条规则约束）：

```
U = D·R                                                  （表达效用 = 两因子乘法）
D = 1 + s·tanh(k·(share_own − base)/base), k=1.5         （沉默的螺旋：有界、无地板）
R = exp(−λ·cum_own/50)                                   （注意力衰减：收益侧疲劳折减）
发言当且仅当 U ≥ activity
```

D 的形式化依据（文献检索，2026-09-12）：Blanco 2005 的博弈模型给出"发言门槛 =
孤立成本/(收益+成本)"，与本模型 U ≥ activity 的门槛结构同构（D<0 即表达存在净成本
= 孤立成本）；Sohn & Geidner 2015 / Cabrera et al. 2021 用 logistic 有界映射把意见气候
δ 转成表达意愿（其 δ 以 50% 为参照，五类场需改以"本类型期望占比"为参照）；Granovetter
1978 阈值分布对应 activity 的 U[0.8,1.2] 个体抖动。原 `clamp(1+s·x, 0.05, 2.0)` 的地板
经实测**在行为上不可观测**（抬到 0.7 结果不变），其真实副作用是把"气候不利"时的所有
类型压成同一个值、抹掉 spiral 的类间差异。实现见共享纯函数
`custom/envs/curation_mechanisms.py::spiral_factor`（agent 与校准脚本同源）。

**玩梗涌现环境已降为观测序列**：env 侧仍逐周计算 B（存量丰沛度）/ S（流量空旷度）/
G = clamp(B^β·S^σ, 0.2, 3.0) 并写入 replay 与监控，作为描述性时间轴与审计线索，
**不进入任何类型的决策**。

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

**~~反事实臂 sustained_hot~~（2026-09-12 退役：θ≡0 时冻结 S 无行为差异；原语义如下）**：事件周（W13）记录 S，之后冻结
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

~~反事实臂 sustained_hot~~（已退役，以下为历史记录；S 冻结在 W13 值 0.20）：G 压平在 0.50-0.72，代理玩梗轨迹
0/0/0/0/1/3/1/2/14/27/41 vs normal 的 0/0/0/0/1/3/9/17/18/18/18 —— **臂间差集中在
W18 起的起量时点与幅度**（W20-22 代理总量 27 vs 54）；两臂总供应接近（523 vs 580），
更强的对比预期出现在算法 × 涌现交互（interest 选择性曝光的同温层突破）。

OAT 敏感性（base=0.95，代理）：normal 臂总量对 K_a/K_f/β/σ/抽样温度/半衰期总体稳健
（545-590），但**玩梗起步幅度（W18-W19）对 K_a 与 β/σ 敏感**（K_a×0.5 → 起步 5 帖、
K_a×2 → 35 帖；β=0.5 → 起步 0 帖）——因为起步期 G 由 B^β·S^σ 决定、而玩梗 U 恰在
门槛附近；sustained_hot 臂对同一组参数更敏感（S 冻结后 G 常年贴近玩梗 U 门槛）——该敏感性随 G 退役一并作废。
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

## no-G 探针 → 已升格为正式模型（用户 2026-09-12 裁定）

**裁定**：「G 没有生效，直接去掉 G 反而好解释 —— 只由沉默螺旋和注意力衰减两条规则
约束 Agent」；并连带裁定实验组降为**单因子 3 臂 × 3 seeds = 9 runs**。
本节保留该探针的构造与**实测结果**，作为"G 退役"这一改动的证据留痕。

**构造**：`init/configs/interest_nog_s0.json` —— 与 `interest_normal_s0` **逐字段相同**，
唯一差别 = 18 个玩梗 agent 的 `params.emergence`（该参数现已退役） 由抖动值（均值 1.0、U[0.8,1.2]）改为 **0.0**
（其余四类本就 θ=0，共 82 个 agent 不变）。env 段逐字节相同、注入样本相同、群体 seed 相同。

**实现选择（当时）**：θ=0（agent 侧）而非 env 侧 G≡1 —— 两者行为完全等价
（θ=0 ⟺ G^θ≡1）；θ=0 不动 env、不动群体其余参数，且监控里 B/S/G 仍逐周记录
（能看到"被解耦的环境本身"）。**正式模型进一步把 U 的表达式直接改为 U = D·R**
（不再保留 G^θ 项），B/S/G 作为观测序列保留。

**门槛口径（用户裁定：不调，沿用 0.95）**：门槛基数锚定中性状态（D≈R≈1 → U≈1.0）。
代理复扫佐证：**门槛对起爆时点无杠杆** ——
区间 [0.85, 1.0] 内一律 W20 起步（8-10 帖、总量 39-43），
只有降到 0.4 档才量级持平（119 帖）但 W14-W17 就出现玩梗（2/5/9/14/17 帖），
与真实基准「W12-W18 梗份额 ≤1.5%」相悖；故不调。

**预注册预期（同构代理，`calibrate_speak.py --nog`，2026-09-12 实跑输出）**：

| 臂 | 玩梗轨迹 W12→W22 | W18-19 | W20-22 | 玩梗总 | 全类型总 |
|---|---|---|---|---|---|
| normal（θ 抖动） | 0/0/0/0/3/7/16/18/18/18/18 | 34 | 54 | 98 | 560 |
| no-G（θ=0） | 0/0/0/0/0/0/0/0/9/15/17 | **0** | 41 | **41** | 531 |

代理判读：**去掉 G 后玩梗在 W12-W19 完全哑火**（normal 臂同期已起 3/7/16/18），
起爆整体推迟到 W20（9 帖），全期玩梗总量只剩 41%（98→41）；
而全类型总供给几乎不变（560→531）——差异集中在玩梗型的**时序与量级**，
不在总供给，与"G 是 W18-19 温和起步的驱动"一致。

> **口径提示**：本节的代理数字记录于"G 退役前"（U = D·R·G^θ 时代），仅作历史对照；
> D 改有界 tanh、U 改为 D·R 之后，代理的玩梗轨迹为 W20 起量（W20-22 约 42 帖），
> 与 no-G 臂实测（38 帖）同量级。代理对起爆速度仍偏乐观，**形态以真实 run 为准**。

**跑法**（单 run，约 2.3h、约 507 次 LLM 调用）：

```bash
$PYTHON_PATH hypothesis_4/experiment_1/run_batch.py --only interest_nog_s0
# 或引擎 CLI 直启（run_dir 独立，不落固定 run/）：
#   $PYTHON_PATH -m agentsociety2.society.cli --config hypothesis_4/experiment_1/init/configs/interest_nog_s0.json \
#     --steps hypothesis_4/experiment_1/init/steps.yaml \
#     --run-dir hypothesis_4/experiment_1/runs/interest_nog_s0 \
#     --experiment-id h4e1_interest_nog_s0
```

**结果对比口径**：直接与已完成的烟测 run `runs/interest_normal_s0` 对读
（同群体、同样本、同 seed、同 feed 机制），差异面只有 θ；
判据 = 玩梗 **起爆时点**（W18-19 是否哑火）、W20-22 量级、combined 玩梗份额 vs 真实基准。

### 实测结果（2026-09-12，`runs/interest_nog_s0` 11/11 周完成）

combined 玩梗供给份额（`supply_share_all_meme`）对读真实基准
（`benchmark_curves.json` weekly_category_matrix，梗文化讨论/总条数）：

| 周 | 真实基准 | normal（θ 抖动） | no-G（θ=0） |
|---|---|---|---|
| W12 | 0.00% | 0.0% | 0.0% |
| W13 | 1.28% | 0.0% | 0.0% |
| W14 | 1.71% | 1.3% | 1.2% |
| W15 | 2.83% | 1.3% | 1.2% |
| W16 | 2.05% | 1.4% | 1.4% |
| W17 | 2.15% | 1.7% | 0.0% |
| W18 | 2.58% | 1.6% | 0.0% |
| **W19** | **7.76%** | **8.1%** | **1.7%** |
| W20 | 29.84% | 24.6% | 16.4% |
| W21 | 55.62% | 44.3% | 41.4% |
| W22 | 60.32% | 47.1% | 50.8% |

玩梗 agent 发言人数：normal `0/0/0/0/0/1/1/4/11/18/18`，no-G `0/0/0/0/0/0/0/0/4/16/18`。

**结论（G^θ 是点火器，不是放大器）**：

1. **起爆点由 G^θ 承载**——真实基准的 W19 跳变（2.58%→7.76%）在 normal 臂被精确复现
   （8.1%，且当周 4 个玩梗 agent 开口），在 no-G 臂**完全消失**（1.7%，0 人开口），
   起爆整体推迟到 W20 且当周欠冲（16.4% vs 基准 29.8%）。
   若不调门槛，去掉 G^θ 就丢掉本假说最关心的那一跳。
2. **尾部水平与 G^θ 无关**——两臂 W21/W22 都在 41-51%，共同低于基准 55-60%，
   且互有高低（W21 no-G 更低 41.4% vs 44.3%，W22 no-G 更高 50.8% vs 47.1%）。
   即：**尾部约 10 个百分点的缺口不是 G^θ 造成的**，归因得另找
   （候选：悼念期衰减、D 项对少数派的压制强度、feed 构成），不构成本次消融的结论。
3. **G^θ 同时加速「玩梗挤出悼念」**——no-G 臂悼念供给全期 70 vs normal 50（+40%），
   W14-W18 悼念发言人数 15/16/13/6/3 vs 8/12/8/3/2。
   去掉 G^θ 后悼念生态多维持 2-3 周，即表征转移（悼念→迷因）的**速度**对 G^θ 敏感，
   这与 H4「算法选择性放大既有玩梗群体、驱动表征转移」的机制叙事一致。
4. **总供给不变**——全期 agent 供给 no-G 500 vs normal 507，
   差异全部集中在玩梗/悼念的时序再分配，不在总量。

**预注册预期核对**：方向命中、量级高估。代理预测「no-G 在 W18-19 完全哑火、
起爆 W20」——实测 W18-19 = 0、W20 起爆（4 人），**方向与起爆时点完全命中**；
但代理高估两臂量级（玩梗总：代理 98/41 vs 实测 53/38；全类型总：560/531 vs 507/500），
代理对起爆速度仍偏乐观，**形态以真实 run 为准**（与上文代理口径提示一致）。

**对用户裁定的意义**：本探针**不支持**把 no-G 升为第 3 水平写入注册设计——
它损失了 W19 起爆且尾部无改善，作为消融臂的信息量已在本次单跑中获得；
若关心尾部缺口，应另开探针（候选：悼念衰减率、D 项 s 系数），而非扩因子。

**产物**：`runs/interest_nog_s0/`（+ `monitor/interest_nog_s0/`、`monitor/overview.md` 已刷新）。

## 噪声结构与分析口径（2026-09-12 立）

**单 run 的周间波动主要是抽样噪声，不是形态证据。** 每个 agent 每周从约 150 条活池里随机抽
10 槽，某类内容出现在 feed 里的条数 sd ≈ 1.4，再经硬门槛（U ≥ activity）放大成"发言人数"的跳变。
实测：**30 seed 平均后，单 run 里出现的 W16 峰、W18 鼓包完全消失**（总量均值 W13→W22 =
52.9/51.0/54.2/49.8/46.2/46.3/45.3/50.7/52.5/41.7，跨 seed sd ≈ 3 帖 ≈ 6%）。

因此：

- **臂间比较与形态判定以"各臂 3 seed 平均"为准**；单 run 曲线的锯齿不作为形态证据，
  也不作为调参依据（详见 SMOKE_DIAGNOSIS_w19_cliff.md §五之五）。
- **降噪手段已穷举实测，只有"把 n 做大"有效**（加 seeds / 加每类 agent 数，σ ∝ 1/√n）。
  已排除：决策改概率式（周间抖动 +20%）、放宽个体门槛抖动（总量掉 15–30%）、
  分层配额抽样（跨 seed 差异归零 + 抖动翻倍）、加大 feed_size（二波缩水 42→29）、
  气候改 EWMA（二波 42→20/13）—— 全部带数字留痕于 §五之五。
- 若后续需要更高精度，优先**增加 seeds**（9 → 18 runs 成本×2），而非改机制。

## 群体（全部 9 runs 共享）

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
- `configs/{algorithm}_s{seed}.json` — 9 个 init_config 变体
  （单因子 3 臂）
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
引擎 CLI 原生支持任意 `--run-dir`（`agentsociety2/society/cli.py`），故各 run
各自独立目录放在 `runs/<run_id>/`；`ags.py run-experiment status` 只看固定 `run/`，
各 run 的状态由监视器总览承担。

```bash
# 冒烟 1 run（标准入口，落固定 run/）
$PYTHON_PATH .agentsociety/bin/ags.py run-experiment start \
  --hypothesis-id 4 --experiment-id 1 \
  --init-config hypothesis_4/experiment_1/init/configs/interest_normal_s0.json

# 9 runs（引擎 CLI 直启，各自独立 run 目录；顺序或 ≤3 并发，控 LLM 速率）
for cfg in hypothesis_4/experiment_1/init/configs/{random,chronological,interest}_s{0,1,2}.json; do
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
再跑全部 9 runs。

## 判类与指标口径

- 帖子主类型 = 作者类型（by construction）；env 判类器（悼念>营销>教育>玩梗>噪音>其他，
  仅用 main + meme 四列表）产出 assigned_type / type_mismatch 诊断。
- 主基准：benchmark_curves.json 周度类型矩阵 vs 模拟供给/曝光份额。
