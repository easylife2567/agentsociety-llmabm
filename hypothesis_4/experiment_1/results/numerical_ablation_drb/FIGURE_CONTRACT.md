# D/R/B 数值消融图证据合同

- **核心发现**：检验 anchored_v1 中 B、D、R 三个组成部分是否产生可区分的时间—类型影响；不预设消融方向一定符合理论。
- **证据来源**：`calibrate_speak.simulate` 数值代理；冻结 `data/anchored_utility_prediction.json` 中的 anchored_v1 参数；100 个相同随机种子的配对比较。
- **图件范围**：一张三部分复合图。
- **图件结构**：总发言趋势 + 玩梗表征份额趋势 + 时期×类型配对差值热图。
- **分析范围**：100 个固定类型 Agent，W12–W22，interest 数值代理；full / no B / no D / no R 四条件。
- **视觉中心**：下方面板展示三项消融相对完整模型的类型发言率百分点差。
- **输出文件**：`charts/figure_01_drb_numerical_ablation.png` 与同名 SVG。
- **审稿风险检查**：必须标注这是 numerical proxy 而非正式 ABM/LLM run；误差带仅表示 Monte Carlo 不确定性；表征份额以 Agent 固定类型的供给构成为代理。

## 模板同构堆叠面积对比图

- **核心发现**：Full 与 No B / No D / No R 在周度绝对供给构成上呈现不同的时间签名。
- **证据来源**：`data/drb_ablation_seed_week_type.csv` 中 100 个配对 seed 的 Agent 供给均值；固定注入帖明确排除，与旧公式 (U=D\times R) 的历史数值代理图保持同一 Agent 供给口径；不读取正式 run、replay 或 decision log。
- **图件范围**：三张 Full-vs-ablation 并排对比图，以及一张 Full + 三消融的 2×2 总览图。
- **图件结构**：沿用用户指定模板的堆叠面积、五类 Agent 颜色与顺序及 W13 事件线；四条件统一纵轴 0–80。
- **分析范围**：100 个配对 seed（3000–3099），W12–W22，full / no B / no D / no R。
- **输出文件夹**：`charts/template_stacked_area/`。
- **审稿风险检查**：图中必须直接标注“100-seed numerical proxy mean”“fixed injected posts are excluded”和“No formal replay or LLM run was used”；No B 的 W19–W22 非玩梗供给必须为 0。
