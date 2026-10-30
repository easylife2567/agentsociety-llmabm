# 两路调度交接证据

仅保存调度与现场核对，不维护独立实时状态。实时进展见run README，实际状态由本批batch_execution.json单写。

| 资产 | 用途 |
|---|---|
| serial-state.json | 暂停旧父后保存的一致串行状态，保留原起点、已完成项与活跃引擎 |
| serial-runtime-plan.json | 原计划历史副本，不改变原预算、配置或绝对截止 |
| handoff-before.json | 交接前真实引擎PID、步骤、决策、账本及原截止 |
| initial-live-check.json | 交接后原引擎PID连续、两路以内与起点/计划/截止/账本守恒初验 |
| live-check.json | 两路实际推进后的进一步核对（完成时写入，不代表已有科研结果） |

信号只发旧监督器PID，不发独立引擎进程组；先STOP取一致状态，再默认HUP与CONT退出父进程，释放同一监督锁后接管。新控制器不会重启、resume或覆盖旧引擎输出。
