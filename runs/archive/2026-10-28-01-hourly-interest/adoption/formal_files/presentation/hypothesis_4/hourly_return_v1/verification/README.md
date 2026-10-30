# 正式落地核验

| 文件 | 用途与实际结果 |
|---|---|
| independent_verification.original.json | 落地前独立标准库复算原件，保留原字节；3000份Agent、33,000决策、6041成功帖及全部DTW/稳定性核对通过，内含历史路径 |
| analyze_attempt1.log | 首次正式分析因时序replay碎片SHA未完整纳入manifest而停止，未写分析输出；现场保留 |
| analyze.log | 补齐原正式relocation已冻结碎片后，30run原始记录和官方replay全部核验通过，7份数据生成 |
| check.log | 正式位置再次复算，7份数据逐字节一致，不覆盖文件 |
| plot.log | 三臂均值与DTW图PNG/SVG实际生成，作图口径核验通过 |
| comparison_attempt1.log | 首次将run_metrics全字节比较时，识别10个时序origin描述变化；科学字段相同 |
| landing_comparison.json | 四份科学数据文件和两张PNG逐字节一致；run_metrics及summary全部科学字段与落地前一致，单列允许的元数据差异 |

首次来源缺项由主端将timestamp_v1/relocation.json中的完整时序replay碎片SHA补入正式manifest解决；没有修改原始输出、统计口径或放宽校验。此次是离线读取契约补齐，不是LLM仿真的重试。

正式provenance含3468项仅读取正式路径的来源；原始metadata和历史审计中的旧路径保留作证据，不作为计算加载依赖。两张PNG已实际查看且与落地前图逐字节一致。独立原件核验不代替新路径的实际运行；正式路径分析与--check均已实际通过。
