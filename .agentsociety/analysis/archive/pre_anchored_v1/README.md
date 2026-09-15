# anchored_v1 分析接入前的 harness 历史记录

此目录保存 `anchored_v1` 正式 9-run 接入官方 analysis harness 之前产生的操作 receipt。
这些记录仅供审计，不参与当前 analysis `status`、可重试任务或阶段门控。

- `run_20260915t083506_9d9d1f8507.json`：在 claims gate 尚未建立时尝试
  `compose-figure`，结果为 `BLOCKED_BY_GATE`；它不是最新正式实验的分析失败。
