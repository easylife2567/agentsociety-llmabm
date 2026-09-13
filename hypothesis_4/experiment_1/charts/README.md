# charts/ 目录约定

**规则（用户 2026-09-13 要求）：烟测实验、预测、正式实验的图表分开放。**

| 桶 | 内容 | 谁写 | 权威性 |
|---|---|---|---|
| `formal/` | **正式 9-run 批跑**（3 推荐算法臂 × 3 seed，2026-09-13）的逐 run 图 + 臂级图 | `plot_run_charts.py`（默认）、`plot_arm_charts.py`（默认） | 主判据来源 |
| `prediction/` | **代理预测**（只读数值推演，不跑 LLM） | `proxy_predict*.py` | 预测，非结果 |
| `smoke/` | **烟测 / 预跑单 run**（正式批跑前） | `plot_run_charts.py --charts-dir charts/smoke` | 仅追溯/诊断 |

---

## formal/ — 正式实验（49 张）

- `ARM_A1..A4_*.png`（4 张）—— **臂级 3-seed 均值，主判据图**。
  `ARM_A1_meme_share_arms_vs_real.png` 是头图。
- `<run>__chart{1,2,3,3b,4}_*.png`（45 张 = 9 run × 5 图型）—— 逐 run 诊断/QC 图。

> 单 run 锯齿不作形态证据（`EXPERIMENT.md:294` 用户裁定）；判读以 `ARM_*` 为准。
> 同一批图的**冻结快照**在 `../results/charts/`（实验包，对应 git `82fdc3c`）。
> 本目录是**工作副本**，重跑脚本会覆盖它，但不会动 `../results/`。

## prediction/ — 代理预测（16 张）

- `PROXY_pred_REGRESSION_CHECK.png` —— 反事实开关改动后的**默认路径回归检验**
  （比对确认与改动前逐值一致，见 `../pred_*_log.txt`）。
- `counterfactual_2mech/`（8 张）—— **本轮两机制反事实预测**
  （沉默螺旋 D × 注意力衰减 R 的 2×2 消融）。
  每套四张：`A` 份额+总量、`B` 各 cell 构成、`C` 消融效应柱状图、
  **`D` 双重分离三联图（分子/分母/比值并排 —— 本轮最核心的一张）**。
  30 seed 与 100 seed 两套：`PROXY_cf_*` / `PROXY_cf_s100_*`（两者几乎逐值相同）。
  预登记读数与可证伪判据见 **`../PREDICTION_counterfactual_2mech.md`**。
- `early_tuning/`（10 张）—— 定标阶段的探索性预测
  （R 半饱和尺度 17/20/15、事件周保底条数、营销 λ 等档位对比）。
  这些**不是**结果，是当时用来选参数的过程记录。

> `proxy_predict.py` 的常规产物（各类 agent 周发帖数预测）也写在本目录。

## smoke/ — 烟测与预跑单 run（10 张）

- `interest_normal_s0__chart*`（5 张）—— 烟测 run（feed 机制重设计后）。
- `interest_nog_s0__chart*`（5 张）—— **no-G 反事实探针** run。
  它是单 run 探针而非烟测，但同属"正式批跑前的单 run"，故并入本桶；
  其证据作用见 `../SMOKE_DIAGNOSIS_w19_cliff.md` §五之三。

---

## 出图命令（重跑时）

```bash
PYTHON_PATH=$(grep "^PYTHON_PATH=" ../../.env | cut -d'=' -f2)

# 正式：逐 run → charts/formal/，臂级 → charts/formal/
for r in random_s{0,1,2} chronological_s{0,1,2} interest_s{0,1,2}; do
  $PYTHON_PATH plot_run_charts.py --status monitor/$r/status.json --run-id $r
done
$PYTHON_PATH plot_arm_charts.py

# 烟测：显式指定桶
$PYTHON_PATH plot_run_charts.py \
  --status monitor/<smoke_run>/status.json --charts-dir charts/smoke

# 预测
$PYTHON_PATH proxy_predict.py                       # → charts/prediction/
$PYTHON_PATH proxy_predict_counterfactual.py        # → charts/prediction/counterfactual_2mech/
```
