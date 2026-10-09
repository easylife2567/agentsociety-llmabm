# Experiment 2：timestamp策展三臂主实验

> 当前状态：已落实用户采纳的W13共同顺延方案，完成30项禁网离线验收；方案与最终patch独立审查均PASS。本轮未启动LLM。

## 目标与范围

100人×W12–W22×random/chronological/interest×3 seeds，共9 runs、9900次行动机会。三臂共享timestamp真实信息时钟和行动表，保留行为参数、各臂回流、内容修复及17条历史池。只将5位过早悼念Agent的W13决策顺延，保证interest的22人在官方取得资格后按原U决策；其他人及其他周保持。

根级runs探索已交接，本目录是当前官方实验入口，不另建研究任务目录。实时进度及交接以本README为准，完整方法见EXPERIMENT.md。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 目标、一级资产、实时进度和交接 |
| [EXPERIMENT.md](EXPERIMENT.md) | 主矩阵、机制、已采纳W13安排、代码事实、patch解释、验收及结论边界 |
| [init/](init/README.md) | 标准库生成器、冻结输入、九配置、693步与manifest |
| [.gitignore](.gitignore) | 忽略本级可丢弃tmp，不忽略持久验收证据 |
| [2026-10-09-01-official-timing-review.md](2026-10-09-01-official-timing-review.md) | nature-reviewer模拟方法评审包；其中共同顺延5次机会建议已获用户采纳 |
| [2026-10-09-02-event-week-schedule.patch](2026-10-09-02-event-week-schedule.patch) | 本次四文件最终修改；基线1539418abf98800d4a3284317c68e8e5ff91319f |
| [2026-10-09-03-event-week-check.py](2026-10-09-03-event-week-check.py) | 从项目根用.env解释器执行的禁网功能检查；不跑社会引擎或LLM |
| [2026-10-09-04-event-week-verification.json](2026-10-09-04-event-week-verification.json) | 当前30项检查、九窗阅读覆盖、900份实际profile读取及41项冻结哈希 |
| [2026-10-08-01-timestamp.patch](2026-10-08-01-timestamp.patch) | timestamp基础接线，基线d4a8319a6477d818dc5efbcc1d475625f14a42fc |
| [2026-10-08-02-functional-verification.json](2026-10-08-02-functional-verification.json) | 基础版本24项功能证据，当前继承项已复跑 |
| [2026-10-08-03-configuration-verification.json](2026-10-08-03-configuration-verification.json) | 基础版本54项源码及资产哈希与启动入口核验；不用于当前版本的全量哈希匹配 |
| [2026-10-08-04-initial-state-check.py](2026-10-08-04-initial-state-check.py) | 基础版本官方覆盖与历史池核对脚本，受当时源哈希约束；不作为当前配置验收入口 |
| [2026-10-08-05-initial-state-evidence.json](2026-10-08-05-initial-state-evidence.json) | 原单seed归档覆盖、18组外部池数值比较；不改写历史证据 |
| tmp/ | 可丢弃候选、测试日志和临时工作区，不进入Git |

## 实时进度

- 方案：用户明确接受三臂共同顺延5次过早机会。独立方案审查PASS，确认原表、固定抽样结果、空批处理和环境/Agent双侧接线可行。
- 实现：环境、arrival调度、Agent行动门及配置生成器已通过保存patch修改；原五人baseline小时保留，仅W13覆盖为70→61、21→67、22→96、20→113、56→166。三臂三seed同表，原W13 hour18为空批，693步未改。
- 配置：官方scan/info、experiment-config validate/info/run/check通过。默认兼容配置官方check通过；九份独立配置均通过官方引擎schema，900份CLI profile拆分、正式Agent工作区创建与读取覆盖一致。
- 功能：30项禁网检查全部通过，0失败、0错误、0网络尝试、0LLM调用；原24项继承功能复跑。九窗各693批、1100唯一Agent×周机会、11周，普通未来曝光0；旧小时不行动、新小时执行U门槛、其他周恢复原时刻、恢复不重复、错误覆盖拒绝通过。
- 官方阅读：interest三个seed各22/22悼念Agent在W13官方后决策，feed最多10且官方首位，生成可读摘录也首位。无Agent产出的环境演练中random为4/6/4人、chronological为6/6/6人收到；这些计数只用于证明没有共同强制槽，不是新LLM结果或最终阅读率预测。
- patch：声明commit的干净副本可应用，应用后四文件与正式工作树逐字节一致；实现后独立终审PASS；审查者另复跑新增6项并验证旧arrival及legacy无新字段checkpoint的空表恢复兼容。
- 机器阶段：控制agent已通过CLI将experiment_config标为completed、verification complete；当前推荐阶段为run_experiment needs_revision，revision_round9，尚未运行。active_reroute中的共同公告/历史池替换理由是原修订记录，当前实施以用户已采纳的分臂阅读与5次共同顺延为准；显式hypothesis_id=4、experiment_id=2记录在本阶段metadata，后续调用仍指定这两个ID。没有手改机器JSON。
- 授权：只准备与离线验收；manifest execution_authorized=false、active_wall_seconds=null。九run结果目录、LLM调用、监督器及新定时器均未创建，旧四格预算和checkpoint不复用。
- 下一步：实际启动需要确定本九run模型/发送范围、时长或费用预算及监督停止设置，本轮不启动。

## 交接与结论边界

官方3月24日20:00是建模约定，不是观测发布时间；分散安排是事件后参与条件，不能证明现实22人必然如此行动。每人仍一次机会，收到官方与愿意发言分别记账。interest保留10槽内置顶，random/chronological允许漏读。比较继续是完整策展制度效应，含原生命周期、议程和回流差异。

B保留现有尺度和floor；独立baseline-anchor候选未采纳。20条内容必查样本仍覆盖两类入口，45条额外筛查命中未全部人工确认。离线成功不能证明新正文质量或闭环曲线改善。历史54项哈希中的正式文件已随本次授权修改，当前验收入口为本级03脚本/04记录，不将历史证据静默覆盖成新结果。

## 启动入口和仍需确定的运行项

官方run-experiment包装器虽接受run_id，但仍使用固定experiment_2/run路径，其status/stop同样不按run_id区分。九run应使用该技能支持的正式引擎CLI，逐run显式指定config、steps、run-dir及log-file，以manifest顺序每seed random→chronological→interest、seed 0→1→2推进。

以下是未来完成运行授权和预算冻结后首组random_s0的命令模板，本次没有执行：

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

启动以项目根为CWD，否则相对ledger可能指向另一账本。单run object_store_memory为1GB，本机10核/16GB；建议串行，实际并发和预算停止需随启动设置冻结。九run预算监督器及原始产物忽略规则留在正式启动准备时处理，不复用旧四格控制器。此前核对的接口/模型只代表本地配置存在，不证明服务连通或新批发送授权；启动时保存实际设置。
