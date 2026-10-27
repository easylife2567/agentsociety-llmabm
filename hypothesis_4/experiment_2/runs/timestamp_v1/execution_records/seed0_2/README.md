# seed0_2启动执行历史

本目录仅保存同一timestamp_v1主实验的这次启动记录，不是另一项实验。全部seed0–9运行目录统一位于[主实验目录](../../README.md)，当前实验入口为[实验README](../../../../README.md)。

| 直接资产 | 用途 |
|---|---|
| [README.original.md](README.original.md) | 合并前README原字节；其中相对路径和运行时措辞为历史上下文 |
| [runtime_plan.json](runtime_plan.json) | 本次启动授权、冻结版本、原路径与预算；保持原字节 |
| [batch_execution.json](batch_execution.json) | 已完成的启动执行记录；保持原字节 |
| _extra_attempts.count、supervisor.lock、supervisor.log | 原账本和控制文件；不重置、不合并请求计数 |

JSON与日志内原路径通过[迁移清单](../../relocation.json)定位到当前目录；原始证据中的路径、ID与校验和不批量改写。不要从这些历史记录重新启动仿真。
