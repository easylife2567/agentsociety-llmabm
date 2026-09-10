---
name: weekly-feed-flow
description: 舆论场数字表征转移模拟（CurationDynamicsSpace）每周行动流程：先用 get_feed 观察本周信息流与舆论场，再决定是否发言；发言通过 create_post 发布，每 tick 至多 1 帖、重复调用无效。
---

# 每周信息流行动流程（Weekly Feed Flow）

您正处在「舆论场数字表征转移」模拟环境中（张雪峰 2026-03-24 去世后 11 周，W12→W22）。
每周（每个 tick）您的固定身份类型保持不变，您需要：**先观察，再决定，必要时发言**。

## 每周标准流程

1. **先调用 `get_feed` 观察舆论场**（只读，零副作用，每周必做）。

   使用框架的 `ask_env` 约定调用环境工具（不要直接写死环境内部细节）：

   ```
   get_feed(agent_id=<您的 agent_id>)
   ```

   返回内容解读：

   - **week**：当前周标签。
   - **norm_pressure / norm_pressure_level**：本周悼念规范压力（0~1）及其等级
     （high / medium / low）。压力越高，环境对该周悼念表达的期望越强。
   - **own_spoke**：您本周是否已发言（true 表示本 tick 已发过帖）。
   - **own_last_post**：您最近一帖（post_id / type / assigned_type / content）。
   - **feed**：本周推荐给您的信息流，长度 = feed_size，官方置顶帖排在前面。
     每条含 post_id / author_handle / content / type / tendencies（四类倾向分：
     词表命中次数/句长密度，表征该帖的玩梗/哀悼/营销/教育倾向）/ week / is_official。
   - **feed_type_distribution**：您所见信息流的类型构成（玩梗 meme / 悼念 mourning /
     教育 education / 营销 marketing / 其他 other / 噪音 noise 六类占比），
     即「意见气候」——观察它了解当前主流声音。
   - **global_supply_shares / global_exposure_shares**：最近完结一周的全局供给份额与
     曝光份额，了解整个舆论场的构成。
   - **personal_stats**：您的累计发帖数与累计各类型曝光数。

2. **基于观察决定本周是否发言**。

   是否发言由数值决策算法合成（沉默的螺旋 / 注意力衰减 / 悼念规范压力三机制，
   参数见您 profile 中的 params）；您只需按流程行动：若本周未获发言，保持沉默即可；
   若本周发言，撰写一条符合您类型与人设的帖子。请注意：**每周至多发布 1 帖**。

3. **若决定发言，先基于你看到的帖子组织内容，再调用 `create_post`**。

   发言应建立在你第 1 步看到的帖子之上：回应、补充、反驳、二创、玩其中的梗、
   或接话跟帖式地引用讨论都可以；与你高度相关的帖子优先围绕它展开。

   ```
   create_post(agent_id=<您的 agent_id>, content=<帖子正文>)
   ```

   - 正文不能为空（空正文返回 status=fail）。
   - 返回 status ∈ {success, fail, error}，并给出 **post_id** 与 **pool_type**
     （=您的固定类型）、**assigned_type**（环境用四词表对正文的独立判类结果）、
     **type_mismatch**（判类与您的类型是否不一致，仅供参考，不影响发布）。
   - 本 tick 发布的帖子自**下一周**起进入信息流传播。

## 关键规则（务必遵守）

- **每周（每 tick）至多发布 1 帖**：同一 tick 内重复调用 `create_post` 不产生任何新变化，
  返回 `already_posted=true` 与首次发布的 post_id（first-write-wins）。
- **get_feed 无副作用**：同 tick 内重复调用返回同一快照，不重复计曝光，可放心多次调用。
- **先看再写**：请养成先 `get_feed` 观察、再决定是否 `create_post` 的习惯，
  让您的发言建立在当前舆论场信息之上。
- 您的身份类型全程固定；不要试图「改类型」，类型由环境在启动时指定。
