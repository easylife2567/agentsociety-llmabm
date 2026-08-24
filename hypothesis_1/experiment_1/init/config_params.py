"""配置参数生成脚本 — 试点实验（100 agents，对照组）

基线组 control_no_intervention：全程不干预，观察认知偏移自然涌现。
生成 init_config.json 和 steps.yaml。

试点规模：100 个 PersonAgent（4 类角色）+ SocialMediaSpace 环境
初始供给：张雪峰去世事件 4 类帖子（事实/悼念/内幕猜测/玩梗）
步数：12 ticks（认知偏移形成链 6 环节 × 2 ticks）
"""

import json
from pathlib import Path
from datetime import datetime

# 输出目录
script_dir = Path(__file__).parent
workspace_root = script_dir.parents[3]

# ============================================
# 1. 模块类型（与 SIM_SETTINGS.json 一致）
# ============================================
AGENT_TYPES = ["PersonAgent"]
ENV_MODULE_TYPES = ["SocialMediaSpace"]

# ============================================
# 2. 试点规模与角色分布（100 agents）
# ============================================
N_AGENTS = 100

# 4 类角色（对应研究设计：高/中/低熟悉度 + 内容生产者）
ROLES = [
    {
        "key": "student",
        "count": 25,  # id 1-25：张雪峰学生/学员（高熟悉）
        "name_prefix": "雪峰考研学员",
        "persona": "曾报名张雪峰的考研辅导课程，听过他的线下课和直播，熟悉他'考研是普通人的翻身机会'的观点，尊称他为'张老师'，对他有深厚感情。",
    },
    {
        "key": "education_follower",
        "count": 25,  # id 26-50：教育领域关注者（中熟悉）
        "name_prefix": "教育圈观察员",
        "persona": "平时关注教育领域资讯和高考志愿填报话题，经常刷到张雪峰的直播切片和采访，对他有一定了解但不算粉丝。",
    },
    {
        "key": "general_user",
        "count": 40,  # id 51-90：普通网友（低熟悉）
        "name_prefix": "刷视频的路人",
        "persona": "平时刷短视频和热搜打发时间，听说过'张雪峰'这个名字，知道他是讲考研的老师，但对他的具体经历了解不深。",
    },
    {
        "key": "creator",
        "count": 10,  # id 91-100：内容生产者/玩梗者（低熟悉但高产）
        "name_prefix": "热点吐槽君",
        "persona": "短视频二创作者，擅长跟热点做吐槽和玩梗视频，为了流量会快速跟进任何热点事件，风格戏谑。",
    },
]


def build_agents():
    """构建 100 个 agent（id 1-100）"""
    agents = []
    cursor = 1
    for role in ROLES:
        for j in range(1, role["count"] + 1):
            i = cursor
            cursor += 1
            agents.append(
                {
                    "agent_id": i,
                    "agent_type": "PersonAgent",
                    "kwargs": {
                        "id": i,
                        "name": f"{role['name_prefix']}{j:02d}",
                        "persona": role["persona"],
                        "max_react_turns": 6,
                        "enable_memory": True,
                        "enable_todo_list": False,
                    },
                }
            )
    return agents


# ============================================
# 3. 事件注入：张雪峰去世事件（4 类初始供给）
# ============================================
EVENT_T = "2026-08-20T20:00:00"

# 媒体/供给账号（非调度用户，仅作为初始帖子作者；id 901-904）
MEDIA_PERSONS = {
    "901": {"id": 901, "username": "教育新闻联播", "created_at": "2026-01-01T00:00:00"},
    "902": {"id": 902, "username": "考研界扛把子", "created_at": "2026-01-01T00:00:00"},
    "903": {"id": 903, "username": "行业深扒", "created_at": "2026-01-01T00:00:00"},
    "904": {"id": 904, "username": "快乐小狗", "created_at": "2026-01-01T00:00:00"},
}

# 初始帖子：事实讣告 / 悼念 / 内幕猜测（去语境化）/ 玩梗二创
INITIAL_POSTS = {
    "1": {
        "post_id": 1,
        "author_id": 901,
        "content": "【讣告】据张雪峰工作室消息，知名考研辅导名师、教育博主张雪峰因病医治无效，于2026年8月20日20时不幸离世，享年42岁。感谢社会各界长期以来的关心和支持。",
        "post_type": "original",
        "parent_id": None,
        "created_at": "2026-08-20T20:00:00",
        "likes_count": 0,
        "reposts_count": 0,
        "comments_count": 0,
        "view_count": 0,
        "tags": ["张雪峰", "讣告"],
        "topic_category": "news",
    },
    "2": {
        "post_id": 2,
        "author_id": 902,
        "content": "凌晨看到这个消息，眼泪一下就出来了。当年考研最迷茫的时候就是听着张老师的课熬过来的，他说'考研是普通人最公平的翻身机会'。张老师，一路走好。",
        "post_type": "original",
        "parent_id": None,
        "created_at": "2026-08-20T20:10:00",
        "likes_count": 0,
        "reposts_count": 0,
        "comments_count": 0,
        "view_count": 0,
        "tags": ["张雪峰", "悼念"],
        "topic_category": "mourning",
    },
    "3": {
        "post_id": 3,
        "author_id": 903,
        "content": "听说张雪峰这次是因为长期高强度直播讲课，身体早就透支了，最近几个月一直在硬撑。教育行业真的卷，名师光环背后都是拿命换的。",
        "post_type": "original",
        "parent_id": None,
        "created_at": "2026-08-20T20:20:00",
        "likes_count": 0,
        "reposts_count": 0,
        "comments_count": 0,
        "view_count": 0,
        "tags": ["张雪峰", "内幕"],
        "topic_category": "rumor",
    },
    "4": {
        "post_id": 4,
        "author_id": 904,
        "content": "笑死，某机构连夜开会改PPT，把'张雪峰老师倾情推荐'全换成'张雪峰老师曾推荐'。人还没凉透，营销先活了。绷不住了哈哈哈哈#张雪峰#",
        "post_type": "original",
        "parent_id": None,
        "created_at": "2026-08-20T20:30:00",
        "likes_count": 0,
        "reposts_count": 0,
        "comments_count": 0,
        "view_count": 0,
        "tags": ["张雪峰", "玩梗"],
        "topic_category": "meme",
    },
}

# ============================================
# 4. 生成 init_config.json
# ============================================
config = {
    "env_modules": [
        {
            "module_type": "SocialMediaSpace",
            "kwargs": {
                "agent_id_name_pairs": [
                    [i, f"user_{i}"] for i in range(1, N_AGENTS + 1)
                ],
                "persons": MEDIA_PERSONS,
                "posts": INITIAL_POSTS,
                "comments": {},
                "follows": {},
                "likes": {},
                "feed_source": "global",
                "polarization_mode": "none",
                "random_seed": 42,
            },
        }
    ],
    "agents": build_agents(),
}

init_config_file = script_dir / "init_config.json"
init_config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2))
print(f"✓ 已生成 init_config.json（{N_AGENTS} agents，{len(INITIAL_POSTS)} 条初始帖子）")

# ============================================
# 5. 生成 steps.yaml
# ============================================
# 认知偏移形成链 6 环节 × 2 ticks = 12 ticks，tick=1（1 小时/步）
# 对照组：全程不干预
steps_config = {
    "start_t": EVENT_T,
    "steps": [
        {"type": "run", "num_steps": 12, "tick": 1},
    ],
}

steps_file = script_dir / "steps.yaml"
try:
    import yaml
    steps_file.write_text(yaml.dump(steps_config, allow_unicode=True, default_flow_style=False))
except ImportError:
    with open(steps_file, "w") as f:
        f.write(f"start_t: {steps_config['start_t']}\n")
        f.write("steps:\n")
        for step in steps_config["steps"]:
            f.write(f"  - type: {step['type']}\n")
            f.write(f"    num_steps: {step['num_steps']}\n")
            f.write(f"    tick: {step['tick']}\n")
print("✓ 已生成 steps.yaml")

print("\n配置文件生成完成！")
print(f"- init_config.json: {init_config_file}")
print(f"- steps.yaml: {steps_file}")
