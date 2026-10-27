# Word与版面核验

| 资产 | 用途 |
|---|---|
| [word_checks.json](word_checks.json) | 字体设置、五图一表、批注与修订组、正文一致、原件指纹及PDF逐页检查 |
| [package_checks.json](package_checks.json) | 三份交付文件的最终SHA256、本地链接、脚本语法及未提交状态 |
| [review_preservation.json](review_preservation.json) | 原作者段落到合稿的位置匹配、42组原文字修订、15条原批注及格式修订 |
| [word_revision_mapping.json](word_revision_mapping.json) | 原修订组及本轮删改到Word修订ID的映射 |
| [docx_schema_clean.txt](docx_schema_clean.txt)、[docx_schema_review.txt](docx_schema_review.txt) | 两份最终DOCX的OOXML结构检查，均通过 |
| [reference_format.json](reference_format.json) | 用户指定旧PDF的实测尺寸、字体、行距、缩进、图注和页码 |
| `reference_page_*.png` | 旧PDF的首页、图件页和书目页版式参照 |
| `page_*.png` | 本次清洁版PDF的16页最终预览 |
| [page_contact_sheet.png](page_contact_sheet.png) | 16页缩略总览，检查整体分页与图表分布 |

实际保留15条原作者批注，审阅版共39条批注；所有批注的开始、结束和引用成对。42组原文字修订及1项原段落格式修订的文字、作者与日期核对通过；原始ID更换不改变修订身份。“幽默”的原插入在本次删除内仍可回看。接受全部修订后，审阅版与清洁版正文相同。

五图为原图嵌入，文件指纹与`paper/figures`一致，图题和图注跟随图片；表1为可编辑三线表。正文默认字体为中文宋体12 pt、西文Times New Roman 12 pt；标题和图注使用已记录层级字号，公式为原生Word公式。

PDF预览使用本机宋体-简的临时字体映射，交付Word字体名保持宋体。已检查全部页的文字未越出纸面、图件实际出现页、正文和英文书目字体；人工查看首页、理论/方法页、五图页、章末和书目页，未发现裁切、图注脱离或标题孤立。最后两段安排在同页，书目另起页。

这些检查针对本次中文合稿和导出，不等于英文投稿词数、匿名提交要求或全稿文献真实性审稿。
