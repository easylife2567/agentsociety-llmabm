"""配置参数生成脚本（hypothesis_4 / experiment_1）

生成 CurationDynamicsSpace × CurationDiscourseAgent 的全因子实验配置：

- **单因子 3 臂**：推荐算法（random / chronological / interest）× 3 seeds（0/1/2）
  = 9 个 init_config 变体，写入 init/configs/。
  其中配置键仍写 `random`，但其操作语义为 **random_global 强反事实**：每个 Agent
  每周从截至当周 Env 已出现的全部帖子中全 10 槽均匀无放回抽样；不使用生命周期、
  发布时间、兴趣、热度、累计曝光，也不执行官方置顶或 W13 哀悼保底。未来帖子因尚未
  进入 Env 而不可能被抽到。chronological 与 interest 的既有机制保持不变。
  （2026-09-12 用户裁定：玩梗涌现环境增益 G 退役 → 第二因子 sustained_hot 无行为差异，
  3×2 全因子降为单因子；2026-09-14 新一轮采用锚定式表达效用
  U = B_i + R·(D−B_i) ≥ activity。env 侧 B/S/G 仍逐周计算并写 replay，
  作为描述性时间轴与审计线索。）
- 100 个 agent（用户 2026-09-13 更正按发帖人口径：营销23/悼念22/其他21/玩梗19/教育15），
  群体由 custom/agents/curation_personas.build_population(seed=42) 生成，**9 个配置完全共享**。
- 真实帖子注入：按用户裁定「全程约 250 条」，从 custom/envs/curation_assets/
  injection_posts.json 的 W12–W22 池中按 seed 预抽样 3 份样本文件（每份 250 条，
  保底+按真实周量比例分配），env 侧 sampling_ratio=1.0 全量注入当周样本。
- 玩梗涌现环境**观测序列**（2026-09-10 定义的存量/流量语义，2026-09-12 起仅记录）：
  Stock_t = 过去 6 周 arena 供给总数（内生：注入 + agent 帖）→ 丰沛度 B_t；
  Flow_t 读取现实口径周新增帖量调度 emergence_flow_by_week → 空旷度 S_t；
  G_t = clamp(B^β·S^σ, 0.2, 3.0)。**不进入任何类型的决策**（θ 随 G 一并退役），
  仅写入 replay 与监控，供"退潮期"等描述性叙述引用。meme_emergence_mode 固定 normal。
- 议程设置（用户 2026-09-10 裁定）：官方媒体全程仅 W13 一条讣告帖（原文给定）。
  chronological / interest 臂在 W13 对全员置顶且不延伸；random 臂不置顶，讣告与
  其他截至当周已出现的帖子一样进入全历史均匀抽样池。其余真实数据帖均按普通内容处理
  （is_official=False）。
- feed 机制：chronological / interest 保持 2026-09-12 裁定的帖子生命周期（时间冷却
  + 曝光饱和 + 退场），interest 另用兴趣比例抽样；random 按本轮裁定忽略这些机制，
  直接从截至当周 Env 已出现的全部帖子中均匀抽满 10 槽。参数仍统一写入配置，random
  分支由 env 明确忽略，详见 manifest["feed_mechanism"]。
- （已作废）探索性反事实探针 interest_nog_s0：G 退役后该探针即正式模型，配置移入
  configs_retired_2factor/
  = interest_normal_s0 去掉玩梗型的涌现环境因子（θ=0，大家都用 D·R），门槛基数不动；
  作为历史证据保留（见 EXPERIMENT.md「no-G 探针 → 已升格为正式模型」节）。
- init/init_config.json 为标准 CLI 默认配置（= configs/anchored_v1_interest_s0.json）。

仅使用标准库；由 `experiment-config run` 执行。
"""

import importlib.util
import json
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------
script_dir = Path(__file__).parent                      # hypothesis_4/experiment_1/init
workspace_root = script_dir.parents[2]                  # workspace 根
assets_dir = workspace_root / "custom" / "envs" / "curation_assets"
personas_path = workspace_root / "custom" / "agents" / "curation_personas.py"

FULL_INJECTION_PATH = assets_dir / "injection_posts.json"
VOCAB_PATH = assets_dir / "vocabs.json"

configs_dir = script_dir / "configs"
configs_dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 实验结构常量（用户 2026-09-08 裁定）
# ---------------------------------------------------------------------------
ALGORITHMS = ["random", "chronological", "interest"]
# 2026-09-12 用户裁定：玩梗涌现模式（normal / sustained_hot）随 G 退役——θ≡0 时冻结 S
# 不产生任何行为差异，故设计降为单因子。保留常量以固定配置里的 meme_emergence_mode。
EMERGENCE_MODES = ["normal"]
SEEDS = [0, 1, 2]
ROUND_TAG = "anchored_v1"  # 新一轮独立命名，避免与历史 U=D·R run/config 混淆

# 用户 2026-09-10 裁定：按发帖人类型占比（不再按内容划分）——
# 用户 2026-09-13 更正：营销23% / 悼念22% / 其他21% / 玩梗19% / 讨论教育15%。
POPULATION_COUNTS = {"meme": 19, "mourning": 22, "marketing": 23, "education": 15, "other": 21}
POPULATION_SEED = 42          # 群体生成种子：全 9 配置共享同一群体
VOCAB_SAMPLE_SEED = POPULATION_SEED + 1  # 各 agent 类型词表抽样子种子（独立于群体 rng）
TYPE_VOCAB_N = 40             # 每个 agent 注入其类型词表的词数（用户裁定：发言用词表词组织语言）
SAMPLE_SEED_OFFSET = 777      # 注入样本抽样种子 = seed + 777

START_WEEK = "2026-W12"
EVENT_WEEK = "2026-W13"
NUM_TICKS = 11                # W12 -> W22
FEED_SIZE = 10                 # 用户 2026-09-10 裁定：每 agent 每周信息流 10 条

# ---------------------------------------------------------------------------
# feed 机制参数（用户 2026-09-12 裁定：生命周期 + 曝光饱和 + 比例抽样）
#
# 诊断（hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md）：烟测中兴趣臂
# (a) 候选集是全历史档案、年龄只是加性加成 → 老帖霸屏（W12-W15 帖吃掉 61.8% 曝光）；
# (b) 打分无 agent 相关项 + "取 top-k" → 同类型 agent 共享同一份 feed（逐 agent sd=0）
#     → D 的输入退化成 {0,1} → W18→W19 发言悬崖。
# 实测排除：寿命衰减单独、±20/30/50% 排序抖动、硬性曝光上限（会饿死早期 feed）。
# ---------------------------------------------------------------------------
LIFE_HALF_LIFE_WEEKS = 1.5     # 时间冷却半衰期（周）：1.5 周龄生命折半
LIFE_SATURATION_SCALE = 20.0   # 曝光饱和尺度：累计曝光达该值生命折半
LIFE_RETIRE_FLOOR = 0.35       # 退场线：时间生命低于此值退出候选池（≈3 周流通窗口）
#                              预飞实测（100 agents × 11 周）：0.05→6.5 周窗口，age≥3 槽位占 60%；
#                              0.35→3 周窗口，age≥3 = 0.00、top-10% 曝光集中度 0.24、
#                              零曝光帖 0.06、share_own 逐 agent sd 0.12（基线分别为 0.60/0.29/0.64/0.54/0.00）
INTEREST_SAMPLE_TEMP = 4.0     # 兴趣比例抽样温度（<=0 退化为确定性 top-k 消融档）
# 议程设置（用户 2026-09-12/13 裁定）：chronological / interest 臂在事件周（W13）
# 为每个 agent 的 feed 保底注入 N 条哀悼帖（按哀悼倾向分取全池前 N 条、全员相同，
# 等效"讣告 + 头版哀悼"的强制曝光）。random_global 强反事实明确忽略该参数。
# 代理实测（2026-09-13 修正同构缺口与代理不可复现后，30 seed，真实 W13 悼念份额 0.414）：
#   N=0 → 0.310（Δ−0.104 ❌，规则必要性）/ N=2 → 0.431 ✅ / N=3 → 0.462 ✅ /
#   N=4 → 0.455 ✅ / **N=5（当前值）→ 0.515（Δ+0.101 ❌）** / N=6 → 0.581 ❌
#   N≥2 时 W13 悼念帖数恒为 22（悼念型全员发言），份额差异来自分母。
# **N 的取值待用户裁定**；下表见 EXPERIMENT.md「保底条数 N 待裁定」节。
EVENT_WEEK_MOURNING_FLOOR = 5

# 250 条周分配：保底 15/周×11=165，余 85 按真实周量比例分配（和=250）。
INJECTION_ALLOCATION = {
    "2026-W12": 17,
    "2026-W13": 35,
    "2026-W14": 30,
    "2026-W15": 24,
    "2026-W16": 22,
    "2026-W17": 19,
    "2026-W18": 18,
    "2026-W19": 18,
    "2026-W20": 20,
    "2026-W21": 23,
    "2026-W22": 24,
}
assert sum(INJECTION_ALLOCATION.values()) == 250

# 议程设置重设计（用户 2026-09-10 裁定）：官方媒体全程仅此一条帖子，W13 注入；
# chronological / interest 臂对全员置顶且不延伸，random 臂不置顶并把它当作普通历史帖
# 等概率抽取。除此之外官方媒体无任何其他作用——其余真实数据帖一律按普通内容处理
# （is_official=False）。
# W13 配额 = 34 条普通抽样 + 1 条讣告帖 = 35（总注入量维持 250）。
ANNOUNCEMENT_WEEK = "2026-W13"
ANNOUNCEMENT_POST: dict = {
    "pid": "official_w13_announcement",
    "week": ANNOUNCEMENT_WEEK,
    "type": "mourning",  # 讣告报道，判类器同向（去世/抢救无效/猝死等哀悼词）
    "author": "官方媒体",
    "is_official": True,
    "content": (
        "今晚（3月24日），苏州峰学蔚来教育科技有限公司发布讣告称，张雪峰因突发疾病，"
        "经抢救无效不幸去世。记者了解到，今天中午12点26分，张雪峰在公司跑步后出现不适，"
        "被紧急送至医院。遗憾的是，经全力抢救无效于下午3点50分不幸去世。"
        "医院诊断，原因为心源性猝死。"
    ),
}

# steps.yaml：1 tick = 1 周 = 604800 秒；start_t = W12 周一。
STEPS_YAML = """\
start_t: "2026-03-16T00:00:00"
steps:
  - type: run
    num_steps: 11
    tick: 604800
"""

# ---------------------------------------------------------------------------
# 1. 加载共享 agent 群体（build_population 仅用 stdlib random）
# ---------------------------------------------------------------------------
spec = importlib.util.spec_from_file_location("curation_personas", personas_path)
personas_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(personas_mod)

population = personas_mod.build_population(POPULATION_COUNTS, seed=POPULATION_SEED)
assert len(population) == 100, f"population size = {len(population)}"

# env 侧 agent_types：{str(agent_id): type}，供兴趣匹配与供给口径统计。
agent_types_map = {str(p["id"]): p["agent_type"] for p in population}

# ---------------------------------------------------------------------------
# 1b. 类型词表注入（用户裁定：agent 发言须用本类型词表中的词组织语言）
# 词源与 env 判类器一致（仅 main + meme 四列表；aux/pruned 不参与）：
# meme = linkage 全量 + strong 抽样；其余主类 = main 抽样；other = 空。
# 每个 agent 抽 40 词作为"个人常用词库"，确定性（Random(43)），全 9 配置共享。
# ---------------------------------------------------------------------------
vocab_doc = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
vocab_rng = random.Random(VOCAB_SAMPLE_SEED)


def _type_vocab_source(agent_type: str) -> list[str]:
    if agent_type == "meme":
        meme = vocab_doc["meme"]
        linkage = list(meme["linkage"])
        strong_n = max(0, TYPE_VOCAB_N - len(linkage))
        return linkage + vocab_rng.sample(list(meme["strong"]), min(strong_n, len(meme["strong"])))
    if agent_type in ("mourning", "marketing", "education"):
        main = list(vocab_doc[agent_type]["main"])
        return vocab_rng.sample(main, min(TYPE_VOCAB_N, len(main)))
    return []  # other：无词表约束


type_vocab_by_id = {p["id"]: _type_vocab_source(p["agent_type"]) for p in population}

agent_specs = [
    {
        "agent_id": p["id"],
        "agent_type": "CurationDiscourseAgent",
        # kwargs 平铺：框架将 id 之外的键全部落入 profile（config 仅保留框架识别键，
        # 本 agent 的 max_content_chars / feed_highlight_n 用代码默认值 300 / 6）。
        "kwargs": {
            "id": p["id"],
            "name": p["name"],
            "agent_type": p["agent_type"],
            "persona": p["persona"],
            "params": p["params"],
            "type_vocab": type_vocab_by_id[p["id"]],
        },
    }
    for p in population
]

# ---------------------------------------------------------------------------
# 2. 按 seed 预抽样注入样本（每份 250 条；schema 与 injection_posts.json 一致）
#
# 抽样方法：分层比例抽样——每周池先按 官方/非官方 分层，层内再按帖子类型
# （数据集标签）分层，各层用最大余数法把当周配额 k 按比例分配到组。
# 因此每周样本的类型构成与官方占比**确定性地**贴合当周真实构成（误差 ≤ 整数取整），
# 不存在简单随机抽样的偶发偏斜；随机性只体现在"组内抽哪几条"。
# ---------------------------------------------------------------------------
full_data = json.loads(FULL_INJECTION_PATH.read_text(encoding="utf-8"))
all_posts = full_data["posts"]
by_week: dict[str, list[dict]] = {}
for rec in all_posts:
    by_week.setdefault(str(rec["week"]), []).append(rec)

# ---------------------------------------------------------------------------
# 2b. 玩梗涌现环境流量调度（emergence_flow_by_week；用户 2026-09-10 存量/流量语义）
#
# S_t（空旷度）读取现实口径周新增帖量：sim arena 的流量被 250 条注入预算压缩
# （保底 15/周托底谷值、洪峰仅 ~2×，agent 供给又平稳 → arena 总流量峰谷比 ~1.6×，
# 远弱于现实 ~9×），单靠内生计数表达不出真实洪峰/退潮节律，S 会失去臂间对比度。
# 故调度取真实数据各周全量帖数（W12–W22），env 内归一化 h(x)=K_f/(K_f+x)、
# 基线周（W12）=1；B_t（丰沛度）保持内生（arena 供给），保留 meme 再拥挤反哺
# 存量的自限反馈。sustained_hot 臂在 env 内冻结 S，不需要单独调度。
# ---------------------------------------------------------------------------
EMERGENCE_FLOW_BY_WEEK: dict[str, int] = {
    week: len(by_week.get(week, [])) for week in INJECTION_ALLOCATION
}
assert all(v > 0 for v in EMERGENCE_FLOW_BY_WEEK.values()), "涌现流量调度存在空周"
print(f"✓ 涌现流量调度（现实口径周新增）：{EMERGENCE_FLOW_BY_WEEK}")


def _largest_remainder(total_k: int, groups: dict[str, list]) -> dict[str, int]:
    """按组大小比例把 total_k 分配到各组（最大余数法），和恰为 total_k。"""
    n = sum(len(g) for g in groups.values())
    quotas = {t: total_k * len(g) / n for t, g in groups.items()}
    alloc = {t: min(int(q), len(groups[t])) for t, q in quotas.items()}
    order = sorted(groups, key=lambda t: (-(quotas[t] - int(quotas[t])), t))
    i = 0
    while sum(alloc.values()) < total_k and i < 100000:
        t = order[i % len(order)]
        if alloc[t] < len(groups[t]):
            alloc[t] += 1
        i += 1
    assert sum(alloc.values()) == total_k, f"最大余数分配失败: {alloc} != {total_k}"
    return alloc


def stratified_week_sample(pool: list[dict], k: int, rng: random.Random) -> list[dict]:
    """当周池的类型分层比例抽样（最大余数法）：样本类型构成确定性贴合当周真实分布，
    随机性只体现在"类型组内抽哪几条"。（2026-09-10 裁定：官方媒体仅 W13 单条讣告帖，
    真实数据帖不再按官方/非官方分层，一律按普通内容处理。）"""
    k = min(k, len(pool))
    by_type: dict[str, list] = {}
    for p in pool:
        by_type.setdefault(str(p.get("type", "other")), []).append(p)
    alloc_t = _largest_remainder(k, by_type)
    picks: list[dict] = []
    for t in sorted(by_type):
        if alloc_t[t] > 0:
            picks.extend(rng.sample(by_type[t], alloc_t[t]))
    rng.shuffle(picks)
    return picks


sample_paths: dict[int, str] = {}
for seed in SEEDS:
    rng = random.Random(seed + SAMPLE_SEED_OFFSET)
    sampled: list[dict] = []
    for week in sorted(INJECTION_ALLOCATION):
        k = INJECTION_ALLOCATION[week]
        pool = by_week.get(week, [])
        # W13 留 1 个名额给官方讣告帖，普通抽样 k-1 条。
        k_regular = k - 1 if week == ANNOUNCEMENT_WEEK else k
        assert len(pool) >= k_regular, f"{week} 池仅 {len(pool)} 条，不足分配 {k_regular}"
        # 官方媒体无其他作用：真实数据帖一律按普通内容处理（is_official=False）。
        sampled.extend(
            {**p, "is_official": False} for p in stratified_week_sample(pool, k_regular, rng)
        )
        if week == ANNOUNCEMENT_WEEK:
            sampled.append(dict(ANNOUNCEMENT_POST))
    sampled.sort(key=lambda p: (p["week"], str(p["pid"])))  # pid 混合 int/str（讣告帖），统一按字符串序
    weekly_counts = {w: sum(1 for p in sampled if p["week"] == w) for w in sorted(INJECTION_ALLOCATION)}
    weekly_type_counts = {
        w: {t: sum(1 for p in sampled if p["week"] == w and p.get("type") == t)
            for t in sorted({p.get("type") for p in sampled if p["week"] == w})}
        for w in sorted(INJECTION_ALLOCATION)
    }
    sample_doc = {
        "meta": {
            "source": "custom/envs/curation_assets/injection_posts.json",
            "purpose": ("hypothesis_4 experiment_1 预抽样注入样本（全程 250 条，用户 2026-09-09 裁定；"
                        "2026-09-10 议程重设计：官方媒体仅 W13 单条讣告帖，其余真实帖按普通内容处理）"),
            "seed": seed,
            "sample_rng": f"Random({seed}+{SAMPLE_SEED_OFFSET})",
            "sampling_method": "每周池内类型分层比例抽样（最大余数法），样本构成确定性贴合当周真实构成",
            "allocation": INJECTION_ALLOCATION,
            "official_announcement": {
                "pid": ANNOUNCEMENT_POST["pid"],
                "week": ANNOUNCEMENT_WEEK,
                "type": ANNOUNCEMENT_POST["type"],
                "note": ("官方媒体全程唯一帖子（讣告，原文给定）；chronological / interest "
                         "臂 W13 对全员置顶，random 臂不置顶而作为普通历史帖参与均匀抽样"),
            },
            "rows_total": len(sampled),
            "weekly_counts": weekly_counts,
            "weekly_type_counts": weekly_type_counts,
            "official_counts": {
                w: sum(1 for p in sampled if p["week"] == w and p.get("is_official"))
                for w in sorted(INJECTION_ALLOCATION)
            },
        },
        "posts": sampled,
    }
    rel = f"hypothesis_4/experiment_1/init/injection_sample_s{seed}.json"
    (workspace_root / rel).write_text(json.dumps(sample_doc, ensure_ascii=False), encoding="utf-8")
    sample_paths[seed] = rel
    print(f"✓ 注入样本 s{seed}: {len(sampled)} 条 -> {rel}")

# ---------------------------------------------------------------------------
# 3. 生成新一轮 9 个 init_config 变体 + 默认 init_config.json
# ---------------------------------------------------------------------------

def make_config(algorithm: str, mode: str, seed: int, agents: list | None = None) -> dict:
    """组装一个 init_config 变体。agents=None 使用新一轮 9 配置的共享群体。"""
    return {
        "env_modules": [
            {
                "module_type": "CurationDynamicsSpace",
                "kwargs": {
                    # —— 实验因子（cell 内锁定）——
                    "recommendation_algorithm": algorithm,
                    "meme_emergence_mode": mode,  # normal / sustained_hot（W13 后冻结 S）
                    "random_seed": seed,
                    # —— 玩梗涌现环境（用户 2026-09-10 存量/流量语义）——
                    "emergence_flow_by_week": EMERGENCE_FLOW_BY_WEEK,
                    # 其余涌现参数（emergence_window_stock=6 / emergence_ka /
                    # emergence_kf / emergence_beta=1.0 / emergence_sigma=1.0 /
                    # gain_min=0.2 / gain_max=3.0）用 env 默认值，
                    # 待校准与敏感性分析（U2）统一处理。
                    # —— feed 机制（用户 2026-09-12 裁定，见 SMOKE_DIAGNOSIS_w19_cliff.md）——
                    # chronological / interest：老帖随时间冷却、被推得多也冷却、寿终退场；
                    # random：这些参数仍为跨配置 schema 一致性而写入，但 env 分支明确忽略。
                    # 兴趣比例抽样：把"取分数最高的 feed_size 条"换成"按 exp(score/temp)
                    # 无放回抽 feed_size 条"，使每个 agent 的 feed 各不相同（修 W19 悬崖）。
                    "life_half_life_weeks": LIFE_HALF_LIFE_WEEKS,
                    "life_saturation_scale": LIFE_SATURATION_SCALE,
                    "life_retire_floor": LIFE_RETIRE_FLOOR,
                    "interest_sample_temp": INTEREST_SAMPLE_TEMP,
                    # —— 议程设置（用户 2026-09-12/13 裁定；random 分支忽略）——
                    "event_week_mourning_floor": EVENT_WEEK_MOURNING_FLOOR,
                    # —— 数据资产 ——
                    "injection_data_path": sample_paths[seed],
                    "vocab_path": "custom/envs/curation_assets/vocabs.json",
                    "sampling_ratio": 1.0,   # 样本文件即全量，env 不再二次抽样
                    # —— 群体口径 ——
                    "agent_types": agent_types_map,
                    # —— 时间结构 ——
                    "start_week": START_WEEK,
                    "num_ticks": NUM_TICKS,
                    "event_week": EVENT_WEEK,
                    "feed_size": FEED_SIZE,
                    # —— 议程设置（用户 2026-09-10 裁定；random 分支忽略）——
                    "official_pin_extend_weeks": 0,  # chrono/interest：仅 W13 置顶，不延伸
                    # 其余 kwargs（alpha / beta / gamma / interest_noise_eps /
                    # exposure_mode）用 spec 默认值。
                },
            }
        ],
        "agents": agent_specs if agents is None else agents,
    }


run_ids: list[str] = []
for algorithm in ALGORITHMS:
    for mode in EMERGENCE_MODES:
        for seed in SEEDS:
            run_id = f"{ROUND_TAG}_{algorithm}_s{seed}"
            cfg = make_config(algorithm, mode, seed)
            (configs_dir / f"{run_id}.json").write_text(
                json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            run_ids.append(run_id)
            print(f"✓ {run_id}")

# 默认 init_config.json = 核心处理臂（interest, seed 0），供标准 CLI / 冒烟。
default_run_id = f"{ROUND_TAG}_interest_s0"
(script_dir / "init_config.json").write_text(
    (configs_dir / f"{default_run_id}.json").read_text(encoding="utf-8"), encoding="utf-8"
)
print(f"✓ init_config.json (= configs/{default_run_id}.json)")

# ---------------------------------------------------------------------------
# 3b.（已作废）no-G 探针配置
#
# 2026-09-12 用户裁定「G 没有生效，直接去掉 G —— 只由沉默螺旋和注意力衰减两条规则约束
# Agent」之后，探针即成为正式模型（U = D·R），故不再单独生成 interest_nog_s0.json：
# 它对应的 run 已跑完并作为 G 退役的证据留痕（configs_retired_2factor/interest_nog_s0.json，
# 结果见 SMOKE_DIAGNOSIS_w19_cliff.md §五之三）。
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 4. steps.yaml + 批次 manifest
# ---------------------------------------------------------------------------
(script_dir / "steps.yaml").write_text(STEPS_YAML, encoding="utf-8")
print("✓ steps.yaml (start_t=2026-03-16, 11 × 604800s)")

manifest = {
    "experiment": "hypothesis_4/experiment_1",
    "round": ROUND_TAG,
    "design": ("锚定式效用新一轮：单因子 3 臂（random/chronological/interest）× 3 seeds = 9 runs；"
               "random 配置键的操作语义为 random_global 强反事实：从截至当周 Env 已出现的"
               "全部帖子中全 10 槽均匀无放回抽样，不使用生命周期、时间、兴趣、热度、累计曝光，"
               "且不执行官方置顶或 W13 哀悼保底；chronological 与 interest 保持原定义；"
               "（2026-09-12 用户裁定：玩梗涌现环境增益 G 退役，第二因子 sustained_hot 随之失效；"
               "2026-09-14 用户裁定：U = B_i + R·(D−B_i) ≥ activity，疲劳使事件冲击回归"
               "常态锚点而非归零）"),
    "run_ids": run_ids,
    "retired_probe": {
        "note": ("interest_nog_s0（no-G 探针）已跑完并升格为正式模型的等价物——"
                 "G 退役后的上一轮模型为 U = D·R；配置移入 configs_retired_2factor/，"
                 "实测结果见 SMOKE_DIAGNOSIS_w19_cliff.md §五之三"),
    },
    "factors": {"recommendation_algorithm": ALGORITHMS, "random_seed": SEEDS},
    "fixed_kwargs": {"meme_emergence_mode": EMERGENCE_MODES[0], "note": "退役因子，固定 normal"},
    "population": {
        "counts": POPULATION_COUNTS,
        "seed": POPULATION_SEED,
        "caliber": "按发帖人类型占比统计（用户 2026-09-10 裁定，不再按内容划分）",
        "note": "9 个配置共享同一群体（id-类型打散，人设含两机制类型化表现 + 发言决策数值参数 params）",
        "type_vocab": {
            "rule": "agent 发言用本类型词表词组织语言（用户 2026-09-09 裁定）；词源=env 判类器同口径 main/meme 列表",
            "per_agent_n": TYPE_VOCAB_N,
            "sample_seed": VOCAB_SAMPLE_SEED,
            "meme": "linkage 全量 + strong 抽样；mourning/marketing/education=main 抽样；other=空",
        },
        "speak_decision": "锚定式表达效用模型（无 LLM，用户 2026-09-14 裁定）：U=B_i+R·(D−B_i)，发言当且仅当 U≥activity。D=1+(alpha_D·s_i)·tanh(1.5·(share_own−base)/base)；alpha_D=0.4296954756，只缩放s而不移动D=1的中性中心。R=exp(−λ_i·cum_own/15)。B_i固定自W05-W12常态供给映射，alpha_D和五类λ只用W13-W18统一标定，W19-W22留出。R=1时U=D，R→0时U→B_i，故衰减有常态下限而不归零。params随profile显式下发activity/spiral/spiral_scale/decay/baseline_utility；共享公式位于curation_mechanisms.anchored_utility。原emergence/θ与G维持退役，env侧B_t/S_t/G_t仅记录。",
        "anchored_calibration": {
            "selection": "B_i fixed from W05-W12; alpha_D and lambda selected on W13-W18 only; W19-W22 held out",
            "alpha_D": personas_mod.CALIBRATED_ALPHA_D,
            "baseline_utility": personas_mod.BASELINE_UTILITY,
            "lambda_mean": personas_mod.CALIBRATED_LAMBDA_MEAN,
            "source": "data/anchored_utility_prediction.json",
        },
        "content_grounding": "发言内容须基于本周 feed 前 5 条（feed_context_n=5）：回应/讨论/二创/跟帖（用户 2026-09-10 裁定）",
    },
    "feed_mechanism": {
        "adopted_from": "hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md（用户 2026-09-12 裁定）",
        "post_lifecycle": {
            "scope": "仅 chronological / interest 臂用于候选资格与打分；random 臂明确忽略",
            "state": "每帖 life（时间生命，创建时 1.0，每周 × weekly_decay）",
            "vitality": "vitality = life × 0.5**(累计曝光 / life_saturation_scale)，打分用",
            "life_half_life_weeks": LIFE_HALF_LIFE_WEEKS,
            "life_saturation_scale": LIFE_SATURATION_SCALE,
            "life_retire_floor": LIFE_RETIRE_FLOOR,
            "note": ("以下诊断与退场规则只约束 chronological / interest。被实测排除的形态："
                     "硬性'每帖每周最多推给 C 个 agent'会饿死早期 feed"
                     "（W12 仅 47 帖，C=2 只供 94 槽位而当周需求 1000 槽位），故曝光上限"
                     "以饱和衰减实现同一意图；退场只按时间生命判，避免高热帖被提前踢出池子"),
        },
        "event_week_mourning_floor": {
            "value": EVENT_WEEK_MOURNING_FLOOR,
            "scope": "仅 chronological / interest；random_global 不执行保底",
            "rule": ("chronological / interest 臂在事件周（W13）为每个 agent 的 feed 保底注入 N 条哀悼帖：取全池（未退场、非置顶、"
                     "**非 noise 语料噪声**）中哀悼倾向分最高的 N 条，全员相同，紧接官方置顶之后占槽位；"
                     "余下槽位照常按算法从剩余候选池选取。random 臂不执行该规则。"
                     "候选资格见共享纯函数 curation_mechanisms.floor_eligible（env 与校准同源）"),
            "why": ("议程设置：讣告/头版哀悼的强制曝光 —— 让事件周全体 agent 都暴露于哀悼叙事。"
                    "代理实测（2026-09-13 修正同构缺口 + 修复代理平票次序不可复现后，30 seed）："
                    "无此规则时 W13 悼念份额低至 0.310（真实 0.414，Δ-0.104 超判据）；"
                    "N=5（当前值）时 0.515（Δ+0.101，反向超判据）；N=2/3/4 档落在判据内。"
                    "**保底条数 N 的取值待用户裁定**（见 EXPERIMENT.md 的 N 扫描表）"),
            "exclude_types_note": ("用户 2026-09-13 补裁定（方案 B）：倾向分 = 命中数/(字数/50) 对短文本"
                                   "密度虚高，实测 2/3 seed 有 1 张 35–98 字的乱码 noise 帖挤进全员强制位，"
                                   "故候选池剔除 noise（mech.floor_eligible）。不限定必须为 mourning 类型"
                                   "（同 N=5 该档 0.555，比本口径 0.515 更差）。"
                                   "本过滤是口径清理、不是标定杠杆：开关对照 |Δ| ≤ 0.01 且符号不定，"
                                   "小于 seed 间噪声；事件周水平几乎完全由保底条数 N 决定"),
        },
        "interest_sampling": {
            "temperature": INTEREST_SAMPLE_TEMP,
            "rule": ("interest 臂把'按分数排序取前 feed_size 条'换成'按 exp(score/temp) 无放回抽"
                     " feed_size 条'；temp<=0 退化为确定性 top-k（消融档）"),
            "rng": "独立流 Random(random_seed + 3000)，同 seed 跨 cell 抽出同一序列，保证臂间可比",
            "why": ("烟测实测：只要保留确定性 top-10 且高分帖数 ≥ 10，选出的集合就与 agent 无关"
                    "（同类型 18 人 share_own 的逐 agent sd = 0）→ D 的输入退化成 {0,1}"),
        },
        "cross_arm_comparability": {
            "shared": ("三臂共享相同的 Agent 群体、当周及此前已注入/内生产生的帖子历史、"
                       "时间轴、表达效用与每周 feed_size=10；均不得访问未来帖子"),
            "random_global": ("配置键为 random；候选池=截至当周 Env 已出现的全部帖子；全 10 槽"
                              "均匀无放回抽样；忽略 life/退场、发布时间、兴趣、热度、累计曝光、"
                              "官方置顶与 W13 哀悼保底"),
            "chronological": "保持原定义：从未退场活帖池中按时间倒序取最新，并保留共同议程槽位",
            "interest": "保持原定义：从未退场活帖池中按兴趣分比例抽样，并保留共同议程槽位",
            "identification_note": ("random_global 是同时移除时间性可得性与强制议程设置的强反事实；"
                                    "因此 random 与另两臂的差异是整体策展制度效应，不宜仅解释为"
                                    "候选池相同条件下的排序效应"),
            "acceptance_note": ("同周三臂不再要求 feed_live_pool 或置顶槽位数相等；应分别检查："
                                "random 的候选池等于截至当周全部已出现帖子且强制槽位为 0，"
                                "chronological / interest 继续遵守生命周期与原议程规则"),
        },
        "replay_columns": [
            "feed_live_pool", "feed_sample_temp", "feed_half_life_weeks",
            "feed_saturation_scale", "exposure_slots_age0/1/2/3plus",
        ],
    },
    "injection": {
        "total_posts_per_run": 250,
        "allocation": INJECTION_ALLOCATION,
        "sample_seed_offset": SAMPLE_SEED_OFFSET,
        "sampling_method": "每周池内类型分层比例抽样（最大余数法），按当周帖子（内容）类型占比分配配额，构成确定性贴合当周真实分布；与 agent 群体的发帖人口径比例（19/22/23/15/21）相互独立、互不混用（用户 2026-09-10 确认）；真实数据帖一律按普通内容处理",
        "official_announcement": ("官方媒体全程仅 W13 一条讣告帖（原文给定）；chronological / "
                                  "interest 臂 W13 全员置顶且不延伸，random 臂不置顶而与其他"
                                  "截至当周已出现帖子等概率参与全历史抽样；官方无其他作用"),
        "sampling_ratio": 1.0,
        "sample_files": {str(s): sample_paths[s] for s in SEEDS},
    },
    "emergence_env": {
        "status": "2026-09-12 退役：仅作为观测序列写入 replay 与监控，不进入任何类型的决策",
        "semantics": "存量/流量（用户 2026-09-10 裁定）：总帖子越丰沛越易诞生 meme（B_t），当期新增越少越空旷越宜传播（S_t）",
        "stock": "Stock_t = 过去 emergence_window_stock=6 周 arena 供给总数（内生：注入+agent 帖），B_t=f(Stock_t)/f(Stock_base)，f(x)=x/(x+K_a)，K_a 默认=注入计划事件周窗口存量",
        "flow": "Flow_t = 现实口径周新增帖量调度（真实数据各周全量帖数，sim arena 流量被注入预算压缩故 S 读外生调度），S_t=h(Flow_t)/h(Flow_base)，h(x)=K_f/(K_f+x)，K_f 默认=调度基线周值",
        "gain": "G_t=clamp(B^β·S^σ,0.2,3.0)，β=σ=1 起步；仅玩梗型 θ=1.0 进入效用，其余 θ=0",
        "sustained_hot": "反事实臂：事件周（W13）后 S 冻结在事件周记录值，B 保持内生",
        "flow_schedule": EMERGENCE_FLOW_BY_WEEK,
    },
    "steps": {"start_t": "2026-03-16T00:00:00", "num_steps": NUM_TICKS, "tick_seconds": 604800},
    "deferred_defaults": {
        "note": ("interest 臂 α/γ 取 DesignSpec 默认值；涌现窗口/αβσ 与 K_a/K_f 用 env 默认，"
                 "待校准与敏感性分析（U2）。β 已废弃（2026-09-09 裁定：倾向分替代硬类型命中+词表重合项），"
                 "保留 kwarg 兼容、不参与评分。2026-09-10 机制重设计：悼念规范压力（norm_pressure/w_* 权重）整体退役。"
                 "2026-09-12：加性时新项 γ·max(0,1−age/recency_max_age_weeks) 退役，"
                 "时新改由帖子生命力的乘性衰减承载（recency_max_age_weeks 保留 kwarg 兼容、不参与评分）"),
        "alpha": 1.0, "beta_deprecated": None, "gamma": 0.5,
        "recency_max_age_weeks_deprecated": None,
        "emergence_window_stock": 6, "emergence_beta": 1.0, "emergence_sigma": 1.0,
        "emergence_gain_clamp": [0.2, 3.0],
    },
    "default_init_config": default_run_id,
    "run_command": (
        "$PYTHON_PATH .agentsociety/bin/ags.py run-experiment start "
        "--hypothesis-id 4 --experiment-id 1 "
        "--init-config hypothesis_4/experiment_1/init/configs/<run_id>.json "
        "--run-id <run_id>"
    ),
}
(configs_dir / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ configs/manifest.json")

print(f"\n配置生成完成：{len(run_ids)} runs（3 臂 × 3 seeds），100 agents，{NUM_TICKS} ticks。")
