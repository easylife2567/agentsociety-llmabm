# H4-E1 实验结果包

**实验**：算法策展如何塑造公众人物去世后公共话语的数字表征
**案例**：张雪峰，去世 2026-03-24（2026-W13）
**批次**：9-run 批跑（3 推荐算法臂 × 3 seed），2026-09-13 完成
**代码版本**：git `82fdc3c`（2026-09-13 历史改写后的提交号；改写前为 `c2d8fb9`，见 `ARCHIVE_MANIFEST_H4E1_formal_20260913.md` 第五节）

---

## 1. 设计

| 项 | 设定 |
|---|---|
| Agent | 100 个固定类型（营销 23 / 悼念 22 / 其他 21 / 玩梗 19 / 教育 15） |
| 时间窗 | W12–W22 共 11 周，tick = 1 周 |
| 实验组 | 3 臂 × 3 seed = 9 runs：`{random, chronological, interest}_s{0,1,2}` |
| 发言决定 | 确定性 `U = D·R ≥ activity`（无 RNG 抽签） |
| D | 沉默螺旋 `D = 1 + s·tanh(k·(share_own − base)/base)`，k=1.5 |
| R | 注意力衰减 `R = exp(−λ·cum_own/scale)`，scale=15.0 |
| 注入预算 | 250 条帖子，按周分配 |
| 分析单位 | **各臂 3 seed 平均**（EXPERIMENT.md:294 用户裁定；单 run 锯齿不作形态证据） |

**受控比较已核对**：同 seed 下三臂的 config 逐行 diff 只差一行
`recommendation_algorithm` —— 即 agent 构成、注入池、随机种子全部相同，**只改推荐算法**。

**seed 的含义**：`s0/s1/s2` 同时改 `random_seed` 与 `injection_sample_s{0,1,2}.json`
（注入帖样本），所以 seed 间差异**包含注入池重采样方差**，不只是蒙特卡洛噪声。
这影响第 6 节对 seed-sd 的解读。

---

## 2. 验收

| 检查 | 结果 |
|---|---|
| `step_count` | 9/9 = 11/11 |
| `curation_dynamics_agent_state` | 9/9 = 1100 行（100 agent × 11 周） |
| `curation_dynamics_env_state` | 9/9 = 11 行 |
| `litellm` 错误 / AIMD DECREASE | 全程 0（并发上限只升不降） |
| `verify_experiment.py` | 25/25 通过 |

> 本次批跑有 2 个 run（`random_s2`、`interest_s1`）在 step 0 撞上框架级竞态
> （replay 写入器被覆盖为 `dict`），引擎误报 completed 而表为空。已定位、加守卫、重跑，
> 上面的验收是对**重跑后**的数据做的。事故留痕见 `runs_retired_writer_bug/`。

---

## 3. 目录

```
results/
├── README.md          本文件
├── charts/            49 张图
│   ├── ARM_A1..A4_*   臂级（3-seed 均值）—— 主判据图
│   └── <run>__chart*  逐 run（9 run × 5 图型）
├── tables/            57 个 CSV
│   ├── arm_*.csv      臂级周度汇总 / 分类型 / 真实基准
│   └── <run>/         逐 run 周度表
└── snapshots/         逐 run status.md/json + 多 run 总览
```

`charts/ARM_A1_meme_share_arms_vs_real.png` 是头图。

---

## 4. 主判据：玩梗份额的二波形态

真实基线来自抖音真实数据（`tables/benchmark.csv`）。指标为 **combined 供给份额**
（agent 帖 + 注入帖同分母），与真实基准同口径。

| 臂 | Pearson r | RMSE | 起爆周 | 峰值周 |
|---|---|---|---|---|
| 真实 | — | — | W20 | W22 仍在升 |
| random | 0.9810 | 0.0551 | W20 ✓ | W22 ✓ |
| chronological | 0.9893 | 0.0601 | W20 ✓ | **W21 ✗** |
| **interest** | **0.9971** | **0.0240** | W20 ✓ | W22 ✓ |

**三臂都抓住了二波起爆周（W20）；水平精度相差 2.3 倍，interest 明显最好。**

### 臂间分离（W20，分离最大的一周）

| 臂 | W20 玩梗份额（3-seed） | 相对真实 0.298 |
|---|---|---|
| random | 0.176 ± 0.018 | 低 41% |
| **interest** | **0.259 ± 0.048** | 低 13% |
| chronological | 0.441 ± 0.012 | 高 48% |

分离度约为 seed 离散度的 **5–17 倍**（chronological 对另两臂）——效应量远大于种子噪声。
但 **random 与 interest 只差约 2.3 个 seed-sd，n=3 下这一对不硬**。

### 终局（W22）

| 臂 | W22 | 3-seed sd |
|---|---|---|
| 真实 | 0.6032 | — |
| random | 0.602 | 0.027 |
| chronological | 0.656 | 0.088 |
| **interest** | **0.603** | **0.002** |

interest 臂**同时最准且最稳**（seed 间 sd 仅 0.002，是 chronological 的 1/44）。

---

## 5. 全类型拟合（11 周平均绝对差，越小越像）

| 类型 | random | chronological | interest |
|---|---|---|---|
| **meme** | 0.0337 | 0.0389 | **0.0175** |
| mourning | **0.0461** | 0.0629 | 0.0502 |
| education | 0.0368 | 0.0550 | **0.0263** |
| marketing | 0.1159 | **0.0889** | 0.1330 |
| other | **0.0343** | 0.0557 | 0.0480 |
| noise | 0.0479 | **0.0461** | 0.0488 |
| **全类型均值** | **0.0525** | 0.0579 | 0.0540 |

**关键读数**：按全六类平均，三臂几乎不分伯仲（0.053 / 0.054 / 0.058）。
**推荐算法的作用几乎只体现在玩梗这一通道上。**

> 因此本实验支持的主张应收窄为「算法策展塑造**玩梗类**表征的二波形态」，
> 而非「塑造全局话语构成」。

---

## 6. 已知局限（判读时必须扣除）

1. **W17/W18 玩梗份额恒为 0.000（全部 9 个 run）—— 这是输入的洞，不是行为结论。**
   注入池 W17/W18 的 meme 注入数本身就是 0，模型当周物理上无法产生玩梗；
   两者真实值为 0.022 / 0.026。

2. **真实的二波是"渐起"，模拟是"开关"。**
   真实 W13–W19 一直有低但持续的玩梗（0.013 → 0.078），模拟几乎恒为 0，
   然后 W20 突变。任何"形状比 / 斜坡"类判据都会受此影响。

3. **营销是全部三臂中最差的类型**（0.089–0.133，其余类型 0.017–0.063），
   模拟中段营销份额系统偏高（W19 模拟 0.522 vs 真实 0.393）。
   与预登记偏差「营销疲劳 λ 偏弱 → 退得比真实慢」一致。

4. **n = 3 seed**：效应量很大且方向一致，但上述比较只能作描述性判断。
   且 seed 同时换了注入样本，所以文中所有 `± sd` **不是纯蒙特卡洛误差**，
   而是「RNG 噪声 + 注入池重采样方差」的合并量——
   解读「分离度是 seed 离散度的 N 倍」时应按此理解（该倍数因此是**保守**的）。

5. **死亡周构成复现尚可**：W13 悼念份额 模拟 0.487（interest）/ 0.501（random）/ 0.551（chronological）
   vs 真实 0.414 —— 三臂一致略过冲，但形状与量级都在。

---

## 7. 复现

```bash
PYTHON_PATH=$(grep "^PYTHON_PATH=" ../../.env | cut -d'=' -f2)

# 跑批（3 并发）
$PYTHON_PATH run_batch.py --concurrency 3 --without-confirm

# 验收
$PYTHON_PATH verify_experiment.py

# 快照（写 monitor/）
$PYTHON_PATH monitor.py

# 出图（逐 run → charts/，臂级 → charts/ARM_*）
for r in random_s{0,1,2} chronological_s{0,1,2} interest_s{0,1,2}; do
  $PYTHON_PATH plot_run_charts.py --status monitor/$r/status.json --run-id $r
done
$PYTHON_PATH plot_arm_charts.py
```

> `results/` 是**冻结快照**（对应 git `82fdc3c`，改写前为 `c2d8fb9`），不是脚本的输出目录。
> 脚本仍写 `charts/`、`data/`、`monitor/`；重跑后需重新生成本包。
