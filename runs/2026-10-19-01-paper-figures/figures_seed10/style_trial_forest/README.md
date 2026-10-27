# 图5风格候选：森林绿、赭黄与陶土橙

用户2026-10-26要求参照所附“Scientific Color Inspiration Board”尝试图5，待作者判断合适后再考虑统一全篇。本目录是独立风格候选；主图1—5、原交付合集、中文图注和Word字节保持。数据与科学含义沿用已核验的十种子图5，当前未采用为全篇风格。

## 色彩与版式

| 语义 | 配色 | 形状 |
|---|---|---|
| Full完整模型 | 森林绿 #1B3D2E | 圆点 |
| B=0 | 赭黄 #D4A85A | 菱形，炭灰描边 |
| D=1 | 陶土橙 #C76A4F | 菱形，炭灰描边 |
| R=1，图5c/d/e固定同色 | 橄榄绿 #6B7F5B | 菱形，炭灰描边 |
| 跨种子均值 | 炭灰 #3A3A3A | 短横线 |

参考图的森林绿衬线编号、细线分格和自然配色被转化为论文图版层级。白底，不加大面积色块、渐变或装饰图像。淡灰绿色连线连接同seed；形状、位置与条件标签共同辨识，灰度校样也保留圆/菱形差别。各面板窗口、轴限、五项指标与原图保持同一口径。

幅面180×112mm，Times New Roman，基准9pt、最小8pt。SVG保留原生文字与路径，PDF为矢量，PNG为400dpi预览。三项预设B/D/R指标在上排，R干预的供给与信息接触指标在下排，保持三上两下。

## 本级资产

| 文件/目录 | 用途 |
|---|---|
| figure_05_bdr_ablation_forest_v1.svg | 可编辑矢量候选 |
| figure_05_bdr_ablation_forest_v1.pdf | 矢量排版候选 |
| figure_05_bdr_ablation_forest_v1.png | 实际导出预览 |
| comparison_previous_vs_forest.png | 左原版、右候选的等比比较，仅用于选风格 |
| CAPTION_ZH.md | 一段中文图注，补充候选配色映射 |
| latex_include.tex | 使用候选PDF的LaTeX片段 |
| gen_fig5_forest.py | 独立复现脚本，CSV驱动，不导入或修改主项目 |
| source_data/ablation_seed10_metrics.csv | 已核验100条面板观测的字节副本，与原表SHA一致 |
| reference_palette.jpg | 用户附件的只读副本，供色彩/版式参考 |
| [qa/](qa/README.md) | 原资产保护、原生矢量/字号/文字几何与灰度校样 |

## 复现

从项目.env仅读取PYTHON_PATH，使用该解释器运行本目录gen_fig5_forest.py；需要现有Matplotlib、Pandas、NumPy与Times New Roman（字体缺失时使用DejaVu Serif）。脚本只读取本目录CSV并输出本目录图件，无LLM/网络调用。新增文件直接保存最终实现；这次没有修改已有代码，不需要代码补丁或项目worktree，未commit或归档。
