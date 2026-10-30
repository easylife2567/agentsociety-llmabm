# 小时回流run归档验收（2026-10-30）

[上级run入口](../../README.md)集中说明当前归档状态、正式采用范围及离线恢复命令。本级保存归档动作的实际证据；原始运行合同、状态、日志及哈希未重写。

## 实际结果

| 检查 | 结果与证据 |
|---|---|
| 独立恢复 | [restore.json](restore.json)与[日志](restore.log)：新空目录、基线aad3267、补丁check/apply、76份镜像、78份候选哈希通过；不依赖原workspace |
| 配置重算 | [generator_check.log](generator_check.log)：恢复目录的prepare_hourly_return.py --check通过 |
| 功能验证 | [tests.json](tests.json)与[日志](tests.log)：42测试、0失败/错误/跳过、0网络/LLM |
| 官方配置/profile | [config_validation.json](config_validation.json)与[日志](config_validation.log)：60配置、600 profile创建恢复通过；Agent行动、环境步骤、Ray、网络、LLM均0 |
| 原始镜像迁移前核对 | [raw_before_move.json](raw_before_move.json)：21快照、18,477数据文件与120项三臂冻结来源SHA一致 |
| 原worktree保全/解除登记 | [worktree_retirement.json](worktree_retirement.json)：10 tracked、18,550 untracked、16 ignored均分类；未知资产0、无占用；不带--force移除成功 |
| 原资产迁移后核对 | [verify_after_move.json](verify_after_move.json)：18,997份原资产SHA一致，原始历史路径字节保持；恢复包、原始数据和冻结分析来源通过 |
| Git克隆复验模式 | [verify_metadata_only.json](verify_metadata_only.json)：恢复材料通过，raw_checked=false；该模式未检查本地原始镜像 |
| 原始凭据扫描 | [raw_credential_scan.json](raw_credential_scan.json)：11,530个原始文本文件，非空认证字段、密钥形状和.env均0；未输出值 |
| 待提交材料预检 | [commit_preflight.json](commit_preflight.json)：7个authorization字段均为人类任务授权范围文字；未发现认证值。历史压缩现场的139份文件另经[包内扫描](archive_package_credential_scan.json)通过 |
| 最终状态 | [final_state.json](final_state.json)：已归档、原worktree已解除登记、未改正式资产/预算/流水线、未commit/push |

本次验证使用项目既有Python 3.13.9 / AgentSociety2 2.8.4。独立恢复发生在旧位置的新空目录 `tmp/archive_check_clean`，全部验收后对缓存逐项分类并清理，因此日志保留其真实旧路径。归档后从新位置实际运行 `verify_archive.py --repo .` 和 `--metadata-only` 均通过。

## 保全与清理范围

原worktree的18,550个未跟踪文件分为18,477原始输出、68个候选文件、5个小型验证输出，全部与本级或既有恢复镜像逐项SHA匹配。10份已跟踪差异按78份候选哈希核对，并另保存完整[最终差异备份](workspace_final_before_retirement.patch)；16份被忽略文件为15个Python缓存和1份已有冻结夹具。逐项路径/哈希/去向清单见[压缩清单](workspace_inventory.json.gz)，小型验证原件见[workspace_validation/](workspace_validation/)，映射见[workspace_validation_manifest.json](workspace_validation_manifest.json)。只在全部保全后恢复这10份已跟踪文件、删除已分类重复文件，随后执行 `git worktree remove`，没有使用reset、全局clean或--force。

成功恢复缓存中的文件均可由准确Git基线/候选镜像/冻结技能/夹具复现；独有的5份小型验证输出分别保存在[旧恢复验证](previous_recovery_validation/)与[本轮恢复验证](current_recovery_validation/)。首次失败恢复现场和两份小型中间候选目录整体保存在[历史准备压缩包](historical_preparation_tmp.tar.gz)；成员166项，其中139份文件，包含安全解包拒绝的真实失败现场。分类与压缩包SHA见[tmp_preservation.json](tmp_preservation.json)。只清理了这5个已逐项核对/保全的临时目录，没有删除原始镜像。

三个本地原始目录仍受 `.gitignore` 排除，合计 **18,595文件 / 667,677,725字节（636.75 MiB，逻辑大小）**，其中两份目录README也计入目录总数。21份run数据清单为18,477文件，历史时序输入快照另有116文件。所有镜像随run一并迁移到当前路径，没有强制添加到Git。原始最大文件25,917,496字节。`.env`继承项目忽略规则，本归档没有.env。

## 路径与复验范围

[relocation.json](relocation.json)保存旧→新映射、三目录大小与编辑过的导航范围；[原资产SHA清单](preserved_files_before_move.json.gz)保存18,997份迁移前原文件哈希。该清单排除了本次 `evidence/archive/` 新增证据、六份明确更新的导航README以及新增校验脚本和忽略规则，其他原资产包括manifest、checkpoint、状态、日志、原分析与正式落地镜像均逐字节核对。归档前六份README原文保存在[navigation_before_archive/](navigation_before_archive/)。

恢复用 `restore_candidate.py --repo . --destination <新空目录>`；显式 `--repo .` 避免目录深度变化影响旧默认值。原始保全校验用上级新增的 `verify_archive.py`，按当前目录的相对位置核对，不改写冻结manifest。历史控制器及旧绝对路径分析源码只作当时的证据，不在归档后启动。

[git_commit_paths.txt](git_commit_paths.txt)为本子任务完成时Git可见的本run路径清单，三个原始目录不在其中。上级归档任务负责共享索引及Git提交/推送，并可补充外部导航链接的精确补丁和快照；本子任务没有修改该材料目录或共享索引。
