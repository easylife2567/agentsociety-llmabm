# weekly_lag1_event_v2：Agent 发帖量预测与中间产物

## 当前有效预测

`prediction_corrected/weekly_lag1_event_v2_agent_post_volume_prediction.png`

这张图依据修正后的 timing-only 方案生成：普通真实帖和 Agent 帖延迟一周，W13官方讣告仍在W13进入，W23作为延迟内容观察周；不再用等效悼念槽位直接提高Agent的发言效用。

预测没有预设W13必须成为总量峰值。三种子均值如下：

- interest：W12为22.3帖，W13为20.7帖，W14为30.0帖，W15达到35.3帖；之后下降，W21–W23出现由meme内容推动的后期回升。
- random：W12为23.3帖，W13为20.7帖，W14为25.0帖；之后总体下降，W23约6.7帖。
- W13的直接反应较小；W14和W15的滞后反应来自Agent帖子下一周才进入信息流，以及后续一轮反馈。

图中的堆叠面积是三种子均值，灰色范围是每周三个种子的总发帖量最小值到最大值。

## 预测边界

这是实验前的机制代理预测，没有调用LLM。程序执行正式环境的feed装配和确定性发言规则，但用上一轮已完成实验中各类Agent帖的分类倾向中位数代替新生成文本。因此，它适合检查峰值是否被配置强制制造、延迟方向和数量级，不应当作正式实验结果。

## 已撤回版本

`withdrawn_mechanical_scenario/`保存了原先使用5个等效悼念槽位生成的图表。该版本会把两组22个mourning Agent全部推过发言门槛，W13约42帖的峰值主要由参数机械叠加形成，已经撤回，不可用于论文或实验预期。

对应的敏感性诊断见`event_signal_salience_sensitivity.csv`。

## 文件夹说明

- `prediction_corrected/`：当前有效的预测图、三种子总量表、类型拆分表、逐运行表和方法摘要。
- `withdrawn_mechanical_scenario/`：已撤回的错误预测，仅供审计。
- `event_signal_salience_sensitivity.csv`：旧事件槽位参数的W13敏感性诊断。
- `design_inputs/`：当前实验设计清单与注入时机审阅说明。
- `prior_weekly_lag1/`：此前已完成实验的聚合图表和说明。
- `prior_per_run/`：此前六个运行的逐运行Agent发帖量图。
- `reference/`：用户指定的旧版绘图模板副本。
- `manifest.json`：文件来源、大小和SHA-256校验值。

预测程序位于`hypothesis_4/experiment_1/predict_weekly_lag_event_v2.py`。

