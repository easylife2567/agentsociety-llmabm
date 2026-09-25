---
schema: agentsociety.paper-review.meta/v1
title: Internal Mock MetaReview
review_mode: author_side_internal_mock_ensemble
round_id: generic-r3
venue: generic
venue_edition: "project-local"
input_manifest: paper/reviews/generic-review-r3/input-manifest.yaml
pdf_intake:
  status: pass
  report_path: paper/reviews/generic-review-r3/pdf-intake/extraction-report.json
  report_sha256: fa2dd0a6a7fffb9fc28b8aacd73736c35187bfde6bc70cdcb99904a55547e3cc
  warnings: []
individual_reviews:
  - paper/reviews/generic-review-r3/reviewer-1.md
  - paper/reviews/generic-review-r3/reviewer-2.md
  - paper/reviews/generic-review-r3/reviewer-3.md
ensemble_size_requested: 3
ensemble_size_completed: 3
execution_mode: parallel
score_observations: [2, 2, 2]
score_median: 2
score_spread_steps: 0
recommendation_votes: [reject, reject, reject]
decision_band_votes: [negative, negative, negative]
concern_agreement:
  unanimous_confirmed: 6
  majority_confirmed: 0
  minority_confirmed: 0
  rejected_after_verification: 2
  unresolved: 0
robustness_status: high
adjudication_required: false
meta_score:
  value: 2
  label: Reject / substantial revision
meta_score_override:
  applied: false
  median_value: 2
  final_value: 2
  reason: null
confidence:
  value: 3
  label: fairly confident
primary_reroute: experiment_config
secondary_reroutes:
  - analysis
  - generate_paper
  - human_decision
blocking_issue_ids: [M1, M2, M3, M4]
---

# Internal Mock MetaReview — Generic

> 这是作者侧内部模拟元评审，不是 ACM Web、CSCW 的正式评审或录用概率。文中 1–5 分仅属于项目本地 generic 量表。

## Review target and ensemble

目标为冻结的 20 页中文主稿 `paper/manuscript/source/v3_20260915_2306_悼念退潮之后.pdf`（SHA-256 `48a4111f22b7b8952d591e2e61721a1382b73e7c4579e4f0da25558cd2aa7340`）。三份独立评审均使用 `generic-r3` 清单、同一 PDF intake 和项目本地 [generic 量表](../../.claude/skills/agentsociety-paper-review/references/venues/generic.md)；三人给出相同总体判断，但对投稿伦理、完整 LLM 消融的严重程度有差别。本评审对照主稿、冻结附录、`EXPERIMENT.md`、消融登记/结果及三份派生 CSV 核验，不把工作区外未提供的原始帖文、平台曝光日志或伦理文件推定为不存在。

## Artifact intake and limitations

共享 PDF intake 状态 `pass`、20 页、无警告。MetaReview 前的 SHA-256 核验覆盖清单中全部 9 个被审材料、5 个参考文件、intake 报告和报告列出的全部 44 个生成文件，**59 项均匹配**；原始 PDF 与 intake 的源摘要一致。未重新抽取源 PDF。通读共享 `document.txt` 后，对候选重大问题的页码与视觉依赖内容重新检查了页面渲染 **5–18 页中的 5、6、7、8、9、10、11、12、13、14、15、16、17、18 页**：样本/作者论证、注入数量、效用公式、表 1–4、图 1–4、评价口径、结论及附录指引均可辨读。PDF 文字层的部分公式符号失真，公式判断据第 8 页渲染及冻结附录。未复核 52,716 条原始帖文、标注员记录、完整运行轨迹或真实平台推荐日志；这限制了经验测量与外部效度判断。

## Paper summary

论文以三平台 52,716 条已编码帖文描述一位公众人物逝后“教育—悼念—玩梗”的周度类别变化，再以 100 名固定类型 Agent、11 周、每臂 3 个 seed 比较全历史随机、小时级时序、兴趣信息流三种**完整模拟制度**。真实帖子按周注入；表达由 `U=B+R(D−B)` 的阈值决定，LLM 在获准发帖后生成文本。另有 100 个配对 seed 的无 LLM 数值代理消融。稿件据模型内曝光、发言和回流链讨论平台策展与数字哀悼治理。

## Claimed contributions

1. 从帖子类别构成而非讨论总量刻画逝后公共表征的时序变化。
2. 以可切换信息流制度展示可见性、固定类型 Agent 表达和内容回流的可能反馈。
3. 用 B、D、R 数值消融解释常态表达、意见气候和注意力余量在模型中的作用，并提出治理方向。

## Reviewer score observations

| Reviewer | Overall | Confidence | Recommendation | Primary reroute |
|---|---:|---:|---|---|
| R1 | 2/5 | 3/5 | reject | `experiment_config` |
| R2 | 2/5 | 3/5 | reject | `experiment_config` |
| R3 | 2/5 | 3/5 | reject | `experiment_config` |

项目本地总体分中位数 **2/5**，跨度 **0 个原生量表档位**；决策带为 **negative / negative / negative**。清单记录并行执行，轮次中未见重试产物。各维度同为本地 1–5 分：

| Venue dimension | R1 | R2 | R3 | Median | Spread in native steps |
|---|---:|---:|---:|---:|---:|
| Technical soundness | 2 | 2 | 2 | 2 | 0 |
| Novelty and relation to prior work | 3 | 3 | 3 | 3 | 0 |
| Significance | 3 | 3 | 3 | 3 | 0 |
| Empirical or theoretical evidence | 2 | 2 | 2 | 2 | 0 |
| Clarity | 3 | 3 | 3 | 3 | 0 |
| Reproducibility | 2 | 2 | 3 | 2 | 1 |
| Limitations, ethics, and societal impact | 2 | 2 | 2 | 2 | 0 |

## Agreement and robustness

六组实质问题均由三份评审提到并经元评审核实：后段输入/事后人口、捆绑的制度差、行为机制效度、真实基准审计、投稿稿形态、伦理责任。分歧主要是**严重程度与修复阶段**：R1 把投稿与伦理材料合为重大项，R2/R3 视为次要投稿障碍；R3 单列未完成的正式 LLM 消融，R1/R2 更强调这并不能替代独立现实行为验证。两处事实误读已核实并在下表驳回，未导致未决重大冲突。依协议，分数跨度 0、全部同一负面决策带、没有未决重大问题或重试，故为 **high robustness**；这只说明本轮模拟评审判断稳定，不证明判断无偏或论文真实录用前景。原始采集和标注记录、独立行为数据及所提最小对照可进一步降低科学不确定性。

## MetaReview venue scorecard

本地总体 **2/5：Reject / substantial revision**，置信度 **3/5：fairly confident**；维度中位数见上表。优势是明确区分真实、Agent-only、混合和代理结果（PDF 第 9、11–12 页），并报告兴趣臂 DTW 均值 22.0、随机臂 23.7 的三 seed 范围重叠（第 12–13 页）。技术与证据只得 2 分，是因为这些数据支持“给定设计条件下模拟制度导致不同模型输出”，尚不足以识别真实平台算法和真实用户表达机制。总分按中心主张与证据权衡，不由维度均值计算。

## Confirmed strengths

- 现实样本大、时间问题具体；第 6、12–13 页显示值得研究的晚期类别转折，但目前只能严格称为**所采帖子**的类别构成。
- 三臂配对 seed 与注入样本，报告 9 个正式 run 全部完成（第 10–11 页），还公开了效用公式和提示/算法附录。
- 主稿承认 DTW 重叠与终点过冲，图 3（第 14 页）提供供给、曝光、发言和回流的可检查模型链。

## Confirmed concerns

### M1 — 后段真实波形和事后人口进入解释系统

- Severity: major
- Support: 3/3（`R1-W1`、`R2-W1`、`R3-W1`）
- Meta verification: verified（数量误读另见驳回表）
- Paper pointer: PDF 第 7、9–10、12–13 页；`EXPERIMENT.md`“真实帖子注入”
- Suggested reroute: `experiment_config`
- Why it matters: 用真实 W19–W22 类别结构持续注入后，再以该阶段相似性论证“既有玩梗群体被算法放大而产生延迟起爆”，会混淆外生输入与内生反馈。Agent 类型还按 W12–W22 全窗发帖人口确定，不能直接证明这些群体在事件前具有相同规模。
- Verified evidence: 方案是**每个 seed 在 W12–W22 全程预抽 250 条**，各周按真实类型比例分层；W19–W22 分别注入 **18/20/23/24** 条。第 7 页“每周约 250 条”为主稿笔误；第 10 页表 2 的终态帖池与 Agent 帖差值约 250，与方案吻合。人口口径使用 W12–W22。第 13 页图 2 显示三臂均在 W20 起量，但没有仅注入或去后段波形对照。因此不能断言输入**完全决定**结果，也不能据当前拟合排除输入驱动。
- Suggested action: 预定同注入序列的“无 Agent 回流/无可见性反馈”基线及去后段波形的匹配输入反事实，分别比较 Agent-only 发言、混合供给和转折时点；评估仅用事件前信息定义群体的可行性。同步更正注入数量措辞。
- Resolution evidence: 固定设计与配对输出展示内生反馈相对外生波形的增量；若事前群体无法可靠估计，明确将其视为事后构造的模型人口。
- Score impact: 是首要 2 分门槛；可识别的增量与稳健群体口径会提高技术/证据评价，若无增量则应收窄中心结论。

### M2 — 三种信息流是捆绑制度，无法单独归因兴趣排序

- Severity: major
- Support: 3/3（`R1-W2`、`R2-W2`、`R3-W2`）
- Meta verification: verified
- Paper pointer: PDF 第 7–8、10、14、16 页；冻结附录 B
- Suggested reroute: `experiment_config`
- Why it matters: 三套制度的模型内对比是有效的**制度包反事实**，但不能单独把差异解释成纯兴趣匹配或现实平台的排序效应。
- Verified evidence: random 从截至当期的全历史池均抽；chronological 按小时行动、取最新十帖并允许跨小时同周反馈；interest 另有生命周期/饱和、加权匹配、官方置顶和 W13 悼念保底。第 10 页表 1 的单一 Γ 因子承载了全部规则差异，第 16 页却突出“兴趣匹配逻辑”解释发言差。
- Suggested action: 若保留个性化排序主张，建立候选池、时点、置顶/保底和回流节奏相同、仅改变选择规则的配对对照；若只研究完整制度，就把贡献明确限定在制度包层面。
- Resolution evidence: 预定估计量、设计矩阵及单规则效应；或与现有证据严格对应的制度包结论。
- Score impact: 单因素效应可提高技术分；若仅有三臂，投稿结论应明显收缩。

### M3 — 表达机制与数值消融缺少独立行为效度

- Severity: major
- Support: 3/3（`R1-W2`、`R2-W3`、`R3-W4`）
- Meta verification: verified
- Paper pointer: PDF 第 5、8–9、11、15–16 页图 4；`ABLATION_anchored_v1.md` 与数值消融 `RESULTS.md`
- Suggested reroute: `experiment_config`
- Why it matters: 可证明 B/D/R 在**作者设定的模型**内起作用，但不足以证明真实悼念者因同类曝光而沉默或因累计曝光而疲劳。正式 LLM 消融未运行也限制了代理与完整系统的一致性判断。
- Verified evidence: 第 8 页可读公式和第 9 页写明 `U` 先决定是否发帖，LLM 仅生成发帖正文；第 11 页表 3 与结果文件确认 100-seed 消融未调用 LLM，95% 区间仅是 Monte Carlo 变异。`ABLATION_anchored_v1.md` 登记了三个正式消融但标注未启动。第 15 页图 4 确实只显示模型代理的供给方向。
- Suggested action: 对 D/R 设独立可证伪的行为预测和更简单基线，并在未用于标定的用户/曝光资料中检验；若无法取得，称其为“假设下的模型敏感性”。已登记的正式消融可在设计检查后运行，以检验代理结论能否转移到完整系统，但**不能代替真实行为验证**。
- Resolution evidence: 独立行为效标与误差，或明确收窄的结构充分性论断；若保留完整 LLM 系统机制贡献，还需配对正式消融日志与生成文本分类核查。
- Score impact: 行为效度可显著提高证据分；仅补正式消融主要加强模型内部可信度，不足以单独改变当前总评。

### M4 — 真实类别基准的采集、编码与平台稳健性尚不可审查

- Severity: major
- Support: 3/3（`R1-W3`、`R2-W4`、`R3-W3`）
- Meta verification: verified（“审稿材料缺少审计”已核实；原始标签质量不可从冻结材料判定）
- Paper pointer: PDF 第 5–6、9、12–13、16 页；`benchmark.csv`、`arm_platform_user_chain.csv`
- Suggested reroute: `analysis`
- Why it matters: 真实轨迹同时用于人口/注入/效标；若采集覆盖、类别边界或平台权重影响转折，整个机制解释的现实锚点会移动。
- Verified evidence: 第 6 页给出 52,716 条有效帖及平台量（小红书 33,328、抖音 16,602、微博 2,806），未在主稿或冻结附录展示采集/去重流程、复标一致性、分歧处理或分平台周曲线。第 12–13 页的 DTW 均值 22.0/23.7 范围重叠；W22 agent-only 份额 44.3%/83.9%/83.9% 与现实五类 63.0% 有明显偏差。**60.3% 与 63.0% 并非矛盾**，详见驳回表。
- Suggested action: 基于现有原始记录完成采样和编码审计、分平台与固定权重曲线、作者口径、注入/seed 敏感性，并给出图 2 的精确五类归一化及 Agent-only/混合分母。
- Resolution evidence: 可重复的代码本、复标记录与分层周图，说明转折是否对合理采样和编码选择稳健；若原始记录不足，应明确外推范围。
- Score impact: 稳健可提高经验依据与复现分；若转折依赖单个平台/口径，现实贡献需收缩。

### M5 — 现稿不具备目标渠道的自足投稿形态

- Severity: minor（R1 评为 major，R2/R3 评为 minor；不以格式替代 M1–M4 的科学门槛）
- Support: 3/3（`R1-W4`、`R2-W5`、`R3-W5`）
- Meta verification: verified
- Paper pointer: PDF 第 1、10–13、17–18 页及 20 页整稿
- Suggested reroute: `generate_paper`
- Why it matters: 当前文件无法直接作为目标渠道稿件送审，且治理措辞与实证范围不完全相称。
- Verified evidence: 中文单栏 20 页，主要结果从第 12 页展开，第 18 页只把附录指向本地工作区；第 17–18 页提出可见性治理但承认没有评价具体方案。ACM Web 2027 官方征稿要求英文双栏、长文前 8 页自足、总页数至多 12 页，并在首页说明具体 Web 问题。
- Suggested action: 在 M1–M4 的证据边界确定后制作目标渠道英文、自足、匿名稿；把未评价的治理效果表述为待检验方向。
- Resolution evidence: 符合所选渠道格式、明确主张范围并附可审查补充材料的投稿包。
- Score impact: 修复直接投稿障碍，但不单独将项目本地 2 分提高到可接收档。

### M6 — 真实帖文使用及规范治理需有责任主体判断

- Severity: minor（潜在后果严重，但冻结稿不足以推定违规）
- Support: 3/3（`R1-W4`、`R2-W5`、`R3-W5`）
- Meta verification: verified（缺少披露已核实；合规状态未知）
- Paper pointer: PDF 第 17–18 页及主稿伦理声明未见
- Suggested reroute: `human_decision`
- Why it matters: 对逝者和可识别用户的帖文进行引用、保存或共享，以及给“恶意玩梗”设治理边界，涉及隐私、表达和误伤，需要研究负责人/机构负责。
- Verified evidence: 主稿未交代数据来源许可、去标识/引用策略或伦理审查状态；第 17–18 页提出抑制相关内容可见性的方向，同时承认没有方案效果评估。此为披露不足，**不是违规认定**。
- Suggested action: 由 PI/机构确定适用的伦理审查、数据分享与引用边界；论文披露实际决定，并说明合理幽默/批评可能被误判的代价。
- Resolution evidence: 有责任主体的伦理与数据治理判定及相应论文披露。
- Score impact: 主要影响伦理维度与投稿可行性；无法仅靠自动化改稿解决。

## Minority and rejected concerns

| Source concern(s) | Support | Verification | Disposition | Reason |
|---|---:|---|---|---|
| `R3-W1` 的“每周约 250 条注入”数量前提 | 1/3 | contradicted | rejected as factual subclaim; M1 retained | `EXPERIMENT.md` 明确是 **每 seed 全程 250 条**，W19–W22 为 18/20/23/24；PDF 第 7 页写错，第 10 页表 2 的终池减 Agent 帖也支持全程 250。时间/类别波形进入输入的担忧仍成立。 |
| `R3-W3` 的 W22 “60.3% 对 63.0% 不能对账”疑点 | 1/3 | contradicted | rejected as discrepancy; M4 retained | `benchmark.csv` 六类含 noise：玩梗 0.603222、noise 0.043087；五类核心归一化为 `0.603222/(1-0.043087)=0.6304`，即论文 63.0%。第 9 页也说明核心/完整双口径。 |
| `R3-W4` 将正式消融缺席作为单独重大项 | 1/3 | verified | merged into M3 | 正式消融确未运行，但它最多检验代理与完整系统一致性；R1/R2 所提的现实行为效度缺口更决定总分。 |
| `R1-W4` 对投稿形态的 major 严重度 | 1/3 | verified | retained as M5, severity minor | 格式问题会阻止当前 PDF 直接投稿，却不能解释当前科学分数；R2/R3 的 minor 定位较符合项目本地总分。 |

没有未获核实而被提升为阻断项的少数意见；事实误读与严重程度分歧已公开保留，未静默平均。

## Questions and score-change conditions

1. 在相同每 seed **全程 250 条**注入计划下，仅注入/无反馈基线能解释多少 W19–W22 转折？再消除后段类别波形时，Agent-only 是否仍出现相似起量？若仍有稳定增量，M1 可缓解；若无，论文应限于给定输入的模拟情景。
2. 固定候选资格、时点、置顶/保底和回流节奏后，只改变兴趣选择规则，曝光与 Agent 发言差是否仍在？若在，个性化机制主张增强；若不在，维持制度包解释。
3. 独立于参数标定的真实用户行为或平台曝光资料能否支持 D/R 的方向和量级？若无，完整 LLM 消融即使一致，也只能提升模型内部而非现实机制效度。
4. 分平台、固定平台权重与独立复标后，W19–W22 转折是否稳健？若稳定且可审计，经验分可能提高；若依赖某一口径，收窄外推。

## Limitations, ethics, and reproducibility

单事件、三平台不均衡采样、固定类型 Agent、作者设定的表达函数、三主实验 seed 和无 LLM 代理消融限制外推。第 13 页重叠的 DTW 范围不能证明兴趣臂优于随机臂；数值消融的 95% 区间仅描述模型抽样随机性。帖子份额不是平台触达份额，也不是受众记忆或态度。附录提供提示、规则与伪代码，但原始采集/标注审计、完整配置/版本和可供外部核查的运行材料未在投稿稿中整合。对真实逝者与普通用户的隐私、引用和内容治理类别需要可问责审定；本评审未发现足以认定违规的证据。

## Final recommendation

**项目本地 2/5（Reject / substantial revision），置信度 3/5，robustness = high；无需另行裁决本轮分数。** 现稿有清楚的研究问题和可运行模型，但给定现实后段输入的仿真拟合不能证明现实平台因果作用，也不能将三套完整制度的差异单独归因于兴趣排序。最有价值的近期目标是先把贡献定为可证伪的结构机制，再用最小对照和可靠经验基准验证。

**ACM Web 2027：** 平台可见性与公共表达属于明确的 Web 问题，适合考虑 Social Networks and Social Media、Responsible Web 或 Search/Recommendation；但目前的现实机制证据与稿件形式均不足以直接投稿。其[官方研究征稿](https://www2027.thewebconf.org/research-track-papers/)要求首页说明具体 Web 挑战，并规定英文双栏、8 页自足正文及最多 12 页总长。**CSCW 2027 及以后：** 数字哀悼和平台介入具有社会技术契合度，现有研究更接近定量社会计算，尚需更扎实的行为/实践证据及概念贡献；按[官方途径](https://cscw.acm.org/2026/rolling.html)，会议报告需先获 PACM HCI/CSCW 或合范围的 TOCHI 接收，具体[分轨标准](https://cscw.acm.org/2026/tracks.html)也要求与贡献类型相称的证据。上述是场域适配判断，**不是两会官方评分或录用概率**。

## Advisory reroute

首要建议 `experiment_config`：M1–M3 的独立对照、估计量与行为效标必须先定义；在既有九次运行上增加 seed 或只重写结论，无法产生这些识别条件。其次 `analysis`：针对 M4 审计现有数据和口径；`generate_paper`：证据边界确定后完成 M5 的自足稿与措辞；`human_decision`：由负责人/机构处理 M6 的伦理及数据共享边界。R3 所提已登记的正式消融可在设计核查后选择运行，但不会替代首要对照或现实行为证据。上述路线仅为建议，本评审未执行任何研究阶段变更。

## Machine-readable handoff

```json
{
  "schema": "agentsociety.paper-review.meta-handoff/v1",
  "review_path": "paper/reviews/generic-review-r3.md",
  "round_id": "generic-r3",
  "ensemble": {
    "requested": 3,
    "completed": 3,
    "execution_mode": "parallel",
    "score_observations": [2, 2, 2],
    "score_median": 2,
    "score_spread_steps": 0,
    "concern_agreement": {
      "unanimous_confirmed": 6,
      "majority_confirmed": 0,
      "minority_confirmed": 0,
      "rejected_after_verification": 2,
      "unresolved": 0
    },
    "robustness_status": "high",
    "adjudication_required": false
  },
  "meta_score": {"value": 2, "label": "Reject / substantial revision"},
  "confidence": {"value": 3, "label": "fairly confident"},
  "primary_reroute": "experiment_config",
  "secondary_reroutes": ["analysis", "generate_paper", "human_decision"],
  "blocking_issue_ids": ["M1", "M2", "M3", "M4"],
  "issues": [
    {"id": "M1", "severity": "major", "support": 3, "verification": "verified", "reroute": "experiment_config", "summary": "后段类别波形和事后人口进入机制解释"},
    {"id": "M2", "severity": "major", "support": 3, "verification": "verified", "reroute": "experiment_config", "summary": "捆绑制度不能单独识别兴趣排序"},
    {"id": "M3", "severity": "major", "support": 3, "verification": "verified", "reroute": "experiment_config", "summary": "表达规则与代理消融缺少独立行为效度"},
    {"id": "M4", "severity": "major", "support": 3, "verification": "verified", "reroute": "analysis", "summary": "真实基准的采集编码与平台稳健性尚不可审查"},
    {"id": "M5", "severity": "minor", "support": 3, "verification": "verified", "reroute": "generate_paper", "summary": "目标渠道投稿稿尚不自足"},
    {"id": "M6", "severity": "minor", "support": 3, "verification": "verified", "reroute": "human_decision", "summary": "真实帖文与治理边界需责任主体判定"}
  ]
}
```
