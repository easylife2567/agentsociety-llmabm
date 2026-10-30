# 主方案选择性落地与验收

本级保存2026-10-29用户明确采用授权后的操作和证据；实时状态仅见[run README](../README.md)，不另建进度跟踪。正式入口为[experiment_2](../../../../hypothesis_4/experiment_2/README.md)与[正式分析](../../../../presentation/hypothesis_4/hourly_return_v1/README.md)。

| 直接资产 | 用途 |
|---|---|
| baseline.json | 落地时准确commit、Git状态、两源码起点SHA与原有用户差异保护哈希 |
| mechanism.patch | 本次采用的两源码最终补丁；原候选补丁原字节复制，git apply --check后应用主区 |
| land_assets.py、assets.log、asset_acceptance.json | 仅主实验的选择性代码/配置/20run原始复制与17,932文件SHA验收，不启动运行 |
| manifest_attempt1.json、relocation_attempt1.json | 首次接收草稿；时序核心状态已锁，但replay碎片来源未合并，保留失败背景 |
| main_tests.json、main_tests.log | 正式主区42项相关功能/回归通过，0网络/LLM |
| verify_main_configs.py、main_config_validation.json、.log | 正式30配置、30环境保存恢复、3000份官方profile创建恢复、registry主区路径及科学配对，禁网验收通过 |
| landing_receipt.json | 最终采用范围、正式输出哈希、原用户差异与DOCX保持核验；完成后生成 |
| formal_files/、formal_files_manifest.json | 正式路径适配后的最终新增分析/图表/报告、接收矩阵和综合镜像及目标路径/SHA；原候选包不改写 |

两份已有源码先用保存补丁检查再应用，新测试和30主配置按候选SHA接收。没有运行同时生成E2/E3的候选准备器，也没有接收消融候选；experiment_3原文件保持。旧配置与默认生成入口保留历史身份，新主方案显式next_batch，不能拿旧checkpoint换策略接续。

20份已完成随机/兴趣原始输出复制到正式结果目录，保留原run_id及内部metadata/路径/正文，不删除原位置；时序复用10份现有正式结果。计划、状态、账本、来源审计只复制原件，不手改监督器状态或合并预算。正式manifest解析30份实际正式路径，正式分析器和冻结输入置于presentation，不依赖本run或其workspace。

首份接收草稿仅从时序审计锁了核心状态，遗漏官方replay碎片SHA，正式离线分析因此失败。已按timestamp_v1正式relocation清单逐项核对并合并，首次稿和分析失败日志均保留（后者见正式分析verification/analyze_attempt1.log），之后正式30run分析、绘图及--check通过。没有新LLM请求、仿真重试或修改科学判据。

正式位置重新验证不能由探索测试代替：本轮实际42项全过、30配置和3000profile验收全过；从正式原始重读30run并经官方query-data核对，7份输出确定性一致。与落地前对照时，四份科学表/路径JSON及两张PNG逐字节一致；run_metrics仅时序origin说明变化，summary仅范围/路径/合约哈希变化，科学字段一致。日志及对照见[正式verification](../../../../presentation/hypothesis_4/hourly_return_v1/verification/README.md)。

正文评估位于[manuscript_impact.md](../../../../presentation/hypothesis_4/hourly_return_v1/manuscript_impact.md)，未改DOCX、主稿或论文图；旧组件消融和旧报告仍按旧制度解释。机器analysis含此前旧E3待分析范围，未将其标为完成。此句记录落地当时的边界；2026-10-30本run已归档并保全恢复材料及原始证据，当前入口见上级README。

恢复采用结果时，以baseline.json的commit为代码起点，检查并应用mechanism.patch，复制原files中选定的新测试与experiment_2的30配置，再按formal_files_manifest将本级镜像放到对应正式位置。原始20run由本run已保全的pilot/results和seed_extension/results按接收映射复制、验SHA；时序10run引用既有timestamp_v1冻结资产及relocation哈希，不依赖探索workspace。所需输入/steps仍是记录commit的冻结主资产。随后执行正式42项测试、verify_main_configs.py和正式分析--check；这些操作不授权重新进行LLM仿真。本轮实际在正式位置完成了上述验证，当时没有另建worktree或归档run；本次归档结果见上级README。
