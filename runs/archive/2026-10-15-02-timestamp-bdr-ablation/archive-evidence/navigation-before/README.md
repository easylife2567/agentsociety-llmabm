# timestamp方案下的B、D、R正式消融

## 目标与边界

用户于2026-10-15明确要求新开run，按最新timestamp主实验确定B、D、R消融方案，随后授权配置准备、离线验收及正式运行。首次启动遇到路径错误已停止并保全；本次又明确授权修正布局、完整CLI离线验收通过后按原模型及剩余预算重启九次、恢复30分钟汇报；随后授权改为两个实验并行。九次已完成并通过终态验收，监督器和实验引擎均已退出；执行期间采用任一路异常两路联停。用户随后授权在本run内与timestamp同seed Full配对分析、整理图表与证据，明确不新增LLM调用、不落地主项目；本轮遵守该边界，未修改正式Agent、环境、配置或论文。

已按确认方案在interest制度下准备去B、去D、去R，各用seed 0、1、2，共九个候选run；后续完整模型参照复用已完成的3次timestamp-interest。消融指每次只关闭一个指定组件，其余规则保留，以观察整个反馈过程怎样变化。具体定义、固定项、指标与运行门槛见[实验方案](EXPERIMENT.md)。

此前“默认不增加U实验”的安排见[正式最小安排](../../paper/必要实验与结果整理.md)。本批启动依据用户本次直接授权，不继承旧批授权。模型deepseek-v4-1-flash-260910、9900机会、全批额外请求上限990、总外层请求上界10890及48小时总时限已确认，实际授权另记results中的runtime_plan，不改准备期冻结manifest。

## 当前阶段与已验证事实

- **当前阶段：用户已接受并授权采用，正式落地完成。** 正式实验入口为[experiment_3](../../hypothesis_4/experiment_3/README.md)，图表和中英文报告在[正式分析](../../presentation/hypothesis_4/timestamp_bdr_v1/README.md)，综合在[synthesis](../../synthesis/timestamp_bdr_v1/README.md)。九份冻结配置、输入和steps字节保持；九次完成结果独立复制并逐文件核对，首次403及布局/并行证据亦保全。正式工具重新读取主工作区12单元、13200次行动，复算三项主差值及D/R逐周解释，不再依赖本run或workspace。用户确认记录为正式adoption.json，三项claim approved=true；原私有harness和候选分析保持采用前历史，未伪造独立模型审阅或正式validate-synthesis签署。无新LLM调用，不改机制或论文正文，不提交Git，不归档。具体映射、起点和实际验收见[adoption](adoption/README.md)。
- **运行终态（保留记录）：正式LLM运行及终态验收完成，9/9。** 最后去R seed2于北京时间2026-10-16 04:20:38完成，监督器于04:20:48结束。04:47:46逐项核验去B/去D/去R×seed0、1、2：每次均693/693步、1100/1100唯一行动、11/11周、100名Agent；合计6237步、9900次行动。监督器11126及九个引擎真实进程均退出，未发现本run残留实验CLI；8165项源/持久镜像文件哈希及40份冻结文件通过。成功发布2652条、模型请求2657/10890、共享额外5/990；额外全部为既定内容改写，无技术错误、无兜底发布。最后去R seed2发布506条/请求506次；较04:17新增完成最后1次，增加37步、61次行动、28条发布/请求。第二次批次实际用时5小时35分16秒；完成时原48小时已用7小时59分37秒，仍余40小时00分23秒，绝对截止仍为10月17日20:21:11。原模型deepseek-v4-1-flash-260910及九份科学配置保持，未重跑、扩条件或续接checkpoint。定时器b-d-r-30已在确认无残留后暂停；全部原始输出、首次403失败和串行/并行交接记录保留。详细逐run终态、请求总账和进程/镜像核对见[完成验收](results/timestamp_bdr_v1_attempt_02/completion_audit.json)。后续离线配对结果见上项及analysis目录，运行原始证据不覆盖。
- 本次引擎物理输出在隔离`workspace/hypothesis_4/experiment_3/runtime/timestamp_bdr_v1_attempt_02/`，官方CLI查得的custom根为隔离workspace；每10秒同步到[第二次输出](results/timestamp_bdr_v1_attempt_02/README.md)，run结束/停止后逐文件核对哈希。科学配置的字节不变，没有修改SDK或放宽路径安全检查。
- 原48小时绝对截止时刻维持北京时间**2026-10-17 20:21:11**，暂停和修复期间也计入，不顺延48小时。重启时约剩45小时36分，首次失败的模型/额外请求为0，所以全批额外请求仍最多990、总外层请求最多10890。
- 每30分钟汇报定时器`b-d-r-30`已为PAUSED。暂停前核对九次完成、监督器及全部引擎真实退出且无本run残留实验CLI；本批没有自动重跑或追加实验。
- `.env`更换了密钥、API路径（coding/v3→plan/v3）和默认模型（deepseek-v4.1-flash）。本批新进程显式覆盖模型为主批固定版本deepseek-v4-1-flash-260910，不修改.env、不把别名直接视为同版本；交接时的去D进程保留旧API直到完成，其余条件使用交接时读取的新API。新接口现已成功返回原固定版本；后续若不兼容或出现技术异常，仍停止两路，不自动换模型。密钥未保存到证据。
- 调度离线验收通过：合成九条件接管不重复启动、最多两路、按原manifest顺序补位、共享请求求和及额外请求越界拒绝、任一路错误联停；0网络/模型调用。完整CLI入口此前已通过，本次不改命令结构或九份科学配置。最终补丁从本轮准确起点重放与当前源逐字节一致，见[evidence/parallel](evidence/parallel/README.md)。
- 新增完整真实CLI入口禁网验收：原布局反例按预期403；新布局九配置都经过真实main的参数/schema/steps/路径检查与custom注册，再在Ray/模型初始化边界用真实类验证900份profile和九个环境全窗（6237批、9900唯一机会），0网络/LLM调用。明确不把此测试写成真实Ray/LLM完整仿真。镜像、原截止时刻及补丁恢复检查均通过，见[layout-fix](evidence/layout-fix/README.md)。
- 首次失败原样留在[第一次输出](results/timestamp_bdr_v1/README.md)及[startup-failure](evidence/startup-failure/README.md)：20:21:11启动、20:21:13报403、20:21:21停止；原因是引擎从worktree外的输出目录向上找到主项目custom，与隔离WORKSPACE_PATH冲突。它没有Agent行动或模型调用，不计完成，不覆盖或清除。
- 以下离线准备和独立恢复验收仍为配置阶段的历史证据；本次真实启动事实另看第二次runtime_plan、实际引擎与Agent记录。
- 主批为`hypothesis_4/experiment_2/runs/timestamp_v1/`。直接读取九次引擎完成状态和环境保存状态，均为693步、1100条不重复Agent×周行动记录、11周；不是仅依据监督器文字判断。
- 主批实际运行计划登记的33份源码/输入/配置/步骤哈希与当前文件全部一致，三个interest完整模型可以作为候选配对参照。调用模型记录为`deepseek-v4-1-flash-260910`。
- 九份配置分别通过官方schema/check与环境实例化；CLI实际拆分并创建、恢复900份Agent工作区，三个参数的零值均按原值加载。8100组合成快照公式检查、45组固定正文发布/空feed/重复行动/Agent恢复检查通过。
- 九个无Agent生成的全窗调度演练各693批、1100唯一机会、11周、267条外部源入池（17历史+250窗口）、未来曝光0；五人W13覆盖及官方普通推荐保持，环境checkpoint恢复后轨迹一致。26项继承功能测试通过，0失败、0错误、0跳过。
- 独立恢复包已保存；在第二个干净基线worktree只应用恢复包，重新生成和复验均通过，manifest与11项生成输出哈希一致；故意改动冻结源会被生成器拒绝，且输出不变。临时恢复worktree已保全日志后安全解除，原workspace保留。
- 离线验收全过程网络尝试0、真实Provider/LLM调用0。45个固定服务返回及全窗无生成演练仅为功能检查；九次正式LLM均已完成；完整性验收与本轮效果分析分开，配对统计和候选结论见analysis目录。
- 旧B/D/R的100配对seed结果属于anchored_v1数值代理；归档run里的额外U计算也不是本run的正式LLM结果。它们只提供操作定义和待检验预期。
- 主项目机器流水线不改，完成前后SHA256一致；仅在隔离workspace通过官方CLI将`run_experiment`登记为`completed`、verification为`complete`，metadata明确hypothesis_id=4、experiment_id=3、batch_id=timestamp_bdr_v1、attempt=02、completed_runs=9。首次failed快照保留。本轮分析仅使用analysis下私有harness，主项目机器状态仍未改变，没有commit。

## 基线与资产

Git基线为`69d243955d341444ae769fae5bf23dc160465cd6`。开始时已有多项未提交修改及未跟踪资产，详见[核对记录](baseline.json)；这些差异不自动带入后续隔离工作区。与主实验可比性以实际冻结哈希及运行证据为准，不能只凭HEAD判断。

| 本级资产 | 用途 |
|---|---|
| [README.md](README.md) | 唯一实时状态、边界、交接及直接资产索引 |
| [analysis/](analysis/README.md) | 采用前同seed配对候选快照与原始离线核验；当前正式入口见experiment_3 |
| [adoption/](adoption/README.md) | 用户采用授权、主项目起点、文档原状、正式路径映射与落地核验 |
| [EXPERIMENT.md](EXPERIMENT.md) | timestamp单因素消融设计、指标、预算建议和执行验收 |
| [baseline.json](baseline.json) | 起点Git状态、来源哈希、33项匹配及九run完成事实；不包含凭据或帖子正文 |
| [workspace/](workspace/hypothesis_4/experiment_3/README.md) | 基线detached worktree；候选仅新增hypothesis_4/experiment_3，不改已有源码 |
| [recovery/](recovery/README.md) | 独立恢复所需的45份新增文件、来源哈希和应用顺序；无凭据或代码patch |
| [evidence/](evidence/README.md) | 准备起点、依赖版本、最终通过/失败日志和干净恢复复验 |
| [run_ablation.py](run_ablation.py) | 两路调度、运行中引擎接管、逐路实际状态、共享预算和异常联停入口 |
| [parallel-control.patch](parallel-control.patch) | 从布局修正后的控制器起点应用的完整并行补丁，不替换原布局补丁 |
| [check_parallel.py](check_parallel.py) | 两路接管、预算和联停的离线合成验收，不调用Ray或模型 |
| [output-layout.patch](output-layout.patch) | 从首次失败控制器修正输出布局的完整补丁；其结果是并行补丁的准确起点 |
| [check_cli_entry.py](check_cli_entry.py) | 调用真实官方CLI复现旧布局拒绝，并验收九份新布局的禁网工具 |
| [cli_entry_hook/](cli_entry_hook/README.md) | 仅供入口验收的禁网/模型边界测试钩子，实际运行不加载 |
| [results/](results/README.md) | 实际运行授权、监督记录、独立账本映射和首条件失败原始日志 |
| [.gitignore](.gitignore) | 忽略未来隔离workspace及可丢弃tmp |

候选位于[九配置目录](workspace/hypothesis_4/experiment_3/init/configs/README.md)，永久副本位于[恢复包](recovery/overlay/hypothesis_4/experiment_3/init/configs/README.md)。配置恢复不依赖原workspace、其他run或主工作区未提交差异，依赖准确Git对象及记录的SDK/官方技能环境，不包含依赖二进制或Full原始结果。配置阶段未改已有代码；布局修正通过output-layout.patch应用，材料在evidence/layout-fix；本轮并行通过parallel-control.patch应用，其准确起点、最终源和离线验证在evidence/parallel。两个补丁按顺序恢复，不修改原配置恢复包。

配置仅修改100个Agent的一个指定参数，以及两项输入路径和新账本路径。共享额外请求上限990不变；隔离区的账本链接已从首次失败目录改指第二次持久目录，文件按实际重写/重试需要才创建；未复制.env、未改主批账本。历史修复测试输入仅作验收，不作为新消融结果。

复验命令和工具边界见[隔离候选说明](workspace/hypothesis_4/experiment_3/README.md)。官方配置run动作仅执行生成器；完整入口禁网测试和真实LLM运行分开记录，状态只更新隔离区。

状态：用主项目.env指定解释器执行本run `run_ablation.py --status`；停止当前及后续条件执行`--stop`。当前默认仍指向第二次启动，status为completed，completed列出九次终态、active_runs为空；实际引擎目录及持久镜像路径保留在runtime_plan、完成验收和逐run镜像清单。该次batch_execution.json已存在时控制器拒绝重复启动；不能删除记录来重跑。第一次results/timestamp_bdr_v1原样保留，当前为results/timestamp_bdr_v1_attempt_02。

## 待办与下一步

1. 九次运行、最终请求总账、原预算、科学配置冻结和进程退出核验已完成；定时器已暂停，不自动重跑或扩充。
2. 原始隔离输出、持久镜像、失败和交接证据保留，未清理或归档workspace；正式副本已按用户明确授权采用，正式分析不依赖私有路径。
3. 本轮结论及D/R解释已由用户确认并采用；保留n=3、interest单制度、闭环反馈及服务路由可比性限制。不自动追加实验或改写论文；独立模型审阅和机器发布签署未执行，不阻止本次用户直接授权的资产落地。

本次按用户授权新增正式experiment_3、独立原始结果副本、正式配对报告和综合，并定向更新所属导航及论文证据安排。主工作区原有改动保留，未改变正式研究机制或论文正文；无暂存、commit、push或归档。后续进度持续更新本README，不另建tracker/status/handoff文档。
