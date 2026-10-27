# 归档核验

用户2026-10-18明确要求归档本run；当前结果及旧新路径映射见上级README。

| 直接资产 | 用途 |
|---|---|
| baseline.json | 本轮主项目原状和Git/worktree边界 |
| process-check.json | 真实进程命令无本run残留，不只凭监督器状态 |
| workspace-preservation.json、workspace-status.json | 含忽略项的10070项盘点，8165镜像与1891独有文件的保全位置 |
| restore/ | 从准确commit及45文件恢复层实际setup/generate/verify，900 profiles、8100公式、26测试 |
| restore-worktree-final/、restore-worktree-inventory.json | 本轮恢复验收现场新增/修改资产，解除临时登记前保全 |
| controller-recovery.json、controller-recovery-test.log | 两个已有patch check/apply及合成并行/共享预算/联停复验 |
| formal-offline-check.json | 正式12单元13200行动、5394源哈希与27配对主指标只读复算 |
| adopted-recovery-check.json | 201份正式候选在空目录恢复、2707项Full外部原始依赖校验 |
| worktree-removal.json | 两个本run worktree无force安全移除，其他run保留 |
| navigation-before/、navigation-before.json | 导航适配前原文及指纹，未改历史数据/报告/代码 |
| navigation-changes.json | 本次可维护Markdown链接及符号链接调整清单 |
| archive-manifest.json | 除自身/最终校验外的归档文件SHA256，保留历史内容指纹 |
| final-check.json | 迁移、链接、Git边界、文件哈希、暂停定时器及无新调用最终结果 |

原始checkpoint、日志、manifest和报告正文不批量改写。旧脚本按原目录层级冻结，归档后不用于启动实验；正式复算入口仍在主项目experiment_3。未新增LLM、未提交Git、未改主机器状态。
