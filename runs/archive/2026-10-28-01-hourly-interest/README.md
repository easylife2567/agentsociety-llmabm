# 三臂小时回流与兴趣组件消融：已归档

## 归档结果（2026-10-30）

用户已明确授权归档全部根级 run。本 run 的小时回流机制、两臂各10 seed运行与三臂对照分析已完成，主实验选定成果已于2026-10-29正式采用；本次归档未新增实验或改变正式代码、配置、数据、预算和研究流水线。

归档前在新的空目录从准确基线独立恢复：78份候选文件、76份文件镜像及21份冻结技能哈希一致；42项测试通过，60份配置及600份 profile（Agent配置）创建/恢复通过，网络、LLM、Agent行动、环境步骤及Ray启动均为0。已逐项保全原 worktree 中10份已跟踪差异、18,550份未跟踪文件和16份被忽略文件；未知资产为0，随后使用不带 `--force` 的 `git worktree remove` 安全解除登记。详情见[归档验收](evidence/archive/README.md)。

旧位置 `runs/2026-10-28-01-hourly-interest/` → 当前 `runs/archive/2026-10-28-01-hourly-interest/`。原始 manifest、checkpoint、日志、预算账本、合同与恢复镜像中的历史路径保持原字节；旧 `workspace/` 已解除登记，恢复缓存已清理。归档前的完整工作记录保存在[历史README](evidence/archive/navigation_before_archive/README.md)。

## 已采用与未采用部分

已采用两份环境机制补丁、小时回流测试、experiment_2主配置30份、新随机/兴趣20份完整原始结果和历史时序10份复用矩阵，以及正式分析、图表和综合。正式入口为[experiment_2](../../../hypothesis_4/experiment_2/README.md)、[小时回流分析](../../../presentation/hypothesis_4/hourly_return_v1/README.md)及[综合说明](../../../synthesis/hourly_return_v1.md)；正式运行及复算独立于本归档的私有路径。选择性落地及正式位置42项测试、30配置/3000 profile和30 run分析的记录见[adoption/](adoption/README.md)。

experiment_3小时回流候选配置及同时准备两实验的生成器未正式采用，未运行新版组件消融；旧组件消融和旧结果保留原身份。本 run 未修改论文正文；[正文影响评估](../../../presentation/hypothesis_4/hourly_return_v1/manuscript_impact.md)保存当时的评估边界。归档不扩大采用范围。

## 原始证据保全

本地保留三个被 Git 忽略的原始镜像目录，共 **18,595份文件 / 667,677,725字节（636.75 MiB，逻辑大小）**：

| 目录 | 保留内容 | 文件数 | 字节 |
|---|---|---:|---:|
| pilot/results/ | 已完成随机/兴趣 seed0和用户撤回的时序部分现场 | 2,338 | 66,854,082 |
| seed_extension/results/ | 随机/兴趣 seed1–9共18份完整现场 | 16,141 | 571,026,306 |
| pilot/agent_supply/inputs/chronological_s0/ | 三臂单seed比较冻结的历史时序原始样本 | 116 | 29,797,337 |

前两个目录共21份快照、18,477文件，其 SHA256 全部与原始清单一致，第三目录及三臂分析的120项冻结来源亦逐项核对。原始数据不会因被忽略而删除，也不会强制加入 Git；Git 保存代码、报告、恢复材料和校验清单。Git 克隆不含这些本地原始镜像，迁移至另一台机器须另行复制三个目录并运行完整哈希检查。

原始与待提交元数据扫描没有发现 `.env`、认证值或密钥形状；7个名为 `authorization` 的字段均为中文用户授权范围文字，核对记录只列路径和字段名。最大原始文件为 `seed_extension/results/hourly_return_v1_random_s7/env/CurationDynamicsSpace/state/ENV_STATE.json`，25,917,496字节。无仍占用本 run 的仿真、控制器进程或打开句柄；历史 PID 不再作为操作入口。

## 离线恢复与复验

准确代码基线为 `aad3267fc9929a08a453ba427bdf25919bbffc70`。恢复顺序为 Git基线导出 → `mechanism.patch` 检查/应用 → 76份最终文件及21份冻结技能复制 → 78份候选哈希核对 → 配置与功能验证。运行时为项目已安装的 Python 3.13.9 / AgentSociety2 2.8.4，SDK commit 为 `13e28b5e67a2a8f2f43d640ebf27859126da622e`；不联网安装，不依赖已移除 worktree 或主工作区未提交改动。

从项目根目录使用现有解释器；`TASK_WS` 必须是尚不存在的目录，`--repo .` 必须显式给出：

```bash
TASK_RUN=runs/archive/2026-10-28-01-hourly-interest
TASK_WS="$TASK_RUN/tmp/recheck_clean"
TASK_PYTHON=$(sed -n 's/^PYTHON_PATH=//p' .env)
PYTHONDONTWRITEBYTECODE=1 "$TASK_PYTHON" "$TASK_RUN/verify_archive.py" --repo .
PYTHONDONTWRITEBYTECODE=1 "$TASK_PYTHON" "$TASK_RUN/restore_candidate.py" --repo . --destination "$TASK_WS" --output "$TASK_RUN/evidence/recheck_restore.json"
PYTHONDONTWRITEBYTECODE=1 "$TASK_PYTHON" "$TASK_WS/hypothesis_4/experiment_2/init/prepare_hourly_return.py" --check
PYTHONDONTWRITEBYTECODE=1 "$TASK_PYTHON" "$TASK_RUN/verify_tests.py" --workspace "$TASK_WS" --output "$TASK_RUN/evidence/recheck_tests.json"
PYTHONDONTWRITEBYTECODE=1 "$TASK_PYTHON" "$TASK_RUN/verify_candidate.py" --workspace "$TASK_WS" --output "$TASK_RUN/evidence/recheck_configs.json"
```

只有 Git 恢复材料、未另行复制本地原始镜像时，用 `verify_archive.py --repo . --metadata-only` 核对恢复包；该模式明确不检查原始实验数据。旧 `pilot/`、`seed_extension/` 控制器及旧 `analysis/analyze_seed10.py` 保留为当时的执行源码，包含历史绝对路径，不作为归档后的启动/复算入口。当前正式分析使用上述正式分析目录，本归档原始保全使用相对路径的 `verify_archive.py`。

## 本级资产

| 资产 | 用途 |
|---|---|
| [README.md](README.md) | 归档状态、采用边界与恢复入口 |
| [.gitignore](.gitignore) | 忽略workspace/tmp及三个本地原始目录 |
| [baseline.json](baseline.json) | 开始时Git基线、主工作区状态与保护哈希 |
| [mechanism.patch](mechanism.patch) | 两份既有环境源码的最终补丁 |
| [recovery_manifest.json](recovery_manifest.json) | 76份镜像、78份候选、21份技能和恢复依赖 |
| [files/](files/) | 候选代码/配置/设计文档最终镜像，保持原哈希 |
| [fixtures/](fixtures/README.md) | 回归所需最小历史输入与来源 |
| [validation_skills/](validation_skills/) | 离线验收必需技能的实体冻结副本 |
| [restore_candidate.py](restore_candidate.py) | 按准确基线独立恢复；显式传入 `--repo .` |
| [verify_tests.py](verify_tests.py) | 42项功能检查，禁网运行 |
| [verify_candidate.py](verify_candidate.py) | 60配置/600 profile及实际模块验收 |
| [verify_archive.py](verify_archive.py) | 按当前相对位置核对恢复材料及本地原始SHA |
| [evidence/](evidence/README.md) | 初次失败、验收、独立恢复与本轮归档证据 |
| [pilot/](pilot/README.md) | seed0执行历史、原始镜像、观察与三臂对照 |
| [seed_extension/](seed_extension/README.md) | 随机/兴趣seed1–9执行历史、原始镜像与收尾 |
| [analysis/](analysis/README.md) | 三臂各10seed分析、DTW、图表与来源 |
| [adoption/](adoption/README.md) | 已采用主实验的正式落地与验收材料 |

本次仅归档并更新本级导航和证据，没有启动历史控制器、社会仿真或模型请求，也没有改变机器流水线状态。共享索引、提交与推送由上级归档任务统一完成。
