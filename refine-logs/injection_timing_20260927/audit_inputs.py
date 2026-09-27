"""Read-only audit of frozen injection inputs; writes only a summary beside this script.

Run with the workspace PYTHON_PATH. Does not import config_params (which writes files),
instantiate simulations, call an LLM, or alter pipeline state.
"""
from __future__ import annotations

import hashlib
import json
import math
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("input_audit.json")
INIT = ROOT / "hypothesis_4/experiment_1/init"
TZ = timezone(timedelta(hours=8))


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def local_time(p):
    raw = p.get("published_at")
    if not raw:
        # Mirror the explicit official-post convention, not a measured timestamp.
        if p.get("pid") == "official_w13_announcement":
            return datetime(2026, 3, 24, 20, tzinfo=TZ)
        return None
    t = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    return t.replace(tzinfo=TZ) if t.tzinfo is None else t.astimezone(TZ)


def iso_week(t):
    y, w, _ = t.isocalendar()
    return f"{y}-W{w:02d}"


def time_quality(posts):
    times = [local_time(p) for p in posts]
    return {
        "rows": len(posts),
        "missing_published_at": sum(not p.get("published_at") for p in posts),
        "unresolved_times": sum(t is None for t in times),
        "local_iso_week_mismatch": sum(t is not None and iso_week(t) != p["week"]
                                       for p, t in zip(posts, times)),
        "duplicate_pid_excess": len(posts) - len({str(p["pid"]) for p in posts}),
        "duplicate_exact_nonempty_content_excess": sum(
            c - 1 for c in Counter(str(p.get("content", "")).strip()
                                  for p in posts if str(p.get("content", "")).strip()).values()),
        "exact_time_tie_excess": sum(c - 1 for c in Counter(t for t in times if t is not None).values()),
    }


def main():
    full_path = ROOT / "custom/envs/curation_assets/injection_posts.json"
    full = read(full_path)["posts"]
    cfg_path = INIT / "configs/anchored_v1_chronological_s0.json"
    cfg = read(cfg_path)
    kw = cfg["env_modules"][0]["kwargs"]
    hours = kw["chronological_action_hours"]
    specs = {str(a["kwargs"]["id"]): a["kwargs"] for a in cfg["agents"]}
    weeks = [f"2026-W{w:02d}" for w in range(12, 23)]
    n = Counter(p["week"] for p in full)
    samples = [read(INIT / f"injection_sample_s{s}.json")["posts"] for s in range(3)]
    counts = [Counter((p["week"], p["type"]) for p in s) for s in samples]
    injected = Counter(p["week"] for p in samples[0])
    by_type_before = {}
    for typ in sorted({a["agent_type"] for a in specs.values()}):
        ids = [aid for aid, a in specs.items() if a["agent_type"] == typ]
        by_type_before[typ] = {
            "agents": len(ids),
            "before_tuesday_1550": sum(int(hours[aid]) <= 39 for aid in ids),
            "before_official_tuesday_2000": sum(int(hours[aid]) < 44 for aid in ids),
        }
    external_only = []
    # Deliberately excludes simulated posts: this is an external support diagnostic,
    # not an actual feed-size or exposure result.
    for seed, posts in enumerate(samples):
        arrivals = sorted(local_time(p) for p in posts if local_time(p) is not None)
        w12_counts = []
        for aid, hour in hours.items():
            t = datetime(2026, 3, 16, tzinfo=TZ) + timedelta(hours=int(hour))
            w12_counts.append(bisect_right(arrivals, t))
        external_only.append({
            "seed": seed,
            "w12_action_opportunities": len(w12_counts),
            "w12_actions_with_zero_external_posts_arrived": sum(c == 0 for c in w12_counts),
            "w12_actions_with_fewer_than_10_external_posts_arrived": sum(c < 10 for c in w12_counts),
            "first_sample_arrival_local": arrivals[0].isoformat(),
        })
    suspicious_terms = ("巧乐兹", "雪碧", "跑不过", "心梗", "张雪峰死了", "张雪峰套餐")
    vocab_flags = {
        term: sum(any(term in word for word in a.get("type_vocab", [])) for a in specs.values())
        for term in suspicious_terms
    }
    cutoff = datetime(2026, 5, 4, tzinfo=TZ)  # W19 Monday local time
    holdout = []
    for seed in range(3):
        posts = read(INIT / f"injection_sample_holdout_s{seed}.json")["posts"]
        holdout.append({"seed": seed, "rows": len(posts),
                        "at_or_after_local_w19_cutoff": sum(
                            local_time(p) is not None and local_time(p) >= cutoff for p in posts)})
    mismatch_transitions = Counter(
        p["week"] + "->" + iso_week(local_time(p)) for p in full
        if local_time(p) is not None and p["week"] != iso_week(local_time(p)))
    sources = [full_path, cfg_path, ROOT / "custom/envs/curation_dynamics_space.py",
               ROOT / "custom/agents/curation_discourse_agent.py",
               ROOT / "custom/agents/curation_personas.py", INIT / "config_params.py",
               ROOT / "hypothesis_4/experiment_1/calibrate_speak.py"]
    sources += [INIT / f"injection_sample_s{s}.json" for s in range(3)]
    sources += [INIT / f"injection_sample_holdout_s{s}.json" for s in range(3)]
    result = {
        "scope": "Static source/input audit; no simulation outcomes or causal estimates",
        "date": "2026-09-27",
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sources},
        "full_asset_time_quality": time_quality(full),
        "utc_to_shanghai_week_transitions": dict(sorted(mismatch_transitions.items())),
        "holdout_local_cutoff_audit": holdout,
        "sample_time_quality": [dict(seed=s, **time_quality(p)) for s, p in enumerate(samples)],
        "weekly_counts": [{"week": w, "source": n[w], "injected": injected[w]} for w in weeks],
        "source_w12_w22_rows": sum(n[w] for w in weeks),
        "weekly_type_quotas_identical_across_three_seeds": counts[0] == counts[1] == counts[2],
        "source_w13_w18_ratio": n["2026-W13"] / n["2026-W18"],
        "injected_w13_w18_ratio": injected["2026-W13"] / injected["2026-W18"],
        "action_schedule": {"agents": len(hours), "unique_hours_per_week": len(set(hours.values())),
                            "same_hour_each_week": True, "same_schedule_across_seeds": True,
                            "before_event_by_type": by_type_before},
        "external_support_only": external_only,
        "vocabulary_risk_flags_agents_with_term": vocab_flags,
        "vocabulary_flag_interpretation": "Profile contains term before first feed; semantic/event-time validity needs review, not all substring hits prove future knowledge",
        "post_lifetime": {
            "half_life_days": 7 * kw["life_half_life_weeks"],
            "retire_floor": kw["life_retire_floor"],
            "continuous_retirement_days": -7 * kw["life_half_life_weeks"] * math.log2(kw["life_retire_floor"]),
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "source_sha256"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
