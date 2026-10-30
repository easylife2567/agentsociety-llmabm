# 三臂均值与DTW图件

解释见[上级报告](../report.md)，本级PNG与SVG均为本次实际生成文件。

| 文件 | 用途 |
|---|---|
| three_arm_mean_supply.png、.svg | 之前chart3b样式的三臂每周成功发帖量；每臂10seed等权均值 |
| dtw_stability.png、.svg | 逐seed DTW分布、均值±样本SD，以及同seed三臂折线 |
| plot_manifest.json | 作图输入、脚本、4份图件SHA256，33行均值及口径核验 |

PNG为300dpi；SVG保留可编辑文字。DTW越低表示当前现实五类份额走势拟合越好，误差棒是跨seed样本标准差，不能当作置信区间。历史时序与先导seed0在图中显式标明。
