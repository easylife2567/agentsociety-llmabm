# 已归档探索run

2026-10-13按用户授权归档三个历史根级run；当前U标定与文稿run保留在[runs活跃入口](../README.md)。归档不等于采用，不包含commit、push或新实验运行。原始实验输出及presentation分析资产保留原位置。

| run | 主题 | 采用情况与验证边界 |
|---|---|---|
| [2026-09-29-01-research-roadmap/](2026-09-29-01-research-roadmap/README.md) | 历史规范和项目导航已落实；现行规范以根AGENTS.md为准。纯文档run，没有候选代码、LLM仿真或worktree。 | 已采用（文档与工作规范）；实际恢复核验范围见本run README |
| [2026-09-29-02-injection-timing/](2026-09-29-02-injection-timing/README.md) | 四格诊断、内容修复与数值验证保留历史证据身份；当前正式主设计为experiment_2。未启动新LLM，不把诊断写成当前主批结果。 | 已采用（timestamp设计与保留发言的内容修复）；实际恢复核验范围见本run README |
| [2026-10-06-01-baseline-anchor/](2026-10-06-01-baseline-anchor/README.md) | 固定曝光数值诊断已完成，候选B没有落地；当前主实验继续保留原B及行为参数。 | 未采用（候选B）；实际恢复核验范围见本run README |

各run README为本run归档结果与恢复说明入口。旧路径 `runs/<run-id>/` 对应现在的 `runs/archive/<run-id>/`；历史manifest、checkpoint、日志及来源哈希不批量改写。归档适配前源码在各run的recovery/original_sources，原tmp证据在historical_tmp。恢复包未复制凭据，复现输入按冻结校验和核对，不从当前活跃run读取私有候选文件。
