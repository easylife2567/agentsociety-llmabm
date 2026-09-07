---
name: social-media-curation
description: 算法策展动力学社交媒体互动：刷新全站信息流（含事件热度热搜）、查看帖文、发布 / 转发 / 评论 / 点赞。必须通过 ask_env 调用 CurationDynamicsSpace 工具。
---

# Social Media Curation

CurationDynamicsSpace 是微博式全局 feed 的社交媒体环境，用于「算法策展如何塑造逝者数字表征」实验。**所有操作通过 `ask_env` 调用**，环境路由器会自动将指令转换为 CurationDynamicsSpace 工具调用。

## 环境概念

### 用户身份

你的 agent id 就是你在 feed 中的身份。`ctx={"id": <your_id>}` 提供你的身份；凡 `author_id` / `user_id` 参数都填自己的 id。你代表一个内容类群（如借势营销 / 事件悼念讨论 / 梗文化讨论），feed 中还有 id=999 的权威媒体账号（官方信源，非互动对象）。

### 帖子

每条帖子有 `post_id`、`author_id`、`content`、`tags`（[类群, 平台]）、`post_type`（`original` / `repost`）、`parent_id`，以及 `likes_count` / `comments_count` / `reposts_count` / `view_count`。`topic_category` 为类群编码。

### 时间门控与信息流

feed 只包含 `created_at` 不晚于当前仿真时间的帖子——**周级错峰供给**：每个 step 推进一周，新帖按真实议程节奏逐周出现，先前看不见的帖子本周可能出现。每次刷新信息流，response 开头有「全站热搜」行：**事件热度 S(t)**（0–100 整数百分位）+ 当前互动最高的前 3 帖。S(t) 由外部关注（死亡事件后的脉冲与衰减）与内部关注（梗类内容互动回灌）共同决定，并随周变化。

### 推荐算法（实验操纵）

- `reddit_hot`（热度加权）：按赞评转热度与时间衰减排序，热度高的帖子更靠前；
- `chronological`（时间倒序）：按发布时间排序，不放大热度。

两者都是「信息流」推荐，不是电商物品推荐。

## 可用工具

所有操作通过 `ask_env` 调用，用模板指令 + `variables` 让同类调用结构一致（易变值放 `variables`，指令措辞保持稳定）：

```
ask_env(instruction="<指令模板>", variables={...}, ctx={"id": <your_id>}, readonly=<bool>)
```

### refresh_feed（只读）

**刷新信息流 refresh_feed(user_id)**：返回当前可见的全站 feed（按实验配置的推荐算法排序，最多 feed_limit 条）与事件热度热搜行。每个 step 先调用它了解当前信息流、事件热度与可选互动对象，再决定互动。只读，不修改任何状态。

```
ask_env(
    instruction="refresh_feed user_id={user_id}",
    variables={"user_id": 0},
    ctx={"id": 0},
    readonly=True
)
```

### view_post（只读）

**查看帖文详情 view_post(view_target_post_id)**：返回指定帖子的完整内容、作者、类群与各互动计数，供决定是否互动。只读，不修改任何状态（不增加浏览计数）。

```
ask_env(
    instruction="view_post view_target_post_id={post_id}",
    variables={"post_id": 3},
    ctx={"id": 0},
    readonly=True
)
```

### create_post（非只读）

**发布新帖 create_post(author_id, content, tags)**：创建原创帖，`created_at` 为当前仿真时间，立即进入（时间门控下的）信息流候选集。**tags** 建议 `["<你的类群>", "微博"]`，第一个 tag 决定帖子的类群分类（供给份额统计口径）。

```
ask_env(
    instruction="create_post author_id={user_id} content={content} tags={tags}",
    variables={"user_id": 0, "content": "事件相关的新帖内容", "tags": ["事件悼念讨论", "微博"]},
    ctx={"id": 0},
    readonly=False
)
```

### repost（非只读）

**转发帖子 repost(author_id, repost_target_post_id, content)**：转发并附言。**repost_target_post_id** 为要转发的原帖 id；**content** 为转发附言（可留空表示纯转发）。转发生成一条 `post_type="repost"` 的新帖并使原帖 `reposts_count + 1`。

```
ask_env(
    instruction="repost author_id={user_id} repost_target_post_id={post_id} content={comment}",
    variables={"user_id": 0, "post_id": 3, "comment": ""},
    ctx={"id": 0},
    readonly=False
)
```

### comment_on_post（非只读）

**评论帖子 comment_on_post(author_id, comment_target_post_id, content)**：对原帖发表评论，使原帖 `comments_count + 1`。**comment_target_post_id** 为要评论的原帖 id，**content** 为评论文本。

```
ask_env(
    instruction="comment_on_post author_id={user_id} comment_target_post_id={post_id} content={content}",
    variables={"user_id": 0, "post_id": 3, "content": "对内容的评论"},
    ctx={"id": 0},
    readonly=False
)
```

### like_post（非只读）

**点赞帖子 like_post(author_id, like_target_post_id)**：对帖子点赞，使其 `likes_count + 1`。**like_target_post_id** 为要点赞的帖子 id。幂等：同一 agent 对同一帖子只生效一次。

```
ask_env(
    instruction="like_post author_id={user_id} like_target_post_id={post_id}",
    variables={"user_id": 0, "post_id": 3},
    ctx={"id": 0},
    readonly=False
)
```

## 实验行为指引

- **参与门控**：根据 refresh_feed 的「全站热搜」事件热度 S(t) 响应——热度高时提高参与概率，热度衰减后回落至类群基线活跃度；事件本身不强制发悼念帖。
- **框架选择**：参与后按类群偏好选择表达框架（营销 / 悼念 / 教育 / 玩梗 / 杂谈 / 灌水）；评论须引用所见内容。
- **玩梗前提**：仅在被信息流实际曝光梗类模板后才能二创（模因接触前提），不要凭空玩梗。
