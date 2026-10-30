# 已归档探索run

2026-10-13按用户授权归档三个历史根级run；2026-10-15归档U标定与文稿run；2026-10-18归档ICA 2027 CAT写作及timestamp B/D/R消融run；2026-10-28归档ICA2027正文核实与润色run。当前活跃状态见[runs入口](../README.md)。归档不等于采用，不包含commit、push或新实验运行。原始实验输出及presentation分析资产保留原位置。

| run | 主题 | 采用情况与验证边界 |
|---|---|---|
| [2026-09-29-01-research-roadmap/](2026-09-29-01-research-roadmap/README.md) | 历史规范和项目导航已落实；现行规范以根AGENTS.md为准。纯文档run，没有候选代码、LLM仿真或worktree。 | 已采用（文档与工作规范）；实际恢复核验范围见本run README |
| [2026-09-29-02-injection-timing/](2026-09-29-02-injection-timing/README.md) | 四格诊断、内容修复与数值验证保留历史证据身份；当前正式主设计为experiment_2。未启动新LLM，不把诊断写成当前主批结果。 | 已采用（timestamp设计与保留发言的内容修复）；实际恢复核验范围见本run README |
| [2026-10-06-01-baseline-anchor/](2026-10-06-01-baseline-anchor/README.md) | 固定曝光数值诊断已完成，候选B没有落地；当前主实验继续保留原B及行为参数。 | 未采用（候选B）；实际恢复核验范围见本run README |
| [2026-10-09-01-activation-calibration/](2026-10-09-01-activation-calibration/README.md) | U/B质疑、文稿对齐、两研究结构及写作安排；九次主实验执行完成，后续在主项目写作。 | 部分采用：理论与文稿文件、两份报告已落地；行为候选未采用；四个离线单元及静态/窗口恢复核验通过 |
| [2026-10-15-01-ica2027-cat-writing/](2026-10-15-01-ica2027-cat-writing/README.md) | ICA 2027 CAT写作、五图、完整中文Word与一句话思维链；中英文定稿、逐句链、写法说明、原批注修订及冻结输入保全。 | 已采用并归档：123个交付文件恢复校验、74块合稿一致性及路径补丁重放通过；原件和实验输出保持，无新实验或Git提交 |

| [2026-10-15-02-timestamp-bdr-ablation/](2026-10-15-02-timestamp-bdr-ablation/README.md) | timestamp-interest B/D/R九次正式LLM消融、同seed Full配对及D/R逐周机制证据；首次403、布局修正和并行交接保全。 | 已采用并归档：配置恢复900 profiles/8100公式/26测试及控制器补丁重放通过；正式12单元27主指标复算、201项采用材料恢复通过；无新LLM或Git提交 |
| [2026-10-18-01-ica2027-text-verification/](2026-10-18-01-ica2027-text-verification/README.md) | 按作者逐条要求核实与润色正文，保留第四章（三）和第五章前三节候选、理论与数据来源核查结论。 | 未执行正式采用并归档：归档前6文件解包逐字节核对通过，保留归档时Word快照及文件指纹；未改作者Word或正式主稿，未作全文正确性结论，无新实验或Git提交 |

各run README为本run归档结果与恢复说明入口。旧路径 `runs/<run-id>/` 对应现在的 `runs/archive/<run-id>/`；历史manifest、checkpoint、日志及来源哈希不批量改写。归档适配前源码在各run的recovery/original_sources，原tmp证据在historical_tmp。恢复包未复制凭据，复现输入按冻结校验和核对，不从当前活跃run读取私有候选文件。
