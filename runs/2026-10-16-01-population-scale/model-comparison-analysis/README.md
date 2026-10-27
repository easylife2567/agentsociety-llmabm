# CUC 服务替换比较：分析资产

本目录保存当前 run 的候选比较报告与复算材料。唯一实时状态仍在[上一级 README](../README.md)，本文件只作资产导航。

| 直接资产 | 用途 |
| --- | --- |
| [report_zh.html](report_zh.html)、[report_zh.md](report_zh.md) | 中文主报告：制度数值、正文质量、回流机制、速度与边界 |
| [report_en.html](report_en.html)、[report_en.md](report_en.md) | 内容一致的英文副本 |
| [synthesis_report_zh.html](synthesis_report_zh.html)、[中文 Markdown](synthesis_report_zh.md) | 综合本轮研究目的、证据一致与张力、适用判断 |
| [synthesis_report_en.html](synthesis_report_en.html)、[English Markdown](synthesis_report_en.md) | 英文综合副本 |
| [data/](data/README.md) | 逐周指标、配对差值、完整性、来源校验和、正文样本与审读 |
| [assets/](assets/README.md) | 报告图PNG与可编辑SVG |
| [tool-logs/](tool-logs/) | 官方分析CLI与门禁操作原始回执；阻塞或未签不伪装PASS |
| [extract_comparison.py](extract_comparison.py) | 基于ReplayReader与冻结账本的离线抽取脚本；来源与命令见data/source_index |
| [build_appendices.py](build_appendices.py) | 离线复算新旧同口径耗时、33行配对周序列及全期峰位 |
| [review.md](review.md)、[review.json](review.json) | 独立报告与综合审查通过，非正式claims批准 |
| [artifact_qa.json](artifact_qa.json) | 1387个来源文件哈希一致、17份导航/报告本地链接及图的实际检查 |
| c1_candidate.json、c2_candidate.json、c3_candidate.json、explore_attestation.json | 未用户签定的候选主张与已完成数据探索的实际签核输入 |
| [plot_speech_volume.py](plot_speech_volume.py)、[speech_volume_contract.json](speech_volume_contract.json) | 用户要求的新批三制度11周Agent发言量趋势图、数据与统计口径 |
| [plot_comparison.py](plot_comparison.py) | 图表复算脚本，输出来源见figure_contract |
| [write_reports.py](write_reports.py) | 报告作者组织的双语Markdown、原生HTML与隔离副本写出脚本，无模型调用 |
| [semantic_report_passages.json](semantic_report_passages.json) | 读取完整正文审读后作者写定的中英文质量段落 |
| [figure_contract.json](figure_contract.json) | 图表主张、证据、范围与输出契约 |
| [analysis_plan_payload.json](analysis_plan_payload.json)、[frame_attestation.json](frame_attestation.json) | 分析问题与范围的官方CLI输入 |
| [report_outline.json](report_outline.json)、[analysis_summary.json](analysis_summary.json)、[artifact_manifest.json](artifact_manifest.json) | 报告结构、结论限制与文件清单 |
| [synthesis_brief.json](synthesis_brief.json) | 单范围综合问题与实际使用证据 |

`workspace/presentation/hypothesis_4_cuc/` 保存隔离的报告副本，`workspace/synthesis/` 保存综合副本。研究仍是H4，4_cuc仅为分析隔离命名；正式claims和发布签名保持未签。本次候选交付不自动采用、归档、commit或push。
