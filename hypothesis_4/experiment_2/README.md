# Experiment 2：timestamp策展三臂主实验

> 当前状态：用户追加的W13共同官方帖覆盖要求未满足，历史初始化需重新论证；配置待修订，不能仅补运行预算后直接启动。见EXPERIMENT.md文末的设定复核。

## 目标与范围

落实已采用的timestamp方案：三臂真实信息时钟、配对行动表、原行为参数和各臂回流制度，继承保留发言内容修复。100人×11周×3算法×3 seeds，共9 runs、9900次行动机会。本轮只准备及离线验收，不调用LLM、不启动实验。

根级runs探索工作已交接，本目录为当前官方实验工作入口；不另建研究任务目录。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 目标、一级资产、实时进度与交接 |
| [EXPERIMENT.md](EXPERIMENT.md) | 完整主设计、基线代码证据、落地方案、patch解释、验收及结论边界 |
| [2026-10-08-04-initial-state-check.py](2026-10-08-04-initial-state-check.py) | 官方帖覆盖与历史初始化的只读/无LLM核对；使用.env解释器运行 |
| [2026-10-08-05-initial-state-evidence.json](2026-10-08-05-initial-state-evidence.json) | 单seed真实归档覆盖、18组外部池数值比较及源哈希，不是闭环仿真 |
| [init/](init/README.md) | 标准库生成器、冻结输入、九份配置、每seed步骤及manifest |
| [2026-10-08-01-timestamp.patch](2026-10-08-01-timestamp.patch) | 三个既有正式模块的最终补丁；基线d4a8319a6477d818dc5efbcc1d475625f14a42fc |
| [2026-10-08-02-functional-verification.json](2026-10-08-02-functional-verification.json) | 24项禁网功能验收结果，0模型调用 |
| [2026-10-08-03-configuration-verification.json](2026-10-08-03-configuration-verification.json) | 官方工作流结果、九配置/900工作区核验、54份源码及资产哈希、干净基线应用证据 |

## 实时进度

- 已完成：核对原设计已采用timestamp、旧主配置尚未接线的差距；通过官方scan-modules、experiment-config prepare/validate/info/run/check；九配置与输入独立冻结。
- 正式代码：三臂均激活arrival路径；chronological使用稳定时间排序、批末入池及当周供给记账，random/interest保持次周回流；共享额外请求990次与新ledger实际接线。原行为参数不变。
- 功能验证：24项通过、0失败；九窗环境演练各693批、1100行动、11周，未来曝光0；同批隔离、分臂回流、跨周供给守恒、恢复一致性和额度耗尽兜底通过。历史20必查样本覆盖两类行动入口；网络连接尝试0、LLM调用0。
- 审查：方案冻结前独立timing_review通过；实现后发现并修正时序周观测遗漏，新增实际发布跨周检查，修正可见词提示说明。最终patch和冻结证据独立终审PASS。
- 机器阶段：用户追加共同事件需求后，控制agent通过CLI reroute至experiment_config，revision_round=9、status needs_revision；原技术验收记录保留为旧规则证据，不代表新需求已经满足。hypothesis_id=4、experiment_id=2，启动仍须显式指定，不手改机器JSON。
- 授权：本轮只完成准备及离线验收；manifest execution_authorized=false、active_wall_seconds=null。没有新LLM结果、监督器、checkpoint或定时器。
- 运行前审核（2026-10-08）：三个独立只读子agent分别复核patch实现、离线功能与配置矩阵，均无blocker；本轮新发现见下节。
- 下一步：先明确共同公告的事件时钟与所有悼念Agent的阅读覆盖，论证历史池并重新冻结/验收配置；这些完成后再确定新批模型/发送范围、活动时长或费用预算，按官方引擎CLI显式指定experiment_2的各run配置与目录，并按manifest逐run执行九格矩阵（工作区start包装器限制见下节）；本轮到此交付准备结果。

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

## 此前技术审核结论（2026-10-08，追加事件需求前）

三个独立只读子agent分别审查最终patch实现、离线功能复现、配置矩阵与预算，均未发现blocker，未修改任何文件或机器阶段。

- **patch实现**：干净基线副本（worktree于d4a8319）可应用，应用后三个文件与工作树逐字节一致；`git diff d4a8319`的哈希等于patch文件本身，证明工作树差异即此patch。`stamp()`固定+08:00且上海无夏令时，25字符时间串字典序等价于时间序（2万组随机含并列与跨年用例通过）；同批互不可见无泄漏路径；`_agent_posts_pooled_prev`只喂已退役的G观测，漏斗供给指标走`_env_row.agent_supply`，三臂同口径；旧anchored_v1、weekly_lag1与四格诊断无回归。
- **离线功能复现**：24项重跑通过、0失败，与记录一致；独立重放九配置得693批/1100行动/11周、未来曝光0、同批隔离、并列稳定、恢复一致、周度供给守恒、额度耗尽兜底，20条必查样本×两行动入口双面断言。
- **配置矩阵与预算**：同seed三臂仅`recommendation_algorithm`不同；跨seed仅`random_seed`与真实帖样本路径不同；9900机会/990额外请求/每行动1次/单ledger与代码一致；授权状态与机器记录一致。

### 本轮新发现与处理

| 发现 | 处理 |
|---|---|
| 相对ledger路径依赖进程CWD。实测本机Ray worker CWD与驱动进程一致，从项目根启动可正确共享；若从其他目录启动，`mkdir(parents=True)`会静默新建幻影账本使990额度重置。现有测试只用绝对路径覆盖该字段 | 启动必须以项目根为CWD；README模板已满足，列为启动前置条件 |
| 单run `object_store_memory` 1GB，本机10核/16GB；旧四格控制器为严格串行（逐个`Popen`等待），九run并行无先例 | 建议串行，或至多2并发；并发设置属待定的监督项 |
| 本实验尚无`.gitignore`规则，九run原始产物（按四格诊断外推约270MB）会全部进入untracked | 启动前补与experiment_1同构的忽略块，只保留README与`_derived/` |
| 功能记录"网络连接尝试0"需加限定：litellm导入时抓取价格表，仅`test_arrival_timing.py`未设`LITELLM_LOCAL_MODEL_COST_MAP`且按字母序先导入。无模型调用、无数据外泄，正式启动模板已设该开关 | 测试文件在54项冻结哈希内，本次不改；限定已在此登记，留待下次重新冻结时补齐 |
| `_compute_event_floor_ids` docstring写"chronological / interest"，实际门控仅对interest生效 | 过时注释，位于冻结文件内；留待下次重新冻结时修正，不影响矩阵 |
| 三seed共享同一人口与行动时刻（继承experiment_1），seed只改变真实帖样本与随机流种子；原文档未显式说明，易被读成三套人口 | 已在EXPERIMENT.md行动机会表补显式说明；跨seed可支持的结论边界不变 |

### 审核后仍缺的启动条件

上述审核只覆盖当时冻结实现。当前首先需修订共同事件的时钟/阅读覆盖并审查历史初始化，原三项启动pending仍保留：新批模型/发送范围与启动授权；运行时长或费用预算及据此冻结的监督停止设置；并发与实际模型运行设置。九run监督器本身尚未实现，旧四格控制器按设计不复用。

此前技术核对结果保存于本级配置验收JSON的prelaunch_check。该核对未涵盖下节用户追加的共同事件条件；当前配置待修订，manifest继续保持未授权。

## 共同事件与历史初始化的当前裁定

已核实：九配置的5位悼念Agent在原官方时刻前用掉W13机会；真实timestamp-random归档仅1/22阅读该官方帖，interest17/22。17历史是分层现实样本但非中性占位，W13随机曝光占比和数值开口对其敏感。无LLM、无Agent反馈的18组比较与独立重放一致；尚未证明完整波峰受到“致命”影响。两点完整依据、数值表和建议在EXPERIMENT.md，不另建主题报告。

用户要求的W13周初共同信息覆盖作为新验收需求；具体公告渠道/时钟定义与历史初始化替代方式仍待方案裁定。本轮未改变冻结代码、参数、配置或历史结果；此前技术审查PASS不能替代这一研究设定审查。流水线回到experiment_config待修订，运行预算仍未授权。后续不得直接使用先前命令模板启动现有九配置。
