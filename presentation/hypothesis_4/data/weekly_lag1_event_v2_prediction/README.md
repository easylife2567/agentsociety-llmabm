# weekly_lag1_event_v2：Agent 发帖量预测与中间产物

## 当前结论：整体滞后方案已撤回并归档

用户将预测图与 `anchored_v1_interest_s0` 正式结果对比后指出，单纯解决注入时机不应改写整体动力学曲线。正式数据复核确认，差异来自整体滞后设计，而不是绘图误差。

请先查看：

- `timing_rethink/formal_timing_rethink.png`：`anchored_v1`与已完成`weekly_lag1`正式结果的对齐诊断。
- `timing_rethink/formal_timing_comparison.csv`：两轮正式结果的三种子周度均值。
- `timing_rethink/formal_timing_diagnostics.json`：原周标签与向前对齐一周后的相关系数和RMSE。
- `hypothesis_4/experiment_1/INJECTION_TIMING_REDESIGN_REVIEW.md`：重新设计建议。

`prediction_corrected/`中的图准确表达了“整体延迟一周”方案的代理走势，但该方案已撤回并归档，因此这张图不能视为当前实验的预测图。

当前正式方案已经恢复为 `anchored_v1` 的周级刺激—响应顺序：同周真实帖作为外部环境先进入并冻结所有Agent的feed；当周Agent帖在所有Agent行动结束后统一提交，从下一周起才影响其他Agent。这样可以消除Agent之间的同一步顺序偏差，同时保留原正式模拟的周度趋势。

## 预测边界

这是实验前的机制代理预测，没有调用LLM。程序执行正式环境的feed装配和确定性发言规则，但用上一轮已完成实验中各类Agent帖的分类倾向中位数代替新生成文本。因此，它适合检查峰值是否被配置强制制造、延迟方向和数量级，不应当作正式实验结果。

## 已撤回版本

`withdrawn_mechanical_scenario/`保存了原先使用5个等效悼念槽位生成的图表。该版本会把两组22个mourning Agent全部推过发言门槛，W13约42帖的峰值主要由参数机械叠加形成，已经撤回，不可用于论文或实验预期。

对应的敏感性诊断见`event_signal_salience_sensitivity.csv`。

## 文件夹说明

- `timing_rethink/`：正式结果的时序对齐诊断和重新设计证据。
- `prediction_corrected/`：整体延迟方案的代理预测；因方案正在撤回，仅作诊断。
- `withdrawn_mechanical_scenario/`：已撤回的错误预测，仅供审计。
- `event_signal_salience_sensitivity.csv`：旧事件槽位参数的W13敏感性诊断。
- `design_inputs/`：当前实验设计清单与注入时机审阅说明。
- `prior_weekly_lag1/`：此前已完成实验的聚合图表和说明。
- `prior_per_run/`：此前六个运行的逐运行Agent发帖量图。
- `reference/`：用户指定的旧版绘图模板副本。
- `manifest.json`：文件来源、大小和SHA-256校验值。

预测程序的审计副本位于`archive/hypothesis_4_experiment_1_batches/design_superseded/weekly_lag1_event_v2/tools/`。完整归档索引见工作区根目录`ARCHIVE_MANIFEST_H4E1.md`。
