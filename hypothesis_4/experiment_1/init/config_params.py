"""配置参数生成脚本（hypothesis_4 / experiment_1）

生成 CurationDynamicsSpace × CurationDiscourseAgent 的全因子实验配置：

- 3 推荐算法（random / chronological / interest）× 2 悼念规范压力模式（decay / sustained）
  = 6 cells，每 cell 3 seeds（0/1/2）= 18 个 init_config 变体，写入 init/configs/。
- 100 个 agent（用户口径：梗41/悼念21/营销13/教育13/其他12），群体由
  custom/agents/curation_personas.build_population(seed=42) 生成，**18 个配置完全共享**。
- 真实帖子注入：按用户裁定「全程约 250 条」，从 custom/envs/curation_assets/
  injection_posts.json 的 W12–W22 池中按 seed 预抽样 3 份样本文件（每份 250 条，
  保底+按真实周量比例分配），env 侧 sampling_ratio=1.0 全量注入当周样本。
- init/init_config.json 为标准 CLI 默认配置（= configs/interest_decay_s0.json）。

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
PRESSURE_MODES = ["decay", "sustained"]
SEEDS = [0, 1, 2]

POPULATION_COUNTS = {"meme": 41, "mourning": 21, "marketing": 13, "education": 13, "other": 12}
POPULATION_SEED = 42          # 群体生成种子：全 18 配置共享同一群体
VOCAB_SAMPLE_SEED = POPULATION_SEED + 1  # 各 agent 类型词表抽样子种子（独立于群体 rng）
TYPE_VOCAB_N = 40             # 每个 agent 注入其类型词表的词数（用户裁定：发言用词表词组织语言）
SAMPLE_SEED_OFFSET = 777      # 注入样本抽样种子 = seed + 777

START_WEEK = "2026-W12"
EVENT_WEEK = "2026-W13"
NUM_TICKS = 11                # W12 -> W22
FEED_SIZE = 20

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
# 事件周及其后一周保证至少 1 条官方帖（官方议程设置处理的载体）。
OFFICIAL_GUARANTEE_WEEKS = ("2026-W13", "2026-W14")

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
# 每个 agent 抽 40 词作为"个人常用词库"，确定性（Random(43)），全 18 配置共享。
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


def stratified_week_sample(pool: list[dict], k: int, week: str, rng: random.Random) -> list[dict]:
    """当周池的两级分层比例抽样：官方/非官方 → 类型；W13/W14 官方保底 1 条。"""
    k = min(k, len(pool))
    official = [p for p in pool if p.get("is_official")]
    regular = [p for p in pool if not p.get("is_official")]
    alloc_top = _largest_remainder(k, {"official": official, "regular": regular})
    if week in OFFICIAL_GUARANTEE_WEEKS and alloc_top["official"] == 0 and official:
        alloc_top["official"] = 1
        alloc_top["regular"] -= 1
    picks: list[dict] = []
    for stratum, group in (("official", official), ("regular", regular)):
        kk = alloc_top[stratum]
        if kk <= 0:
            continue
        by_type: dict[str, list] = {}
        for p in group:
            by_type.setdefault(str(p.get("type", "other")), []).append(p)
        alloc_t = _largest_remainder(kk, by_type)
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
        assert len(pool) >= k, f"{week} 池仅 {len(pool)} 条，不足分配 {k}"
        sampled.extend(stratified_week_sample(pool, k, week, rng))
    sampled.sort(key=lambda p: (p["week"], p["pid"]))
    weekly_counts = {w: sum(1 for p in sampled if p["week"] == w) for w in sorted(INJECTION_ALLOCATION)}
    weekly_type_counts = {
        w: {t: sum(1 for p in sampled if p["week"] == w and p.get("type") == t)
            for t in sorted({p.get("type") for p in sampled if p["week"] == w})}
        for w in sorted(INJECTION_ALLOCATION)
    }
    sample_doc = {
        "meta": {
            "source": "custom/envs/curation_assets/injection_posts.json",
            "purpose": "hypothesis_4 experiment_1 预抽样注入样本（全程 250 条，用户 2026-09-09 裁定）",
            "seed": seed,
            "sample_rng": f"Random({seed}+{SAMPLE_SEED_OFFSET})",
            "sampling_method": "每周池内两级分层比例抽样（官方/非官方×类型，最大余数法），样本构成确定性贴合当周真实构成",
            "allocation": INJECTION_ALLOCATION,
            "official_guarantee_weeks": list(OFFICIAL_GUARANTEE_WEEKS),
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
# 3. 生成 18 个 init_config 变体 + 默认 init_config.json
# ---------------------------------------------------------------------------

def make_config(algorithm: str, pressure: str, seed: int) -> dict:
    return {
        "env_modules": [
            {
                "module_type": "CurationDynamicsSpace",
                "kwargs": {
                    # —— 实验因子（cell 内锁定）——
                    "recommendation_algorithm": algorithm,
                    "mourning_norm_pressure": pressure,
                    "random_seed": seed,
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
                    # 其余 kwargs（official_pin_extend_weeks / alpha / beta / gamma /
                    # interest_noise_eps / P_t 权重与阈值 / exposure_mode）用 spec 默认值，
                    # 待校准与敏感性分析（U2）统一处理。
                },
            }
        ],
        "agents": agent_specs,
    }


run_ids: list[str] = []
for algorithm in ALGORITHMS:
    for pressure in PRESSURE_MODES:
        for seed in SEEDS:
            run_id = f"{algorithm}_{pressure}_s{seed}"
            cfg = make_config(algorithm, pressure, seed)
            (configs_dir / f"{run_id}.json").write_text(
                json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            run_ids.append(run_id)
            print(f"✓ {run_id}")

# 默认 init_config.json = 核心处理 cell（interest × decay, seed 0），供标准 CLI / 冒烟。
default_run_id = "interest_decay_s0"
(script_dir / "init_config.json").write_text(
    (configs_dir / f"{default_run_id}.json").read_text(encoding="utf-8"), encoding="utf-8"
)
print(f"✓ init_config.json (= configs/{default_run_id}.json)")

# ---------------------------------------------------------------------------
# 4. steps.yaml + 批次 manifest
# ---------------------------------------------------------------------------
(script_dir / "steps.yaml").write_text(STEPS_YAML, encoding="utf-8")
print("✓ steps.yaml (start_t=2026-03-16, 11 × 604800s)")

manifest = {
    "experiment": "hypothesis_4/experiment_1",
    "design": "3 推荐算法 × 2 悼念规范压力 全因子，每 cell 3 seeds，共 18 runs",
    "run_ids": run_ids,
    "factors": {
        "recommendation_algorithm": ALGORITHMS,
        "mourning_norm_pressure": PRESSURE_MODES,
        "random_seed": SEEDS,
    },
    "population": {
        "counts": POPULATION_COUNTS,
        "seed": POPULATION_SEED,
        "note": "18 个配置共享同一群体（id-类型打散，人设含三机制类型化表现）",
        "type_vocab": {
            "rule": "agent 发言用本类型词表词组织语言（用户 2026-09-09 裁定）；词源=env 判类器同口径 main/meme 列表",
            "per_agent_n": TYPE_VOCAB_N,
            "sample_seed": VOCAB_SAMPLE_SEED,
            "meme": "linkage 全量 + strong 抽样；mourning/marketing/education=main 抽样；other=空",
        },
    },
    "injection": {
        "total_posts_per_run": 250,
        "allocation": INJECTION_ALLOCATION,
        "sample_seed_offset": SAMPLE_SEED_OFFSET,
        "sampling_method": "每周池内两级分层比例抽样（官方×类型，最大余数法），构成确定性贴合当周真实分布",
        "sampling_ratio": 1.0,
        "sample_files": {str(s): sample_paths[s] for s in SEEDS},
    },
    "steps": {"start_t": "2026-03-16T00:00:00", "num_steps": NUM_TICKS, "tick_seconds": 604800},
    "deferred_defaults": {
        "note": "interest 臂 α/β/γ 与 P_t 权重/阈值取 DesignSpec 默认值，待校准与敏感性分析（U2）",
        "alpha": 1.0, "beta": 1.0, "gamma": 0.5,
        "w_official": 0.3, "w_mourning": 0.4, "w_volume": 0.3,
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

print(f"\n配置生成完成：18 runs（6 cells × 3 seeds），100 agents，{NUM_TICKS} ticks。")
