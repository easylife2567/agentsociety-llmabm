# 假设4图表

父级入口见[分析资产](../README.md)。原三seed图仅制作timestamp_v1发帖量图；本轮各10seed的完整主实验分析与新图见下节及上一级报告。

## timestamp_v1正式实验Agent发帖量

2026-10-15根据experiment_2正式九次运行制作。完全复用用户指定的experiment_1 chart3b模板：五类堆叠配色、W13红色事件线、纵轴0–80，每格10帖。仅计Agent成功发布，不含真实注入、官方输入或17条历史池。五类按固定作者类型统计，不是正文重新分类。

| 本级资产 | 用途 |
|---|---|
| [timestamp_v1_random_mean__chart3b_agent_supply_stacked_area.png](timestamp_v1_random_mean__chart3b_agent_supply_stacked_area.png) / [SVG](timestamp_v1_random_mean__chart3b_agent_supply_stacked_area.svg) | 随机制度三次重复均值；W13后小幅达峰，随后整体回落 |
| [timestamp_v1_chronological_mean__chart3b_agent_supply_stacked_area.png](timestamp_v1_chronological_mean__chart3b_agent_supply_stacked_area.png) / [SVG](timestamp_v1_chronological_mean__chart3b_agent_supply_stacked_area.svg) | 时序制度三次重复均值；W13波峰、后期玩梗发帖回升 |
| [timestamp_v1_interest_mean__chart3b_agent_supply_stacked_area.png](timestamp_v1_interest_mean__chart3b_agent_supply_stacked_area.png) / [SVG](timestamp_v1_interest_mean__chart3b_agent_supply_stacked_area.svg) | 兴趣制度三次重复均值；W13悼念波峰、后期玩梗发帖回升 |
| timestamp_v1_{random,chronological,interest}_s{0,1,2}__chart3b_agent_supply_stacked_area.png / .svg | 九次单独运行图；每张为真实整数发帖数，3000×1620 PNG及可编辑SVG |
| [timestamp_v1_plot_agent_supply.py](timestamp_v1_plot_agent_supply.py) | 调用官方只读查询CLI和原模板；重新制作图表及核验数据 |

各图描述的是仿真中的发帖轨迹。三seed均值不代表某一次运行，也未绘制置信区间；不能据此直接判断统计显著性。重复之间的区别保留在九张单图和CSV中。

数据与证据位于上一级data目录：`timestamp_v1_agent_supply_by_run_week.csv`（99个run×week行）、`timestamp_v1_agent_supply_arm_week_mean.csv`（33个arm×week行）、`timestamp_v1_agent_supply_sources.json`（SQL、图形口径、原始资产路径和SHA256校验和）。原始数据来自experiment_2/runs/timestamp_v1的replay目录，不修改原始结果。

核验：九次pid状态均为completed、各693步、11周、1100次决策；replay周度五类计数与900份AGENT.json中的posted成功记录逐项一致（9×11×5=495项）。累计发帖随机s0/s1/s2为176/173/174，时序为210/212/216，兴趣为214/227/216；所有单周均低于80，无裁剪。新增绘图脚本不改正式Agent、环境或配置，未提交Git。

复现（项目根目录）：

```bash
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
LITELLM_LOCAL_MODEL_COST_MAP=True "$PYTHON_PATH" presentation/hypothesis_4/charts/timestamp_v1_plot_agent_supply.py
```

本次未修改既有代码，无需代码修改补丁。制作时Git基线为69d243955d341444ae769fae5bf23dc160465cd6；实际原始数据和模板版本以来源清单的校验和为准。历史weekly_lag1图表保留原文件，不能与timestamp_v1混称。


## 三臂各10seed的稳定性对照

本轮从30次完整主实验复算，沿用原图3/4供给与接触口径，旧3、新7和合计10分开显示。报告入口为[上一级双语报告](../report_zh.md)；原三seed单图和均值图保持。

| 直接资产 | 用途 |
|---|---|
| chart_01_seed10_trajectories.png / .svg | W12–W22玩梗作者周供给；三批次均值及实际seed极差，范围带不是置信区间 |
| chart_02_seed10_model_cohorts.png / .svg | W19–W22五项原指标、seed散点与t近似均值区间；0起点外的负下界完整值在CSV |
| chart_03_seed10_paired_seeds.png / .svg | 同seed三制度差值，标出旧新块和seed5供给份额反向 |
| seed10_plot.py | 只读seed10派生CSV，生成三图的PNG/SVG；Agg后端与可编辑SVG文本 |

复现：从项目根用.env的PYTHON_PATH执行`presentation/hypothesis_4/charts/seed10_plot.py`。提取脚本为上一级data/seed10_analyze.py，内含30次官方只读query-data及原9次逐格复验。seed10_sources.json来源证据存在时拒绝自动覆盖；需要复算版本时先保留该来源和产物，不重跑原仿真。

2026-10-24解释口径修订：按用户确认将模型版本视为等价，All 10标为主分析，旧3/新7仅作批次补充。图表数值未变。现有绘图代码通过[seed10_model_convention.patch](seed10_model_convention.patch)修改两处标签，先git apply --check再应用；起点commit为`69d243955d341444ae769fae5bf23dc160465cd6`，任务开始时seed10_plot.py尚未跟踪，实际起点SHA256为`79fa47ebca599092a0bcba727c9dd211880afdad8acdfc30906c38ac905ff476`。补丁只含本次两处标签改动，未混入其他未提交差异。
