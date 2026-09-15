# 无效或不完整 run 归档

本目录只保存人工停止、并发度切换、失败恢复前残留和已确认污染的 run，用于事故审计。

这些目录一律标记为 `invalid/partial`：

- 不属于最新 `anchored_v1` 正式 9-run；
- 不参与完成率、三臂聚合、图表或论文结论；
- 不得作为 `analysis intake` 的 replay 数据源；
- 后续即使目录内出现 `pid.status=completed` 或 `_schema.json`，也不能自动升格为正式结果。

最新正式批的唯一清单见 `../runs/README.md` 和
`../runs/anchored_v1/_derived/monitor/overview.json`。
