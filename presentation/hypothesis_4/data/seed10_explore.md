# 三臂10seed探索与口径复验

范围为30次完整主实验、330个run×week，3000份Agent工作区，总成功发布6041帖。新批原失败random_s7不进入科学汇总；interest_s6采用resume1副本。旧99行周表和原论文图3/4的9行晚期供给及接触指标均逐格一致。

核心窗仍W19–W22，作者类型posted供给；晚期份额先各seed内作比再均值。每run玩梗发帖率分母76机会，同类所见分母760槽，跨群体生成玩梗帖再展示分母3240槽；10数值槽位不等于LLM读取的前5条。

初步方向：旧3和新7内兴趣、时序均高于随机，时序总体高于兴趣。旧3晚期玩梗份额随机10.32%、兴趣65.61%、时序73.30%；新7为10.98%、69.70%、75.74%。不能把模型与seed范围混杂的批次均值差归因模型升级。

统计单位是seed；固定15个配对指标×对比/层（五指标含帖数与发帖率的线性重复，校正偏保守），精确双侧符号翻转检验须假设零差对称，t均值区间须作分布近似。旧3、新7精确p值分辨率有限，新7的15项Holm校正均未过0.05；混合10seed的p不能当跨模型等价证据。剔除任意一个seed后的均值方向仍正。

官方harness旧H4E1停在claims，使本轮intake实际返回BLOCKED_BY_PHASE；先保存seed10_prior_harness.json及state.pre_seed10.yaml再重新intake。intake只支持experiment_2/run/replay且该路径不存在，CLI没有多run数据源入口；仅用已安装state API把db_path设为本轮可追溯的seed10_metrics.sqlite，未改研究progress JSON或原始run，其他阶段操作仍用官方CLI。
