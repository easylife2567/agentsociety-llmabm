#!/usr/bin/env python3
"""抽取 9 个正式 run 的 Agent 生成帖，冻结为盲法判类输入（W2 整改第一步）。

背景
----
环境把每条 Agent 帖的类别写成 **pool_type = 该 Agent 的固定类型（by construction）**，
判类字段 **assigned_type** 则是用**与生成提示同一套四词表**对正文的复核。两者共享
同一把词表尺子，因此「看到同类内容 → 同类 Agent 发声 → 被记为同类」在测量上闭环，
无法证明表征是涌现的（内部 mock review W2）。

本脚本只负责**冻结输入**：把每条生成帖的正文单独抽出来，附带仅供分析用的元数据
（run / arm / seed / week / agent_id / pool_type / env_assigned_type）。判类脚本只把
**正文**送给模型，不送 arm、不送 pool_type、不送词表、不送周次。

用法
----
    python extract_agent_posts.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
RUNS_DIR = SCRIPT_DIR / "runs" / "anchored_v1"
OUT_DIR = SCRIPT_DIR / "results" / "blind_classification"
OUT_JSONL = OUT_DIR / "agent_posts.jsonl"

AGENT_ID = re.compile(r"^\d+$")


def parse_run_dir(name: str) -> tuple[str, int] | None:
    """anchored_v1_<arm>_s<seed> -> (arm, seed)。"""
    m = re.fullmatch(r"anchored_v1_(random|chronological|interest)_s(\d+)", name)
    return (m.group(1), int(m.group(2))) if m else None


def main() -> int:
    run_dirs = sorted(p for p in RUNS_DIR.iterdir() if p.is_dir())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    per_run: dict[str, dict] = {}
    for run_dir in run_dirs:
        parsed = parse_run_dir(run_dir.name)
        if parsed is None:
            continue
        arm, seed = parsed
        state_path = run_dir / "env" / "CurationDynamicsSpace" / "state" / "ENV_STATE.json"
        if not state_path.exists():
            print(f"[skip] 无 ENV_STATE：{run_dir.name}")
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        posts = list(state["_posts"].values())

        agent_posts = [
            p for p in posts
            if AGENT_ID.fullmatch(str(p.get("author_id", "")))
            and int(p["author_id"]) <= 100
        ]
        # 与 monitor 的排序口径一致：按 post_id 升序
        agent_posts.sort(key=lambda p: p.get("post_id") or 0)

        lengths = []
        for p in agent_posts:
            content = str(p.get("content") or "")
            lengths.append(len(content))
            records.append(
                {
                    "run_id": run_dir.name,
                    "arm": arm,
                    "seed": seed,
                    "week": p.get("week"),
                    "post_id": p.get("post_id"),
                    "agent_id": str(p.get("author_id")),
                    "pool_type": p.get("type"),            # Agent 固定类型（by construction）
                    "env_assigned_type": p.get("assigned_type"),  # 四词表复核
                    "env_mismatch": bool(p.get("type_mismatch")),
                    "content": content,
                }
            )
        per_run[run_dir.name] = {
            "agent_posts": len(agent_posts),
            "content_len_min": min(lengths) if lengths else 0,
            "content_len_max": max(lengths) if lengths else 0,
            "content_len_mean": round(sum(lengths) / len(lengths), 1) if lengths else 0.0,
            "truncated_at_1000": sum(1 for n in lengths if n >= 1000),
        }
        print(f"[ok] {run_dir.name:32s} agent_posts={len(agent_posts):4d} "
              f"len {per_run[run_dir.name]['content_len_min']}–"
              f"{per_run[run_dir.name]['content_len_max']}", flush=True)

    with OUT_JSONL.open("w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")

    pool_dist = Counter(r["pool_type"] for r in records)
    env_dist = Counter(r["env_assigned_type"] for r in records)
    env_mismatch = sum(1 for r in records if r["env_mismatch"])
    summary = {
        "runs": per_run,
        "total_agent_posts": len(records),
        "pool_type_dist": dict(pool_dist),
        "env_assigned_type_dist": dict(env_dist),
        "env_type_mismatch": env_mismatch,
        "env_type_mismatch_rate": round(env_mismatch / len(records), 4) if records else 0.0,
        "note": "pool_type=Agent 固定类型（by construction）；env_assigned_type=环境四词表复核。",
    }
    (OUT_DIR / "extraction_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n=== 汇总 ===")
    print(f"Agent 帖总数：{len(records)}")
    print(f"pool_type（固定身份）：{dict(pool_dist)}")
    print(f"env_assigned_type（四词表复核）：{dict(env_dist)}")
    print(f"环境四词表判类与身份不一致：{env_mismatch} "
          f"({summary['env_type_mismatch_rate']:.1%})")
    print(f"\n✅ 输入：{OUT_JSONL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
