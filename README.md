# 算法策展与公众人物身后数字表征

本仓库是一个基于 AgentSociety 的可执行社会科学研究工作区，研究问题是：**推荐算法如何通过选择性放大不同表达群体，改变公众人物去世后的公共数字表征？**

当前提交版本以 `hypothesis_4/experiment_1` 为唯一主实验，采用 3 种推荐制度 × 3 个随机种子的设计，共 9 个正式 run。9 个 run 已全部完成并通过完成性复核；结果分析仍在进行。最终报告尚未完成，因此本版不把 `paper/` 作为正式成果或实验状态依据。

## 1. 研究设计概览

- 研究对象：公众人物去世后的平台表达与数字表征转移。
- 经验效标：真实打标数据中“教育表达 → 事件悼念 → 玩梗再激活”的周级变化。
- 仿真规模：100 个固定类型 Agent，W12–W22 共 11 个周点。
- 对照因素：推荐制度。
- 实验臂：`random`、`chronological`、`interest`。
- 重复次数：每个实验臂 3 个 seeds，共 9 个正式 run。
- 当前行为公式：`U_i = B_i + R_i(D_i - B_i)`。

三种推荐制度是完整的平台策展制度反事实：

- `random`：从截至当周已经出现的全部帖子中，对全部 10 个 feed 槽位进行均匀无放回抽样，不使用时序、兴趣、热度、生命周期、置顶或事件周保底。
- `chronological`：按事件前真实的星期 × 小时分布行动，在每个行动时刻推荐当时已经发布的最新 10 条帖子；同小时 Agent 共享批次前快照。
- `interest`：从仍处于生命周期内的候选帖中按兴趣分比例抽样，并保留该制度下的共同议程槽位。

三臂差异应解释为三种完整策展制度的总体效应，而不是相同候选池下的单一排序效应。更完整的理论与操作化说明见 [`TOPIC.md`](TOPIC.md)、[`hypothesis_4/HYPOTHESIS.md`](hypothesis_4/HYPOTHESIS.md) 和 [`hypothesis_4/experiment_1/EXPERIMENT.md`](hypothesis_4/experiment_1/EXPERIMENT.md)。

## 2. 当前状态

| 阶段 | 状态 | 权威材料 |
|---|---|---|
| 研究问题与假设 | 已完成 | `TOPIC.md`、`hypothesis_4/HYPOTHESIS.md` |
| 实验配置 | 已完成 | `hypothesis_4/experiment_1/init/configs/manifest.json` |
| 正式实验 | **已完成，9/9** | `hypothesis_4/experiment_1/runs/anchored_v1/` |
| 完成性复核 | **已通过** | `runs/anchored_v1/_derived/monitor/overview.{md,json}` |
| 结果分析 | 进行中 | `runs/anchored_v1/_derived/`、`presentation/` |
| 最终报告 | 尚未完成，本版不纳入 | `paper/` |

9 个正式 run 均覆盖 W12–W22。`random` 与 `interest` 各执行 11 个周级批次；`chronological` 为小时级微批次制度，每个 run 执行 693 个引擎批次并汇总为 11 个周点。

## 3. 官方目录与权威入口

工作区保持 AgentSociety 推荐的 `hypothesis_{id}/experiment_{id}/init`、`run` 与分析产物结构，同时在 `runs/anchored_v1/` 中保存多臂多 seed 扩展：

```text
.
├── TOPIC.md
├── PARAMETERS.md
├── env.template
├── custom/
│   ├── agents/                         # 自定义 Agent
│   └── envs/                           # 推荐、互动与环境机制
├── datasets/                           # 可选的受控复现数据
├── hypothesis_4/
│   ├── HYPOTHESIS.md
│   ├── SIM_SETTINGS.json
│   ├── benchmark_curves.json
│   └── experiment_1/
│       ├── EXPERIMENT.md
│       ├── init/                       # 官方实验配置入口
│       ├── run -> runs/anchored_v1/anchored_v1_interest_s0
│       ├── runs/
│       │   ├── README.md               # 批次分类与排除规则
│       │   └── anchored_v1/
│       │       ├── README.md           # 最新正式批说明
│       │       ├── anchored_v1_*       # 3 arms × 3 seeds 原始 run
│       │       └── _derived/           # CSV、图表和完成性快照
│       ├── run_batch.py
│       ├── verify_experiment.py
│       └── monitor.py
└── presentation/
    └── hypothesis_4/data/analysis_sources.json
```

### 入口优先级

1. 官方单-run兼容入口：`hypothesis_4/experiment_1/run/`，锚定生成性验证主 run `anchored_v1_interest_s0`。
2. 全部正式实验：`hypothesis_4/experiment_1/runs/anchored_v1/anchored_v1_{random,chronological,interest}_s{0,1,2}`。
3. 跨臂结论的权威数据：`hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/`。
4. 9-run 机器可读清单：`presentation/hypothesis_4/data/analysis_sources.json`。

AgentSociety 当前官方状态检查与分析 intake 读取单一 `run/replay`，因此 `run/` 只承担官方兼容和生成性验证入口的作用。跨算法结论必须使用全部 9 个 replay 或三臂 3-seed 聚合表，不能只读取 `run/`。

> 打包注意：`run` 在工作区中是相对符号链接。提交压缩包时应确认压缩格式保留符号链接，或在交付副本中将其实体化为同内容的真实目录，避免解压后丢失 `run/replay`。

## 4. 最新正式实验矩阵

| 算法 | seed 0 | seed 1 | seed 2 | 状态 |
|---|---|---|---|---|
| random | `anchored_v1_random_s0` | `anchored_v1_random_s1` | `anchored_v1_random_s2` | 3/3 完成 |
| chronological | `anchored_v1_chronological_s0` | `anchored_v1_chronological_s1` | `anchored_v1_chronological_s2` | 3/3 完成 |
| interest | `anchored_v1_interest_s0` | `anchored_v1_interest_s1` | `anchored_v1_interest_s2` | 3/3 完成 |

每个 run 均有 replay schema、6 张周度 CSV 和 5 张逐 run 图。三臂聚合目录包含 3-seed 周度汇总、拟合指标、DTW 指标、平台—用户机制链数据及汇总图。完成性详情见 [`hypothesis_4/experiment_1/runs/anchored_v1/_derived/monitor/overview.md`](hypothesis_4/experiment_1/runs/anchored_v1/_derived/monitor/overview.md)。

## 5. 环境与复现

本工作区验证环境：

- AgentSociety2：`2.8.4`
- 对应引擎 Git revision：`13e28b5e`
- Python：`3.13.9`

不要提交含真实凭据的 `.env`。请从模板创建本机配置，并将 `PYTHON_PATH` 指向能够导入 `agentsociety2` 的 Python：

```bash
cp env.template .env
```

然后按本机 `.env` 解析解释器：

```bash
PYTHON_PATH=$(grep "^PYTHON_PATH=" .env | cut -d'=' -f2)
PYTHON_PATH=${PYTHON_PATH:-python3}
```

### 5.1 检查流水线与配置

```bash
$PYTHON_PATH .agentsociety/bin/ags.py research-pipeline where-am-i --json
$PYTHON_PATH .agentsociety/bin/ags.py experiment-config validate \
  --hypothesis-id 4 --experiment-id 1
$PYTHON_PATH hypothesis_4/experiment_1/verify_experiment.py
```

`verify_experiment.py` 是离线核验，不调用 LLM；它检查正式配置、样本、关键机制与批次一致性。

### 5.2 预览和运行 9-run 批次

先只打印计划：

```bash
$PYTHON_PATH hypothesis_4/experiment_1/run_batch.py --dry-run
```

确认 API、预算和运行环境后再启动。建议并发数不超过 3：

```bash
$PYTHON_PATH hypothesis_4/experiment_1/run_batch.py \
  --concurrency 3 --with-monitor
```

该命令会产生外部 LLM 调用和相应费用。调度器具有完成检测能力，不会默认重跑已经完成的正式 run；除非明确需要重算，不要使用 `--force`。

### 5.3 刷新完成性总览

```bash
$PYTHON_PATH hypothesis_4/experiment_1/monitor.py --overview-only
```

## 6. 配置与结果边界

正式批次 ID 为 `anchored_v1`。只有以下 9 个目录进入当前正式分析：

```text
hypothesis_4/experiment_1/runs/anchored_v1/anchored_v1_*
```

以下内容均不得并入当前统计：

| 路径或类型 | 分类 | 当前用途 |
|---|---|---|
| 旧公式 9-run 与旧冻结图表/CSV | 历史正式批，旧公式 `U=D·R` | 已移出 `hypothesis_4/`，仅作版本审计 |
| 历史烟测与早期探针 | `smoke/probe` | 已移出 `hypothesis_4/` |
| replay 写入器事故样本 | `invalid` | 已移出 `hypothesis_4/` |
| 停止、中断或混跑残留 | `invalid/partial` | 已移出 `hypothesis_4/` |
| 退役两因子配置与旧公式配置 | `historical_config` | 已移出 `hypothesis_4/` |

上述材料已备份到本地 `archive/hypothesis_4_experiment_1_history_20260915/`，不属于比赛提交内容；索引见根目录 `ARCHIVE_MANIFEST_H4E1_history_20260915.md`。不得将其放回 `anchored_v1/`，也不得修改 `analysis_sources.json` 将其列为正式数据源。

## 7. 消融结果说明

`ABLATION_anchored_v1.md` 已登记 B、D、R 三项 one-at-a-time 消融，但正式 AgentSociety/LLM 消融尚未运行。现有 `results/numerical_ablation_drb/` 是复用同源纯函数完成的 100-seed numerical proxy，只用于机制方向检查，不能与正式 9-run 并列，也不能表述为正式 ABM/LLM 消融结果。

## 8. 数据与提交说明

建议将比赛材料分为两个层级：

### 核心评审包

包含研究说明、`hypothesis_4` 当前配置、`custom` 实现、`anchored_v1/_derived`、批次 README 和 `analysis_sources.json`。该层足以检查研究设计、程序实现、9-run 完成性与聚合结果。

### 可复现数据附件

在比赛规则、数据授权和隐私要求允许时，另附：

- 9 个 `anchored_v1_*` 原始 replay；
- `custom/envs/curation_assets/injection_posts.json`；
- `datasets/zhangxf_labeled/valid_posts_clusters.parquet`；
- 必要时另行受控提供原始打标 Excel。

真实帖子样本可能包含原文和作者字段，提交或公开前必须按比赛条款检查数据授权、隐私和再分发条件。

原始 replay 和部分数据文件受 `.gitignore` 管理，因此不要只用 `git archive` 制作完整复现包；否则这些本地存在但未纳入 Git 的文件会被遗漏。

## 9. 安全与排除项

以下文件或目录不属于比赛成果包：

- `.env`、`easypaper_config.yaml` 等真实凭据或本机配置；
- `AgentSociety2/` 上游引擎源码及其虚拟环境；
- `.git/`、`.claude/`、`.codex/`、`.mcp.json`、`.vscode/`；
- `.playwright-mcp/`、缓存、日志、`__pycache__`、`.DS_Store`；
- `agentsociety_data/` 等可重建运行缓存；
- 未完成的 `paper/`；
- 全量文献 PDF 和重复研究档案。
- `archive/` 下的本地历史实验备份。

上游 AgentSociety2 不随包复制；请使用前述版本号和 revision 复现依赖环境。

## 10. 关键文件索引

| 内容 | 路径 |
|---|---|
| 研究主题 | `TOPIC.md` |
| 参数口径 | `PARAMETERS.md` |
| 实验约束 | `EXPERIMENT_CONSTITUTION_1788335113228_0_gm0h.md` |
| 主假设 | `hypothesis_4/HYPOTHESIS.md` |
| 仿真设置 | `hypothesis_4/SIM_SETTINGS.json` |
| 真实效标 | `hypothesis_4/benchmark_curves.json` |
| 实验设计 | `hypothesis_4/experiment_1/EXPERIMENT.md` |
| 权威配置清单 | `hypothesis_4/experiment_1/init/configs/manifest.json` |
| 批次边界 | `hypothesis_4/experiment_1/runs/README.md` |
| 最新正式批说明 | `hypothesis_4/experiment_1/runs/anchored_v1/README.md` |
| 9-run 完成性总览 | `hypothesis_4/experiment_1/runs/anchored_v1/_derived/monitor/overview.md` |
| 三臂聚合数据 | `hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/` |
| 正式结果图 | `hypothesis_4/experiment_1/runs/anchored_v1/_derived/charts/` |
| 多数据源清单 | `presentation/hypothesis_4/data/analysis_sources.json` |

---

**本 README 对应快照：2026-09-15。** 后续最终报告完成后，应单独更新提交清单和成果状态；在此之前，以本文件列出的 `anchored_v1` 边界、`manifest.json` 和 `analysis_sources.json` 为准。
