# D/R/B 数值消融图证据合同

- **核心发现**：检验 anchored_v1 中 B、D、R 三个组成部分是否产生可区分的时间—类型影响；不预设消融方向一定符合理论。
- **证据来源**：`calibrate_speak.simulate` 数值代理；冻结 `data/anchored_utility_prediction.json` 中的 anchored_v1 参数；100 个相同随机种子的配对比较。
- **图件范围**：一张三部分复合图。
- **图件结构**：总发言趋势 + 玩梗表征份额趋势 + 时期×类型配对差值热图。
- **分析范围**：100 个固定类型 Agent，W12–W22，interest 数值代理；full / no B / no D / no R 四条件。
- **视觉中心**：下方面板展示三项消融相对完整模型的类型发言率百分点差。
- **输出文件**：`charts/figure_01_drb_numerical_ablation.png` 与同名 SVG。
- **审稿风险检查**：必须标注这是 numerical proxy 而非正式 ABM/LLM run；误差带仅表示 Monte Carlo 不确定性；表征份额以 Agent 固定类型的供给构成为代理。
