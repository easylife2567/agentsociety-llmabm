# 随机/兴趣seed0试运行资产（含原三臂历史）

> 2026-10-30已归档。当前状态、路径映射与复验入口见[run README](../README.md)。以下为当时的执行/分析记录；历史控制器及含旧绝对路径的命令不再作为启动入口，原始记录保持。

实时进展统一见[run README](../README.md)，本级只索引执行资产，不另建人工状态表。

用户最新将范围缩减为随机/兴趣；当前查看/停止使用`run_selected.py --status`/`--stop`。原runtime_plan.json与parallel_revision.json保持历史字节，selected_revision.json记录有效两臂范围；旧控制器作为冻结来源与共享核验模块保留，不用旧停止入口操作当前监督器。

执行现已全部结束，无活跃引擎；本级只保留历史控制入口，不授权重新启动。结果见analysis/，原始冻结镜像见results/及raw_results_manifest.json；自动检查已删除。实时结论仍以run README为准。

| 资产 | 用途 |
|---|---|
| [runtime_plan.json](runtime_plan.json) | 用户运行授权、来源冻结、三臂顺序、模型约束、独立预算和新8小时截止 |
| [selected_revision.json](selected_revision.json) | 当前仅随机/兴趣的范围修订，时序撤回消耗计入原总上界 |
| run_selected.py、test_selected.py | 当前两臂监督器及9项禁网夹具检查，已完成随机不重跑，时序不再启动 |
| [scope_handoff/](scope_handoff/README.md) | 时序撤回现场、旧并行状态及两臂接管证据、分析补丁起点 |
| selected_check_attempt1.log、selected_preflight.log | 两臂调度检查与实际交接前只读核对 |
| selected-supervisor.log、selected-supervisor.stderr.log | 当前两臂监督器日志 |
| [configs/](configs/) | 三份seed0运行配置，仅变更共享重试上界和账本 |
| run_pilot.py | 本批监督器及只针对本批的status/stop入口 |
| run_parallel.py | 当前两路监督器，接管原引擎、共享累计预算、失败联停；需显式--handoff且仅一次 |
| test_parallel.py | 7项禁网交接/两路调度检查，不启动真实引擎或发真实信号 |
| [parallel_revision.json](parallel_revision.json) | 用户并行授权、两路上限、控制器哈希与原预算/截止守恒 |
| [parallel_handoff/](parallel_handoff/README.md) | 原串行现场与实际PID连续、两路推进核验证据 |
| parallel_check.json、parallel_check_attempt2.log | 两路假进程验收统计与日志；首轮夹具错误另存attempt1 |
| parallel_preflight.log | 真实交接前只读检查通过，不发模型请求 |
| parallel-supervisor.log、parallel-supervisor.stderr.log | 当前监督器日志 |
| test_runner.py | 控制器的禁网夹具验收，不启动真实引擎 |
| verify_preflight.py | 三份运行配置的官方schema、步骤和实际模块禁网验收 |
| batch_execution.json | 监督器维护的本次实际状态与完成核验，不是科学结果分析 |
| extra_attempts.count | 本pilot独立额外请求账本，只有正式执行需要时创建 |
| evidence/ | 启动前验收、控制器检查与实际运行核验证据 |
| analyze_pilot.py | 完整通过后才运行的效果观察脚本；当前必须传--selection selected_revision.json，仅分析随机/兴趣 |
| test_analysis.py | 指标、回流审计、选臂与图表数据一致性的6项纯离线检查 |
| plot_pilot.py | 显式传--selection，生成两臂的数量/供给份额/实际曝光三面板图，不画虚构结果 |
| [selected_analysis.patch](selected_analysis.patch) | 已有分析/绘图/测试的最终选臂修改，起点副本和重放核验见scope_handoff |
| [analysis/](analysis/README.md) | 已完成两臂的22行真实周表、比较图及探索性报告 |
| plot_agent_supply.py | 沿用旧chart3b样式绘制两臂发帖量，独立核对200份Agent逐周逐类成功发布 |
| compare_three_arms.py | 新两臂加历史完整时序的离线三臂对比、五类现实轨迹DTW与--check复算；不启动仿真 |
| [agent_supply/](agent_supply/README.md) | 两臂原图及新增三臂堆叠图/DTW、33行周表、冻结来源与方法；时序为历史参考 |
| [raw_results_manifest.json](raw_results_manifest.json) | 完整随机/兴趣及撤回时序共2337份原始文件的来源映射与逐文件SHA256 |
| results/ | 原始输出独立复制快照，Git忽略但不可当缓存删除；不只依赖workspace |
| [analysis_metadata.patch](analysis_metadata.patch) | 图表来源行数、真实图链接及分析索引修订，初版产物保存在evidence |

本次原始引擎结果位于隔离workspace的`hypothesis_4/experiment_2/runs/hourly_return_pilot_s0/`。所启动条件均从W12开始，未使用旧时序结果；时序已撤回，不进入当前两臂比较。暂不存在的上述执行/分析资产在对应阶段产生，不代表已经启动或完成。
