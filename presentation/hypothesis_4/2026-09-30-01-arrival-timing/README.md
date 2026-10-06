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
