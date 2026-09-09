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
        },
    }
    for p in population
]

# ---------------------------------------------------------------------------
# 2. 按 seed 预抽样注入样本（每份 250 条；schema 与 injection_posts.json 一致）
# ---------------------------------------------------------------------------
full_data = json.loads(FULL_INJECTION_PATH.read_text(encoding="utf-8"))
all_posts = full_data["posts"]
by_week: dict[str, list[dict]] = {}
for rec in all_posts:
    by_week.setdefault(str(rec["week"]), []).append(rec)

sample_paths: dict[int, str] = {}
for seed in SEEDS:
    rng = random.Random(seed + SAMPLE_SEED_OFFSET)
    sampled: list[dict] = []
    for week in sorted(INJECTION_ALLOCATION):
        k = INJECTION_ALLOCATION[week]
        pool = by_week.get(week, [])
        assert len(pool) >= k, f"{week} 池仅 {len(pool)} 条，不足分配 {k}"
        picks = rng.sample(pool, k)
        # 官方帖保底：事件周及次周至少 1 条 is_official（不够则从池中换入）。
        if week in OFFICIAL_GUARANTEE_WEEKS and not any(p.get("is_official") for p in picks):
            picked_ids = {p["pid"] for p in picks}
            officials = [p for p in pool if p.get("is_official") and p["pid"] not in picked_ids]
            if officials:
                swappable = [p for p in picks if not p.get("is_official")]
                picks[picks.index(rng.choice(swappable))] = rng.choice(officials)
        sampled.extend(picks)
    sampled.sort(key=lambda p: (p["week"], p["pid"]))
    weekly_counts = {w: sum(1 for p in sampled if p["week"] == w) for w in sorted(INJECTION_ALLOCATION)}
    sample_doc = {
        "meta": {
            "source": "custom/envs/curation_assets/injection_posts.json",
            "purpose": "hypothesis_4 experiment_1 预抽样注入样本（全程 250 条，用户 2026-09-09 裁定）",
            "seed": seed,
            "sample_rng": f"Random({seed}+{SAMPLE_SEED_OFFSET})",
            "allocation": INJECTION_ALLOCATION,
            "official_guarantee_weeks": list(OFFICIAL_GUARANTEE_WEEKS),
            "rows_total": len(sampled),
            "weekly_counts": weekly_counts,
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
    },
    "injection": {
        "total_posts_per_run": 250,
        "allocation": INJECTION_ALLOCATION,
        "sample_seed_offset": SAMPLE_SEED_OFFSET,
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
