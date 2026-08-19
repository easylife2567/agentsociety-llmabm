# NoteExpress 导出字段清单（CNKI 实测）

CNKI「导出与分析 → NoteExpress」产出的记录块（CRLF 分隔，块与块之间空行）。每条块首为 `{Reference Type}: <类型>`，其后每行一个字段。

## 常见字段

| 字段 | 内容 | 注意 |
|---|---|---|
| `{Reference Type}` | Journal Article / Newspaper Article / Thesis / Book / Conference Proceedings / Book Section 等 | 块分割依据，见 SKILL.md 步骤 6 |
| `{Title}` | 题名 | **截断副标题**（「A——B」→「A」），比对前从两侧剥离 |
| `{Author}` | 作者，分号分隔 | 第一作者做去重键 |
| `{Author Address}` | 作者单位 | 学位论文 = 学校 |
| `{Journal}` | 期刊名 | 仅 Journal Article 可靠 |
| `{Secondary Title}` | 副刊名 / **报纸名** / **会议名称** | Newspaper 与 Conference 的 venue 都在这 |
| `{Publisher}` | 出版社 / 学校（学位论文） | Book/Thesis 的 venue |
| `{Place Published}` | 会议地点 | Conference venue 兜底 |
| `{Year}` | 年份 | **报纸为空** |
| `{Date}` | 日期（YYYY-MM-DD 或 YYYYMM） | 报纸年份在这里；Book 为 YYYYMM |
| `{Volume}` / `{Issue}` | 卷/期 | |
| `{Pages}` | 页码 | |
| `{DOI}` | DOI | 网络首发记录常缺失 |
| `{URL}` | CNKI 链接（detail urlid 或 thinker 章节链接） | 网络首发仅有此 |
| `{Keywords}` | 关键词，分号分隔 | |
| `{Abstract}` | 摘要 | 图书章节手工补录时可能是预览快照，需标注 |
| `{Type of Work}` | 硕士 / 博士 | 学位论文 |
| `{Tertiary Author}` | 导师 | 学位论文 |
| `{Subsidiary Author}` | 其他作者 | |

## 类型 → 索引字段映射

| NoteExpress 类型 | venue_type | venue 取 | 年份取 | 额外字段 |
|---|---|---|---|---|
| Journal Article | journal | `{Journal}` 或 `{Secondary Title}` | `{Year}` | |
| Newspaper Article | newspaper | `{Secondary Title}` 或 `{Publisher}` | **`{Date}`**（`{Year}` 为空） | |
| Thesis | thesis | `{Publisher}` | `{Year}` | supervisor=`{Tertiary Author}`; degree=`{Type of Work}` |
| Book | book | `{Publisher}` | `{Date}` (YYYYMM) | |
| Conference Proceedings | conference | `{Secondary Title}` 或 `{Place Published}` 或 `{Publisher}` | `{Year}` | |
| Book Section（补录） | book | 出版社 | 年份 | ISBN、页码 手工记录 |

## 图书章节手工补录模板（XKPT 记录）

```
{Reference Type}: Book
{Title}: 第三章 过滤气泡：定义、辨析与研究进展
{Author}: 杨莉明
{Publisher}: 中国社会科学出版社
{ISBN}: 978-7-5227-2791-2
{Pages}: 57
{Date}: 202311
{Abstract}: （章节预览快照，非全文摘要——标注「预览」）
{URL}: https://thinker.cnki.net/wbfd/chapterdetail/...
```

## 已知源数据缺口（如实保留，不编造）

- 网络首发记录无 `{Year}`（只有 urlid URL），年份缺失可接受
- 部分记录无 DOI 和 URL
- 同名重复记录（报纸多期连载）在导出中保留全部
