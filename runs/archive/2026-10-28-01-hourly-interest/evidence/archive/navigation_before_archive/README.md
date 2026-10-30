# 三臂小时回流与兴趣组件消融：隔离实现

## 当前状态与授权

用户于2026-10-28在本run确认三臂统一回流方向，随后明确授权进入代码实现阶段，要求按AGENTS在本run内修改、先不进行仿真。

**当前状态：新增随机/兴趣18/18完成，复用seed0后各10seed；与原完整时序10seed的离线比较、30run官方replay核验、独立DTW复算及均值图均已完成。DTW×100均值±样本SD：随机31.629±4.781、时序28.368±3.313、兴趣24.559±2.506；兴趣7/10次第一，平均排序在去seed0、同实际模型及逐一剔除seed检查中保持。组件消融未动；本轮已选择性正式落地，见下节。**新增批于北京时间2026-10-29 06:08:20完成，全批原始结果保全及--check复算通过。随机累计1702帖、兴趣2185帖；后台检查18已删除，本批监督器及18个引擎均已退出。本run继续保留隔离workspace。新增成功正文均为261017；新增正文请求3508次、额外1次空正文重写已成功。三臂seed0的历史时序参考结果及原pilot资产保持。未启动未授权条件、commit、push、归档或论文修改；主项目机器流水线保持。evidence/final_state.json是代码实现阶段历史记录，pilot/evidence/completion_closeout.json是seed0收尾；本批18次收尾见seed_extension/completion_summary.json及checks/closeout_check.log。

本run只处理新回流方式及其试验，不涉及论文正文。原60份候选manifest继续保持准备期execution_authorized=false；实际运行授权由对应批次单独冻结，不改写历史manifest。本轮仅完成随机/兴趣seed1–9，组件消融及其他条件仍不启动。

## 正式落地与正文评估（2026-10-29）

用户明确要求将本次结果落实主工作区。已选择性采用两份环境机制补丁、新增小时回流测试、experiment_2主配置30份、新随机/兴趣20份完整原始结果与时序10份正式复用矩阵，以及正式分析、图表和综合。未落地experiment_3候选/双实验准备器，未新增仿真或改正文。旧回流结果与旧Full/消融配对继续保留。

正式入口为[experiment_2](../../hypothesis_4/experiment_2/README.md)、[hourly_return_v1分析](../../presentation/hypothesis_4/hourly_return_v1/README.md)及[synthesis](../../synthesis/hourly_return_v1.md)。正式原始和复算不依赖本run或workspace；原始20run共17,932文件逐项复制验SHA，保留run_id、metadata、旧计划/状态/账本字节。正式位置42项回归、30配置/3000profile创建恢复通过；30run官方replay分析、绘图和7产物--check通过，科学数值不变。首份接收清单缺历史时序replay碎片SHA，离线分析据实失败；按原正式relocation清单补齐，原稿与失败日志保留，未重跑模型或改数据。

[落地操作与验收](adoption/README.md)保存基线、最终机制补丁、操作脚本、实际结果和首次失败；本run不归档、不清理workspace或原始镜像。旧恢复包继续对应原候选，新正式路径适配不反写旧恢复材料。

[作者DOCX影响评估](../../presentation/hypothesis_4/hourly_return_v1/manuscript_impact.md)已完成：第五章方法/表4、图4/5及数字需更新，旧组件消融需限定旧回流身份；DTW可补充，但其冻结现实参照与正文49,930条样本口径需说明衔接。本轮仅评估，没有改DOCX、正文或论文图，既有用户差异保持。全局机器analysis仍保留旧E3待分析状态，未冒标全流程完成。

## 三臂各10seed离线分析

用户追加要求将本次随机/兴趣各10seed与原时序10seed比较。已完成[analysis/](analysis/README.md)的离线分析与[中文报告](analysis/report.md)：10个时序的完成、配置、输入、提示来源、实际模型及回流复用审计全部通过；30run均693步、1100唯一行动/决策、100人、11周，原始3000份Agent、33,000次决策、6041次成功发帖与环境/官方replay逐周五类供给及曝光一致。分析--check的7份输出逐字节一致，独立标准库实现复算的最大差为1.07×10⁻¹⁴。原样式三臂均值图和DTW稳定性图的PNG/SVG均已生成，PNG已实际查看，来源哈希与完整对齐路径保留。

DTW沿用上海周W12–W22、五类份额、±1周、按最小累计距离路径长度归一化后×100，先逐run计算再汇总。兴趣均值24.559、时序28.368、随机31.629；兴趣样本SD2.506最小，相对于随机/时序分别8/10个seed更低，三臂第一7/10次。seed1、2随机第一，seed3时序第一，未隐去反例。去掉已观察的seed0及只保留实际模型同为261017的seed3–9，平均排序均保持兴趣＜时序＜随机；10次逐一剔除seed的平均排序也保持，但这些不是额外独立重复，不作显著性或普遍最优结论。

均值图按逐seed成功发帖数等权平均，全窗均值随机170.2、时序215.4、兴趣218.5。晚期W19–W22玩梗作者产量仍为时序45.4高于兴趣40.5、随机2.6，实际玩梗标签曝光份额43.22%/25.59%/3.50%，故DTW拟合优势不等于玩梗传播量最大。时序seed0–2实际返回旧别名，后三臂同版7seed已另列；现实效标与注入样本同源、固定作者类型不等于独立正文分类。分析口径已在analysis/contract.json冻结，没有新增仿真、调参、请求或修改正式资产。历史候选manifest仍保留准备期pending，本分析审计不改写其原状态。

## 随机/兴趣seed1–9并行补齐

用户最新指令为“先通过并行的方案来补齐随机推荐和兴趣推荐的剩余18组seed，注意复用目前的这2组已经跑完的Seed。组件消融实验后续再补，本轮暂时不动”。新增执行资产见[seed_extension/](seed_extension/README.md)。只读核对通过：候选恢复包/科学源码与输入保持，两份seed0各693步、1100唯一行动和决策、11周、100人，正文实际模型均261017，可直接复用；18份候选均为next_batch，每seed两臂除推荐算法外科学配置一致。

本批计划每seed随机→兴趣填补两路，使用独立新状态、锁和账本；新增19,800机会、1,980额外上限、21,780正文外层请求上限及48小时绝对截止。旧pilot账本410次（含撤回时序30次）保持原字节，既不清零也不计为本批新请求；新批不启动seed0、时序或消融。启动前冻结来源、执行预算和实际模型约束，不发接口探针。运行失败保留现场，不自动重试或接续。

实际启动前103项冻结来源、18份官方配置/steps/环境实例与1800份Agent profile创建恢复均通过，网络/LLM/Ray尝试0；12项假进程控制器检查通过，独立限定范围审查无阻塞。真实启动监督器PID15826，首两路随机seed1 PID15838、兴趣seed1 PID15839，完整命令身份与实际SOCIETY_STEP、ENV_STATE行动和100份Agent均已核对，两路均有261017成功正文，见[seed_extension/checks/launch_check.json](seed_extension/checks/launch_check.json)。PID为历史启动记录，实时身份以新控制器--status/--stop核对，不能据旧PID直接操作。

本批原绝对截止为北京时间2026-10-31 00:10:02（UTC 2026-10-30T16:10:02.379083+00:00），未延长或重置；实际于10月29日06:08:20提前完成。后台检查id=18曾按用户要求每30分钟报告完成数、实际步数/行动数、发帖与请求消耗，全批收尾及复算通过后已删除。新增18与复用2分别记录，无条件级重试或resume；旧pilot控制器保留历史，不用于本批。

已完成seed1–9两臂共18项，成功发帖依次181/218、164/220、183/212、171/216、167/227、177/218、164/216、157/224、173/219。每项实际693步、100名Agent、1100唯一决策/环境行动和11周，成功正文均为261017。逐周五类成功posted及实际曝光均与环境和官方replay一致，发布入池集合守恒，未来/同批曝光及延迟队列均0。全批重新核验18项的1854份核心原始SHA、两份复用seed0的210项来源和103项冻结输入均保持；全部完成记录与监督器一致，未修改实际状态。

| 成功发帖范围 | 随机 | 兴趣 | 合计 |
|---|---:|---:|---:|
| 新增seed1–9 | 1537 | 1970 | 3507 |
| 复用seed0 | 165 | 215 | 380 |
| 各10seed合计 | 1702 | 2185 | 3887 |

此表仅记录完成情况及发帖数量；后续多seed效果比较见上节analysis，不据发帖总量直接判断最优。新增正文外层请求3508次、额外1次；含复用seed0的两臂科学结果共3888次，另计撤回时序30次后跨批账面3918次，不等于全部SDK调用或token账单。旧pilot的410次计数保持，未清零或混入新批预算。

必要离线收尾脚本为[seed_extension/closeout_extension.py](seed_extension/closeout_extension.py)，实际运行及相同命令加--check均通过：20行[逐run汇总](seed_extension/completion_runs.csv)、[来源与完整性汇总](seed_extension/completion_summary.json)，以及18份完整原始结果共16140文件的[逐文件来源映射](seed_extension/raw_results_manifest.json)。原始镜像保存在seed_extension/results（Git忽略但不可作为缓存删除），workspace原件继续保留，不只依赖活跃worktree；原始metadata的历史路径未改写。两个seed0继续引用pilot/results。离线收尾未发模型请求或启动引擎。

interest_s7在Agent7/W22出现唯一额外请求：首次generation为空正文、finish_reason=stop，无明确provider refusal；按已冻结规则进行一次rewrite并accepted，最终service_success/published。总2次正文请求，额外1次，符合每行动最多一次额外和共享1980上限。原始决策保留，未发探针或重新运行该条件。

## 三臂DTW对比（历史时序参考）

用户最新要求“三臂一同做对比，并且计算DTW值”。本次仅增加离线分析，原runtime_plan、selected_revision、batch_execution和预算保持原字节，不重跑或接续撤回时序。完整[三臂报告和图件](pilot/agent_supply/three_arm_report.md)比较本次random/interest与正式`timestamp_v1_chronological_s0`；后者100人、1100唯一行动/决策、693步、210帖，科学配置与本pilot对应配置除保护预算/回流声明外一致，107条当前有效时序决策与历史一致。

主DTW对比上海周W12–W22的五类周供给份额与全量现实非噪音构成，±1周受限、多变量欧氏距离、按最小累计代价路径长度归一化后×100。兴趣20.5180、时序27.9168、随机33.2796，兴趣在“接近现实构成”这个目标上最好；晚期玩梗作者产量则时序41帖高于兴趣36帖，不能混为所有目标都最优。历史时序实际返回`deepseek-v4-1-flash`，本次两臂为261017，明确保留版本差异与单seed限制。33行周表、300名Agent原始发布记录、环境及官方replay五类逐周核对，具体来源、方法和路径已冻结在本run；新两臂原分析产物未改。

## 本次随机/兴趣单种子试运行

### 实际观察结果（已完成）

两run分别完成693步、1100条完整唯一环境行动及Agent决策、11周、100Agent，无行动/发布失败，实际正文模型均为deepseek-v4-1-flash-261017。独立核对200份Agent和实际feed、官方replay周表及原始来源哈希通过；未来曝光和同批Agent新帖曝光均0，发布/入池守恒。

| 固定W19–W22指标 | 随机 | 兴趣 |
|---|---:|---:|
| 玩梗型作者成功发帖 | 1 | 36 |
| 同窗全部成功发帖 | 24 | 62 |
| 玩梗型作者供给份额 | 4.17% | 58.06% |
| 实际玩梗标签曝光 | 135/4000＝3.38% | 870/4000＝21.75% |
| 全窗全部成功发帖 | 165 | 215 |

这次seed0中兴趣的晚期玩梗作者供给及标签曝光高于随机；没有时序完整结果参与，不能据此判断三制度最优或跨seed稳定性，也不能将差值全部归因于回流速度。供给按固定作者类型计算，不等于独立正文语义分类。

完整[中文观察报告](pilot/analysis/report.md)、[实际比较图](pilot/analysis/weekly_comparison.png)、周表与逐run来源哈希从[pilot分析入口](pilot/analysis/README.md)进入。输出为22行两臂周表，分析--check确定性复算通过，6项口径测试通过，独立只读结果审查无阻塞；图表已实际查看。时序部分轨迹没有补入结果或分母。

按用户追加要求，另生成[Agent每周发帖量堆叠对比图](pilot/agent_supply/README.md)：沿用之前chart3b的五类作者配色、W13事件线与0–80帖统一纵轴，随机/兴趣并排展示本次seed0。绘图前用原始快照的200份Agent决策逐周逐类核对22行数据，来源哈希一致；PNG/SVG已生成，PNG已实际查看。只新增本run绘图材料，未重跑仿真或修改论文、历史图与原分析产物。

所选两臂正文外层请求380次，另计撤回时序已持久化30次，预算账面累计410次、额外请求0，未越原上界。该计数不等于SDK全部调用或精确token账单。原输出没有删除；2337份原始文件已逐一复制并校验到pilot/results（Git忽略但不可视为缓存），映射和SHA256在pilot/raw_results_manifest.json，恢复数据不只依赖workspace。代码恢复包与实际试运行证据分开保留。

以下为运行范围与交接历史，当前完成结论以上述结果为准。

用户最新指令为“时序臂好像不用跑，能否只跑随机臂、兴趣臂”。当前有效范围以[pilot/selected_revision.json](pilot/selected_revision.json)追加为random/interest各seed0，共2200次完整行动机会；原runtime_plan与parallel_revision保持历史字节。旧时序回流机制未因本次改动改变，本轮不再重跑时序，也不自动将旧时序结果拼入新两臂观察。

实际仅对时序引擎PID85275定向SIGINT停止，停于69步、107条环境行动、30帖和30次已持久化正文请求；原始输出与SHA256见[pilot/scope_handoff/](pilot/scope_handoff/README.md)，标记withdrawn_by_user，不作为完整实验或科学比较。取消时未持久化的在途调用及SDK重试不在这30次中，不能据此声称精确API账单。

随机PID70792未被停止，自然完成693步、1100唯一行动/决策、11周、100份Agent并通过完整验收，共165帖/165次正文请求。新run_selected.py接管并吸收该结果，不重跑随机，仅启动兴趣PID89249；监督器PID89240。接管初核时累计正文195次（含时序30次）、共享额外0，后续用实际状态读取累计值。总请求上界仍不超过原3630/330，不清零账本、不把撤回的额度用于扩矩阵；原北京时间10月29日05:38:46截止保持。

范围控制器9项禁网假进程检查首轮通过，独立只读审查无阻塞。旧两路监督器先暂停以避免时序的有意撤回触发联停，再保存状态并仅HUP/CONT退出旧父、取得原锁。当前查看/停止入口为`pilot/run_selected.py --status`/`--stop`；只等待random/interest完成，excluded_runs保存时序现场与消耗。

分析、绘图和口径测试按保存的[pilot/selected_analysis.patch](pilot/selected_analysis.patch)修改，先保全3脚本起点，git apply --check后应用，并在起点副本独立重放得到相同最终哈希。6项纯离线检查通过；两臂完成后必须显式执行`pilot/analyze_pilot.py --plan pilot/runtime_plan.json --selection pilot/selected_revision.json`及`pilot/plot_pilot.py --analysis-dir pilot/analysis --selection pilot/selected_revision.json`，输出22行周表和两条曲线，撤回时序只计请求，不进入科学结果。后台检查已据此更新并恢复，正常运行时静默。

下列为原三臂授权与首次调度历史，后续范围缩减以本节为准。

用户新指令为“三臂先各跑一个种子做一下测试，观测一下效果”。本次三臂均从头运行seed0，不复用旧时序结果，以当前同一模型条件作探索性比较。规模仍100人、W12–W22、每人每周一次、每次693批和1100行动机会。

原运行授权、三配置、来源哈希、预算、截止与停止条件见[pilot/runtime_plan.json](pilot/runtime_plan.json)，其初始串行计划保持原字节。用户随后明确要求开启并行，当前有效调度由[pilot/parallel_revision.json](pilot/parallel_revision.json)追加为最多2路，仍按random→chronological→interest顺序填空位。请求当前.env模型别名deepseek-v4.1-flash，首个真实正文响应锁定返回版本，后续不一致停批，不额外发接口探针。三run共3300次机会、独立额外请求上限330、正文外层请求上限3630；这些不是全部SDK调用或token费用。原绝对截止仍为北京时间2026-10-29 05:38:46，不延长或重新计时。

启动前3配置官方校验、3环境实例与300份profile创建恢复通过，128项冻结来源保持，网络尝试0；控制器6项假进程检查通过。监督器PID70791，第一路随机引擎PID70792；启动核对时实际100份Agent已创建。PID只用于历史记录，当前进程身份及进度以实际状态和checkpoint核验，不据旧PID操作。

### 两路调度交接

用户“尝试开启并行提高速度”授权只改变墙钟调度，不改变仿真时钟、科学参数或矩阵。新增run_parallel.py复用原统计与完成核验，原run_pilot.py、runtime_plan.json、三份配置及源冻结保持字节不变。共享原账本，不清零请求；原started_at与绝对截止保持。两路各沿用4个Ray worker，未增加Agent行动或改提示。

7项禁网假进程检查通过，覆盖父PID专属信号、接管与两路上限、去重、失败两路联停、PID误伤防护、累计预算及原截止；独立只读审查无阻塞。首轮夹具缺deadline_at导致一项错误，修正夹具后全过，日志保留，未为此改科学代码。只读--check通过后，暂停旧父、保存原状态，再仅对旧父HUP/CONT退出释放锁，新控制器取得同一锁接管原引擎。原随机PID70792保持，新的监督器PID85266、第二路时序PID85275；交接信号未发给引擎。

原始串行状态、计划和实际交接证据见[pilot/parallel_handoff/](pilot/parallel_handoff/README.md)。当前停止/查看入口为`pilot/run_parallel.py --stop`及`--status`，不要用旧串行停止入口。实际active_runs列表由新监督器单写，任一路异常两路联停，不自动重跑。后台检查在交接期间短暂停用后已恢复，并已更新为读取active_runs及新监督器身份。

首批真实正文已返回deepseek-v4-1-flash-261017并锁定。后台检查（automation id：seed0）每15分钟核对实际进展，正常且无新完成条件时静默；只在单臂完成、整批完成、失败或需用户操作时更新。当前检查及分析将按selected_revision只等待random/interest，不等待撤回时序。两臂完成后独立分析、绘图与复算检查，结束自动检查；不自动扩大或重跑。

两臂完成后已生成真实报告和两曲线三面板图，6项口径检查及确定性复算通过。图表来源行数说明曾保留旧三臂33行字样，已通过保存的analysis_metadata.patch修成实际22行，并补全图链接与索引；初版分析完整保存在pilot/evidence/analysis_before_metadata，指标、窗口和原始数据未变。最终selected_analysis.patch仍相对已保存起点汇总，独立重放一致。没有清理原始结果或归档。

本次只把来源候选配置的重试额度/账本改为本pilot独立配置，未改科学参数；所有新生成输出均在本run隔离workspace内。任一路失败、模型不一致、预算越限或超时即停批并保留现场，不自动重跑或接续。实际执行状态由pilot/batch_execution.json记录，本README是唯一人工状态入口。

保留条件完成后独立检查每次693步、1100唯一行动、11周、100Agent各11条有效决策及成功发布正文；再比较周供给/曝光、W19–W22玩梗作者供给及回流时间。当前两臂单seed只作初步观察，不进行显著性检验，不预设兴趣最强；撤回时序只计消耗和保全，不填入比较图或分母。

## 已实现机制

新环境参数`arrival_agent_return_policy`有两种取值：

| 取值 | 含义 |
|---|---|
| `legacy`（缺省） | 保留旧三臂：时序批末回流，随机/兴趣次周回流 |
| `next_batch` | 仅限arrival调度；三臂生成帖统一批末入池，后续行动小时具备推荐资格 |

共同规则是先冻结同小时全部feed，再提交曝光与产出，同小时新帖互不可见。无需增加无行动小时，每人仍每周一次。外部真实帖按发布时间到达、原评分/抽样、生命周期、曝光饱和、W13安排、行为与生成提示均保持。小时回流不意味着每小时重复执行周衰减，也不保证新帖一定被推荐。

机制修改仅涉及隔离工作区的两个既有文件：

- `custom/envs/curation_dynamics_space.py`：解析策略、同源发布反馈、保存恢复；缺字段旧状态按legacy解释，换策略恢复拒绝。
- `custom/envs/curation_arrival_schedule.py`：入池分支读取有效回流规则，复用原时序批末路径及周供给记账。

既有代码先形成mechanism.patch，再git apply --check及git apply；原始起点为下列commit，最终补丁仍仅包含两份源码。新增准备器与测试直接保存最终文件；设计与导航文档在隔离工作区更新。

## 两套新版实验配置

新增标准库准备器为`workspace/hypothesis_4/experiment_2/init/prepare_hourly_return.py`，同时生成experiment_2与experiment_3的`init/hourly_return_v1/`。每份配置显式为next_batch，来源、机制、输出和配对均冻结SHA256；生成及--check拒绝覆盖冲突，不运行旧生成器、不重抽输入。

| 实验/条件 | seed | 准备状态 |
|---|---|---|
| 主实验random Full | 0–9 | 10次planned_new |
| 主实验interest Full | 0–9 | 10次planned_new，同时作为新消融Full |
| 主实验chronological Full | 0–9 | 10次planned_reuse_pending；本次不新增运行预算 |
| 兴趣no_b | 0–9 | 10次planned_new；100人baseline_utility=0，U=RD |
| 兴趣no_d | 0–9 | 10次planned_new；100人spiral_scale=0，D=1 |
| 兴趣no_r | 0–9 | 10次planned_new；100人decay=0，R=1 |

共60份配置，对应50次计划新运行、55,000次行动机会与10次候选复用。三消融从新interest Full逐份复制，只改变指定组件和独立预算字段，Full不重复运行。旧周回流结果和checkpoint不用于中途改规则接续；所有新条件从W12开始。

100人、11周、693批、每次1100机会、同seed人口/输入/行动表、250条外部样本及17条历史池、W13五人共同顺延、最多10槽、原指标窗口均保持。新主批与消融分别使用独立未创建账本，额外请求配置准备上界2200与3300，沿用10%和每行动最多一次额外的既有约定；不混用旧批990/2310的不同上界。

准备阶段已离线验证时序新旧策略的固定输入逐批行为一致，当时10次时序结果尚待核对，原manifest因此保留pending。本轮追加离线分析已完成10次实际结果的复用审计，结论与模型分层见上文analysis；不回写准备期历史manifest，不据此自动正式落地。

## 验证与实际结果

| 证据 | 实际结果 |
|---|---|
| evidence/hourly-tests-attempt1.log | 7项新增测试首轮通过；三臂回流、同批隔离、恢复、跨周与末批供给守恒、完整时序新旧行为等价 |
| evidence/regression_attempt2.json及.log | 新旧共42项测试通过，0失败/错误/跳过，网络尝试0 |
| evidence/config_validation.json及.log | 18项汇总检查通过；60份官方schema/steps与环境实例化、6代表条件共600份CLI profile创建恢复、6份环境策略保存恢复通过 |
| evidence/recovery_structure.json及.log | 在独立干净导出中检查并应用补丁，恢复76份镜像，78份候选文件哈希全部一致 |
| evidence/recovery_tests.json及.log | 独立恢复后42项再次通过，无失败/错误/跳过，网络尝试0 |
| evidence/recovery_config_validation.json及.log | 独立恢复后60配置与600profile再次通过，实际模块来自恢复目录custom |
| evidence/review.md | 独立只读审查无实质阻塞问题 |

所有检查均未启动社会引擎、Ray或真实LLM，也未生成新实验轨迹。环境方法使用固定测试正文的功能演练只验证机制执行，不是仿真结果。

首轮广义回归35项有6项环境错误：干净worktree缺少旧测试所需tmp目录/被忽略历史样本，且SDK的WORKSPACE_PATH仍指向主目录。verify_tests.py在进程内配置正确工作区、创建测试tmp并恢复最小历史夹具后，42项全部通过；未为此修改既有测试或机制。初次日志和JSON保留。第一次独立恢复因Git基线技能为本机绝对链接，被安全解包拒绝；改为冻结两项必需技能实体及校验和，第二个新目录恢复通过，未绕过安全检查。失败说明见evidence/recovery_attempt1.log。

## 基线、独立恢复与复验

- 基线commit：`aad3267fc9929a08a453ba427bdf25919bbffc70`，无前置代码改动；开始时主项目状态和322项保护文件哈希见baseline.json。
- 运行时：Python 3.13.9、AgentSociety2 2.8.4；本机解释器为`/Users/easylife/Project/AgentSociety/AgentSociety2/.venv/bin/python`。SDK仓库commit为`13e28b5e67a2a8f2f43d640ebf27859126da622e`，开始时干净。
- recovery_manifest.json记录基线导出路径、补丁与全部候选哈希、依赖和21份必要验收技能哈希。恢复不依赖原workspace或主项目未提交修改；已有Git基线对象及同版本已安装运行时是前提，不联网安装。
- files/含76份新增实现/配置及修改后设计文档；mechanism.patch含两份既有源码改动。没有删除或重命名正式资产。
- fixtures/只含既有回归所需的一条历史生成文本及提取来源，不包含Agent配置或凭据，不是新实验输入。
- validation_skills/保存验收必需的两个技能实体，避免恢复依赖原机绝对链接；未安装新技能。Ponytail本地技能已读；本地未找到Karpathy Guidelines，参考其[项目维护者公开原文](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md)，不将其视为已安装技能或科学证据。

从项目根使用已配置解释器复验隔离候选：

```bash
TASK_RUN=runs/2026-10-28-01-hourly-interest
TASK_WS="$TASK_RUN/workspace"
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
"$PYTHON_PATH" "$TASK_WS/hypothesis_4/experiment_2/init/prepare_hourly_return.py" --check
"$PYTHON_PATH" "$TASK_RUN/verify_tests.py" --workspace "$TASK_WS" --output "$TASK_RUN/evidence/recheck_tests.json"
"$PYTHON_PATH" "$TASK_RUN/verify_candidate.py" --workspace "$TASK_WS" --output "$TASK_RUN/evidence/recheck_configs.json"
```

独立恢复到一个尚不存在的目录，再用上述两验证器指定该目录：

```bash
"$PYTHON_PATH" "$TASK_RUN/restore_candidate.py" --repo . --destination "$TASK_RUN/tmp/recheck_clean" --output "$TASK_RUN/evidence/recheck_restore.json"
```

恢复顺序为Git基线导出→补丁check/apply→复制files与冻结技能→逐文件哈希校验→运行配置--check及两验证器。已实际核验目录为tmp/recovered_v2，首次部分导出tmp/recovered保留作为失败现场。重要证据已在evidence，不只放tmp。

## 本级资产

| 资产 | 用途 |
|---|---|
| [README.md](README.md) | 唯一实时状态、实施范围和恢复交接 |
| [.gitignore](.gitignore) | 忽略workspace/tmp及pilot、seed_extension原始镜像；原始镜像不可视为缓存删除 |
| [baseline.json](baseline.json) | 主工作区起始状态、准确基线与保护哈希 |
| [mechanism.patch](mechanism.patch) | 两份既有环境源码的最终补丁 |
| [recovery_manifest.json](recovery_manifest.json) | 最终文件清单、哈希和恢复依赖 |
| [files/](files/) | 76份候选文件的独立镜像 |
| [fixtures/](fixtures/README.md) | 既有回归的最小历史输入及来源 |
| [validation_skills/](validation_skills/) | 两项验收必需技能的实体冻结文件 |
| [verify_tests.py](verify_tests.py) | 禁网运行42项新旧功能检查 |
| [verify_candidate.py](verify_candidate.py) | 官方配置/模块/profile禁网验收 |
| [restore_candidate.py](restore_candidate.py) | 从基线与恢复材料重建干净候选 |
| [evidence/](evidence/README.md) | 实际验收、失败与恢复证据 |
| [pilot/](pilot/README.md) | 本次授权的三臂seed0配置、运行控制与后续观察产物 |
| [seed_extension/](seed_extension/README.md) | 新授权随机/兴趣seed1–9共18次两路补齐，复用两份seed0且不运行消融 |
| [analysis/](analysis/README.md) | 当前新随机/兴趣与历史时序各10seed的原始核验、均值图、DTW与重复稳定性比较 |
| [adoption/](adoption/README.md) | 正式落地基线、补丁、选择性接收、正式位置验收及交付记录 |
| workspace/ | 保留原探索工作区及证据；选定主实验成果已正式落地，正式复算不依赖本目录 |
| tmp/ | 恢复验证导出与可丢弃中间文件，失败现场暂保留 |

## 后续边界

代码实现、两臂seed0、随机/兴趣seed1–9及本轮选择性正式落地均已完成，两个自动检查已删除。组件消融、更多条件、正文实际修改及commit/push仍未授权，不自动继续仿真。主项目机器阶段保持，不干预论文、不提交或归档；原代码恢复包继续对应已验收候选，pilot与seed_extension原始结果、验证和汇总分别保留。实际完成状态仍由各监督器原始文件单写保全。
