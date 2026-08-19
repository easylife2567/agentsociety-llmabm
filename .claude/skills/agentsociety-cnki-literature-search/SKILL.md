---
name: agentsociety-cnki-literature-search
version: 1.0.0
description: 通过本机浏览器（Playwright MCP）在 CNKI 做中文文献检索、NoteExpress 导出、完整性校验并合并进 literature_index.json。当需要补充中文文献证据、检索 CNKI/万方、或执行中文文献补检时使用。
---

# CNKI 中文文献调研（浏览器自动化）

在 CNKI 高级检索页用「专业检索」语法执行检索，NoteExpress 格式全量导出，解析后合并进 `papers/literature_index.json`（source=`cnki_wanfang_roundN`）。本 skill 沉淀自 q1–q6 实战（1258 条），包含全部已知坑位与验证方法。

与 `agentsociety-literature-search` 的关系：该 skill 走学术网关（英文为主），本 skill 专用于 CNKI 浏览器自动化（中文）。两者结果合并进同一个 index，source 字段区分。

## 何时使用

- 需要中文文献证据（CNKI/万方 此前未系统检索）
- 用户要求「中文补检」「CNKI 检索」
- literature_index.json 中中文语料覆盖不足

**不要用于**：纯英文检索（用网关）、已确定假设后的精读（用 hypothesis/analysis）、单篇 PDF 阅读。

## 安全红线（先于一切）

1. **登录与验证码绝不经过 Claude**：SSO 登录、腾讯拼图验证等由用户在本机浏览器手动完成。Claude 不读取、不输入、不处理任何密码或验证码。
2. **research/ 目录只读**：研究工作在其他工具中完成；Claude 不需要在该路径下写任何文件。
3. 工作产物写入 `papers/cnki_export/` 与 `papers/`；每次文件变更后 `git add -A && git commit`。
4. 单组命中 > 500 条（CNKI 单次导出上限）时，**先与用户确认口径**（限近 N 年 / 限学术期刊 / 分批全导），不擅自决定。

## 前置条件

- Playwright MCP 已注册（`.mcp.json`，项目级）
- 用户已在本机浏览器完成学校 SSO 登录（`browser_navigate` 后提示用户操作，等待用户确认「继续」）
- 导出下载落在 `.playwright-mcp/`（该目录已被 gitignore，不会污染仓库）

## 工作流总览

1. 设计检索式（专业检索语法）→ 2. 执行检索 → 3. 全选/翻页 → 4. NoteExpress 导出 + 手工补录图书章节 → 5. 完整性校验（导出集合为权威）→ 6. 解析合并 → 7. README + pipeline metadata + commit。

## 步骤 1：设计检索式

CNKI「专业检索」语法（在高级检索页的**专业检索 tab** 中输入）：

- `SU=主题`（最常用；`TKA`=篇关摘，`KY`=关键词，`TI`=题名，`AB`=摘要，`FT`=全文，`AU`=作者，`LY`=发表时间，`CLC`=分类号，`DOI`，`CF`=基金）
- `+` 或 `OR` 表示**或**；`*` 或 `AND` 表示**与**；`-` 或 `NOT` 表示**非**
- 半角括号分组；同义扩展词用 `+`（如 `SU=(网络悼念 + 数字遗产 + 数字来生)`）
- 检索式记录进 `papers/cnki_export/README.md` 与 index 的 `query` 字段

参考分组模式（q1–q6）：核心主题组 / 本土案例组 / 个案×机制组 / 机制子维度组，每组一个检索式，relevance_group 按查询命名。

## 步骤 2：执行检索

1. `browser_navigate` 到 https://kns.cnki.net/kns8s/AdvSearch （先确认已登录）。
2. **先点击可见的「专业检索」tab**（LI 元素）。`querySelector('textarea')` 会匹配到隐藏的「高级检索」输入框——reload 后必做此步，否则点检索报「请输入检索词」。
3. 用 `browser_type`（真实事件）向专业检索 textarea 填入完整检索式；**提交用 evaluate click 在 `input.btn-search` 上**（可见按钮；隐藏的 `input.search-btn` 不可点；切勿点顶部导航的「检索」链接）。
4. 等待结果页加载。命中数取自结果页统计（如「共找到 809 条结果」）。
5. 若命中 > 500：暂停，问用户口径（见安全红线 4）。

## 步骤 3：全选与翻页（节奏是关键）

- **`#selectCheckAll1` 只全选当前页**。>20 条时循环：翻页 → 全选 → 等 → 下一页。已选计数跨页累积（如 20→40→60→77），结束后与总数核对。
- **节奏**：点 checkbox 后等 **800ms**，页面变化后等 **1600ms**。400/1200ms 会丢记录（实测 478/500、287/309）。
- 结果页分页条只渲染约 7 个页码按钮（动态窗口），「跳页」只对可见数字有效，否则静默失败。可靠翻页：**重复点「上一页」**（或「下一页」）直到目标页。
- 分页条中的页码链接（如 "3"）复用第一条结果的 abstract 链接，点击会开新 tab 而非 AJAX 翻页——点 `javascript:void(0)` 的「下一页」。
- **「已选」集合跨检索持久化**（Vue store）：每组检索勾选前先刷新页面/清空，避免上一组残留混入。

## 步骤 4：导出（NoteExpress）+ 手工补录

1. 裸 `A` 标签「导出与分析」→ hover →「导出文献」→ hover → **NoteExpress**。
2. 点下载按钮 `a[title="导出题录文件"]`；文件落在 `.playwright-mcp/CNKI-YYYYMMDDHHMMSSmmm.net`。
3. **导出中心 tab 生命周期**：每次导出前必须关闭旧的导出中心 tab，否则新 tab 载入旧批次（q2 踩坑）。
4. 重命名存入 `papers/cnki_export/qN.txt`，并记录进 README（检索式/命中数/口径/类型分布）。

**手工补录规则（图书章节）**：心可书馆图书章节（uniplatform=XKPT，如「第X章 …」）会被 NoteExpress **批量导出跳过**。检出方法：结果页「类型筛选 → 图书」；补录途径：结果页打开章节详情（thinker.cnki.net/wbfd/chapterdetail），手工记录 著者/出版社/ISBN/页码/年份/摘要（摘要若为章节预览快照则标注），以 Book 类型追加到 qN.txt 末尾。样例：q4 的 2 条、q5 的 1 条（第三章 过滤气泡 / 杨莉明 / 中国社会科学出版社）。

## 步骤 5：完整性校验（导出集合为权威）

命中数 ≠ 渲染数 ≠ 导出数（q5：声称 809，渲染 810 行含重复，导出去重后 804）。**以 NoteExpress 导出集合为准**：结果页逐页抓取标题，与导出记录比对。

- 规范化必须用 **Python**（`re.sub(r"[\W_]+", "", main).lower()`，re 的 `\w` 支持中文；**JS 的 `\W` 不匹配中文**，会把所有中文标题删空，产生假「全部通过」）。
- **NoteExpress `{Title}` 截断副标题**：「A——B」→ 导出「A」。比对前从**两侧**剥离 `——` 之后部分，否则产生假「缺失」。比对键 = (规范化标题, 第一作者)。
- 报纸记录年份在 `{Date}`（如 2015-11-03），`{Year}` 为空——年份提取依次检查两个字段。
- 校验通过标准：missing=0（剥离副标题后）。同名重复记录（如报纸连载「精彩有你」×9）属正常，导出保留全部。

## 步骤 6：解析合并

解析脚本参照 `papers/merge_cnki_round1.py`（本 skill 的 canonical 实现，q1–q6 已用）：

- 块分割：`re.split(r"(?m)^\{Reference Type\}:\s*", text)`（保留类型在块首，不要用 `split("\n{Reference Type}:")` 否则丢类型导致 KeyError）；字段：`\{([^}]+)\}:\s*(.*)`；CRLF。
- 去重键 = (规范化标题, 规范化第一作者)；先组内/跨查询去重，再与既有条目标题规范化比对（跨语言检索通常 0 重叠，符合预期）。
- 索引契约（对齐 `agentsociety-literature-search` 的 register 脚本）：`title` / `source` / `query`(qN + 检索式) / `saved_at` / 可选 `abstract` / `journal` / `extra_fields{authors[], year, record_type, venue_type, relevance_group, selection_status="title_abstract", verification="CNKI_EXPORT", url, doi, keywords, supervisor, degree}`。**selection_status 如实写 title_abstract（题录级，未精读），不声称原文结论。**
- 字段映射（venue 取值规则）：
  - Journal Article → `{Journal}`（`{Secondary Title}` 兜底）
  - Newspaper Article → `{Secondary Title}`（`{Publisher}` 兜底）；年份用 `{Date}` 提取
  - Thesis → `{Publisher}`（学校）+ `{Type of Work}`（硕/博）+ `{Tertiary Author}`（导师）
  - Book → `{Publisher}` + `{Date}`:YYYYMM
  - Conference Proceedings → `{Secondary Title}`（会议名称）或 `{Place Published}` 或 `{Publisher}`——**不要只看 `{Journal}`**，否则会议论文 venue 全空（q1–q6 曾 18 条全空）
- 已知可接受的源数据缺口（如实标注，不编造）：网络首发记录无 `{Year}`（只有 urlid URL）、少量记录无 DOI/URL。
- 合并后更新 README 合并账目、`research-pipeline update-stage literature_search completed --metadata '{"cnki_roundN": {...}}'`、`git add -A && git commit`。

## 风控与恢复（腾讯拼图验证）

- 连续自动化操作会触发 tencent-captcha 弹窗：**暂停并请用户手动完成**，验证码不经手 Claude；用户完成后继续。
- 弹窗关闭后 DOM 残留（移出屏幕，y≈-1000000），不阻塞后续操作；可见性检测用 `getBoundingClientRect().y > -1000`。
- 若页面已 reload：回到步骤 2 的「先点专业检索 tab」再继续。

## 运行参数备忘（踩坑实证）

| 参数 | 值 |
|---|---|
| 单次导出上限 | 500 条 |
| checkbox 后等待 | 800ms |
| 页面变化后等待 | 1600ms |
| 全选作用域 | 当前页（`#selectCheckAll1`） |
| 翻页 | 动态窗口 ~7 页，可靠途径「上一页/下一页」循环 |
| 导出格式 | NoteExpress（.net，UTF-8/GBK 均可，解析统一处理） |
