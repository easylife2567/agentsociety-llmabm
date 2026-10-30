# 归档恢复与证据

## 最终图离线恢复

最终脚本均为本run新增完整文件，源码位于../figures_unified_v1/scripts；冻结绘图数据自含。无需旧候选目录、worktree、原始大工作簿或LLM服务即可重绘六图。

在项目根读取`.env`中的PYTHON_PATH，使用项目解释器执行：

```bash
task_python=$(sed -n 's/^PYTHON_PATH=//p' .env)
PYTHONDONTWRITEBYTECODE=1 "$task_python" runs/archive/2026-10-19-01-paper-figures/figures_unified_v1/scripts/rebuild_final.py --verify-only --pymupdf-path /Users/easylife/.cache/uv/archive-v0/gazd_6nNK5VOozdKrmrr4
```

独立重绘使用同一入口的`--output /绝对路径/新的空目录`，不覆盖已有非空目录。环境/字体指纹见environment.json；验证时使用本机已有PyMuPDF缓存路径，换机可使用已安装的PyMuPDF并省略该参数。字体未复制，需提供相同Arial/STIX字体以复现同样排版。

## 直接材料

- final_assets.json：最终保留文件SHA256清单，供默认入口校验。
- archive_verification.json：本次实际独立重绘、图件一致性、最终路径验证与清理结果。
- archive_source_inventory.json、cleanup_manifest.json：归档前文件指纹和仅保留最终图的清理清单。
- baseline.json、archive_start_git_status.txt：基线commit及开始状态。
- source_path_map.json、upstream_sources/：原始来源路径与冻结非图元数据映射；不改原manifest或原始日志。
- fact_inputs/：最终框架核对的实际代码、协议与正文文字快照，仅作为事实证据，不应用到正式项目。
- code_changes/：最终绘图修订的完整补丁与纯源码起点，不含旧图候选。恢复入口直接使用最终完整源码，无需依次回放历史迭代。
- archive_reference_fix.patch、archive_reference_input_png.patch、original_sources/、formal_dependency_fix.json：旧Word图1脚本解除活跃run依赖的单行修改及同字节输入核对。
- prior_user_edits/：归档前未提交draw.io及其备份的文本差异，基线见baseline.json；保全用户编辑，不作为保留的图件版本。
- original_tools/、historical_word_tools/：原始数据准备和旧文档处理源码，仅作历史溯源，不作为归档默认入口。
- run_history.md：归档前run说明原文，内含的已清理旧图链接仅属历史记录。

原Word与原输入在归档中保持字节；本次不宣称能以已清理的旧候选图重新构建历史修订Word。归档不是当前六图的正式落地，无新实验、无commit/push。

本次已实际在run专属空目录中独立重绘六图：六份SVG去除日期metadata后XML完全一致，六份PNG逐字节一致，六份PDF和六页合集的逐字符文字/路径/颜色/坐标完全一致。报告见offline_redraw_verification.json；原生成日期元数据允许变化，不放宽任何图形坐标。

外部历史PNG输入作为新增资产的Git二进制补丁保全，不另留旧图候选文件；该补丁与单行路径修正、三份最终绘图补丁及用户draw.io编辑差异均已在专属空目录中重放，逐字节一致，见patch_replay_checks.json。
