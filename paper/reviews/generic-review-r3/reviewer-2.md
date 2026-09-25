---
schema: agentsociety.paper-review.individual/v1
title: Internal Mock Review — Independent Reviewer R2
review_mode: author_side_internal_mock_individual
round_id: generic-r3
reviewer_id: R2
independence: isolated
input_manifest: paper/reviews/generic-review-r3/input-manifest.yaml
venue: generic
venue_edition: "project-local"
template_verified_at: "2026-09-25"
template_source: "none"
score_scale_origin: project_local
reviewed_at: "2026-09-25T20:25:31+08:00"
reviewed_artifacts:
  - path: "paper/manuscript/source/v3_20260915_2306_悼念退潮之后.pdf"
    sha256: 48a4111f22b7b8952d591e2e61721a1382b73e7c4579e4f0da25558cd2aa7340
  - path: paper/manuscript/manuscript.accepted.md
    sha256: 6945443a48ed2382fb84990db1c71de8ee5f57a181b8d6591da3bf40693049b6
  - path: "paper/appendices/附录Ⅰ和Ⅱ：Prompt模板与算法伪代码.md"
    sha256: f24ea9daf675e5cd4c916909a7a5ff038adf4c6b67ca084f0fed2070b03e4a41
  - path: hypothesis_4/experiment_1/EXPERIMENT.md
    sha256: 2ab46542078bf85521d678ee919edd7aa28881d6a8eec33233a3a9a9aca995e3
  - path: hypothesis_4/experiment_1/ABLATION_anchored_v1.md
    sha256: bd40881013aa417d5ffd7d14c55499779178f80f3095d50d031d5786ced84a55
  - path: hypothesis_4/experiment_1/results/numerical_ablation_drb/RESULTS.md
    sha256: 644dbc73456a14d317b37adf8740659b4348d1b4af1802ca6aae9e8076524a27
  - path: hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_dtw_fit_summary.csv
    sha256: 8ee15d5460b64a9b6c06bc56fbf5bfa40f89116d8bf04498a185f310ac12ece8
  - path: hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_platform_user_chain.csv
    sha256: 1543930ea5d57a72ca5b2e7f2bd16eaff9768aab32a88bc2a9cac5a1bf56d35d
  - path: hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/benchmark.csv
    sha256: ef841e6bce9e75a69cb7e787b5167864bd425d1e44988625e534212398cebded
pdf_intake:
  status: pass
  report_path: paper/reviews/generic-review-r3/pdf-intake/extraction-report.json
  report_sha256: fa2dd0a6a7fffb9fc28b8aacd73736c35187bfde6bc70cdcb99904a55547e3cc
  warnings: []
overall_score:
  value: 2
  label: Reject / substantial revision
confidence:
  value: 3
  label: fairly confident
recommendation: reject
primary_reroute: experiment_config
secondary_reroutes:
  - analysis
  - human_decision
  - generate_paper
blocking_issue_ids:
  - W1
  - W2
  - W3
  - W4
---

# Internal Mock Review — Generic — R2

> 这是一份独立的作者侧内部模拟评审，不是 ACM Web、CSCW 的正式评审或录用概率。下列 1–5 分仅属于项目本地 generic 量表。

## Review target

R2 审阅 `generic-r3` 冻结清单中的 20 页主稿（SHA-256 见 frontmatter），并用同清单中的正文交叉稿、Prompt 与伪代码附录、实验设计、消融说明及结果、三份汇总 CSV 核查关键主张。评分模板是 `.claude/skills/agentsociety-paper-review/references/venues/generic.md` 的项目本地量表；ACM Web 2027 和 CSCW 2027+ 的契合度另行讨论。主稿可读，但机制辨识、标注审计、伦理依据与复现实务仍倚赖稿外材料；作为投稿主文尚不自足。未见原始帖文、完整标注审计、平台推荐日志、真实用户行为资料或机构伦理审查结论；据此不能断言这些资料不存在。

## Artifact intake and limitations

共同 PDF intake 状态为 `pass`，无警告。已通读 `document.txt` 的 20 页正文、附录说明和参考文献，并用共同生成的页面 PNG 核查所引用的视觉证据：第 6 页图 1、第 8 页效用公式、第 10–11 页表 1–3、第 13 页图 2、第 14 页图 3a/3b、第 15 页图 4；这些元素可辨认。页码以下均指 PDF 印刷页码。正文文本抽取对数学符号有乱码，故公式判断依据第 8 页渲染图及冻结附录 F-1–F-3。没有未能辨读的关键元素。

## Paper summary

论文用抖音、微博、小红书 52,716 条已编码帖文描述一位公众人物去世后，教育讨论、悼念与玩梗内容的周度构成变化。模型设 100 个固定类型 Agent、每周真实帖子注入和三种信息流制度；是否发帖由锚定式效用 `U=B+R(D−B)` 决定，LLM 在已决定发帖后生成正文。九次正式运行比较随机、时序与兴趣制度，另以 100 个配对种子的无 LLM 数值代理消融 B、D、R。稿件据此提出“平台配置可见性—用户表达—内容回流”解释及治理建议。

## Claimed contributions

1. 以帖文类别而非单纯提及量刻画逝后数字表征的“教育—悼念—玩梗”阶段变化。
2. 用可切换信息流制度和固定类型 Agent 展示不同可见性配置下的表达与内容回流轨迹。
3. 用 B、D、R 消融将常态表达、意见气候和注意力衰减分别对应于模型中的持续供给、选择性激活和退潮。

## Venue scorecard

| 项目本地维度（1–5） | 分数 | 证据与理由 |
|---|---:|---|
| Technical soundness | 2 | 第 8 页公式与第 11 页表 3 的内部逻辑明确；然而所设行为规则与平台制度的对比尚不能独立识别现实中的沉默螺旋或个性化推荐效应（W1、W2）。 |
| Novelty and relation to prior work | 3 | 将逝后表征类别与策展反馈结合有问题意识；第 2–4 页已讨论数字哀悼、迷因及算法互动，但与已有数字哀悼研究相比，新的可检验知识边界尚需收紧。 |
| Significance | 3 | 对社交平台公共记忆和敏感内容治理有现实意义；目前是单事件、三平台混合样本，外推范围不明。 |
| Empirical or theoretical evidence | 2 | 第 13 页图 2 的兴趣制度 DTW 均值 22.0，随机 23.7，三 seed 范围重叠；第 14–15 页图展示模型内差异，但未来真实帖文输入、缺少外部行为验证和标注审计限制机制结论。 |
| Clarity | 3 | 正文区分真实、模拟、混合数据且承认三 seed 不支持显著性判断；第 16–17 页结论仍使用超出证据的因果和治理措辞，投稿版呈现也未完成。 |
| Reproducibility | 2 | 附录给出 Prompt、公式与伪代码，优于只述概念；但主稿未提供采样、标注协议、模型版本/推理参数、可审计数据或开放方案，难以独立复核真实基准与模拟。 |
| Limitations, ethics, and societal impact | 2 | 第 17 页承认未评价具体治理方案，但缺少处理逝者、可能可识别用户帖文和误判“恶意玩梗”的伦理/隐私说明（W4）。 |

## Venue fit

**ACM Web 2027：议题相关，现稿不宜直接投稿。** 官方研究征稿明确包含 Social Networks and Social Media、Responsible Web、Search/Recommendation 等方向，且要求首页清楚说明具体 Web 科学问题；仅把社交网络作为数据源不够。本文研究信息流与公共表达，具有实质 Web 关联；但缺少足以区分真实机制的设计与可靠数据基准。现有中文单栏 20 页稿也不符合其英文双栏、主文 8 页且含参考文献和可选附录总计不超过 12 页的长文格式；这是投稿前可修复的形式门槛。依据：[ACM Web 2027 Research Track CFP](https://www2027.thewebconf.org/research-track-papers/)。

**CSCW 2027+：社会计算问题契合，需更扎实的人与平台实践证据。** 官方指南的 Quantitative track 接纳大规模社会技术现象研究，Mixed Methods 或 Design/Theory 也可能容纳不同贡献形式；此稿的真实帖文时序与模拟框架更接近 Quantitative，但目前缺少能验证用户表达机制的经验资料及对平台差异、语境和转移性的讨论。按官方 2027+ 流程，会议展示以 PACM HCI/CSCW 或符合 CSCW 范围的 TOCHI 论文获接收为前提，并非直接向一个固定年份的会议长文截稿投稿。依据：[CSCW 2027+ papers](https://cscw.acm.org/2026/rolling.html)、[track guidelines](https://cscw.acm.org/2026/tracks.html)。以上契合判断不使用或暗示任何 venue 官方分数。

## Strengths

- 第 6–9 页明确将内容池、个体信息流、表达阈值和回流连成可运行过程；第 8 页公式及附录 F-1–F-3 可追踪决策的数值定义。
- 第 9、11 页区分真实观测、混合供给、Agent-only 供给及无 LLM 数值消融，避免把全部模拟结果直接称为真实观察。
- 九次正式运行完整；第 13 页图 2 披露三 seed 的点与范围，并正面指出兴趣制度终点过冲、与随机制度距离重叠。
- 第 14 页图 3a 以供给、曝光、发言、回流连续呈现，让读者能够检查“总曝光更高但该类 Agent 发言率更低”的模型内差异。

## Concerns

### W1 — 现实后段被持续输入，无法据拟合证明延迟增长机制

- Severity: major
- Paper pointer: 第 6–9 页研究设计；第 12–13 页图 2；附录 B 算法 2/5。
- Suggested reroute: experiment_config
- Why it matters: 论文的中心贡献是解释现实中玩梗为何延迟起爆，而非仅重播该事件的时序。若 W19–W22 的真实内容类别和到达时间已注入模型，拟合这些周次并非独立的机制检验。
- Evidence: 主稿第 6、9 页称每周按真实时间注入帖文，W19–W22 作为后段检查；附录 B 说明每周先注入真实帖再形成 Agent feed。`benchmark.csv` 中真实玩梗全环境份额由 W19 的 7.8% 升至 W20 的 29.8%、W22 的 60.3%。图 2 中兴趣与时序制度的终点超过现实，而兴趣与随机 DTW 范围重叠。这些事实不能单独区分“外生输入本来如此”与“内生反馈产生了延迟”。
- Suggested action: 预先规定最小对照：相同注入序列下的仅注入/无 Agent 回流轨迹，以及关闭反馈或将后段注入类别保持在前段分布的反事实；分别报告 Agent-only 与混合轨迹对转折周和份额的增量解释。若要主张现实预测，再使用真正未进入模拟信息流的事件/时段测试。
- Resolution evidence: 冻结的对照设计、配对运行及分离外生输入和 Agent 增量的周级结果，显示延迟增长在无后段真实玩梗输入时是否仍出现，以及与简单重播基线相比有多少增益。
- Score impact: 若机制在最小对照下仍成立，证据维度和总分可上调；若主要轨迹由注入决定，须将主张降为“给定真实输入的结构情景分析”。

### W2 — 三臂同时改动多项制度，个性化推荐效应不可单独识别

- Severity: major
- Paper pointer: 第 7 页制度定义、第 10 页表 1、第 13–14 页图 2/3；附录 B 算法 1、3、5。
- Suggested reroute: experiment_config
- Why it matters: 比较三套完整制度可以回答“这三种模拟环境何者产生何种轨迹”，但不能将差异专门归因于兴趣匹配，更不能由此得出具体推荐杠杆将推迟现实起爆的效应。
- Evidence: 附录 B 载明 random 从全部历史池抽样；chronological 用小时级行动时点前最新 10 帖；interest 独有生命周期/曝光饱和、官方帖置顶和 W13 悼念保底 5 槽，并以类型倾向加权抽样。因此候选池、置顶、事件周保底、行动粒度和排序逻辑同步变化。主稿第 10 页表 1 将这些差异概括为单一 Γ 因子；第 16–17 页进一步把制度差解释为兴趣推荐与可见性治理的作用。
- Suggested action: 先定义可识别的估计量。至少设置同一候选池、注入时点、行动粒度、置顶/保底规则下的“仅排序改变”配对比较；若研究对象本就是制度包，则更改贡献与结论为制度包的结构反事实，不单独声称个性化排序效应。
- Resolution evidence: 正交或最小匹配对照及其 Agent-only、曝光与构成变化；或明确限制在制度包层面的修订稿。
- Score impact: 有受控比较可提高技术可信度；只保留现有三臂时应显著收缩算法因果主张。

### W3 — 沉默螺旋与注意力衰减主要由规则赋予，缺少独立行为效度

- Severity: major
- Paper pointer: 第 5 页理论假设、第 8 页公式、第 11 页表 3、第 15 页图 4、第 16–17 页结论；附录 A.3。
- Suggested reroute: experiment_config
- Why it matters: 数值消融能够证明代码中的 D、R、B 项影响代码产出，却不足以证明现实用户因意见气候沉默、因同类曝光疲劳，或这些效应共同解释真实舆论变化。
- Evidence: 第 8 页的发帖判定是确定性的 `U>=a`，D 和 R 的具体函数在模型中预设；附录说明 LLM 不决定是否发帖。第 11 页表 3 及消融结果文件确认 100 seed 消融是无 LLM 数值代理。第 15 页图 4 对移除项的方向性响应清晰，但与现实个体行为没有独立比较。第 5 页用 58.9% 多帖作者内容全属同类和约 4% 跨类型表达支撑固定类型，稿中没有交代单帖作者不可观察转变的分母问题。
- Suggested action: 为关键函数设独立可证伪预测，例如同一作者在不同可见气候或累计曝光下的发言率变化；以留出的真实用户时序、可审计平台/用户行为资料或有设计的实验评估，并与无 D/R 的较简模型比较。至少将目前结果严格称为模型内必要性，不称作现实机制证实。
- Resolution evidence: 与参数标定数据分开的行为验证、误差和不确定性，以及简单替代模型的相同指标；若取不到资料，则清楚标注理论机制为假设。
- Score impact: 独立行为证据可明显提高科学贡献；若结果只重复设定，核心结论需改为条件性模拟示例。

### W4 — 真实基准的标注和平台构成缺乏可审计性

- Severity: major
- Paper pointer: 第 6 页数据构建、第 9 页基准定义、第 13 页图 2；主稿附录说明第 18 页。
- Suggested reroute: analysis
- Why it matters: “教育—悼念—玩梗”的真实三阶段轨迹是整个模拟的校准对象。类别边界、采集覆盖和平台权重若不稳定，DTW 与机制叙事都会随之变化。
- Evidence: 第 6 页报告小红书 33,328、抖音 16,602、微博 2,806 条，并称每帖有三列人工编码；主稿及冻结的 Prompt/伪代码附录未给出完整采集/去重规则、类别判定手册、复标或分歧处理、标注可信度，也未展示三平台各自的周度轨迹和独立作者口径。第 13 页图 2 的现实曲线将平台混合，不能排除采样或平台构成变化形成部分阶段趋势。此处是“所审材料未展示”，不等于原始审计不存在。
- Suggested action: 利用现有帖文与标注记录补齐采样流程、类别操作化及盲复核/分歧报告；分别计算平台内趋势、固定平台权重与独立作者口径，并评估类别误差对转折周的敏感性。若没有原始记录，应重新建立可审计样本。
- Resolution evidence: 数据字典、标注审计与分层趋势图，显示 W19–W22 转折在合理采样/编码口径下仍稳定。
- Score impact: 稳健且可审计的真实基准可提高证据与复现评分；若趋势只见于混合权重，主结论需收缩为样本特定现象。

### W5 — 治理与伦理措辞需要有责任主体的审定

- Severity: minor
- Paper pointer: 第 1–2 页研究问题、第 17–18 页治理讨论；未在主稿找到数据伦理声明。
- Suggested reroute: human_decision
- Why it matters: 对逝者及用户的敏感表达贴“恶意”标签并提出减少其可见性，牵涉批评、幽默、哀悼与言论表达边界。论文亦使用真实平台用户内容；投稿前需要有可追溯的隐私与机构审查判断。
- Evidence: 第 17 页一方面提出降低戏谑迷因曝光增益，另一方面承认未对具体治理方案作因果评估；主稿未陈述公开帖的存储、引用、去标识、同意或 IRB/豁免评估。ACM Web 2027 官方征稿明确要求遵守人类参与者政策并在适用时交代机构审查。
- Suggested action: 由研究负责人/机构判断伦理审查、数据使用与公开边界，明确“恶意”类别的规范依据；在论文中将治理建议限制为未实测的方向性假设。
- Resolution evidence: 有责任主体签署的伦理/数据治理判定、风险缓解说明，以及与实际实验范围一致的修订表述。
- Score impact: 解决后主要提升伦理与清晰度；若无法合法或合伦理使用数据，投稿不可继续。

## Questions and score-change conditions

1. W19–W22 的真实注入帖在何种程度上已经决定图 2 的转折？若无回流和无后段玩梗注入仍有增量起爆，将提高证据评分；若仅重播输入即可得到相似曲线，则维持 2 分并改写中心主张。
2. 将候选池、事件周保底、置顶和行动粒度统一之后，只改兴趣排序是否仍改变 Agent 发言与回流？若仍有稳定差异，可提高技术评分；若消失，则只能保留“制度包”解释。
3. 独立作者或逐帖复标后，三平台内是否仍显示同一 W19–W22 转折？若平台内与不同标注口径均稳健，可提高真实基准可信度；若由某平台采样波动主导，需要收缩结论。
4. 是否有独立于模型标定的用户表达/曝光证据支持 D、R 函数？有则可能提升总分；无则应把沉默螺旋与注意力衰减保留为显式假设，而非已识别的现实机制。

## Limitations, ethics, and reproducibility

本稿能够支持“在设定的反馈规则和给定真实输入下，不同模拟策展制度形成不同轨迹”，但目前不能支持对真实平台算法的因果归因，也未评价具体治理干预。三 seed 的正式运行足以展示若干模型路径，却不足以精确估计细小制度差异；数值代理的 100 seed Monte Carlo 区间只覆盖模拟随机性，不能当作现实总体不确定性。Prompt 和伪代码相对详尽，但论文仍应披露 LLM 版本/参数、数据访问边界与标注审计。真实用户帖文和死亡议题的使用与发布应有机构/负责人判断，避免把可被识别的悲伤或戏谑表达不必要地再传播。

## Overall recommendation

**项目本地总分 2/5（Reject / substantial revision），置信度 3/5。** 这是有潜力的社会计算研究问题，现稿的模型内部过程也较透明；然而最核心的“现实延迟增长机制”和“个性化推荐效应”仍受真实帖文持续注入与制度包混杂所限。真实标签基准也缺少充分审计。建议先补设计与分析，再选择目标 venue 的叙述结构。此评价不是 WWW 或 CSCW 的官方打分，也不是录用概率。

## Advisory reroute

**Primary: `experiment_config`（W1–W3）。** 决定性缺口在于机制主张所需的独立对照、可识别的排序变化及真实行为效度；单靠重写结论或继续汇总现有九次运行无法补出这些对照。**Secondary: `analysis`（W4）**，利用原始帖文和标注审计真实基准及平台分层；如资料不存在，再由后续负责者决定新采样。**Secondary: `human_decision`（W5）**，由可问责人员确定伦理、隐私和规范分类边界。**Secondary: `generate_paper`**，待证据边界确定后，收缩因果/治理措辞并满足目标 venue 的语言、版式与自足性要求。此路线仅为建议，不改变研究状态或自动触发实验。

## Machine-readable handoff

```json
{
  "schema": "agentsociety.paper-review.individual-handoff/v1",
  "review_path": "paper/reviews/generic-review-r3/reviewer-2.md",
  "round_id": "generic-r3",
  "reviewer_id": "R2",
  "overall_score": {"value": 2, "label": "Reject / substantial revision"},
  "confidence": {"value": 3, "label": "fairly confident"},
  "recommendation": "reject",
  "primary_reroute": "experiment_config",
  "secondary_reroutes": ["analysis", "human_decision", "generate_paper"],
  "blocking_issue_ids": ["W1", "W2", "W3", "W4"],
  "issues": [
    {"id": "W1", "severity": "major", "reroute": "experiment_config", "summary": "后段真实帖文持续输入，缺少分离外生注入与内生反馈的对照"},
    {"id": "W2", "severity": "major", "reroute": "experiment_config", "summary": "三种制度同时改变候选池、时间粒度和其他规则，排序效应不可单独识别"},
    {"id": "W3", "severity": "major", "reroute": "experiment_config", "summary": "D/R 数值消融缺少独立真实行为效度"},
    {"id": "W4", "severity": "major", "reroute": "analysis", "summary": "真实标注基准与跨平台趋势缺乏审计和稳健性分析"},
    {"id": "W5", "severity": "minor", "reroute": "human_decision", "summary": "治理分类及真实帖文使用需要可问责的伦理审定"}
  ]
}
```
