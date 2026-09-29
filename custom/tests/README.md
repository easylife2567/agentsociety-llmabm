# 自定义模块功能验收

`test_arrival_timing.py` 验证到达时机诊断：完整时间窗口、初始池、官方时刻、稳定抽样、次周回流、周龄、批次边界恢复、空/短feed、生成失败重试、发布确认和指标手算。

使用 `.env` 中的 Python 执行 `-m unittest discover -s custom/tests -p test_arrival_timing.py -v`，不调用真实LLM。
