# timestamp B/D/R正式LLM批次

用户2026-10-15授权启动九次正式LLM消融，沿用主实验模型和既定预算；出现异常先停，保留记录，不自动重启。实际状态统一见本run README。

| 直接资产 | 用途 |
|---|---|
| runtime_plan.json | 本批真实运行授权、模型、九次顺序、输入/源码冻结及预算；不覆盖准备期manifest |
| batch_execution.json | 串行控制的当前条件、进程、实际进度、完成核对或停止原因 |
| supervisor.log | 控制进程日志；原始保留 |
| supervisor.lock | 单监督器排他锁，防止重复启动 |
| _extra_attempts.count | 本批九run共享额外请求账本，初始为零，硬上限990；独立于主实验 |
| timestamp_bdr_v1_interest_no_b_s0等九个目录 | 各次引擎日志、Agent决定/正文、环境、replay和checkpoint；大体积原始资料忽略Git，持续保留 |

顺序为seed 0→1→2，每seed no_b→no_d→no_r；100人×11周，每run693批/1100次机会，九次9900次机会。模型为deepseek-v4-1-flash-260910；首次请求最多9900，额外请求最多990，总外层请求上界10890，总时限48小时，串行运行。

从隔离workspace启动官方CLI，--run-dir和--log-file显式指向本目录的独立run。隔离区`hypothesis_4/experiment_3/runs/timestamp_bdr_v1`符号链接到本持久目录，使原已验收配置的相对ledger路径保持原样；输入仍从隔离区读取，主项目不写入。

控制器每10秒检查实际checkpoint、Agent记录、日志、请求账本及冻结哈希；检测步骤失败、服务技术异常、行动/发布失败、未来曝光、重复行动、源码漂移、预算越界或连续30分钟无实际推进时，向当前进程组请求优雅中止并停止后续条件。已约定的内容修复/拒答重写不自行改变规则；发生技术请求错误即使已有限重试也停止。优雅停止后若进程仍不退出，继续发送TERM并保留人工处理提示，不自动强制删除或重跑。

准备期manifest中的execution_authorized=false按原始证据保留，实际授权以runtime_plan.json为准。此目录不含凭据；API密钥只在进程内读取现有.env。停止使用本run的`run_ablation.py --stop`，状态使用`--status`；不使用指向固定正式experiment_2/run的旧包装器。
