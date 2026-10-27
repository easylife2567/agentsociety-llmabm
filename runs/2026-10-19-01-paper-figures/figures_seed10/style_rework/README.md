# 图5结构重做：种子图谱与配对差值表

用户指出前一版只是换色、风格变化不足。本轮在原制图run内新增两个结构候选，改变读图组织与图形编码，均采用同一100条冻结观测、10个同seed配对与五项指标。原图1—5、森林绿首版、合集和Word均保留字节，候选尚未统一用于全篇。

## 两种阅读方式

| 方案 | 构图与统计表达 | 尺寸 |
|---|---|---|
| A：种子配对图谱 | 五项指标横向一字排开，seed0—9共享行；每行Full圆点与干预菱形相连，底部独立Mean行显示条件均值 | 180×90mm |
| B：配对差值＋均值表 | 五项指标纵向分行，中列每点为干预−同seed Full，黑菱形为差值均值；右侧两列保留Full/干预的原单位均值 | 180×104mm |

A保留逐seed的两端数值与配对关系，适合横向紧凑排版。B集中表达变化方向和配对幅度：图5a单独采用帖/周标尺，图5b—e共同采用百分点标尺，两个零线位置对齐。B没有把绝对百分比与百分点混为一谈，也没有对不同单位共用一条数值标尺。

颜色仍采用参考的森林绿、赭黄、陶土橙和橄榄绿：Full森林绿，B/D/R条件各用赭黄/陶土/橄榄。白底、衬线字体、最小8pt，使用轻线与克制表格层级；不使用大色块、图像装饰或密度拟合。

## 本级资产

| 文件/目录 | 用途 |
|---|---|
| figure_05_seed_atlas_v1.svg/.pdf/.png | A版原生可编辑SVG、矢量PDF、400dpi预览 |
| figure_05_effect_table_v1.svg/.pdf/.png | B版对应输出 |
| comparison_layouts.png | A/B等比版式预览，供作者判断 |
| CAPTION_seed_atlas_ZH.md | A版的一段中文图注 |
| CAPTION_effect_table_ZH.md | B版的一段中文图注，明确配对差值与百分点 |
| figure_05_seed_atlas_v1_include.tex、figure_05_effect_table_v1_include.tex | 各自PDF与图注的LaTeX插入片段 |
| gen_fig5_seed_atlas.py、gen_fig5_effect_table.py | 一图一个复现脚本 |
| style_rework_common.py | 当前两候选共用字体、颜色、冻结数据核验与矢量导出 |
| source_data/ablation_seed10_metrics.csv | 上一级100条观测CSV的精确副本 |
| [qa/](qa/README.md) | 原资产保护、数值/单位复算、字体/越界/碰撞与独立审查 |

## 复现与状态

从项目.env仅读取PYTHON_PATH，使用该解释器分别运行本目录两个gen_fig5脚本；依赖现有Matplotlib、Pandas、NumPy与Times New Roman。绘图脚本只读本目录CSV，输出仅写本目录；无网络或LLM调用，不运行仿真。全部实现为本轮新增文件，无既有代码修改，不需要.patch或worktree；尚未commit或归档。当前候选供作者比较，不自动替换现有交付图或Word。
