# Word结构与视觉校样

| 资产 | 用途 |
|---|---|
| edit_log.json | 52项文字、段落、图注操作及四张SVG媒体信息 |
| structural_checks.json | 121处真实修订、拒绝回退、120个原段落与逐字格式、四SVG、原件未变及ISO核心结构对比 |
| visual_checks.json | 最终全页PNG检查清单与实际发现 |
| accepted_check.docx / accepted_check.txt | 仅供检查的接受修订视图，不另交付用户 |
| rejected_check.docx / rejected_check.txt | 仅供检查的拒绝修订视图，验证原文恢复 |
| accepted_render_v2/ | 正确中文字体校样的接受视图，17页 |
| tracked_render_v2/ | 正确中文字体校样的最终修订视图，23页；旧图和删除内容在标记视图中可见是预期行为 |
| reference_render_v2/ | 同字体环境下原稿18页，作为保留格式参照 |
| fonts.conf | 仅校样进程使用的字体映射；文档字体设置没有改变 |
| fontcache/ | 校样字体缓存，已忽略，可再生成 |
| initial_schema_draft.docx | 首次草稿历史材料，核心顺序修复前，不作交付 |
| reference_render/、tracked_render/、accepted_render/ | 初次渲染缺CJK字体的历史结果，已废止，不用于验收 |

通用Office验证CLI在捆绑Python中缺少defusedxml，因此没有声称其检查通过。已改用捆绑lxml直接验证ISO模式并与原稿逐项对照：原稿自带MS/WPS扩展不受纯ISO模式识别，新稿仅增加四个新图注段的合法MS paraId属性差异，没有新增核心元素顺序错误。没有通过忽略新增错误来宣称全包ISO通过。

实际最终校样使用文档技能`render_docx.py`和捆绑LibreOffice：

```text
FONTCONFIG_FILE=<本目录/fonts.conf> <捆绑Python> <documents技能/render_docx.py> <目标DOCX> --output_dir <本目录/tracked_render_v2> --emit_pdf
```

从Word删除图5等内容以及新增图注会自然改变页数；未通过改字号、行距、页边距来维持旧页数。所有校样PDF/PNG及接受/拒绝副本都是内部验收材料，不作为最终交付。
