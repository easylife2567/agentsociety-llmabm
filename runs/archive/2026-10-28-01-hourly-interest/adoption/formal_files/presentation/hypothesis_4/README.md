# 假设4分析资产

本目录保存假设4的图表和派生数据；不同批次保留各自来源，不能混用。

| 一级资产 | 职责 |
|---|---|
| README.md | 本级导航 |
| [hourly_return_v1/](hourly_return_v1/README.md) | 当前采用的统一小时回流三臂10seed：正式路径复算、原样式均值图、DTW与稳定性、正文影响评估 |
| [report_zh.md](report_zh.md) / [HTML](report_zh.html)、[report_en.md](report_en.md) / [HTML](report_en.html) | 三臂各10seed主实验稳定性：沿用原W19–W22口径，按用户确认将版本视为等价、合计10主分析，批次补充、配对与留一法；明确时序排序与更快回流未分离，不更新消融 |
| report_outline.json、artifact_manifest.json | 本轮主实验报告结构、三张对照图及资产对应 |
| [charts/](charts/README.md) | timestamp_v1正式实验Agent周发帖量：九次单图、三臂均值图；历史图表保留原路径 |
| [timestamp_bdr_v1/](timestamp_bdr_v1/README.md) | 已采用的B/D/R同seed配对分析：双语报告、逐周机制证据、19张图和原始来源 |
| data/ | 原三seed表保留；seed10_*为本轮30次完整主实验、330周表、分层汇总、45项配对、SQLite派生库、3416项来源哈希和保全检查；seed10_quick_stats/为本轮EDA |
| [2026-09-30-01-arrival-timing/](2026-09-30-01-arrival-timing/README.md) | 普通真实帖到达时机四格诊断的复算表、来源核验和图形 |
| [2026-10-06-01-baseline-anchor/](2026-10-06-01-baseline-anchor/README.md) | 常态锚点换算的独立固定曝光数值检查；不含新LLM轨迹 |

到达时机任务的完整解释与交接见[任务README](../../runs/archive/2026-09-29-02-injection-timing/README.md)。本目录不另设实时进度。

2026-10-29已采用hourly_return_v1作为当前主实验结果。以下report_zh/en、seed10_*及timestamp_bdr_v1保留旧回流制度身份，旧统计检验不移作新版结论；新版Full与旧消融不能混搭配对。新版与原分析分别保存，历史原始结果、报告、图和来源清单不覆盖。

本轮10seed分析复用原论文图3/4数值口径，旧三seed图和原paper/figures/source_data保持。完整综合见[综合说明](../../synthesis/synthesis_report_zh.md)。官方分析harness及研究流水线状态已由CLI登记；旧harness阶段快照与默认固定单run入口不适配30run的处理，在data/seed10_explore.md、seed10_prior_harness.json说明。

运行兼容记录：旧claims阶段无法直接intake、固定单run入口无法接收30run，以及新综合scope为空时预检无法引导范围，均已实际记录CLI阻塞。保留旧状态后，仅用已安装SDK的state API分别设置本轮派生db_path和综合scope=[4]；真实produce gate通过后，其余审查、attestation、release、synthesis与研究阶段登记均由官方CLI执行。未修改引擎或技能代码，也未手改progress JSON。

运行资产目录整理（2026-10-24）：本报告30次主实验的实际目录统一为[experiment_2/runs/timestamp_v1](../../hypothesis_4/experiment_2/runs/timestamp_v1/README.md)。CSV、SQLite、来源JSON及报告数值保持原字节；其中旧路径通过该目录relocation.json与run_asset_paths.py定位。seed10_analyze.py及原三seed绘图读取入口只修订路径，未重新计算或覆盖既有分析。
