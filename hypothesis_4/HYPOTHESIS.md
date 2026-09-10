# Hypothesis

## Description

算法策展主假设（2026-09-08 按《实验设计阶段.md》定稿与用户四项裁定重写；2026-09-10 机制重设计：第二因子由悼念规范压力改为**玩梗涌现环境**）：推荐算法的个性化兴趣匹配（Agent 类型词表 × 帖子内容特征 + 历史曝光/互动，**不含帖子级热度信号**）会选择性激活既有的玩梗表达群体——同一初始内容池与同一群体构成条件下，兴趣推荐环境中玩梗群体的表达活跃度及其内容的供给/曝光份额显著高于去个性化环境（随机推荐与时序推荐），舆论场对逝者的公共表征构成沿"专业→悼念→迷因"轨迹转移，且转移幅度显著大于两个基线臂。机制定位：玩梗群体事件前已存在于平台生态（真实数据：W05–W12 梗文化内容每周 0–6 条持续产出；用户口径主导类型占比 37.9%，为人数最多的潜伏表达群体），算法改变的是**既有群体的差异化激活与可见度分配**（构成效应），不以个体认知偏移或类型转换为中介——Agent 类型全程固定，仅公开表达/沉默与内容可见性可变。第二因子为**玩梗涌现环境**（用户 2026-09-10 裁定的存量/流量语义：舆论场存量越丰沛越易诞生 meme，当期新增越少越空旷越宜 meme 传播）：normal（空旷度 S 随现实口径周新增调度逐周演化，洪峰期压抑、退潮期释放）vs sustained_hot（反事实：事件周后冻结 S，维持高热洪峰不退），用于识别"算法策展 × 涌现环境"交互作用——若高热维持下兴趣臂玩梗表征不再崛起，则算法效应依赖热度退潮释放的未饱和传播空间；若仍然崛起，则算法自身足以驱动表征转移。备择情形分支：(a) 兴趣臂相对基线的差异化激活成立但公共表征未转移 → 激活仅是曝光分配层面现象，需检验供给端与涌现机制；(b) 各臂均转移且臂间无显著差异 → 表征改变由群体内生动力（涌现环境 + 注意力衰减 + 沉默螺旋）驱动，算法非核心机制，命题修正为"算法×群体内生动力合谋"；(c) 任何臂均不涌现转移 → 微观规则集不足，按模式导向建模原则返回调整初始规则，而非强行修改结果。生成性验证前提：interest×normal cell 须先复现真实"教育→悼念→玩梗"三阶段周级形态（拟合 benchmark_curves.json：W13 悼念份额峰 41.4%±8pp、玩梗 W19 7.8% → W22 60.3% 二波结构定性必需、相位 ±1 周、形状比 log 空间 ±0.3），否则返回调整规则而非下因果结论。因变量：五类表征的内容供给占比与曝光占比周级轨迹（结果层）；各类型 Agent 发言率，及"群体规模→发言比例→供给比例→曝光比例"漏斗的逐级偏移（机制层）。不观测个体认知偏移。分组变量：推荐算法（random / chronological / interest）× 玩梗涌现模式（normal / sustained_hot），3×2 全因子 6 cells。规模预算（用户 2026-09-08 裁定 100 agents × 11 ticks × 3 seeds = 18 runs ≈1.98 万 agent-ticks；2026-09-10 裁定群体比例按**发帖人口径**：玩梗 18 / 悼念 21 / 营销 26 / 讨论 15 / 其他 20）。

## Rationale

理论框架第三层（算法策展/算法放大）将推荐系统定位为信息环境组织者。本版假设按用户裁定将策展操作化为**纯兴趣匹配**（无热度项）：这是个性化策展的最小机制——若仅凭"类型词表匹配 + 历史行为"的选择性曝光即可差异化激活既有玩梗群体并驱动公共表征转移，则个性化策展本身构成充分放大机制；若不能涌现，则为"热度/互动信号是放大必要成分"提供反证，机制归因边界同样具有理论价值。与"认知偏移"框架的区别不变：机制是群体层面的构成效应——个体无需转变，表征构成改变来自哪类既有群体被激活、被看见。数据实证三重支撑：①真实曲线"教育→悼念→玩梗"三阶段转移（W13 悼念 41.4% 峰值，W19–W22 玩梗 7.8%→60.3%，benchmark_curves.json）；②平台分化（抖音玩梗 W22 82% vs 小红书 19%）表明策展逻辑差异决定放大速率；③用户口径 vs 内容口径的结构性错位（梗文化：37.9% 用户 vs 13.6% 内容；营销：12.6% 用户 vs 30.7% 内容）表明玩梗群体是人数最多、常态表达最低的潜伏群体，差异化激活空间最大，故 Agent 比例按用户（发帖人）口径设定。**涌现环境维度（2026-09-10 机制重设计）**：注意力经济（Simon 1971——信息的丰裕造成注意力的稀缺，洪峰期新表达被淹没）、生态位/logistic 增长（meme 需要未饱和空间才能指数扩张）、模因论（Dawkins 1976——模因在丰宿主池中复制变异）。玩梗涌现增益 G = B^β·S^σ 仅进入玩梗型效用（θ=1.0）：存量丰沛（B）给梗以土壤，当期流量空旷（S）给梗以扩散空间；洪峰期 G<1 压制玩梗、退潮期 G>1 释放。反事实臂 sustained_hot（事件周后冻结 S，维持高热）用于识别算法效应的边界条件（交互作用），替代旧设计的事件/无事件嵌套臂承担内部因果识别角色（亦替代 2026-09-10 前版本的悼念规范压力第二因子——与沉默的螺旋 D 因子存在共线性冗余，经用户确认退役）。机制链（沉默螺旋 + 注意力衰减 + 涌现环境增益 → 发言决策 U = D·R·G^θ；类型固定 → 内容类型不变）的微观规则详见《实验设计阶段.md》。配置裁定：2026-09-08 四项（纯兴趣匹配、用户口径群体比例、3×2 全因子、11 ticks × 3 seeds）+ 2026-09-10（发帖人口径 18/21/26/15/20、涌现环境第二因子、发言基于所见、feed_size=10）。

## Experiment Groups

### Group 1: random_normal

**Type:** control

**Description:** 弱策展基线：随机推荐 × 玩梗涌现环境正常演化（S 随现实调度）。Agent 从公共内容池均匀随机获得帖子，兴趣与历史不影响曝光。

**Agent Selection Criteria:** 全体 100 agents（玩梗 18 / 悼念 21 / 营销 26 / 教育 15 / 其他 20，发帖人口径）; recommendation_algorithm=random; meme_emergence_mode=normal

### Group 2: chrono_normal

**Type:** control

**Description:** 去个性化时序基线：时序推荐（发布时间倒序）× 玩梗涌现环境正常演化。对应旧版"去策展化 chronological"臂。

**Agent Selection Criteria:** 全体 100 agents（同上）; recommendation_algorithm=chronological; meme_emergence_mode=normal

### Group 3: interest_normal

**Type:** treatment

**Description:** 主治疗臂：兴趣推荐（类型词表×帖子特征匹配 + 历史曝光/互动，无热度项）× 玩梗涌现环境正常演化。兼任生成性验证 run——须复现真实三阶段形态（拟合 benchmark_curves.json），通过后方可进行臂间因果比较。

**Agent Selection Criteria:** 全体 100 agents（同上）; recommendation_algorithm=interest; meme_emergence_mode=normal

### Group 4: random_sustained_hot

**Type:** treatment

**Description:** 反事实 cell：随机推荐 × 玩梗涌现环境维持高热（事件周后冻结空旷度 S，洪峰不退）。与 Group 1 对照估计热度退潮释放传播空间在弱策展下的独立效应。

**Agent Selection Criteria:** 全体 100 agents（同上）; recommendation_algorithm=random; meme_emergence_mode=sustained_hot

### Group 5: chrono_sustained_hot

**Type:** treatment

**Description:** 反事实 cell：时序推荐 × 玩梗涌现环境维持高热（事件周后冻结 S）。与 Group 2 对照估计热度退潮在时序环境下的独立效应。

**Agent Selection Criteria:** 全体 100 agents（同上）; recommendation_algorithm=chronological; meme_emergence_mode=sustained_hot

### Group 6: interest_sustained_hot

**Type:** treatment

**Description:** 核心反事实 cell：兴趣推荐 × 玩梗涌现环境维持高热（事件周后冻结 S）。回答"若事件后舆论场始终维持洪峰高热、未饱和传播空间不释放，兴趣推荐能否单独推动玩梗表征崛起"——识别算法策展效应 × 涌现环境的交互作用。

**Agent Selection Criteria:** 全体 100 agents（同上）; recommendation_algorithm=interest; meme_emergence_mode=sustained_hot
