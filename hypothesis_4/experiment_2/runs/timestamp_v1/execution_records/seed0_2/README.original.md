# timestamp_v1主实验运行

实际进度以[实验README](../../README.md)及batch_execution.json中的引擎记录为准。2026-10-14用户授权启动九次原方案；不含额外U或关闭回流实验。

| 资产 | 用途 |
|---|---|
| runtime_plan.json | 实际启动授权、模型、代码与输入版本、九次顺序及48小时总运行上限 |
| batch_execution.json | 串行运行进程与各次实际进度，失败时停止而不重跑 |
| supervisor.log | 运行控制日志 |
| timestamp_v1_random_s0等九目录 | 各次官方引擎的日志、用户记录、环境、生成帖与保存状态；原始资料保留，不纳入Git |
| _extra_attempts.count | 全批共享额外请求计数，最多990次 |

主实验计划9,900次表达机会，每人每周一次。总运行停止上限48小时为本次启动的限时保护，不继承旧诊断预算；不会因此增加条件或重复失败运行。停止命令向batch_execution.json中的supervisor_pid发送TERM，保存已有记录并停止后续各次。
