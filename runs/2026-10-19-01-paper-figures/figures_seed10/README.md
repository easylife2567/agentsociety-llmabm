# V5图件重制：十组主实验与组件干预

2026-10-24依据ICA2027-V5.docx完成图1—4十组主实验版本；2026-10-26用户确认消融运行完成，要求按相同规范补制图5。当前交付图1—5，每图英文SVG、矢量PDF与PNG预览，中文图注独立提供。图5采用兴趣制度Full与B=0、D=1、R=1各10个种子的同seed配对结果；旧三种子候选保留用于对照。正式Word、既有paper图件、实验数据及流水线未改；没有启动新实验、commit、push或归档。

## 图件与阅读顺序

| 图 | 分图及读图顺序 | 数据与重复单位 | SVG |
|---|---|---|---|
| 1 | 1a合并五类构成→1b悼念和玩梗数量 | 真实帖文，W05—W22；五类46,602条 | [图1](figure_01_observed_pooled.svg) |
| 2 | 2a抖音→2b小红书，同轴比较 | 平台内各周五类比例；不把面板面积作平台流量比例 | [图2](figure_02_observed_platforms.svg) |
| 3 | 3a随机→3b时序→3c兴趣轨迹→3d晚期供给份额 | 每制度10个种子，共30次完整主运行 | [图3](figure_03_simulated_trajectories.svg) |
| 4 | 4a接触→4b参与→4c生成帖跨群体再展示 | W19—W22，每制度10个种子的指标与均值 | [图4](figure_04_feedback_exposure.svg) |
| 5 | 上排5a—c预设B/D/R指标→下排5d/e供给与可见位置 | 兴趣制度，Full与三项干预各10seed，40run单元，其中Full复用主实验 | [图5](figure_05_bdr_ablation.svg) |

图1—3的时间轴均有W13虚线，英文图例明确写出“Zhang Xuefeng's death (24 Mar 2026)”。图4汇总W19—W22；图5汇总W19—W22及W14—W18，窗口标在各面板上。图内编号完整标为Fig. 1a等；不放整体图题或长段图注，实验条件及窗口保留为必要标签。

## 本级资产

| 文件/目录 | 用途 |
|---|---|
| `figure_01_observed_pooled.svg/.pdf/.png` | 图1，可编辑主图、矢量排版与预览 |
| `figure_02_observed_platforms.svg/.pdf/.png` | 图2，可编辑主图、矢量排版与预览 |
| `figure_03_simulated_trajectories.svg/.pdf/.png` | 图3，十组主实验轨迹与晚期份额 |
| `figure_04_feedback_exposure.svg/.pdf/.png` | 图4，十组主实验过程指标 |
| `figure_05_bdr_ablation.svg/.pdf/.png` | 图5，十种子配对组件干预的五面板图 |
| [style_trial_forest/](style_trial_forest/README.md) | 首轮森林绿配色候选，保留用于对照；用户反馈结构变化不足 |
| [style_rework/](style_rework/README.md) | 当前两种结构候选：五列种子配对图谱、五行配对差值与均值表；独立SVG/PDF与各自中文图注 |
| [CAPTIONS_ZH.md](CAPTIONS_ZH.md) | 可供正文采用的五段中文图注 |
| [REVISION_ADVICE.md](REVISION_ADVICE.md) | 新旧数字对照、可替换段落、补入十种子图5后的正文数值与章节调整 |
| [all_figures_preview.png](all_figures_preview.png) | 五图等比缩略总览，仅用于预览 |
| [all_figures.pdf](all_figures.pdf) | 五页矢量图册 |
| [latex_includes.tex](latex_includes.tex) | 五图PDF与中文图注的LaTeX插入片段 |
| [figures_seed10_delivery.zip](figures_seed10_delivery.zip) | 图1—5、中文图注、修改意见、独立脚本及冻结作图CSV；不含旧三种子图5或原Word |
| [source_data/](source_data/README.md) | 本轮图1—5冻结输入、来源与十组分析说明 |
| [scripts/](scripts/README.md) | 一图一个脚本、共享样式和离线验收 |
| [qa/](qa/README.md) | 数据身份、字体、裁切、文字碰撞与独立审查记录 |
| [original_media/](original_media/README.md) | V5内嵌位图，只读对照，不是本次SVG输出 |
| [legacy_v5_source_data/](legacy_v5_source_data/README.md) | V5原三种子基线，用于修改意见对照，不用于图3、4 |
| [deferred_ablation/](deferred_ablation/README.md) | 2026-10-24暂存的旧三种子消融候选，仅保留历史对照，不进入当前十种子交付包 |

## 统计、样式与使用边界

原始两平台语料49,930条与五类分析46,602条分开说明；不把被排除的噪音和存疑条目计入占比。五类仍含营销。图3、4读取最新`seed10_runs.csv`与`seed10_weekly.csv`，seed 0—9齐全；先每run求指标，再跨种子平均，重复单位为seed。失败尝试没有进入已选定的30次完整运行。按用户已采纳的模型版本等价约定合并原3组与新增7组，精确批次标识仍在来源清单。

图3只计成功发布的智能体帖，以固定作者类型归属；图4a同类接触包含外部帖与生成帖，图4c的分子只包括玩梗型作者生成帖。每次运行的相关分母分别为760条同群体feed、76次表达机会、3,240条其他作者feed。十组表总成功发帖数6,041，周表与运行表一致。图中不把实际重复的范围称为95%置信区间，也不把过程相关称为回流净因果效应。

五图统一180mm宽、Times New Roman、9pt基准字体，最小导出字体8pt；图1/2高99mm、图3高128mm、图4高98mm、图5高112mm。白底、语义类别配色固定，曲线另用线型/点形区分，关键数字作有限标注。SVG保留文字、路径、viewBox及`preserveAspectRatio`，没有嵌入位图；PDF同为矢量，PNG只是400dpi预览。缩放矢量图不会降低像素分辨率，但插入Word仍须锁定纵横比，不能分别拉伸宽、高。

已完成数据表/来源指纹核对、SVG结构检查、实际PDF字体与文字几何检查、五张最终PNG查看，以及paper-figure指定模型gpt-5.6-sol的独立质量审查；结果见qa。图1—4的原始结果完整性沿用既有核验；图5已重新读取所需40run的环境/Agent/replay并逐源对账，全程没有重跑仿真。投稿时仍需在实际Word或LaTeX版面检查字号与跨栏位置。

图5从40次实际完成运行的环境、Agent及官方replay读取100条面板观测；对应44,000次完整唯一决策。三个预设指标分别使用4周、76次玩梗型表达机会、500次全体表达机会为分母。图5e计入外部帖和生成帖，分母为每run的3,240次其他作者feed展示；图4c只计生成帖。旧失败或中断的前置目录通过完批清单筛选，未作为额外重复计入。逐源指纹、模型标识、科学配置对齐及旧三种子数值复现见source_data/ablation_seed10_sources.json与qa/fig5_extraction.json。

图3最新排版将画幅从180×150mm收紧为180×128mm；两条重复说明由现有中文图注承载，五类作者图例与W13事件各一行。数据、字号及图1/2/4保持原样，修订Word中的既有嵌图未自动替换；补丁与定向核对见[qa/fig3_compact_footer/](qa/fig3_compact_footer/README.md)。

## 复现

在当前项目中，从`.env`读取`PYTHON_PATH`（不要输出其他凭据），依次运行`scripts/gen_fig1.py`至`gen_fig5.py`。五张绘图脚本只读本目录冻结CSV，不读取原始重型运行状态或调用LLM。共用样式和一图一个脚本随交付包提供。

离线验收使用`scripts/validate_delivery.py`；PDF检查依赖PyMuPDF，本机可复用既有缓存包而不安装依赖：

```bash
AgentSociety2/.venv/bin/python runs/2026-10-19-01-paper-figures/figures_seed10/scripts/validate_delivery.py --pymupdf-path /Users/easylife/.cache/uv/archive-v0/gazd_6nNK5VOozdKrmrr4
```

图5新增独立绘图和提取脚本；对既有验收/打包脚本的改动由[最终补丁](qa/fig5_seed10/fig5_delivery_extension.patch)应用，起始副本、指纹与恢复核验见[qa/fig5_seed10/](qa/fig5_seed10/README.md)。独立文档/绘图不依赖项目引擎，无需项目worktree。旧版框架图与原图1—5均保留。
