# anchored_v1 已取代正式批的派生结果兼容包

本目录只收纳新公式

\[
U_i=B_i+R_i(D_i-B_i)
\]

下的主实验：3种推荐算法×3 seeds，共9个完整run。2026-09-27因周级真实帖子注入时机改为一期滞后而被`weekly_lag1`取代，不再是最新正式证据。

9个原始run已归档至`archive/hypothesis_4_experiment_1_batches/formal_superseded/anchored_v1/raw/`。本目录保留Git跟踪的`_derived/`冻结副本，避免旧论文、审阅记录和图表引用失效。

## 目录结构

```text
anchored_v1/
├── README.md
└── _derived/                        # 归档时冻结的兼容副本
    ├── monitor/<run_id>/            # status.md / status.json
    ├── data/<run_id>/               # 6 张周度 CSV 表
    ├── data/arm/                    # 三臂 3-seed 汇总表（9 run 完成后生成）
    └── charts/                      # 逐 run 图与臂级汇总图
```

原始run的`pid.json`、`SOCIETY*.json`、`replay/`、`agents/`、`env/`和日志均已移入本地归档。`_derived/`中的CSV与图表继续入库，只能作为旧批证据使用。

## AgentSociety 官方兼容入口

AgentSociety 当前的 `run-experiment status` 与 `analysis intake` 只读取单一的
`experiment_1/run/replay`，暂不能原生登记同一实验的 9 个 replay。为兼容官方工具，
`../../run`现已转向当前`weekly_lag1_interest_s0`，不再指向本批。

本批完整raw证据与配置见根目录归档索引。不得把本批的聚合表当作`weekly_lag1`结果。

## 9-run 状态

| run | 状态 | 引擎批次 |
|---|---|---:|
| `anchored_v1_random_s0` | 已完成 | 11/11 |
| `anchored_v1_random_s1` | 已完成 | 11/11 |
| `anchored_v1_random_s2` | 已完成 | 11/11 |
| `anchored_v1_chronological_s0` | 已完成 | 693/693 |
| `anchored_v1_chronological_s1` | 已完成 | 693/693 |
| `anchored_v1_chronological_s2` | 已完成 | 693/693 |
| `anchored_v1_interest_s0` | 已完成（原完整 smoke，现升格为正式 s0） | 11/11 |
| `anchored_v1_interest_s1` | 已完成 | 11/11 |
| `anchored_v1_interest_s2` | 已完成 | 11/11 |

9 个 run 均使用当前锚定式公式并已覆盖 W12–W22。`interest_s0` 虽然最初以 smoke
标签运行，但完整执行了 11 周，配置与当前正式 s0 一致；后续代码改动只改变
random-global 与 hourly chronological 的独立路径，因此无需重跑。完成性复核见
`_derived/monitor/overview.md`；每个 run 均已生成 6 张周度 CSV、5 张逐 run 图，三臂
3-seed 汇总表及臂级图也已生成。

本批历史配置副本保存在归档中；当前配置以`../../init/configs/weekly_lag1_manifest.json`为准。
