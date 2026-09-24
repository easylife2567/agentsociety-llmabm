---
schema: agentsociety.paper-review.individual/v1
title: Internal Mock Review — Independent Reviewer R2
review_mode: author_side_internal_mock_individual
round_id: generic-r1
reviewer_id: R2
independence: isolated
input_manifest: paper/reviews/generic-review-r1/input-manifest.yaml
venue: generic
venue_edition: "project-local"
template_verified_at: "not_applicable"
template_source: "none; AgentSociety project-local rubric"
score_scale_origin: project_local
reviewed_at: "2026-09-15T20:50:58+08:00"
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
  value: 4
  label: confident, with limited residual uncertainty
recommendation: strong_reject
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
  - W5
  - W6
  - W7
---

# Internal Mock Review — Generic — R2

> This is one isolated author-side mock review. It is not an official venue review or acceptance prediction.

## Review target

- Reviewer: R2；round: `generic-r1`。
- 冻结输入清单：`paper/reviews/generic-review-r1/input-manifest.yaml`。
- 主审稿件：`paper/reviews/generic-review-r1/frozen/manuscript.docx`（SHA-256：`0720c2c402c8112cb7531fc53f13abf6f70eb673d6d08dfd6bab9740431464e5`）；以接受修订后的 `manuscript-accepted.md` 为主文本，以 `manuscript.md` 为修订审计文本，并逐页检查了 `manuscript.pdf` 的33页冻结版面。
- 采用 generic、`project-local` 的 AgentSociety 项目内量表；该量表没有外部会议表单来源。
- 清单未授权任何原始数据、编码手册、运行日志、配置、Prompt、代码或分析产物，因此本文中的数据质量、参数来源和计算结果只能依据稿件陈述判断，不能独立复算。
- 主文不自足：核心 Prompt、伪代码、代码与数据获取方式均仍是占位符，若干关键参数与标定流程也没有给出。

## Artifact intake and limitations

冻结源格式为 DOCX，因此不存在 PDF intake 报告字段；PDF仅作为同一冻结 DOCX 的33页版面渲染使用。我通读了接受修订文本及全部修订审计文本，并检查了全部33页渲染，重点放大核对了第1、8—18、20—23、26—33页中的标题、公式、表1—4、图4—6、脚注、附录和参考文献。图表本身可辨识，但冻结版显示大量彩色插入/删除痕迹和修订线；第9页图1仍为“〔待制〕”，第26页三个附录均为“〔待填〕”。没有发现可供核验的图2或图3，也没有独立的结果表支撑图中全部数值。由于没有底层证据文件，本评审对“稿件是否已经提供足够证据”的判断置信度高，对具体数值是否可由原始产物复现则无法判断。

## Paper summary

稿件以张雪峰逝后跨平台舆情为单案例，先用抖音、微博和小红书的人工分类帖文描述“教育—悼念—玩梗”的周级表征转移，再构建100个固定类型 Agent 的 LLM 多智能体模型。模型将全历史随机、时序和兴趣三种信息流制度作为 Γ，通过常态表达效用 B、意见气候 D 和注意力余量 R 组成的阈值模型 U 决定是否发声，并把生成内容回流公共内容池。论文用每制度3个 seed 的9次正式运行、受限多变量 DTW，以及100个配对 seed 的数值代理消融来论证平台策展与用户表达共同塑造表征漂移。

## Claimed contributions

1. 将公众人物逝后研究从“被记住多少”推进到“被如何表征”，并提出平台策展—用户表达的反馈循环。
2. 用真实帖文构造外部输入、固定用户类型与现实轨迹基准，使 LLM 多智能体仿真具有经验锚点。
3. 通过三种策展制度比较和 B/D/R 消融，解释悼念退潮、玩梗二次增长及差异化群体激活。
4. 将分发规则识别为潜在治理杠杆，但声明不把模型内差异直接等同于真实平台算法的净因果效应。

## Venue scorecard

| Field | Score | Evidence and rationale |
|-------|-------|------------------------|
| technical soundness | 1/5 | 第10—13页的机制可形式化，但后段真实类别轨迹被持续注入、输出类别又由固定 Agent 类型赋值，令主要“生成/机制”证据存在结果泄漏与构念循环。 |
| novelty and relation to prior work | 3/5 | “逝后表征转移×算法策展×LLM-ABM”的组合有潜在新意；但第2—9页相关工作没有建立与最接近的生成式 ABM、推荐系统仿真和校准方法的直接差异，部分理论仅被用作参数叙事。 |
| significance | 4/5 | 数字哀悼、迷因化和推荐治理的交叉问题重要，真实案例与机制化表达具有明显传播学价值。 |
| empirical or theoretical evidence | 1/5 | 第17—23页主要结果只有3个正式 seed，DTW区间重叠且无推断；更根本的是 W19—W22“验证”结果在每周真实注入中已进入模型输入。 |
| clarity | 2/5 | 章节骨架和公式可读，但第1页摘要为空，第9页图1缺失，第20—22页修订文本重复/交叠，33页冻结版仍显示大规模修订痕迹。 |
| reproducibility | 1/5 | 第26页附录 A—C 全部待填；α_D、k、s_i、λ_i、scale、词表、抽样与标定程序等关键要素不完整，且没有代码、数据或运行日志。 |
| limitations, ethics, and societal impact | 2/5 | 第25—26页对3 seeds、单案例、黑箱和非现实净因果效应有诚实限制，但没有交代公开帖文抓取的合规性、用户隐私处理、对逝者/家属的风险或生成地狱梗内容的治理。 |

## Strengths

- 研究问题重要且现象具体。稿件把“总关注量”与“可见表征构成”区分开，这一转向有理论价值。
- 第10—13页清楚给出了 Γ、U、B、D、R 的作用位置，第13—17页也明确区分真实、模拟与混合数据；这种口径意识优于把所有仿真输出直接称为现实证据。
- 三臂使用同 seed 匹配注入样本，论文也主动承认每臂3个 seed、注入抽样和随机过程混杂、终点拟合偏差及不能外推真实平台净因果效应。
- 图4—6试图同时展示轨迹、机制链和消融，而不是只报告单一终点；兴趣制度并非在所有指标上“最好”这一反常结果也被如实呈现。

## Concerns

### W1 — 后段真实结果被作为输入，所谓“留出复现”存在目标泄漏

- Severity: fatal
- Paper pointer: Section 2.1, pages 9–10; Section 2.3, page 13; Section 4.1, pages 17–18, Figure 4
- Suggested reroute: experiment_config
- Why it matters: “模型生成了现实相近的教育—悼念—玩梗转移”是中央证据，也是后续机制解释成立的前提；若验证期的真实结果已经进入刺激流，DTW接近和W20起爆不能证明模型具有生成解释力。
- Evidence: 稿件明确称模型在W12—W22“每周从真实数据中抽取约250条帖文作为外部输入，并保留其到达顺序和类别构成”，同时把W19—W22称为后段检查窗口。现实中W19起玩梗回升、W20—W22快速增长，因此Agent-only输出虽然与真实统计分开计数，却在产生前已经看到了同周包含目标类别结构的真实帖子。三种制度均复现W20相位与这一共同外生驱动完全相容。
- Suggested action: 预注册一个结果盲的验证设计，例如只允许使用W19前历史、对W19—W22输入做类别标签/正文内容遮蔽或构造保持总量与到达时间但不携带玩梗结局的对照输入；同时加入无后段真实注入的反馈自维持臂，并在相同候选池上比较制度。
- Resolution evidence: 一组在W19—W22结果信息未进入Agent观察或推荐打分前生成的正式运行及日志，仍能在独立人工编码输出中复现转折周与构成替代，并报告相对无泄漏基线的误差和不确定性。
- Score impact: 若泄漏被确认而未重做，整体分维持1；若结果盲验证仍支持核心轨迹，技术与证据维度可升至2—3，并可能把总分提高到2或3。

### W2 — 结果类别由Agent身份预先赋值，构念循环替代了语义涌现

- Severity: fatal
- Paper pointer: Section 2.1, pages 10–11; Section 2.2(3), pages 12–13; Section 2.3, page 13; Figure 5b, page 21
- Suggested reroute: experiment_config
- Why it matters: 论文声称LLM内容与公共表征从互动中“涌现”，但主要结果中的Agent-only类别实际上由固定人设直接决定；这不能检验表达是否发生语义转型，也无法说明LLM生成相对简单计数模型增加了什么证据。
- Evidence: 五类Agent在全程固定；生成Prompt强制相应类型词表；发布后即使正文复核类型与固定类型不一致，“内容池中的结构类型仍由固定类型确定”。兴趣推荐又使用同一套正文类型倾向匹配固定人设，D再根据同类可见份额提高发言概率。因而“看到同类内容—固定类型Agent发声—产出被记为同类”在测量定义上闭环，图5b和图6的类别供给很大程度是哪些固定群体越过阈值的重标记，而非对生成文本表征的独立观测。
- Suggested action: 将结果测量从Agent身份解耦：允许生成文本跨类表达，冻结生成后由不知道实验臂和Agent类型的独立人工编码或外部分类器判类；报告身份—文本错配矩阵，并用该独立类别重做所有轨迹和制度效应。若研究只打算检验固定群体发言份额，应收窄主张并移除“语义涌现/形象生成”的表述。
- Resolution evidence: 盲法独立编码的生成文本、可靠性指标及基于文本类别而非身份标签重算的图4—6；关键效应在允许错配并控制词表提示后仍存在。
- Score impact: 不解耦则中央“表征涌现”结论不能成立，总分维持1；解耦后若结果稳健，可将技术与证据维度至少提高一档。

### W3 — 三臂同时改变候选池、时间结构和个性化，不能把差异归因于推荐机制本身

- Severity: major
- Paper pointer: Section 2.2(1), page 11; Table 1, page 14; Section 4.2, pages 19–22, Figures 5a–5b; Section 5.3, page 25
- Suggested reroute: experiment_config
- Why it matters: 稿件从制度差异进一步推到“调整推荐逻辑是治理杠杆”；但Random、Chronological和Interest并非只替换排序函数，候选可得性、内容年龄、行动批次和个性化同时变化，无法知道哪个组件造成差异。
- Evidence: Random从截至当期的全历史池抽样，Chronological使用行动前最新帖且运行693个小时批次，Interest按类型倾向比例抽样；前两者与Interest面对的有效候选分布和内容寿命不同。论文虽然在局限中把它们称为完整策展制度并避免真实净因果措辞，但摘要、创新点和治理讨论仍多次归因于“算法推荐机制”。
- Suggested action: 新增共享候选池、共享到达时钟和共享内容寿命的正交比较，只改变排序/匹配项；如要研究完整制度，则把组件做最小析因或逐项消融，并将治理结论限定到被识别的组件。
- Resolution evidence: 候选集合逐决策一致的日志、组件级处理定义以及排序/匹配开关的估计；或明确证据仅支持“完整制度组合不同”并删除组件级与治理因果主张。
- Score impact: 修复归因可把技术可靠性从1提高到2；仅改措辞可缓解过度主张，但不能弥补W1和W2。

### W4 — 正式运行重复不足且参数选择不可审计，拟合优势不稳定

- Severity: major
- Paper pointer: Section 2.2(2), pages 11–12; Section 2.3, page 13; Tables 1–3, pages 14–16; Section 4.1, pages 17–18
- Suggested reroute: experiment_config
- Why it matters: Interest的平均DTW 22.0相对Random 23.7是主要制度证据之一，但每臂仅3个seed、范围高度重叠，且seed同时改变模型随机性和注入样本；关键参数又在W13—W18约束，选择自由度无法审计，容易把偶然或手工调参误作机制支持。
- Evidence: Interest范围19.6—24.3、Random范围19.9—26.9；论文明确不做显著性判断。α_D、k、s_i分布、λ_i、scale及参数搜索空间/损失函数未给出；门槛0.95来自“数值扫描”，B由数据映射，后续又报告100-seed数值代理消融，但正式LLM制度比较仍只有3个seed，且数值代理是否忠实复现LLM回流没有验证。
- Suggested action: 在配置阶段冻结完整参数表、搜索空间、训练目标、停止规则和seed分解方案；分别固定注入样本与模型随机性，按预先设定的精度或功效标准扩充正式重复，并加入参数敏感性与代理—LLM一致性检查。
- Resolution evidence: 可审计的训练/验证分离记录、完整配置哈希、足量独立重复、配对制度对比区间，以及核心排序在合理参数邻域与不同注入样本下保持稳定。
- Score impact: 若兴趣优势在稳健重复下消失，应删除相应贡献；若保持且不确定性收窄，可把证据与复现维度提高到2—3。

### W5 — 真实基准与人设比例的测量质量没有建立

- Severity: major
- Paper pointer: opening pages 1 and 9–10; Section 2.1, pages 9–10; not found in manuscript: sampling query, deduplication, coder protocol, intercoder reliability, annotation audit
- Suggested reroute: analysis
- Why it matters: 现实轨迹、Agent人口比例、B基线和模型拟合目标都来自同一人工分类数据；若抓取覆盖或编码误差未知，整个校准目标和“真实存在的表征转移”都会失去可信基准。
- Evidence: 稿件只报告平台数量、三列人工编码和剔除20条存疑数据，没有检索词、API/爬虫覆盖、去重、账号/机器人处理、编码员人数、盲法、类别定义、混淆矩阵或一致性。数量也不一致：第1页称52,737条，方法称原始52,736条，三平台数量之和为52,736条，分析样本为52,716条。“多帖作者58.9%全部评论同类”与“约96%用户类型不转换”之间的口径关系也未解释。
- Suggested action: 对现有数据完成可复核的样本流图、平台分层覆盖说明和编码审计；由至少两名独立编码者对分层样本复编码，报告类别级一致性与对周级曲线/Agent比例的误差传播或敏感性，并统一所有样本数。
- Resolution evidence: 数据字典、纳排与去重日志、编码手册、盲法复编码结果、可靠性统计及在替代编码/排除规则下仍成立的周级转移。
- Score impact: 若可靠性不足或轨迹对规则敏感，现实锚点不成立，总分仍为1；若审计通过，可把经验依据提高一档。

### W6 — 当前稿件缺失复现所需的核心材料，而非仅有格式瑕疵

- Severity: major
- Paper pointer: Section 2.2, pages 11–13; Appendix A–C, page 26; not found in manuscript: full prompts, vocabularies, pseudocode, software/model versions, code/data link
- Suggested reroute: generate_paper
- Why it matters: 审稿人无法判断实现是否与文字模型一致，也无法复现任何结果；这直接影响方法可信度而不只是可选开放科学加分。
- Evidence: 附录A、B、C分别保留“Prompt逐字全文待填”“主循环伪代码待填”“代码仓库链接、数据获取方式与限制待填”。正文没有LLM供应商/模型版本、解码参数、失败重试、运行日期、费用、完整词表、参数表或环境实现细节。
- Suggested action: 若这些材料已存在，将其完整纳入主文/补充材料并为代码、数据、配置和运行产物提供持久标识、版本和哈希；若因隐私不能开放原帖，至少提供可复现的派生特征、合成替代和受控访问流程。
- Resolution evidence: 无占位符的附录、可执行的冻结配置、逐字Prompt和词表、软件/LLM版本与随机性设置、代码及最小复算说明。
- Score impact: 完成后复现维度可由1升至3，但不会单独修复W1—W4的科学识别问题。

### W7 — 冻结版尚非可提交论文，且真实社交数据与伤害性生成缺少伦理处置

- Severity: major
- Paper pointer: page 1; page 9, missing Figure 1; pages 11–23, visible tracked changes; page 26, Appendices A–C; Section 6.2, pages 25–26; not found in manuscript: ethics/privacy statement
- Suggested reroute: human_decision
- Why it matters: 当前文件在形式上不能作为完整投稿，同时使用可识别社交媒体内容研究真实逝者并驱动“地狱梗”生成，涉及平台条款、用户隐私、对家属和相关群体的潜在伤害，需要可追责的人类判断。
- Evidence: 第1页摘要栏为空且关键词重复显示新旧版本；33页PDF显示大量彩色插入/删除、下划线和修订线；图1标明“待制”；第20—22页存在删改文本重叠，附录全部待填。稿件没有说明伦理审查/豁免、抓取合规、个人标识移除、原帖引用策略、敏感生成内容的访问控制、研究者暴露风险或治理建议可能造成的表达压制风险。
- Suggested action: 由项目负责人确认数据使用授权、伦理审查需求和伤害最小化方案，记录可公开边界；随后生成接受全部修订的干净稿，补全摘要、图1、附录、图表编号和参考文献。
- Resolution evidence: 书面伦理/合规决策、去标识与访问控制说明、伤害评估，以及无修订痕迹、无占位符、交叉引用完整的最终PDF。
- Score impact: 若伦理授权不足，研究不应按当前形式提交；若合规且版面补全，清晰度与伦理维度可提高，但中央分数仍取决于W1—W5。

## Questions and score-change conditions

1. W19—W22真实帖文是否在每个Agent当周决策前以原正文和原类别结构进入其候选池？若是，W1成立且总分保持1；若作者能提供逐决策日志证明这些信息被严格滞后或遮蔽，并展示无泄漏复算，总分可能上调。
2. 图4—6中的Agent-only类别究竟来自固定Agent类型，还是来自对最终生成正文的独立盲法分类？若仅来自身份标签，W2成立；若已有独立文本编码及错配矩阵，提供后可重新评估“表征涌现”。
3. α_D、k、s_i、λ_i、scale、0.95门槛和B的完整确定顺序、搜索空间及目标函数是什么？若任何一步使用了W19—W22或反复观察终态后调整，总分不提高；若有预先冻结、训练期限定和参数敏感性证据，可改善技术评分。
4. 人工编码由几名编码者完成，是否盲于周次/假设，类别级一致性如何？若独立审计显示周级转折对编码误差稳健，可解除W5；若无复编码或可靠性低，现实基准仍不可用。
5. 冻结PDF是否代表准备提交的可见版本？即使回答“仅为审计视图”，也需要一份接受全部修订、补齐摘要/图1/附录的冻结投稿版；这只会改善完整性，不会抵消W1—W4。

## Limitations, ethics, and reproducibility

稿件对单案例、3 seeds、模型黑箱、量纲差异和“不等于真实平台净因果效应”的自我限制较为充分，这是优点。但真正决定结论的限制——后段现实结果注入、固定身份决定输出类别、参数选择自由度和三臂组件混杂——尚未被当作识别失败处理。复现方面，附录和代码/数据声明仍为空，无法审计公式是否对应实现。伦理方面，公开平台数据不自动意味着无需审查；研究包含真实逝者、普通用户表达和伤害性迷因生成，必须由负责人明确平台条款、去标识、保存与访问、敏感文本展示、家属/相关群体伤害及治理误伤风险。

## Overall recommendation

**Overall score: 1/5 — Strong reject / foundational rework.** 选题重要，理论—模型映射也有发展潜力，但当前稿件的中央证据受到两个基础性问题破坏：验证期真实结果持续进入模型，以及模拟输出类别由固定身份与同一词表闭环定义。它们意味着现有图4—6无法证明论文所声称的生成性复现与表征涌现；这不是通过润色或补一张图可以解决的问题。三臂组件混杂、极少重复、数据编码未验证和参数/代码缺失进一步降低可信度。

**Confidence: 4/5 — confident, with limited residual uncertainty.** 我检查了完整冻结文本、修订审计和33页版面，足以确认上述设计与提交缺口。剩余不确定性主要来自清单没有授权底层配置、日志、数据与代码；这些材料如果存在，可能修正个别实现层判断，但无法消除稿件明示的后段注入和身份赋类逻辑。

## Advisory reroute

- Primary reroute: `experiment_config`，decisive issues: W1, W2, W3, W4。需要先把验证输入做成结果盲、将输出测量与Agent身份解耦、正交化候选池与排序组件，并冻结参数/重复计划；直接运行更多现有配置只会更精确地重复同一识别问题。
- Secondary reroute 1: `analysis`，issue: W5。底层人工标签若已存在，应先完成样本流、编码可靠性、误差传播和轨迹敏感性审计；只在正文中解释数量差异不足以恢复基准可信度。
- Secondary reroute 2: `generate_paper`，issue: W6。仅在科学设计和已有证据确认后，补齐Prompt、词表、参数、伪代码、代码/数据可得性及干净版面；晚阶段编辑不能修复W1—W5。
- Secondary reroute 3: `human_decision`，issue: W7。真实社交数据、逝者相关伤害性文本和治理含义的合规/伦理边界必须由负责人作可追责决定，不能自动化代替。
- 这些路由均为建议，不修改 `.agentsociety/progress.json`，也不授权执行实验或改稿。

## Machine-readable handoff

```json
{
  "schema": "agentsociety.paper-review.individual-handoff/v1",
  "review_path": "paper/reviews/generic-review-r1/reviewer-2.md",
  "round_id": "generic-r1",
  "reviewer_id": "R2",
  "overall_score": {"value": 1, "label": "Strong reject / foundational rework"},
  "confidence": {"value": 4, "label": "confident, with limited residual uncertainty"},
  "recommendation": "strong_reject",
  "primary_reroute": "experiment_config",
  "secondary_reroutes": ["analysis", "generate_paper", "human_decision"],
  "blocking_issue_ids": ["W1", "W2", "W3", "W4", "W5", "W6", "W7"],
  "issues": [
    {
      "id": "W1",
      "severity": "fatal",
      "reroute": "experiment_config",
      "summary": "后段真实类别轨迹持续作为模型输入，所谓留出复现存在目标泄漏"
    },
    {
      "id": "W2",
      "severity": "fatal",
      "reroute": "experiment_config",
      "summary": "输出类别由固定Agent身份和同一词表闭环决定，无法证明语义表征涌现"
    },
    {
      "id": "W3",
      "severity": "major",
      "reroute": "experiment_config",
      "summary": "三臂混杂候选池、时间结构与个性化，不能识别推荐组件效应"
    },
    {
      "id": "W4",
      "severity": "major",
      "reroute": "experiment_config",
      "summary": "正式重复不足且参数选择不可审计，拟合优势不稳定"
    },
    {
      "id": "W5",
      "severity": "major",
      "reroute": "analysis",
      "summary": "真实基准与人设比例缺少抽样、编码可靠性和敏感性证据"
    },
    {
      "id": "W6",
      "severity": "major",
      "reroute": "generate_paper",
      "summary": "Prompt、参数、伪代码、代码与数据可得性仍缺失，结果不可复现"
    },
    {
      "id": "W7",
      "severity": "major",
      "reroute": "human_decision",
      "summary": "冻结版含修订与占位符，真实社交数据和伤害性生成缺少伦理处置"
    }
  ]
}
```
