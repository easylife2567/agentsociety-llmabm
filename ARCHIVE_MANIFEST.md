# AgentSociety 工作区归档说明

**归档日期**：2026-09-12
**归档内容**：工程文件 + 实验设计 + 原始资料 + 第一次烟测全量数据
**工作区根目录**：`/Users/easylife/Project/AgentSociety`

---

## 一、归档范围

### 1. 工程文件（自研代码与工作区状态）

| 路径 | 说明 |
|------|------|
| `custom/agents/` | 自研 Agent：`curation_discourse_agent.py`、`curation_personas.py` |
| `custom/envs/` | 自研环境模块：`curation_dynamics_space.py`（含进程内确定性哈希 embedding 补丁） |
| `custom/envs/curation_assets/` | 环境资产：`injection_posts.json`(70M)、`vocabs.json`、`build_assets.py` |
| `hypothesis_4/experiment_1/*.py` | 实验脚本：`run_batch.py`(批量调度)、`monitor.py`(监视)、`plot_run_charts.py`(绘图)、`calibrate_speak.py`(说话率校准) |
| `hypothesis_4/experiment_1/init/` | 运行配置：`init_config.json`、`steps.yaml`、`config_params.py`、`configs/`、`injection_sample_s{0,1,2}.json` |
| `.agentsociety/` | 流水线状态：`progress.json`、`bin/ags.py`、`env_modules/`、`skill-presets.json` |
| `.claude/` | 工作区技能包（skill bundle） |
| `.env` | 环境变量（**含有效 API Key，见第五节注意事项**） |
| `.git/` | 工作区提交历史（**本机唯一副本，无远端**） |
| `agentsociety_data/` | 引擎 codegen router 缓存 |
| `.mcp.json`、`.vscode/`、`easypaper_config.yaml` | 工具链配置 |
| `CLAUDE.md`（`AGENTS.md` 为其符号链接） | 工作区操作规范 |

### 2. 实验设计

| 路径 | 说明 |
|------|------|
| `TOPIC.md` | 研究主题与目标 |
| `TOPIC_1788166337268_0_u31u.md` | 早期主题稿 |
| `实验设计阶段.md` | 实验设计阶段记录 |
| `EXPERIMENT_CONSTITUTION_1788335113228_0_gm0h.md` | 实验宪法（设计约束总纲） |
| `PARAMETERS.md` | 参数设定总表（决策模型四参数 + 类型规格 + 校准、env 涌现环境 K_a/K_f/β/σ、排序/feed 参数、实验设计与注入预算、来源索引） |
| `hypothesis_4/HYPOTHESIS.md` | H4 假设正文 |
| `hypothesis_4/SIM_SETTINGS.json` | 模块挂载声明（`CurationDiscourseAgent` / `CurationDynamicsSpace`） |
| `hypothesis_4/benchmark_curves.json` | 真实数据基准曲线 |
| `hypothesis_4/experiment_1/EXPERIMENT.md` | E1 实验设计 |
| `DATA_MINING_REVIEW.md`、`data_mining_report_*.md` | 数据挖掘评审与报告 |

### 3. 原始资料

| 路径 | 大小 | 说明 |
|------|------|------|
| `抖音微博小红书-全量已打标.xlsx` | 82M | 三平台全量已打标原始数据 |
| `datasets/zhangxf_labeled/` | 30M | 张雪峰事件标注数据集：`valid_posts_clusters.parquet`、`cluster_profiles.json`、`meme_stats.json`、聚类与匹配脚本、`CLUSTERS.md` |
| `research/停止更新公众人物的算法推荐与公众认知/` | 56M | 研究档案：phase1 问题界定、phase2 文献调研（含文献全文 PDF）、phase3 综合分析、研究日志 |
| `papers/` | 5.8M | CNKI 导出、精读笔记、`literature_index.json`、相关性分类 |
| `output/reports/` | — | AgentSociety2 论文精读报告 |
| `词表_{哀悼型,教育型,玩梗型,营销型}_最终版.md` | — | 四类话语词表 |
| `图表解读.docx` | 1.8M | 图表解读文档 |
| `AgentSociety 2- An Integrated Research Environment for Executable Social Science.pdf` | 21M | 引擎论文 |

### 4. 第一次烟测全量数据

**Run ID**：`interest_normal_s0`（`hypothesis_4/experiment_1/runs/` 下唯一 run）

| 项 | 值 |
|----|-----|
| experiment_id | `h4e1_interest_normal_s0` |
| 规模 | 100 agents（record-based） |
| 步数 | 11 步，`tick=604800`（1 周/步） |
| 仿真时间 | 起始 `2026-06-01T00:00:00` |
| 运行区间 | 2026-09-11 12:40:07 → 15:24:09（约 2h44m） |
| 终态 | `status: completed`、`terminated: false`、`completed_step_count: 1` |

| 路径 | 说明 |
|------|------|
| `runs/interest_normal_s0/replay/` | 全量 agent 状态回放日志（`.jsonl`） |
| `runs/interest_normal_s0/agents/agent_*/` | 100 个 agent 的 `AGENT.json` + `config.json` |
| `runs/interest_normal_s0/env/CurationDynamicsSpace/` | 环境模块落盘状态 |
| `runs/interest_normal_s0/artifacts/`、`trace/` | 产物与执行 trace |
| `runs/interest_normal_s0/SOCIETY.json` | 社会快照（190K） |
| `runs/interest_normal_s0/{engine.log,console.out,pid.json,SOCIETY_STEP.json}` | 运行日志与控制状态 |
| `experiment_1/data/weekly_*.csv` | 6 张周度指标表：`benchmark`、`mechanism`、`bias`、`supply`、`agent_behavior`、`exposure` |
| `experiment_1/charts/*.png` | 5 张关键图：`chart1` 梗占比仿真 vs 真实、`chart2` 周度供给量、`chart3` 供给堆叠面积、`chart3b` Agent 发帖量堆叠面积、`chart4` 玩梗型说话率 |
| `experiment_1/monitor/` | 监视快照：`overview.md`、`overview.json`、`run/` |
| `experiment_1/smoke_interest_normal_s0.log`、`smoke_watchdog.log` | 烟测与看门狗日志 |

---

## 二、未归档内容（及原因）

| 排除项 | 大小 | 原因 |
|--------|------|------|
| `AgentSociety2/` | 3.9G | 引擎为上游 fork（工作区干净、可重新 clone）；`.venv`(1.1G) / `node_modules`(2.2G) / `.git`(360M) 含绝对路径，跨机不可用。**按归档需求排除。** |
| `.ccb/` | 1.0G | CCB agent 运行时状态与缓存（含嵌套 git 仓库），可重建 |
| `.playwright-mcp/` | 11M | 浏览器自动化临时截图 |
| `__pycache__/`、`*.pyc`、`.DS_Store` | — | 构建产物与系统文件 |

**恢复引擎**：
```bash
git clone https://github.com/easylife2567/AgentSociety.git AgentSociety2
cd AgentSociety2 && uv sync && npm --prefix extension install && npm --prefix frontend install
```

---

## 三、还原方式

```bash
tar -xzf AgentSociety_H4E1_smoke1_20260912.tar.gz
cd AgentSociety
# 引擎按第二节恢复；随后按 .env 的 PYTHON_PATH 指向的 venv 运行
```

---

## 四、烟测关键结论（已从归档数据复核）

**Agent 类型分布（共 100）**：`marketing` 26、`mourning` 21、`other` 20、`meme` 18、`education` 15。

**W12 首周发帖验证**（源自 `agents/agent_*/AGENT.json` 的 `decision_log`）：

| 类型 | W12 已发布 / 决策数 |
|------|--------------------|
| marketing | **26 / 26** |
| education | 4 / 15 |
| meme | 0 / 18 |
| mourning | 0 / 21 |
| other | 0 / 20 |

营销型 26 个 agent 在首周全部发言并发布，与 `weekly_supply.csv` 的 `supply_share_all_marketing=0.83`(W12) 一致；玩家流回路由 0 启动。

**运行完整性**：`pid.json` 记 `status: completed`，`engine.log` 记 `Experiment completed successfully`，11/11 步执行完毕。`SOCIETY_STEP.json` 的 `completed_step_count: 1` 是落盘语义差异，**非**运行中断。

---

## 五、注意事项

⚠️ **`.env` 内含有效 API Key**（`AGENTSOCIETY_LLM_API_KEY`、`AGENTSOCIETY_CODER_LLM_API_KEY`、`AGENTSOCIETY_EMBEDDING_API_KEY`、`LITERATURE_SEARCH_API_KEY`）。**外发本压缩包前务必移除或轮换这些密钥。**

⚠️ `.git/` 是工作区提交历史的**本机唯一副本**（无 remote），已一并归档以免审计线索丢失。若仅需交付代码现状，可重新打包并排除 `.git/`，体积由约 500M 降至约 270M。
