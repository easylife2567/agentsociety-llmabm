# 算法策展与公众人物身后数字表征

本仓库是一个基于 AgentSociety 的可执行社会科学研究工作区，研究问题是：**推荐算法如何通过选择性放大不同表达群体，改变公众人物去世后的公共数字表征？**

当前修订以`hypothesis_4/experiment_1`为唯一主实验。原`anchored_v1`的9个run已完整归档，但因真实帖注入时机问题不再作为最新正式证据。`weekly_lag1`已完成受影响的interest/random×3 seeds，共6个run；chronological保持原设计，不混入本轮主比较。

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
| 实验配置 | 已完成 | `hypothesis_4/experiment_1/init/configs/weekly_lag1_manifest.json` |
| 旧正式批 | 已归档，9/9完整但被取代 | `ARCHIVE_MANIFEST_H4E1.md` |
| 当前正式实验 | 已完成，6/6 | `hypothesis_4/experiment_1/runs/weekly_lag1/` |
| 当前完成性复核 | 已通过 | `runs/weekly_lag1/_derived/monitor/` |
| 结果分析 | 进行中，已生成三seed聚合数据与探索图 | `runs/weekly_lag1/_derived/`、`presentation/hypothesis_4/` |
| 最终报告 | 尚未完成，本版不纳入 | `paper/` |

当前6个run均完整覆盖W12–W22，每个run执行11个周级批次并产生1100条Agent状态与11条环境状态。旧`anchored_v1`中的chronological 3个run完成693个小时批次，仅保留作未改制度的历史参照。

## 3. 官方目录与权威入口

工作区保持AgentSociety推荐的`hypothesis_{id}/experiment_{id}/init`和`run`结构，同时用`runs/weekly_lag1/`保存多臂多seed扩展：

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
│       ├── run -> runs/weekly_lag1/weekly_lag1_interest_s0
│       ├── runs/
│       │   ├── README.md               # 批次分类与排除规则
│       │   ├── weekly_lag1/             # 当前2 arms × 3 seeds正式批
│       │   └── anchored_v1/_derived/    # 已取代批的冻结派生结果兼容副本
│       ├── run_batch.py
│       ├── verify_experiment.py
│       └── monitor.py
└── presentation/
    └── hypothesis_4/data/analysis_sources.json
```

### 入口优先级

1. 官方单-run兼容入口：`hypothesis_4/experiment_1/run/`，指向`weekly_lag1_interest_s0`。
2. 当前正式实验：`hypothesis_4/experiment_1/runs/weekly_lag1/weekly_lag1_{interest,random}_s{0,1,2}`。
3. 当前配置清单：`hypothesis_4/experiment_1/init/configs/weekly_lag1_manifest.json`。
4. 历史批次分类：`ARCHIVE_MANIFEST_H4E1.md`。

AgentSociety 当前官方状态检查与分析 intake 读取单一 `run/replay`，因此 `run/` 只承担官方兼容和生成性验证入口的作用。本轮interest/random结论必须使用全部6个 replay 的两臂3-seed聚合表，不能只读取 `run/`；旧chronological不与本轮数值混算。

> 打包注意：`run` 在工作区中是相对符号链接。提交压缩包时应确认压缩格式保留符号链接，或在交付副本中将其实体化为同内容的真实目录，避免解压后丢失 `run/replay`。

## 4. 当前正式实验矩阵

| 算法 | seed 0 | seed 1 | seed 2 | 状态 |
|---|---|---|---|---|
| random | `weekly_lag1_random_s0` | `weekly_lag1_random_s1` | `weekly_lag1_random_s2` | 完成 |
| interest | `weekly_lag1_interest_s0` | `weekly_lag1_interest_s1` | `weekly_lag1_interest_s2` | 完成 |

每个run均已有replay、周度CSV和逐run图。旧`anchored_v1`的冻结派生结果仍保留在原`_derived/`路径，但已明确分类为superseded。

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
$PYTHON_PATH hypothesis_4/experiment_1/run_weekly_lag_batch.py \
  --concurrency 2 --with-monitor
```

该命令会产生外部 LLM 调用和相应费用。调度器具有完成检测能力，不会默认重跑已经完成的正式 run；除非明确需要重算，不要使用 `--force`。

### 5.3 刷新完成性总览

```bash
$PYTHON_PATH hypothesis_4/experiment_1/monitor.py \
  --out-dir hypothesis_4/experiment_1/runs/weekly_lag1/_derived/monitor \
  --run-dir hypothesis_4/experiment_1/runs/weekly_lag1/weekly_lag1_interest_s0
```

## 6. 配置与结果边界

当前正式批次ID为`weekly_lag1`。只有以下6个目录在完成性复核后可以进入新分析：

```text
hypothesis_4/experiment_1/runs/weekly_lag1/weekly_lag1_*
```

以下内容均不得并入当前统计：

| 路径或类型 | 分类 | 当前用途 |
|---|---|---|
| `anchored_v1` 9-run | 已完成但被注入时机修订取代 | 已归档，仅用于旧结论复核和新旧配对比较 |
| 旧公式 9-run 与旧冻结图表/CSV | 历史正式批，旧公式 `U=D·R` | 已移出 `hypothesis_4/`，仅作版本审计 |
| 历史烟测与早期探针 | `smoke/probe` | 已移出 `hypothesis_4/` |
| replay 写入器事故样本 | `invalid` | 已移出 `hypothesis_4/` |
| 停止、中断或混跑残留 | `invalid/partial` | 已移出 `hypothesis_4/` |
| 退役两因子配置与旧公式配置 | `historical_config` | 已移出 `hypothesis_4/` |

全部历史材料的位置和证据分类见根目录`ARCHIVE_MANIFEST_H4E1.md`。不得把归档raw run放回当前活动批，也不得把它们列为最新正式数据源。

## 7. 消融结果说明

`ABLATION_anchored_v1.md` 已登记 B、D、R 三项 one-at-a-time 消融，但正式 AgentSociety/LLM 消融尚未运行。现有 `results/numerical_ablation_drb/` 是复用同源纯函数完成的 100-seed numerical proxy，只用于机制方向检查，不能与正式 9-run 并列，也不能表述为正式 ABM/LLM 消融结果。

## 8. 数据与提交说明

建议将比赛材料分为两个层级：

### 核心评审包

新批完成后，核心评审包应包含研究说明、`hypothesis_4`当前配置、`custom`实现、`weekly_lag1/_derived`、批次README和更新后的分析来源清单。

### 可复现数据附件

在比赛规则、数据授权和隐私要求允许时，另附：

- 6个`weekly_lag1_*`原始replay；
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
| 当前配置清单 | `hypothesis_4/experiment_1/init/configs/weekly_lag1_manifest.json` |
| 批次边界 | `hypothesis_4/experiment_1/runs/README.md` |
| 当前正式批说明 | `hypothesis_4/experiment_1/runs/weekly_lag1/README.md` |
| 历史归档总索引 | `ARCHIVE_MANIFEST_H4E1.md` |
| 旧9-run冻结派生结果 | `hypothesis_4/experiment_1/runs/anchored_v1/_derived/` |
| 多数据源清单 | `presentation/hypothesis_4/data/analysis_sources.json` |

---

**本README状态更新：2026-09-28。** `weekly_lag1`已完成并通过复核；当前聚合分析只覆盖同步重跑的interest/random两臂，论文数值须待图表与论断审核后更新。
