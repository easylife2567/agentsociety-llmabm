# 比较数据与证据

本目录只维护直接资产用途；解释见[主报告](../report_zh.html)，实时状态见[run README](../../README.md)。

| 资产 | 用途 |
| --- | --- |
| weekly_metrics.csv、weekly_comparison.md | 新三臂/旧s0–s2逐周指标与配对11周可读附表、全期峰位 |
| metrics_summary.json、paired_metric_differences.csv、institution_contrasts.csv | 预设事件周与后期指标、配对差值、三制度差值方向 |
| late_author_participation.csv | 五类固定作者的后期发言Agent周与分母 |
| integrity.json | 终态步数、唯一行动、发布账本等独立核验 |
| source_index.json | 原始路径、SHA256、读取方法和离线复算命令 |
| runtime_comparison.json | 新旧批次/引擎时间及对应原始证据 |
| first_differences.json、mechanism_trace.json | 首次分歧及正文倾向→feed→效用/发言链条 |
| agent_decision_differences.json、feed_key_differences.json | 全量所查决策字段与feed稳定键分歧 |
| quality_summary.json | 首次/重写/修复/兜底账本、原始与最终正文长度/完全重复 |
| sample_selection.json、paired_text_samples.jsonl | 固定分层SHA256抽样规则及59对完整提示/正文/feed |
| supplementary_anomaly_samples.jsonl、unpaired_publication_samples.jsonl | 解释处理异常及非共同发布键的补充材料；不混入固定抽样分母 |
| text_review_annotations.jsonl、text_review_findings.md | 上下文语义审读逐条注释与说明，非人类金标 |
| eda_quick_stats.md | 官方分析CLI对新兴趣臂两张选定表的EDA |
| weekly_agent_posts.csv、weekly_agent_posts_verification.json | 新批33个制度×周的发言量和五类作者计数；核对总发帖数、环境供给和五类之和相等 |
| extraction_stdout.txt | 提取脚本输出原始回执 |

作者固定类型、feed池标签和正文词表分类是不同口径。旧s1/s2只提供旧重复范围，不是新旧配对的额外重复；所有样本分母见抽样规则和主报告。
