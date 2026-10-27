# seed3–9的21次兴趣B/D/R消融执行记录

当前状态以[实验README](../../../../README.md)为准。

**当前终态：北京时间2026-10-26 02:07:28新增21次全部完成，21/21逐次完整验收通过，全部本批进程已退出。**每次693步/1100完整唯一行动与决策/11周/100Agent，最终服务/行动/模型失败计数0。有效发布6206帖、正文6214次，旧B失败62次继续计费，总正文6276、共享额外9，原预算/截止未越界。暂未做结果分析。

- [completion_check_recovery_3.json](completion_check_recovery_3.json)：21条件完整矩阵、真实返回模型、预算、退出进程及19,063项实际完成来源哈希；148冻结文件和19,381项旧完成/失败证据保持。
- [completion_registration_recovery_3.json](completion_registration_recovery_3.json)：官方CLI completed/verification complete，明确H4/E3/本批；定时任务b-d-r-seed3-9-30已结束并删除。
- [automation_before_completion_recovery_3.toml](automation_before_completion_recovery_3.toml)：结束前定时配置快照。所有历史终态/停止快照/失败目录保留，不覆盖、不清理。

## 第三次恢复启动记录（历史）

**恢复时记录：用户2026-10-26明确授权后，00:10:03恢复两路。**保留16次完成和所有失败现场，seed8去D/去R在各自_resume1副本从249/174步直接接续，再补seed9三次。原检查点不编辑，原正文4876/额外8起续，原截止当天16:34:46不变；启动时每30分钟任务为ACTIVE，现已完批并结束。

- [recovery_3.json](recovery_3.json)：当前授权、两个接续副本路径、旧B失败62次计费及原配置/总预算/截止。
- [recovery_3_offline_check.json](recovery_3_offline_check.json)及.log：[recovery_3_controller_check.json](recovery_3_controller_check.json)六类假进程检查，16完整结果重验、200Agent恢复、同步行动/发布矩阵、随机状态及环境往返一致，0网络/模型/引擎；19,381项原证据保持。首轮夹具旧脚本名断言失败保留为recovery_3_offline_check_attempt1及recovery_3_verifier_attempt1.py。
- [recovery_probe_3.json](recovery_probe_3.json)：本次一次37tokens接口/模型确认，原90/51/65tokens探针另列。
- [stopped_execution_3.json](stopped_execution_3.json)：原停止状态字节快照；[recovery_launch_receipt_3.json](recovery_launch_receipt_3.json)、[recovery_3_launch_check.json](recovery_3_launch_check.json)：实际启动与推进核对；[automation_at_recovery_3_start.toml](automation_at_recovery_3_start.toml)保存本次定时配置。

运行入口experiment_3/run_seed_extension_recovery_3.py，使用--status/--stop，监督器PID92491；只读新recovery3-engine.log/recovery3-stderr.log和本目录recovery3-supervisor.log判断当前错误，复制的旧日志不作新故障。

## 周额度耗尽终态（历史）

**当时终态：北京时间2026-10-25 00:16:49因服务周额度耗尽自动完全联停，16完成/2中断/3未启动，全部本批进程已退出。**去D seed8为249步/396环境行动/183帖，去R seed8为174步/274环境行动/112帖；seed9三次未启动。16完整结果重新核验通过，正文4,876含旧B失败62次，共享额外8；原配置/预算/截止保持。

证据[terminal_check_recovery_2.json](terminal_check_recovery_2.json)、官方登记回执[terminal_registration_recovery_2.json](terminal_registration_recovery_2.json)单独保存，不覆盖历史。定时任务b-d-r-seed3-9-30已结束并删除，停止前配置见[automation_before_terminal_recovery_2.toml](automation_before_terminal_recovery_2.toml)。服务日志提示10月26日00:00重置仅为未验证信息，原实验截止仍为10月26日16:34:46。

## 第二次恢复启动记录（历史）

**恢复时记录：用户明确授权的第二次恢复于北京时间2026-10-24 22:28:21启动，最多两路。**保留11次完成与所有失败现场，R seed6修复副本从602步接续、B seed7独立重跑，再补其余8次，原配置/总预算/截止保持。实际入口experiment_3/run_seed_extension_recovery_2.py，使用--status/--stop，监督器PID77433；新日志为recovery2-engine.log/recovery2-stderr.log及本目录recovery2-supervisor.log。启动时30分钟任务为ACTIVE，现已结束，当前终态见上节。

- [recovery_2.json](recovery_2.json)：本次授权、实际路径、B失败62次单列计费、R465次只计一次、模型/原预算/原截止和来源冻结。
- [recovery_2_offline_check.json](recovery_2_offline_check.json)及.log：[recovery_2_checkpoint/](recovery_2_checkpoint/)仅补齐已成功694号帖的待提交状态，0正文重生成；11完整结果、13,444项原证据、148项冻结文件验收保持。
- [recovery_2_controller_check.json](recovery_2_controller_check.json)：最终服务失败/发布缺模型联停、不误停成功重试、两路/预算/原截止等六种假进程检查。
- [recovery_probe_2.json](recovery_probe_2.json)：单列接口确认1次/65tokens；前两阶段探针90/51tokens另列。
- [stopped_execution_2.json](stopped_execution_2.json)：上次停止状态原字节；[recovery_launch_receipt_2.json](recovery_launch_receipt_2.json)、[recovery_2_launch_check.json](recovery_2_launch_check.json)：实际启动/推进、694号帖只提交一次及PID/命令核对。

## 上次停止记录（历史）

**上次终态：北京时间2026-10-24 22:01:04恢复后再次完全停止，11完成/2中断/8未启动。**去B seed7的Agent19/W12两次Timeout后发布兜底，缺真实返回模型，无法通过既定完整性验收；监控按规则联停，全部进程退出。证据[terminal_check_recovery_1.json](terminal_check_recovery_1.json)和登记回执[terminal_registration_recovery_1.json](terminal_registration_recovery_1.json)不覆盖第一次停止记录。原定时任务b-d-r-30已结束并删除，其配置保存在[automation_before_terminal_recovery_1.toml](automation_before_terminal_recovery_1.toml)。当时累计正文3529、共享额外7；原证据保持。

## 获授权恢复时记录（历史）

用户随后明确授权继续；北京时间2026-10-24 21:27:50恢复，原10次完成保留，两次中断核查安全后在完整副本接续，后续seed7–9按原manifest补位，原预算/账本/截止不变，30分钟定时器已恢复ACTIVE，暂不分析。授权与路径见[recovery_1.json](recovery_1.json)；[recovery_1_offline_check.json](recovery_1_offline_check.json)记录禁网安全检查及原现场哈希，[recovery_1_controller_check.json](recovery_1_controller_check.json)记录假进程验收，[recovery_probe_1.json](recovery_probe_1.json)记录单列恢复探针1次/51tokens，[recovery_1_launch_check.json](recovery_1_launch_check.json)记录实际启动推进核对。旧状态原字节保存于[stopped_execution_1.json](stopped_execution_1.json)。运行/状态/停止入口改用experiment_3/run_seed_extension_recovery.py，并实际ps匹配脚本名核对监督器；其绝对路径检测的supervisor_alive字段可能误报false，说明见实验README。

第一次因服务5小时额度耗尽，于北京时间2026-10-24 21:06:52按冻结规则完全停止，10完成/2中断/9未启动。证据[terminal_check.json](terminal_check.json)、[terminal_registration.json](terminal_registration.json)和[automation_at_stop.toml](automation_at_stop.toml)保留当时事实，后续终态须另存，不覆盖。本次授权不允许未来失败后自行再次恢复。

## 准备时历史记录

- [preparation_plan.json](preparation_plan.json)：execution_authorized=false，21条件、同seed Full、当前模型、预算、两路上限、48小时首次启动计时、失败联停与只读/探针证据。
- _extra_attempts.count：独占初始化为0，21次共享额外正文请求额度2,310；旧九次账本5保持。SDK辅助请求及单列2次接口探针不在该账本中。

正文上界25,410、23,100次机会；当前无started_at或deadline_at。未来正式启动后不得因交接、停机或恢复重置48小时保护；失败不自行重跑或接续checkpoint。完整配置清单在实验init/manifest_seed3_9.json，所有引擎目录尚未创建，不提供当前仿真运行许可。

## 首次正式启动记录（历史）

- [runtime_plan.json](runtime_plan.json)：用户最新正式授权、首次启动及绝对截止、148项冻结文件、21配置、原预算与失败联停规则。
- [batch_execution.json](batch_execution.json)：本批唯一动态执行状态，completed与active_runs逐次记录真实引擎和请求；不能使用上级根目录旧九次状态。
- supervisor.log、supervisor.lock、launch_receipt.json：新监督器日志、互斥锁与原始启动回执；不覆盖旧实验记录。

只读检查从项目根用.env的PYTHON_PATH执行experiment_3/run_seed_extension.py --status；停止用--stop。不要再次启动。48小时从runtime_plan.started_at起，截止已固定，不因切换条件而重新计时。定时器b-d-r-30每30分钟报告，终态核验后暂停；不做分析。
