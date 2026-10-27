# 输出布局修正后的第二次启动

用户明确授权：保留首次失败，完整CLI离线验收通过后，按原模型和剩余预算重新启动九次消融，恢复30分钟汇报；异常继续先停。唯一实时状态见本run README。

| 直接资产 | 用途 |
|---|---|
| runtime_plan.json | 本次实际授权、原48小时绝对截止时刻、剩余预算、配置/代码哈希和输出路径 |
| [completion_audit.json](completion_audit.json) | 九次实际终态、8165项镜像哈希、40份冻结文件、总账、无残留进程及定时器暂停的最终核验 |
| batch_execution.json | active_runs列出的最多两路引擎、监督进程、实际进度、镜像及联停记录 |
| supervisor.log、parallel-supervisor.log、supervisor.lock | 原串行及并行控制日志，共用同一单实例锁 |
| _extra_attempts.count | 九次共享额外请求账本，最多990；首次失败为零消耗，不与主批混用 |
| timestamp_bdr_v1_interest_no_b_s0等九个目录 | 隔离工作区原始输出的持久镜像；运行期逐次原子复制，结束后逐文件核对SHA256 |

引擎物理输出位于`workspace/hypothesis_4/experiment_3/runtime/timestamp_bdr_v1_attempt_02/<run_id>/`。官方CLI从该实际目录向上寻找custom，得到隔离workspace；不使用把运行目录链接到worktree外的方案，也不放宽SDK路径安全检查。

每10秒检查实际输出并镜像到本目录。活跃写入、尚未形成完整JSON的文件等待下一轮复制；原始文件持续保留。各run停止/结束后再次完整镜像，mirror_manifest.json记录已核对的文件哈希；异常时镜像失败也明确留账，不删除源文件。

科学配置不变；最多两路，按seed 0→1→2、每seed no_b→no_d→no_r顺序补位，完成顺序可不同，模型deepseek-v4-1-flash-260910。总预算截止时刻保持首次启动后48小时（北京时间2026-10-17 20:21:11），不因本次重启顺延。首次失败目录`../timestamp_bdr_v1/`保持原样，不覆写、合并或冒充完成结果。

并行交接时保留当时去D进程和去B完成记录，不重启引擎或重置账本。交接前原计划和状态另存于../../evidence/parallel，runtime_plan登记用户并行授权、固定原模型及新API无密钥摘要。新接口失败时两路停止，不自动更换模型。
