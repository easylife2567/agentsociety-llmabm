# Experiment 3：timestamp-interest的B、D、R消融


## seed3–9全部完成并通过完整性验收（2026-10-26）

**当前状态：新增21次B/D/R消融已于北京时间2026-10-26 02:07:28全部完成，21/21逐次完整性复核通过，活动路数0/2，监督器及全部匹配引擎已退出。**加上原seed0–2九次，B/D/R各10seed的运行数据已补齐；同seed Full继续复用主实验，没有新增Full运行。这里只做运行完整性和预算核验，尚未对补齐数据开展结果分析，旧九次分析结论未自动更新。

- 按实际completed.run_dir和recovery_3.runs逐一重验：每次693步、1100完整唯一环境Agent×周行动、11周、100份Agent及1100完整唯一无失败决策，发布正文/ID/预期返回模型均通过，最终service_failures、posted_model_failures和action_failures均0。共2100份Agent、23,100条完整唯一决策/环境行动，保存[completion_check_recovery_3.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/completion_check_recovery_3.json)。
- 21次有效结果共发布6,206帖、正文请求6,214次；另保留旧去B seed7失败62次正文（61帖，不计最终完整结果），因此总正文账本为6,276/25,410次。共享额外为9/2,310次，预算均未越界，也未重复累计接续前旧目录。SDK辅助调用/内部重试不在正文账本中，不能把上述数值当全部API请求量。
- 准备探针2次/90tokens，三次恢复探针分别1次/51、65、37tokens单列，不计正文预算。成功发布记录的真实返回模型均为deepseek-v4-1-flash-261017，请求别名deepseek-v4.1-flash；按用户确认新旧版本在本研究中等价处理，准确标识和旧批260910来源保留。
- 从原首次启动北京时间10月24日16:34:46到完成耗时33小时32分42秒（含停机），早于原截止10月26日16:34:46约14小时27分18秒，48小时起点及截止从未重置。最后去R seed9达到693步、1100完整唯一行动/决策、11周，发布530帖/530次正文。
- 148项冻结文件、19,381项既有完成及历次失败证据均核验保持；本次21个实际完成目录的19,063项来源哈希另存完批检查。所有旧失败、terminal_check、stopped_execution和原始日志保留，未覆盖或清理。实际完成时间以原batch_execution.finished_at为准，完批检查checked_at记录本次复核时间。
- 官方CLI已登记run_experiment completed、verification complete，metadata明确hypothesis_id=4、experiment_id=3、batch_id=timestamp_bdr_v1_seed3_9，回执[completion_registration_recovery_3.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/completion_registration_recovery_3.json)。30分钟定时任务b-d-r-seed3-9-30已结束并删除，配置快照[automation_before_completion_recovery_3.toml](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/automation_before_completion_recovery_3.toml)保留。未分析、归档、commit、push或开启其他实验。

## 第三次恢复启动记录（2026-10-26，历史）

**恢复时记录：北京时间2026-10-26 00:10:03按用户明确授权恢复，保留16次完成和全部失败现场，最多两路补完剩余5次。**原绝对截止仍为当天16:34:46（runtime_plan精确时间不变），未延长或重新计时。授权、实际目录和来源冻结见[recovery_3.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_3.json)，最终执行状态为[batch_execution.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/batch_execution.json)。

- 去D seed8从249步、去R seed8从174步完整复制接续，实际目录分别为timestamp_bdr_v1_interest_no_d_s8_resume1、timestamp_bdr_v1_interest_no_r_s8_resume1。两份原检查点均未修改：396/274条环境行动与完整唯一决策相等，183/112条发布均有对应环境记录，无待补发布或失败决策；无须像上次去R seed6那样重建待提交状态，也不重新生成已完成正文。
- [recovery_3_offline_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_3_offline_check.json)通过16次完整结果重验、200Agent实际恢复、四组随机状态与环境保存恢复一致、冻结行动表前缀矩阵和发布对应检查；148项冻结文件、19,381项先前完成/失败证据核验保持。0网络/LLM、0真实引擎/Ray。六种假进程调度检查见[recovery_3_controller_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_3_controller_check.json)。首轮仅测试夹具仍指旧脚本名而断言失败，已修正并保留attempt1报告/日志和验收器快照，未改冻结配置或机制。
- 本次最小接口确认1次/37tokens成功，实际返回deepseek-v4-1-flash-261017；准备2次/90tokens及前两次恢复各1次/51、65tokens继续单列。原请求别名deepseek-v4.1-flash及用户确认的研究版本等价处理保持。SDK辅助调用/内部重试不在正文账本中，不把正文数称全部API请求数。
- 本次从正文4,876次、共享额外8次继续；两个副本已累计183/112次，不重复加原目录295次。旧去B seed7失败62次仍单列计入总正文预算，旧失败61帖不计最终完整条件。总上限25,410、共享额外上限2,310及原账本保持；16次完成结果（包括各历史接续实际目录）只保留不重跑，之后按seed9 no_b→no_d→no_r补三次，不重跑Full。
- 新入口[run_seed_extension_recovery_3.py](run_seed_extension_recovery_3.py)，验收器[verify_seed_extension_recovery_3.py](verify_seed_extension_recovery_3.py)，复用已修复的最终服务失败/缺有效模型检测；再次失败即联停，不自动再次恢复。监督器PID92491；只读--status、按本批PID停止--stop均用新入口。各运行新日志为recovery3-engine.log/recovery3-stderr.log，监督器日志为控制目录recovery3-supervisor.log，旧复制日志只作历史证据。
- 00:11启动核对时仍16/21完成，两路已超过原中断步数（去D260/693、去R186/693），服务/行动/模型失败计数均0，证据[recovery_3_launch_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_3_launch_check.json)。旧停止状态原字节另存[stopped_execution_3.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/stopped_execution_3.json)，所有历史terminal_check与失败现场不覆盖。
- 恢复时每30分钟任务b-d-r-seed3-9-30为ACTIVE，官方CLI为run_experiment in_progress；完批后的当前登记和定时任务结束情况见上节，未分析、归档、commit或push。

## 周额度耗尽停止记录（2026-10-25，历史）

**当时状态：北京时间2026-10-25 00:16:49已自动完全联停，16/21完成、2次中断、3次未启动，活动路数0/2。**两路环境路由收到服务weekly usage quota耗尽的RateLimitError；新监督器按冻结服务失败检测自动联停，无需人工补发停止。监督器77433及引擎85173、86134均已退出。日志“Interrupted by user”是收到监督器信号的通用文字，不是用户手动取消；pid.json保留历史running字段，不代表进程仍活着。

- 16次完成为seed3–7全部B/D/R及seed8去B，已按实际completed.run_dir逐一复核693步、1100完整唯一环境行动、11周、100Agent/1100完整唯一无失败决策、正文/ID/模型；最终service_failures和posted_model_failures均为0。去R seed7为本次新增完成，532帖/532次正文。
- 去D seed8停在W15、249/693步、396/1100唯一环境行动、3/11周汇总、183帖/183次正文；去R seed8停在W14、174/693步、274/1100唯一环境行动、2/11周汇总、112帖/112次正文。两路Agent决策与环境行动集合一致，无最终正文服务/发布/模型失败记录；本次故障发生于SDK环境路由辅助调用，不以正文计数代替辅助调用用量。seed9去B/去D/去R三次均未启动。
- 累计正文4,876/25,410次，含旧去B seed7失败62次；当前完成及中断条件已发布4,807帖，旧失败61帖另列不计最终完整条件。共享额外8/2,310次，账本不重置；准备探针2次/90tokens、首次恢复1次/51tokens、本次恢复1次/65tokens单列。SDK辅助请求/内部重试不含在正文账本内，服务周额度耗尽不是实验正文预算耗尽。
- 停止时从原首次启动起耗时7小时42分03秒，原48小时保护剩40小时17分57秒；原截止仍为北京时间2026-10-26 16:34:46。错误日志声称周额度在北京时间10月26日00:00恢复，仅为服务返回信息，未探针验证，不自动等待启动、重试或接续。成功正文实际返回deepseek-v4-1-flash-261017，按用户已确认的研究等价版本处理并保留准确标识。
- 新终态证据[terminal_check_recovery_2.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/terminal_check_recovery_2.json)保留本次矩阵、实际PID退出、日志来源及哈希；148项冻结文件、13,444项先前完成/失败证据保持。官方CLI已登记run_experiment failed、verification partial，metadata明确H4/E3/本批及16/21验收范围，回执[terminal_registration_recovery_2.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/terminal_registration_recovery_2.json)。既有terminal_check、stopped_execution及全部原始失败目录不覆盖。定时任务b-d-r-seed3-9-30已结束并删除，配置快照[automation_before_terminal_recovery_2.toml](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/automation_before_terminal_recovery_2.toml)保留。未改配置/模型/凭据，未分析、归档、commit或push。

## 第二次恢复启动记录（2026-10-24，历史）

**恢复时记录：北京时间2026-10-24 22:28:21按用户明确授权启动，最多两路，原11次完成及全部失败现场保留，暂不分析。**去R seed6在副本补齐待提交的成功原帖后接续，去B seed7独立重跑，随后补其余八次；原科学配置、模型、总预算、共享账本和48小时原截止均保持。授权与实际路径见[recovery_2.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_2.json)，实时状态仍为[batch_execution.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/batch_execution.json)。

- 失败检测已在新恢复入口[run_seed_extension_recovery_2.py](run_seed_extension_recovery_2.py)补齐：最终generation_status=service_failed或已发布正文没有预期真实response_model即联停，不再仅依赖reason=published；成功有限重试保留的generation_error不误报。监督器按脚本名和明确参数匹配PID，已修正绝对/相对路径误报；旧调度器作为历史冻结来源不改动。当前监督器PID77433，只读`--status`和停止`--stop`均使用该新入口。
- 去R seed6的原_resume1检查点保留。准备副本[recovery_2_checkpoint/](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_2_checkpoint/)仅改变ENV_STATE.json的_pending_agent_posts、_posted_this_step、_spoke_this_tick、_next_post_id，恢复Agent95/W21已成功的694号帖待提交记录；原正文/ID、Agent29/95已有决策、602步时钟、随机状态保持，无正文重新生成。实际接续目录为timestamp_bdr_v1_interest_no_r_s6_resume2。正式启动后已确认694号帖仅提交一次、Agent95该周仍唯一，未丢帖或重复请求。
- 去B seed7在timestamp_bdr_v1_interest_no_b_s7_retry1从头运行；旧失败目录的61帖/62次正文作为discarded_attempts保留，62次仍计入正文总预算，旧61帖不计最终完整条件。原R的465次已在_resume2累计，不再加_resume1或最早208次。新启动基线仍正文3,529次、共享额外7次；上限仍25,410/2,310，不归零。
- [recovery_2_offline_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_2_offline_check.json)通过：11次结果重验、100Agent恢复、修复副本仅一文件/四字段差异、两次内存单批重放一致，0网络/LLM、0真实引擎/Ray；13,444项原完成/失败证据及148项冻结文件哈希核验保持。[recovery_2_controller_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_2_controller_check.json)覆盖成功补位、服务失败兜底、缺模型返回、额度错误、正文越界及原截止六种假进程情形。
- 本次短接口探针1次/65tokens成功，实际模型deepseek-v4-1-flash-261017；准备2次/90tokens、第一次恢复1次/51tokens分别单列，均不计正文账本。新旧模型按用户确认在本研究等价处理，保留实际标识。SDK辅助请求/内部重试不在正文账本内。
- 22:30启动核对时仍11/21完成、活动2/2：去R seed6为622/693步、去B seed7为30/693步，最终服务/行动/模型失败计数均0，实际模型正确，证据[recovery_2_launch_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_2_launch_check.json)。原首次启动北京时间10月24日16:34:46、绝对截止10月26日16:34:46不变；后续顺序仍seed7去D/去R、seed8–9全部B/D/R，不重跑Full。
- 旧停止状态原字节另存[stopped_execution_2.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/stopped_execution_2.json)；既有两次terminal_check及所有原始失败目录保持。启动时30分钟任务b-d-r-seed3-9-30为ACTIVE，官方CLI为run_experiment in_progress；再次停止后的当前状态见上节，不自行再试，未分析、归档、commit或push。

## 第二次停止记录（2026-10-24，历史）

**第二次停止时状态：北京时间2026-10-24 22:01:04已完全停止，11/21完成、2次中断、8次未启动，活动路数0/2。**去B seed7的Agent19/W12连续两次正文请求Timeout，冻结的有限重试用尽后发布了保守兜底文本（content_origin=fallback、generation_status=service_failed），没有真实response_model，因此不能通过既定完整性验收。该次没有新的额度耗尽记录；不能把兜底正文当成模型成功返回，也不补写模型标识。监督器检查行动/发布失败和部分日志错误，未自动捕获该published+service_failed情形，监控发现后按再次失败联停规则请求停止；监督器71703及两路引擎71716/72024均已退出。

- 11次完整结果已逐一重验693步、1100完整唯一环境行动、11周、100Agent/1100完整唯一无失败决策、发布正文/ID/返回模型；原seed3–5全部、seed6去B/去D保留。去D seed6副本已完成，证明本次安全接续核查通过的该条件最终验收通过。
- 两份中断现场：去R seed6副本停在W21、602/693步、951/1100唯一环境行动、9/11周汇总，Agent953份决策、463帖/465次正文；去B seed7停在W19、483/693步、763/1100唯一环境行动、7/11周汇总，Agent763份决策、61帖/62次正文，其中1帖为无模型返回的兜底。去R另有Agent65/W17一次Timeout，冻结范围内第二次请求成功；不把它写成完整行动失败。
- 未启动八次：seed7去D/去R，seed8–9全部B/D/R。累计正文3,529/25,410次、成功发布3,522帖（含上述1条兜底）、独立共享额外7/2,310次；SDK辅助调用/内部重试不含在正文账本内。准备探针2次/90tokens、恢复探针1次/51tokens单列；原接续前470次未重复相加。
- 停止时从原首次启动起耗时5小时26分19秒，原48小时保护剩42小时33分41秒；原截止北京时间10月26日16:34:46不变。科学配置、模型、凭据、冻结文件未改；148项冻结文件及原完成/失败现场2,714项哈希复核保持。
- 新证据：[terminal_check_recovery_1.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/terminal_check_recovery_1.json)；官方CLI已登记run_experiment failed、verification partial，metadata明确H4/E3/本批及11/21验收范围。回执见[terminal_registration_recovery_1.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/terminal_registration_recovery_1.json)。第一次terminal_check.json及所有原始现场保留，不覆盖。定时监控已结束并删除b-d-r-30，停止前配置保存在[automation_before_terminal_recovery_1.toml](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/automation_before_terminal_recovery_1.toml)。不自动再试或接续，未分析、归档、commit或push。

## 本次获授权恢复记录（2026-10-24，历史）

**恢复时记录：北京时间2026-10-24 21:27:50恢复，最多两路并行，暂不分析。**用户明确授权在核查安全性后继续剩余消融；保留原10次完成、两份失败现场及第一次停止证据。恢复授权、实际运行目录与计费口径见[recovery_1.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_1.json)，实时进度仍以本批[batch_execution.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/batch_execution.json)为准。

- 安全核查：[recovery_1_offline_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_1_offline_check.json)禁网通过，恢复200个真实Agent及两份环境的快照/随机状态，重验原10次完整结果。去R seed6的469条环境行动与决策一致；去D seed6领先环境的Agent25/W22为已完成的沉默决策，没有正文请求或发布副作用，实际step已验证直接跳过且不新增决策。原674/297步检查点都可安全复制接续，无需从头重试或编辑检查点。
- 去D、去R seed6分别完整复制到同根目录下的`timestamp_bdr_v1_interest_no_d_s6_resume1`、`timestamp_bdr_v1_interest_no_r_s6_resume1`，在副本使用官方CLI `--resume`。原目录只读保留，接续前262/208次正文已在副本累计，不再加原目录470次；随后按manifest补seed7–9九次。停止状态原字节保存在[stopped_execution_1.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/stopped_execution_1.json)。
- 21:30恢复核对时已11/21完成：去D seed6接续后已达到693步、1100唯一环境行动、11周、100Agent/1100完整唯一无失败决策，264帖/264次正文。活动两路已为去R seed6和去B seed7；启动/推进证据见[recovery_1_launch_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/recovery_1_launch_check.json)。原完成及失败现场2,714项哈希、148项冻结文件核验未变。
- 恢复前短探针1次/51tokens成功，实际模型deepseek-v4-1-flash-261017，准备探针2次/90tokens另列，均不占正文预算。原独立共享账本从4继续、正文从3,208累计；总上限25,410及共享额外上限2,310均不变。原首次启动北京时间10月24日16:34:46及绝对截止10月26日16:34:46不重置；同seed Full只复用，不重跑。
- 接续调度器[run_seed_extension_recovery.py](run_seed_extension_recovery.py)及核查工具[verify_seed_extension_recovery.py](verify_seed_extension_recovery.py)复用既有检查/预算函数，未改冻结科学代码、配置、输入或模型凭据。假进程验收覆盖成功补位、额度失败联停、正文越界、原截止，0真实引擎/LLM调用；后续再次失败即联停，不推定本次授权允许再试。
- 新监督器PID71703。只读用新调度器`--status`并实际ps核对PID/命令：启动命令使用相对脚本路径，`supervisor_alive`因按绝对脚本路径匹配会误报false，须以ps中的`run_seed_extension_recovery.py --continue-authorized`确认，不能据该字段认定退出。异常时先核对实际PID再停止本批，不全局停止Ray。新日志为各引擎的recovery-engine.log/recovery-stderr.log及控制目录recovery-supervisor.log，旧失败日志不再扫描为新错误。
- 恢复时定时器b-d-r-30为ACTIVE，官方CLI的run_experiment为in_progress；再次停止后的当前状态见上节，未做分析、归档、commit或push。

## 第一次停止记录（2026-10-24，历史）

**第一次停止时状态：北京时间2026-10-24 21:06:52已完全停止；新增21次中10次完成、2次中断、9次未启动，实际活动路数0/2。**约21:04两路环境路由出现服务5小时额度耗尽的RateLimitError，SDK辅助请求正在内部退避，监督器未自动联停；当次监控按冻结的服务异常即联停规则调用本批`--stop`。原始状态中的“收到停止请求”来自该监控操作，不是用户手动取消。监督器37735及引擎65060、67321均已退出；保留pid.json中的历史running字段，以实际进程核对为准。

- 完成的10次为seed3–5全部B/D/R及seed6去B，逐次复核均为693步、1100完整唯一环境行动、11周、100份Agent及1100完整唯一无失败决策，发布正文、ID和返回模型检查通过。
- 中断现场：去D seed6停在W22、674/693步、1066/1100环境行动、10/11周汇总、262帖/262次正文；Agent已有1067份决策，比环境落盘多1，不能视为完整同步checkpoint。去R seed6停在W16、297/693步、469/1100环境行动、4/11周汇总、208帖/208次正文。seed7–9全部九次未启动。
- 本批累计正文3,208/25,410次、成功发布3,204帖、独立共享额外4/2,310次；准备探针2次/90tokens另列。SDK辅助调用和内部重试不在正文账本中，服务额度耗尽不是本批正文预算耗尽。已发布正文实际模型均为deepseek-v4-1-flash-261017，按用户确认在本研究中与旧版等价处理并保留标识。
- 从首次启动至停止耗时4小时32分07秒，原48小时保护尚余43小时27分53秒；截止仍为北京时间2026-10-26 16:34:46。错误日志声称服务额度21:18:57恢复，仅为服务返回信息，未探针验证、不自动恢复或重跑。
- 新停止证据为[terminal_check.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/terminal_check.json)：148项冻结文件及11,637项旧资产核验保持。官方CLI已登记run_experiment为failed、verification partial，明确本批H4/E3及10/21验收范围；[terminal_registration.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/terminal_registration.json)记录定时器b-d-r-30已PAUSED。原始日志、状态、输入与历史证据未覆盖；未分析、未归档、未commit或push。

### 正式启动时记录（历史）

**启动记录：北京时间2026-10-24 16:34:46正式启动21次兴趣制度B/D/R消融，最多两路并行；本次48小时绝对截止为北京时间2026-10-26 16:34:46。**用户已明确启动授权，实际授权与冻结时限见[runtime_plan.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/runtime_plan.json)，唯一当前执行状态为本批[batch_execution.json](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/batch_execution.json)。准备manifest和preparation_plan仍保留当时execution_authorized=false，不改写历史证据。

- 首两路为seed3去B、去D。监督器PID37735；已核对实际命令、两路独立引擎、checkpoint、环境行动及Agent记录确实推进，实际正文返回deepseek-v4-1-flash-261017，无启动期行动/发布失败；一次性启动核对在checks/seed3_9_launch_check.json。
- 新批正文累计上限25,410、共享额外上限2,310，独立账本启动前为0；旧9次账本5及Full不改动。准备期探针2次/90tokens单列。SDK辅助请求与内部重试不在正文账本内。
- 按seed3→9、每seed no_b→no_d→no_r填补空位，完成顺序可不同。任一路技术失败、行动/发布失败、模型变化、额度或截止到达即联停，不自动重跑或接续checkpoint，交接/停机不重置截止。
- 启动时定时器b-d-r-30为ACTIVE并绑定当前聊天；停止核验后已PAUSED，当前状态见上节。旧9次记录不混入本次21次进度或账本。
- 本轮只运行与完整性核验，不开展曲线、配对效应、显著性或机制分析，不自动归档、commit或push。

控制入口：[run_seed_extension.py](run_seed_extension.py)；只读核对用`--status`，停止本批用`--stop`，禁止重复`--start-authorized`。新调度器通过3类禁网假进程检查（成功补位、失败联停、额度越界），0真实子进程/LLM；当前版本检查见[seed3_9_controller_check.json](checks/seed3_9_controller_check.json)。

## seed3–9准备验收记录（2026-10-24，保留）

**准备阶段快照：21份配置、离线验收和最小接口测试完成时，正式仿真尚未启动，execution_authorized=false。**此前准备请求仅覆盖准备与测试；后续正式启动授权见上节。新增兴趣制度no_b/no_d/no_r各7次，复用同seed Full；seed6明确配对timestamp_v1_interest_s6_resume1。完成未来21次后，Full/no_b/no_d/no_r可各10seed配对；本次没有重跑Full或改动旧9次消融。

- 配置及配对：[init/manifest_seed3_9.json](init/manifest_seed3_9.json)，21次按seed3→9、每seed no_b→no_d→no_r补空位，最多两路沿用原规则。
- 独立账本：[execution_records/seed3_9/](runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/README.md)下_extra_attempts.count已以独占创建方式初始化为0；旧账本5保持。新增23,100次机会、共享额外正文请求上限2,310、正文累计上限25,410。SDK辅助请求不在正文账本内。
- 48小时保护：从未来首次正式启动时一次性冻结起点及截止；当前started_at/deadline_at均为空，不从准备或接口测试计时，交接/停机不重置。预算与截止边界工具为[seed_extension_guard.py](seed_extension_guard.py)。异常联停，不自动重跑或接续checkpoint。
- 模型沿用当前deepseek-v4.1-flash，实际测试返回deepseek-v4-1-flash-261017；按用户确认新旧版本在本研究中视为等价，准确标识保留溯源。生成温度1、timeout60、num_retries=0、caching=false等正文参数保持。
- 离线验收：[checks/seed3_9_offline_verification.json](checks/seed3_9_offline_verification.json)通过21份官方配置检查、2,100份真实CLI profile创建/恢复、7个Full完整性与11,637项旧资产保全；禁网验收0网络/LLM尝试、0 Agent行动/环境步进，未启动Ray或引擎。首次验收器起点误写已修正并保留首轮记录；诊断导入的SDK远程价格表读取超时另有披露，后续固定本地价格表。
- 最小接口测试共2次、90tokens，均单列不占正文预算：首个8-token探针被推理占满而正文截断；保留原记录后只修正探针上限，再次返回OK并通过。见[修正探针](checks/model_probe_seed3_9_token_cap_correction.json)，不是服务失败重跑，更不是仿真。

主要指标仍为B：W19–W22全体每周成功发帖数；D：W19–W22玩梗型Agent发言率；R：W14–W18全体发言率。比较保持消融−同seed Full，speak与posted分开，保留所有机会分母。该扩充只检验兴趣制度内B/D/R，不能拆分时序排序与更快入池。

以下为已采用seed0–2九次结果与历史落地说明；本次仅补齐运行数据并验收，尚未分析新增种子，其统计结论没有自动更新。


用户于2026-10-16明确接受九次正式LLM消融、同seed配对结果及D/R过程解释，并授权落实主工作区。本目录是已采用成果的实时交接入口；来源探索run已按用户2026-10-18明确指令归档，见[归档记录](../../runs/archive/2026-10-15-02-timestamp-bdr-ablation/README.md)。本次落地不新增LLM调用、不改行为机制、不改主实验或论文正文、不提交Git。

九次消融已全部完成：每次693步、100人×11周=1100次机会；合计2652条成功发布、2657次模型请求、额外5次内容重写。主模型请求标识固定deepseek-v4-1-flash-260910。复用experiment_2三个同seed timestamp-interest Full，配对分析共12单元、13200次机会。旧九次完批时定时器已暂停；采用既有结果本身不构成新批授权。

| 直接资产 | 用途 |
|---|---|
| [EXPERIMENT.md](EXPERIMENT.md) | 已采用的条件、固定项、窗口、比较口径、预算历史与局限 |
| [init/](init/README.md) | 旧九份及新增21份配置、Full参考、输入、steps与分批manifest |
| [runs/](runs/README.md) | 已完成第二批的独立正式副本，原始计划/日志/Agent/replay不改写 |
| [analysis/](analysis/README.md) | 正式路径的只读提取、绘图、报告及离线核验工具 |
| [payloads/](payloads/README.md) | 预设分析计划、用户已确认的三项结论与图契约 |
| [checks/](checks/README.md) | 旧结果检查及本次21配置离线验收、模型探针和旧资产保全 |
| [run_seed_extension.py](run_seed_extension.py)、[verify_seed_extension_controller.py](verify_seed_extension_controller.py) | 新21次最多两路的官方CLI调度、只读status、按PID停止及假进程检查 |
| [verify_seed_extension.py](verify_seed_extension.py)、[probe_seed_extension.py](probe_seed_extension.py)、[seed_extension_guard.py](seed_extension_guard.py) | 新增配置禁网验收、有限接口测试及预算/截止边界检查；均不启动仿真 |
| [provenance/](provenance/README.md) | 原始失败、路径修正/并行交接、历史来源和新旧路径映射 |
| [adoption.json](adoption.json) | 用户接受与落地授权；独立模型审阅和正式harness签署仍为false |
| [.gitignore](.gitignore) | 原始引擎产物、可重建缓存的Git边界，不授权删除 |

正式报告和全套图表见[配对分析](../../presentation/hypothesis_4/timestamp_bdr_v1/README.md)，双语综合见[综合入口](../../synthesis/timestamp_bdr_v1/README.md)。预设差值均为消融−同seed Full：去B晚期周供给−7.00帖；去D晚期玩梗型作者发言率−30.70个百分点；去R事件后全体发言率+30.07个百分点。三个seed方向一致，保留实际配对值和范围，不报告显著性或置信区间。

去D前期释放表达，玩梗型作者W12–W18平均由1.33增至61.33条，晚期由36.33降至13.00条；去R的全窗口总量由219.00增至520.67条，但玩梗型作者由37.67降至25.67条。逐周轨迹、阅读/累计接触、原始Agent12记录及34次去R晚期发言损失核验均已保存；这是支持闭环解释的过程证据，不是独立中介分解。

作用结论仅限冻结interest配置、3个seed及相同人口/调度表。Full与消融分批运行，API路径/返回模型标识存在差异，无法确认后台完全相同；R=1同时消除B权重，三项差值不可相加为贡献率。固定作者类型、环境阅读标签、既有词表正文标签分别保留，均不冒充人工语义金标。

原始配置和运行计划中的历史路径不批量重写；当前实际复算来源由presentation中的source_index.json指向正式目录，映射见provenance/path_map.json。正式工具不依赖活跃探索run或其workspace。共享账本实际记录仍为第二批_extra_attempts.count=5；不重置预算或提供自动重跑入口。

离线重建及验证命令见analysis/README。主项目机器流水线状态本次保持原样：用户接受已如实登记，但未伪造独立模型review或validate-synthesis签署。未改论文正文，供后续按已接受证据写作。
