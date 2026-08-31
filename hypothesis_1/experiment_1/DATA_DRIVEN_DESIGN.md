# 数据驱动试点设计：env 与 agent 交互规则（v0.1，2026-08-31）

> 用真实打标数据（`datasets/zhangxf_labeled/`）替换 experiment_1 试点配置中的合成供给与合成 persona。
> 数据依据见 `datasets/zhangxf_labeled/CLUSTERS.md`；本文件回答两件事：**env 怎么建**、**agent 怎么交互**。

---

## 0. 设计映射总览

```
真实数据                          模拟构件
──────────────────────────────  ─────────────────────────────────────
10 供给主题簇                    供给池 posts（真实文本采样 + is_meme 元数据）
主题 × 平台构成                  producer agent persona（每主题 1-2 个真实作者）
死亡冲击波（03-24 脉冲指数衰减）   供给时间曲线（producer 发帖节奏参数）
供给 Gini=0.156（分散）           对照张力：推荐臂制造曝光集中 → Q1 归因
梗判定规则（967 词库）            is_meme 内容元数据 → 治理干预靶点（限流降权）
平台结构（抖音梗/小红书悼念）      受众 archetype 的主题偏好向量
——                              受众 agent 熟悉度分组（低/高，β0）
```

---

## 1. env 设计

### 1.1 试点：沿用 `SocialMediaSpace`（module_type 已注册）

试点配置全部通过 `SocialMediaSpace` 现有 kwargs 实例化，不写新代码：

| kwargs | 数据驱动取值 | 来源 |
|---|---|---|
| `persons` | 每供给主题 2 个真实作者（id 901-921），username 用化名（`主题名_作者A`，避免真实用户名入库） | parquet `author` 列（化名化） |
| `posts` | 采样 120-160 条真实文本（配额见 1.2），`tags=[主题名, is_meme]` | parquet 采样 |
| `agent_id_name_pairs` | 100 个受众 agent 映射 | §2.1 |
| `feed_source` | `global`（试点）；对照臂实验再改 | 原配置 |
| `recommendation_algorithm` | 臂 A `chronological` / 臂 C `random`（RecommendationEngine 内置）；臂 B 个性化见 1.4 | 三臂设计 |
| `random_seed` | 固定（同供给同用户池跨臂复用） | Q1 设计 |

### 1.2 供给池配额（posts 采样）

以 9 个有效主题 + 借势营销（人工类别，从无效侧采样）共 10 类供给，按「真实占比 × 保底」配额，共 ~140 帖：

| 供给类 | 配额 | 说明 |
|---|---:|---|
| 悼念颂扬 | 28 | 最大主题，峰值在死亡日 |
| 泛议论杂谈 | 16 | 权重下调（兜底簇，0.19 真实占比 → 0.11） |
| 巧乐兹雪碧梗 | 20 | **is_meme=1 全量**，抖音占比 98% → tags 标注 |
| 人生语录 | 14 | 去语境化切片的主要载体 |
| 死因健康科普 | 12 | |
| 家庭教育观点 | 12 | 争议最高（N=34%） |
| 志愿填报干货 | 10 | 死前存量供给（pre_death 7.2%） |
| 学习方法观点 | 10 | 死前存量供给（pre_death 16%） |
| 公司接班后事 | 8 | 死后组织延续叙事 |
| 借势营销（噪音供给） | 10 | 从无效侧采样，模拟真实噪音 |

规则：每帖真实文本（截断 280 字）；`tags = [主题名, "is_meme" 若命中]`；同一主题内按 `dup` 加权采样（重复度高的文本优先入选，保留供给同质化结构）。

### 1.3 供给时间曲线（producer 发帖节奏）

- `start_t = 2026-03-24T08:00:00`（真实讣告日，修正原配置虚构的 08-20）。
- tick = 1 仿真日（12 ticks ≈ 03-24 → 04-04）。
- producer agent 每 tick 的发帖概率按真实日供给曲线归一化：

```
p_post(theme, t) ∝ daily_count(theme, t) / Σ_t daily_count(theme, t)
```

- 悼念颂扬/泛议论/人生语录/死因科普：死亡日脉冲 + 指数衰减（1236→1073→764→547…）；
- 志愿填报/学习方法：平坦存量（峰值在 4 月，模拟窗内缓升）；
- 巧乐兹雪碧梗：低量持续（5-6%/日占比），第 3 日后占比稳定。

### 1.4 个性化臂（臂 B）——`DouyinSpace` 自定义 env（设计，二期实现）

RecommendationEngine 内置算法无「主题-偏好个性化」，臂 B 需要自定义 env（`custom/envs/douyin_space.py`，继承 `SocialMediaSpace`）：

- **主题赌博机推荐器**：维护 user×theme 偏好表；`refresh_feed` 时按 `score(user, post) = β·affinity(user, post.theme) + (1-β)·popularity(post)` 排序，`affinity` 由 like/comment/view 事件以 η 学习率更新（Explore/Exploit：ε=0.1 随机探索，对应 H5 的探索率参数）；
- **治理开关**（hypothesis_1 干预臂的基础）：
  - `meme_demotion(factor)`: is_meme 帖排序分 ×factor（0.1 = 限流降权）——实验 2/3/4 的「对梗/二创内容限流降权」直接以 `is_meme` 为靶点，判定器即那把尺子；
  - `theme_supply_filter(theme, cap)`: 供给端下架（内容生产期干预）；
  - `ban_author(author_id)`: 封禁高频二创账号（账号端干预）。
- 三臂对照全部复用同一份 init_config，仅 env kwargs 的 `recommendation_algorithm` / 治理开关不同（同供给同用户池）。

---

## 2. agent 设计与交互规则

### 2.1 受众 agent：archetype × 熟悉度（100 个）

**archetype 由数据的平台 × 主题消费结构定义**（3 类），每类再分低/高熟悉度（2 组）→ 6 组：

| 组 | archetype | n | 主题偏好向量（供赌博机/行为倾向用） | 熟悉度 | persona 要点 |
|---|---|---:|---|---|---|
| 1 | 抖音娱乐向 | 30 | 梗 0.5 / 语录 0.15 / 泛议论 0.1 / 悼念 0.1 / 其他 0.15 | 低（25）/高（5） | 以短视频为唯一信息源，不认识张雪峰本人（低熟悉组 β0≈0） |
| 2 | 小红书共鸣向 | 30 | 悼念 0.3 / 语录 0.25 / 家庭教育 0.15 / 泛议论 0.1 / 其他 0.2 | 低（15）/高（15） | 女性向生活平台用户，关注情感与教育话题 |
| 3 | 教育关切向 | 30 | 家庭教育 0.3 / 志愿填报 0.25 / 学习方法 0.2 / 泛议论 0.15 / 其他 0.1 | 低（10）/高（20） | 家长/学生/教师，有实际教育决策需求 |
| 4 | 热点吃瓜向 | 10 | 泛议论 0.3 / 梗 0.25 / 死因科普 0.15 / 其他 0.3 | 低（9）/高（1） | 热搜冲浪选手，围观图乐，无立场 |
| 5 | 供给者侧 producer | —（试点不做 LLM agent，见 §2.3） | — | 高 | 真实作者的化名代理 |

- **低熟悉组**：persona 明确「此前不了解张雪峰，对其无既有印象」——首因印象由本次曝光形成（RQ 核心亚群，共 59/100）。
- **高熟悉组**：persona 含具体生前认知（如「看过他讲志愿填报的视频」）——作对照组。
- 偏好向量只作用于 env 赌博机学习初始化与 agent 行为倾向（点赞概率），**不直接写入认知**；印象必须由 LLM 在浏览中涌现（§3 原则）。

### 2.2 受众 agent 每 tick 交互规则（steps.yaml `run` 步骤内的行为协议）

每 tick（=1 仿真日）执行固定行为循环，决策由 LLM 在 persona 约束下做出：

1. **刷流**：`refresh_feed` 取 20 条（env 推荐器排序结果，agent 不可见排序原因——对应 L034「解释≠真值」）；
2. **浏览**：`view_post` 逐条观看，最多 8 条/日（注意力有限）——曝光由此进入 view log（中间变量）；
3. **互动决策**（LLM，逐帖）：基于 persona + 已看内容，输出 `{like?, comment?, repost?}`；
   - 点赞概率受 archetype 偏好调节（数据先验）；
   - **玩梗触发规则**（梗词判定规则的 agent 侧使用）：若所见帖 is_meme 且 agent 已见过同类梗 ≥2 次（重复曝光），评论中允许使用梗词/句式（从 `meme_words` 采样），模拟梗的再生产；低熟悉 agent 首次接触玩梗帖不主动玩梗（先观察后模仿——H8 一致性机制）；
   - **评论内容协议**：评论必须引用或回应所见帖子内容（可溯源），禁止凭空生成对张雪峰的评价；
4. **不作全局总结**：tick 内不输出「我对张雪峰的看法」——印象只通过问卷测量（§2.4），避免引导效应。

### 2.3 producer agent 每 tick 交互规则

1. 按 §1.3 供给曲线判定本 tick 是否发帖（`p_post(theme, t)`）；
2. 发帖内容从所属主题的**真实语料池**采样（含梗帖——producer 是真实供给的代理，不是观点生成器）；
3. 不浏览不互动（供给与需求解耦，保持供给侧 Gini≈0.156 的分散结构）。

> **试点简化**：内置 `SocialMediaSpace` 不支持时间门控发帖（chronological 排序不过滤未来时间戳），且 LLM producer 会生成非真实文本、破坏「供给=真实语料」原则。因此试点中 **producer 不作为 LLM agent**：供给为静态存量池（140 条真实文本，死亡日前存量帖 `created_at` 设在 03-20~23，其余 03-24 当日交错），供给侧 Gini≈0.156 的分散结构直接由池构成保证。producer 发帖曲线与时间门控在 `douyin_space.py`（二期）实现。

### 2.4 印象测量（steps.yaml `questionnaire`）

- **节点**：T0（run 前，基线自评熟悉度）→ run 4 → T1 → run 4 → T2 → run 4 → T3（12 ticks 共 3 次测量）；
- **题目**（全部 agent）：
  1. 「用 3-5 个词描述你对张雪峰的印象」`text` → 事后编码为标签集，算 HHI/Top-1 份额/组间 Jaccard；
  2. 「你对张雪峰的熟悉程度 1-5」`integer` → 低/高分组效度检验；
  3. 「你的印象主要来自？（生前视频/死亡事件相关短视频/新闻/朋友讨论/不确定）」`choice` → 首因来源归因；
  4. 「你印象中张雪峰是做什么的」`text` → 事实层偏差（认知偏移因变量的操作化）。
- 问卷对 agent 不可见彼此答案（无群体极化的直接诱导，极化只能经 env 涌现）。

---

## 3. 两条不可妥协的设计原则

1. **曝光层可参数化，认知层必须涌现**：推荐器权重、供给曲线、互动概率先验都来自数据（可硬编码）；但「重复曝光→印象单一化」不得写成代码规则——LLM agent 在真实文本曝光下自然形成印象，事后用 view log 拟合 log 形更新曲线（校准闭环，对照 L060）。
2. **同供给同用户池**：三推荐臂（chronological / random / personalized）与治理臂共享同一 init 数据与 agent 种子，仅 env 行为参数不同——否则归因无效（B19 逻辑）。

---

## 4. 与 hypothesis_1 四个实验的对接

| 实验 | 组 | 本设计的实现 |
|---|---|---|
| experiment_1 | 无干预基线 | §1.1 配置 + 臂 A/B/C 三推荐子臂（Q1 归因在此完成） |
| experiment_2 | 早期干预（内容生产期） | `theme_supply_filter`：t0 起对 is_meme 供给限流 |
| experiment_3 | 中期干预（算法曝光期） | `meme_demotion(0.1)`：T1 问卷后启动排序降权 |
| experiment_4 | 晚期干预（认知形成期） | `meme_demotion(0.1)`：T2 问卷后启动 |

## 5. 交付物与状态

- [x] 聚类 + 画像：`datasets/zhangxf_labeled/`（CLUSTERS.md / parquet / profiles / meme_stats）
- [x] 梗判定器：`meme_matcher.py`（规则文档 → is_meme）
- [ ] `build_config_from_data.py`：xlsx/parquet → init_config.json + steps.yaml（本目录 init/）
- [ ] `custom/envs/douyin_space.py`：臂 B 个性化 + 治理开关（二期，试点用内置算法先行）
- [ ] 配置校验：`ags.py experiment-config validate`（生成后）
