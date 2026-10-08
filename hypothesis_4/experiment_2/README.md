# Experiment 2：timestamp策展三臂主实验

## 目标与范围

落实已采用的timestamp方案：三臂真实信息时钟、配对行动表、原行为参数和各臂回流制度，继承保留发言内容修复。100人×11周×3算法×3 seeds，共9 runs、9900次行动机会。本轮只准备及离线验收，不调用LLM、不启动实验。

根级runs探索工作已交接，本目录为当前官方实验工作入口；不另建研究任务目录。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 目标、一级资产、实时进度与交接 |
| [EXPERIMENT.md](EXPERIMENT.md) | 完整主设计、基线代码证据、落地方案、patch解释、验收及结论边界 |
| [init/](init/README.md) | 标准库生成器、冻结输入、九份配置、每seed步骤及manifest |
| [2026-10-08-01-timestamp.patch](2026-10-08-01-timestamp.patch) | 三个既有正式模块的最终补丁；基线d4a8319a6477d818dc5efbcc1d475625f14a42fc |
| [2026-10-08-02-functional-verification.json](2026-10-08-02-functional-verification.json) | 24项禁网功能验收结果，0模型调用 |
| [2026-10-08-03-configuration-verification.json](2026-10-08-03-configuration-verification.json) | 官方工作流结果、九配置/900工作区核验、54份源码及资产哈希、干净基线应用证据 |

## 实时进度

- 已完成：核对原设计已采用timestamp、旧主配置尚未接线的差距；通过官方scan-modules、experiment-config prepare/validate/info/run/check；九配置与输入独立冻结。
- 正式代码：三臂均激活arrival路径；chronological使用稳定时间排序、批末入池及当周供给记账，random/interest保持次周回流；共享额外请求990次与新ledger实际接线。原行为参数不变。
- 功能验证：24项通过、0失败；九窗环境演练各693批、1100行动、11周，未来曝光0；同批隔离、分臂回流、跨周供给守恒、恢复一致性和额度耗尽兜底通过。历史20必查样本覆盖两类行动入口；网络连接尝试0、LLM调用0。
- 审查：方案冻结前独立timing_review通过；实现后发现并修正时序周观测遗漏，新增实际发布跨周检查，修正可见词提示说明。最终patch和冻结证据独立终审PASS。
- 机器阶段：控制agent通过CLI将experiment_config登记completed、verification complete；current_stage自动进入run_experiment，继承reroute状态needs_revision、verification not_started。该状态表示尚待新批运行，并非新批执行失败。阶段metadata明确hypothesis_id=4、experiment_id=2；where-am-i顶层ID仍为空，启动时须显式指定，不手改机器JSON。
- 授权：本轮只完成准备及离线验收；manifest execution_authorized=false、active_wall_seconds=null。没有新LLM结果、监督器、checkpoint或定时器。
- 下一步：用户确定新批模型/发送范围、活动时长或费用预算后，按官方引擎CLI显式指定experiment_2的各run配置与目录，并按manifest逐run执行九格矩阵（工作区start包装器限制见下节）；本轮到此交付准备结果。

## 交接边界

行为参数、B和各臂回流保留；baseline-anchor候选未采纳，B的W13尺度/floor限制见方案。45条额外筛查命中未全人工确认，正文与作者分类仍需分别解释。本轮功能成功不代表新生成质量或曲线已经改善。旧四格预算、checkpoint、兼容run链接及旧分析来源不复用；原始结果保持历史位置。

## 最终启动前核对（2026-10-08）

冻结的54项代码/输入/配置/测试哈希全部一致，官方默认配置check复查通过。九组参数经过官方引擎main实际解析，正式schema、693步骤和每组100份Agent specs正确，arrival及990次共享额外请求profile没有在运行器切分时丢失。运行器与日志写入替换为记录器，因此这项检查没有初始化Ray、发送模型请求或生成仿真结果；原24项功能验收因源码/输入/测试无变化继续作为功能证据，不宣称本次重跑了整套测试。

九个结果路径唯一且均不存在，默认run和独立ledger也未创建，不存在需续跑的Experiment 2 checkpoint。`.env`解释器能导入agentsociety2，三项LLM变量均存在；当前接口为`https://ark.cn-beijing.volces.com/api/coding/v3`、模型为`deepseek-v4-1-flash-260910`，这里只核对本地配置，未验证密钥有效性或服务连通性。未来启动前保存实际运行设置并复核与预算一致。

**实际入口限制与处理**：工作区`.claude/skills/agentsociety-run-experiment/scripts/run.py`的start接受`--run-id`但仍使用固定`experiment_2/run/`；上游status/stop实现同样未按run_id区分目录。直接逐九run调用该包装器会共享输出路径。采用该技能明确支持的官方引擎CLI`python -m agentsociety2.society.cli`，逐run显式传入config、steps、run-dir、experiment-id、log-file；状态读取对应run目录的pid/checkpoint/replay，停止针对对应PID使用SIGTERM，不使用包装器的多run status/stop。无需修改实验机制或上游代码。

以下是**未来完成运行授权和预算冻结后**首组random_s0的命令模板，本次没有执行：

```bash
cd /Users/easylife/Project/AgentSociety
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
E2_RUN_DIR=/Users/easylife/Project/AgentSociety/hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_random_s0
mkdir -p "$E2_RUN_DIR"
LITELLM_LOCAL_MODEL_COST_MAP=True "$PYTHON_PATH" -m dotenv -f .env run --no-override -- \
  "$PYTHON_PATH" -m agentsociety2.society.cli \
  --config /Users/easylife/Project/AgentSociety/hypothesis_4/experiment_2/init/configs/timestamp_v1_random_s0.json \
  --steps /Users/easylife/Project/AgentSociety/hypothesis_4/experiment_2/init/steps_s0.yaml \
  --run-dir "$E2_RUN_DIR" \
  --experiment-id timestamp_v1_random_s0 \
  --log-file "$E2_RUN_DIR/engine.log"
```

命令从项目根目录运行，dotenv按与包装器相同的“不覆盖已有进程环境”规则加载凭据，不把密钥放入参数或报告。九组固定顺序为每seed random→chronological→interest，seed 0→1→2，以manifest为准。此模板是单组前台入口，不是已实现的九run预算监督器；批准新预算后才配置监督停止、后台stdout/stderr及进度报告，不复用旧四格控制器。

当前结论：代码、配置和离线功能准备通过；新九run的启动授权、活动时长/费用上限及据此冻结的监督/并发设置尚待确定，manifest继续保持未授权。本次只更新准备核对记录，不改变机器阶段或原冻结方案。完整证据见本级配置验收JSON的prelaunch_check。
