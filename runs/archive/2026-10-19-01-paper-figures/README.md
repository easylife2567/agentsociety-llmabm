# 论文图件重制与项目框架图（已归档）

2026-10-30按用户“归档，只保留最后一版本的图”指令归档。归档位置为`runs/archive/2026-10-19-01-paper-figures/`，原活跃目录已清理。

## 结果与采用边界

最终图1—6与中文图注已完成，全部保留SVG、PDF和600dpi PNG。图1为含U公式、固定个体发言门槛和参数短释义的环形框架；图2—5使用真实数据/最新统一小时回流主实验，图6保持原十种子组件配对。旧候选图、灰度稿、拼版中间件、旧打包和旧图注版本不再保留。

最新图件仅在本归档交付，没有自动替换正式paper图件或Word；归档不等于正式采用。此前按用户授权交付的十组修订Word和原稿输入保全为历史文档，其内容未更新为本轮六图。

## 本级资产

| 资产 | 用途 |
|---|---|
| [figures_unified_v1/](figures_unified_v1/README.md) | 唯一最终版六图、六页PDF、六图SVG压缩包、中文图注、源码、冻结数据和最终QA |
| [inputs/](inputs/README.md) | 两份原稿DOCX及冻结指纹/检索文本 |
| [word_seed10/](word_seed10/README.md) | 先前交付的唯一十组修订Word及结构/编辑证据 |
| [recovery/](recovery/README.md) | 源码恢复、来源映射、环境指纹、清理清单与归档验证 |
| initial_git_status.txt、input.sha256、manuscript.extracted.txt | 本run初始状态、初稿指纹和检索文本 |
| .gitignore | 临时验证目录忽略规则 |

## 基线与独立恢复

初始commit为`69d243955d341444ae769fae5bf23dc160465cd6`；归档时基线与Git状态见recovery/baseline.json、archive_start_git_status.txt。最终绘图脚本均为本run新增文件，保留完整最终副本；不需要恢复任何引擎改动或旧候选图即可离线重绘。重要已有源码修订的最终补丁与起点另存recovery/code_changes。

从项目根读取`.env`中的PYTHON_PATH，以项目解释器运行`figures_unified_v1/scripts/rebuild_final.py --verify-only`核对最终材料，或使用`--output`指向新的空目录离线重绘。精确命令、字体/依赖版本及实际重绘结果见recovery/README.md。没有启动LLM、实验或网络请求。

## 路径与外部依赖

历史日志、原始manifest和来源SHA保留原字节，旧`runs/2026-10-19-01-paper-figures/`路径对应本归档；被冻结源表的映射见recovery/source_path_map.json。

旧Word图1脚本已改读正式目录的source_figure1.svg及同字节PNG冻结副本，避免依赖已清理的旧run图；仅修改输入路径，没有执行历史构建器或改Word。补丁、原脚本与精确哈希见recovery/archive_reference_fix.patch和formal_dependency_fix.json。

归档本身未自动提交或推送；2026-10-30用户追加授权提交本run归档并推送GitHub。本次提交仅包含归档、旧候选清理及本run索引，不混入其他正文或实验修改。最终离线恢复与清理验证见recovery/archive_verification.json。
