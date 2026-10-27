# 首次官方启动失败

北京时间2026-10-15 20:21启动no_b_s0，官方CLI在扫描custom时因工作区不一致报403；监督器按异常即停规则结束，后八次未启动。没有Agent创建、决策、模型调用或额外账本消耗。监督器和引擎都已退出，定时器已暂停。

| 直接资产 | 用途 |
|---|---|
| [RESULT.json](RESULT.json) | 停止事实、时间、根因、0调用及下一步边界 |
| engine.log、stdout.log、stderr.log、pid.json | 失败run的原始日志及引擎failed状态副本；原文件仍在results中 |
| runtime_plan.json、batch_execution.json | 当次实际用户授权、模型/预算/源码和监督器停止状态副本 |
| run_ablation.attempt-01.py | 当次启动控制源，SHA256与runtime_plan一致；保全启动布局原状 |
| isolated-pipeline.json | 通过官方CLI更新的隔离run_experiment=failed快照，主项目机器状态未改 |

根因证据为SDK`society/cli.py`第442—451行：从run_dir.resolve向父级查找custom。本轮持久输出在隔离worktree外，因此误定位主项目custom，与隔离WORKSPACE_PATH冲突；失败发生在init_dispatchers之前。之前离线验收直接在隔离区扫描registry，没有覆盖完整官方CLI的输出布局，是启动配置遗漏，不是已完成的LLM消融。

保持停止，不自动重试、不覆盖原失败目录。后续需要修正启动布局并核验真实CLI入口；不能通过放开路径检查或直接改用主项目模块来规避隔离要求。
