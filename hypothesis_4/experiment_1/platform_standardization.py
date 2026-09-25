#!/usr/bin/env python3
"""平台构成标准化：池化曲线的"玩梗爆发"是真实转移还是平台构成变化？

问题
----
原始样本 52,716 行中，小红书（sinamidu）占 63%、抖音（gsdata）占 31%、微博（weibo）占 5%。
但三个平台的玩梗轨迹差异极大（W22 玩梗份额：抖音 82.4%、微博 40.8%、小红书 19.3%，
DeepSeek 轮）。若各平台发帖量随周变化，池化后的"玩梗爆发"可能主要由**平台构成变化**
产生，而不是各平台内部的表征转移。

方法
----
直接标准化（direct standardization）：把每周的平台构成固定为全窗口总体构成，重新加权
各平台的周级类别份额，得到"固定平台构成"下的反事实曲线：

    share*_{t,k} = Σ_p  w_p^overall · share_{p,t,k}

再与原始池化曲线比较。若爆发在标准化后基本消失，则池化结论不能作为跨平台表征转移的证据。

用法
----
    python platform_standardization.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CACHE = SCRIPT_DIR / "results" / "platform_heterogeneity" / "platform_weekly_matrices.json"
REPORT = SCRIPT_DIR / "results" / "platform_heterogeneity" / "STANDARDIZATION.md"

VALID_TYPES = ["meme", "mourning", "education", "marketing", "other"]
TYPE_CN = {"meme": "玩梗", "mourning": "悼念", "education": "教育",
           "marketing": "营销", "other": "其他"}
PLATFORM_CN = {"gsdata": "抖音", "sinamidu": "小红书", "weibo": "微博"}


def main() -> int:
    payload = json.loads(CACHE.read_text(encoding="utf-8"))
    cells: dict[str, dict[str, int]] = payload["cells"]
    labelers = sorted({k.split("|")[0] for k in cells})
    platforms = sorted({k.split("|")[1] for k in cells})
    weeks = sorted({k.split("|")[2] for k in cells})

    def counter(labeler: str, plat: str, wk: str) -> Counter:
        return Counter(cells.get(f"{labeler}|{plat}|{wk}", {}))

    lines = ["# 平台构成标准化：玩梗爆发是真实转移还是构成变化", ""]

    for labeler in labelers:
        # 总体平台构成（作为固定权重）
        overall = Counter()
        for wk in weeks:
            for p in platforms:
                overall[p] += sum(counter(labeler, p, wk)[t] for t in VALID_TYPES)
        total_all = sum(overall.values())
        weights = {p: overall[p] / total_all for p in platforms}

        # 逐周平台构成（用于展示是否漂移）
        lines += [f"## {labeler}", "", "### 周级平台构成（行占比）", ""]
        lines.append("| 周 | " + " | ".join(PLATFORM_CN.get(p, p) for p in platforms) + " | 池化玩梗 | 固定构成玩梗 |")
        lines.append("|---|" + "---|" * (len(platforms) + 2))
        for wk in weeks:
            wk_counts = {p: sum(counter(labeler, p, wk)[t] for t in VALID_TYPES) for p in platforms}
            wk_total = sum(wk_counts.values())
            comp = {p: (wk_counts[p] / wk_total if wk_total else 0.0) for p in platforms}
            raw_meme = 0.0
            if wk_total:
                raw_meme = sum(counter(labeler, p, wk)["meme"] for p in platforms) / wk_total
            std_meme = sum(
                weights[p] * (
                    counter(labeler, p, wk)["meme"] / wk_counts[p] if wk_counts[p] else 0.0
                )
                for p in platforms
            )
            lines.append(
                f"| {wk.replace('2026-', '')} | "
                + " | ".join(f"{comp[p]:.0%}" for p in platforms)
                + f" | {raw_meme:.1%} | {std_meme:.1%} |"
            )
        lines.append("")

        # 相位比较
        raw_series, std_series = {}, {}
        for wk in weeks:
            wk_counts = {p: sum(counter(labeler, p, wk)[t] for t in VALID_TYPES) for p in platforms}
            wk_total = sum(wk_counts.values())
            raw_series[wk] = (
                sum(counter(labeler, p, wk)["meme"] for p in platforms) / wk_total if wk_total else 0.0
            )
            std_series[wk] = sum(
                weights[p] * (counter(labeler, p, wk)["meme"] / wk_counts[p] if wk_counts[p] else 0.0)
                for p in platforms
            )

        def onset(series: dict[str, float]) -> str:
            pre = [v for w, v in series.items() if w < "2026-W13"]
            base = sum(pre) / len(pre) if pre else 0.0
            hit = next((w for w in weeks if w >= "2026-W13" and series[w] > base + 0.10), None)
            return (hit or "未触发").replace("2026-", "")

        lines += ["### 相位对比", "",
                  "| 口径 | 玩梗基线 | 起爆周 | 峰值周 | W22 玩梗 |",
                  "|---|---|---|---|---|"]
        for name, series in (("原始池化", raw_series), ("固定平台构成", std_series)):
            pre = [v for w, v in series.items() if w < "2026-W13"]
            base = sum(pre) / len(pre) if pre else 0.0
            peak = max(weeks, key=lambda w: series[w])
            lines.append(f"| {name} | {base:.1%} | {onset(series)} | "
                         f"{peak.replace('2026-', '')} | {series[weeks[-1]]:.1%} |")
        lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ 报告：{REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
