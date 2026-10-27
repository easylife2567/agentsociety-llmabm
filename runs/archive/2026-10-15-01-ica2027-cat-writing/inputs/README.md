# 写作输入冻结

本目录保存run初始化时实际读取的非敏感文稿与规范副本。目标、实时状态和下一步见[上一级README](../README.md)；所有来源路径、字节数及SHA256见[sources.json](sources.json)。这些文件含任务开始前已有未提交材料，不能用Git HEAD替代其内容，也不算本run新增研究成果。

## 本级资产

| 文件 | 来源与身份 |
|---|---|
| [sources.json](sources.json) | 九份冻结输入的原路径、快照路径与内容指纹；包括上一级上传README原始副本 |
| [initial_git_status.txt](initial_git_status.txt) | 创建本run之前主工作区Git状态 |
| [project-agents.md](project-agents.md) | 项目AGENTS读取时快照；执行时仍核对现行项目规范 |
| [manuscript.accepted.md](manuscript.accepted.md) | 当前可检索合稿；定稿与待重写部分按原标记区分 |
| [manuscript.before_chapter_3.md](manuscript.before_chapter_3.md) | 第三章采用前新增快照，保留已采用二（二）及旧第三章；来源与SHA256见上一级第三章定稿记录，不属于初始化九份输入 |
| [manuscript.before_chapter_4_1.md](manuscript.before_chapter_4_1.md) | 第四章章首与（一）采用前完整快照；来源与SHA256见上一级第四章定稿记录，保留旧版本供追溯 |
| [manuscript.before_chapter_4_2.md](manuscript.before_chapter_4_2.md) | 第四章（二）采用前完整快照，保留旧（二）与旧图4a/4b；SHA256见上一级section_4_2定稿记录 |
| [manuscript.before_chapter_4_3.md](manuscript.before_chapter_4_3.md) | 第四章（三）采用前完整快照，保留旧数值代理消融与旧图5；SHA256见上一级section_4_3定稿记录 |
| [manuscript.before_chapter_4_closing.md](manuscript.before_chapter_4_closing.md) | 第四章章末采用前完整快照，保留此前各节定稿与第五章旧稿；SHA256见上一级README |
| [manuscript.before_chapter_5.md](manuscript.before_chapter_5.md) | 第五章采用前完整快照，保留旧第五章与补全DOI前的参考条目；SHA256见上一级section_5定稿记录 |
| [INTAKE_AUDIT.md](INTAKE_AUDIT.md) | 正文接入审计，时间表述属于其原记录 |
| [background-literature.final.docx](background-literature.final.docx) | 作者研究背景与文献综述原DOCX副本，含修订和批注 |
| [theory-framework.final.docx](theory-framework.final.docx) | 作者理论框架原DOCX副本，含修订和批注 |
| [后续论文具体写作报告.md](后续论文具体写作报告.md) | 已采用的后文写作依据读取时副本 |
| [必要实验与结果整理.md](必要实验与结果整理.md) | 已采用的实验与结果安排读取时副本 |
| [experiment_2.README.md](experiment_2.README.md) | 正式主实验状态入口读取时副本，不能替代原始结果审计 |

副本按字节保留，未改写其中的历史路径、相对链接和时间状态。需要访问其引用材料时，先按sources.json定位原来源，再相对于原文件目录解析；例如manuscript.accepted.md的media仍指原paper/manuscript/media。这里未复制所有参考文献、图件与仿真输出，不宣称是完整排版或实验复现包。后续新候选稿另存，不覆盖输入快照。
