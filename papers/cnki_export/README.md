# CNKI/万方 中文文献补检 — 执行方案（v0.1）

> 目的：弥补 phase2 文献调研的中文证据缺口（CNKI/万方 此前未系统检索）。
> 前置：Playwright MCP 已注册（`.mcp.json`，项目级）；需要用户在本机浏览器完成一次学校 SSO 登录。
> 状态跟踪：检索完成后并入 `papers/literature_index.json`，并更新流水线 `literature_search` 元数据。

## 检索式（6 组，CNKI「主题」检索）

| # | 检索式 | 目的 |
|---|---|---|
| q1 | `主题=(网络悼念 OR 数字遗产 OR 数字来生 OR 身后身份 OR 数字死亡)` | 中文数字哀悼研究 |
| q2 | `主题=(名人去世 OR 公众人物去世) AND 主题=(社交媒体 OR 短视频 OR 抖音)` | 本土名人死亡传播 |
| q3 | `主题=(张雪峰 OR 公众人物) AND 主题=(算法推荐 OR 信息茧房 OR 流量)` | **个案本土研究（重点）** |
| q4 | `主题=(短视频) AND 主题=(去语境化 OR 碎片化叙事 OR 标签化)` | 短视频叙事机制 |
| q5 | `主题=(算法推荐 OR 推荐算法) AND 主题=(重复曝光 OR 内容同质化 OR 回声室 OR 茧房)` | 算法曝光机制中文版 |
| q6 | `主题=(首因效应 OR 第一印象 OR 印象形成) AND 主题=(社交媒体 OR 网络)` | 首因/印象中文版 |

规则：
- 每组的全部检索结果导出为**一个文件**：`papers/cnki_export/q1.txt` … `q6.txt`。
- 单组超过 500 条时，与用户确认后再决定限年限或限「学术期刊」。
- 万方：优先补 q1/q2 的**学位论文**（CNKI 学位论文库导出受限时的替代来源）。

## 导出格式要求

- 首选 CNKI「导出与分析」→ **RefWorks 或 NoteExpress 格式**（含题名/作者/来源/年份/摘要/关键词）。
- 若无上述格式，用「自定义导出」，勾选：题名、作者、来源、年份、期号、摘要、关键词。
- 保持 UTF-8 / 原始编码均可，解析脚本统一处理。

## 流程（Playwright MCP 就绪后）

1. `browser_navigate` 到 CNKI 检索页（如 https://kns.cnki.net/kns8s/defaultresult/index ）。
2. 若未登录：提示用户在**打开的浏览器窗口**里完成学校 SSO 登录（密码不经手 Claude）。
3. 逐组执行 q1–q6：输入检索式 → 检索 → 全选结果 → 导出 → 下载文件（playwright MCP 的下载处理）→ 重命名为 `qN.txt` 存入 `papers/cnki_export/`。
4. 万方（可选）：学位论文补检 q1/q2。
5. 解析：标题规范化去重（与现有 67 条比对）→ 题录核验（DOI/作者/年份/期刊）→ 按相关性分级（core/supporting/peripheral）→ 追加进 `papers/literature_index.json`（source=cnki_wanfang_round1）。
6. 更新流水线元数据：`research-pipeline update-stage literature_search completed --metadata '{"cnki_round1": ...}'`。
7. `git add -A && git commit`。

## 与本项目协议的一致性

- 纳入/排除标准沿用 `research/停止更新公众人物的算法推荐与公众认知/phase2_文献调研/00_检索协议_v0.1.md`。
- 未取得全文的条目只登记题录（selection_status=title_abstract），不声称原文结论。
- 中文文献同样记录：证据等级（如适用）、综合评级、COI 声明状态（未定位 ≠ 无）。
