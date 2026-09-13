#!/usr/bin/env python3
"""快速测试：逐 Agent 类型 × 时段的发帖数（代理推演，多 seed）。

复用 calibrate_speak.simulate()（与 env 同构的 feed 推演 +
U=B_i+R·(D−B_i) 锚定式数值决策），
只把兴趣抽样的 RNG 种子扫一遍（对应 env 的 seed+3000 流），
对 100 人群体（meme19/mourning22/marketing23/education15/other21）出：

  表A  逐周 × 逐类型发帖数（多 seed 均值，括号内为逐 seed sd）
  表B  时段汇总（早期 W12-W15 / 中期 W16-W19 / 后期 W20-W22）：帖数、占比、人均发言次数
  表C  R 尺度对照（默认 20 vs 50），看增强 R 后哪类 Agent 在哪个时段少说了多少

用法：
    $PYTHON_PATH type_weekly_proxy.py                  # 30 seed，R=20
    $PYTHON_PATH type_weekly_proxy.py --seeds 60
    $PYTHON_PATH type_weekly_proxy.py --no-compare      # 跳过表C
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cal = load("calibrate_speak", SCRIPT_DIR / "calibrate_speak.py")

WEEKS = cal.WEEKS
TYPES = cal.TYPE_ORDER
LABEL = {"meme": "玩梗", "mourning": "悼念", "marketing": "营销",
         "education": "教育", "other": "其他"}
N_AGENTS = cal.POPULATION_COUNTS
PERIODS = [
    ("早期 W12-W15", ("2026-W12", "2026-W13", "2026-W14", "2026-W15")),
    ("中期 W16-W19", ("2026-W16", "2026-W17", "2026-W18", "2026-W19")),
    ("后期 W20-W22", ("2026-W20", "2026-W21", "2026-W22")),
]


def run_seeds(base: float, n_seeds: int, decay_scale: float | None) -> list[dict]:
    """跑 n_seeds 个 seed，返回 [{week: {type: count}}, ...]。"""
    orig_fatigue = cal.mech.fatigue_factor
    if decay_scale is not None:
        def patched(decay, cum_own, scale=decay_scale):
            return orig_fatigue(decay, cum_own, scale)
        cal.mech.fatigue_factor = patched
    try:
        out = []
        for s in range(n_seeds):
            cal.CALIB_SAMPLE_SEED = s + 3000          # 与 env 的 seed+3000 流对齐
            res, _, _ = cal.simulate(base, "normal")
            out.append(res)
    finally:
        cal.mech.fatigue_factor = orig_fatigue
    return out


def mean_sd(vals: list[float]) -> tuple[float, float]:
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((x - m) ** 2 for x in vals) / len(vals))
    return m, sd


def table_a(runs: list[dict], n_seeds: int) -> None:
    print(f"\n表A 逐周 × 逐类型发帖数（{n_seeds} seed 均值，括号=逐 seed sd）")
    print("周        |" + "".join(f"{LABEL[t]:>16}" for t in TYPES) + f"{'合计':>10}")
    for wk in WEEKS:
        cells = ""
        for t in TYPES:
            m, sd = mean_sd([r[wk][t] for r in runs])
            cells += f"{m:>10.1f}({sd:>3.1f})"
        tot_m, tot_sd = mean_sd([sum(r[wk].values()) for r in runs])
        print(f"{wk} |{cells}{tot_m:>7.1f}({tot_sd:>3.1f})")


def table_b(runs: list[dict], n_seeds: int) -> None:
    print(f"\n表B 时段汇总（{n_seeds} seed 均值；人均 = 帖数 ÷ 该类 agent 数）")
    hdr = "时段           |"
    for t in TYPES:
        hdr += f"{LABEL[t]+'(' + str(N_AGENTS[t]) + '人)':>22}"
    print(hdr + f"{'合计':>10}")

    for pname, pweeks in PERIODS:
        cells = ""
        for t in TYPES:
            per_run = [sum(r[w][t] for w in pweeks) for r in runs]
            m, sd = mean_sd(per_run)
            per_agent = m / N_AGENTS[t]
            cells += f"{m:>13.1f}±{sd:>3.1f}({per_agent:>4.2f})"
        tot_m, tot_sd = mean_sd([sum(r[w][t] for w in pweeks for t in TYPES) for r in runs])
        print(f"{pname:<15}|{cells}{tot_m:>7.1f}±{tot_sd:>3.1f}")

    # 全期
    cells = ""
    for t in TYPES:
        per_run = [sum(r[w][t] for w in WEEKS) for r in runs]
        m, sd = mean_sd(per_run)
        cells += f"{m:>13.1f}±{sd:>3.1f}({m/N_AGENTS[t]:>4.2f})"
    tot_m, tot_sd = mean_sd([sum(r[w][t] for w in WEEKS for t in TYPES) for r in runs])
    print(f"{'全期 W12-W22':<15}|{cells}{tot_m:>7.1f}±{tot_sd:>3.1f}")

    # 时段占比（该类型自己三期怎么分）
    print("\n各类型自身的时段分布（占该类型全期帖数的比例）")
    print("类型       |" + "".join(f"{p:>16}" for p, _ in PERIODS))
    for t in TYPES:
        tot = sum(sum(r[w][t] for w in WEEKS) for r in runs)
        cells = ""
        for _, pw in PERIODS:
            part = sum(sum(r[w][t] for w in pw) for r in runs)
            cells += f"{(part / tot if tot else 0):>15.1%}"
        print(f"{LABEL[t]:<10}|{cells}")


def _inj_type_counts() -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for wk in WEEKS:
        c = {t: 0 for t in TYPES}
        for rec in cal.INJECTED_BY_WEEK[wk]:
            if rec["type"] in c:
                c[rec["type"]] += 1
        out[wk] = c
    return out


INJ_T = None


def table_d(runs: list[dict], n_seeds: int, runs50: list[dict] | None) -> None:
    """combined 口径玩梗份额（注入+产出）vs 真实基准 —— 核心效标。"""
    global INJ_T
    if INJ_T is None:
        INJ_T = _inj_type_counts()
    # 真实基准口径与 env/monitor 一致：value / 该周 total（total 含「爬取噪音」）。
    import json as _json
    bench = _json.loads(cal.BENCH_PATH.read_text(encoding="utf-8"))["weekly_category_matrix"]
    cn_of = {v: k for k, v in cal.TYPE_KEYS.items()}     # type -> benchmark 中文键
    real = {}
    for wk in WEEKS:
        row = bench[wk]
        tot = float(row.get("total", 0) or 0)
        real[wk] = {t: (float(row.get(cn_of[t], 0) or 0) / tot if tot else 0.0)
                    for t in TYPES}

    def share(runs_: list[dict], wk: str) -> tuple[float, float]:
        vals = []
        for r in runs_:
            num = INJ_T[wk]["meme"] + r[wk]["meme"]
            den = sum(INJ_T[wk].values()) + sum(r[wk].values())
            vals.append(num / den if den else 0.0)
        return mean_sd(vals)

    print(f"\n表D combined 口径玩梗份额 vs 真实（{n_seeds} seed 均值±sd）")
    head = f"{'周':<9}| {'真实':>7} | {'R=20 当前':>14}"
    if runs50:
        head += f" | {'R=50 改前':>14}"
    print(head + " | 逐周差(R=20)")
    err20 = []
    err50 = []
    for wk in WEEKS:
        m20, s20 = share(runs, wk)
        real_v = real[wk]["meme"]
        err20.append((m20 - real_v) ** 2)
        line = f"{wk} | {real_v:>7.3f} | {m20:>8.3f}±{s20:>4.3f}"
        if runs50:
            m50, s50 = share(runs50, wk)
            err50.append((m50 - real_v) ** 2)
            line += f" | {m50:>8.3f}±{s50:>4.3f}"
        line += f" | {m20 - real_v:>+7.3f}"
        print(line)
    tail = f"RMSE(W19-W22) | {'':>7} | {math.sqrt(sum(err20[7:])/4):>14.4f}"
    if runs50:
        tail += f" | {math.sqrt(sum(err50[7:])/4):>14.4f}"
    print(tail)


def table_c(base: float, n_seeds: int, runs20: list[dict]) -> None:
    print(f"\n表C R 尺度对照（{n_seeds} seed 均值；R=20 为当前值，R=50 为改前）")
    runs50 = run_seeds(base, n_seeds, decay_scale=50.0)
    hdr = "时段           |" + "".join(f"{LABEL[t]:>20}" for t in TYPES) + f"{'合计':>12}"
    print(hdr)
    for pname, pweeks in PERIODS + [("全期 W12-W22", tuple(WEEKS))]:
        cells = ""
        for t in TYPES:
            m20, _ = mean_sd([sum(r[w][t] for w in pweeks) for r in runs20])
            m50, _ = mean_sd([sum(r[w][t] for w in pweeks) for r in runs50])
            cells += f"{m50:>9.1f}→{m20:>7.1f}"
        t20, _ = mean_sd([sum(sum(r[w].values()) for w in pweeks) for r in runs20])
        t50, _ = mean_sd([sum(sum(r[w].values()) for w in pweeks) for r in runs50])
        print(f"{pname:<15}|{cells}{t50:>6.1f}→{t20:>5.1f}")
    return runs50


def main() -> int:
    ap = argparse.ArgumentParser(description="逐类型 × 时段发帖数（快速代理）")
    ap.add_argument("--base", type=float, default=cal.BASE_REF, help="门槛基数（默认 0.95）")
    ap.add_argument("--seeds", type=int, default=30, help="seed 数（默认 30）")
    ap.add_argument("--no-compare", action="store_true", help="跳过 R=50 对照")
    args = ap.parse_args()

    import time
    t0 = time.time()
    runs = run_seeds(args.base, args.seeds, decay_scale=None)
    dt = time.time() - t0
    print(f"== 代理推演：{args.seeds} seed × 11 周，用时 {dt:.1f}s"
          f"（{dt/args.seeds:.2f}s/run）｜门槛基数={args.base}｜R 尺度={cal.mech.DEFAULT_DECAY_SCALE:g}"
          f"｜feed=10 条/周｜群体 100 人 ==")

    # 单 seed（=真实 s0 的那条抽样流）单独看一眼
    r0 = runs[0]
    print("\nseed0 单次实现（≈ 真实 interest_s0 的抽样流）："
          + " | ".join(f"{LABEL[t]} {sum(r0[w][t] for w in WEEKS)}" for t in TYPES)
          + f" | 合计 {sum(sum(r0[w].values()) for w in WEEKS)}")

    table_a(runs, args.seeds)
    table_b(runs, args.seeds)
    runs50 = None
    if not args.no_compare:
        runs50 = table_c(args.base, args.seeds, runs)
    table_d(runs, args.seeds, runs50)
    print(f"\n总用时 {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
