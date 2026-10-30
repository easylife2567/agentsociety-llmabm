# 三臂10seed分析数据

本级只索引最终离线数据；方法、解释与核验入口见[上级README](../README.md)。

| 文件 | 用途 |
|---|---|
| weekly.csv | 30run×11周，共330行；五类成功发帖数、份额及实际曝光 |
| run_metrics.csv | 30个完整run的发帖、W19–W22供给/曝光、模型及独立DTW |
| paired_dtw.csv | 3种同seed两两比较×10seed，共30行差值 |
| dtw_summary.csv | 每臂10seed DTW均值、样本SD、范围；均值轨迹DTW独立列示 |
| summary.json | 逐seed排名、配对胜出、去seed0/同模型/逐一剔除seed等完整汇总 |
| dtw_paths.json | 逐run和均值份额轨迹对现实上海周/UTC周的完整对齐路径 |
| provenance.json | 输入/原始来源SHA256、30run完成/回流/官方replay核验及运行时 |

`analyze_seed10.py --check`在不覆盖文件的情况下复算以上7份数据。README不是计算输出的一部分。
