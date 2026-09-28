#!/usr/bin/env python3
"""Generate weekly_lag1_event_v2 without rewriting completed weekly_lag1 artifacts.

This round starts from the frozen anchored_v1 interest/random configs, reapplies the
one-week real-post lag, keeps the W13 official obituary available in its source week,
removes utility-level event boosts and the old interest-only mourning floor, and adds
W23 as a drain/readout week for W22 posts.
The three W11 initialization samples are reused byte-for-byte from weekly_lag1 so
the timing/event change is not confounded by a different initial information pool.

Usage:
    python init/weekly_lag_event_v2_config.py
    python init/weekly_lag_event_v2_config.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_DIR = SCRIPT_DIR.parent
WORKSPACE_ROOT = EXPERIMENT_DIR.parent.parent
CONFIGS_DIR = SCRIPT_DIR / "configs"

ROUND_TAG = "weekly_lag1_event_v2"
ARMS = ("interest", "random")
SEEDS = (0, 1, 2)
SOURCE_WEEKS = tuple(f"2026-W{week:02d}" for week in range(12, 23))
RUN_WEEKS = tuple(f"2026-W{week:02d}" for week in range(12, 24))
INITIAL_SAMPLE_N = 17
OFFICIAL_SAME_WEEK_PIDS = ("official_w13_announcement",)
EVENT_SIGNAL_TYPE = ""
EVENT_SIGNAL_SALIENCE_SLOTS = 0.0
EVENT_WEEK = "2026-W13"
DRAIN_READOUT_WEEK = "2026-W23"

STEPS_FILENAME = f"steps_{ROUND_TAG}.yaml"
MANIFEST_FILENAME = f"{ROUND_TAG}_manifest.json"
STEPS_TEXT = """\
start_t: "2026-03-16T00:00:00"
steps:
  - type: run
    num_steps: 12
    tick: 604800
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def initial_sample_path(seed: int) -> Path:
    return SCRIPT_DIR / f"initial_sample_weekly_lag_s{seed}.json"


def config_path(arm: str, seed: int) -> Path:
    return CONFIGS_DIR / f"{ROUND_TAG}_{arm}_s{seed}.json"


def protected_weekly_lag1_paths() -> list[Path]:
    return (
        [CONFIGS_DIR / f"weekly_lag1_{arm}_s{seed}.json" for arm in ARMS for seed in SEEDS]
        + [CONFIGS_DIR / "weekly_lag1_manifest.json", SCRIPT_DIR / "steps_weekly_lag.yaml"]
        + [initial_sample_path(seed) for seed in SEEDS]
    )


def source_counts(seed: int = 0) -> dict[str, int]:
    sample = read_json(SCRIPT_DIR / f"injection_sample_s{seed}.json")
    return {
        week: sum(str(post.get("week")) == week for post in sample["posts"])
        for week in SOURCE_WEEKS
    }


def expected_arrivals() -> dict[str, int]:
    counts = source_counts()
    arrivals = {week: 0 for week in RUN_WEEKS}
    arrivals["2026-W12"] = INITIAL_SAMPLE_N
    for source_week, count in counts.items():
        source_number = int(source_week.split("-W", 1)[1])
        if source_week == EVENT_WEEK:
            count -= 1
            arrivals[EVENT_WEEK] += 1
        arrivals[f"2026-W{source_number + 1:02d}"] += count
    return arrivals


def expected_overrides(seed: int) -> dict:
    return {
        "weekly_real_post_lag_weeks": 1,
        "weekly_initial_injection_data_path": (
            f"hypothesis_4/experiment_1/init/initial_sample_weekly_lag_s{seed}.json"
        ),
        "weekly_same_week_official_source_pids": list(OFFICIAL_SAME_WEEK_PIDS),
        "event_signal_type": EVENT_SIGNAL_TYPE,
        "event_signal_salience_slots": EVENT_SIGNAL_SALIENCE_SLOTS,
        "event_week_mourning_floor": 0,
        "num_ticks": len(RUN_WEEKS),
    }


def generate() -> None:
    protected = protected_weekly_lag1_paths()
    before = {str(path.relative_to(WORKSPACE_ROOT)): sha256(path) for path in protected}

    for arm in ARMS:
        for seed in SEEDS:
            config = read_json(CONFIGS_DIR / f"anchored_v1_{arm}_s{seed}.json")
            config["env_modules"][0]["kwargs"].update(expected_overrides(seed))
            write_json(config_path(arm, seed), config)

    (SCRIPT_DIR / STEPS_FILENAME).write_text(STEPS_TEXT, encoding="utf-8")
    arrivals = expected_arrivals()
    manifest = {
        "experiment": "hypothesis_4/experiment_1",
        "round": ROUND_TAG,
        "parent_round": "anchored_v1",
        "comparison_round": "weekly_lag1",
        "design": (
            "普通真实帖与 Agent 帖均在来源周后一周首次可见；W13 唯一官方讣告仍同周进入。"
            "不以外生事件槽位直接改变任何 Agent 的发言效用，旧的 interest-only 哀悼"
            "保底关闭。W23 仅作 drain/readout，接收 W22 延迟帖，"
            "不注入 W23 来源外部帖；chronological 保持原设计且不重跑。"
        ),
        "run_ids": [f"{ROUND_TAG}_{arm}_s{seed}" for arm in ARMS for seed in SEEDS],
        "protected_weekly_lag1_sha256": before,
        "source_250_sha256": {
            str(seed): sha256(SCRIPT_DIR / f"injection_sample_s{seed}.json")
            for seed in SEEDS
        },
        "initial_sample_sha256": {
            str(seed): sha256(initial_sample_path(seed)) for seed in SEEDS
        },
        "initial_sample": {
            "reused_from_round": "weekly_lag1",
            "source_week": "2026-W11",
            "available_week": "2026-W12",
            "rows_per_seed": INITIAL_SAMPLE_N,
        },
        "event_signal": {
            "enabled": False,
            "week": EVENT_WEEK,
            "type": EVENT_SIGNAL_TYPE,
            "salience_slots": EVENT_SIGNAL_SALIENCE_SLOTS,
            "reason": "avoid forcing a W13 participation peak through deterministic thresholds",
            "event_week_mourning_floor": 0,
        },
        "timing": {
            "ordinary_real_post_lag_weeks": 1,
            "agent_post_lag_weeks": 1,
            "same_week_official_pids": list(OFFICIAL_SAME_WEEK_PIDS),
            "source_weeks": [SOURCE_WEEKS[0], SOURCE_WEEKS[-1]],
            "simulation_weeks": [RUN_WEEKS[0], RUN_WEEKS[-1]],
            "drain_readout_week": DRAIN_READOUT_WEEK,
            "drain_readout_week_accepts_source_week": "2026-W22",
            "drain_readout_week_has_same_week_external_source": False,
            "expected_external_arrivals_by_week": arrivals,
            "expected_external_arrivals_in_window": sum(arrivals.values()),
            "w22_posts_drained_in_w23": arrivals[DRAIN_READOUT_WEEK],
            "deferred_beyond_window": 0,
        },
        "steps": f"hypothesis_4/experiment_1/init/{STEPS_FILENAME}",
    }
    write_json(CONFIGS_DIR / MANIFEST_FILENAME, manifest)

    after = {str(path.relative_to(WORKSPACE_ROOT)): sha256(path) for path in protected}
    changed = [path for path in before if before[path] != after[path]]
    if changed:
        raise RuntimeError(f"generator modified protected weekly_lag1 artifacts: {changed}")


def validate() -> list[str]:
    problems: list[str] = []
    manifest_path = CONFIGS_DIR / MANIFEST_FILENAME
    if not manifest_path.exists():
        return [f"missing {manifest_path.relative_to(WORKSPACE_ROOT)}"]
    manifest = read_json(manifest_path)

    for relative, expected_hash in manifest["protected_weekly_lag1_sha256"].items():
        path = WORKSPACE_ROOT / relative
        if not path.exists() or sha256(path) != expected_hash:
            problems.append(f"protected weekly_lag1 artifact changed: {relative}")

    for seed in SEEDS:
        source_path = SCRIPT_DIR / f"injection_sample_s{seed}.json"
        if sha256(source_path) != manifest["source_250_sha256"][str(seed)]:
            problems.append(f"s{seed}: frozen 250-post sample hash changed")
        source = read_json(source_path)
        if len(source.get("posts", [])) != 250:
            problems.append(f"s{seed}: frozen source sample is not 250 posts")

        initial_path = initial_sample_path(seed)
        if sha256(initial_path) != manifest["initial_sample_sha256"][str(seed)]:
            problems.append(f"s{seed}: reused W11 initial sample hash changed")
        initial = read_json(initial_path)
        if len(initial.get("posts", [])) != INITIAL_SAMPLE_N:
            problems.append(f"s{seed}: reused W11 initial sample is not 17 posts")

        for arm in ARMS:
            path = config_path(arm, seed)
            if not path.exists():
                problems.append(f"{arm} s{seed}: missing v2 config")
                continue
            revised = read_json(path)
            base = read_json(CONFIGS_DIR / f"anchored_v1_{arm}_s{seed}.json")
            kwargs = dict(revised["env_modules"][0]["kwargs"])
            base_kwargs = dict(base["env_modules"][0]["kwargs"])
            for key, value in expected_overrides(seed).items():
                if kwargs.pop(key, None) != value:
                    problems.append(f"{arm} s{seed}: invalid {key}")
                base_kwargs.pop(key, None)
            if kwargs != base_kwargs:
                changed = sorted(
                    key for key in set(kwargs) | set(base_kwargs)
                    if kwargs.get(key) != base_kwargs.get(key)
                )
                problems.append(f"{arm} s{seed}: unexpected base-config changes {changed}")
            if len(revised.get("agents", [])) != 100:
                problems.append(f"{arm} s{seed}: expected 100 agents")

    arrivals = manifest["timing"]["expected_external_arrivals_by_week"]
    if list(arrivals) != list(RUN_WEEKS):
        problems.append("arrival table must cover W12-W23 in order")
    if list(arrivals.values()) != [17, 18, 34, 30, 24, 22, 19, 18, 18, 20, 23, 24]:
        problems.append("arrival table differs from the approved W12-W23 schedule")
    if sum(arrivals.values()) != 267:
        problems.append("expected 267 external arrivals in W12-W23")
    if manifest["timing"].get("deferred_beyond_window") != 0:
        problems.append("expected no external posts deferred beyond W23")
    if manifest["event_signal"] != {
        "enabled": False,
        "week": EVENT_WEEK,
        "type": EVENT_SIGNAL_TYPE,
        "salience_slots": EVENT_SIGNAL_SALIENCE_SLOTS,
        "reason": "avoid forcing a W13 participation peak through deterministic thresholds",
        "event_week_mourning_floor": 0,
    }:
        problems.append("manifest event-signal definition is invalid")
    if (SCRIPT_DIR / STEPS_FILENAME).read_text(encoding="utf-8") != STEPS_TEXT:
        problems.append("v2 steps file differs from the approved 12-week schedule")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate existing v2 artifacts only")
    args = parser.parse_args()
    if not args.check:
        generate()
    problems = validate()
    if problems:
        print(f"{ROUND_TAG} validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print(f"{ROUND_TAG} validation passed")
    print("- configs: 6; protected weekly_lag1 artifacts: unchanged")
    print("- W13 utility-level event signal: disabled; official obituary remains same-week")
    print("- W12-W23 external arrivals: 267; W23 drains 24 W22-source posts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
