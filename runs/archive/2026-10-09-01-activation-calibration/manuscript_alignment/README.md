# 最新作者文稿对齐证据

本目录保存2026-10-12主工作区文稿对齐的来源与差异，实时状态只在[run README](../README.md)维护。用户授权直接落实研究背景、文献综述、理论框架及研究分工；第二章第二部分与第三、四章尚未重写。

| 资产 | 用途 |
|---|---|
| `before/` | 本轮修改前13份文档的实际文件副本，含此前已有未提交修改，不以HEAD冒充起点 |
| [git_start.txt](git_start.txt) | 修改前主工作区Git状态 |
| [background.accepted.md](background.accepted.md)、[framework.accepted.md](framework.accepted.md) | Word接受修订后提取的正文与脚注，去转换器包装、保留作者论点 |
| [alignment.diff](alignment.diff) | 本轮13份文档相对于上述副本的差异，不含用户其他已有修改 |
| [evidence.json](evidence.json) | 三份作者来源与前后文档SHA256、Git基线及实际核验结果 |

作者原始文件位于项目根目录，名称与SHA256见evidence.json；本目录不复制或修改原DOCX/PDF。差异用于审阅和追溯文档对齐，不是新的代码候选补丁，也不包含参数或数据变更。本轮完整验证仅为文档核验，不重跑实验、调用LLM或改变机器阶段。

实际核验全部通过：作者原件及前状态副本的哈希、Word修订/批注/注释数量、作者更新部分完整同步、三个研究问题一致、18项新增脚注对应、新链接有效、摘要与后续正文及旧引用保留、此前修订说明保留、修改路径范围与Git差异格式、暂存区为空。逐项结果在evidence.json；原有未提交修改没有被清理或提交。
