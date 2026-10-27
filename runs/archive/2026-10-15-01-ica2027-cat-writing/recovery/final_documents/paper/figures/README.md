# 正文图1—图5

依据当前[定稿主稿](../manuscript/manuscript.accepted.md)的图位和图注制作，数据来自既有冻结结果，不运行新仿真或新编码。图号与正文一一对应；本文件夹先交付图件，正文图位暂保留。

## 作图契约

| 图 | 要呈现的结论及面板职责 | 数据与统计 | 版式 |
|---|---|---|---|
| 1 | 悼念集中与玩梗晚期增长；a五类构成，b悼念和玩梗数量 | 两平台原分类周计数，先合并计数再计算比例；无抽样误差条 | 两面板量化网格 |
| 2 | 同一总体顺序下的平台分化；a抖音，b小红书 | 同周同口径的五类比例，共用坐标及颜色 | 两面板量化网格 |
| 3 | 三种制度下固定作者群体的供给轨迹分化；a—c周度数量，d晚期玩梗型份额 | 原timestamp_v1九次；细线/点为单次重复，粗线/横线为三次均值；份额先在run内计算 | 四面板量化网格 |
| 4 | 个人接触、参与及生成帖再流通相互衔接；a同类接触，b发帖率，c生成帖跨群体展示 | W19—W22，各制度三个seed的取值与均值 | 三面板量化网格 |
| 5 | B、D、R干预改变参与并重组供给和可见位置；a总供给，b玩梗型参与，c总体参与，d供给份额，e跨群体展示 | 兴趣制度内三个配对seed；原完整模型与正式消融，连线保留配对 | 五面板量化网格 |

统一使用Python/Matplotlib、白底、英文图内文字、固定类别配色；宽180 mm（图5为183 mm），字体不小于7 pt。每图导出600 dpi PNG、含可编辑文本的PDF与SVG。中文图题、图注及各项分母见下文。图3—5展示实际三次重复，不做显著性检验或推断性置信区间。

## 文件

| 图号 | 内容 | PNG预览 | PDF排版 | SVG编辑 |
|---|---|---|---|---|
| 1 | 两平台合并的内容构成与悼念、玩梗数量 | [PNG](figure_01_observed_pooled.png) | [PDF](figure_01_observed_pooled.pdf) | [SVG](figure_01_observed_pooled.svg) |
| 2 | 抖音与小红书的内容构成比较 | [PNG](figure_02_observed_platforms.png) | [PDF](figure_02_observed_platforms.pdf) | [SVG](figure_02_observed_platforms.svg) |
| 3 | 三制度的作者类型供给轨迹与晚期构成 | [PNG](figure_03_simulated_trajectories.png) | [PDF](figure_03_simulated_trajectories.pdf) | [SVG](figure_03_simulated_trajectories.svg) |
| 4 | 个人接触、发帖参与与生成帖跨群体展示 | [PNG](figure_04_feedback_exposure.png) | [PDF](figure_04_feedback_exposure.pdf) | [SVG](figure_04_feedback_exposure.svg) |
| 5 | B、D、R组件消融的配对比较 | [PNG](figure_05_bdr_ablation.png) | [PDF](figure_05_bdr_ablation.pdf) | [SVG](figure_05_bdr_ablation.svg) |

[五图合册PDF](all_figures.pdf)适合连续审阅；[全部图件总览](all_figures_preview.png)适合快速浏览；[中英文图题与图注](CAPTIONS.md)说明各面板及统计单位。PDF和SVG为矢量文件，PNG为600 dpi预览；图3、5较高，建议按原宽度查看。

## 复现

从项目根目录运行，默认直接读取本文件夹保存的作图CSV：

```bash
AgentSociety2/.venv/bin/python paper/figures/scripts/build_figures.py
```

若需从原始项目资产重新核对并整理所有数据，使用`build_figures.py --prepare`；三个数据整理脚本只读既有数据。重新整理需要原始工作簿、原始实验状态和来源清单中的项目文件；仅重画图件不需要重新读取大体量状态文件或调用LLM。

字体与PDF几何检查：

```bash
AgentSociety2/.venv/bin/python paper/figures/scripts/run_qa.py
```

项目解释器中没有PyMuPDF时，`run_qa.py`可通过`--pymupdf-path`复用现有包目录；本次使用既有uv缓存的PyMuPDF 1.25.2，未安装依赖或改动项目环境。实际命令及结果见[QA记录](qa/README.md)。

## 统计及来源要点

图1、2采用已定稿的两平台主分类矩阵，实际周范围为W05—W22；合并比例从两平台计数相加后计算。图内五类为教育、悼念、玩梗、其他讨论和营销。图3—5使用原`timestamp_v1`九次主实验及正式B/D/R消融，未使用旧`anchored_v1`或扩容候选结果。

图3—5的三次重复单位均为seed，先计算每run指标，再取算术均值。细线或点保留每次取值，粗线或黑色短线表示均值；图5连线表示相同seed的完整模型与组件干预。没有平滑、补造周数据、显著性检验或推断性置信区间。

图4c只计来自玩梗型作者的**生成帖**在其他作者信息流中的再次展示；图5e计其他作者所见的**全部玩梗类内容**，包含外部帖与生成帖。两项都以实际获得的信息流条目为分母，不互相替代。

## 数据与复现入口

- [source_data/](source_data/README.md)：逐周、逐run和逐seed作图表，以及原始输入路径与SHA256。
- [scripts/](scripts/README.md)：离线整理、绘图和版式检查脚本。
- [qa/](qa/README.md)：数字核对、轴对齐、字体与碰撞检查、人工视觉检查记录。

原始实验、原始编码和既有图件均不改动。本文图件与旧anchored_v1及后续扩容实验分开使用。
