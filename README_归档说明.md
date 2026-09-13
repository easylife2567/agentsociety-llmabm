# AgentSociety 工作区归档包 — H4-E1 正式批跑

**归档日期**：2026-09-13（同日因历史改写重打）
**归档内容**：工程文件 + 实验设计 + 原始资料 + 正式实验数据（9-run 批跑全量）
**工作区 HEAD**：即完整版包内 `.git/` 的 HEAD，用 `git log -1 --format='%H %s'` 复核。
2026-09-13 曾改写历史，**旧提交号已全部失效**，对照表见根目录
`ARCHIVE_MANIFEST_H4E1_formal_20260913.md` 第四节。
**原始体积**：569 MB（19,809 个文件）／**裁剪版**：428 MB（19,768 个文件）
**上游引擎 commit**：`13e28b5e67a2a8f2f43d640ebf27859126da622e`（以 gitlink 形式钉在工作区 git 中，见第五节）

> 本包是工作区的内容快照，保留了原始相对路径，因此包内的脚本、
> 配置与文档中的相对引用（如 `<run>/../../.env`）在解包后依然成立。
>
> 本文件同时存在于工作区根目录（已入库），每次打包随之复制进包内。

---

## 零、你手里是哪个版本

| 包名 | `.git/` | `.env` | 凭据 | 定位 |
|---|---|---|---|---|
| `AgentSociety_H4E1_formal_20260913.tar.gz` | ✅ | ✅ | ❌ 无 | 本机留档（版本史唯一副本，无远端） |
| `AgentSociety_H4E1_formal_20260913_share.tar.gz` | ❌ | ❌ | ❌ 无 | 外发用裁剪版，含 `env.template` |

**两个包都不含任何真实凭据。** 历史改写已于 2026-09-13 完成并逐对象验证
（详见留痕文件第四节），所以完整版也不再是「不可外发」的。

**首次使用请先 `cp env.template .env` 并填入凭据**（模板不含任何真实密钥）。

---

## 一、这是什么实验

**命题**：公众人物去世后，算法策展如何塑造舆论场对其的数字表征。
**案例**：张雪峰，去世 2026-03-24（2026-W13）。
**设计**：100 个固定类型 agent，W12–W22 共 11 周（tick = 1 周），
3 个推荐算法臂 × 3 seed = 9 个 run：

```
random_s{0,1,2}        chronological_s{0,1,2}        interest_s{0,1,2}
```

受控比较已核对：同 seed 下三臂配置逐行 diff **只差 `recommendation_algorithm` 一行**。

---

## 二、想快速看懂结果，从这里进

| 想干什么 | 打开 |
|---|---|
| **看结论与读数** | `hypothesis_4/experiment_1/results/README.md` ← **首选入口** |
| 看主判据图 | `hypothesis_4/experiment_1/results/charts/ARM_A1_meme_share_arms_vs_real.png` |
| 看实验设计 | `hypothesis_4/experiment_1/EXPERIMENT.md`、`hypothesis_4/HYPOTHESIS.md` |
| 看参数总表 | `PARAMETERS.md` |
| 看研究主题 | `TOPIC.md`、`EXPERIMENT_CONSTITUTION_1788335113228_0_gm0h.md` |
| 复核数据 | `hypothesis_4/experiment_1/results/tables/`（57 CSV）、`data/`（周度指标表） |
| 复现 | `hypothesis_4/experiment_1/` 下的 `run_batch.py` / `verify_experiment.py` / `monitor.py` / `plot_*.py`；命令见 results/README 第 7 节 |

---

## 三、目录导航（按用户要的四类 + 留痕）

### 1. 工程文件

| 路径 | 说明 |
|---|---|
| `custom/agents/` | 自研 Agent：`curation_discourse_agent.py`、`curation_personas.py` |
| `custom/envs/curation_dynamics_space.py` | 自研环境模块（含 replay 写入器守卫，见第六节） |
| `custom/envs/curation_mechanisms.py` | 共享纯函数（沉默螺旋 D / 注意力衰减 R） |
| `custom/envs/curation_assets/` | 环境资产：`injection_posts.json`(70M)、`vocabs.json`、`build_assets.py` |
| `hypothesis_4/experiment_1/*.py` | 实验脚本：`run_batch.py` / `monitor.py` / `verify_experiment.py` / `plot_run_charts.py` / `plot_arm_charts.py` / `calibrate_speak.py` / `proxy_predict.py` / `probe_llm.py` / `type_weekly_proxy.py` |
| `.agentsociety/` | 流水线状态：`progress.json`、`bin/ags.py` |
| `.claude/` | 工作区技能包 |
| `agentsociety_data/` | 引擎 codegen router 缓存 |

### 2. 实验设计

`TOPIC.md`、`TOPIC_1788166337268_0_u31u.md`、`实验设计阶段.md`、
`EXPERIMENT_CONSTITUTION_1788335113228_0_gm0h.md`、`PARAMETERS.md`、
`DATA_MINING_REVIEW.md`、`data_mining_report_*.md`、
`hypothesis_4/HYPOTHESIS.md`、`hypothesis_4/SIM_SETTINGS.json`、
`hypothesis_4/benchmark_curves.json`、`hypothesis_4/experiment_1/EXPERIMENT.md`、
`hypothesis_4/experiment_1/init/`（`init_config.json`、`steps.yaml`、`config_params.py`、
`configs/` 9 份臂×seed 配置、`injection_sample_s{0,1,2}.json`）。

### 3. 原始资料

| 路径 | 大小 | 说明 |
|---|---|---|
| `抖音微博小红书-全量已打标.xlsx` | 82M | 三平台全量已打标原始数据 |
| `datasets/zhangxf_labeled/` | 30M | 标注数据集：`valid_posts_clusters.parquet`、`cluster_profiles.json`、`meme_stats.json`、`type_concentration.json`、聚类与匹配脚本、`CLUSTERS.md` |
| `research/停止更新公众人物的算法推荐与公众认知/` | 56M | 研究档案：phase1 问题界定 / phase2 文献调研（含全文 PDF）/ phase3 综合分析 / 研究日志 |
| `papers/` | 5.8M | CNKI 导出、精读笔记、`literature_index.json` |
| `词表_{哀悼型,教育型,玩梗型,营销型}_最终版.md` | — | 四类话语词表 |
| `图表解读.docx`、`cnki-q1-state.png` | 1.8M | 图表解读文档与配图 |
| `AgentSociety 2- An Integrated Research Environment….pdf` | 21M | 引擎论文 |
| `output/reports/` | — | AgentSociety2 论文精读报告 |

### 4. 正式实验数据（9-run 批跑）

| 路径 | 说明 |
|---|---|
| `hypothesis_4/experiment_1/runs/<arm>_s<seed>/` | 9 个 run 的引擎原始输出：`replay/`（分片 JSONL 全量状态回放）、`agents/agent_*/`（100 × `AGENT.json` + `config.json`）、`env/CurationDynamicsSpace/`、`SOCIETY.json`、`SOCIETY_STEP.json`、`pid.json`、`engine/console/stderr/stdout` 日志、`artifacts/`、`trace/` |
| `hypothesis_4/experiment_1/results/` | **结果包（冻结快照）**：`README.md` + `charts/`(49 PNG) + `tables/`(57 CSV) + `snapshots/`(19 文件) |
| `hypothesis_4/experiment_1/charts/` | 出图目录：69 PNG = 49 张正式图 + `_pre_experiment/` 20 张标定期图 |
| `hypothesis_4/experiment_1/monitor/` | 监视快照：`overview.md/json` + 逐 run `status.md/json` |
| `hypothesis_4/experiment_1/data/` | 周度指标表。逐 run 一份：`data/<arm>_s<seed>/weekly_{benchmark,mechanism,bias,supply,agent_behavior,exposure}.csv`；臂级汇总：`data/arm/{arm_weekly_summary,arm_weekly_by_type,benchmark}.csv`；另有 `data/_pre_batch_smoke/` 与代理预测 `proxy_pred_agent_supply.csv` |
| `hypothesis_4/experiment_1/*.log` | 批跑与烟测日志（含 3 并发批跑、鉴权失败、单 run 重跑） |

**验收状态**（对重跑后的数据）：

| 检查 | 结果 |
|---|---|
| `step_count` | 9/9 = 11/11 |
| `curation_dynamics_agent_state` | 9/9 = 1100 行（100 agent × 11 周） |
| `curation_dynamics_env_state` | 9/9 = 11 行 |
| `litellm` 错误 / AIMD DECREASE | 全程 0 |
| `verify_experiment.py` | 25/25 通过 |

### 5. 退役与事故留痕

| 路径 | 说明 |
|---|---|
| `hypothesis_4/experiment_1/runs_retired_writer_bug/` | 框架级竞态事故留痕（`README.md` + 被污染的 `interest_s1` 原始证据） |
| `hypothesis_4/experiment_1/runs_retired_pre_batch/` | G 机制退役前的旧设计 run |
| `hypothesis_4/experiment_1/runs_stopped_partial/` | 中途停止的部分 run |
| `hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md` | 烟测 W19 悬崖诊断 |
| `hypothesis_4/experiment_1/init/configs_retired_2factor/` | 旧的二因子设计配置 |

### 6. 版本史

`.git/`（工作区提交历史；**本机唯一副本，无远端**；**仅完整版含**）。
解包后可 `git log --oneline` 追溯全部设计裁定与留痕。

> 2026-09-13 曾用 `git filter-repo` 剔除历史中的凭据文件（`.env`、`easypaper_config.yaml`），
> 因此**所有提交号已变更**，提交数 99 → 97。旧号→新号完整映射见包内
> `.git/filter-repo/commit-map`（裁剪版无 `.git/`，见留痕文件第四节的表）。

---

## 四、还原方式

```bash
tar -xzf AgentSociety_H4E1_formal_20260913_share.tar.gz
cd AgentSociety_H4E1_formal_20260913

cp env.template .env        # 然后编辑 .env，填入凭据并改本机路径
# 引擎按第五节恢复；随后按 .env 的 PYTHON_PATH 指向的 venv 运行
```

**裁剪版不含 `.git/`**，无法用 `git log` 校验版本；**完整版含 `.git/`**，
`git log -1` 即为本包的打包提交。

---

## 五、未归档内容（及原因）

| 排除项 | 大小 | 原因 |
|---|---|---|
| `AgentSociety2/` | 3.9G | 上游引擎 fork。其中 `.venv`(1.1G) / `node_modules`(2.2G，extension+frontend) / `.git`(360M) 含绝对路径，跨机不可用。**版本已钉住**：工作区 git 以 gitlink 记录引擎 commit `13e28b5e67a2a8f2f43d640ebf27859126da622e` |
| `.git/` | 141M | **仅裁剪版特有**：工作区提交历史。体积考虑 + 完整版已承担本机留档职责 |
| `.env` | 923B | **仅裁剪版特有**：含真实 API Key，已替换为不含密钥的 `env.template` |
| `easypaper_config.yaml` | 1.8K | **仅裁剪版特有**：内含 9 处同一把 `LITERATURE_SEARCH_API_KEY`（与 `.env` 中为同一凭据）。属论文工具链配置，与本实验无关 |
| `.ccb/` | 1.0G | CCB agent 运行时状态与缓存（含嵌套 git 仓库），可重建 |
| `.playwright-mcp/` | 11M | 浏览器自动化临时截图 |

**恢复引擎**：

```bash
git clone https://github.com/easylife2567/AgentSociety.git AgentSociety2
cd AgentSociety2 && git checkout 13e28b5e67a2a8f2f43d640ebf27859126da622e
uv sync && npm --prefix extension install && npm --prefix frontend install
```

> 在**完整版**中，还原后 `git status` 会显示 1 项变更：` D AgentSociety2`
> —— 即被有意排除的引擎 gitlink，属打包的预期副作用，**不是数据丢失**。
> （`.env` 与 `easypaper_config.yaml` 在完整版中虽被包含，但已在 `.gitignore` 内，不产生状态噪声。）
> 裁剪版不含 `.git/`，无此项。

---

## 六、注意事项

✅ **两个版本都不含任何真实凭据。** `.env` 与 `easypaper_config.yaml` 已退出 git 跟踪
（提交 `a8d454c`），并从**全部历史**中改写剔除（2026-09-13，逐对象验证 3,124 个对象 0 命中），
改用无密钥的 `env.template`。首次使用请 `cp env.template .env` 并填入自己的凭据。

模板中需要你自备的项：

| 变量 | 说明 |
|---|---|
| `AGENTSOCIETY_LLM_API_KEY` | 仿真主模型 Key |
| `LITERATURE_SEARCH_API_KEY` | 文献检索 MCP Key（非必需，跑仿真用不到） |
| `PYTHON_PATH` | 本机解释器绝对路径，需能 `import agentsociety2` |
| `WORKSPACE_PATH` | 本工作区绝对路径 |

> 历史改写的**前提**是用户裁定「只改写历史、不轮换 Key」，即该 Key 从未离开本机。
> 若本包曾被外发过（改写之前的版本），应按泄露处置：轮换对应 Key。

⚠️ 框架竞态留痕：本次批跑有 2 个 run（`random_s2`、`interest_s1`）在 step 0 撞上框架级
replay 写入器竞态（写入器被覆盖为 `dict`），引擎误报 completed 而表为空。
已在 `custom/envs/curation_dynamics_space.py` 加类型守卫（拒绝非写入器对象并保留原写入器、
记录调用栈），并重跑这两个 run。事故证据留在 `runs_retired_writer_bug/`。
**本包中的 `runs/` 是重跑后的干净数据。**
