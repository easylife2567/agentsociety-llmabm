# 数字与版式核验

本次五图均完成数据核对、最终PDF字体/碰撞检查、轴对齐检查，以及各面板和整图的视觉查看。主稿SHA256前后保持`7b82052396fcd4119b89064da75b0b85bdbdcddd928d7ce8c1b7d86c1bd969c6`；未改正文或原始数据。

## 文件组

| 文件 | 用途 |
|---|---|
| [build_manifest.json](build_manifest.json) | 主稿版本、绘图环境、尺寸、配色及15份单图导出指纹 |
| [export_checks.json](export_checks.json) | 五图PDF字体/碰撞/对齐结果、SVG文本节点数、真实页面尺寸 |
| [package_checks.json](package_checks.json) | 15份导出与5份CSV指纹、五页图册、正文未变、脚本语法与本地链接核验 |
| [source_preflight.json](source_preflight.json) | 源码预检；18项通过、3项提示、无FAIL |
| [simulation_checks.json](simulation_checks.json) | 九run完成记录、1818帖与495项周类型计数及图3/4指标交叉核对 |
| [ablation_checks.json](ablation_checks.json) | 图5五个配对指标，55项数值交叉核对 |
| `figure_*.alignment.json`、`.alignment.svg` | 最终面板几何与仅供检查的轴框示意图；五图均PASS |
| `figure_*.fonts.json` | 最终PDF字体检查，无低于5 pt的文本 |
| `figure_*.collisions.json`、`.collisions.pdf` | 最终PDF文本/线条检查及诊断PDF；五图均PASS，无FAIL/WARN |

图1、2的数字核对另见[source_data/observed_checks.json](../source_data/observed_checks.json)。`.alignment.svg`只含检查用矩形，`.collisions.pdf`属于诊断副本；论文使用上一级的正式PDF/SVG。

## 实际执行

```bash
AgentSociety2/.venv/bin/python paper/figures/scripts/build_figures.py
AgentSociety2/.venv/bin/python paper/figures/scripts/run_qa.py --pymupdf-path /Users/easylife/.cache/uv/archive-v0/gazd_6nNK5VOozdKrmrr4
```

使用已存在的PyMuPDF 1.25.2缓存包，未修改项目解释器依赖。源检查的三项提示已逐项处理：

1. 没有TIFF：本次交付为矢量PDF/SVG及600 dpi PNG，不声称已核对会议最终上传格式。
2. 源扫描器未识别`mm()`转换的静态宽度：已从最终PDF测得图1—4宽180 mm、图5宽183 mm，与作图契约一致。
3. 没有传统误差条：图3逐一显示每seed细线和晚期散点，图4显示每seed散点，图5显示三个配对取值及连线；所有图同时保留均值，不以n=3构造推断性区间。

## 逐面板视觉与含义检查

| 面板 | 独立证据职责 | 中心与重复展示 | 图例、尺度、对齐及文本 |
|---|---|---|---|
| 1a | 合并内容构成 | 原始周计数之比例；完整所用样本，无误差条 | W05—W22、五色与图2一致；通过 |
| 1b | 悼念峰与玩梗数量增长 | 原始数量；不同颜色和点形 | 同时间轴、W13虚线；末刻度无重叠；通过 |
| 2a | 抖音构成 | 原始平台周比例 | 与2b同轴同色；通过 |
| 2b | 小红书构成 | 原始平台周比例 | 与2a同轴同色；通过 |
| 3a | 随机制度轨迹 | 三条细线及均值 | 同周与数量范围；通过 |
| 3b | 时序制度轨迹 | 三条细线及均值 | 同周与数量范围；通过 |
| 3c | 兴趣制度轨迹 | 三条细线及均值 | 同周与数量范围；通过 |
| 3d | 晚期供给构成 | 三seed点和均值短线 | 比例0—100%；分母为全部生成帖；通过 |
| 4a | 玩梗型作者同类接触 | 三seed点和均值短线 | 实际feed条目分母，制度共用行；通过 |
| 4b | 玩梗型作者参与 | 三seed点和均值短线 | 表达机会分母，制度共用行；通过 |
| 4c | 生成帖跨群体再展示 | 三seed点和均值短线 | 仅生成帖分子、其他群体全部feed分母；通过 |
| 5a | B支撑常态参与 | 三配对seed、均值 | W19—W22、帖/周；通过 |
| 5b | D干预的晚期参与变化 | 三配对seed、均值 | W19—W22、表达机会分母；通过 |
| 5c | R干预的退潮期参与变化 | 三配对seed、均值 | W14—W18、全体表达机会分母；通过 |
| 5d | R干预后供给构成 | 三配对seed、均值 | W19—W22、全部生成帖分母；通过 |
| 5e | R干预后跨群体可见份额 | 三配对seed、均值 | W19—W22、含外部/生成的玩梗类别分子；通过 |

面板字母、图例、轴标题和刻度已检查；首次渲染发现的末周刻度和图5说明重叠已在最终版本修复。自动检查只证明本次导出满足所检项目，不代替整稿排版验收。
