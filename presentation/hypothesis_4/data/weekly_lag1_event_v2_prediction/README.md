# weekly_lag1_event_v2：Agent 发帖量预测与中间产物

本文件夹用于审核尚未正式运行的 `weekly_lag1_event_v2`。根据 AgentSociety 分析技能的目录约定，单实验的中间数据与探索性图表放在 `presentation/hypothesis_4/data/`，因此这里没有另建顶层 `raw/`。原文件均保留在原位置，本文件夹收集的是便于集中查看的副本。

## 先看什么

1. `prediction/weekly_lag1_event_v2_agent_post_volume_prediction.png`：修改后方案的 Agent 发帖量预测图。
2. `prediction/predicted_agent_posts_total.csv`：每种推荐机制、每周的三种子均值、最小值、最大值和标准差。
3. `prediction/predicted_agent_posts_by_type.csv`：按 Agent 类型拆分的预测。
4. `prior_weekly_lag1/eda_figure_03_weekly_lag_agent_supply_stacked_area.png`：上一轮正式实验的聚合图，适合和预测图对照。
5. `prior_per_run/`：上一轮 interest/random 六个运行各自的 Agent 发帖量图。

## 预测结论

- 两组的最高峰都在 W13：interest 预计平均 41.7 帖，random 预计平均 42.0 帖。
- W13 两组均预计有 22 个 mourning Agent 发帖。这来自两组共享的 W13 外生事件信号，符合“讣告当周发生并被 Agent 感知”的修订目标。
- interest 在 W14 仍保持较高水平，随后下降；W21–W23 因兴趣推荐下 meme 内容的反馈累积而回升。
- random 在 W14 后总体下降，没有再形成接近 W13 的第二高峰。
- W23 是 drain/readout 周，只注入 W22 来源的延迟真实帖。它仍允许 Agent 对这些内容作出反应，但没有可用于拟合的 W23 同周真实基准，应该单独解释。

## 预测是怎样得到的

这不是正式实验结果，也没有调用 LLM。预测程序直接读取六个待审配置，逐周执行正式环境中的 feed 装配与确定性发帖判定规则。为了让本周 Agent 帖在下一周继续影响信息流，程序用上一轮六个已完成运行中 1,110 条 Agent 帖的分类倾向中位数，作为各类新帖内容的代理向量。

因此，这张图适合在正式运行前检查峰值位置、两组大致差异和数量级。具体文本会怎样改变后续排序，仍需正式实验确认。三种子的预测范围已经保存在 `predicted_agent_posts_total.csv`，不应把图中的均值当成精确结果。

预测程序位于：

`hypothesis_4/experiment_1/predict_weekly_lag_event_v2.py`

## 文件夹说明

- `prediction/`：本次机制代理预测的图、汇总表、逐运行表和方法摘要。
- `design_inputs/`：当前实验设计清单与注入时机审阅说明。
- `prior_weekly_lag1/`：此前基于已完成 `weekly_lag1` 结果制作的临时聚合图表和说明。
- `prior_per_run/`：此前六个运行的逐运行 Agent 发帖量图。
- `reference/`：用户指定的旧版绘图模板副本。
- `manifest.json`：本文件夹全部产物的来源、大小和 SHA-256 校验值。

