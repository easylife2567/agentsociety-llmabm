# 离线绘图与验收

| 文件 | 职责 |
|---|---|
| paper_plot_style.py | 共用Times/字号/颜色/线型、W13图例、分图编号、SVG/PDF/PNG导出 |
| gen_fig1.py | 图1：合并构成与两类周数量 |
| gen_fig2.py | 图2：两平台周构成、共同坐标 |
| gen_fig3.py | 图3：三制度十组轨迹及晚期份额；180×128mm紧凑排版，运行/均值说明见中文图注 |
| gen_fig4.py | 图4：十组接触、参与、生成帖再展示 |
| gen_fig5.py | 图5：B/D/R各10种子的同seed配对；三上两下五面板，180×112mm |
| extract_fig5_seed10.py | 图5冻结表提取：40完成run，原始Agent/环境/官方replay三路对账 |
| validate_delivery.py | 冻结来源、分母、30run、SVG矢量和PDF字体/文字边界检查 |
| package_delivery.py | 四图等比预览、矢量图册、LaTeX片段及包含最新十种子图5、排除旧三种子候选的ZIP |

绘图脚本读取上一级source_data；不硬编码实验数值、不运行新实验，不导入或修改正式项目模型。当前项目Python来自`.env`的PYTHON_PATH，核心依赖Matplotlib、Pandas、NumPy、Pillow。验收另需PyMuPDF，允许`--pymupdf-path`指定既有包目录，不安装依赖或更改全局环境。旧三种子图5脚本保留在延后目录，当前gen_fig5.py读取最新十种子表。extract_fig5_seed10.py仅在需要从原始资产重新提取时执行；普通重绘只需gen_fig5.py。对既有验收/打包脚本的最终补丁与精确起点见上一级qa/fig5_seed10。
