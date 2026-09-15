# anchored_v1 主实验结果包

本目录只收纳新公式

\[
U_i=B_i+R_i(D_i-B_i)
\]

下的主实验：3 种推荐算法 × 3 seeds，共 9 个 run。旧公式、旧 random、旧
chronological、烟测失败和中断残留均不放入本目录。

## 目录结构

```text
anchored_v1/
├── anchored_v1_random_s0/          # 原始引擎输出（raw run）
├── anchored_v1_random_s1/          # 后续运行时自动创建
├── ...
├── anchored_v1_interest_s2/
└── _derived/
    ├── monitor/<run_id>/            # status.md / status.json
    ├── data/<run_id>/               # 6 张周度 CSV 表
    ├── data/arm/                    # 三臂 3-seed 汇总表（9 run 完成后生成）
    └── charts/                      # 逐 run 图与臂级汇总图
```

原始 run 目录包含 `pid.json`、`SOCIETY*.json`、`replay/`、`agents/`、`env/`
和日志；这些大体积可重建文件被 Git 忽略。`_derived/` 中的 CSV 与图表作为持久结果入库。

## AgentSociety 官方兼容入口

AgentSociety 当前的 `run-experiment status` 与 `analysis intake` 只读取单一的
`experiment_1/run/replay`，暂不能原生登记同一实验的 9 个 replay。为兼容官方工具，
`../../run` 使用相对符号链接指向本批的生成性验证主 run
`anchored_v1_interest_s0`。该入口只负责让官方完成性检查和分析 harness 找到一份
合法 replay，**不代表三臂分析只有一个 run**。

正式反事实分析的权威输入是本目录下全部 9 个 run，以及
`_derived/data/arm/` 的 3-seed 聚合表。批次边界和历史排除规则见
`../README.md`；不得让旧公式正式批、烟测或中断残留进入本轮输入。

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

权威配置与运行顺序仍以 `../../init/configs/manifest.json` 为准。
