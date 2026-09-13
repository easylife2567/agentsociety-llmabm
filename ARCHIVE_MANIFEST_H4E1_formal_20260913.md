# 归档留痕：H4-E1 正式批跑全量快照

**归档日期**：2026-09-13（同日因历史改写重打一次）
**归档范围**：工程文件 + 实验设计 + 原始资料 + 正式实验数据（9-run 批跑全量）+ 退役留痕 + 版本史
**工作区 HEAD**：打包时的 `main`（2026-09-13 历史改写后，提交号已全部变更）——包内 `.git/` 可用
`git log -1 --format='%H %s'` 查看；与旧号的对照见第四节
**原始体积**：569 MB / 19,809 文件（上一版为 689 MB / 26,283 文件，减少的 120 MB 全部来自
`.git` 从 261 MB 瘦身到 141 MB —— 松散对象被 gc 打包，**内容零丢失**，见第五节）
**包内说明**：解包后根目录的 `README_归档说明.md`（含目录导航、验收状态、还原方式、注意事项）

> 上一份归档 `ARCHIVE_MANIFEST.md`（2026-09-12，第一次烟测）保留为历史记录，描述的是当时那份烟测包。

---

## 一、两个压缩包

均置于工作区根目录，按 `.gitignore:23`（`AgentSociety_*.tar.gz`）不入库。

| 文件 | 解包体积 | 含 `.git/` | 含真实凭据 | 用途 |
|---|---|---|---|---|
| `AgentSociety_H4E1_formal_20260913.tar.gz` | 569 MB | ✅（141 MB） | ❌ | **本机留档**：完整快照，可用 `git log` 溯源 |
| `AgentSociety_H4E1_formal_20260913_share.tar.gz` | 428 MB | ❌ | ❌ | **外发用裁剪版**：剔除 `.git/`、`.env`、`easypaper_config.yaml`，改用 `env.template` |

两者的内容主体完全一致（工程 / 设计 / 原始资料 / 正式数据 / 退役留痕），差别仅在上述三项。
两个包**都整体排除了 `AgentSociety2/` 引擎源码**。

> **与上一版的关键差异**：因历史已改写（第四节），**完整版的 `.git/` 现在也不再含任何凭据**，
> 即两个包**都可以外发**。完整版仍建议本机留档，理由是它是版本史的唯一副本（无远端）。

## 二、内容（解包后顶层为 `AgentSociety_H4E1_formal_20260913/`）

| 类别 | 主要路径 |
|---|---|
| 工程文件 | `custom/`（agents + envs + curation_assets）、`hypothesis_4/experiment_1/*.py`、`.agentsociety/`、`.claude/`、`agentsociety_data/` |
| 实验设计 | `TOPIC.md`、`实验设计阶段.md`、`EXPERIMENT_CONSTITUTION_*.md`、`PARAMETERS.md`、`hypothesis_4/{HYPOTHESIS.md,SIM_SETTINGS.json,benchmark_curves.json}`、`experiment_1/{EXPERIMENT.md,init/}` |
| 原始资料 | `抖音微博小红书-全量已打标.xlsx`(82M)、`datasets/zhangxf_labeled/`(30M)、`research/`(56M)、`papers/`、`词表_*.md` ×4、`图表解读.docx`、`cnki-q1-state.png`、引擎论文 PDF |
| 正式实验数据 | `experiment_1/runs/`（9 run 引擎原始输出）、`results/`（49 图 / 57 表 / 19 快照）、`charts/`、`monitor/`、`data/`、全部 `.log` |
| 退役留痕 | `runs_retired_writer_bug/`、`runs_retired_pre_batch/`、`runs_stopped_partial/`、`SMOKE_DIAGNOSIS_w19_cliff.md`、`init/configs_retired_2factor/` |
| 版本史 | `.git/`（**仅完整版**；本机唯一副本，无远端） |

## 三、排除内容（及原因）

| 排除项 | 大小 | 原因 |
|---|---|---|
| `AgentSociety2/` | 3.9G | 上游引擎 fork；**按用户指示不导出源码**。排除 `node_modules`/`.venv` 后的源码与工作无关，且引擎版本已由工作区 git 的 gitlink 钉住：commit `13e28b5e67a2a8f2f43d640ebf27859126da622e` |
| `.git/` | 141M | **仅裁剪版**：提交历史（现已不含凭据，见第四节）。裁剪版剔除它主要是体积与「无远端、本机留档」的定位考虑 |
| `.env` | 923B | **仅裁剪版**：含真实 API Key，已改用 `env.template` |
| `easypaper_config.yaml` | 1.8K | **仅裁剪版**：内含 9 处与 `.env` 同值的 API Key（见第四节） |
| `.ccb/` | 1.0G | CCB agent 运行时状态与缓存，可重建 |
| `.playwright-mcp/` | 11M | 浏览器自动化临时截图 |

**恢复引擎**（**不要在归档里分发源码**，使用者自行 clone）：

```bash
git clone https://github.com/easylife2567/AgentSociety.git AgentSociety2
cd AgentSociety2 && git checkout 13e28b5e67a2a8f2f43d640ebf27859126da622e
uv sync && npm --prefix extension install && npm --prefix frontend install
```

## 四、凭据处置（本次打包新发现 + 已彻底断掉）

打包前的全树扫描发现：**`.env` 不是工作区里唯一的凭据副本**。

`easypaper_config.yaml`（工作区根目录，1.8K，**被 git 跟踪**）内含 **9 处 API Key**，
经哈希比对，9 处**是同一把**，且与 `.env` 的 `LITERATURE_SEARCH_API_KEY` **完全同值**
（sha256 前 12 位 `dfcadb86a027`）。也就是说只删 `.env` 并不能挡住它，**只裁剪 `.env` 的归档仍会泄露**。
全树复扫（`sk-` 模式 + 6383 个小配置文件的凭据字段扫描）确认**再无其他副本**
（另有 1 处 `sk-` 命中是文献正文里的 `algorithm-task-...`，误报）。

处置分两步：

**① 退出跟踪 —— 提交 `a8d454c`**（旧号 `a992daa`）
`.env` 与 `easypaper_config.yaml` 均 `git rm --cached` 退出跟踪，`.gitignore` 新增凭据段
（磁盘文件保留，运行时不受影响），新增无密钥的 `env.template` 作模板。

**② 改写历史 —— 用户 2026-09-13 裁定「只改写历史，不轮换」**
用 `git filter-repo --invert-paths --path .env --path easypaper_config.yaml` 从**全部提交**中剔除这两个路径：

- `.env` 自首个提交 `1ddb575`（旧号 `f545289`，2026-08-18 bootstrap）起即在库中，共 14 个提交涉及
- 提交数 **99 → 97**（另有 2 个空提交被一并裁掉），**全部 SHA 重写**
- 改写前做完整备份；改写后按「枚举每个对象、逐字节搜索凭据值」验证：**3,124 个对象，0 命中**
  （验证脚本只在内存中比对，从不打印凭据值）
- 一个**容易漏掉的坑**：`refs/codex/turn-diffs/*` 两棵树引用未被 filter-repo 覆盖
  （工具输出 `Unexpected object of type tree, skipping`），而这两棵树里**确实含 `.env` 与
  `easypaper_config.yaml`** —— 若直接 gc，凭据会因这些引用而存活。已先将其内容（**去掉两个凭据文件**）
  导出为 `codex_trees_sanitized.tar.gz` 保全，再删除这两个引用，最后
  `git reflog expire --expire=now --all` + `git gc --prune=now`
- 结果：`.git` 261 MB → 141 MB（pack 117.75 MiB），对象数 3,128 → 3,124
- 复验：`git log --all -- .env` = 0 条，`git log --all -- easypaper_config.yaml` = 0 条，
  `git rev-list --objects --all | grep` = 0 命中

**旧号 → 新号对照**（完整映射见包内 `.git/filter-repo/commit-map`）：

| 改写前 | 改写后 | 提交说明 |
|---|---|---|
| `f545289` | `1ddb575` | `init: bootstrap research workspace`（首个提交，`.env` 自此在库中） |
| `c2d8fb9` | `82fdc3c` | `h4e1: 9-run 批跑收尾 —— 9/9 完成 + 快照/图表产出`（`results/` 冻结快照对应版本） |
| `3eedd96` | `7209449` | `h4e1: replay 写入器守卫 + interest_s1 事故归档` |
| `759073c` | `607db2d` | `h4e1: 全量归档打包……`（上一版完整包） |
| `ef29767` | `5d241fd` | `h4e1: 整理实验结果包 results/……`（上一版留痕记录的工作区 HEAD） |
| `0116a04` | `5cdb9ae` | `h4e1: 归档裁剪版……`（上一版裁剪包） |
| `a992daa` | `a8d454c` | `security: .env 与 easypaper_config.yaml 退出 git 跟踪` |
| `9740db9` | `c717cbe` | `docs: 归档留痕补记凭据处置结果与剩余风险` |

> **风险仍存的部分**：改写只清除了**本机 git 库中的旧值**。用户裁定不轮换该 Key，
> 前提是它从未离开本机（该 Key 仅出现在 `.env` 与 `easypaper_config.yaml`，两者都只在本机，
> 且两个包现已都不含它）。**改写前的备份仍留在本机** `/tmp/h4e1_git_backup/`
> （`pre_rewrite_all.bundle` 124M 等），其中含旧值 —— 确认无需回滚后应删除。

## 五、校验（均实测，非推断）

| 项 | 完整版 | 裁剪版 |
|---|---|---|
| `gzip -t` CRC | ✅ | ✅ |
| 解包体积 | 569 MB | 428 MB |
| 归档条目 | 见下 | 见下 |
| 非 `.git` 文件数 | 19,770 | 19,768 |
| `git log` 可溯源 | ✅（包内 `.git`，`git log -1` 可得 HEAD） | —（无 `.git/`） |
| 引擎源码残留 | 0 | 0 |
| 9 run 数据 | 各 100 agent + 335–344 replay 分片 | 同 |
| `results/` | 49 图 / 57 表 / 19 快照 | 同 |
| 符号链接 `AGENTS.md -> CLAUDE.md` | ✅ 保留 | ✅ 保留 |
| AppleDouble 垃圾 | 无 | 无 |

> 两版非 `.git` 文件数相差 2，正是 `.env` 与 `easypaper_config.yaml` —— 即**裁剪版恰好只少了这两个凭据文件**。
> 上一版体积差（689 → 569 MB）为 120 MB，恰好等于 `.git` 瘦身量（261 → 141 MB），**内容零丢失**。
