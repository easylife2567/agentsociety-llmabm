# charts/ 图表溯源与释义

**这份文件回答两个问题**：`results/charts/` 里的每一张图，是**哪个（些）run** 生成的？每张图**在说什么**？

- 包级总览（设计、验收、主判据读数、局限）见 [`README.md`](README.md)。
- 出图分桶约定（formal / prediction / smoke）见 [`../charts/README.md`](../charts/README.md)。
- 本文件只管一件事：**图 → 来源 run → 含义** 的对应关系。

**图表总数：51 张**（2026-09-13 现况）。分三类作者：

| 类 | 张数 | 由谁生成 | 对应 run |
|---|---|---|---|
| 逐 run 图 `<run>__chart*` | 45 | `plot_run_charts.py` | **单个 run**（9 个 run 各 5 张） |
| 臂级图 `ARM_A1..A4` | 4 | `plot_arm_charts.py` | **全部 9 个 run 聚合**（不是某一个 run） |
| 真实基准图 `real_baseline__chart3*` | 2 | `plot_real_baseline_chart.py` | **不来自任何 run**（外部真实数据） |

> ⚠️ [`README.md`](README.md) 第 3 节写的「charts/ 49 张」「tables/ 57 个 CSV」是 2026-09-13 15:31 的计数，
> 早于当晚 20:33 加入的 2 张真实基准图与其 CSV。**以本文件为准**：51 张图 / 58 个 CSV。

---

## 1. 命名规则

```
<run>__chart<N>_<描述>.png     逐 run 图     例：interest_s0__chart1_meme_share_sim_vs_real.png
ARM_A<N>_<描述>.png            臂级图        例：ARM_A1_meme_share_arms_vs_real.png
real_baseline__chart3_*.png    真实基准图    例：real_baseline__chart3_supply_stacked_area.png
```

`<run>` = `<推荐算法>_s<seed>`，取值恰为 9 个：

- 算法臂：`random`（随机推荐）/ `chronological`（时序推荐）/ `interest`（兴趣推荐）
- seed：`s0` / `s1` / `s2`

**seed 的含义（判读时重要）**：`s0/s1/s2` 同时改引擎 `random_seed` **和**注入帖样本
（`injection_sample_s{0,1,2}.json`）。所以逐 run 图之间的差异**包含注入池重采样方差**，
不只是蒙特卡洛噪声。

> **每个 run 的物理位置**：引擎输出 `runs/<run>/`；图表脚本真正的输入是 `monitor/<run>/status.json`
> （由 `monitor.py` 汇总 replay 表与 ENV_STATE.json 生成）；冻结快照在 `snapshots/<run>/status.{json,md}`。

---

## 2. 逐 run 图（45 张 = 9 run × 5 图型）

**生成命令**（对 9 个 run 各跑一次）：

```bash
$PYTHON_PATH plot_run_charts.py --status monitor/<run>/status.json --run-id <run>
```

**数据落盘**：同一脚本顺带把周度指标导出为 6 个 CSV → `results/tables/<run>/weekly_*.csv`
（`supply` / `exposure` / `agent_behavior` / `mechanism` / `benchmark` / `bias`）。
图上一个点、表里一行，可逐值回查。

**所有逐 run 图的公共元素**：x 轴 11 周（2026-W12 → W22，1 tick = 1 周）；红色虚线 = 去世周
**W13**（2026-03-24）；款式对齐工作区根目录《图表解读.docx》的真实数据分析图
（结论式标题、事件红线、末端终值标注、% 刻度），目的是让模拟图能与真实数据图**同等解读、并排比读**。

### chart1 — 玩梗份额：模拟 vs 真实 `chart1_meme_share_sim_vs_real.png`

| 项 | 内容 |
|---|---|
| 画的是什么 | 蓝方块实线 = 真实基准（抖音）；橙圆点实线 = 本 run 模拟。两端各标 W22 终值 % |
| 字段 | `supply_share_all_meme`（模拟）vs `benchmark.meme.bench_share`（真实，来自 `hypothesis_4/benchmark_curves.json`） |
| 口径 | **combined 供给份额** = 玩梗帖（注入+agent）÷ 全部帖（**分母含噪音**），与真实基准同分母 |
| 含义 | 本 run 是否复现真实基准的「事件压抑 → **W20 起爆**」二波形态。这是全实验的核心现象图 |
| 回查表 | `tables/<run>/weekly_benchmark.csv`（含 `sim_share_all` / `bench_share` / `delta` 三列） |

**别误读**：单 run 曲线的周间锯齿主要是抽样噪声，**不作形态证据**（`EXPERIMENT.md` §噪声结构与分析口径，
用户 2026-09-12 裁定：臂间比较与形态判定一律以「各臂 3 seed 平均」为准）。这张图是**诊断/QC**用途——
看这个 run 有没有跑歪。**要下形态判断，去看 `ARM_A1`。**

### chart2 — 周度供给量（绝对量） `chart2_weekly_supply_volume.png`

| 项 | 内容 |
|---|---|
| 画的是什么 | 堆叠柱：浅蓝 = 注入帖；深蓝 = Agent 产出；柱顶标周总量 |
| 字段 | `injected_count` / `agent_supply` |
| 含义 | 每周「盘子」有多大——W13 事件尖峰、之后如何衰减，以及该 run 里注入与 agent 产出各占多少 |
| 回查表 | `tables/<run>/weekly_supply.csv` |

读图提示：标题写「arena 口径」= 注入 + agent 产出之和。本实验注入预算是 **250 条**
（按周分配），故 agent 产出是总盘子的主导项。

### chart3 — 各内容类型供给量（堆叠面积 · 绝对数量） `chart3_supply_stacked_area.png`

| 项 | 内容 |
|---|---|
| 画的是什么 | 6 类型堆叠面积（玩梗/悼念/教育/营销/其他/噪音），**绝对帖数** |
| 字段 | 每类型 = `agent_supply_<type>` + `injected_<type>` |
| 含义 | 内容构成随时间的绝对量变化——**哪种内容在什么时候占住盘子** |
| 回查表 | `tables/<run>/weekly_supply.csv` |

**这张图的存在意义在于：它与 `real_baseline__chart3` 同款式（配色 / 事件线 / 轴标签 / figsize / dpi 逐项一致），
可以两图并排直接比读形态与量级。** 量级对照：模拟 run 约 50–80 帖/周；真实数据 W12–W22 共 48,360 帖、
W13 单周 11,394。

### chart3b — 各内容类型 Agent 发帖量（不含注入帖） `chart3b_agent_supply_stacked_area.png`

| 项 | 内容 |
|---|---|
| 画的是什么 | chart3 的 **Agent 侧变体**：同样堆叠面积，但只算 Agent 产出 |
| 字段 | 每类型仅 `agent_supply_<type>`；只有 **5 类**（无噪音——噪音只来自注入，Agent 不产噪音帖） |
| 含义 | 把「真实数据注入」这一**外生输入摘掉**，单看模拟 agent 自己造出来的构成 |
| 回查表 | `tables/<run>/weekly_supply.csv` 的 `agent_supply_*` 列 |

**为什么要有这两张**：chart3 是「仿真 arena 的完整盘子」（含外生注入），chart3b 是「模拟自身的产出」。
两者相减即注入贡献。看「模拟是否自己涌现出玩梗二波」要用 **chart3b**；看「与真实数据的总盘子对照」用 chart3。

### chart4 — 玩梗型 Agent 发言率与涌现增益 G `chart4_meme_speaking_rate.png`

| 项 | 内容 |
|---|---|
| 左轴（绿线+填充） | 玩梗型 Agent 发言率 = 玩梗型发言人数 ÷ 玩梗型人数（19 人）；末端标 % |
| 右轴（紫点线） | 涌现增益 G = clamp(B·S, 0.2, 3.0)，**仅观测、不参与决策** |
| 字段 | `agent_agg.meme.spoke_rate` / `meme_env_gain` |
| 含义 | **行为层**：玩梗群体什么时候开始开口、开口比例多高。这是「供给份额」变化的微观来源 |
| 回查表 | `tables/<run>/weekly_agent_behavior.csv`（`spoke_rate`）、`weekly_supply.csv`（`gain_G`） |

**⚠️ 不要按老标题读这张图**：脚本注释已明确记载，旧标题「涌现增益 G 释放后 W19 起爆」把跳变归因给 G，
**该归因已被诊断推翻**（W18/W19 的 G 同为 3.0，跳变来自 D 的输入退化）。2026-09-12 用户裁定
**G 与 agent 侧 θ 一并退役**，G 序列现在**仅作描述性时间轴与审计**。故本图标题已改为中性描述。
右轴的 G 曲线**不是**机制解释，别把它当因。

---

## 3. 臂级图（4 张）—— 主判据

**生成命令**（一条命令读全部 9 个快照）：

```bash
$PYTHON_PATH plot_arm_charts.py
```

**由哪些 run 生成**：自动扫描 `monitor/{random,chronological,interest}_s*/status.json`，
即**全部 9 个 run**。按臂分组，同臂的 3 个 seed 逐周取 **mean / min / max**，图上画均值线 +
`min–max` 包络阴影（n=3 时用包络比 sd 带更诚实）。

**强校验（重要）**：脚本拒绝用不完整数据出图。每个 run 必须同时满足
① 快照周数 = 11；② replay 落盘行数 = `curation_dynamics_agent_state` 100×11 = 1100 行、
`curation_dynamics_env_state` = 11 行。任一不合格 → **报错退出**，不做「有几个算几个」的宽松处理
（少一个 seed 会让 3-seed 均值变成 2-seed 均值却画出同样的曲线——那是静默错误）。
这层校验的存在理由见 [`README.md`](README.md) 第 2 节记录的 writer-bug 事故。

**数据落盘**：`tables/arm_weekly_summary.csv`（每臂每周每指标的 mean/sd/min/max）、
`tables/arm_weekly_by_type.csv`（每臂每周每类型的 agent 发帖量与策展偏差）、
`tables/benchmark.csv`（真实基准，三臂同源故只出一份）。

### ARM_A1 — 玩梗份额 · 三臂 vs 真实基准（**头图，主判据**）`ARM_A1_meme_share_arms_vs_real.png`

- 黑线 = 真实基准；三条彩色线 = 三臂 3-seed 均值（灰 random / 蓝 chronological / 橙 interest）；阴影 = 同臂 seed 间包络。
- 指标同 chart1：combined 口径玩梗供给份额。
- **含义**：三个推荐算法臂**是否都能复现真实的「W20 起爆」形态**，以及**水平精度差多少**。
- 已确立读数（见 [`README.md`](README.md) §4）：三臂都抓住起爆周 W20；Pearson r 为
  random 0.9810 / chronological 0.9893 / **interest 0.9971**，RMSE 相差约 2.3 倍，interest 最优；
  W20 分离度约为 seed 离散度的 5–17 倍。**但 random 与 interest 只差约 2.3 个 seed-sd，n=3 下这一对不硬。**

### ARM_A2 — Agent 周发帖量 · 按内容类型（三面板）`ARM_A2_agent_supply_by_type_arms.png`

- 三个并排面板（每臂一个），各画该臂 3-seed 的 Agent 周发帖量堆叠面积（5 类，**不含注入帖**，`sharey` 同刻度）。
- **含义**：看「**谁先开口**」——不同推荐算法下，各内容类群的产出何时起来、盘子怎么分配。
- 对应逐 run 的 chart3b，只是升到臂级。

### ARM_A3 — 玩梗型 Agent 发言率 · 三臂对比 `ARM_A3_meme_speaking_rate_arms.png`

- 三臂的玩梗型 Agent 发言率（3-seed 均值 + 包络）。
- **含义**：**行为层**的臂间分离——起爆时点与幅度是否被推荐算法改变。
- 对应逐 run 的 chart4 左轴，去掉 G 副轴。

### ARM_A4 — 策展偏差 · 按内容类型（三面板）`ARM_A4_curation_bias_arms.png`

- 每臂一个面板，5 条类型线，零线以下/以上分界。
- **量**：`bias_t = 曝光份额 − combined 供给份额`。**> 0 = 该类被算法多推（放大）；< 0 = 被压制。**
- **含义**：这是**机制层的直接后果量**——算法把哪些内容推多/推少了。是「选择性放大」主张的**最贴近证据**：
  假设说「玩梗群体的曝光份额超过其供给占比」，在这张图里就是**玩梗线（橙）站上零线**。
- 回查表：`tables/arm_weekly_by_type.csv`（`mean_bias` 列）、逐 run 的 `tables/<run>/weekly_bias.csv`。

---

## 4. 真实基准图（2 张）—— **不由任何 run 生成**

**生成命令**：

```bash
$PYTHON_PATH plot_real_baseline_chart.py          # 主图（W12–W22）
$PYTHON_PATH plot_real_baseline_chart.py --zoom   # 另出 W14–W22 细看版
```

**数据来源**（与 9 个 run **无关**）：

- 工作区根目录 `抖音微博小红书-全量已打标.xlsx`（52,736 行，人工打标），剔除 `数据有效性=='存疑'` 20 行；
  `无效` 保留（= 营销 + 噪音，属真实供给组成）。
- **自校验**：脚本现算的「周 × 类型」计数必须与 `hypothesis_4/benchmark_curves.json` 的
  `weekly_category_matrix` **逐周逐类完全相同**，不一致直接 `raise SystemExit` 中止出图——
  防止口径漂移后静默出图。
- 输出 CSV：`tables/real_baseline_weekly_category.csv`（长表：week / type / count / week_total / share）。

### `real_baseline__chart3_supply_stacked_area.png`

- 真实打标数据 W12–W22 六类型绝对帖数堆叠面积，柱顶标周总数。**共 48,360 帖；W13 单周 11,394（占全期 23.6%）。**
- **含义**：模拟侧 `chart3` 的**真实对照图**。同款式是为了并排比读。

### `real_baseline__chart3_supply_stacked_area_W14-W22.png`

- 同图但**剔除 W13 尖峰**（只画 W14–W22）。
- **含义**：绝对量口径下纵轴被 W13 的 11,394 支配，衰减段与玩梗二波被压扁看不出来；
  这张细看版把尖峰拿掉，才能看清 W14 之后的**衰减与 W19+ 二波**。
- 读二波必看这张。

---

## 5. 生成链路（一句话版）

```
runs/<run>/                    引擎落盘（replay JSONL + ENV_STATE.json）
     │  monitor.py 汇总
     ▼
monitor/<run>/status.json      ← 出图脚本的唯一输入
     │
     ├─ plot_run_charts.py  ──► charts/formal/<run>__chart{1,2,3,3b,4}_*.png   （逐 run，45 张）
     │                       └► data/<run>/weekly_*.csv ─┐
     │                                                    │
     └─ plot_arm_charts.py  ──► charts/formal/ARM_A{1,2,3,4}_*.png （9 run 聚合，4 张）
                             └► data/arm/*.csv ──────────┤
                                                          │ 冻结进包
抖音微博小红书-全量已打标.xlsx                            │
     │  plot_real_baseline_chart.py（+ benchmark_curves.json 自校验）│
     └──────────────────────► results/charts/real_baseline__chart3*.png （2 张，不经 formal/）
                                                          ▼
                                              results/（冻结快照）
                                              ├── charts/    51 张图 = formal 的 49 张 + 2 张真实基准图
                                              ├── tables/    58 个 CSV = arm 3 + 逐 run 54 + 真实基准 1
                                              └── snapshots/ 逐 run status.{json,md} + overview
```

**已验证**：`results/charts/` 里 49 张 formal 图与工作副本 `charts/formal/` **逐字节相同**（`cmp` 全过）；
`results/tables/` 与 `data/` 下同名 CSV 亦逐字节相同。冻结包不是「另画一遍」，是同一批文件。

> `results/` 是**冻结快照**（对应 git `82fdc3c`，历史改写前为 `c2d8fb9`）。
> `charts/formal/`、`data/`、`monitor/` 是**工作副本**，重跑脚本会覆盖它们，不会动 `results/`。

---

## 6. 该按什么顺序读

| 问题 | 看哪张 |
|---|---|
| 仿真复现真实现象了吗？ | **`ARM_A1`**（主判据），真实侧对照 `real_baseline__chart3_W14-W22` |
| 三个推荐算法有区别吗？差多少？ | **`ARM_A1`**（份额分离）+ **`ARM_A3`**（行为层分离） |
| 「算法选择性放大玩梗」这个机制成立吗？ | **`ARM_A4`**（看玩梗线是否站上零线） |
| 各内容类群谁先开口？ | **`ARM_A2`**（臂级）/ `chart3b`（逐 run） |
| 模拟的绝对盘子与真实差多远？ | `chart3` 并排 `real_baseline__chart3` |
| 某个 run 是不是跑歪了？ | 该 run 的 `chart1` + `snapshots/<run>/status.md` |
| 单 run 的细节（发言率、G、偏差）？ | 该 run 的 `chart4` / `tables/<run>/weekly_*.csv` |

**两条判读纪律**（来自 `EXPERIMENT.md` §噪声结构与分析口径）：

1. **单 run 锯齿不作形态证据**——45 张逐 run 图用于诊断/QC，形态与臂间比较只看 `ARM_*`。
2. **所有 `± sd` 不是纯蒙特卡洛误差**，而是「RNG 噪声 + 注入池重采样方差」的合并量
   （seed 同时换注入样本），因此「分离度是 seed 离散度的 N 倍」这类倍数是**保守**估计。

---

## 7. 几个必须知道的坑

1. **W17/W18 的玩梗份额恒为 0.000（全部 9 个 run）——是输入的洞，不是行为结论。**
   注入池 W17/W18 的 meme 注入数本身就是 0，模型当周物理上无法产生玩梗；两者真实值为 0.022 / 0.026。
   `chart1` / `chart3` / `ARM_A1` 上这个「凹口」按此理解。

2. **真实的二波是「渐起」，模拟是「开关」。** 真实 W13–W19 一直有低但持续的玩梗（0.013 → 0.078），
   模拟几乎恒为 0 然后在 W20 突变。任何「形状比 / 斜坡」类判据都会受此影响。

3. **`plot_real_baseline_chart.py` 直接写 `results/charts/`**（脚本 `OUT_DIR` 写死指向冻结包），
   而非写工作副本 `charts/formal/`。**重跑它会覆盖冻结快照里的这 2 张图**——
   如果只是想在别处试验，先改 `OUT_DIR` 或先备份。

4. **`charts/formal/` 不含真实基准图**（49 张 = 4 臂级 + 45 逐 run）。
   真实基准 2 张只存在于 `results/charts/`。

5. **`ARM_A4` 的 `bias` 分母是 combined 供给份额（含注入帖）**，不是 agent 产出口径。
   `monitor.py` 里另有 `supply_share_*`（仅 agent 口径、分母不含噪音）的版本，别混用。

6. **`ARM_*` 图例标签里的 `n=3`** 恒等于「该臂 3 个 seed 全部通过校验」。
   若某臂显示 `n=2`，说明有 run 被校验拦下了——此时脚本本身**不会出图**（强校验会直接退出），
   所以看到 `n=2` 只可能来自 `--dry-run`，那是验证脚本本身用的，不是产物。
