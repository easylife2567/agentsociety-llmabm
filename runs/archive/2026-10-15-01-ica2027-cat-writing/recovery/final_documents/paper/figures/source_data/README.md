# 作图数据

| 文件 | 用途及结构 |
|---|---|
| [observed_weekly.csv](observed_weekly.csv) | 图1、2；两平台及合并范围×18周×五类，共270行。`count`为数量，`total_five`为该平台该周五类合计，`share`为0—1比例 |
| [observed_sources.json](observed_sources.json) | 原始已标注工作簿、已采用矩阵、周归属、筛选账及SHA256 |
| [observed_checks.json](observed_checks.json) | 与原始工作簿逐格一致性、W13峰值、W22比例及周份额加总检查 |
| [simulation_weekly.csv](simulation_weekly.csv) | 图3a—c；3制度×3seed×11周×5固定作者类型，共495行，仅成功发布的Agent帖 |
| [simulation_late.csv](simulation_late.csv) | 图3d；每run晚期玩梗型帖数、全部帖数及其比值，共9行 |
| [simulation_exposure.csv](simulation_exposure.csv) | 图4；每run晚期同类接触、玩梗型发帖率、生成帖跨群体展示，共9行；比例为0—1 |
| [simulation_sources.json](simulation_sources.json) | 原timestamp_v1九run身份、919份输入文件指纹及指标分母说明 |
| [ablation_metrics.csv](ablation_metrics.csv) | 图5；5面板×2条件×3seed，共30行；记录窗口、群体、分子、分母、单位和取值 |
| [ablation_sources.json](ablation_sources.json) | 正式消融来源、完整模型复用关系、输入SHA及指标对应 |

现实平台映射为`gsdata → douyin`、`sinamidu → xiaohongshu`。图1、2不包含微博；五类比例沿用已采用矩阵口径，完整来源账保留在JSON，不改原分类。实际周范围W05—W22，按原生成器直接从原发布时间取得ISO周，不另作时区转换或补零。

仿真中的`category`表示固定作者类型；接触构成中的生成帖按作者类型、外部帖按来源内容类别归属。主实验使用原`timestamp_v1`，消融使用正式`timestamp_bdr_v1`；所有完整模型对照都来自同一批原主实验。冻结外部输入的来源保持实验原貌，具体范围见[正文设计](../../manuscript/manuscript.accepted.md)。

全部份额先在每run内计算，绘图时再取三个seed的算术均值。源数据保留小数，图注仅按正文精度显示；合并现实数据则先合并两平台计数再计算份额。
