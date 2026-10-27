# 风格候选定向核对

| 文件 | 内容 |
|---|---|
| baseline.json | Git基线、原图1—5/合集/Word/原CSV保护指纹、参考附件与CSV的SHA |
| build.json | 版式、实际颜色、字体、数据/脚本/输出哈希、十个均值与文字边界 |
| checks.json | 原生SVG/PDF、100行输入与十种子均值、最小8pt、无裁切/文字重叠、原交付字节保持 |
| grayscale.png | 实际候选的灰度校样，仅用于辨识检查 |
| REVIEW.md | 已实际查看候选的独立定向审查 |

此处只核对风格候选的数据身份与图面，不重复原始40run提取。40run数据及科学配置核验仍见上两级qa/fig5_extraction.json和source_data/ablation_seed10_sources.json。候选采用与原图相同的100条CSV观测、10个同seed配对及均值，没有重新运行实验。
