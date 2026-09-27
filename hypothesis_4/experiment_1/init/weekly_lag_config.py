#!/usr/bin/env python3
"""Generate the approved weekly-lag timing revision without touching frozen artifacts.

The revision keeps each seed's existing 250-post sample byte-for-byte unchanged and
adds a separate 17-post W11 initialization sample.  Only the interest and random
arms are emitted; chronological is deliberately left on its existing exact-time
design.

Usage:
    python init/weekly_lag_config.py
    python init/weekly_lag_config.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_DIR = SCRIPT_DIR.parent
WORKSPACE_ROOT = EXPERIMENT_DIR.parent.parent
CONFIGS_DIR = SCRIPT_DIR / "configs"
FULL_INJECTION_PATH = (
    WORKSPACE_ROOT / "custom" / "envs" / "curation_assets" / "injection_posts.json"
)

ROUND_TAG = "weekly_lag1"
ARMS = ("interest", "random")
SEEDS = (0, 1, 2)
SOURCE_WEEK = "2026-W11"
AVAILABLE_WEEK = "2026-W12"
INITIAL_SAMPLE_N = 17
INITIAL_SAMPLE_SEED_OFFSET = 1777
OFFICIAL_SAME_WEEK_PIDS = ("official_w13_announcement",)
SOURCE_WEEKS = tuple(f"2026-W{week:02d}" for week in range(12, 23))

STEPS_TEXT = """\
start_t: "2026-03-16T00:00:00"
steps:
  - type: run
    num_steps: 11
    tick: 604800
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def largest_remainder(total: int, groups: dict[str, list[dict]]) -> dict[str, int]:
    population = sum(len(rows) for rows in groups.values())
    if total > population:
        raise ValueError(f"sample size {total} exceeds population {population}")
    quotas = {name: total * len(rows) / population for name, rows in groups.items()}
    allocation = {name: int(quota) for name, quota in quotas.items()}
    order = sorted(groups, key=lambda name: (-(quotas[name] - int(quotas[name])), name))
    index = 0
    while sum(allocation.values()) < total:
        name = order[index % len(order)]
        if allocation[name] < len(groups[name]):
            allocation[name] += 1
        index += 1
    return allocation


def stratified_sample(pool: list[dict], total: int, rng: random.Random) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for post in pool:
        groups.setdefault(str(post.get("type", "other")), []).append(post)
    allocation = largest_remainder(total, groups)
    selected: list[dict] = []
    for post_type in sorted(groups):
        selected.extend(rng.sample(groups[post_type], allocation[post_type]))
    rng.shuffle(selected)
    return selected


def base_sample_paths() -> list[Path]:
    return [SCRIPT_DIR / f"injection_sample_s{seed}.json" for seed in SEEDS]


def initial_sample_path(seed: int) -> Path:
    return SCRIPT_DIR / f"initial_sample_weekly_lag_s{seed}.json"


def config_path(arm: str, seed: int) -> Path:
    return CONFIGS_DIR / f"{ROUND_TAG}_{arm}_s{seed}.json"


def source_counts() -> dict[str, int]:
    sample = read_json(SCRIPT_DIR / "injection_sample_s0.json")
    return {week: sum(post["week"] == week for post in sample["posts"]) for week in SOURCE_WEEKS}


def expected_arrivals() -> tuple[dict[str, int], int]:
    counts = source_counts()
    arrivals = {week: 0 for week in SOURCE_WEEKS}
    arrivals[AVAILABLE_WEEK] = INITIAL_SAMPLE_N
    for source_week, count in counts.items():
        week_num = int(source_week.split("-W", 1)[1])
        if source_week == "2026-W13":
            count -= 1
            arrivals["2026-W13"] += 1
        available_num = week_num + 1
        if available_num <= 22:
            arrivals[f"2026-W{available_num:02d}"] += count
    return arrivals, counts["2026-W22"]


def generate() -> None:
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    guarded = base_sample_paths()
    guarded += [
        CONFIGS_DIR / f"anchored_v1_{arm}_s{seed}.json"
        for arm in ARMS
        for seed in SEEDS
    ]
    before = {str(path.relative_to(WORKSPACE_ROOT)): sha256(path) for path in guarded}

    full = read_json(FULL_INJECTION_PATH)
    w11_pool = [post for post in full["posts"] if str(post.get("week")) == SOURCE_WEEK]
    if len(w11_pool) < INITIAL_SAMPLE_N:
        raise RuntimeError(f"{SOURCE_WEEK} pool has only {len(w11_pool)} posts")

    initial_sha: dict[str, str] = {}
    for seed in SEEDS:
        rng_seed = seed + INITIAL_SAMPLE_SEED_OFFSET
        selected = stratified_sample(w11_pool, INITIAL_SAMPLE_N, random.Random(rng_seed))
        selected.sort(key=lambda post: str(post["pid"]))
        type_counts = dict(sorted(Counter(str(post.get("type", "other")) for post in selected).items()))
        document = {
            "meta": {
                "source": "custom/envs/curation_assets/injection_posts.json",
                "purpose": (
                    "weekly_lag1 的 W12 初始信息环境：从 W11 历史池独立抽取 17 条；"
                    "帖子保留来源周 W11，在 W12 首次可见，周龄为 1"
                ),
                "seed": seed,
                "sample_rng": f"Random({seed}+{INITIAL_SAMPLE_SEED_OFFSET})",
                "sampling_method": "W11 池内按帖子类型分层比例抽样（最大余数法），层内独立随机抽取",
                "source_week": SOURCE_WEEK,
                "available_week": AVAILABLE_WEEK,
                "age_at_first_availability_weeks": 1,
                "rows_total": len(selected),
                "type_counts": type_counts,
            },
            "posts": selected,
        }
        out = initial_sample_path(seed)
        write_json(out, document)
        initial_sha[str(seed)] = sha256(out)

    for arm in ARMS:
        for seed in SEEDS:
            base = read_json(CONFIGS_DIR / f"anchored_v1_{arm}_s{seed}.json")
            kwargs = base["env_modules"][0]["kwargs"]
            kwargs.update(
                {
                    "weekly_real_post_lag_weeks": 1,
                    "weekly_initial_injection_data_path": (
                        f"hypothesis_4/experiment_1/init/initial_sample_weekly_lag_s{seed}.json"
                    ),
                    "weekly_same_week_official_source_pids": list(OFFICIAL_SAME_WEEK_PIDS),
                }
            )
            write_json(config_path(arm, seed), base)

    steps_path = SCRIPT_DIR / "steps_weekly_lag.yaml"
    steps_path.write_text(STEPS_TEXT, encoding="utf-8")
    arrivals, deferred_w23 = expected_arrivals()
    manifest = {
        "experiment": "hypothesis_4/experiment_1",
        "round": ROUND_TAG,
        "design": (
            "周级注入时机修订：interest/random 的普通真实帖在来源周后一周首次可见；"
            "Agent 帖保持下一周可见；W13 唯一官方讣告同周进入，interest 同周置顶，"
            "random 按普通帖处理；chronological 保持原设计且不重跑"
        ),
        "run_ids": [f"{ROUND_TAG}_{arm}_s{seed}" for arm in ARMS for seed in SEEDS],
        "source_250_sha256": {
            str(seed): sha256(SCRIPT_DIR / f"injection_sample_s{seed}.json") for seed in SEEDS
        },
        "initial_sample_sha256": initial_sha,
        "initial_sample": {
            "source_week": SOURCE_WEEK,
            "available_week": AVAILABLE_WEEK,
            "rows_per_seed": INITIAL_SAMPLE_N,
            "sample_seed_offset": INITIAL_SAMPLE_SEED_OFFSET,
        },
        "timing": {
            "ordinary_real_post_lag_weeks": 1,
            "agent_post_lag_weeks": 1,
            "same_week_official_pids": list(OFFICIAL_SAME_WEEK_PIDS),
            "simulation_weeks": [SOURCE_WEEKS[0], SOURCE_WEEKS[-1]],
            "expected_external_arrivals_by_week": arrivals,
            "expected_external_arrivals_in_window": sum(arrivals.values()),
            "deferred_to_w23": deferred_w23,
        },
        "steps": "hypothesis_4/experiment_1/init/steps_weekly_lag.yaml",
    }
    write_json(CONFIGS_DIR / f"{ROUND_TAG}_manifest.json", manifest)

    after = {str(path.relative_to(WORKSPACE_ROOT)): sha256(path) for path in guarded}
    changed = [path for path in before if before[path] != after[path]]
    if changed:
        raise RuntimeError(f"generator modified frozen artifacts: {changed}")


def validate() -> list[str]:
    problems: list[str] = []
    manifest_path = CONFIGS_DIR / f"{ROUND_TAG}_manifest.json"
    if not manifest_path.exists():
        return [f"missing {manifest_path.relative_to(WORKSPACE_ROOT)}"]
    manifest = read_json(manifest_path)
    full = read_json(FULL_INJECTION_PATH)
    w11_pids = {str(post["pid"]) for post in full["posts"] if post.get("week") == SOURCE_WEEK}

    for seed in SEEDS:
        original = SCRIPT_DIR / f"injection_sample_s{seed}.json"
        if sha256(original) != manifest["source_250_sha256"][str(seed)]:
            problems.append(f"s{seed}: frozen 250-post sample hash changed")
        original_doc = read_json(original)
        if len(original_doc["posts"]) != 250:
            problems.append(f"s{seed}: frozen sample has {len(original_doc['posts'])} rows, expected 250")

        initial_path = initial_sample_path(seed)
        if not initial_path.exists():
            problems.append(f"s{seed}: missing W11 initial sample")
            continue
        initial = read_json(initial_path)
        posts = initial.get("posts", [])
        pids = [str(post.get("pid")) for post in posts]
        if len(posts) != INITIAL_SAMPLE_N or len(set(pids)) != INITIAL_SAMPLE_N:
            problems.append(f"s{seed}: W11 initial sample is not {INITIAL_SAMPLE_N} unique posts")
        if any(post.get("week") != SOURCE_WEEK for post in posts):
            problems.append(f"s{seed}: W11 initial sample contains another source week")
        if not set(pids).issubset(w11_pids):
            problems.append(f"s{seed}: W11 initial sample contains posts outside source pool")
        if initial.get("meta", {}).get("available_week") != AVAILABLE_WEEK:
            problems.append(f"s{seed}: initial sample available_week is not {AVAILABLE_WEEK}")
        if sha256(initial_path) != manifest["initial_sample_sha256"][str(seed)]:
            problems.append(f"s{seed}: initial sample hash differs from manifest")

        for arm in ARMS:
            revised_path = config_path(arm, seed)
            if not revised_path.exists():
                problems.append(f"{arm} s{seed}: missing config")
                continue
            revised = read_json(revised_path)
            base = read_json(CONFIGS_DIR / f"anchored_v1_{arm}_s{seed}.json")
            kwargs = revised["env_modules"][0]["kwargs"]
            base_kwargs = base["env_modules"][0]["kwargs"]
            expected_extra = {
                "weekly_real_post_lag_weeks": 1,
                "weekly_initial_injection_data_path": (
                    f"hypothesis_4/experiment_1/init/initial_sample_weekly_lag_s{seed}.json"
                ),
                "weekly_same_week_official_source_pids": list(OFFICIAL_SAME_WEEK_PIDS),
            }
            stripped = dict(kwargs)
            for key, value in expected_extra.items():
                if stripped.pop(key, None) != value:
                    problems.append(f"{arm} s{seed}: invalid {key}")
            if stripped != base_kwargs:
                changed = sorted(
                    key for key in set(stripped) | set(base_kwargs)
                    if stripped.get(key) != base_kwargs.get(key)
                )
                problems.append(f"{arm} s{seed}: unexpected base-config changes {changed}")
            if len(revised.get("agents", [])) != 100:
                problems.append(f"{arm} s{seed}: expected 100 agents")
            for agent in revised.get("agents", []):
                if agent.get("agent_id") != agent.get("kwargs", {}).get("id"):
                    problems.append(f"{arm} s{seed}: agent_id/kwargs.id mismatch")
                    break

    arrivals = manifest["timing"]["expected_external_arrivals_by_week"]
    if sum(arrivals.values()) != 243:
        problems.append(f"expected in-window external arrivals={sum(arrivals.values())}, not 243")
    if manifest["timing"]["deferred_to_w23"] != 24:
        problems.append("expected 24 W22 posts deferred to W23")
    if (SCRIPT_DIR / "steps_weekly_lag.yaml").read_text(encoding="utf-8") != STEPS_TEXT:
        problems.append("weekly-lag steps file differs from the approved 11-week schedule")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate existing artifacts only")
    args = parser.parse_args()
    if not args.check:
        generate()
    problems = validate()
    if problems:
        print("weekly_lag1 validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    manifest = read_json(CONFIGS_DIR / f"{ROUND_TAG}_manifest.json")
    print("weekly_lag1 validation passed")
    print(f"- configs: {len(manifest['run_ids'])}")
    print(f"- initial samples: {len(SEEDS)} x {INITIAL_SAMPLE_N} W11 posts")
    print(f"- expected W12-W22 external arrivals: {manifest['timing']['expected_external_arrivals_in_window']}")
    print(f"- deferred to W23: {manifest['timing']['deferred_to_w23']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
