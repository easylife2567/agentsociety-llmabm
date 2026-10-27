# 三臂主实验两路调度交接

本目录仅保存调度变更与交接证据，实时状态仍统一在[实验README](../README.md)。不改科学配置、源码、总预算或首次启动后的绝对截止，不重跑或接续checkpoint。

| 直接资产 | 用途 |
|---|---|
| recovery-check.py | 后续用户明确恢复授权对应的禁网实际checkpoint/环境/100份Agent恢复及两路假进程故障联停；证据在本批recovery_check_1.json |
| baseline.json | 准确commit、既有控制器哈希、原105项冻结检查及预算/截止 |
| check.py、offline-check.json | 假进程验证接管不重复、父PID专属信号、两路上限、故障联停和预算/截止守恒，0真实CLI/网络/LLM |
| serial-state.json、serial-runtime-plan.json | 暂停旧父监督器后保存的一致历史状态和原始运行计划，不作当前状态入口 |
| handoff-before.json | 接管前真实引擎PID、进度及额外额度 |
| live-check.json | 实际接管后的引擎PID连续、两路进度、原预算/截止和冻结哈希核对 |

旧run_seed_extension.py保持字节不变，新run_seed_extension_parallel.py复用其Agent统计及旧主批完成核验。此次没有修改既有代码，不需要新增代码patch；完整新增源文件直接保留并记录SHA256。先--check和本目录check.py，再显式--handoff一次；已有serial-state.json时拒绝自动重复交接。

交接仅对旧监督器PID发STOP取得一致状态，再发默认HUP退出及CONT释放锁；不向当前独立引擎PID/进程组发送交接信号。新监督器取得原supervisor.lock并接管原PID，再按原manifest顺序填补第二路。运行时TERM/INT是两路联停入口，不自动重启。原ledger沿用，不写回零；原deadline保持2026-10-24T15:40:45.950453+00:00（北京时间10月24日23:40:45）。

首轮离线夹具因临时ROOT未同步模拟控制器路径而断言失败；修正夹具后5项通过，未对真实运行发信号或请求模型。

后续用户明确要求“额度已经恢复，尝试继续”，该新授权下的恢复由实验README及run_seed_extension_recovery.py说明；上文不接续限制描述原交接授权。恢复不改原科学机制、总正文预算、账本或截止，旧停止与原始目录保留。
