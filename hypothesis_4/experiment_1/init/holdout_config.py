#!/usr/bin/env python3
"""生成"结果盲"嵌套 holdout 臂：W19–W22 不注入真实帖（r3 W1 整改）。

问题
----
W19–W22 的真实帖（含玩梗类别构成）在每个 Agent 当周决策前进入候选池，而 W19–W22 又被
正文称为"后段检查窗口"。因此"模型复现了 W20 起爆"与外生输入完全相容，不能证明模型的
生成性解释力（r3 三位审稿人一致列为阻断项 W1）。

设计：NESTED HOLDOUT（嵌套留出）
- holdout 臂的注入帖 = 对应全臂注入帖中 `week < 2026-W19` 的**严格子集**；
  两臂在 W12–W18 的外部输入逐条相同（同一 pid、同一顺序、同一类型构成）。
- 因此 W19–W22 轨迹的任何差异只能来自"是否注入了 W19–W22 的真实帖"。
- 保留 W12–W18 注入（不改变事件触发期与悼念期的外部条件）。
- 涌现环境 G 自 2026-09-12 起为纯观测、不进入决策（见 env 第 225 行），故本研究
  不存在其他行为性泄漏通道；`emergence_flow_by_week` 保持原值以保证与全臂可比。

新增 run：`anchored_v1_holdout_{interest,random}_s{0,1,2}`，共 6 个。

安全约束
--------
本脚本**不修改** `config_params.py`，只新增文件。导入 `config_params` 会按其设计
确定性重写 9 个配置与 3 个注入样本；脚本在导入前后对已冻结产物做 SHA-256 守卫，
一旦发现被改动即报警并列出需 `git checkout --` 恢复的路径。

用法
----
    python init/holdout_config.py            # 生成 + 自校验
    python init/holdout_config.py --check    # 仅校验已有产物
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_DIR = SCRIPT_DIR.parent
WORKSPACE_ROOT = EXPERIMENT_DIR.parent.parent
CONFIGS_DIR = SCRIPT_DIR / "configs"

HOLDOUT_FROM_WEEK = "2026-W19"
HOLDOUT_ARMS = ("interest", "random")
SEEDS = (0, 1, 2)

# 导入 config_params 时会被其确定性重写的已冻结产物
GUARDED = ([CONFIGS_DIR / f"anchored_v1_{arm}_s{s}.json"
            for arm in ("random", "chronological", "interest") for s in SEEDS]
           + [CONFIGS_DIR / f"anchored_v1_ablation_{a}_s0.json" for a in ("no_b", "no_d", "no_r")]
           + [CONFIGS_DIR / "manifest.json",
              SCRIPT_DIR / "init_config.json",
              SCRIPT_DIR / "steps.yaml",
              SCRIPT_DIR / "steps_chronological_hourly.yaml"]
           + [SCRIPT_DIR / f"injection_sample_s{s}.json" for s in SEEDS])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "<missing>"


def snapshot() -> dict[str, str]:
    return {str(p.relative_to(WORKSPACE_ROOT)): sha256(p) for p in GUARDED}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_holdout_sample(seed: int) -> dict:
    """从全臂注入样本中裁出 W12–W18 子集，构成 holdout 注入样本。"""
    full = load_json(SCRIPT_DIR / f"injection_sample_s{seed}.json")
    kept = [p for p in full["posts"] if str(p.get("week", "")) < HOLDOUT_FROM_WEEK]
    dropped = [p for p in full["posts"] if str(p.get("week", "")) >= HOLDOUT_FROM_WEEK]

    weeks = sorted({p["week"] for p in kept})
    weekly_counts = {w: sum(1 for p in kept if p["week"] == w) for w in weeks}
    weekly_type_counts = {
        w: {t: sum(1 for p in kept if p["week"] == w and p.get("type") == t)
            for t in sorted({p.get("type") for p in kept if p["week"] == w})}
        for w in weeks
    }
    meta = dict(full["meta"])
    meta.update({
        "purpose": (f"结果盲嵌套 holdout 注入样本：仅 W12–{HOLDOUT_FROM_WEEK} 前的真实帖，"
                    f"W19–W22 不注入，用于检验玩梗延迟爆发能否在无后段真实输入时自维持 "
                    f"（r3 W1 整改）"),
        "holdout_from_week": HOLDOUT_FROM_WEEK,
        "parent_sample": f"hypothesis_4/experiment_1/init/injection_sample_s{seed}.json",
        "parent_rows_total": len(full["posts"]),
        "dropped_from_week": HOLDOUT_FROM_WEEK,
        "dropped_rows_total": len(dropped),
        "rows_total": len(kept),
        "weekly_counts": weekly_counts,
        "weekly_type_counts": weekly_type_counts,
        "official_counts": {
            w: sum(1 for p in kept if p["week"] == w and p.get("is_official")) for w in weeks
        },
    })
    return {"meta": meta, "posts": kept}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="仅校验已有 holdout 产物")
    args = ap.parse_args()

    if not args.check:
        before = snapshot()
        sys.path.insert(0, str(SCRIPT_DIR))
        import config_params as cp  # noqa: E402  导入即确定性重写冻结产物
        after = snapshot()
        changed = [k for k in before if before[k] != after[k]]
        if changed:
            print("⚠️  导入 config_params 改动了已冻结产物，请先恢复：")
            for k in changed:
                print(f"    git checkout -- {k}")
            return 2
        print(f"✓ 哈希守卫通过：{len(GUARDED)} 个冻结产物未被改动")

        for seed in SEEDS:
            doc = build_holdout_sample(seed)
            out = SCRIPT_DIR / f"injection_sample_holdout_s{seed}.json"
            out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"✓ holdout 注入样本 s{seed}: {doc['meta']['rows_total']} 条"
                  f"（自 {doc['meta']['parent_rows_total']} 条中裁出，"
                  f"去掉 W19–W22 共 {doc['meta']['dropped_rows_total']} 条）-> {out.name}")

        base_kwargs = None
        for arm in HOLDOUT_ARMS:
            for seed in SEEDS:
                cfg = cp.make_config(arm, "normal", seed)
                kwargs = cfg["env_modules"][0]["kwargs"]
                kwargs["injection_data_path"] = (
                    f"hypothesis_4/experiment_1/init/injection_sample_holdout_s{seed}.json"
                )
                run_id = f"anchored_v1_holdout_{arm}_s{seed}"
                (CONFIGS_DIR / f"{run_id}.json").write_text(
                    json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"✓ {run_id}")
                if arm == HOLDOUT_ARMS[0] and seed == 0:
                    base_kwargs = kwargs

    # ---------------- 自校验 ----------------
    problems: list[str] = []
    for arm in HOLDOUT_ARMS:
        for seed in SEEDS:
            run_id = f"anchored_v1_holdout_{arm}_s{seed}"
            cfg_path = CONFIGS_DIR / f"{run_id}.json"
            if not cfg_path.exists():
                problems.append(f"缺少配置 {cfg_path.name}")
                continue
            cfg = load_json(cfg_path)
            kwargs = cfg["env_modules"][0]["kwargs"]
            inj_rel = kwargs["injection_data_path"]
            inj = load_json(WORKSPACE_ROOT / inj_rel)

            late = [p for p in inj["posts"] if str(p["week"]) >= HOLDOUT_FROM_WEEK]
            if late:
                problems.append(f"{run_id}: 注入样本仍含 {len(late)} 条 W19–W22 帖子")
            if kwargs["recommendation_algorithm"] != arm:
                problems.append(f"{run_id}: algorithm={kwargs['recommendation_algorithm']} != {arm}")

            # 嵌套性：holdout 的 W12–W18 pid 集合必须是全臂的同集合
            full = load_json(SCRIPT_DIR / f"injection_sample_s{seed}.json")
            full_early = {str(p["pid"]) for p in full["posts"]
                          if str(p["week"]) < HOLDOUT_FROM_WEEK}
            hold_early = {str(p["pid"]) for p in inj["posts"]}
            if full_early != hold_early:
                only_full = full_early - hold_early
                only_hold = hold_early - full_early
                problems.append(
                    f"{run_id}: W12–W18 注入非严格子集"
                    f"（仅全臂有 {len(only_full)}，仅 holdout 有 {len(only_hold)}）")

            # 除注入路径外，配置应与全臂完全一致
            twin = load_json(CONFIGS_DIR / f"anchored_v1_{arm}_s{seed}.json")
            twin_kwargs = dict(twin["env_modules"][0]["kwargs"])
            cmp_kwargs = dict(kwargs)
            twin_kwargs.pop("injection_data_path", None)
            cmp_kwargs.pop("injection_data_path", None)
            if twin_kwargs != cmp_kwargs:
                diff = sorted(set(twin_kwargs) | set(cmp_kwargs))
                diff = [k for k in diff if twin_kwargs.get(k) != cmp_kwargs.get(k)]
                problems.append(f"{run_id}: 除 injection_data_path 外仍有差异 {diff}")

    if problems:
        print("\n❌ 自校验失败：")
        for p in problems:
            print(f"  - {p}")
        return 1

    print("\n✅ 自校验通过：")
    print(f"  - 6 个 holdout 配置均不含 W19–W22 注入帖")
    print(f"  - W12–W18 注入与全臂逐 pid 一致（严格嵌套子集）")
    print(f"  - 除 injection_data_path 外与全臂配置完全相同")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
