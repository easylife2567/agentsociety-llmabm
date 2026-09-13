# 归档留痕：H4-E1 正式批跑全量快照

**归档日期**：2026-09-13
**压缩包**：`AgentSociety_H4E1_formal_20260913.tar.gz`（484 MB，工作区根目录，按 `.gitignore` 不入库）
**归档范围**：工程文件 + 实验设计 + 原始资料 + 正式实验数据（9-run 批跑全量）+ 退役留痕 + 版本史
**原始体积**：689 MB / 26,283 文件
**工作区 HEAD**：`ef29767`
**包内说明**：解包后根目录的 `README_归档说明.md`（含目录导航、验收状态、还原方式、注意事项）

> 上一份归档 `ARCHIVE_MANIFEST.md`（2026-09-12，第一次烟测）仍保留，是历史记录，描述的是当时那份烟测包。

---

## 一、内容（解包后顶层为 `AgentSociety_H4E1_formal_20260913/`）

| 类别 | 主要路径 |
|---|---|
| 工程文件 | `custom/`（agents + envs + curation_assets）、`hypothesis_4/experiment_1/*.py`、`.agentsociety/`、`.claude/`、`agentsociety_data/` |
| 实验设计 | `TOPIC.md`、`实验设计阶段.md`、`EXPERIMENT_CONSTITUTION_*.md`、`PARAMETERS.md`、`hypothesis_4/{HYPOTHESIS.md,SIM_SETTINGS.json,benchmark_curves.json}`、`experiment_1/{EXPERIMENT.md,init/}` |
| 原始资料 | `抖音微博小红书-全量已打标.xlsx`(82M)、`datasets/zhangxf_labeled/`(30M)、`research/`(56M)、`papers/`、`词表_*.md` ×4、`图表解读.docx`、引擎论文 PDF |
| 正式实验数据 | `experiment_1/runs/`（9 run 引擎原始输出）、`results/`（49 图 / 57 表 / 19 快照）、`charts/`、`monitor/`、`data/`、全部 `.log` |
| 退役留痕 | `runs_retired_writer_bug/`、`runs_retired_pre_batch/`、`runs_stopped_partial/`、`SMOKE_DIAGNOSIS_w19_cliff.md`、`init/configs_retired_2factor/` |
| 版本史 | `.git/`（本机唯一副本，无远端） |

## 二、排除内容（及原因）

| 排除项 | 大小 | 原因 |
|---|---|---|
| `AgentSociety2/` | 3.9G | 上游引擎 fork；`.venv`/`node_modules`/`.git` 含绝对路径，跨机不可用。**版本已钉住**：工作区 git 以 gitlink 记录引擎 commit `13e28b5e67a2a8f2f43d640ebf27859126da622e` |
| `.ccb/` | 1.0G | CCB agent 运行时状态与缓存，可重建 |
| `.playwright-mcp/` | 11M | 浏览器自动化临时截图 |

## 三、校验（解包后复核）

```bash
tar -xzf AgentSociety_H4E1_formal_20260913.tar.gz && cd AgentSociety_H4E1_formal_20260913
git log --oneline -1        # 应为 ef29767
git status --porcelain      # 应只剩 " D AgentSociety2"（有意排除，非数据丢失）
```

已实测：`gzip -t` CRC 通过；解包 689 MB；9 个 run 各 100 agent + 335–344 replay 分片；
`results/` 49 图 / 57 表 / 19 快照；`AGENTS.md -> CLAUDE.md` 符号链接保留；
无 AppleDouble 垃圾。

## 四、注意事项

⚠️ **`.env` 内含有效 API Key**，该文件在工作区 git 中一直被跟踪，故密钥同样存在于 `.git/` 历史对象里。
**外发前请移除 `.env` 或轮换密钥**；无法轮换时应改为分发不含 `.git/` 的裁剪版。
