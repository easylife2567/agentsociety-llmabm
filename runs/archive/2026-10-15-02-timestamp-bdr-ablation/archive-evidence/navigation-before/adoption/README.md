# 本轮成果正式采用

用户已明确接受本轮消融与D/R解释并要求落地主工作区。正式入口为[experiment_3](../../../hypothesis_4/experiment_3/README.md)、[双语图表报告](../../../presentation/hypothesis_4/timestamp_bdr_v1/README.md)及[综合](../../../synthesis/timestamp_bdr_v1/README.md)。

| 直接资产 | 用途 |
|---|---|
| baseline.json | 本次采用起点commit、所有已跟踪文件哈希、Git状态和用户原话 |
| preexisting/ | 本次涉及的既有说明文件采用前原状，不覆盖用户已有差异 |
| verification.json | 正式配置、数值/来源/链接和修改边界检查结果副本 |
| adopted_files.json | 正式采用文件及SHA256，对应当前落地版本 |

采用相对于原方案的适配为：原始数据独立复制、只调整分析工具和派生来源路径；保留冻结配置、原始JSON及日志中的历史路径，由正式provenance/path_map.json解释。正式目标均为本轮开始前不存在的新增代码文件；没有修改已有代码，因此无需要应用的既有代码patch。文档按采用前快照定向插入，不使用全工作区diff。

没有新增LLM、修改.env、重置账本、改写论文正文、自动提交或归档。原私有harness和候选产物是采用前快照，当前用户确认以正式adoption.json为准；未补造独立review或validate-synthesis通过记录。
