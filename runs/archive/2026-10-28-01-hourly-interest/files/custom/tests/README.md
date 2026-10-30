# 自定义模块功能验收

`test_arrival_timing.py` 验证到达时机诊断：完整时间窗口、初始池、官方时刻、稳定抽样、次周回流、周龄、批次边界恢复、空/短feed、生成失败重试、发布确认和指标手算。

使用 `.env` 中的 Python 执行 `-m unittest discover -s custom/tests -p test_arrival_timing.py -v`，不调用真实LLM。

`test_content_quality.py`验证共享内容修复：20条冻结样本在常规/arrival两入口、相对日期输入、拒答/过滤、有限事实支持、正常观点与阅读时间正例、互斥账本、20样本修正后发布、技术重试/重写/兜底、五个具体语义实例、真实环境曝光及次周回流。使用`.env`中的Python执行`-m unittest discover -s custom/tests -p test_content_quality.py -v`。服务返回为mock；成功不等于已验证模型重新生成质量。联合禁网验证及结果见根级runs的到达时机任务README。

`test_timestamp_main.py`验证experiment_2九配置：共享输入和profile、九个完整窗口的真实到达与行动记账、三臂回流、同批隔离、稳定排序、恢复、时序周供给守恒及共享请求耗尽兜底。使用`.env`中的Python执行`-m unittest discover -s custom/tests -p test_timestamp_main.py -v`，不调用LLM。联合24项禁网验收记录见`hypothesis_4/experiment_2/README.md`；环境演练与固定生成返回不代表完整模型仿真结果。

`test_event_week_schedule.py`验证experiment_2的W13共同顺延：仅5人本周改变、九窗22位悼念均事件后行动、三臂官方无特殊槽且最多10槽、900份正式CLI/profile工作区保留覆盖、实际Agent行动门及恢复不重复、错误覆盖拒绝。联合当前功能禁网验收使用`hypothesis_4/experiment_2/2026-10-09-03-event-week-check.py`，输出路径见实验README。阅读计数为无Agent产出的环境演练，不是闭环LLM结果。

`test_ordinary_official.py`核验官方普通评分/抽样、候选资格和20:00门控、不进入置顶/保底、可选中或漏读、历史agenda兼容、换策略恢复拒绝及真实registry源码位于custom。当前35项联合验收输出为实验目录2026-10-09-06-ordinary-official-verification.json。

`test_hourly_return.py`验证候选`next_batch`三臂批末入池、同小时隔离、旧配置兼容、策略保存恢复与换策略拒绝、跨周和末批供给守恒，以及时序新旧回流声明的逐批等价。固定测试正文只调用环境方法，不运行Agent或模型；使用项目解释器执行`-m unittest discover -s custom/tests -p test_hourly_return.py -v`。
