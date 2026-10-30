# 最终绘图冻结数据

| 文件 | 内容 |
|---|---|
| observed_total.csv | 49,930条采集样本的真实周总量，保留溯源；五类面积图不含全部噪音/不确定内容 |
| observed_weekly.csv | 图2/3：18周、三平台键、五类内容；合并五类46,602条 |
| weekly_supply.csv | 图4：三制度×10seed×11周的固定作者成功发帖数 |
| main_runs.csv | 30run整体和晚期指标 |
| feedback_runs.csv | 图5三项过程指标及原分子/分母，30run |
| ablation_metrics.csv | 图6五项原批组件配对，100行，每条件10seed |
| observed_sources.json、ablation_source_index.json | 经验数据与消融原来源记录 |
| official_weekly.csv、official_run_metrics.csv | 正式小时主实验周表与run表冻结副本 |
| official_manifest.json、official_provenance.json | 正式30run矩阵与原始验证记录 |
| provenance.json | 原准备脚本和输入/输出SHA、指标公式及30ENV分母核对 |

这些文件字节未改。原记录含历史路径，映射见../../recovery/source_path_map.json；旧run内部来源中重复字节映射到本表，不同的非图元数据另存recovery/upstream_sources。

图5的分母依次为760、76和3,240。图6保留原timestamp_v1的Full与干预配对，不将新小时Full代入。内部xiaohongshu键保持，图面显示Rednote。默认重绘只读本冻结表。
