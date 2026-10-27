# 事件表达激活势能：公式与常态锚点标定质疑

## 目标与边界

用户于2026-10-09明确要求新开run，核查当前U公式及B标定能否回应“事件前锚点使用W13缩放尺度”和“小差异压零”两项质疑，并判断补实验或修改设计的必要性。

本run进行证据核查、数学推演和修订路径评估。探索阶段正式资产只读；随后用户明确要求“我的理论框架的表述落实到主项目中去”，授权选择性更新正式研究文档及论文Markdown理论段落。该授权仅涉及理论表述，正式Agent、环境、配置、历史结果和原始DOCX/PDF保持；不启动LLM，不重新拟合参数，不更新研究流水线，不commit或push。其他候选成果仍须另获采用授权。

用户随后明确：建模目标为机制重演与解释，不做预测。理论框架为“本文将算法策展置于传播反馈回路之中，提出并检验‘可见性配置—选择性表达—内容回流’的表征重组机制，说明平台上的主导逝者形象可以在公众原有倾向未发生普遍改变的情况下，由差异化的表达激活与内容循环逐步生成。”本run以此框架评价标定，不以独立事前预测作为必要条件。

## 基线与阶段

- 基线提交：`69d243955d341444ae769fae5bf23dc160465cd6`。
- 起始`git status --short`为空，暂存区与工作区干净。
- 当前正式入口：`hypothesis_4/experiment_2`；机器阶段只读快照为`run_experiment / needs_revision`，revision_round=10，本run不改变该状态。
- 当前阶段：2026-10-12用户明确授权的实验1与2离线阶段已完成，窗口检查与45单元有限正文闭环代理全部通过执行验收；恢复验证通过。run保持活跃，B标定与行动候选未采纳。
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

2026-10-09用户明确授权后，已将原句写入[TOPIC.md](../../TOPIC.md)、[主假设](../../hypothesis_4/HYPOTHESIS.md)、[当前实验设计](../../hypothesis_4/experiment_2/EXPERIMENT.md)、[U模型说明](../../锚定式事件表达激活模型.md)及[论文Markdown理论框架](../../paper/manuscript/manuscript.accepted.md)。根README和experiment_2 README同步研究目标与入口。

同步明确机制重演与解释的目标、Agent类型固定的模型条件、可见性/表达/回流的对应关系。TOPIC以反馈回路替换旧热度放大链；HYPOTHESIS旧定向假设与理论依据保留并标明历史身份；论文标注未同步原始DOCX/PDF。本次不采纳新的B、概率行动机制、附加实验矩阵或运行预算。

检查仅针对文档：原句一致性、链接、Git差异格式和修改范围；不运行代码测试或仿真。当前修改均未暂存、未提交。

## 待办与下一步

两实验结果详见assessment.md开头：主要晚期表征重组与制度分化保留；局部差异会反转；常态均值转换相容不等于W12动态相容。当前W12初始发布数约25–26、固定尺度现实参照5.288，R初值含义需要另行澄清。第二项低频行动规则没有修改或解决。后续若检验常态初始化或正式LLM尺度敏感性，分别按所选设计及预算执行；不沿用旧批预算。实时状态仅维护于本README。

## 独立恢复与实际验证

- 恢复起点：上述commit；现有源码没有修改，故不存在候选代码patch或主工作区前置差异。新增实现为本run四个脚本，最终版本均直接保存在外层；无需原workspace或其他run。
- 必要输入：frozen/全部内容、experiment_manifest.json、experiment_protocol.md、baseline_evidence.json（可由baseline命令重新产生）。采用已登记版本的项目uv解释器与SDK；不复制凭据或虚拟环境，不调用模型。
- 2026-10-12实际独立验证：另建本run内的干净基线worktree，复制冻结输入与脚本到临时恢复目录，窗口CSV/JSON逐字节一致；current与double_stress的interest s0两单元共2200条行动解压内容SHA256及周汇总一致。恢复不依赖原workspace和原工作簿；该范围不等于45单元全矩阵复算。
- 恢复worktree验证后已安全解除Git登记，重要日志与recovery_evidence保留在外层。原探索workspace继续保留；tmp/recovery-output仅是已有证据的可丢弃恢复副本。原始证据中的恢复历史路径不批量改写。
- 首次原始聚合prepare输出记录在execution.log；重建聚合需SHA256一致的原工作簿。通常恢复只读已冻结observations.json即可，不需要再次prepare。
- 本轮未修改主项目源码/配置/数据/理论文档，仅本run资产及runs索引；未暂存、未commit、未push，未改变机器研究阶段，未启动LLM。

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
