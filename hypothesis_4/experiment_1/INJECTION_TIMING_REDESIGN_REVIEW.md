# 注入时机重新设计审阅

## 结论

2026-09-28 已决定撤回“所有真实帖整体延迟一周”的 `weekly_lag1_event_v2` 方案，并恢复 `anchored_v1` 的周级刺激—响应顺序。需要修正的是论文中的时间语义说明，而不是把真实帖子整体后移。

推荐的周级顺序是：

1. 将来源周为 $W_t$ 的真实帖子作为该周的外生刺激载入环境。
2. 在任何 Agent 行动前冻结该周全部 Agent 的 feed 快照。
3. 所有 Agent 基于冻结快照各自决定是否发言并生成内容。
4. 当周 Agent 帖先进入 pending buffer；本周所有 Agent 完成后再统一并入帖子池。
5. 因此，当周 Agent 帖最早从 $W_{t+1}$ 起影响其他 Agent，任何 Agent 都看不到同一步中稍早生成的同伴帖子。

该顺序把真实帖子定义为实验输入，把 Agent 帖定义为模型响应。两者角色不同，不要求同时进入同一决策快照。周级模型表达的是“Agent对该周外部舆论环境的响应”，不声称复原一周内每条帖子的分钟级先后顺序。

## 为什么整体延迟改变了曲线

这次差异来自实验设计本身，不是绘图误差。

以 interest_s0 为例：

- `anchored_v1` 正式结果总量为：28、42、34、22、20、12、8、7、16、23、21。
- 已完成的 `weekly_lag1` 正式结果为：22、21、30、31、22、17、16、7、8、15、23。
- 当前无事件效用加成的代理结果为：22、19、31、37、23、16、14、7、3、17、22、20。

代理结果与已经完成的 `weekly_lag1` 正式结果接近，说明预测图呈现的是滞后设计的真实结构变化。

整体延迟造成了四个同时发生的变化：

1. W12不再使用W12真实帖，而改用W11初始化样本，起点的教育等内容结构发生变化。
2. W13官方讣告被保留在W13，但其他W13真实帖延迟到W14，同一个事件周的内容被拆成两个到达批次。
3. W14由Agent生成的响应帖在W15才可见，原本集中的响应进一步摊到W15。
4. 发言采用确定性门槛，并受累计曝光和疲劳影响。早一周的细小差异会改变后续哪些Agent跨过门槛，所以结果不是原曲线的机械平移。

三种子正式结果也支持这一解释。interest在原周标签下，`anchored_v1`与`weekly_lag1`总量相关系数为0.690；把滞后结果向前对齐一周后，相关系数提高到0.962，RMSE从7.41降到4.29。random对齐后的相关系数为0.959。也就是说，宏观趋势确实大体保留，但在行动周坐标上被平移，并且W13事件峰被拆散。

用户提供的 `anchored_v1_interest_s0` 图中，W12非悼念发帖为28帖，W13非悼念发帖约20帖；W13总量升至42帖主要同样来自mourning增加到22帖。它与已撤回的“5个事件槽位”预测外形相似，但因果来源不同：旧正式结果的W13 Agent看到了完整W13真实内容批次，而错误预测是用一个参数直接把mourning Agent推过门槛。

## 三种方案

### 方案A：恢复周级刺激—响应顺序（推荐）

保留 `anchored_v1` 的真实帖同周输入和 Agent 帖次周可见机制，并在论文中明确周级批处理语义。

优点：

- 保留已经完成的正式结果和曲线解释。
- 不引入W11初始化样本、W23排空周或事件周特殊补丁。
- 不需要为“保持W13峰值”增加事件效用参数。
- 与研究问题一致：比较推荐机制如何改变Agent对真实周度舆论环境的响应。

限制：

- 周级臂不解释日内先后顺序；需要在方法部分明确这是周度聚合模型。
- 若论文要回答分钟级或日级因果先后，只能依赖chronological臂或另建细粒度实验。
- 主结果应优先报告Agent-authored输出；包含真实注入帖的combined供给口径只用于描述环境，避免同周外部输入造成机械拟合的误解。

### 方案B：保留整体一周延迟

继续让所有普通真实帖和Agent帖在下一周首次可见，并将主要图按行动周报告。

优点是输入可得性规则形式上对称。代价是研究对象变成“信息延迟一周后的舆论动力学”，不能再期待与原正式曲线按同一周标签相似；W13事件响应被拆分也是该方案的真实结果。

如果采用此方案，比较时应额外提供向前对齐一周的source-cohort图，但不能用重新标记掩盖行动时间上的真实延迟。

### 方案C：为W13设置特殊即时规则

让W13更多事件帖同周进入，其他周继续延迟，可以恢复W13峰值，但需要人为决定哪些帖子属于事件例外，也会使W13与其他周使用不同规则。该方案最容易被质疑为针对目标曲线调参，不建议采用。

## 建议的论文表述

> Each weekly step represents a batch-level stimulus–response cycle. Exogenous posts dated to week $W_t$ were loaded as the observed information environment for that week, after which all agents received frozen feed snapshots and made one posting decision. Agent-generated posts were buffered until all agents completed the step and became eligible for recommendation from $W_{t+1}$. This synchronous update prevented within-step ordering effects among agents while preserving the observed weekly external context.

中文可表述为：

> 每个周级步长表示一次批量刺激—响应过程。来源周为 $W_t$ 的真实帖子构成该周的外部信息环境；环境先为所有Agent冻结推荐流快照，随后Agent各自完成一次发言决策。当周生成的Agent帖子在所有Agent行动结束后统一并入帖子池，并从 $W_{t+1}$ 起参与推荐。因此，同一步内不存在后行动Agent看到先行动Agent新帖的顺序偏差。

## 已执行的归档决定

`weekly_lag1_event_v2` 已标记为未运行的废止设计；`weekly_lag1` 已作为信息延迟敏感性批归档；`anchored_v1` 已恢复为正式主方案。后续只需沿用周级更新顺序的验证和论文说明，不因本次决定新增一轮大规模实验。
