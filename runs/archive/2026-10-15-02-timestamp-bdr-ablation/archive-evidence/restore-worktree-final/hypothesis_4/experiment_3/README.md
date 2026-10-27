# timestamp B/D/R隔离候选资产

此目录仅存在于消融run的隔离worktree及恢复包，不是主项目新建的正式experiment_3。实时状态统一见本run README；不在此维护第二份进度。

| 直接资产 | 用途 |
|---|---|
| [EXPERIMENT.md](EXPERIMENT.md) | 候选范围和规模；完整研究设计见消融run EXPERIMENT.md |
| [init/](init/README.md) | 冻结来源、九变体、步骤及manifest |
| [verify_offline.py](verify_offline.py) | 官方配置操作、真实profile与效用、全窗、恢复和继承功能验收 |
| [offline_guard/](offline_guard/README.md) | 本进程及生成器子进程禁网钩子 |
| [test_inputs/](test_inputs/README.md) | 一份历史内容修复验收输入，不是新消融仿真输出 |
| verification/ | 本工作区离线验收JSON及日志；持久证据另存run的evidence/verification |

从隔离workspace根使用项目现有SDK解释器，依次执行：

```bash
"$BDR_PYTHON" hypothesis_4/experiment_3/verify_offline.py setup
"$BDR_PYTHON" hypothesis_4/experiment_3/verify_offline.py generate
"$BDR_PYTHON" hypothesis_4/experiment_3/verify_offline.py verify
```

`BDR_PYTHON`应为run依赖记录中的项目解释器；无需复制.env或凭据。setup调用官方validate/info；generate调用官方prepare/run/check，仅生成配置；verify逐个调用官方check，并做功能检查。这里的run是配置生成动作，不启动社会引擎。

输入和账本使用相对workspace的独立experiment_3路径。`runs/timestamp_bdr_v1/`账本/运行目录尚未创建。不得从主项目根执行这些候选配置；正式LLM运行、采用和主流水线更新均未授权。
