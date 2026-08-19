#!/usr/bin/env python3
"""q6 完整性校验：结果页抓取标题 vs q6.txt 导出记录。

规范化：剥离副标题（——之后）→ 去非单词字符 → 小写（Python re 的 \w 支持中文）。
"""
import json
import re
import sys
from pathlib import Path

TITLES = Path("/tmp/q6_titles.json")
NET = Path(__file__).resolve().parent.parent / "papers/cnki_export/q6.txt"


def norm(t: str) -> str:
    main = t.split("——")[0].split("--")[0]
    return re.sub(r"[\W_]+", "", main).lower()


def main() -> int:
    page_titles = json.loads(TITLES.read_text(encoding="utf-8"))
    net = NET.read_text(encoding="utf-8")
    blocks = [b.strip() for b in net.split("\n{Reference Type}:") if b.strip()]

    exported = []
    for b in blocks:
        m = re.search(r"\{Title\}:\s*(.+)", b)
        exported.append(m.group(1).strip() if m else "?")

    exp_map: dict[str, list[str]] = {}
    for t in exported:
        exp_map.setdefault(norm(t), []).append(t)

    missing, seen = [], set()
    for t in page_titles:
        k = norm(t)
        if k in seen:
            continue
        seen.add(k)
        if k not in exp_map:
            missing.append(t)

    dups = {k: v for k, v in exp_map.items() if len(v) > 1}
    print(json.dumps({
        "page_unique": len(page_titles),
        "exported": len(exported),
        "missing": missing,
        "dup_keys": len(dups),
        "dup_examples": {k: v for k, v in list(dups.items())[:10]},
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
