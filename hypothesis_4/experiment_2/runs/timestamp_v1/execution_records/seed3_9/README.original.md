# seed 3–9三臂主实验运行资产

本批实时状态统一见[实验README](../../README.md)，实际运行依据为本目录的runtime_plan.json及batch_execution.json。21次已全部完成，最终完整性证据见completion_check.json；定时汇报已暂停，暂不分析。准备期init/manifest_seed3_9.json保持原字节及execution_authorized=false，本次实际启动授权单独冻结在runtime_plan.json。

| 直接资产 | 用途 |
|---|---|
| completion_check.json | 全21次最终完整性、Agent/环境矩阵、模型与用量核对、进程退出、冻结及原始输出SHA256；不含科研结果分析 |
| runtime_plan.json | 用户本次启动授权、原21次顺序、最多2路交接授权、当前模型别名/预期返回版本、105项冻结哈希、48小时保护及请求预算 |
| recovery_live_1.json | 恢复后两路实际PID、推进、账本、105项冻结哈希及原中断环境/Agent摘要未改核验 |
| recovery_1.json | 本次用户恢复授权、原计划哈希、当前控制器哈希、21条件实际路径映射、54次失败尝试保留及原截止；不是新科学批次 |
| stopped_execution_1.json | 第一次停止时batch_execution.json原字节，只作历史证据 |
| recovery_probe_1.json、recovery_check_1.json | 1次额度恢复探针（36tokens）及禁网真实恢复/假进程联停检查 |
| recovery-supervisor.log | 当前恢复监督器日志 |
| timestamp_v1_interest_s6_resume1/ | 从原兴趣seed6完整副本接续；不另加原目录175次请求 |
| timestamp_v1_random_s7_retry1/ | 原随机seed7失败现场保留后的独立重试；旧54次正文仍计全批预算 |
| terminal_check.json | 停止后的原始输出复验、11次完整性、2次中断位置、进程退出、额度错误出处及最终账本；未补跑 |
| batch_execution.json | 监督器/当前引擎PID、实际步数与Agent记录摘要、完成列表及停止原因；原子更新 |
| parallel-supervisor.log | 当前两路监督器日志，不覆盖原串行日志 |
| supervisor.log | 本批控制器日志；禁止覆盖已有日志后重启 |
| supervisor.lock | 防止同批两个控制器同时运行 |
| _extra_attempts.count | 本批共享额外请求计数，初值0、上限2310；不复用旧账本 |
| timestamp_v1_random_s3等21个规划目录 | 各次独立官方CLI输出、engine/stdout/stderr日志、Agent、环境、replay与checkpoint，按实际顺序逐次创建 |

总计23100次行动机会，Agent正文外层请求上界25410；准备期3次接口测试及3697 tokens单列。最多2路，按seed3→9、每seed random→chronological→interest原顺序填补空位，完成顺序可不同；不补消融。任一步失败、真实行动/发布失败、返回模型版本变化或时限到达即停止后续，不自动重跑或恢复checkpoint。完成检查核对每次693步、1100唯一环境行动、11周和100份Agent/1100唯一决策。

当前请求别名deepseek-v4.1-flash，预期实际返回deepseek-v4-1-flash-261017；保留与旧seed0–2批次的版本差异，采用同一大版本系列是用户决定。监督器每10秒读取真实进程与已保存记录；不能把批状态文件独自当作进程仍存活的证据。每30分钟汇报由当前聊天的heartbeat自动任务seed-3-9-30负责；完成或明确停止后报告并暂停，不自动分析或补跑。

并行交接证据保存在[parallel_control](../../parallel_control/README.md)，原运行引擎PID78411保留。原105项冻结哈希、共享账本和2026-10-24T15:40:45.950453+00:00截止不变。当前状态有active_runs数组；监督器最多保留两路，并在故障时联停。
