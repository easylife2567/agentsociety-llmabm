# 参数设定总表（H4E1：算法策展三臂实验 · anchored_v1 轮）

本文档汇总 hypothesis_4 / experiment_1 的全部参数设定，按"谁在用、在哪定义"分层组织。
代码为唯一事实来源，本文与其对应代码块一一互引；修改代码后请同步更新本文。

> **当前轮次**：`anchored_v1`（2026-09-14）——锚定式表达效用 + 单因子 3 臂
> （random-global / chronological / interest）× 3 seeds = 9 runs。理论冻结文档见
> `锚定式事件表达激活模型.md`（构念、方程、理论锚点、命题与可证伪条件）；
> 本轮实验叙述见 `hypothesis_4/experiment_1/EXPERIMENT.md`。基线 run
> `anchored_v1_random_s0`（强去策展反事实）已完成 11/11 ticks（2026-09-14），
> 产物与运行状态见 §5.5。

---

## 0. 总纲：发言决策模型（锚定式表达效用，用户 2026-09-14 裁定）

每个 agent 每周（1 tick = 1 周 = 604800 秒）做一次**确定性数值决策**（无 LLM、无随机数；
随机性只存在于平台侧的 feed 选址，见 §4）：

```
U = B_i + R·(D − B_i)  ≡  (1−R)·B_i + R·D      发言当且仅当 U ≥ activity
```

理论文档称 U 为**事件表达激活势能**。两条行为机制（沉默螺旋 D、注意力衰减 R）不变，
组合公式由旧 `U = D·R` 改为锚定式；G^θ 维持退役。

| 因子 | 公式 | 语义 | 理论锚定 |
|---|---|---|---|
| B_i | 类型常数（标定值见 §1.3，运行期不变） | **常态表达锚点**：事件前（W05–W12）常态供给映射到 activity 分布的效用分位点。注意力衰减只消除事件冲击，`R→0 ⇒ U→B_i`，表达回归常态盘而非机械归零 | 本研究锚定结构（W05–W12 实证常态盘；理论文档命题 1） |
| D | `1 + (alpha_D·s)·tanh(1.5·(share_own − base)/base)`，**有界、无地板** | 沉默的螺旋：同类气候共振放大收益；少数派处境抑制收益；**D<0 即表达存在净成本（孤立成本）**。全局 alpha_D=0.4297 乘在个体敏感度 s 上而非 D 上，保持 D=1 的中性中心不移动 | Noelle-Neumann 1974；Blanco 2005（发言门槛 = c/(b+c)）；Sohn & Geidner 2015 / Cabrera et al. 2021（logistic 有界映射）；Granovetter 1978（阈值分布 ↔ activity 抖动） |
| R | `exp(−λ·cum_own/15)` | 注意力衰减：重复同类曝光越多，**事件冲击偏离（D−B_i）**被折减越多。半饱和尺度 **15**（≈一周半活跃曝光；2026-09-12 由 50 调至 20，2026-09-13 进一步下压至 15，"让退潮更猛烈"） | Wu & Huberman 2007；Candia et al. 2019 |

边界含义：`R=1 ⇒ U=D`（冲击期由当周意见气候决定）；`R→0 ⇒ U→B_i`（疲劳后回到常态
锚点）；`D=B_i ⇒ U=B_i`；中性气候且无疲劳（D=R=1）时 `U=1`，与门槛基数 0.95 的旧
锚定一致。

~~G^θ~~（原第三因子"玩梗涌现环境增益"）**2026-09-12 用户裁定退役**：G 与 θ 不再进入
任何决策；B/S/G 仅作观测序列写入 replay 与监控（依据与 no-G 探针证据见
`SMOKE_DIAGNOSIS_w19_cliff.md` §五之二/§五之三）。

> **D 的输入 `share_own` = 该 agent 本周 feed 中本类内容占比**（不是全局份额、也不是真实世界份额）。
> 2026-09-12 烟测诊断（`hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md`）：旧 feed 机制下
> 同类型 agent 拿到同一份 top-10，share_own 只能取 {0,1}，D 因此退化成 0.05↔2.0 的开关
> （W18→W19 发言率 0→100%）。修复放在推荐算法侧（§4），D 的公式未动。

- 代码：`custom/agents/curation_discourse_agent.py`（`_speak_stimulus`，第 261–310 行）
- 共享纯函数（agent / env / 校准脚本三处同源 import）：`custom/envs/curation_mechanisms.py`
  —— `spiral_factor`（第 237–251 行）、`fatigue_factor`（第 272–283 行）、
  `anchored_utility`（第 286–303 行）
- 环境侧 G 的计算（仅观测）：`custom/envs/curation_dynamics_space.py`（`_compute_meme_env`）

---

## 1. Agent 个体决策参数（每 agent 一次性抽定，整局不变）

### 1.1 参数类型规格 `_PARAM_SPECS`

个体值 = 类型均值 × U[0.8, 1.2] 均匀抖动，再截断到 [下限, 上限]。
定义：`custom/agents/curation_personas.py` 第 138–154 行。格式：`均值 [下限, 上限]`。

| 类型 | activity（门槛） | spiral（螺旋 s 原始值） | decay（λ 抽样规格） |
|---|---|---|---|
| meme（玩梗 19 人） | 0.95 [0.5, 1.5] | 1.2 [0.3, 2.5] | 0.8 [0.2, 2.0] |
| mourning（悼念 22 人） | 0.95 [0.5, 1.5] | 0.8 [0.2, 2.0] | 1.2 [0.4, 2.5] |
| marketing（营销 23 人） | 0.95 [0.5, 1.5] | 0.2 [0.0, 0.8] | 0.05 [0.0, 0.2] |
| education（教育 15 人） | 0.95 [0.5, 1.5] | 0.5 [0.1, 1.5] | 0.4 [0.1, 1.2] |
| other（其他 21 人） | 0.95 [0.5, 1.5] | 1.5 [0.5, 3.0] | 1.0 [0.3, 2.2] |

> 群体构成为 2026-09-13 用户更正：**营销 23 / 悼念 22 / 其他 21 / 玩梗 19 / 教育 15**
> （发帖人口径；旧 26/21/20/18/15 随口径更正废弃）。

**decay 列只是抽样规格，不是实际生效均值**：个体 λ 按上表抽定后，`build_population`
把每类 λ **类型内同比缩放**到 §1.3 的标定均值 `CALIBRATED_LAMBDA_MEAN`（保留个体相对
异质性、不重新抽样）。缩放故意的放在抽样之后而非直接改规格均值——避免旧上下界截断
marketing/education/other（如营销标定均值 1.019 远超旧上限 0.2）。
代码：`curation_personas.py` 第 251–261 行。

**~~emergence（θ）~~ 已退役**（2026-09-12）：`_RETIRED_PARAM_DRAWS=1`（第 187 行）
保序消耗一次抽样，使 100 人群体的 activity/spiral/decay 抽样序列与历史 run 逐值一致；
`baseline_utility` 与 `spiral_scale` 是本轮预注册常数，**不消耗随机数**
（`_sample_params`，第 190–200 行）。

设定依据（用户 2026-09-10 裁定，沿用）：

- **activity 类型均值统一为 0.95**：发帖人口径下各类型人均发帖强度实证
  meme 0.82 / mourning 0.89 / marketing 1.00 / education 1.02 / other 0.88（W12–W22
  注入池 48,360 帖）≈ 1，无类型差异依据；类型行为分化由 spiral/decay 承载。
- **spiral**：沉默螺旋敏感度——路人最强（最看风向）、营销商业动机稳定最弱；正式计算时
  统一乘全局 alpha_D（§1.3）。
- **decay 语义随公式改变**：锚定式下 R 只折减事件冲击偏离（D−B_i）而非全部效用，λ 的
  量纲含义与旧乘法公式不可直接比较，故五类 λ 由 W13–W18 统一重新标定（营销 0.05→1.019
  不再与"几乎不疲劳"的旧裁定冲突——它现在是"事件偏离的中等衰减速度"）。

### 1.2 个体参数抽样

- 抽样时机：`build_population(counts, seed=42)` 建人设时一次性抽定，写入 `profile.params`，
  运行期只读不重算（`step()` 内 `threshold = self._params["activity"]`）。
- params 现含 5 键：`activity / spiral / spiral_scale / decay / baseline_utility`
  （agent 侧 restore 仅认这 5 键，旧 profile 的 emergence 直接忽略）。
- 代码：`custom/agents/curation_personas.py` `_sample_params`（第 190–200 行）、
  λ 同比缩放（第 251–261 行）。
- 9 个实验配置**共享同一群体**（POPULATION_SEED=42），跨 cell/seed 个体参数完全可比。

### 1.3 锚定式效用标定（`predict_anchored_utility.py`，2026-09-14）

标定协议（数据划分用户裁定，写入配置 manifest 的 `anchored_calibration`）：

- **B_i 固定，不参与拟合**：真实 W05–W12 周均供给按 agent 当量换算（W13 真实悼念
  4714 帖 → 22 名悼念 agent 各发 1 帖，乘数 0.004667）得各类型事件前周均发言人数
  （营销 2.63 / 教育 0.29 / 其他 0.07 / 玩梗 0.009 / 悼念 0.0006），再映射到该类型
  activity 分布的效用分位点：周均 <0.5 人的类型取该类最低门槛 −0.02（潜伏态，
  B_i 低于最低门槛 → 事件前几乎无人发言），营销取第 2.6 分位处相邻两门槛均值。
- **alpha_D 与五类 λ 只用 W13–W18 拟合，W19–W22 留出验证**（效标 = 分型发言率对真实
  周曲线的 RMSE）。
- 搜索：Sobol 粗搜 1024 点（1 seed）→ 前 32 名 8-seed 复核 → 截断高斯局部搜索 768 点
  （2 seed）→ 24 名决赛 20-seed → 最终预测 100 seed。目标 = 分型发言率 RMSE（W13–W18）
  + 0.004·log λ 正则（仅打破等拟合解，数据误差主导）。
- 搜索域：alpha_D ∈ [0.08, 1.0]；λ 各类对数均匀（meme 0.05–2.5 / mourning 0.15–5.0 /
  marketing 0.015–5.0 / education 0.05–5.0 / other 0.10–6.0）。

标定结果（`data/anchored_utility_prediction.json`；**数值代理预测，非正式仿真**）：

| 类型 | B_i（常态锚点） | λ 标定均值 | （参考）缩放前旧均值 |
|---|---|---|---|
| meme | 0.7755 | 1.243038 | 0.819 |
| mourning | 0.7678 | 2.282035 | 1.186 |
| marketing | 0.82515 | 1.019241 | 0.051 |
| education | 0.7412 | 2.493614 | 0.412 |
| other | 0.7686 | 4.429458 | 0.977 |

全局 **alpha_D = 0.4296954756**（乘在每个 agent 的 s 上，写入 `spiral_scale`）。

拟合质量（100-seed 代理）：分型发言率 RMSE 拟合期（W13–W18）**0.093** / 留出期
（W19–W22）**0.128**，旧乘法 U=D·R 对照为 0.314 / 0.255——锚定式两期均更优；
总量形态 RMSE 0.087 / 0.091。已知局限：真实基准是帖量而非活跃作者数（当量换算是
显式代理假设）；代理复用 feed 机制与注入样本 s0。

> **门槛基数 0.95 的历史来源**：`calibrate_speak.py` 扫描定标
> （`CANDIDATE_BASES = [1.0, 0.95, 0.9, 0.85, 0.8, 0.7]`，`BASE_REF = 0.95` 为缩放锚点；
> 选点标准：agent 供给 ≈300–350 帖/run、W13 悼念冲击与玩梗 W20–22 回潮形态合理）。
> 该脚本现为同构数值代理底座：`simulate()` 已支持 `utility_mode="anchored"|"multiplicative"`、
> `baseline_utility` 锚点与 `spiral_mult` 覆盖，并保留 `--assert-replay` 涌现环境公式断言。
> random-global 臂的代理预测另见 `predict_random_global.py`
> （冻结锚定参数 + 全历史均匀抽样；产物 `data/random_global_proxy_prediction.{json,csv}`）。

### 1.4 回退默认值 `_PARAM_DEFAULTS`

profile 未带 params 时的回退值（`custom/agents/curation_discourse_agent.py` 第 79–92 行；
正式配置经 profile 显式下发全部 5 键，回退值与之一致）：

| 类型 | activity | spiral | spiral_scale（=alpha_D） | decay（=λ 标定均值） | baseline_utility（=B_i） |
|---|---|---|---|---|---|
| meme | 0.95 | 1.2 | 0.4297 | 1.243038 | 0.7755 |
| mourning | 0.95 | 0.8 | 0.4297 | 2.282035 | 0.7678 |
| marketing | 0.95 | 0.2 | 0.4297 | 1.019241 | 0.82515 |
| education | 0.95 | 0.5 | 0.4297 | 2.493614 | 0.7412 |
| other | 0.95 | 1.5 | 0.4297 | 4.429458 | 0.7686 |

---

## 2. 决策全局常量

定义：`custom/envs/curation_mechanisms.py`（`DEFAULT_SPIRAL_K` 第 234 行、
`DEFAULT_DECAY_SCALE` 第 269 行）、`custom/agents/curation_personas.py`
（`CALIBRATED_ALPHA_D` 第 159 行、`POP_SHARE` 第 175–180 行）。

| 常量 | 值 | 含义 |
|---|---|---|
| `DEFAULT_SPIRAL_K` | 1.5 | D 的 tanh 过渡陡度 |
| `CALIBRATED_ALPHA_D` | 0.4296954756 | 沉默螺旋全局强度（乘在 s 上，D 的中性中心保持 1；标定见 §1.3） |
| `POP_SHARE` | meme 0.19 / mourning 0.22 / marketing 0.23 / education 0.15 / other 0.21 | 沉默螺旋的"期望份额"基线 base，与 100 人群体构成一致（发帖人口径，2026-09-13 更正后构成） |
| `DEFAULT_DECAY_SCALE` | **15.0** | 注意力衰减半饱和尺度（共享常量，`curation_mechanisms.py::fatigue_factor`）：cum_own=15 时 R≈e^(−λ)。沿革：50 → 20（2026-09-12，"让退潮显现"：真实总量深 V 而模拟近平，RMSE 0.132→0.043）→ **15**（2026-09-13，λ 等效 ×3.33；代理实测玩梗 W22 0.608 vs 真实 0.603） |
| 门槛形式 | 硬阈值 `U ≥ activity` | 概率式被实测否决（周间抖动 +20%、W19 前自发帖，见 SMOKE_DIAGNOSIS §五之五）；个体门槛 ∈ [0.76, 1.14] |
| ~~D clamp~~ | ~~[0.05, 2.0]~~ | 2026-09-12 退役：D 改有界 tanh（`spiral_factor`），无地板 |
| ~~G clamp~~ | [0.2, 3.0] | **退役（2026-09-12）**：涌现环境增益的上下限；现仅约束观测序列，不进入决策 |

---

## 3. 环境侧：玩梗涌现环境参数（env 模块）——**仅作观测序列，不进入任何类型的决策**

定义：`custom/envs/curation_dynamics_space.py`（init kwargs 默认值，第 346–356 行；周度计算 `_compute_meme_env`）。
实验配置不显式覆盖以下任何涌现参数（全部取默认）。

### 3.1 涌现环境（G 的输入）

| 参数 | 默认值 | 含义 |
|---|---|---|
| `emergence_window_stock` | 6 | 存量窗口：Stock_t = 过去 6 周（含本周）arena 供给总数（注入 + agent 帖；agent 帖滞后 1 tick 入池） |
| `emergence_ka`（K_a） | None → 自动 | 丰沛度半饱和常数；回退值 = 注入计划事件周窗口存量（W12+W13 = 17+35 = 52） |
| `emergence_kf`（K_f） | None → 自动 | 空旷度半饱和常数；回退值 = 调度基线周值 **1246**（现实口径 W12 帖数） |
| `emergence_beta`（β） | 1.0 | 丰沛度指数 |
| `emergence_sigma`（σ） | 1.0 | 空旷度指数 |
| `emergence_gain_min / max` | 0.2 / 3.0 | G 的截断区间（仅约束观测序列） |

> 注：Stock 用**逐周供给计数**（注入 + agent 帖），与 §4 的帖子生命周期/候选池无关 ——
> 帖子退场只影响"谁能被推荐"，不影响 B。/ K_a/K_f/β/σ 本轮未动（用户裁定）。

### 3.2 周度计算公式

```
B_t（存量丰沛度） = f(Stock_t) / f(Stock_base)，  f(x) = x / (x + K_a)
S_t（流量空旷度） = h(Flow_t) / h(Flow_base)，  h(x) = K_f / (K_f + x)
G_t = clamp(B_t^β · S_t^σ, 0.2, 3.0)
```

- **基线周 = 2026-W12**（start_week），B、S、G 均以基线周 = 1。
- **Stock（存量）内生**：arena 实际供给（注入 + agent 帖），窗口在基线周截断 → Stock_W12 = Flow_W12。
  B 不做任何冻结，保留"玩梗再拥挤反哺存量"的自限反馈。
- **Flow（流量）外生优先**：读 `emergence_flow_by_week`（现实口径周新增调度 = 真实数据各周
  全量帖数，W12 1246 → W13 11394 → W18 1703 → W22 5338，见 §5.4），缺该周回退内生 arena 计数。
  理由：sim arena 流量被 250 条注入预算压缩（峰谷比 ~1.6× vs 现实 ~9×），
  表达不出真实洪峰/退潮节律。
- ~~**sustained_hot 反事实臂**~~：**2026-09-12 退役**（θ≡0 时冻结 S 不产生任何行为差异）；
  配置统一 `normal`。

---

## 4. 信息流与排序参数（env 模块）

定义：`custom/envs/curation_dynamics_space.py` init kwargs（第 307–345 行）；实验传参见
`hypothesis_4/experiment_1/init/config_params.py`（`LIFE_*` / `INTEREST_SAMPLE_TEMP` /
`EVENT_WEEK_MOURNING_FLOOR` 常量）。

**feed 装配两条路径（2026-09-14 random 修订后，`_assemble_feed` 第 745–787 行）**：

- **random（random-global 强反事实）**：候选池 = 截至当周已进入 Env 的**全部历史帖子**，
  全 10 槽**均匀无放回抽样**；不读取帖子年龄、生命力、累计曝光、内容类型，**不应用
  官方置顶与 W13 哀悼保底**。未来帖尚未入 Env，不会时间穿越（第 756–761 行）。
  该对比识别的是**整体策展制度效应**，不是同候选池下的纯排序效应。
- **chronological / interest**：先应用官方置顶 + 事件周保底（§4.2），再从**未退场活帖池**
  按各自逻辑填充剩余槽位（chronological 按周序新→旧取最新；interest 按兴趣分比例抽样）。
  生命周期/退场参数**只约束这两臂**，random 分支明确忽略。

| 参数 | 实验取值 | 含义 |
|---|---|---|
| `recommendation_algorithm` | `random` / `chronological` / `interest`（**单因子 3 臂**） | 排序臂；配置键仍写 `random`，操作语义为 random-global 强反事实（2026-09-14 用户裁定） |
| `feed_size` | 10 | 每 agent 每周信息流条数（用户 2026-09-10 裁定） |
| `sampling_ratio` | 1.0 | 注入样本全量进 env，不再二次抽样 |
| `meme_emergence_mode` | `normal`（固定；`sustained_hot` 已退役） | 涌现环境反事实臂（2026-09-12 起无行为差异） |
| `alpha` | 1.0 | interest 臂：倾向分匹配权重 |
| `gamma` | 0.5 | interest 臂：新鲜度基准项（`score = (α·倾向分 + γ)·生命力`） |
| `beta` | 1.0（**废弃**） | 2026-09-09 裁定：倾向分替代词表重合项，不再使用 |
| `interest_noise_eps` | 0.05 | interest 臂均匀噪声幅度 [-eps, +eps]（相对分数跨度可忽略，保留兼容） |
| `recency_max_age_weeks` | 8（**退役**） | 旧加性时新项已于 2026-09-12 退役，kwarg 仅保留兼容 |
| `exposure_mode` | none | 曝光惩罚模式（none/penalize/exclude，实验关闭） |
| `exposure_penalty_weight` | 0.1 | 曝光惩罚权重（exposure_mode=none 时不生效） |
| `random_recency_window_weeks` | None | 随机时新窗口（已由生命周期/退场取代，实验未启用） |

RNG 独立流（第 385–388 行）：注入=`Random(seed)`、随机臂选址=`seed+1000`、兴趣噪声
=`seed+2000`、兴趣抽样=`seed+3000`。同 seed 跨 cell 抽出同一序列 → 臂间可比性不变；
三臂不再要求同周 feed_live_pool 或置顶槽位数相等（replay 列 `feed_live_pool`：random=
全历史帖数，chrono/interest=未退场活帖数，供验收分别核对）。

### 4.1 帖子生命周期（用户 2026-09-12 裁定；**仅 chronological / interest，random 明确忽略**）

| 参数 | 实验取值 | 含义 |
|---|---|---|
| `life_half_life_weeks` | 1.5 | 时间冷却半衰期（周）：1.5 周龄生命力折半 |
| `life_saturation_scale` | 20.0 | 曝光饱和尺度：累计曝光达该值生命力折半（"被推给约 20 人后就腻了"） |
| `life_retire_floor` | 0.35 | 退场线：时间生命低于此值退出候选池（≈**3 周流通窗口**：只在 age 0/1/2 可见） |

每帖状态 `life`（创建 1.0，每周 × `0.5**(1/half_life)`）；打分用
`生命力 = life × 0.5**(累计曝光 / saturation_scale)`；`life < retire_floor` 的帖退出候选池。
**退场只按时间生命判、不按曝光饱和判**（避免高热帖被提前踢出池子使后期池塌缩）。
预飞实测（100 agents × 11 周）：退场线 0.05（6.5 周窗口）→ age≥3 槽位占 60%；
0.35（3 周窗口）→ age≥3 = 0.00、top-10% 曝光集中度 0.24、零曝光帖 0.06
（旧机制分别为 0.60 / 0.64 / 0.54）。

### 4.2 议程设置：官方置顶 + 事件周哀悼保底（**仅 chronological / interest；random 不执行**）

| 参数 | 实验取值 | 含义 |
|---|---|---|
| `official_pin_extend_weeks` | 0（env 默认 1，实验显式置 0） | 官方讣告帖仅事件周 W13 置顶，不延伸 |
| `event_week_mourning_floor` | **5** | 事件周（W13）每条 feed 在置顶之后固定占 5 个槽位放"全池哀悼倾向分最高的 5 条"（未退场、非置顶、**非 noise**），全员相同；非事件周保底集合为空 |

- 保底帖计入曝光记账与气候统计；余下槽位照常按算法从剩余候选池选取。
- **候选池口径（2026-09-13 用户裁定·方案 B）**：按哀悼**倾向分**排序而非"mourning 类型帖"；
  剔除 `noise` 语料噪声（倾向分 = 命中数/(字数/50) 对短文本密度虚高，实测曾有 35–98 字
  乱码帖挤进全员强制位）。资格判定为共享纯函数 `curation_mechanisms.floor_eligible`
  （第 192–201 行，env 与校准同源）。该过滤是**口径清理而非标定杠杆**（开关对照
  |Δ| ≤ 0.01 且符号不定，小于 seed 间噪声）。
- ⚠ **保底条数 N=5 为当前配置、取值待用户裁定**：30-seed 代理扫描（真实 W13 悼念份额
  0.414）—— N=0→0.310（Δ−0.104 ❌）/ N=2→0.431（+0.018 ✅）/ N=3→0.462 / N=4→0.455 /
  **N=5→0.515（+0.101 ❌）** / N=6→0.581 ❌。N≥2 时 W13 悼念帖数恒为 22（悼念型全员
  发言），份额差异几乎全部来自分母（保底越多，非悼念类型 share_own 被压得越低、D<1
  抑制越强）。扫描表见 `EXPERIMENT.md`「保底条数 N 待裁定」节。
- 代码：`_compute_pinned_ids`（第 614 行起）、`_compute_event_floor_ids`（第 625–645 行）、
  random 臂置顶/保底旁路（第 840–848 行）。replay 列 `event_floor_slots` 记录保底条数
  （random=0）；`official_posts_count` 语义为**置顶集合中的官方帖数**（random 不置顶
  → 恒 0，讣告帖本身仍作为普通帖注入并参与均匀抽样）。

### 4.3 兴趣比例抽样（interest 臂的选择实现）

| 参数 | 实验取值 | 含义 |
|---|---|---|
| `interest_sample_temp` | 4.0 | 抽样温度：按 `exp(score/temp)` 无放回抽 feed_size 条；`<=0` 退化为确定性 top-k（消融档） |

---

## 5. 实验设计参数（config_params.py）

定义：`hypothesis_4/experiment_1/init/config_params.py`。

### 5.1 因子设计与轮次

- **单因子 3 排序算法 × 3 seeds = 9 个配置**（2026-09-12 用户裁定由 3×2 全因子降为
  单因子），写入 `init/configs/`。`ROUND_TAG = "anchored_v1"`（第 69 行），run_id =
  `anchored_v1_{algorithm}_s{seed}`，与旧公式（U=D·R）轮的 run/配置隔离。
- 群体 100 人全 9 配置共享。默认 `init_config.json` = `anchored_v1_interest_s0`。
- ~~no-G 反事实探针~~：已作废升格——G 退役后探针即正式模型；历史配置移入
  `configs_retired_2factor/`，证据留痕见 `SMOKE_DIAGNOSIS_w19_cliff.md` §五之三。

### 5.2 群体与随机种子

| 参数 | 值 | 含义 |
|---|---|---|
| `POPULATION_COUNTS` | meme 19 / mourning 22 / marketing 23 / education 15 / other 21 | 100 人的类型构成（发帖人口径，2026-09-13 更正） |
| `POPULATION_SEED` | 42 | 群体生成种子（全配置共享） |
| `VOCAB_SAMPLE_SEED` | 43 | 各类型词表抽样子种子（= POPULATION_SEED + 1） |
| `TYPE_VOCAB_N` | 40 | 每 agent 注入其类型词表的词数 |
| `SAMPLE_SEED_OFFSET` | 777 | 注入样本抽样种子 = seed + 777 |

### 5.3 时间轴

| 参数 | 值 | 含义 |
|---|---|---|
| `START_WEEK` | 2026-W12 | 基线周（start_t = 2026-03-16T00:00:00，W12 周一） |
| `EVENT_WEEK` | 2026-W13 | 事件周（讣告帖注入 + chrono/interest 哀悼保底） |
| `NUM_TICKS` | 11 | W12 → W22，1 tick = 1 周 = 604800 秒 |
| `FEED_SIZE` | 10 | 每周信息流条数 |

### 5.4 注入预算（250 条全程）

保底 15/周 × 11 = 165，余 85 按真实周量比例分配（和恰为 250）：

| 周 | W12 | W13 | W14 | W15 | W16 | W17 | W18 | W19 | W20 | W21 | W22 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 条数 | 17 | 35 | 30 | 24 | 22 | 19 | 18 | 18 | 20 | 23 | 24 |

- 抽样方法：每周池内**类型分层比例抽样**（最大余数法），样本类型构成确定性贴合当周真实分布，
  随机性只体现在"类型组内抽哪几条"（注入按帖子内容类型口径分层，与群体的发帖人口径
  相互独立、互不混用，用户 2026-09-10 确认）。
- **官方媒体仅 W13 单条讣告帖**（`official_w13_announcement`，type=mourning，is_official=True；
  W13 配额 = 34 条普通抽样 + 1 条讣告 = 35）。chrono/interest 全员置顶且不延伸；random
  不置顶，讣告帖与其他历史帖等概率参与均匀抽样。其余真实数据帖一律 is_official=False。
- `EMERGENCE_FLOW_BY_WEEK` = 真实数据各周全量帖数（W12–W22：1246/11394/8678/5050/
  3756/2416/1703/1792/2735/4252/5338），作为空旷度 S 的现实口径流量调度。

### 5.5 本轮运行状态（2026-09-14）

| run | 状态 | 备注 |
|---|---|---|
| `anchored_v1_random_s0` | **completed**（11/11 ticks，W22，2026-09-14） | 基线 run（random_global 强去策展反事实）。周度数据 `data/anchored_v1_random_s0/`（weekly_supply / behavior / exposure / mechanism / bias / benchmark 六表），正式图 `charts/formal/anchored_v1_random_s0__chart1–4`（玩梗份额 sim vs real、周供给量、供给堆叠面积、玩梗发言率）；W22 玩梗供给份额 0.552（真实 0.603） |
| `anchored_v1_interest_s0/s1/s2` | failed（3/11，W15 中断） | 待诊断后重跑（run 目录 `runs/anchored_v1_interest_s*`） |
| `anchored_v1_chronological_*` | 未开跑 | — |
| （上一轮 U=D·R）`random/chronological/interest_s0–2` | completed | 历史对照，不属于本轮 9-run 批次 |

---

## 6. Agent 内容生成参数（LLM，仅写帖内容，不参与决策）

定义：`custom/agents/curation_discourse_agent.py` `_content_messages`（第 315 行起）；
config 未显式覆盖，取代码默认值。

| 参数 | 默认值 | 含义 |
|---|---|---|
| `max_content_chars` | 300 | 帖子正文最大字数 |
| `feed_context_n` | 5 | 写帖 prompt 里携带本周 feed 前 5 条（摘录 120 字/条）作为发言对象 |
| `type_vocab` 使用 | 1–3 词/帖 | 从类型词表自然选词融入正文 |

数值决策的 `components` 只用于决策与日志记录，供事后分析；唯一进入写帖 prompt 的
决策数值是 `share_own`（告知模型"你 feed 里同类内容占比约 x%"）。

---

## 7. 参数来源文件索引

| 文件 | 参数内容 |
|---|---|
| `custom/agents/curation_personas.py` | `_PARAM_SPECS`（三参数抽样规格）、`_RETIRED_PARAM_DRAWS`（保序消耗）、`CALIBRATED_ALPHA_D` / `BASELINE_UTILITY` / `CALIBRATED_LAMBDA_MEAN`（标定常数）、λ 类型内同比缩放、`POP_SHARE`、人设文本 |
| `custom/agents/curation_discourse_agent.py` | `_CALIBRATED_ALPHA_D`、`_PARAM_DEFAULTS`（5 键回退值）、`_POP_SHARE`、锚定式决策（`_speak_stimulus`）与内容生成逻辑（公式均调用 `curation_mechanisms` 的共享纯函数） |
| `custom/envs/curation_mechanisms.py` | **feed 机制与决策共享纯函数**（周序数、文本归一化/词表命中/倾向分、生命周期与曝光饱和、`floor_eligible` 保底资格、兴趣打分、`spiral_factor` / `fatigue_factor` / `anchored_utility`、softmax 权重与加权无放回抽样）——agent / env / 校准脚本三处同源 |
| `custom/envs/curation_dynamics_space.py` | 涌现环境（观测序列：窗口/K_a/K_f/β/σ/clamp）、feed 机制（random-global 全历史均匀抽样 / 生命周期 / 退场 / 保底 / 置顶）、排序（alpha/gamma/noise/exposure）、feed_size |
| `hypothesis_4/experiment_1/init/config_params.py` | 因子设计（anchored_v1 单因子 9 配置）、群体种子、时间轴、注入分配、官方讣告帖、env 实验传参、manifest（含 `anchored_calibration` 标定备案） |
| `hypothesis_4/experiment_1/predict_anchored_utility.py` | 锚定式效用标定与代理预测（B_i/alpha_D/λ；W13–W18 拟合、W19–W22 留出）；产物 `data/anchored_utility_prediction.{json,csv}`、`charts/prediction/PROXY_anchored_utility_prediction.png` |
| `hypothesis_4/experiment_1/predict_random_global.py` | random-global 臂代理预测（冻结锚定参数 + 全历史均匀抽样，无生命周期/置顶/保底）；产物 `data/random_global_proxy_prediction.{json,csv}` |
| `hypothesis_4/experiment_1/calibrate_speak.py` | 同构数值代理底座（`simulate` 支持 anchored/multiplicative）、门槛基数 0.95 扫描史、`--assert-replay` 涌现环境公式断言 |
| `锚定式事件表达激活模型.md` | 理论冻结讨论稿（2026-09-14）：构念（事件表达激活势能）、核心方程、理论锚点（Noelle-Neumann/Blanco/Sohn & Geidner/Cabrera/Granovetter）、命题 1–6、可证伪条件 |
| `hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md` | 2026-09-12 烟测诊断（W19 悬崖与老帖霸屏的因果链、G 退役、D 改 tanh、R 尺度沿革、被实测排除的改法、用户裁定） |
