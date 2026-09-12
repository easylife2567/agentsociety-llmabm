# 归档：正式 9-run 批跑之前的历史 run 目录

移出 `runs/` 的原因：monitor.py 与批量调度器都按 `runs/*` 自动发现，
这些目录若留在原处会被当成当前实验的 run，污染总览与图表。

| 目录 | 来源 | 说明 |
|---|---|---|
| `random_s0/s1/s2` | 2026-09-12 22:44 启动的并发试跑 | 22:46 被 SIGTERM 中止（仅存活 ~2 分钟，零 step 完成，无 SOCIETY_STEP.json）。`pid.json` 停留在 `status=running`，留着会被调度器误判为"运行中"而**静默跳过整个 random 臂**。 |
| `interest_nog_s0` | 早期烟测 | 旧命名（G 因子退役前） |
| `interest_normal_s0` | 早期烟测 | 旧命名 |
| `interest_normal_s0_pre_lifecycle` | 早期烟测 | feed 生命周期修复前 |
| `interest_s0_pre_R20` | 早期烟测 | R 尺度下压前 |
| `random_s0_authfail_0913` | 2026-09-13 01:12 串行批跑首个 run | 卡在 init（`step_count=0`，无 `SOCIETY_STEP.json`）被中止。**根因是凭据而非限流**：2026-09-12 22:49 写入 `.env` 的 API key 被火山方舟整段拒绝（`AuthenticationError`，~0.4s 返回），litellm Router 遂把 deployment 打入 cooldown，日志里表现为 `Rate limit` / `No deployments available` / `[AdaptiveSem] DECREASE`——**次生现象，非真限流**。用户 2026-09-13 01:40 换用 DeepSeek 官方端点后恢复。 |

保留作审计线索，不参与当前分析。

> 上表 `random_s0/s1/s2`（22:44 并发）与 `*_conc2/conc3_aborted` 的"限流"记录同理存疑：
> 其自身 `stderr.log` 里**零** `Rate limit`、仅 1 条 60s 超时；鉴权错误的真实来源是 22:49 之后的密钥失效。
