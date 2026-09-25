---
schema: agentsociety.paper-review.individual/v1
title: Internal Mock Review — Independent Reviewer R1
review_mode: author_side_internal_mock_individual
round_id: generic-r3
reviewer_id: R1
independence: isolated
input_manifest: paper/reviews/generic-review-r3/input-manifest.yaml
venue: generic
venue_edition: "project-local"
template_verified_at: "2026-09-25"
template_source: "none; project-local generic rubric"
score_scale_origin: project_local
reviewed_at: "2026-09-25T20:24:18+08:00"
reviewed_artifacts:
  - path: paper/manuscript/source/v3_20260915_2306_悼念退潮之后.pdf
    sha256: 48a4111f22b7b8952d591e2e61721a1382b73e7c4579e4f0da25558cd2aa7340
  - path: paper/manuscript/manuscript.accepted.md
    sha256: 6945443a48ed2382fb84990db1c71de8ee5f57a181b8d6591da3bf40693049b6
  - path: paper/appendices/附录Ⅰ和Ⅱ：Prompt模板与算法伪代码.md
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
  - generate_paper
  - human_decision
blocking_issue_ids:
  - W1
  - W2
  - W3
  - W4
---

# Internal Mock Review — Generic — R1

> This is one isolated author-side mock review. It is not an official venue review or acceptance prediction. All scores below use the project-local generic scale, not ACM Web or CSCW scores.

## Review target

本评审为 R1 对 `generic-r3` 冻结输入的独立意见。主稿是 `paper/manuscript/source/v3_20260915_2306_悼念退潮之后.pdf`（SHA-256：`48a4111f22b7b8952d591e2e61721a1382b73e7c4579e4f0da25558cd2aa7340`）；输入清单为 `paper/reviews/generic-review-r3/input-manifest.yaml`。我通读了 20 页 PDF 的共享全文提取和逐页文本，并检查了第 7、8、10、13、14、15 页的渲染图像；另对照了上述附录、实验设计、数值消融结果、DTW、基准与机制链数据，以及已接受文本中的相关段落。没有检查原始 52,716 条帖子、编码手册、标注员记录、完整运行日志或全部 LLM 生成文本；因此数据质量和代码执行细节的判断限于冻结材料所呈现的证据。

评分依据是 `.claude/skills/agentsociety-paper-review/references/venues/generic.md`（project-local）。会议契合度分别参照 [ACM Web 2027 Research Track 官方征稿](https://www2027.thewebconf.org/research-track-papers/)、[CSCW 2027 及以后投稿途径](https://cscw.acm.org/2026/rolling.html)和[CSCW 2027 及以后分轨指引](https://cscw.acm.org/2026/tracks.html)。这些官网规则用于投稿适配判断，不改变本地评分尺度。主稿提供问题、方法和主要结果，作为研究叙述基本可读；但附录被放在工作区路径，生成模型、提示、算法细节和伦理说明未整合为可独立审查的投稿包，故不是充分自足的会议投稿稿件。

## Artifact intake and limitations

共享 PDF intake 为 `pass`，20 页，`warnings: []`。我同时使用 `document.txt` 的完整文本与共享页面渲染；无警告页需要额外核查。图 2、图 3a/3b、图 4 的形状、图例与数值解释均核对了第 13–15 页渲染；公式及组间时间规则核对第 7–8 页渲染；表 1/2 核对第 10 页渲染。没有发现上述被引用元素不可读。PDF 文本层对公式有乱码，但页面渲染清楚；本评审的公式判断以第 8 页图像及冻结附录为准。

## Paper summary

论文用三平台编码帖文描绘一名公众人物逝后“教育—悼念—玩梗”的周级表征转移，再以 100 名固定类型智能体、11 周、三种信息流制度和每臂 3 个 seed 探索推荐环境、表达阈值、内容回流的组合效应。兴趣臂在五类构成轨迹上取得最低平均受限 DTW（22.0），但与随机臂的 seed 范围重叠；三臂都在 W20 左右出现玩梗增长。数值代理消融显示，删去常态锚点、意见气候或疲劳项会使模型产生不同轨迹。论文据此提出算法策展通过可见性改变既有群体的发声机会，并讨论数字哀悼治理。

## Claimed contributions

1. 描述真实帖子中逝后表征的时序变化，强调“被如何表达”而非仅看关注总量。
2. 提出推荐制度、固定类型用户、意见气候与注意力衰减组成的生成模型，并用三臂仿真比较轨迹。
3. 用数值消融解释模型部件的作用，提出以可见性调节作为治理线索。

## Venue scorecard

| Field（project-local 1–5） | Score | Evidence and rationale |
|---|---:|---|
| Technical soundness | 2 | 第 7–9 页模型定义明确，但真实后段帖文按周类型配额注入且智能体人口从含事后数据的 W12–W22 估计；这些设计不能单独识别“原有玩梗群体被算法放大”。第 7–8 页渲染和实验设计文件均核对。 |
| Novelty and relation to prior work | 3 | 将数字哀悼、迷因与推荐策展相连有潜力；第 2–4 页已列相关文献，但未在被审稿中精确界定相对现有算法审计和数字哀悼研究的可检验新发现。 |
| Significance | 3 | 人物逝后表征及平台治理有 Web 与 CSCW 意义；目前只有单一事件、三平台合并口径，第 6–7、16–18 页未证明机制可迁移。 |
| Empirical or theoretical evidence | 2 | 图 2（第 13 页）显示拟合重叠和 W22 端点偏差；图 3（第 14 页）是模型内部链；图 4（第 15 页）来自不调用 LLM 的数值代理。尚无现实曝光或行为验证。 |
| Clarity | 3 | 主线清楚且主动区分真实、模拟与混合数据（第 9、11–12 页）；第 7 页注入规模表述与实验文件、表 2 不一致，摘要和结论的因果措辞强于结果。 |
| Reproducibility | 2 | 有提示、伪代码、种子和派生 CSV，但主稿未提供投稿可用的数据许可、采样/编码协议、匿名代码包或模型版本与生成设置；第 18 页把细节指向本地工作区。 |
| Limitations, ethics, and societal impact | 2 | 第 17–18 页承认治理方案未被因果评估，但缺少公开帖子使用、用户隐私、逝者及亲属尊严、分类误伤及人工编码的伦理处理说明；不宜直接把“玩梗”一律视作恶意。 |

**单独的会议适配判断。** ACM Web 2027 的 Social Networks and Social Media、Responsible Web、Search/Recommendation 等轨道具有主题入口，且官网要求论文在首页说明所解决的 Web 研究挑战；当前模型确实研究 Web 上的可见性分配，但证据链和泛化不足以形成有说服力的 Web 因果结论。现稿为中文单栏 20 页，尚不符合该会议英文双栏、长文正文 8 页且总页数至多 12 页、前 8 页自足的正式格式要求，直接投稿还面临格式退稿风险。[ACM Web 2027 官方规则](https://www2027.thewebconf.org/research-track-papers/)。CSCW 2027 及以后不是按传统会议截止日直接投会议论文，而是经 PACM HCI/CSCW 或 ToCHI 接收后申请会议报告；其 Quantitative 轨可容纳社会技术现象的量化研究，Mixed Methods 需要真正相互补强的方法，Design/Theory 则要求更清晰的概念推进。当前仅有帖子统计与仿真，尚不足以将 LLM 仿真自动算作混合方法；真实用户如何理解、协商和实践数字哀悼也没有被直接研究，故对 CSCW 的社会互动贡献同样需要加强。[CSCW 投稿途径](https://cscw.acm.org/2026/rolling.html)；[CSCW 分轨指引](https://cscw.acm.org/2026/tracks.html)。

## Strengths

- 有具体的现实事件与 52,716 条人工编码帖子，能够提出不同于总量注意力研究的构成性问题（第 6、12、16 页）。
- 将真实、模拟和混合数据分开标示，并承认兴趣与随机臂 DTW 范围重叠、终点拟合失准（第 9、12–13 页）；这比仅报告一个最优拟合值更可信。
- 三臂使用匹配 seed 和注入样本，附录公开表达函数、词表推荐与小时级时序规则；图 3 将供给、曝光、发言率和内容回流放在同一链上，有助于提出可反驳的机制问题（第 7–8、10、14 页）。

## Concerns

### W1 — 现实后段轨迹进入仿真输入，且“既有群体”由事后数据定义

- Severity: major
- Paper pointer: 第 6–7 页“数据驱动的环境与智能体构建”；第 12–13 页图 2；`EXPERIMENT.md`“真实帖子注入”段（与第 7、10 页渲染核对）。
- Suggested reroute: experiment_config
- Why it matters: 核心论断是算法选择性放大已存在的玩梗群体并解释延迟起爆。若输入本身按现实每周类型份额携带 W19–W22 的玩梗浪潮，或智能体类型由这一时期的发帖者事后确定，就不能从拟合现象推知算法及预存群体机制。
- Evidence: 实验文件规定**每个 seed 的整个 W12–W22 窗口共预抽 250 帖**，每周按真实类型比例分层，W19–W22 注入数为 18/20/23/24；第 7 页却写“模型每周从真实数据中抽取约 250 条”，而第 10 页表 2 的终态池量减 Agent 帖通常为 250，与“全程 250”相符。智能体类型依 W12–W22 全窗发帖用户主导类型设定，既包括事件前也包括事件后的发帖。三种臂均在 W20 起爆，图 2（渲染第 13 页）并未分离外生输入相位与内生生成相位。这是证据事实；“输入泄漏削弱归因”是我的解释，并非指控数据造假。
- Suggested action: 预先设计能区分输入驱动与反馈驱动的最小反事实：固定事前可观察的人口构成，分别使用真实后段输入与不携带后段类别浪潮的匹配外生输入，报告两条件下 Agent-only 玩梗发言、供给和起爆时点；再评估“既有玩梗群体”的事前可识别性。更正每周/全程注入数。
- Resolution evidence: 可审计的事前人口估计、固定输入与去后段波形输入的配置和成对结果；若去波形后仍出现同方向的制度差异，才支持更强的内生放大解释。若没有，则把结论收窄为“给定现实输入时，模拟制度会改变回流量”。
- Score impact: 这是首要门槛；设计与结果能够排除该替代解释，可将技术与证据分数提高至少一档。若波形完全由注入和事后人口定义给出，整体分数可能降至 1。

### W2 — 干预混合多种制度差异，内部消融不能验证真实行为机制

- Severity: major
- Paper pointer: 第 7–8 页策展制度与 `U=B+R(D−B)`（均核对渲染）；第 11 页表 3；第 14–15 页图 3、图 4（均核对渲染）；附录 A.3 与 B.7。
- Suggested reroute: experiment_config
- Why it matters: 论文从模拟的制度差异进一步声称兴趣匹配、沉默螺旋、注意力衰减及“可见性治理”解释了现实平台。为达到这个推论，需知道结果对哪一项制度差异敏感，并证明表达函数不是只因规则设定而产生预期方向。
- Evidence: random 是全历史均抽，interest 有词表匹配及自身候选规则，chronological 按小时行动且同周较早生成帖可被后续小时看见，另两臂周末才回流。第 10 页表 1 的“组间仅改变信息流生成制度”作为完整制度比较可以成立，但不能隔离个性化排序、候选池、时间尺度或同周反馈。附录明确 LLM **不决定是否发言**；发言由数值阈值决定，类型词表约束文本。图 4 的 100-seed 消融是未运行 LLM 的数值代理；消融显示模型部件对模型输出的作用，不是现实用户沉默或注意力机制的独立证据。
- Suggested action: 明确论文只比较完整策展制度，或增加同候选池、同决策时刻、同回流节奏下的排序消融，以检验“个性化选择性曝光”这一更窄主张；最少给出一项独立微观验证（真实互动/发帖率与曝光代理关系，或透明的外部行为证据），并把数值消融标作模型内一致性检查。
- Resolution evidence: 与主实验配对的单因素制度对照、Agent-only 敏感性和不用于校准的行为效标；若仍无现实微观观察，则必须将结论限定为“在这些假设下的可能机制”。
- Score impact: 若真实行为层证据支持模型方向且干预可分解，证据与技术分数可上升。若只有数值模型内部结果，不能据此宣称识别了现实平台机制，整体建议保持拒稿。

### W3 — 现实基准与拟合评价缺少可审查的测量和泛化检验

- Severity: major
- Paper pointer: 第 5–6 页数据采集与人工编码；第 9 页评价协议；第 12–13 页图 2；第 16 页现实结论。
- Suggested reroute: analysis
- Why it matters: 52,716 条帖文是论文最强的现实证据，且是参数、输入与输出效标的共同来源。若平台覆盖、去重、编码或抽样误差未说明，不能把“帖文样本的类别份额”直接上升为全网公共表征或个人记忆。
- Evidence: 主稿给出各平台数量、20 条存疑数据剔除及类别数，但未见采集查询式、API/爬虫覆盖边界、转发/重复帖处理、人工编码手册、盲审复核及一致性/分歧记录；第 5 页以多帖作者 58.9%同类和约 4%明显跨类支持固定偏好，却未说明单帖用户对这一判断的影响。第 9 页称 W19–W22 为后段检查窗口；该窗口的类别构成同时按周进入外生注入。图 2（第 13 页）中兴趣 DTW 均值 22.0、随机 23.7，其 seed 范围重叠，W22 两个非随机臂达 83.9% 而现实为 63.0%，不能被“最低平均距离”遮蔽。
- Suggested action: 在已有原始数据上完成可审计的采集与编码质量报告，分平台、分周报告类别量与不确定性，区分帖文份额、触达份额和受众认知；用 Agent-only 与混合供给分别评价持出窗口，对 seed、参数和注入样本给出敏感性，而非只用 3-seed DTW 排序。
- Resolution evidence: 采集/排重流程、编码手册与复核记录、按平台与周的鲁棒曲线、持出期误差及输入敏感性；若材料无法取得，明确收窄外推范围。
- Score impact: 若测量与持出评估稳健，证据分可上升一档；若样本类别曲线对采样/编码选择高度敏感，现实贡献也需重估。

### W4 — 投稿形态及研究伦理材料尚不足以支撑目标会议判断

- Severity: major
- Paper pointer: 第 1 页摘要与研究问题，第 17–18 页治理讨论及附录指引；主稿中伦理、数据权利和复现披露 **not found in manuscript**。
- Suggested reroute: generate_paper
- Why it matters: ACM Web 2027 明确要求 Web 研究挑战在首页可见、英文双栏及 8 页自足正文，并提出涉及人的数据伦理及相关机构审查说明。CSCW 2027+ 为 PACM HCI/CSCW 或 ToCHI 论文渠道，重点是可迁移的社会技术知识。即使补齐实验，当前稿也无法直接当作符合这些目标的投稿包。
- Evidence: 现稿是中文单栏 20 页，主稿第 18 页仅写附录在工作区；没有数据取得方式、用户隐私/同意或伦理审查状态的明确交代。第 17 页提出降低“恶意地狱梗”曝光增益，却没有相应治理策略的实验或错误抑制代价评估，同时也在同页承认未做具体方案因果评估。官网规则分别见 [ACM Web](https://www2027.thewebconf.org/research-track-papers/)、[CSCW 投稿途径](https://cscw.acm.org/2026/rolling.html)与[CSCW 轨道](https://cscw.acm.org/2026/tracks.html)。
- Suggested action: 在证据范围确定后选择目标轨道，重写首页问题、贡献和局限，准备符合 venue 的英文投稿稿与匿名复现材料；由负责人核定公开社媒数据的伦理/隐私处理及许可边界，再如实披露。若治理是核心贡献，另需明确策略及效果/误伤指标；否则降为审慎讨论。
- Resolution evidence: 可独立阅读且符合相应渠道格式的稿件、数据与代码说明、PI/机构对伦理及公开范围的决定文档、与结果一致的治理表述。
- Score impact: 修正可消除格式退稿风险并改善清晰度与复现性，但**不能**单独解决 W1–W3；若伦理来源无法合规解释，投稿可行性下降。

## Questions and score-change conditions

1. **W1：**W19–W22 的注入帖类别与数量剥离后，Agent-only 玩梗在各臂何时、以多大幅度出现？若后段起爆仍存在、组间方向稳健，提高技术/证据分；若消失，保留描述性发现，降低因果主张及总体分。
2. **W1：**“既有玩梗群体”能否仅用去世前观测识别？若可以，并且人数比例与结果对事前口径稳健，可支持该构念；若不行，需要把它描述成“按事后发帖类型构造的潜在人群”，不能据此证明事件前群体规模。
3. **W2：**在固定候选池与回流时序后，纯排序/个性化改变的曝光与 Agent 发言差异还存在吗？若存在可将具体算法效应分数上调；若没有，应把效应归于完整制度组合。
4. **W3：**原始样本采集与人工编码可否复核，分平台曲线是否一致？稳健则提高现实证据分；若单个平台或采集规则主导现象，结论需限于该平台与样本。
5. **W4：**公开社媒数据、生成内容与治理建议的伦理和许可责任由谁审查？明确合规决定可移除投稿障碍；缺失则保持当前判断，发现不合规则需暂停投稿。

## Limitations, ethics, and reproducibility

单一人物与有限时间窗限制外推；帖子频率只能说明采到的公开表达，不能直接测量受众实际曝光、记忆、态度或逝者形象。100 名固定型智能体的发言由人为指定效用函数决定，LLM 主要生成正文，因而“LLM 多智能体”不应被用于暗示认知或行为是由 LLM 自发形成。3 个正式 seed 只刻画很小一部分模拟随机性；100-seed 代理消融的区间不能当作现实总体效应的置信区间。源码路径和提示是复现起点，仍需要可匿名获取的代码、数据字典、版本、模型调用设置、采集/编码协议，以及对无法共享的真实帖子说明可替代审计路径。

真实逝者与普通用户都是受影响主体。公开帖子仍可能有可识别、可搜索的文本；需要 PI/机构判断同意、隐私、引用和共享边界，并说明对逝者亲属、悼念者与戏谑表达者的潜在伤害。治理分析应保留表达自由、非恶意幽默与误分类成本；“可见性治理”在未做策略评估前只能是研究方向，不能被呈现为已证实可推迟现实起爆的政策效果。

## Overall recommendation

**项目本地总体 2/5，`reject`（需实质性修订），信心 3/5。** 这是有潜力的描述性发现与机制原型，但目前的设计将现实后段波形作为输入，人口定义也含事后信息，模型内机制消融又缺少现实行为验证，无法支撑“算法选择性放大既有群体导致现实表征转移”的中心因果结论。建议先解决 W1、W2 的可识别性，再完成 W3 的测量审计，最后按具体目标场域重写论文。当前不能把这篇 20 页中文稿作为 ACM Web 2027 正式长文直接提交，也尚未形成足以满足 CSCW 定量轨的稳健社会技术结论；两者均有主题契合空间，但需要不同的贡献重心。

## Advisory reroute

**Primary：`experiment_config`（W1、W2）。** 需要先改进对照设计与人口定义，否则在原设计上增加 seed 或润色图文仍不能排除输入波形与制度捆绑的解释。建议仅规划能直接回答这两个疑问的最小成对对照，再决定是否执行。

**Secondary 1：`analysis`（W3）。** 既有真实数据与运行产物需完成编码质量、平台异质性、持出评价及敏感性分析；仅修改文字无法生成这些证据。

**Secondary 2：`generate_paper`（W4 中的论断、结构和格式）。** 上游证据确认后，重写适合 Web 或 CSCW 的英文自足稿，去掉未测试的治理效果措辞。

**Secondary 3：`human_decision`（W4 中的伦理/共享边界）。** PI/机构须决定真实帖子、可识别文本、LLM 生成内容和伦理审查的披露及分享方式；这些责任判断不能由自动化改稿代替。以上均为建议，不改动研究流水线状态。

## Machine-readable handoff

```json
{
  "schema": "agentsociety.paper-review.individual-handoff/v1",
  "review_path": "paper/reviews/generic-review-r3/reviewer-1.md",
  "round_id": "generic-r3",
  "reviewer_id": "R1",
  "overall_score": {"value": 2, "label": "Reject / substantial revision"},
  "confidence": {"value": 3, "label": "fairly confident"},
  "recommendation": "reject",
  "primary_reroute": "experiment_config",
  "secondary_reroutes": ["analysis", "generate_paper", "human_decision"],
  "blocking_issue_ids": ["W1", "W2", "W3", "W4"],
  "issues": [
    {"id": "W1", "severity": "major", "reroute": "experiment_config", "summary": "Late observed meme trajectory and post-event population definition enter the simulation inputs"},
    {"id": "W2", "severity": "major", "reroute": "experiment_config", "summary": "Bundled curation regimes and internal numerical ablations do not validate a real behavioral mechanism"},
    {"id": "W3", "severity": "major", "reroute": "analysis", "summary": "Observed benchmark lacks auditable sampling, coding quality, and out-of-sample robustness"},
    {"id": "W4", "severity": "major", "reroute": "generate_paper", "summary": "Current manuscript and ethics disclosures are not ready for the target publication channels"}
  ]
}
```
