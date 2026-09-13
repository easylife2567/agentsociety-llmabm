# 归档留痕：H4-E1 正式批跑全量快照

**归档日期**：2026-09-13
**归档范围**：工程文件 + 实验设计 + 原始资料 + 正式实验数据（9-run 批跑全量）+ 退役留痕 + 版本史
**原始体积**：689 MB / 26,283 文件
**工作区 HEAD**：`ef29767`
**包内说明**：解包后根目录的 `README_归档说明.md`（含目录导航、验收状态、还原方式、注意事项）

> 上一份归档 `ARCHIVE_MANIFEST.md`（2026-09-12，第一次烟测）保留为历史记录，描述的是当时那份烟测包。

---

## 一、两个压缩包

均置于工作区根目录，按 `.gitignore:17`（`AgentSociety_*.tar.gz`）不入库。

| 文件 | 体积 | 含 `.git/` | 含真实凭据 | 用途 |
|---|---|---|---|---|
| `AgentSociety_H4E1_formal_20260913.tar.gz` | 484 MB | ✅ | ✅ | **本机留档**：完整快照，可用 `git log` 溯源 |
| `AgentSociety_H4E1_formal_20260913_share.tar.gz` | 252 MB | ❌ | ❌ | **外发用裁剪版**：剔除 `.git/`、`.env`、`easypaper_config.yaml`，改用 `env.template` |

两者的内容主体完全一致（工程 / 设计 / 原始资料 / 正式数据 / 退役留痕），差别仅在上述三项。
两个包**都整体排除了 `AgentSociety2/` 引擎源码**。

## 二、内容（解包后顶层为 `AgentSociety_H4E1_formal_20260913/`）

| 类别 | 主要路径 |
|---|---|
| 工程文件 | `custom/`（agents + envs + curation_assets）、`hypothesis_4/experiment_1/*.py`、`.agentsociety/`、`.claude/`、`agentsociety_data/` |
| 实验设计 | `TOPIC.md`、`实验设计阶段.md`、`EXPERIMENT_CONSTITUTION_*.md`、`PARAMETERS.md`、`hypothesis_4/{HYPOTHESIS.md,SIM_SETTINGS.json,benchmark_curves.json}`、`experiment_1/{EXPERIMENT.md,init/}` |
| 原始资料 | `抖音微博小红书-全量已打标.xlsx`(82M)、`datasets/zhangxf_labeled/`(30M)、`research/`(56M)、`papers/`、`词表_*.md` ×4、`图表解读.docx`、引擎论文 PDF |
| 正式实验数据 | `experiment_1/runs/`（9 run 引擎原始输出）、`results/`（49 图 / 57 表 / 19 快照）、`charts/`、`monitor/`、`data/`、全部 `.log` |
| 退役留痕 | `runs_retired_writer_bug/`、`runs_retired_pre_batch/`、`runs_stopped_partial/`、`SMOKE_DIAGNOSIS_w19_cliff.md`、`init/configs_retired_2factor/` |
| 版本史 | `.git/`（**仅完整版**；本机唯一副本，无远端） |

## 三、排除内容（及原因）

| 排除项 | 大小 | 原因 |
|---|---|---|
| `AgentSociety2/` | 3.9G | 上游引擎 fork；**按用户指示不导出源码**。排除 `node_modules`/`.venv` 后的源码与工作无关，且引擎版本已由工作区 git 的 gitlink 钉住：commit `13e28b5e67a2a8f2f43d640ebf27859126da622e` |
| `.git/` | 261M | **仅裁剪版**：含密钥历史对象，外发有泄露风险 |
| `.env` | 923B | **仅裁剪版**：含真实 API Key，改用 `env.template` |
| `easypaper_config.yaml` | 1.8K | **仅裁剪版**：见第四节 |
| `.ccb/` | 1.0G | CCB agent 运行时状态与缓存，可重建 |
| `.playwright-mcp/` | 11M | 浏览器自动化临时截图 |

**恢复引擎**（**不要在归档里分发源码**，使用者自行 clone）：

```bash
git clone https://github.com/easylife2567/AgentSociety.git AgentSociety2
cd AgentSociety2 && git checkout 13e28b5e67a2a8f2f43d640ebf27859126da622e
uv sync && npm --prefix extension install && npm --prefix frontend install
```

## 四、凭据核查（打包时新发现，需留意）

打包前做的全树扫描发现：**`.env` 不是工作区里唯一的凭据副本**。

`easypaper_config.yaml`（工作区根目录，1.8K，**被 git 跟踪**）内含 **9 处 API Key**，
经哈希比对，9 处**是同一把**，且与 `.env` 的 `LITERATURE_SEARCH_API_KEY` **完全同值**
（sha256 前 12 位 `dfcadb86a027`）。也就是说只删 `.env` 并不能挡住它，**只裁剪 `.env` 的归档仍会泄露**。

处理：裁剪版已将 `easypaper_config.yaml` 一并剔除。全树复扫（`sk-` 模式 + 6383 个小配置文件的
凭据字段扫描）确认**再无其他副本**（另有 1 处 `sk-` 命中是文献正文里的 `algorithm-task-...`，误报）。

**已处置（提交 `a992daa`）**：`.env` 与 `easypaper_config.yaml` 均已 `git rm --cached` 退出跟踪，
`.gitignore` 新增凭据段（磁盘文件保留，运行时不受影响），并新增无密钥的 `env.template`。

> **仍未消除的风险**：退出跟踪只影响**后续**提交。旧值仍在历史对象里
> ——`.env` 自首个提交 `f545289`（2026-08-18 bootstrap）起就在库中，共 14 个提交涉及。
> 彻底断掉需二选一或都做：**① 轮换 `LITERATURE_SEARCH_API_KEY`**（推荐，最省事且不动审计线索）；
> **② `git filter-repo` 改写历史**（会重写全部 98 个提交的 SHA，本包正文中引用的
> `ef29767` 等提交号将失效，需同步重新打包）。
>
> **另注**：完整版 `AgentSociety_H4E1_formal_20260913.tar.gz` 内含 `.git/`（6818 条目），
> 因此**该压缩包本身携带密钥历史**，不可外发。

## 五、校验（均实测，非推断）

| 项 | 完整版 | 裁剪版 |
|---|---|---|
| `gzip -t` CRC | ✅ | ✅ |
| 解包体积 | 689 MB | 428 MB |
| 归档条目 | 30,110 | 23,291 |
| `git log` 可溯源 | ✅ `ef29767` | —（无 `.git/`） |
| 引擎源码残留 | 0 | 0 |
| 9 run 数据 | 各 100 agent + 335–344 replay 分片 | 同 |
| `results/` | 49 图 / 57 表 / 19 快照 | 同 |
| 符号链接 `AGENTS.md -> CLAUDE.md` | ✅ 保留 | ✅ 保留 |
| AppleDouble 垃圾 | 无 | 无 |
