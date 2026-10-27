# 候选分析图

| 图组 | 数量与格式 | 口径 |
|---|---|---|
| `chart_01_<condition>_s<seed>_agent_supply` | 12张，PNG/SVG | Full、no_b、no_d、no_r各3seed，直接调用原chart3b模板 |
| `chart_02_<condition>_mean_agent_supply` | 4张，PNG/SVG | 3seed算术均值，仍是作者类型Agent成功供给 |
| [chart_03_supply_mean_comparison.png](chart_03_supply_mean_comparison.png) | PNG/SVG/PDF | 四条件均值供给分面，统一0–80；不含真实外部输入 |
| [chart_04_primary_paired_effects.png](chart_04_primary_paired_effects.png) | PNG/SVG/PDF | 预设B/D/R三指标的同seed配对点、平均差与实际差值范围 |
| [chart_05_speaking_trajectories.png](chart_05_speaking_trajectories.png) | PNG/SVG/PDF | 全体与玩梗型作者发言率，3seed均值和最小–最大带，不是置信区间 |

五类堆叠配色与W13标记参照用户指定模板；作者类型不是正文语义金标。图契约见../../../payloads/figure_contracts.json，模板哈希/原图尺寸与导出规则见../../../checks/template_and_exports.json。SVG文字可编辑；没有把未运行结果或旧100seed数值代理画入本轮图。
