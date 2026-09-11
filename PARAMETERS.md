# 参数设定总表（H4E1：玩梗涌现环境实验）

本文档汇总 hypothesis_4 / experiment_1 的全部参数设定，按"谁在用、在哪定义"分层组织。
代码为唯一事实来源，本文与其对应代码块一一互引；修改代码后请同步更新本文。

---

## 0. 总纲：发言决策模型

每个 agent 每周（1 tick = 1 周 = 604800 秒）做一次**确定性数值决策**（无 LLM、无随机数）：

```
U = D × R × G^θ        发言当且仅当 U ≥ activity
```

| 因子 | 公式 | 语义 | 理论锚定 |
|---|---|---|---|
| D | `1 + s·(share_own − base)/base`，clamp [0.05, 2.0] | 沉默的螺旋：同类气候共振放大收益，少数派处境抑制收益 | Noelle-Neumann 1974；Granovetter 1978 |
| R | `exp(−λ·cum_own/50)` | 注意力衰减：重复同类曝光越多，边际表达收益越低 | Wu & Huberman 2007；Candia et al. 2019 |
| G^θ | `clamp(B^β·S^σ, 0.2, 3.0)^θ` | 玩梗涌现环境增益：仅玩梗型（θ>0）受环境影响 | Simon 1971；logistic 生态位；Dawkins 1976 |

中性状态（D≈R≈1、G=1）下 U≈1.0。三因子全部**乘法**进入效用（收益侧），杜绝线性等权平均的补偿性稀释。

- 代码：`custom/agents/curation_discourse_agent.py`（`_speak_stimulus`，第 228–278 行）
- 环境侧 G 的计算：`custom/envs/curation_dynamics_space.py`（第 526–560 行附近）

---

## 1. Agent 个体决策参数（每 agent 一次性抽定，整局不变）

### 1.1 参数类型规格 `_PARAM_SPECS`

个体值 = 类型均值 × U[0.8, 1.2] 均匀抖动，再截断到 [下限, 上限]。
定义：`custom/agents/curation_personas.py` 第 142–153 行。

| 类型 | activity（门槛） | spiral（螺旋 s） | decay（疲劳 λ） | emergence（θ） |
|---|---|---|---|---|
| meme（玩梗 18 人） | 0.95 [0.5, 1.5] | 1.2 [0.3, 2.5] | 0.8 [0.2, 2.0] | **1.0** [0.5, 1.5] |
| mourning（悼念 21 人） | 0.95 [0.5, 1.5] | 0.8 [0.2, 2.0] | 1.2 [0.4, 2.5] | 0 |
| marketing（营销 26 人） | 0.95 [0.5, 1.5] | 0.2 [0.0, 0.8] | 0.1 [0.0, 0.6] | 0 |
| education（教育 15 人） | 0.95 [0.5, 1.5] | 0.5 [0.1, 1.5] | 0.4 [0.1, 1.2] | 0 |
| other（其他 20 人） | 0.95 [0.5, 1.5] | 1.5 [0.5, 3.0] | 1.0 [0.3, 2.2] | 0 |

格式说明：`均值 [下限, 上限]`；抖动后实际取值区间 ≈ 均值×[0.8, 1.2] 与截断区间的交集。

设定依据（用户 2026-09-10 裁定）：

- **activity 类型均值统一为 0.95**：发帖人口径下各类型人均发帖强度实证
  meme 0.82 / mourning 0.89 / marketing 1.00 / education 1.02 / other 0.88（W12–W22 注入池 48,360 帖）≈ 1，
  无类型差异依据；类型行为分化由 spiral/decay/θ 三参数承载。
- **spiral**：沉默螺旋敏感度——路人最强（最看风向）、营销商业动机稳定最弱。
- **decay**：注意力疲劳——悼念情感疲劳最快、营销近乎无疲劳。
- **emergence θ**：结构性取值，仅玩梗型 >0（玩梗时机受涌现环境门控：洪峰期新表达被淹没、
  退潮期才被看见）；其余类型 θ=0，G^0 ≡ 1，环境不影响其决策。

### 1.2 个体参数抽样

- 抽样时机：`build_population(counts, seed=42)` 建人设时一次性抽定，写入 `profile.params`，
  运行期只读不重算（`step()` 内 `threshold = self._params["activity"]`）。
- 代码：`custom/agents/curation_personas.py` `_sample_params`（第 164–169 行）。
- 18 个实验配置**共享同一群体**（POPULATION_SEED=42），跨 cell/seed 个体参数完全可比。

### 1.3 门槛基数校准

- 基数 0.95 由 `hypothesis_4/experiment_1/calibrate_speak.py` 扫描定标：
  候选 `CANDIDATE_BASES = [1.0, 0.95, 0.9, 0.85, 0.8, 0.7]`（第 46 行），
  方法为真实周构成气候代理 + 真实 Stock/Flow 涌现环境代理（确定性、无随机数），
  个体门槛按基数等比例缩放、保留 U[0.8,1.2] 抖动结构。
- 选点标准：agent 供给 ≈300–350 帖/run（>250 注入），形态合理（W13 悼念冲击、
  玩梗 W20–22 回潮、营销/教育稳定供给）。本脚本零副作用，定标结果由人工裁定写入代码。

### 1.4 回退默认值 `_PARAM_DEFAULTS`

profile 未带 params 时的回退值，与 1.1 各类型均值一致
（`custom/agents/curation_discourse_agent.py` 第 56–60 行）：

| 类型 | activity | spiral | decay | emergence |
|---|---|---|---|---|
| meme | 0.95 | 1.2 | 0.8 | 1.0 |
| mourning | 0.95 | 0.8 | 1.2 | 0.0 |
| marketing | 0.95 | 0.2 | 0.1 | 0.0 |
| education | 0.95 | 0.5 | 0.4 | 0.0 |
| other | 0.95 | 1.5 | 1.0 | 0.0 |

---

## 2. 决策全局常量

定义：`custom/agents/curation_discourse_agent.py`（第 62–64 行）、`custom/agents/curation_personas.py`（POP_SHARE）。

| 常量 | 值 | 含义 |
|---|---|---|
| `POP_SHARE` | meme 0.18 / mourning 0.21 / marketing 0.26 / education 0.15 / other 0.20 | 沉默螺旋的"期望份额"基线 base，与 100 人群体构成一致（发帖人口径，用户 2026-09-10 裁定） |
| `_DECAY_SCALE` | 50.0 | 注意力衰减半饱和尺度：cum_own=50 时 R≈e^(−λ) |
| D clamp | [0.05, 2.0] | 螺旋因子的上下限 |
| G clamp | [0.2, 3.0] | 涌现环境增益的上下限（`emergence_gain_min` / `emergence_gain_max`） |

---

## 3. 环境侧：玩梗涌现环境参数（env 模块）

定义：`custom/envs/curation_dynamics_space.py`（init kwargs 默认值，第 296–316 行；周度计算第 526–560 行附近）。
实验配置不显式覆盖以下任何涌现参数（全部取默认）。

### 3.1 涌现环境（G 的输入）

| 参数 | 默认值 | 含义 |
|---|---|---|
| `emergence_window_stock` | 6 | 存量窗口：Stock_t = 过去 6 周（含本周）arena 供给总数（注入 + agent 帖；agent 帖滞后 1 tick 入池） |
| `emergence_ka`（K_a） | None → 自动 | 丰沛度半饱和常数；回退值 = 注入计划事件周窗口存量（W12+W13 = 17+35 = 52） |
| `emergence_kf`（K_f） | None → 自动 | 空旷度半饱和常数；回退值 = 空旷度流量口径的基线周值（现实调度 W12 帖数） |
| `emergence_beta`（β） | 1.0 | 丰沛度指数 |
| `emergence_sigma`（σ） | 1.0 | 空旷度指数 |
| `emergence_gain_min / max` | 0.2 / 3.0 | G 的截断区间 |

### 3.2 周度计算公式

```
B_t（存量丰沛度） = f(Stock_t) / f(Stock_base)，  f(x) = x / (x + K_a)
S_t（流量空旷度） = h(Flow_t) / h(Flow_base)，  h(x) = K_f / (K_f + x)
G_t = clamp(B_t^β · S_t^σ, 0.2, 3.0)
```

- **基线周 = 2026-W12**（start_week），B、S、G 均以基线周 = 1。
- **Stock（存量）内生**：arena 实际供给（注入 + agent 帖），窗口在基线周截断 → Stock_W12 = Flow_W12。
  B 不做任何冻结，保留"玩梗再拥挤反哺存量"的自限反馈。
- **Flow（流量）外生优先**：读 `emergence_flow_by_week`（现实口径周新增调度，见 §5.4），
  缺该周回退内生 arena 计数。理由：sim arena 流量被 250 条注入预算压缩（峰谷比 ~1.6× vs 现实 ~9×），
  表达不出真实洪峰/退潮节律。
- **sustained_hot 反事实臂**：W12/W13 正常计算，W13 记录事件周空旷度 S，之后**冻结 S**；
  B 保持内生演化。

---

## 4. 信息流与排序参数（env 模块）

定义：`custom/envs/curation_dynamics_space.py` init kwargs；实验传参见
`hypothesis_4/experiment_1/init/config_params.py` 第 286–312 行。

| 参数 | 实验取值 | 含义 |
|---|---|---|
| `recommendation_algorithm` | `random` / `chronological` / `interest`（全因子 3 水平） | 排序臂 |
| `feed_size` | 10 | 每 agent 每周信息流条数（用户 2026-09-10 裁定） |
| `sampling_ratio` | 1.0 | 注入样本全量进 env，不再二次抽样 |
| `meme_emergence_mode` | `normal` / `sustained_hot`（全因子 2 水平） | 涌现环境反事实臂 |
| `alpha` | 1.0 | interest 臂：倾向分匹配权重 |
| `gamma` | 0.5 | interest 臂：时新近度权重（score = alpha·倾向分 + gamma·时新近度 + 噪声） |
| `beta` | 1.0（**废弃**） | 2026-09-09 裁定：倾向分替代词表重合项，不再使用 |
| `interest_noise_eps` | 0.05 | interest 臂均匀噪声幅度 [-eps, +eps] |
| `recency_max_age_weeks` | 8 | 时新近度线性衰减的最大周龄 |
| `exposure_mode` | none | 曝光惩罚模式（none/penalize/exclude，实验关闭） |
| `exposure_penalty_weight` | 0.1 | 曝光惩罚权重（exposure_mode=none 时不生效） |
| `random_recency_window_weeks` | None | 随机时新窗口（实验未启用） |
| `official_pin_extend_weeks` | 0 | 官方置顶延伸周数：讣告帖仅事件周 W13 置顶，不延伸 |

---

## 5. 实验设计参数（config_params.py）

定义：`hypothesis_4/experiment_1/init/config_params.py`。

### 5.1 因子设计

- 3 排序算法 × 2 涌现模式 × 3 seeds = **18 个配置**，写入 `init/configs/`。
- 群体 100 人全 18 配置共享。

### 5.2 群体与随机种子

| 参数 | 值 | 含义 |
|---|---|---|
| `POPULATION_COUNTS` | meme 18 / mourning 21 / marketing 26 / education 15 / other 20 | 100 人的类型构成（发帖人口径） |
| `POPULATION_SEED` | 42 | 群体生成种子（全配置共享） |
| `VOCAB_SAMPLE_SEED` | 43 | 各类型词表抽样子种子（= POPULATION_SEED + 1） |
| `TYPE_VOCAB_N` | 40 | 每 agent 注入其类型词表的词数 |
| `SAMPLE_SEED_OFFSET` | 777 | 注入样本抽样种子 = seed + 777 |

### 5.3 时间轴

| 参数 | 值 | 含义 |
|---|---|---|
| `START_WEEK` | 2026-W12 | 基线周（start_t = 2026-03-16T00:00:00，W12 周一） |
| `EVENT_WEEK` | 2026-W13 | 事件周（讣告帖注入 + sustained_hot 冻结锚点） |
| `NUM_TICKS` | 11 | W12 → W22，1 tick = 1 周 = 604800 秒 |
| `FEED_SIZE` | 10 | 每周信息流条数 |

### 5.4 注入预算（250 条全程）

保底 15/周 × 11 = 165，余 85 按真实周量比例分配（和恰为 250）：

| 周 | W12 | W13 | W14 | W15 | W16 | W17 | W18 | W19 | W20 | W21 | W22 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 条数 | 17 | 35 | 30 | 24 | 22 | 19 | 18 | 18 | 20 | 23 | 24 |

- 抽样方法：每周池内**类型分层比例抽样**（最大余数法），样本类型构成确定性贴合当周真实分布，
  随机性只体现在"类型组内抽哪几条"。
- **官方媒体仅 W13 单条讣告帖**（`official_w13_announcement`，type=mourning，is_official=True，
  全员置顶可见）；其余真实数据帖一律按普通内容处理（is_official=False），官方置顶不延伸周。
- `EMERGENCE_FLOW_BY_WEEK` = 真实数据各周全量帖数（W12–W22），作为空旷度 S 的现实口径流量调度。

---

## 6. Agent 内容生成参数（LLM，仅写帖内容，不参与决策）

定义：`custom/agents/curation_discourse_agent.py` `_content_messages`（第 283–326 行）；
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
| `custom/agents/curation_personas.py` | `_PARAM_SPECS`（四参数类型规格）、`_sample_params`（抖动抽样）、`POP_SHARE`、人设文本 |
| `custom/agents/curation_discourse_agent.py` | `_PARAM_DEFAULTS`（回退值）、`_POP_SHARE`、`_DECAY_SCALE`、决策与内容生成逻辑 |
| `custom/envs/curation_dynamics_space.py` | 涌现环境（窗口/K_a/K_f/β/σ/clamp）、排序（alpha/gamma/noise/recency/exposure）、feed_size、置顶延伸 |
| `hypothesis_4/experiment_1/init/config_params.py` | 因子设计、群体种子、时间轴、注入分配、官方讣告帖、env 实验传参 |
| `hypothesis_4/experiment_1/calibrate_speak.py` | 门槛基数 0.95 的扫描定标方法与候选集 |
