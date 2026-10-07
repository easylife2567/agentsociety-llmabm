# 到达时机四格诊断的量化资产

本目录保存冻结四格的分析结果，不替代原始引擎run。解释、研究判断和正文逐条核查见[任务入口](../../../runs/2026-09-29-02-injection-timing/README.md)。原四格结果仅描述seed 0；新增数值回放的条件与边界单独登记，不作为新LLM实验结果。

| 本级资产 | 内容与使用 |
|---|---|
| README.md | 本目录说明和一级索引 |
| summary.json | 全窗/后期Y、S、A、O、E、作者生产、词表测量、候选分布及预登记交互 |
| weekly.csv | 四格44行周级结果，包括提前曝光、历史来源、生命周期排除 |
| future.csv | 按条件、周、类别区分数值feed及实际生成上下文的未来曝光 |
| sources.csv | 全部曝光按来源、置顶/保底/抽样和内部类型分解 |
| initial.csv | W13、W19首批前100人的累计同类曝光、R、既有供给和候选池 |
| historical.csv | 两个anchored_v1历史s0的完整周作者口径桥接 |
| decisions.csv | 4400条行动的作者类型、成功发布、词表主类/信号及效用/R；不含正文 |
| 2026-10-06-01-numerical-decisions.csv | timestamp原轨迹、固定发布安排屏蔽和有限支持闭环共6,004条已提交数值行动；不是6,004次模型调用 |
| 2026-10-06-02-week-boundary.csv | 现实UTC/上海周界的五类非噪音内容份额差，营销保留在分母 |
| 2026-10-06-03-numerical-summary.json | 无LLM验证的复现结果、拒答影响、归档正文支持边界、日期原型检查及输入哈希 |
| 2026-10-06-04-timestamp-interest-numerical-expectation.png / .svg | chart3b样式的interest条件性拟发布机会；219次，假设其他生成通过，非完整闭环预测 |
| 2026-10-06-05-timestamp-random-numerical-expectation.png / .svg | 同口径random零干预对照；169次，纵轴同为0–80 |
| 2026-10-06-06-numerical-expectation-weekly.csv | 两臂22行五类作者拟发布机会及归档发布数排除已确认拒答后的周表 |
| 2026-10-06-07-numerical-expectation-provenance.json | 预期图指标、固定供给边界及源CSV、摘要、模板、绘图脚本的哈希 |
| 2026-10-07-01-content-decisions.csv | 794条原归档的派生修正文、原文编辑坐标、初始状态与正文来源；原始run只读 |
| 2026-10-07-02-content-weekly.csv | 四格44行作者类型保留发布数，逐项等于原周表；不驱动新库存 |
| 2026-10-07-03-content-summary.json | 794保留、729原文/64局部修正/1离线兜底、20必查与45额外待核查、4,400次U误差0及源哈希 |
| 2026-10-07-05-content-preload-interest.png / .svg | preload-interest内容修复后保留234条；chart3b样式 |
| 2026-10-07-06-content-timestamp-interest.png / .svg | 既有timestamp-interest静态修正后保留214条；未新增run |
| 2026-10-07-07-content-preload-random.png / .svg | preload-random同口径177条；统一0–80轴 |
| 2026-10-07-08-content-timestamp-random.png / .svg | 既有timestamp-random同口径169条；统一0–80轴 |
| 2026-10-07-09-content-overview.png / .svg | 四格固定供给数值预期总览，沿用chart3b五类配色、事件线及0–80轴；标注各周总数 |
| 2026-10-07-10-content-overview-provenance.json | 总览图的四格合计、作者分类口径、源周表/摘要/模板/脚本SHA-256 |
| input_hashes.json | 原始四格及历史Agent账本、配置清单、复算器与判类依据SHA-256 |
| replay_checks.json | 官方analysis query-data的SQL和四格返回，独立核对11周及主要总量 |
| knowledge_summary.json | 555条实际阅读覆盖检查、问题帖计数及直接曝光；引用逐条判读哈希 |
| exposure.png / exposure.svg | 周主曝光Y轨迹；PNG阅读，SVG编辑 |
| production.png / production.svg | 周玩梗作者发帖数；PNG阅读，SVG编辑 |
| semantic_signal.png / semantic_signal.svg | 周独立玩梗词表信号份额；不等同互斥类别或人工金标 |
| timestamp_interest_s0__chart3b_agent_supply_stacked_area.png | timestamp-interest五类Agent周发帖堆叠，复用用户指定chart3b模板，统一0–80轴 |
| timestamp_random_s0__chart3b_agent_supply_stacked_area.png | timestamp-random同口径同尺度堆叠图 |
| timestamp_agent_supply_by_type.csv | 两臂22行周×五类成功发帖数，与行动账本逐项一致 |

复现：使用工作区`.env`中的Python，依次执行任务内`2026-09-30-04-analyze.py`、`2026-09-30-09-plot.py`、`2026-09-30-11-knowledge-coverage.py`。三者只读原始run，不调用外部模型；最后一步使用任务内已经完成的逐条阅读记录，不重新自动“判语义”。官方SQL保存在replay_checks.json，可逐条按其run_id对应的replay路径执行。

分母与边界：主窗口W19–W22，每run400次计划行动、4000实际槽；单seed不做显著性/置信区间。source=agent的内部type来自固定作者，不代表正文互斥语义；问题帖曝光不是错误细节传播或效应偏差的因果界限。

堆叠图单独复现：运行任务内`2026-09-30-12-timestamp-stacked-area.py`。图中类型表示固定作者类型，不是正文语义重新判类；真实帖按实际发布时间可见，Agent生成帖次周才可推荐。图形直接复用`hypothesis_4/experiment_1/plot_run_charts.py`的`chart3b_agent_supply_stacked_area`，不修改模板或原始run。

数值验证单独复现：使用.env中的Python运行任务内`2026-10-06-01-numerical-check.py`。脚本设置依赖的本地价格表并禁止网络连接，只使用实际环境、纯效用函数与原始归档正文。固定发布安排分支不能解释为完整闭环新曲线；interest有限支持闭环在W17遇到不同生成上下文后停止，random是零干预控制。

数值预期图单独复现：运行任务内`2026-10-06-02-plot-numerical-expectation.py`。色块计重算达到发言阈值且非已确认拒答的行动，假设其余生成均通过验收；虚线计归档发布排除已确认拒答，其他正文未经本图重新验证。只汇总数值CSV，不运行环境或生成接口。chronological仅提供样式，图示条件仍为timestamp-interest/random。

内容修复数值图单独复现：运行任务内`2026-10-07-03-content-numerical-expectation.py`，无模型/网络。归档正文作局部修正、拒答作标明来源的离线兜底，发布量全部保留；额外45条筛查仍待人工确认。来源正文是服务后保存文本，完整服务字段不能追回。色块与原发布虚线逐周重合是固定供给的数量守恒，不是新闭环结果。正文改变仍可能影响以后interest feed，不能据本图承诺新实验全窗数量或现实拟合。chronological只提供样式，timestamp推进仍暂停；实现解释、功能验收和最终patch见任务结果报告。

四格总览单独复现：使用.env指定Python运行任务内`2026-10-07-06-content-overview.py`。只读取已验收周表，检查11周完整性、作者分组之和、原发布量逐周一致及794条合计；不执行环境或模型。图中各周数字是保留发布数，不能当作新闭环生成结果。
