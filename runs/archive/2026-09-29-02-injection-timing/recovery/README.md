# 归档恢复材料

归档结果和恢复顺序统一见[本run README](../README.md)。

| 资产 | 用途 |
|---|---|
| [original_sources](original_sources/) | 原始文档、代码和补丁快照，供核对历史校验和及原目录恢复 |
| [original_inventory.json](original_inventory.json) | 归档前全部文件校验和、旧路径与提交 |
| [arrival_new](arrival_new/) | 初始到达阶段新增模块、测试和审计脚本，来自785ad416 |
| [final_code](final_code/) | 19650745历史最终代码快照，与阶段补丁恢复结果核对 |
| [frozen_inputs](frozen_inputs/) | 必要冻结配置、素材、词表及离线测试使用的一份Agent记录 |
| [restoration_inputs.json](restoration_inputs.json) | 准确恢复基线、输入/结果位置与校验和 |
| [recovery_verification.json](recovery_verification.json) | 归档前实际恢复核验及明确范围 |
| [recovery_verification.log](recovery_verification.log) | 恢复核验原始日志，包括缺依赖失败与补齐后的通过 |
| [formal_test_before](formal_test_before/) | 正式测试路径调整前副本 |
| [archive-paths.patch](archive-paths.patch) | 归档目录与正式测试引用的最终代码补丁 |
| [archive-document-links.diff](archive-document-links.diff) | 本轮文档导航修改，与原件比较，不混入已有未提交修改 |
| [archive_scope.json](archive_scope.json) | 本次修改范围及当前活跃run的原文件校验和 |
| [post_archive_tests.log](post_archive_tests.log) | 归档路径下18项离线功能测试与零网络尝试记录 |
| [archive_metadata.json](archive_metadata.json) | 归档采用状态、路径映射及实际核验结果 |

历史源码哈希按original_sources中的原件核对；上一级脚本已作归档路径适配，恢复旧目录布局时使用原件。manifest、checkpoint及原始日志保留旧路径，归档不授权继续运行实验。
