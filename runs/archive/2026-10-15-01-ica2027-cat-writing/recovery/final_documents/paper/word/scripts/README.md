# 合稿与Word生成

| 脚本 | 职责 |
|---|---|
| [assemble_article.py](assemble_article.py) | 从分部分采用稿整理合稿源，接入五图、确认表1和22项书目；保存前后文与输入SHA |
| [attach_reviews.py](attach_reviews.py) | 依据源审阅JSON匹配段落，迁入批注、文字修订及本轮编辑锚点 |
| [build_word.cjs](build_word.cjs) | 使用docx-js生成审阅版和清洁版，设置字体、图表、原生公式及页码 |
| [finalize_word.py](finalize_word.py) | 接回原段落格式修订和嵌套历史修订，完成OOXML设置与字体别名 |
| [render_preview.py](render_preview.py) | 用独立LibreOffice临时配置及渲染副本导出PDF，不改交付Word字体或全局配置 |
| [verify_word.py](verify_word.py) | 验证字体设置、两版文字一致、五图一表、批注及原修订完整、原件未变和PDF页面 |

从项目根目录执行。使用项目Python整理合稿，使用已提供的bundled Node与Python生成及检查Word，未改变项目依赖。`build_word.cjs`的依赖目录可通过`CODEX_NODE_MODULES`指定。

```bash
AgentSociety2/.venv/bin/python paper/word/scripts/assemble_article.py
/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/word/scripts/attach_reviews.py
/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node paper/word/scripts/build_word.cjs
/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/word/scripts/finalize_word.py
/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/word/scripts/render_preview.py
/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/word/scripts/verify_word.py
```

`source_reviews.json`保存两份原Word的完整只读提取，`references.json`保存去重书目，都是复现输入。只从现有合稿JSON重建Word可从`build_word.cjs`开始，不需要读取活跃run。最终OOXML检查使用项目docx技能的`office/validate.py`；其缺失的纯Python检查依赖只装在临时目录，没有写入项目解释器。
