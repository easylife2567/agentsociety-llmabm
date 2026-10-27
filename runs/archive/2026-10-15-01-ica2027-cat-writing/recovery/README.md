# 写作run归档恢复材料

本目录保全本次写作run的归档前记录、最终交付副本及路径适配补丁；归档结果与唯一状态入口见[上一级README](../README.md)。本run没有项目模型代码探索或独立worktree，没有仿真恢复与重跑授权。

## 本级资产

| 资产 | 用途 |
|---|---|
| [original_run/](original_run/) | 归档前11份run根级Markdown原字节，供历史来源指纹与导航修复前内容核对 |
| [original_run_manifest.json](original_run_manifest.json) | 上述原文件路径、副本位置与SHA256 |
| [original_navigation/](original_navigation/) | 归档前相关正式导航及活跃、归档索引副本，按当时路径解释 |
| [original_sources/](original_sources/) | 唯一需适配的既有合稿脚本修改前原字节 |
| [archive_paths.patch](archive_paths.patch) | 仅将合稿脚本两项run输入改读正式冻结输入；从保存的原字节执行`git apply --check`后应用 |
| [git_status.before_archive.txt](git_status.before_archive.txt) | 本轮归档开始时的实际Git状态，包含用户及其他任务差异，不计作本run成果 |
| [final_documents/](final_documents/) | 本run最终交付的Word、图件、可检索稿、思维链与配套来源、脚本、核验副本，保留项目相对位置；无需原run工作区即可恢复这些交付物 |
| [final_documents_manifest.json](final_documents_manifest.json) | 最终交付副本的项目相对路径、字节数与SHA256 |
| [archive_checks.json](archive_checks.json) | 实际离线恢复、合稿、输入指纹与迁移核验结果 |

## 恢复顺序与边界

1. 在一个空目录中，按`final_documents_manifest.json`核对并复制`final_documents/`，保留其中的项目相对位置；这是离线交付恢复，无需Git worktree、原run路径或其他活跃run。
2. 正文、两版Word、PDF与图件可直接使用；已有正式项目上的恢复须先比较当前文件，不能用归档副本覆盖用户后续修改。
3. 从已保存`article*.json`重建Word，使用`paper/word/scripts/README.md`的既有方法；从部分采用稿重新装配，则读取正式`paper/word/source_materials/`的两份冻结文稿输入，合稿函数继续记录其SHA256。
4. 如需单独复原路径适配，以`original_sources/`保存的脚本为实际起点，在对应目录先执行`git apply --check archive_paths.patch`再应用；该补丁只涉及两个输入路径，不修改模型、正文规则或实验。
5. 图件可从保存的CSV离线重画；从原始仿真状态重算指标仍需正式实验中的冻结资产，按原来源清单核对，不从其他活跃run读取私有文件。

`final_documents/`、`original_*`及上级`inputs/`是冻结副本，内部旧链接不批量改写；相对链接按原项目位置解析。旧`runs/2026-10-15-01-ica2027-cat-writing/`统一对应当前`runs/archive/2026-10-15-01-ica2027-cat-writing/`。

本次实际恢复核验会复制交付物到空的临时目录、逐文件校验SHA256，并以适配后的合稿函数重建文章块后比较正文、公式、图表与引用。Word仅进行既有交付文件的结构和批注修订核对；不重新生成排版，不将本次核验称为新增实验、全稿文献审稿或正式投稿验收。
