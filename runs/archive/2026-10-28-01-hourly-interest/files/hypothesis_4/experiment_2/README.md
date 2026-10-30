# Experiment 2：timestamp策展三臂主实验

> 本run隔离工作区新增[小时回流候选设计](EXPERIMENT.md)及[版本化配置](init/hourly_return_v1/README.md)：随机/兴趣计划新跑各10次，时序10次待复用条件核对。当前仅实现和离线验收，未启动；下方完成状态仅属于原timestamp_v1批次。

本文稿分工已于2026-10-12按作者修订同步：本实验主要回答问题（2）算法与发帖的循环机制，以及问题（3）完整策展制度是否差异化推动悼念向玩梗转变。问题（1）的现实轨迹与平台差异由原始数据分析回答。理论来源与实验对应见[EXPERIMENT.md](EXPERIMENT.md)，作者文稿接入见[paper](../../paper/README.md)。

> 当前状态（北京时间2026-10-23 14:48核验）：seed3–9新增21次三臂主实验于2026-10-23 14:39:57全部完成并逐次核验通过；结合原seed0–2，每臂已补齐10个seed。监督器及全部引擎均已退出，seed-3-9-30定时汇报已暂停。原中断现场保留；已按后续授权完成三臂各10seed的原口径主分析，报告见下；不补或改动消融。

## 运行目录（统一组织）

seed0–9的三臂主实验现统一位于[runs/timestamp_v1/](runs/timestamp_v1/README.md)，按算法×seed排列，共30次完整条件；不再保留timestamp_v1_seed3_9实体目录。两次启动仅作为同一实验的[执行历史](runs/timestamp_v1/execution_records/README.md)，预算、恢复与失败证据分别保持原字节。最终路径、旧新对应关系及逐文件迁移校验见[relocation.json](runs/timestamp_v1/relocation.json)。历史正文中的批次ID和旧路径保留溯源，不代表两个实验。

## 三臂各10seed的主实验分析

本轮用户明确要求沿用原分析口径，核查补种子后的结论稳定性。已从实际完成路径读取旧9次与新21次，共30run、330个run×week、3000份Agent和6041篇成功发布帖；原九次周表与原论文图3/4指标逐格复现。兴趣seed6使用resume1、随机seed7使用retry1，旧中断现场不进入科学汇总，原始结果保持。

核心窗仍W19–W22，按固定作者类型成功posted计算供给，先每run内比例再seed均值。合计10seed的随机/时序/兴趣晚期玩梗帖均值为3.1/45.4/37.8，份额10.780%/75.011%/68.472%。兴趣与时序相对随机在全部10seed及新增7seed均同向；逐一剔除seed的配对均值方向保持。时序相对兴趣帖数9正1平、份额9正1负，因此不支持“兴趣最强”，也不意味着每条轨迹、每个seed相同。

**当前采用口径（用户2026-10-24确认）：新旧模型版本在本研究中视为等价，三臂各10seed合并作为主分析。**精确请求/返回标识保留作溯源：旧seed0–2请求260910、返回无日期别名，新seed3–9返回261017；旧3/新7表仅为补充批次检查。合计10seed的15项精确符号翻转经Holm校正均p=0.029296875。

**时序臂的设计限制：不能把较高结果单独归因于时序排序。**实际`custom/envs/curation_arrival_schedule.py`中，外部真实帖在三臂均按共同发布时间取得资格；Agent生成帖则在时序臂批末入池、后续小时即可见，随机/兴趣臂延迟至次周。因此当前时序制度同时包含排序、生成帖更快入池与周内回流，以及候选池规则的差异。较强玩梗传播可能部分来自更快回流，本轮无法分解或量化各机制贡献。实际feed接触也不等于全文阅读，作者类型不等于独立语义分类。

[中文报告](../../presentation/hypothesis_4/report_zh.md) / [HTML](../../presentation/hypothesis_4/report_zh.html)，英文同级；数值、来源、配对与原始哈希见该目录data/seed10_*。未改论文正文、原3seed图表或消融。数值、双语报告及综合均经独立审查；官方release与synthesis核验通过后通过CLI登记analysis=completed。综合见[synthesis](../../synthesis/synthesis_report_zh.md)。

## 目标与范围

以“可见性配置—选择性表达—内容回流”的传播反馈回路解释逝者表征重组，检验既有倾向稳定条件下的差异化激活与内容循环。研究目标是机制重演与解释，当前理论框架和操作化见[EXPERIMENT.md](EXPERIMENT.md)。

100人×W12–W22×random/chronological/interest；原3 seeds共9次、9900次行动机会已完成；新增seed3–9的21次、23100次行动机会也已全部完成并核验，每臂现为10个seed。本批曾因服务额度联停，再按用户明确恢复授权继续，原中断现场保留，详见实时进度。三臂共享timestamp真实信息时钟和行动表，保留行为参数、各臂回流、内容修复及17条历史池。只将5位过早悼念Agent的W13决策顺延，使22位悼念Agent在官方取得资格后获得决策机会，按实际feed与原U决定是否发言；其他人及其他周保持。

此前到达时机探索已交接，U标定与文稿run已归档，后续写作依据已落实paper目录；本目录是当前官方实验入口，不另建研究任务目录。实时进度及交接以本README为准，完整方法见EXPERIMENT.md。

## 一级资产

| 资产 | 职责 |
|---|---|
| [README.md](README.md) | 目标、一级资产、实时进度和交接 |
| [EXPERIMENT.md](EXPERIMENT.md) | 主矩阵、机制、已采纳W13安排、代码事实、patch解释、验收及结论边界 |
| [run_seed_extension_recovery.py](run_seed_extension_recovery.py) | 用户明确恢复后的当前两路监督器；保留完成与失败现场、干净检查点接续、失败条件独立重试、累计含失败尝试的预算，后续异常联停 |
| [run_seed_extension_parallel.py](run_seed_extension_parallel.py) | 原两路交接监督器，代码和历史运行证据保持 |
| [parallel_control/](parallel_control/README.md) | 串行交接原始状态、5项禁网假进程检查、PID连续与预算/截止守恒证据 |
| [run_seed_extension.py](run_seed_extension.py) | 新批21次串行启动、独立status、模型版本核对和失败停批；调用官方CLI |
| [seed_extension_launcher_check.json](seed_extension_launcher_check.json) | 控制器失败不续跑/成功按序推进的离线检查；无CLI或LLM调用 |
| [run_main_experiment.py](run_main_experiment.py) | 正式九次串行启动与逐次进度；调用官方CLI，失败时停止而不自动重跑 |
| [verify_seed_extension.py](verify_seed_extension.py) | 新增21配置禁网验收、真实profile恢复和运行条件核对；不启动引擎或模型 |
| [probe_current_model.py](probe_current_model.py) | 最多3次授权接口测试，复用旧真实提示；证据存在时拒绝自动重复调用 |
| [model_compatibility_probe.json](model_compatibility_probe.json) | 实际请求别名、返回版本、消息、响应检查和用量；与离线验收分开 |
| [seed_extension_verification.json](seed_extension_verification.json) | 实际离线验收、旧资产保全、模型差异和当前运行库快照 |
| [runs/](runs/README.md) | 唯一timestamp_v1主实验目录，三臂各10seed结果及执行历史 |
| [run_asset_paths.py](run_asset_paths.py)、[run_storage_merge.patch](run_storage_merge.patch) | 旧证据路径定位与读取入口路径修订；不改科学逻辑 |
| [init/](init/README.md) | 标准库生成器、冻结输入、原九配置和新增21配置、693步及分批manifest |
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

- 执行终态：北京时间2026-10-23 14:39:57完成21/21（seed3–9×random/chronological/interest），最后一路为兴趣seed9；逐一从实际输出路径重新读取核验，不能只依据监督器摘要。唯一当前执行状态仍为本批batch_execution.json，active_runs为空，监督器及21次实际引擎PID均已退出。
- 完整性核验：每次693步、11个完整周、1100唯一环境Agent×周行动、100份Agent及1100条完整唯一决策；环境行动和Agent决策都精确覆盖Agent1–100×W12–W22，既无重复也无缺失。共2100份Agent、23100次环境行动及23100次决策，最终21次结果无行动/发布失败。正文发布记录具有正文、post_id及实际返回模型。未作曲线、比较、显著性或结论分析。
- 路径及保全：兴趣seed6取timestamp_v1_interest_s6_resume1，随机seed7取timestamp_v1_random_s7_retry1，其余依照recovery_1.json实际路径。两次原中断目录、第一次停止证据terminal_check.json和stopped_execution_1.json保持；新的完整核验证据为[runs/timestamp_v1/execution_records/seed3_9/completion_check.json](runs/timestamp_v1/execution_records/seed3_9/completion_check.json)，包含逐run核验及原始输出SHA256，未覆盖历史证据。原计划、105项冻结源码/输入及原中断环境/Agent证据核对保持。
- 最终用量：21次完整结果发布4223帖、正文请求4231次；旧随机seed7失败尝试的54次另计，因此全批正文外层请求4285/25410，共享额外请求8/2310。兴趣seed6副本原有175次只累计一次。原3次兼容性测试（3697tokens）及恢复探针1次（36tokens）单列；SDK辅助请求与内部重试不在正文账本，4285不是全部API请求数。
- 模型与时限：请求别名deepseek-v4.1-flash，完成结果全部正文返回deepseek-v4-1-flash-261017；旧批260910版本和本批分开保留。原首次启动至完成约14小时59分12秒（含停机等待），原48小时截止2026-10-24 23:40:45未变，完成时尚余约33小时00分48秒。
- 机器登记及汇报：官方CLI已登记本批run_experiment=completed、verification=complete，metadata明确hypothesis_id=4、experiment_id=2、batch_id=timestamp_v1_seed3_9和完整核验证据。seed-3-9-30已通过automation_update设为PAUSED，不再周期空报；旧30-2保持暂停。完批时仅做完整性核验；后续用户明确授权的30run主分析见上节。未补充消融、归档、commit或push。

### 恢复授权与启动历史（保留）

- 恢复授权及验收：用户“额度已经恢复，尝试继续”构成本次恢复授权。10:18一次最小接口探针成功（36tokens），实际返回deepseek-v4-1-flash-261017，原3次兼容性探针另列。禁网检查读取官方checkpoint、完整恢复环境及100份Agent决策；921条唯一Agent决策与环境行动逐条一致。假进程检查通过最多2路、再次失败联停及失败请求不归零。证据见本批recovery_probe_1.json和recovery_check_1.json；临时检查夹具的路径错误修正已披露，未改原始记录或调用模型。
- 恢复启动历史：10:24启动监督器25815；兴趣seed6引擎25824使用timestamp_v1_interest_s6_resume1副本和官方--resume从580步接续，随机seed7引擎25831使用timestamp_v1_random_s7_retry1从头独立重试。10:25实际核对两引擎与监督器均存活并推进，兴趣已586步/931决策、随机已4步/5决策，正文实际返回版本一致、无行动失败。后续按seed与三臂manifest补空位，已完成11次不重复运行。
- 恢复边界：随机seed7原失败发生在决策前，但当周记录已落盘，直接--resume会因周去重跳过失败决策，无法获得1100条完整成功决策；故原失败目录完整保留，另建独立重试目录。该旧尝试224行动/54帖不计完整结果，54次正文请求仍计入全批25410上限。兴趣seed6副本包含已有175次请求，累计时不再另加原目录以免重复。
- 冻结与账本：原runtime_plan.json、11次完成目录、两次原中断目录、terminal_check.json均保持。停止状态原字节另存stopped_execution_1.json，本次授权与实际路径映射见recovery_1.json；唯一当前执行状态仍batch_execution.json。原105项源码/输入哈希一致，不改custom机制、科学配置、模型或凭据；共享额外账本沿用原值5/2310，正文总上限25410且包含失败尝试，原截止2026-10-24 23:40:45不变。
- 恢复启动时机器登记及定时器：已通过CLI将本批run_experiment从failed更新为in_progress、verification=partial，metadata明确H4E2及batch_id。seed-3-9-30已通过automation_update恢复ACTIVE，每30分钟报告当前两路、真实路径与包含旧失败54次的累计预算，终态再暂停。当前控制器为run_seed_extension_recovery.py，不能用旧parallel脚本仅匹配旧监督器名称来推断新监督器退出。后续再失败即联停，不自动再次重试；不补消融、不自动分析、归档、commit或push。

### 第一次停止的历史事实（保留）

- 首次停止：北京时间2026-10-23 04:01:14停止，实际运行4小时20分29秒。完成11/21：seed3–5三臂及seed6随机/时序；seed6兴趣、seed7随机中断，剩余8次未启动。重新读取11次原始引擎/环境/Agent文件，各693步、1100唯一环境行动、11周、100份Agent与1100唯一决策且无行动失败。终态只读核验见[runs/timestamp_v1/execution_records/seed3_9/terminal_check.json](runs/timestamp_v1/execution_records/seed3_9/terminal_check.json)。
- 停止原因：两路stderr均返回服务5小时额度耗尽。random seed7的Agent31在W14决策前发生RayTaskError(LLMDispatchError)，记录action_failed、正文生成尝试0；监督器按冻结规则联停两路。日志中的Interrupted by user是控制器发出的中断信号，不代表用户手动停止。服务日志提示额度2026-10-23 04:57:46恢复，未联网验证恢复情况，不据此自动重启。
- 中断位置：兴趣seed6模拟W21，580/693步、921/1100唯一行动、9/11周汇总、175篇发布/175次正文请求；随机seed7模拟W14，141/693步、224/1100唯一行动、2/11周汇总、54篇发布/54次正文请求，含1次行动失败。各自checkpoint、环境、Agent、replay及日志原样保留；两次均不计完成。
- 用量与版本：全批2412篇已发布，正文外层请求2417/25410，共享额外请求5/2310，前置3次接口测试另列。实际正文返回均deepseek-v4-1-flash-261017，旧批请求版本deepseek-v4-1-flash-260910单独保留。SDK环境路由等辅助模型请求和内部自动重试未计入正文账本；2417不是全API请求总数。此次停止来自服务额度，并非正文预算耗尽。
- 时限与进程：原截止2026-10-24 23:40:45不变，停止时尚余43小时39分31秒。实际核对监督器83453、兴趣seed6引擎1346、随机seed7引擎3539均不存在；状态文件残留active_runs和pid.json的running不表示进程仍运行。实际授权与105项冻结哈希仍见runtime_plan.json，不覆盖原始证据。
- 首次停止时机器登记：已通过官方CLI更新run_experiment=failed、verification=partial，metadata明确hypothesis_id=4、experiment_id=2、batch_id=timestamp_v1_seed3_9及完成/中断/未启动数。
- 首次停止时定时汇报：当前聊天heartbeat自动任务seed-3-9-30已通过automation_update设为PAUSED；旧30-2保持暂停。不补消融、不自动重跑、接续checkpoint、分析、归档、commit或push。以下九次记录保留旧seed0–2批次身份。


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

## 旧seed 0–2批次启动记录

本节命令和run_main_experiment.py固定对应旧seed 0–2九次；不适用于新增21次。新增矩阵已另获授权并由run_seed_extension.py执行，见当前补充批运行约定。

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

## 已采用的表达组件消融

本批三个interest Full被[experiment_3](../experiment_3/README.md)用作同seed参照。另行授权的去B/去D/去R×三seed九次正式LLM已完成，配对分析及过程解释已获用户接受并落地。主批原始结果、模型请求账本和科学配置保持；不把三项消融差值相加为独立贡献，不据此推广到其余制度。

## 补到10个seed的准备与复验（2026-10-22）

用户仅授权三臂seed 3–9配置、输入、运行条件核对及离线验证，消融仍3个seed。新增21配置、28份输入和7份steps位于init，独立清单为init/manifest_seed3_9.json。窗口250帖按原Random(seed+777)，历史17帖按原Random(seed+1777)，类型分层最大余数、组内抽样和最终排序保持。源W11标签池890条中6条按上海时间已进入W12，按既有timestamp历史资格排除后为884条。原池使seed4/8抽中窗口内pid4496并被既有引擎拒绝；修正仅使seed4将4496换为3549、seed8换为3698，其余新历史样本及全部窗口样本不变。旧seed0–2在两种候选池下复算均与冻结posts、次序、全部字段完全一致。原记录、时间戳和旧样本不改，六条排除与逐seed差异在新manifest披露。

人口、行为、词表、行动表、W13五人覆盖和科学机制保持，同seed三臂仅算法不同。新profile共享2310次额外请求上限，仍每行动最多一次额外尝试；独立输出与账本规划在runs/timestamp_v1_seed3_9/，准备时未创建；现由本次启动新建。23100次机会、最多25410次Agent正文外层请求及2310额外额度已纳入本次启动计划；另设新批48小时保护，不复用旧checkpoint或剩余额度。

项目根使用.env解释器执行：

```bash
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
"$PYTHON_PATH" hypothesis_4/experiment_2/init/prepare_seed_extension.py --check
MEM0_TELEMETRY=False ANONYMIZED_TELEMETRY=False LITELLM_LOCAL_MODEL_COST_MAP=True \
  "$PYTHON_PATH" hypothesis_4/experiment_2/verify_seed_extension.py
```

官方experiment-config run固定执行旧config_params.py，故本次直接使用新增生成器，保留旧默认入口。验收用官方validate/check核对旧入口，并以实际ExperimentRunner、StepsConfig和registry逐份检查新增21配置。每窗693批、1100唯一Agent×周机会、11周、250窗口帖+17历史帖、W13悼念22人事件后行动、未来曝光0及feed不超过10均通过；2100份CLI profile实际创建/恢复通过。另复验同批隔离、分臂回流/恢复和共享额度耗尽3项；旧主批33项冻结输入/源码及主批/消融已盘点59项资产保持。全窗无Agent正文生成，不作为科研产量或曲线。

准备时的运行条件核对快照（后续模型决定见下节）：旧请求模型deepseek-v4-1-flash-260910，1818条Agent记录返回标识均为deepseek-v4-1-flash；当前.env默认deepseek-v4.1-flash，同主机ark.cn-beijing.volces.com，当前API路径/api/plan/v3。旧主批未冻结完整API路径及可核对的SDK包版本，不能声称接口、后台与运行库完全相同。当前Python3.13.9、agentsociety2 2.8.4及实际运行库哈希保存在验收JSON；.env未改，本次未联网探测。启动前须明确采用模型标识、确认接口支持情况、复核冻结哈希并记录实际返回标识。拟沿用串行、batch_size=100、4个Ray worker、16并发的原设置；ready_to_launch=false。

本次未改已有代码或正式custom机制，无新增代码patch；新增生成器及验收脚本直接保存。普通模式直接写入实验准备资产，未创建根级run/worktree、未提交或推送。

## 当前模型接口测试与用户决定

用户明确当前模型为deepseek-v4.1-flash-20261017，并接受与旧版本按同一大版本系列用于后续实验；接口测试时仅授权3次探针；后续已明确授权21次正式仿真，见实时进度。当前.env请求别名仍为deepseek-v4.1-flash，未修改。经相同SDK Config/Router、temperature=1.0、timeout=60、num_retries=0、caching=false和非流式调用，实际3次均成功返回deepseek-v4-1-flash-261017。返回后缀261017按命名解读对应用户描述的2026-10-17日期；完整字符串与长写法不同，报告同时保留两者。

3条提示按固定规则选取原seed0随机W13悼念、兴趣W22玩梗、时序W14教育的首位符合条件Agent真实消息，原样发送，未按输出挑选或重抽。总用量3697 tokens；2条原文通过现有有限检查，教育样本触发既有年龄规则并经本地局部修复形成合格候选。无拒答、重试、模型重写或兜底，无环境发布。这些仅证明接口和现有响应/修复路径可用，不将3个样本写成全面生成质量评估，也不声称新旧权重或输出分布经统计检验相同。

实际源路径/哈希、请求消息、旧新正文、返回模型及用量见model_compatibility_probe.json；原离线验收JSON保留为测试前零网络的历史快照，不将本次3次真实请求混记为零。原主批与消融已盘点59项资产仍一致，新增批输出/正式账本未创建；3次测试用量单列，不占正式新增2310次重试额度。模型系列采用条件已由用户决定明确，后续保留新旧日期版本和批次，正式启动时继续核对实际返回标识。现已另获正式启动授权，并启用当前聊天每30分钟汇报，完成或停止后暂停。

## 当前补充批运行约定

用户本次明确授权当前模型seed3–9三臂21次正式LLM仿真及每30分钟汇报，不含消融。新增run_seed_extension.py复用旧控制器的原子记录、进度读取与完成核验，只组织官方CLI，不修改既有代码或custom机制。启动前新增配置/输入再复算一致，105项冻结文件核对通过；控制器两项离线流程检查（失败不续跑、成功按序推进）通过，实际CLI/LLM调用0。准备期manifest和model probe作为历史证据保持，启动授权独立写入新批runtime_plan.json。

新批目前最多2路并行，每路保持batch_size=100、4个Ray worker及16并发设置，共23100次行动机会、额外请求上限2310、正文外层请求上限25410。此前3次接口测试单列；辅助SDK请求如有不得混称正文请求。请求别名和接口从当前.env一次读取冻结，.env不修改；实际返回须为deepseek-v4-1-flash-261017，变化即停批并保留记录。源码/输入在每次run前复核；实际行动/发布失败、引擎失败或新批48小时保护到达均停后续，不自动重跑。文件存在不等于成功，完成时逐run核对引擎693步、环境1100唯一行动/11周及Agent1100唯一决策。

原交接控制器只读状态命令（仅供历史定位；当前恢复后的监督器命令匹配请用下方恢复状态读取）：

```bash
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
"$PYTHON_PATH" hypothesis_4/experiment_2/run_seed_extension_parallel.py --status
```

停止时先核对本批batch_execution.json的supervisor_pid及实际进程命令，再向该监督器发送TERM；它会停止当前引擎及后续21次中的未执行部分，保留已有资料。当前聊天定时器ID为seed-3-9-30，终态报告后通过automation_update暂停；状态未变化也按用户要求报告。旧30-2定时器不启用。未授权commit、push或自动分析。

本批新保护时限：北京时间2026-10-22 23:40:45起，最晚2026-10-24 23:40:45；这是新批保护，不继承旧批授权截止。

## 最多2路并行的交接决定（2026-10-23）

用户明确要求保留当前引擎继续运行，只把监督调度改为最多2路。交接前随机seed3已完成；时序seed3引擎PID78411保持不变，新监督器PID83453已接管它，并启动兴趣seed3作为第二路。旧监督器69988只收到父PID专属STOP/HUP/CONT交接信号，当前引擎不接收交接信号，不重启也不从checkpoint接续。原supervisor.lock、全部输出路径和共享账本沿用，完成顺序可不同，按原manifest填补空位，不新增或重跑条件。

新增控制器直接保存，旧run_seed_extension.py及原105项冻结字节保持，因此没有已有代码patch。5项离线检查通过：已完成/接管条件不重复、父PID专属信号、两路上限与失败联停、共享额度守恒及原截止不顺延；真实CLI/网络/LLM调用均0。交接前串行状态和运行计划只读保存在parallel_control，当前唯一运行状态仍是本批batch_execution.json。

科学配置/输入/模型及每路调用参数保持；原23100次机会、2310次共享额外额度和25410次正文外层请求上界保持。原首次启动时刻不改，原截止仍为北京时间2026-10-24 23:40:45，不从并行接管重新计时。新增引擎显式RAY_ADDRESS=local以隔离两套Ray调度进程，不改变仿真内容。任一路失败、返回模型变更、预算越界或原截止到达均联停两路，保留全部证据，不自动补跑。

30分钟定时器seed-3-9-30已更新为报告active_runs两路、累计完成/21、共享请求与原截止余量；完成或全部引擎明确停止后报告并暂停。状态为stopping且仍有引擎存活时不得提前称停妥。实际交接及两路进度、模型与预算核对见parallel_control/live-check.json。未提交或推送Git。


## 恢复后的只读状态读取

使用项目.env解释器，读取唯一batch_execution.json，并按当前恢复控制器及真实引擎目录核对PID；不调用LLM。完整恢复授权及路径映射在本批recovery_1.json，恢复后实际推进和原始资产保全核对见recovery_live_1.json。旧runtime_plan.json和第一次停止的terminal_check.json保持历史身份。

```bash
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
"$PYTHON_PATH" - <<'PY_STATUS'
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path('hypothesis_4/experiment_2').resolve()))
import run_seed_extension_recovery as c
state = c.read(c.STATE)
state['supervisor_alive'] = c.process_alive(state['supervisor_pid'], str(c.SELF))
for run in state.get('active_runs', []):
    directory = Path(run['run_dir'])
    run['engine_alive'] = c.process_alive(run['child_pid'], str(directory))
    run['actual_progress'] = c.progress(directory)
    run['actual_agent_summary'] = c.agent_summary(directory)
print(json.dumps(state, ensure_ascii=False, indent=2))
PY_STATUS
```

恢复监督器为本次新增文件，旧控制器及科学代码均未改；禁网恢复检查由parallel_control/recovery-check.py保存，证据由recovery_check_1.json记录，接口恢复探针是单独1次实际调用（36tokens），不混记为零网络。所有修改未暂存、未提交或推送。
