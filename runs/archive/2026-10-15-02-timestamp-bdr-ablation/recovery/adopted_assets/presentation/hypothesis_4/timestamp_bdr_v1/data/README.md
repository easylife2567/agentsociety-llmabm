# 数据、定义与来源

- `source_index.json`：12次原始来源、哈希、实际profile及9次科学配置兼容性对照。
- `metric_dictionary.json`：预设三指标、固定分母、比例/百分点及作者/正文标签定义。
- `decisions.csv`：13200条Agent机会记录，含U/B/D/R、门槛、发言/发布/请求及原始文件与记录位置。
- `weekly_by_type.csv`、`weekly_totals.csv`：660行条件×seed×周×作者类型及132行总周表，保留零产出周。
- `exposure_by_opportunity.csv`、`weekly_exposure_by_cohort.csv`：实际feed长度、标签和来源计数；以实际阅读数作分母。
- `run_metrics.csv`：12个run的预设窗口指标与辅助指标。
- `paired_differences.csv`、`paired_summary.csv`：同seed消融−Full及n=3均值/实际范围；rate字段为0–1比例，乘100才是百分数和百分点。
- `vocab_label_counts.csv`：既有词表assigned_type与固定作者类型的交叉计数，不是人工分类准确率。
- `illustrative_examples.json`：声明规则排序选取的三组实际正文/静默分叉，含完整源定位；不是代表性样本。
- `generated_examples_all.json`：所有3309条实际生成正文的只读派生索引。
- `runtime_summary.json`：12次实际发布、外层请求、返回模型标识和原因计数。
- `replay_*_{weekly,agent}.json`：官方CLI的24份只读SQL查询结果，供环境和Agent记录交叉复核。
- 原no_b seed0代表性结构EDA保存在正式experiment_3/provenance/original_representative_eda；总体判断使用12次全量表。
- `analysis_summary.json`、`evidence_index.json`、`report_context.md`：人工叙述与实际证据映射，均保留候选身份。
- `chart_outputs.json`：41个图表导出文件名。

W22已成功发布但尚未到次周推荐资格的帖子可能只在arrival.week_posts，不能只用候选池_posts计数而漏掉它们。原始LLM、真实外部输入及词表分类分别保留身份，不混成一次新仿真或人工正文编码。

用户已确认并采用本轮结论。mechanism_weekly_by_seed.csv与mechanism_weekly_mean.csv给去D/去R的逐周总量和玩梗型作者量；mechanism_checks.json给228对晚期机会的决策转换及代数性质；mechanism_agent12_records.json保留五条原始记录、索引、哈希和实际feed构成。它们是既有输出核对，不是新实验或独立中介识别。source_index.json当前指向正式原始目录，原路径索引在experiment_3/provenance保全。
