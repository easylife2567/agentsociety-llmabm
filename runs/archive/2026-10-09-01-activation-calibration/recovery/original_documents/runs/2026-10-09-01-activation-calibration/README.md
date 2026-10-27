# 事件表达激活势能：公式与常态锚点标定质疑

## 目标与边界

用户于2026-10-09明确要求新开run，核查当前U公式及B标定能否回应“事件前锚点使用W13缩放尺度”和“小差异压零”两项质疑，并判断补实验或修改设计的必要性。

本run进行证据核查、数学推演和修订路径评估。探索阶段正式资产只读；随后用户明确要求“我的理论框架的表述落实到主项目中去”，授权选择性更新正式研究文档及论文Markdown理论段落。该授权仅涉及理论表述，正式Agent、环境、配置、历史结果和原始DOCX/PDF保持；不启动LLM，不重新拟合参数，不更新研究流水线，不commit或push。其他候选成果仍须另获采用授权。

用户随后明确：建模目标为机制重演与解释，不做预测。理论框架为“本文将算法策展置于传播反馈回路之中，提出并检验‘可见性配置—选择性表达—内容回流’的表征重组机制，说明平台上的主导逝者形象可以在公众原有倾向未发生普遍改变的情况下，由差异化的表达激活与内容循环逐步生成。”本run以此框架评价标定，不以独立事前预测作为必要条件。

## 基线与阶段

- 基线提交：`69d243955d341444ae769fae5bf23dc160465cd6`。
- 起始`git status --short`为空，暂存区与工作区干净。
- 当前正式入口：`hypothesis_4/experiment_2`；机器阶段只读快照为`run_experiment / needs_revision`，revision_round=10，本run不改变该状态。
- 当前阶段：已依据作者定稿与侧边聊天重新组织后续写作，完成逐段写作报告及最小补充安排。保留正式原U、参数和三种完整制度，不采用上一轮随机发言/只读起始候选，不新增U实验。论文结构已落主项目；当前新版主批已获授权并于2026-10-14启动，正文重写尚未开始，run保持活跃。
- 本轮代码基线仍为上述commit；task_start_git_status.txt记录本轮开始时的未提交文档变化（含用户更新的AGENTS）。这些变化不自动带入workspace；理论目标按用户最新指令及experiment_protocol.md冻结。未修改已有代码，因此无需代码补丁；新增脚本完整保留在run外层，不依赖workspace私有新增文件。

## 一级资产

| 资产 | 用途 |
|---|---|
| [README.md](README.md) | 唯一实时状态、授权、资产索引及交接 |
| [.gitignore](.gitignore) | 隔离workspace与可丢弃tmp的忽略规则 |
| [assessment.md](assessment.md) | 两项质疑的判断、证据边界与设计/验证建议 |
| [calibration_audit.py](calibration_audit.py) | 无项目代码导入的标准库算术复核，只读冻结数据 |
| [calibration_evidence.json](calibration_evidence.json) | 五类B复算、极限人数、尺度压力测试及来源SHA256 |
| [experiment_protocol.md](experiment_protocol.md) | 实验1/2预先约定的矩阵、判据、预算与代理边界 |
| [calibration_experiments.py](calibration_experiments.py) | 冻结输入、窗口复核、复用正式环境开展闭环代理 |
| [task_start_git_status.txt](task_start_git_status.txt) | 本轮开始时主工作区状态，不含用户改动的diff |
| [experiment_execution.log](experiment_execution.log) | 原始执行与失败日志；重要证据，不放tmp |
| [experiment_manifest.json](experiment_manifest.json) | 输入/代码SHA256、基线、依赖、冻结尺度及矩阵预算 |
| [baseline_observations.csv](baseline_observations.csv) | 现实数据逐周聚合，作者身份不保存 |
| [window_checks.csv](window_checks.csv)、[baseline_evidence.json](baseline_evidence.json) | 11窗口×4测量口径×5类的220条检查及候选门槛 |
| [scale_anchors.csv](scale_anchors.csv) | 五条件的实际期望/B/极限人数，识别整数档退化 |
| [feedback_evidence.json](feedback_evidence.json)、[weekly_metrics.csv](weekly_metrics.csv) | 45单元完成证据、周供给/曝光/候选池指标 |
| [summarize_experiments.py](summarize_experiments.py)、[experiment_analysis.log](experiment_analysis.log) | 配对汇总与49,500次决策独立复算 |
| [experiment_summary.json](experiment_summary.json)、[trajectory_summary.csv](trajectory_summary.csv)、[arm_contrasts.csv](arm_contrasts.csv) | 闭环改变、峰周、制度差值与反转，全条件保留 |
| [action_audits/](action_audits/README.md) | 45个逐行动压缩审计文件，重要原始证据 |
| [cell_metrics/](cell_metrics/README.md) | 45个单元周汇总与审计哈希 |
| [plot_experiments.py](plot_experiments.py)、[calibration_results.png](calibration_results.png)、[calibration_results.svg](calibration_results.svg) | 绝对供给与份额并列的静态图，不以份额代替绝对增长 |
| [verify_recovery.py](verify_recovery.py)、[recovery_evidence.json](recovery_evidence.json)、[experiment_recovery.log](experiment_recovery.log) | 独立基线恢复窗口及2个闭环单元的实际证据 |
| [validation_evidence.json](validation_evidence.json) | 来源不变、单元数量、文档链接及最终资产SHA256核验 |
| [frozen/](frozen/README.md) | 可恢复的冻结配置、素材、观察聚合与来源说明 |
| [manuscript_alignment/](manuscript_alignment/README.md) | 作者最新来源校验、前状态副本、正文提取、主工作区文档差异及核验 |
| [后续论文具体写作报告.md](后续论文具体写作报告.md) | 最新依据：定稿衔接、第二章后半至讨论的逐段表述、图表与证据、U压缩及旧稿处理 |
| [必要实验与结果整理.md](必要实验与结果整理.md) | 保留原设计完成既定九次主实验；默认无新增U实验，结果整理及一个条件性小对照 |
| [paper_outline.md](paper_outline.md) | 研究一/二详细大纲、问题—主张—证据—图表对应及ICA正文重点；当前写作组织依据 |
| [outline_sources.json](outline_sources.json) | 本轮所读来源SHA256、开始时Git状态及文档核验；不改原数据或实验 |
| [u_protocol.md](u_protocol.md) | 八项U检验的冻结条件、预算、判据与两阶段顺序 |
| [u_experiments.py](u_experiments.py)、[analyze_u.py](analyze_u.py) | 新增离线条件与独立逐行动复算；复用原冻结素材和共享环境 |
| [u_results_report.md](u_results_report.md) | 八项判断、全部主要条件、回流反例及主实验建议 |
| [u_results/](u_results/README.md) | 108新增单元、3原单元验同、静态映射、全条件统计与原始审计 |
| [u_task_start.json](u_task_start.json)、[u_validation.json](u_validation.json) | 本轮基线/状态、主项目大纲与来源/文档核验 |
| [u_execution.log](u_execution.log)、[u_analysis.log](u_analysis.log) | 原始执行及分析输出，不是LLM日志 |
| [verify_u_recovery.py](verify_u_recovery.py)、[u_recovery.json](u_recovery.json)、[u_recovery.log](u_recovery.log) | 从Git准确对象导出源码，实际恢复静态表与两个候选单元 |
| [u_failure_baseline/](u_failure_baseline/README.md)、[u_failure_baseline.log](u_failure_baseline.log) | 首次精确浮点等同失败的完整保全 |
| `workspace/` | 基于准确commit的独立Git worktree，代码与正式资产分离 |

## 已核查事实

- 正式experiment_2保留anchored_v1的B及行为参数；既有baseline-anchor候选未采纳。
- 当前B以W05–W12供给形状乘W13悼念峰换算尺度；亚单位期望的floor与有限人口门槛映射均需核查。
- 相关历史决策仅作证据读取，不续接、修改或归档旧run。
- 独立复算五类当前B与profile及原标定产物一致，R=0时人数为玩梗0/悼念0/营销3/教育0/其他0；三seed数值人口相同。
- 原始正期望人数依次约0.009334/0.000583/2.625159/0.285267/0.071754；四类低频被结构性压为零人数，非日志舍入造成。
- 第一项判断已根据用户明确的解释目标修订：W13参与不自动构成方法缺陷；撤回仅因此必须更换标定的建议，优先完善说明并补共同尺度稳健性检查，再按结果决定。第二项独立待讨论。具体候选机制、参数和预算尚未冻结，未获正式采用或运行授权。
- 验证：算术脚本断言全部通过；workspace/tmp忽略规则有效。旧9900条固定曝光检查为历史证据引用，本轮没有重跑。
- 本地未找到Karpathy Guidelines；查阅历史指向的上游原文，未安装。编码采用Ponytail最小方案，仅新增本run独立复算脚本。

## 已授权的理论表述落实

2026-10-09用户明确授权后，已将原句写入[TOPIC.md](../../../TOPIC.md)、[主假设](../../../hypothesis_4/HYPOTHESIS.md)、[当前实验设计](../../../hypothesis_4/experiment_2/EXPERIMENT.md)、[U模型说明](../../../锚定式事件表达激活模型.md)及[论文Markdown理论框架](../../../paper/manuscript/manuscript.accepted.md)。根README和experiment_2 README同步研究目标与入口。

同步明确机制重演与解释的目标、Agent类型固定的模型条件、可见性/表达/回流的对应关系。TOPIC以反馈回路替换旧热度放大链；HYPOTHESIS旧定向假设与理论依据保留并标明历史身份；论文标注未同步原始DOCX/PDF。本次不采纳新的B、概率行动机制、附加实验矩阵或运行预算。

检查仅针对文档：原句一致性、链接、Git差异格式和修改范围；不运行代码测试或仿真。当前修改均未暂存、未提交。

## 最新作者文稿对齐与后续写作授权（2026-10-12）

用户明确授权先把最新研究背景、文献综述和第二章第一节理论框架落实主工作区，再在本run讨论和重写第二章第二部分及第三、四章。本轮完成前一阶段，主工作区的研究文档与论文Markdown已更新；原始DOCX/PDF、实验代码、配置、数据、历史结果与机器状态保留。实际修改路径及逐文件差异见[对齐证据](manuscript_alignment/README.md)。这是后续新增的文档采用授权，不改变原离线实验候选未采纳的状态。

问题（1）由原始数据挖掘与分析回答；LLM ABM主要回答问题（2）的循环机制与问题（3）的制度差异。总体解释采用传播反馈回路视角与策展流框架，U中的B、D、R为选择性表达的操作化；三臂仍比较完整策展制度。文稿对齐不构成这些机制已获全部验证的声明。

文档核验已通过：三份作者原件SHA256保持不变，三个研究问题与作者稿一致，18项新增引用均有唯一脚注定义，新链接目标存在；摘要、第二章（二）以后的全部旧正文及原脚注逐字保留，此前编码诚信修订说明完整保留。`git diff --check`通过，暂存区为空；本轮没有修改代码、配置或数据，没有运行仿真或改变研究阶段。U说明同时更正门槛为0.95乘0.8–1.2扰动，未更改参数。

2026-10-12用户认可过下列八项正文/补充材料分工；表格保留当时安排。2026-10-14用户进一步要求筛选ICA正文的重中之重，最新取舍以[paper_outline.md第六节](paper_outline.md#六u公式八项问题正文的必要取舍)及下节为准，不再按八项逐一安排正文说明。两版写作安排均不表示各项实验已经完成。

| 问题 | 正文关键信息 | 在线补充材料 |
|---|---|---|
| 1．0.95的选择 | 简述探索后保留的共同门槛基准，非实测心理临界值 | 历史探索、门槛分布、候选值与敏感性 |
| 2．文献公式迁移 | 文献依据、从意见气候到可见内容/从集体注意力到个体接触的迁移与新增假设 | 原模型逐项对应、D/R全式、变量及适用边界 |
| 3．B、D、R标定 | 数据窗口、W13作用、固定/拟合项、三制度共享 | 参数表、换算映射、搜索目标与范围、可识别性及代码 |
| 4．低频差异压零 | 100人尺度下正低频期望被近似为零发言及解释限制 | 原始期望、映射人数、取整与替代规则检验 |
| 5．U组合形式 | U公式、R降低使效用回B，可能减弱激活或释放抑制 | 数学性质、边界、替代组合与检验 |
| 6．初始化与常态 | 初始累计接触、首次行动B不起作用及常态主张边界 | 初始化、W12现实/模拟对照、敏感性 |
| 7．标定与验证 | 数据使用历史、后段检查性质、数值代理与完整生成验证区别 | 设计历史、数据用途、版本及全部验证 |
| 8．反馈机制支持 | 机制干预设计、实际关键结果与可支持的解释 | 全部干预条件、类型/周次结果、重复与补充图 |

上述2026-10-12的章节次序已由下节用户确认的两研究结构替代。不得将现实平台差异当算法因果证据，不将旧批结果写作timestamp结果，不借写作启动新LLM或扩大实验矩阵。

## 两研究结构与正文重点（2026-10-14）

用户明确要求在本run先整理第三、四章详细大纲及“研究问题—主张—证据—图表”对应表。已完成[paper_outline.md](paper_outline.md)：第二章第二部分只写总体研究设计；第三章研究一包含数据/编码/分析方法、现实结果与仿真解释任务；第四章研究二包含模型/标定/评价、制度结果、过程与干预；后续讨论综合两项研究。本文档仅规划，本轮未修改主项目正文、数据、代码、配置或机器研究阶段。

U的八项作为内部核查清单。正文重点合并为三组：2＋5说明规则与传播学依据；3＋7说明参数来源与证据性质；8在结果章呈现机制支持。1的具体数值/探索历史进补充材料，4＋6合并简述低频及常态解释限制；若它们改变核心结论或正文主张常态成功复现，必须提高正文报告程度。当前新主批未运行、直接回流干预和跨群体曝光证据未在所核来源中核实，大纲明确预留而未填入阳性结论。

规划源文件、证据身份、拟图编号及现有/待整理/待运行的界限均在大纲中说明。文档链接、源码/数据只读边界与Git差异格式核验通过，详见outline_sources.json；本轮没有重新执行数值实验、生成图表或调用LLM。下一步按该大纲从现实发现和图表口径整理起，再撰写总体设计和模型方法。

## 本轮采用与U补充结果

用户明确授权执行先离线后主批的方案，并允许本run内比较最小规则调整。实际完成108新增单元、108900次发帖决策、三原单元3300条验同；静态6设置×5类各100000轮；独立分析117原/新单元；从准确Git对象恢复静态表和两候选单元2200条记录。全程零LLM/网络，未修改正式Agent、环境、配置、数据或机器阶段。新脚本是本轮新增实现，没有修改已有代码，因此不需代码patch。

仅采用文档成果：[paper/OUTLINE.md](../../../paper/OUTLINE.md)为正式两研究结构、详细大纲与证据对应，paper README已登记。第三/四章正文尚未改写。行为候选仍留run，不随文档采用而自动落地。当前源码恢复基线和父冻结输入不变；u_experiments及helper的精确版本与协议哈希在u_results/manifest.json。

最新结论见[u_results_report.md](u_results_report.md)：分数期望映射消除结构性压零，门槛/初始化/D/R替代保留主要晚期制度分化，但量级有变化。直接去回流后晚期增长仍存在，不支持“回流必要或统一正向放大”；回流对跨类型可见性的作用因制度而异。首轮约1e-16的B浮点差异检出后已统一读取原标定精确值，失败包保留，不隐藏技术失败。

## 两份报告正式采用及主实验启动授权

2026-10-14用户明确要求将两份报告落实到主项目并开始主实验。已采用到[paper/后续论文具体写作报告.md](../../../paper/后续论文具体写作报告.md)及[paper/必要实验与结果整理.md](../../../paper/必要实验与结果整理.md)，更新paper入口与旧大纲说明。run原报告保留为来源；未改作者定稿或正式行为模型。主实验按experiment_2既定九次运行开展，实际状态只维护于[实验README](../../../hypothesis_4/experiment_2/README.md)。启动授权不包括可选小对照，不自动归档本run或提交Git。

## 最新写作目标与工作取舍

用户明确指出上一轮108个新增条件过度扩大任务，要求重读前两章定稿和侧边聊天，以合理解释研究问题、讲清“可见性配置—选择性表达—内容回流”的表征重组为目标，交付逐段写作报告和单独的必要实验安排。本轮完成[写作报告](后续论文具体写作报告.md)与[最小安排](必要实验与结果整理.md)，重新读两份Word正文/批注/注释、原PDF/当前正文、现实分析、旧完整仿真与当前正式机制；侧边讨论以用户所给完整截图为依据。

当前建议保留已采用timestamp_v1及原U/B/行为参数、W12和各制度旧帖与新帖安排，撤回上一轮将随机发言＋只读W12推荐为主方案以及另跑完整LLM去回流矩阵的推进建议。已完成的108项记录和结果不覆盖、不删除；本轮不继续计算，不修改代码/配置/数据/正文或机器阶段。三种制度的不同旧帖处理属于研究对象，不视为需要统一才能做主比较的错误。

理论检验聚焦整体循环能否生成表征变化及其制度分化，不要求证明每类现实玩梗均由反馈独立生成。先完成已确定九次主实验，再从同批记录整理群体接触、表达、新帖再展示及实际正文。新增U实验默认零；只有额外主张某一回流净作用时才考虑最小安排中的三个数值条件，本轮未执行。报告中的第四章新结果数值明确等待主实验，不拿旧版或候选计算填入。

## 待办与下一步

本轮交付是完整写作报告与最小补充方案，不是正式整稿改写。下一步可按报告先写第三章现实发现与第二章总体设计、第四章方法，完成当前版本主实验后填入过程和制度结果。理论、两研究结构和主设计保持；不先解决全部U内部问题，不追求统一旧帖规则或证明公众心理全部稳定。run保持活跃，未暂存、commit、push或归档。旧结果与补充计算仍可按以下说明恢复，恢复命令不表示应继续跑实验。

复现新条件（从记录commit的干净源码恢复，提供父级冻结包与原脚本，使用新的结果目录以保全原始证据）：

```bash
task_python=$(sed -n 's/^PYTHON_PATH=//p' .env)
task_run=runs/2026-10-09-01-activation-calibration
"$task_python" "$task_run/u_experiments.py" --project-root "$task_run/workspace" \
  --run-dir "$task_run" --output "$task_run/u_results_reproduction"
"$task_python" "$task_run/analyze_u.py" --run-dir "$task_run"
"$task_python" "$task_run/verify_u_recovery.py"
```

analyze_u固定核查已冻结u_results，不写或替换原始审计；重跑到新目录后可独立比较逐行动内容。verify_u_recovery只导出Git对象与复制冻结包到本run tmp，源码完全来自准确commit，无需原workspace或主工作区未提交代码；它不覆盖原始结果。临时恢复副本在验证后删除，重要恢复证据保留外层。

## 独立恢复与实际验证

- 恢复起点：上述commit；现有源码没有修改，故不存在候选代码patch或主工作区前置差异。新增实现为本run四个脚本，最终版本均直接保存在外层；无需原workspace或其他run。
- 必要输入：frozen/全部内容、experiment_manifest.json、experiment_protocol.md、baseline_evidence.json（可由baseline命令重新产生）。采用已登记版本的项目uv解释器与SDK；不复制凭据或虚拟环境，不调用模型。
- 2026-10-12实际独立验证：另建本run内的干净基线worktree，复制冻结输入与脚本到临时恢复目录，窗口CSV/JSON逐字节一致；current与double_stress的interest s0两单元共2200条行动解压内容SHA256及周汇总一致。恢复不依赖原workspace和原工作簿；该范围不等于45单元全矩阵复算。
- 恢复worktree验证后已安全解除Git登记，重要日志与recovery_evidence保留在外层。原探索workspace继续保留；tmp/recovery-output仅是已有证据的可丢弃恢复副本。原始证据中的恢复历史路径不批量改写。
- 首次原始聚合prepare输出记录在execution.log；重建聚合需SHA256一致的原工作簿。通常恢复只读已冻结observations.json即可，不需要再次prepare。
- 上述离线实验阶段未修改主项目源码/配置/数据/理论文档，仅本run资产及runs索引；后续2026-10-12文稿对齐已按独立授权更新正式研究文档，详见上节；未暂存、未commit、未push，未改变机器研究阶段，未启动LLM。

首次实际运行的命令如下（工作目录为主项目根；prepare只执行一次，所有输出在本run，不写正式资产）：

```bash
task_python=$(sed -n 's/^PYTHON_PATH=//p' .env)
task_run=runs/2026-10-09-01-activation-calibration
"$task_python" "$task_run/calibration_experiments.py" prepare \
  --project-root "$task_run/workspace" --output "$task_run" \
  --workbook data/baseline/抖音微博小红书-全量已打标.xlsx
"$task_python" "$task_run/calibration_experiments.py" baseline \
  --project-root "$task_run/workspace" --output "$task_run"
"$task_python" "$task_run/calibration_experiments.py" feedback \
  --project-root "$task_run/workspace" --output "$task_run"
"$task_python" "$task_run/summarize_experiments.py" --output "$task_run"
"$task_python" "$task_run/verify_recovery.py" --run-dir "$task_run" \
  --restored-root "$task_run/tmp/recovery-workspace"
"$task_python" "$task_run/plot_experiments.py" --output "$task_run"
```

在新建的干净基线worktree中，用以下命令恢复（示例项目根为shell当前目录，输出使用新的空目录以保全原始证据）：

```bash
task_python=$(sed -n 's/^PYTHON_PATH=//p' .env)
# 将本run的frozen、protocol、manifest和四个脚本复制到恢复输出目录后：
"$task_python" /path/to/restored-output/calibration_experiments.py baseline \
  --project-root /path/to/clean-worktree --output /path/to/restored-output
"$task_python" /path/to/restored-output/calibration_experiments.py feedback \
  --project-root /path/to/clean-worktree --output /path/to/restored-output
"$task_python" /path/to/restored-output/summarize_experiments.py --output /path/to/restored-output
"$task_python" /path/to/restored-output/plot_experiments.py --output /path/to/restored-output
```

完整反馈命令只执行冻结45个数值条件，脚本检查源码/输入/protocol哈希并拒绝网络；不要对已有action_audits/cell_metrics目录重复执行以覆盖证据。更换B公式、参数、素材规则或矩阵属于新实验，须重新明确设计。
