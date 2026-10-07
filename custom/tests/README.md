# 自定义模块功能验收

`test_arrival_timing.py` 验证到达时机诊断：完整时间窗口、初始池、官方时刻、稳定抽样、次周回流、周龄、批次边界恢复、空/短feed、生成失败重试、发布确认和指标手算。

使用 `.env` 中的 Python 执行 `-m unittest discover -s custom/tests -p test_arrival_timing.py -v`，不调用真实LLM。

`test_content_quality.py`验证共享内容修复：20条冻结样本在常规/arrival两入口、相对日期输入、拒答/过滤、有限事实支持、正常观点与阅读时间正例、互斥账本、20样本修正后发布、技术重试/重写/兜底、五个具体语义实例、真实环境曝光及次周回流。使用`.env`中的Python执行`-m unittest discover -s custom/tests -p test_content_quality.py -v`。服务返回为mock；成功不等于已验证模型重新生成质量。联合禁网验证及结果见根级runs的到达时机任务README。
