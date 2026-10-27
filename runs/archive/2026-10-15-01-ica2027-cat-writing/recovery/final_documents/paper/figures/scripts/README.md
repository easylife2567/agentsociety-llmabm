# 离线整理、绘图与检查

| 文件 | 职责 |
|---|---|
| [build_figures.py](build_figures.py) | 读取本文件夹的CSV，统一绘制五图、五页PDF合册和预览总图；`--prepare`先执行三个整理脚本 |
| [prepare_observed.py](prepare_observed.py) | 核对第三章采用矩阵及原始已标注工作簿，整理图1、2 |
| [prepare_simulation.py](prepare_simulation.py) | 对照九run原ENV、Agent状态和正式周供给，整理图3、4 |
| [prepare_ablation.py](prepare_ablation.py) | 从正式周供给及接触汇总重算图5，再交叉核对run指标及配对结果 |
| [run_qa.py](run_qa.py) | 导出PDF字体、文本碰撞、真实页面尺寸及SVG文本检查 |
| [audit_panel_alignment.py](audit_panel_alignment.py) | 绘图时检查最终轴区域、面板字母及间距；1.5 pt容差 |
| [audit_pdf_text.py](audit_pdf_text.py) | 导出PDF有效字体大小检查，最低5 pt |
| [audit_figure_collisions.py](audit_figure_collisions.py) | PyMuPDF检查文本重叠、与线条碰撞及页面裁切 |
| [validate_figure.py](validate_figure.py) | 绘图源码的字体、导出、采样与不确定性编码预检查 |

项目环境为`AgentSociety2/.venv/bin/python`。核心绘图依赖Matplotlib、NumPy、Pandas、Pillow；从原始工作簿重整数据还使用openpyxl。PDF几何检查使用PyMuPDF。软件实际版本保存在[build_manifest.json](../qa/build_manifest.json)。

后四份通用审计脚本原样复制自本机`nature-skills:nature-figure/scripts/`，以技能提供的接口进行检查；原始位置为`/Users/easylife/.agents/skills/nature-skills-nature-figure/scripts/`。复制到此处使重画不依赖该技能私有路径，没有改写审计阈值。

默认重画只需要本文件夹已整理的CSV；完整重整脚本需要来源JSON列出的项目原始资产。所有脚本均不运行仿真、不调用LLM、不写入原始输入。
