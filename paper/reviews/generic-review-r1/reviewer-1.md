---
schema: agentsociety.paper-review.individual/v1
title: Internal Mock Review — Independent Reviewer R1
review_mode: author_side_internal_mock_individual
round_id: generic-r1
reviewer_id: R1
independence: isolated
input_manifest: paper/reviews/generic-review-r1/input-manifest.yaml
venue: generic
venue_edition: "project-local"
template_verified_at: "project-local"
template_source: "none"
score_scale_origin: project_local
reviewed_at: "2026-09-15T20:51:19+08:00"
reviewed_artifacts:
  - path: paper/reviews/generic-review-r1/frozen/manuscript.docx
    sha256: 0720c2c402c8112cb7531fc53f13abf6f70eb673d6d08dfd6bab9740431464e5
  - path: paper/reviews/generic-review-r1/frozen/manuscript-accepted.md
    sha256: 7ec9a4407e62d3ca07700d9bf48b0dfdbeae92c7864baafd4bb85f97db06f011
  - path: paper/reviews/generic-review-r1/frozen/manuscript.md
    sha256: 002a1741535a74b4e34392ffd7ee895aa5495083c8fd74099063e1af567cd659
  - path: paper/reviews/generic-review-r1/frozen/manuscript.pdf
    sha256: bf57a8429702f0d198dafec879763d2987c084ccdcd289ed6c35ddbef77574b8
overall_score:
  value: 1
  label: Strong reject / foundational rework
confidence:
  value: 3
  label: fairly confident, but some related work or technical details were not fully checked
recommendation: strong_reject
primary_reroute: experiment_config
secondary_reroutes:
  - run_experiment
  - human_decision
  - generate_paper
blocking_issue_ids:
  - W1
  - W2
  - W3
  - W4
  - W5
  - W6
---

# Internal Mock Review — Generic — R1

> This is one isolated author-side mock review. It is not an official venue review or acceptance prediction.

## Review target

- 评审者与轮次：R1，`generic-r1`。
- 冻结输入清单：`paper/reviews/generic-review-r1/input-manifest.yaml`。
- 主稿：`paper/reviews/generic-review-r1/frozen/manuscript.docx`，SHA-256 为 `0720c2c402c8112cb7531fc53f13abf6f70eb673d6d08dfd6bab9740431464e5`。
- 实际检查材料：接受修订视图全文 `manuscript-accepted.md`、包含全部修订的审计文本 `manuscript.md`、DOCX 包结构及主文档设置、33 页冻结 PDF 与其全部逐页渲染。四项哈希均与 manifest 一致。
- 模板：Generic Research Venue，edition 为 `project-local`，采用 AgentSociety 项目本地 1–5 分量表，而非任何会议官方表单。
- 未提供且无法核查的材料：原始平台数据与抽样日志、编码手册和编码者一致性结果、仿真代码与环境、逐字 Prompt、配置与参数搜索记录、9 个 run 的原始日志/输出、按 seed 的完整指标、数据及伦理审批或豁免文件。
- 自包含性：否。摘要为空，图 1 与三个关键附录仍为占位符，核心决策规则和运行身份也缺乏可复核材料。

## Artifact intake and limitations

本轮源格式为 DOCX，因此 manifest 未提供 PDF intake 报告；我以接受修订文本作为主文本，并将全修订文本与 PDF 仅用于审计和版式核查。冻结 PDF 共 33 页，全部页面均已逐页视觉检查；表 1–4、图 4–6、公式、脚注、附录与参考文献均可辨认。没有因分辨率而无法读取的关键元素。

版式核查发现的限制本身具有实质性：PDF 第 1–23 页大面积显示彩色插入、删除、下划线与删除线，部分段落在“旧文—新文”之间重复；第 1 页摘要栏为空；第 9 页图 1 为“〔待制〕”；第 25 页附录 A–C 全为“〔待填〕”；第 25–33 页参考文献从 `[2]` 起排、脚注与文末条目并存，页面留白和断行异常。因而该 PDF 不能视为可直接提交的干净稿。

## Paper summary

论文以张雪峰逝后网络舆情为案例，使用抖音、微博和小红书的人工编码帖子构造现实周度表征轨迹，并建立 100 个固定类型智能体、W12–W22 共 11 周的仿真。平台策展制度 `Γ` 设为全历史随机、时序和兴趣三臂；表达效用 `U=B+R(D-B)` 将常态表达、同类内容可见份额和注意力衰减组合为发言阈值，LLM 仅在达到阈值后生成具体文本。论文以 3 个 seed/臂比较五类内容轨迹和 DTW 距离，并以 100 个数值推演 seed 对 B、D、R 做消融。作者据此主张：现实输入、平台可见性配置与既有用户类型的表达响应共同形成“教育—悼念—玩梗”的表征漂移，Interest 制度对现实轨迹拟合较好且在后段产生最强的玩梗型表达和内容回流。

## Claimed contributions

1. 将公众人物逝后的研究对象从“被记住多少”推进到“被如何表达”，连接数字哀悼、迷因传播与算法策展。
2. 构造 `Γ → F → U → X → 内容回流` 的平台—用户反馈循环，并用真实帖子和固定类型智能体作生成性推演。
3. 通过三种策展制度及 B/D/R 消融，区分平台可见性、意见气候、注意力衰减和内容回流的方向性作用。
4. 为平台治理提供“调整分发规则可能比单纯删除更接近机制”的方向性提示。

## Venue scorecard

| Field | Score | Evidence and rationale |
|-------|-------|------------------------|
| technical soundness | 1/5 | 第二章第 2 节、PDF 第 11–12 页把同类曝光份额直接写入发言效用；兴趣制度又按固定类型匹配内容。核心算法—表达链缺乏独立估计或验证，后段检查还继续注入现实结果轨迹。 |
| novelty and relation to prior work | 3/5 | 将逝后表征、迷因延迟增长与算法策展结合具有潜在新意，第一章覆盖三条相关文献脉络；但新意最终依赖尚未被有效识别的机制主张，且文末参考文献系统不完整。 |
| significance | 3/5 | 数字哀悼治理和公共人物表征是重要问题，单案例也具有启发性；然而现有证据不足以支持对真实平台机制或治理杠杆的判断。 |
| empirical or theoretical evidence | 1/5 | 三臂各仅 3 个 seed，DTW 区间重叠；现实帖子按真实周次持续注入；Table 2 的终态池数还与“同 seed 匹配注入”发生可计算的冲突。 |
| clarity | 2/5 | 变量、公式和三臂概念大体可追踪，但摘要为空、图 1 缺失、图文存在修订痕迹与重复，核心口径和 DTW 细节不足。 |
| reproducibility | 1/5 | 附录 A–C 明示待填，缺少逐字 Prompt、伪代码、代码/数据可得性、参数搜索与原始运行身份；目前无法复现。 |
| limitations, ethics, and societal impact | 1/5 | 第六章列出了 seed 数、单案例和量纲等局限，但没有对平台抓取、用户隐私、内容引用、在世家属伤害、治理误伤或“恶意玩梗”规范标签作伦理与权利审查。 |

## Strengths

1. 论文清楚区分了现实观测、模拟数据和混合内容池，并在多处主动收窄到“结构反事实比较”，没有把模型内差异直接宣称为真实平台算法的净因果效应。
2. 把表达数量、内容供给、曝光和内容回流分层记录是正确方向；图 5 对“总体曝光最高不等于同类群体激活最强”的观察值得进一步严谨检验。
3. 论文报告 Interest 与 Random 的 DTW 范围重叠、三 seed 不足以作显著性结论，并列出 W17–W18 输入缺口等边界，说明作者意识到模型验证的局限。

## Concerns

### W1 — 核心“算法—表达”机制被直接写入规则，尚未被独立识别

- Severity: fatal
- Paper pointer: 第二章（二）2（1）–（3），公式 `D_it` 与阈值规则，PDF 第 11–13 页；第四章 2–3，PDF 第 19–23 页
- Suggested reroute: experiment_config
- Why it matters: 论文的中心贡献是解释平台策展如何选择性激活既有群体，而不是仅展示一组预设方程的行为。若兴趣匹配和表达响应在构造上共享同一个“固定类型/同类份额”变量，则后续差异不能作为对该真实机制的独立证据。
- Evidence: Interest 制度按智能体固定类型与帖子倾向进行匹配；`D_it` 又被定义为同类内容可见份额相对人口基准的单调函数，并经确定性门槛决定是否发言。正文明确说明 LLM 只在门槛达到后生成文本，并不决定是否表达。去 D 消融使玩梗发言率下降，因此首先证明的是作者定义的 D 在作者定义的 U 中有效，而非现实用户真的遵循该响应函数。文稿没有给出独立曝光—表达微观数据、响应函数估计、外部参数或替代行为模型比较。
- Suggested action: 在新设计中将曝光分配、用户类型测量和表达响应的估计来源分离；用独立数据或预注册的外部依据估计/验证 `D`，并加入不依赖同类份额的空模型、不同函数形状和随机置换类型等最小对照。若无法获得行为层验证，应把中心结论改写为“一个构造性充分性示例”，而不是现实机制解释。
- Resolution evidence: 预先冻结的机制估计与验证方案、独立或交叉拟合的曝光—表达数据、替代/空模型比较，以及在不共享同一类型信号时仍能恢复关键相位和制度差异的结果。
- Score impact: 若独立验证支持该响应链，technical soundness 和 evidence 可从 1 提升到至少 3，并可重新考虑总体 2 分以上；若不支持，现有中心机制结论需基础性重构，因此当前为 fatal。

### W2 — “后段检查窗”仍被真实周度结果注入，生成性验证存在结果泄漏

- Severity: major
- Paper pointer: 第二章（二）1 与第二章（三），PDF 第 9–13 页；第四章 1、图 4，PDF 第 17–18 页
- Suggested reroute: experiment_config
- Why it matters: 论文把 W19–W22 称为后段检查窗口，并以复现 W20 玩梗起爆作为生成性证据。若仿真在这些周继续接收按真实到达顺序和类别构成抽取的帖子，则输入本身已经包含要预测的后段转折，DTW 接近和三臂共同起爆不能证明模型从早期条件生成了该现象。
- Evidence: 第二章称模型每周从真实数据抽取约 250 条帖子并保留到达顺序和类别构成，时间覆盖 W12–W22；同章又将 W19–W22称为“后段检查窗口”。第四章报告三种制度均复现 W20 起爆，并承认 W17–W18 注入池缺少玩梗内容会影响连续积累。这一承认反向说明现实注入类别直接控制关键结果。图 4 虽比较 Agent-only 供给，但 Agent 的信息流和表达效用仍由包含该后段现实结果的注入池驱动。
- Suggested action: 重新定义无结果泄漏的生成性检验，例如只使用转折前可获得的外生输入、对后段类别标签/构成遮蔽、做 leave-future-out 或跨事件验证；同时报告“固定现实注入本身”“无 Agent 回流”和“仅 Agent 内生供给”等基线，以量化 W20 转折中有多少来自外部回放。
- Resolution evidence: 冻结的时间切分与输入可用性规则、不会编码 W19–W22 目标构成的评估输入，以及模型在该条件下的后段预测/生成结果和基线分解。
- Score impact: 解决该问题是把“轨迹回放”提升为“生成性验证”的必要条件；单独修复不足以消除 W1，但可使 empirical evidence 从 1 上调。

### W3 — Table 2 暗示配对注入身份被破坏，且三臂差异没有可审计的不确定性证据

- Severity: major
- Paper pointer: 第三章 1–2、Table 1–2，PDF 第 13–15 页；第四章 1、图 4e，PDF 第 17–18 页
- Suggested reroute: run_experiment
- Why it matters: 三臂反事实依赖“同 seed 跨制度匹配注入样本”。只要任一配对 run 的现实输入不同，制度差异就和输入差异混杂；仅凭 3 个 seed 的均值/min–max 也不足以支撑 Interest 的相对优势。
- Evidence: Table 2 中 Random-s0 为 193 个 Agent 帖、终态池 443，Chronological-s0 为 212/462，均对应 250 条非 Agent 帖；Interest-s0 为 233/500，却对应 267 条，和同一 s0 另外两臂不一致。s1、s2 各行均恰好相差 250。正文未解释这 17 条差异，也未提供逐周注入哈希。DTW 方面，Interest 为 19.6–24.3，Random 为 19.9–26.9，明显重叠；未报告配对差值、置信区间或任何稳健性统计。
- Suggested action: 先用原始 run 日志逐周核对每个 seed 的注入条目、时间戳和哈希；若 s0 实际不匹配，应按冻结配置补跑受影响单元。随后基于配对 seed 报告制度差值和不确定性，并增加足以判断方向稳定性的重复数，而不是据 3 个均值选择“主要拟合结果”。
- Resolution evidence: 九个 run 的输入身份清单、逐周哈希、完整性日志；必要时完成的替代 run；按预先指定 estimand 给出的配对差值、区间与方向稳定性。
- Score impact: 若 17 条差异只是表格错误且哈希证明严格配对，该部分可降为展示问题；若确有输入不匹配，当前三臂制度比较失效，须在有效运行完成前维持拒绝。

### W4 — 现实数据的抽样、编码和“稳定类型”测量不可审计

- Severity: major
- Paper pointer: 摘要与第二章（二）1，PDF 第 1、9–10 页；not found in manuscript: 抓取方案、编码手册、编码者一致性、用户去重与平台分层结果
- Suggested reroute: experiment_config
- Why it matters: 现实周度轨迹、100 人类型比例、固定类型假设和所有仿真输入均来自这套标注数据。若抽样覆盖、重复帖、跨平台作者身份、编码误差或用户类型计算不可靠，中心现象与初始化都可能是测量产物。
- Evidence: 文稿只给出平台总量、三列人工编码字段和剔除 20 条存疑数据；未说明检索词/入口、抓取覆盖率、时区、去重规则、视频/图片如何编码、编码者人数、训练、盲法、一致性、分歧裁决及每周每平台误差。样本总量在摘要为 52,737、方法为 52,736、分析样本为 52,716。固定类型依据一处写“约 96% 用户只属一类、4% 转换”，理论框架又写“多帖作者中 58.9% 的全部评论属同一类型”，两者分母及计算关系未解释。
- Suggested action: 在设计层冻结数据生成与测量协议：完整抽样框、去重和作者聚合规则、跨平台分层、编码本体与示例、至少双人重叠编码及一致性/混淆矩阵，并对类型比例、现实周曲线和关键结论做编码误差敏感性分析。
- Resolution evidence: 可审计的数据字典和抽样日志、编码者与裁决记录、可靠性统计、各口径精确分母，以及对 52,737/52,736/52,716 和 58.9%/96% 的一致解释。
- Score impact: 若测量可靠且结论对编码误差稳健，现实基准可信度可明显提高；若无这些记录，论文无法证明中心现象和人群构成不是采样/标注偏差。

### W5 — 涉及真实用户和近期死亡事件，却没有伦理、隐私与治理误伤评估

- Severity: major
- Paper pointer: 研究问题与数据构建，PDF 第 1、9–10 页；第五章 3 与第六章 2，PDF 第 24–25 页；not found in manuscript: 伦理审批/豁免、隐私保护、内容引用与数据共享风险
- Suggested reroute: human_decision
- Why it matters: 研究处理跨平台真实用户关于死亡、悼念和“地狱梗”的内容，并提出压低某类表达的治理建议。是否可抓取、如何去标识、能否共享原帖、如何避免伤害家属或误伤讽刺/批评表达，涉及不可由自动流程代替的权利与价值判断。
- Evidence: 第六章局限只讨论 seed、量纲、黑箱和外推，没有说明公开数据是否经过伦理审查或豁免、平台条款、账号/文本去标识、敏感原文进入 LLM 的边界、数据保留与访问控制。论文反复使用“恶意玩梗”“精准遏制与正向引导”，但没有给出伤害判据、误报代价、申诉机制或与合法表达之间的权衡。
- Suggested action: 由 PI/机构作出并记录伦理和数据治理决定；明确数据合法来源、最小化、去标识、LLM 数据处理、引用与共享规则；将“恶意”改为可操作且可审计的伤害标准，并分析治理误伤和表达权衡。
- Resolution evidence: 伦理审批/豁免或正式自评记录、数据治理与风险缓解方案、可审计的伤害标签定义、误报/漏报及受影响主体分析。
- Score impact: 这是进入任何真实数据发表与治理讨论的前置条件；缺失时 limitations/ethics 保持 1，解决后才可能上调。

### W6 — 冻结稿不是完整、干净、可复现的提交件

- Severity: major
- Paper pointer: 摘要，PDF 第 1 页；图 1，PDF 第 9 页；附录 A–C，PDF 第 25 页；全稿修订痕迹，PDF 第 1–23 页；参考文献，PDF 第 25–33 页
- Suggested reroute: generate_paper
- Why it matters: 即使上游科学问题被修复，当前文件也无法作为完整投稿接受评审；摘要、理论图、复现材料和干净版式均是提交完整性的一部分。
- Evidence: “摘要：”后无任何摘要；图 1 标注“〔待制〕”；Prompt、伪代码、代码与数据可得性全部标注“〔待填〕”。PDF 显示 track changes，包含大量重复段落、删除线和彩色修订；DOCX 设置中启用了 `trackRevisions`。参考文献从 `[2]` 起，正文脚注与文末列表的编号/条目不一致，并出现 DOI 以 Markdown 链接原样排版和异常大行距。
- Suggested action: 在上游设计、运行和伦理问题有结论后，接受或拒绝全部修订并重新生成干净稿；补齐结构化摘要、图 1、逐字 Prompt、完整伪代码、版本化代码/数据声明；统一引文系统并逐项核对正文引用和文末条目。
- Resolution evidence: 无可见修订的最终 PDF、非空摘要和实际图 1、完整附录与可访问性声明、通过引用一致性检查的参考文献，以及所有图表在最终页上的可读性核查。
- Score impact: 单独清理版式不会修复 W1–W5，因此总体分不会自动提高；但它是任何重新送审的必要条件，并可使 clarity/reproducibility 各上调至少 1 档。

## Questions and score-change conditions

1. 是否存在与本次仿真独立的个体级“所见信息流—后续发言”数据，用于估计或验证 `D_it` 和门槛？若有且预注册/交叉拟合结果支持同一方向，我会考虑把 technical soundness 从 1 提至 3；若没有，中心主张应降为构造性机制示例。
2. W19–W22 的真实注入中，类别构成、文本和时间戳哪些在运行前可视为外生信息？若目标周的类别轨迹已直接进入信息流，当前 DTW 与相位复现不能提高分数；若能给出无泄漏的冻结证明及替代评估，evidence 可上调。
3. Table 2 中 Interest-s0 的 500−233=267 条非 Agent 内容来自何处？若逐周哈希证明三臂 s0 实际完全一致且只是表格错误，W3 可降级；若不一致，需有效补跑后才能评价制度差异。
4. 52,737、52,736、52,716 与 58.9%、96%、4% 的精确分母、去重和作者聚合规则是什么？只有在完整编码协议和可靠性统计支持这些口径时，现实基准才可视为可信。
5. 数据抓取、去标识、向 LLM 提供原帖和后续共享分别经过何种伦理/法律审查？缺乏可问责决定时，我不会上调 ethics 分；获得正式决定并补足风险缓解后才可能改善。
6. 若作者仅清理摘要、占位符和修订痕迹而不修复 W1–W5，总体仍为 1；若 W1–W4 均有可审计的新证据、W5 完成问责判断且形成完整干净稿，可重新评估至 2–3 区间。

## Limitations, ethics, and reproducibility

作者对小 seed、注入重采样、W17–W18 玩梗输入缺口、单案例、量纲差异、LLM 黑箱和模型内识别边界的披露是充分讨论的良好起点。但遗漏更根本：后段真实输入泄漏、行为函数和兴趣匹配共享构念、配对注入身份矛盾、编码可靠性与数据伦理。这些不是增加一段“局限”即可消解的问题。

复现性目前不合格。附录明确缺少逐字 Prompt、主循环伪代码和代码/数据路径；正文也未提供 LLM 模型版本、采样参数、失败/重试规则、词表全文、参数搜索边界、DTW 的约束窗/归一化/权重/距离定义，以及 100-seed “数值推演”与正式 LLM 运行的代码差异。上述信息需与版本化运行身份和原始日志绑定。

伦理方面，单纯称数据“公开”并不足以免除对脆弱语境、可搜索原文、账号重识别、平台条款、近期死亡相关伤害及治理误伤的评估。尤其“精准遏制恶意玩梗”把规范标签写入研究目标，却没有操作化伤害或建立申诉与比例原则，必须由具备责任主体的人作出明确决定。

## Overall recommendation

**Overall score: 1/5 — Strong reject / foundational rework (`strong_reject`).**

选题重要，平台—用户循环的分层框架也有潜力；但当前稿的中心机制在模型结构中被预设，所谓后段验证继续接收目标周现实轨迹，关键 run 的输入身份又出现内部矛盾。再加上数据测量不可审计、伦理治理缺位和稿件本身未完成，现有结果无法支撑“平台算法与用户互动解释现实逝后表征漂移”的中心结论。

**Confidence: 3/5.** 我已完整读取主文、审计修订、公式、表格、脚注、附录和参考文献，并视觉检查全部 33 页，因此对稿内证据缺口较有把握；但 manifest 未授权原始数据、代码、运行日志和外部文献核验，Table 2 的异常究竟是排版错误还是实际运行污染仍无法判定，故不评为 4 或 5。

## Advisory reroute

- Primary reroute: `experiment_config`，决定性问题为 W1、W2、W4。必须先重构机制识别、无泄漏验证和测量审计；仅在分析或写作阶段修辞收窄，无法让现有设计独立检验中心机制。
- Secondary reroute 1: `run_experiment`，对应 W3。只有在逐周输入身份核验后，才知道是否需要补跑受污染单元；若配对不成立，现有九 run 不能继续作为三臂证据。
- Secondary reroute 2: `human_decision`，对应 W5。真实用户数据、近期死亡语境、LLM 数据处理和表达治理涉及问责性伦理/法律判断，不应自动执行。
- Secondary reroute 3: `generate_paper`，对应 W6。上游证据与伦理决定完成后，再补齐摘要、图、附录、引文并输出无修订痕迹的干净稿；现在先做版式清理不足以改变科学结论。

以上均为建议，不修改 `.agentsociety/progress.json`，也不触发任何后续工作。

## Machine-readable handoff

```json
{
  "schema": "agentsociety.paper-review.individual-handoff/v1",
  "review_path": "paper/reviews/generic-review-r1/reviewer-1.md",
  "round_id": "generic-r1",
  "reviewer_id": "R1",
  "overall_score": {"value": 1, "label": "Strong reject / foundational rework"},
  "confidence": {"value": 3, "label": "fairly confident, but some related work or technical details were not fully checked"},
  "recommendation": "strong_reject",
  "primary_reroute": "experiment_config",
  "secondary_reroutes": ["run_experiment", "human_decision", "generate_paper"],
  "blocking_issue_ids": ["W1", "W2", "W3", "W4", "W5", "W6"],
  "issues": [
    {
      "id": "W1",
      "severity": "fatal",
      "reroute": "experiment_config",
      "summary": "Core algorithm-to-expression mechanism is directly encoded and lacks independent validation"
    },
    {
      "id": "W2",
      "severity": "major",
      "reroute": "experiment_config",
      "summary": "Real weekly outcome trajectory leaks into the claimed late holdout through continued post injection"
    },
    {
      "id": "W3",
      "severity": "major",
      "reroute": "run_experiment",
      "summary": "Table 2 contradicts matched-input identity for Interest-s0 and regime uncertainty is not auditable"
    },
    {
      "id": "W4",
      "severity": "major",
      "reroute": "experiment_config",
      "summary": "Sampling, coding reliability, and stable-user-type measurement are not auditable"
    },
    {
      "id": "W5",
      "severity": "major",
      "reroute": "human_decision",
      "summary": "Ethics, privacy, and governance false-positive risks are not assessed"
    },
    {
      "id": "W6",
      "severity": "major",
      "reroute": "generate_paper",
      "summary": "Frozen submission has a blank abstract, placeholders, visible tracked changes, and incomplete references"
    }
  ]
}
```
