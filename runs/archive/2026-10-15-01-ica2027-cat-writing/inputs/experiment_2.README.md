# Experiment 2：timestamp策展三臂主实验

本文稿分工已于2026-10-12按作者修订同步：本实验主要回答问题（2）算法与发帖的循环机制，以及问题（3）完整策展制度是否差异化推动悼念向玩梗转变。问题（1）的现实轨迹与平台差异由原始数据分析回答。理论来源与实验对应见[EXPERIMENT.md](EXPERIMENT.md)，作者文稿接入见[paper](../../paper/README.md)。

> 当前状态：2026-10-15 06:52（北京时间）既定九次主实验全部完成。每次693步、1100次行动机会，合计9900次行动机会、1818条Agent帖子，额外调用4次。实际执行记录见runs/timestamp_v1/batch_execution.json；30分钟报告定时器已暂停，后续进入结果整理。

## 目标与范围

以“可见性配置—选择性表达—内容回流”的传播反馈回路解释逝者表征重组，检验既有倾向稳定条件下的差异化激活与内容循环。研究目标是机制重演与解释，当前理论框架和操作化见[EXPERIMENT.md](EXPERIMENT.md)。

100人×W12–W22×random/chronological/interest×3 seeds，共9 runs、9900次行动机会。三臂共享timestamp真实信息时钟和行动表，保留行为参数、各臂回流、内容修复及17条历史池。只将5位过早悼念Agent的W13决策顺延，使22位悼念Agent在官方取得资格后获得决策机会，按实际feed与原U决定是否发言；其他人及其他周保持。

此前到达时机探索已交接，U标定与文稿run已归档，后续写作依据已落实paper目录；本目录是当前官方实验入口，不另建研究任务目录。实时进度及交接以本README为准，完整方法见EXPERIMENT.md。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 目标、一级资产、实时进度和交接 |
| [EXPERIMENT.md](EXPERIMENT.md) | 主矩阵、机制、已采纳W13安排、代码事实、patch解释、验收及结论边界 |
| [run_main_experiment.py](run_main_experiment.py) | 正式九次串行启动与逐次进度；调用官方CLI，失败时停止而不自动重跑 |
| [runs/](runs/README.md) | 当前主实验的运行计划、实际记录、生成帖与日志 |
| [init/](init/README.md) | 标准库生成器、冻结输入、九配置、693步与manifest |
| [.gitignore](.gitignore) | 忽略本级可丢弃tmp，不忽略持久验收证据 |
| [2026-10-09-01-official-timing-review.md](2026-10-09-01-official-timing-review.md) | nature-reviewer模拟方法评审包；其中共同顺延5次机会建议已获用户采纳 |
| [2026-10-09-02-event-week-schedule.patch](2026-10-09-02-event-week-schedule.patch) | 本次四文件最终修改；基线1539418abf98800d4a3284317c68e8e5ff91319f |
| [2026-10-09-03-event-week-check.py](2026-10-09-03-event-week-check.py) | 从项目根用.env解释器执行的当前共同顺延及官方普通推荐的禁网功能检查，输出06；不跑社会引擎或LLM |
| [2026-10-09-04-event-week-verification.json](2026-10-09-04-event-week-verification.json) | 官方置顶版本30项原验收、900份实际profile及哈希；保留为历史证据 |
| [2026-10-09-05-ordinary-official.patch](2026-10-09-05-ordinary-official.patch) | 当前官方普通推荐的五文件最终patch；基线7adc50d08b41e1c3da26d62ec3833d9d6694ad5b |
| [2026-10-09-06-ordinary-official-verification.json](2026-10-09-06-ordinary-official-verification.json) | 当前官方普通推荐与继承功能验收、实际custom路径及冻结哈希 |
| [2026-10-08-01-timestamp.patch](2026-10-08-01-timestamp.patch) | timestamp基础接线，基线d4a8319a6477d818dc5efbcc1d475625f14a42fc |
| [2026-10-08-02-functional-verification.json](2026-10-08-02-functional-verification.json) | 基础版本24项功能证据，当前继承项已复跑 |
| [2026-10-08-03-configuration-verification.json](2026-10-08-03-configuration-verification.json) | 基础版本54项源码及资产哈希与启动入口核验；不用于当前版本的全量哈希匹配 |
| [2026-10-08-04-initial-state-check.py](2026-10-08-04-initial-state-check.py) | 基础版本官方覆盖与历史池核对脚本，受当时源哈希约束；不作为当前配置验收入口 |
| [2026-10-08-05-initial-state-evidence.json](2026-10-08-05-initial-state-evidence.json) | 原单seed归档覆盖、18组外部池数值比较；不改写历史证据 |
| tmp/ | 可丢弃候选、测试日志和临时工作区，不进入Git |

## 实时进度

- 采用规则：三臂官方按共同20:00取得资格；interest官方不置顶、不参与悼念保底，正常参与兴趣评分和抽样。其他悼念帖最多5条保底、生命周期、10槽、U、内容修复与各臂回流保持。
- 时间：五人W13共同顺延61/67/96/113/166保持；三臂三seed共表，其他95人及其他周不变，原hour18为空批，693步未改。保证事件后决策机会，不保证22人都读到官方或都发言。
- 正式路径：registry实际扫描并加载custom/envs/curation_dynamics_space.py及custom/agents/curation_discourse_agent.py；arrival推荐实现位于custom/envs/curation_arrival_schedule.py。init生成器仅声明配置，实验目录patch用于记录和应用，不是运行模块。
- 配置：九配置显式arrival_official_policy=ordinary；原人口、样本、共同顺延表、steps和预算保持。准备期manifest保留其原始状态，本次实际运行授权记录在runs/timestamp_v1/runtime_plan.json。官方run/check通过；35项禁网验收全部通过，0失败/错误/网络/LLM，42份当前冻结哈希一致；九窗各693批/1100机会/11周，900份实际CLI/profile工作区读取通过。新5项核验官方普通评分、可选可漏、候选时钟、历史兼容和custom源码路径。
- 审查：独立方案审查PASS，已将“官方标记等价”验收限定在固定保底集合的普通评分/抽样层；最终patch审查PASS，审查者独立复跑新5项通过，干净基线应用与五文件一致。
- 机器阶段：已通过CLI登记run_experiment in_progress，hypothesis_id=4、experiment_id=2、batch_id=timestamp_v1；不自动提交Git。
- 授权：用户2026-10-14明确要求启动主实验，并在外部调用审批处再次授权。范围为既定九次、9900次表达机会及最多990次额外请求；不包含新增U或关闭回流实验。实际模型deepseek-v4-1-flash-260910（现有火山方舟服务），一次只运行一个制度/重复，最多48小时总运行时限。
- 执行结束：九次全部完成，监督进程及最后一次引擎进程已退出；实际记录以batch_execution.json及各次原始输出为准。运行控制调用官方CLI并逐次核对实际完成记录；任一步失败停止后续，不重抽或改参数。

## 交接与结论边界

官方20:00是建模约定；五人分散安排是条件化参与假设。官方可能被普通兴趣槽选中或漏读，不通过保底绕过选择；收到后是否发言仍由U判定。其他保底及回流差异保持，比较仍是完整制度效果。原04的22/22首位阅读属于置顶版本历史验收，当前以06证据为准，不静默改写原结果。禁网功能演练不代表新LLM闭环波峰或阅读率预测。

B尺度/floor、17条历史池及20条内容必查样本保持；45条额外命中未全人工确认。旧54项或41项源码哈希不代表当前冻结状态，当前入口为03脚本，当前输出为06。

## 当前启动入口与运行约定

官方run-experiment包装器虽接受run_id，但仍使用固定experiment_2/run路径，其status/stop同样不按run_id区分。九run应使用该技能支持的正式引擎CLI，逐run显式指定config、steps、run-dir及log-file，以manifest顺序每seed random→chronological→interest、seed 0→1→2推进。

实际批量启动使用run_main_experiment.py；下列为监督器调用的首组random_s0官方CLI命令形式：

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

启动以项目根为CWD，否则相对ledger可能指向另一账本。单run object_store_memory为1GB，本机10核/16GB；当前按串行运行，实际设置已写入runtime_plan.json。各run原始产物保留在独立目录并忽略Git跟踪，不复用旧四格控制器。外部调用已获用户授权，生成是否成功以实际用户记录为准。

## 已采用的写作与结果整理依据

[后续论文具体写作报告](../../paper/后续论文具体写作报告.md)和[必要实验与结果整理](../../paper/必要实验与结果整理.md)已落实主项目。保持当前主设计，完成此批后从已有记录整理轨迹、群体接触、表达参与、生成帖再次阅读和实际正文；默认新增U实验为零。

检查当前进度：使用项目解释器执行`run_main_experiment.py --status`；停止：向batch_execution.json记录的supervisor_pid发送TERM，停止当前及后续运行，已有资料保留，不自动恢复。
