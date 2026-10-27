# 两个结构候选的定向核对

| 文件 | 用途 |
|---|---|
| baseline.json | Git基线、100行原CSV及主图/旧候选/合集/Word的起点指纹 |
| figure_05_seed_atlas_v1.build.json | A版源/脚本/输出哈希、逐条件均值、seed行和原单位轴限 |
| figure_05_effect_table_v1.build.json | B版逐seed差值、差值均值、两条件均值及单位 |
| checks.json | 两版原生SVG/PDF、8pt字号、数值一致、无裁切/文字重叠、原交付未改 |
| figure_05_seed_atlas_v1_grayscale.png、figure_05_effect_table_v1_grayscale.png | 各自灰度校样 |
| REVIEW.md | 指定模型的实际PNG及科学表达定向审查 |

当前源数据与已审查图5相同。A逐seed横线与独立Mean行不改变观测；B仅派生同seed干预−Full，分母和窗口保持。配对差值为−7.825帖/周、−32.7632/+30.7600/−56.4452/−12.8519个百分点。没有生成新的置信区间、拟合分布或隐藏实际重复。原始40run及18,108项来源对账仍见上两级qa/fig5_extraction.json和source_data/ablation_seed10_sources.json。
