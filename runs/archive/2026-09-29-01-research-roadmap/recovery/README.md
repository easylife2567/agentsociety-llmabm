# 归档恢复材料

归档结果和恢复顺序统一见[本run README](../README.md)。

| 资产 | 用途 |
|---|---|
| [original_sources](original_sources/) | 原始文档、代码和补丁快照，供核对历史校验和及原目录恢复 |
| [original_inventory.json](original_inventory.json) | 归档前全部文件校验和、旧路径与提交 |
| [archive_metadata.json](archive_metadata.json) | 归档采用状态、路径映射及实际核验结果 |

历史源码哈希按original_sources中的原件核对；上一级脚本已作归档路径适配，恢复旧目录布局时使用原件。manifest、checkpoint及原始日志保留旧路径，归档不授权继续运行实验。
