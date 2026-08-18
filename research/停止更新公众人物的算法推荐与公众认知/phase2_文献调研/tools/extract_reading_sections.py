#!/usr/bin/env python3
"""从已提取原文中定位摘要、方法、结果、讨论/结论、限制和利益冲突片段。"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_DIR = ROOT / "文献全文" / "提取文本"
OUT = ROOT / "精读卡片" / "原文结构化抽取"


SECTION_SPECS = {
    "摘要": (["abstract"], ["keywords", "key words", "introduction", "background"], 4200),
    "方法": (["methods", "methodology", "method", "data and methods", "research design", "materials and methods"], ["results", "findings", "analysis"], 6000),
    "结果": (["results", "findings"], ["discussion", "conclusion", "limitations"], 6000),
    "讨论与结论": (["discussion", "conclusion", "conclusions", "discussion and conclusion"], ["references", "acknowledg", "funding", "notes"], 6000),
    "限制": (["limitations", "limitation", "study limitations"], ["conclusion", "references", "acknowledg", "funding"], 3500),
    "资助与利益冲突": (["funding", "conflict of interest", "declaration of conflicting interests", "competing interests"], ["references", "notes", "appendix"], 2500),
}


def clean(text: str) -> str:
    text = re.sub(r"\n===== PAGE \d+ =====\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def heading_match(text: str, label: str):
    return re.search(rf"(?im)^\s*(?:\d+(?:\.\d+)*[.)]?\s+)?{re.escape(label)}\s*[:.]?\s*$", text)


def section(text: str, starts: list[str], ends: list[str], limit: int) -> str:
    start_match = None
    for label in starts:
        candidate = heading_match(text, label)
        if candidate and (start_match is None or candidate.start() < start_match.start()):
            start_match = candidate
    if start_match is None:
        # 摘要在部分PDF中与正文同行，使用谨慎后备匹配。
        for label in starts:
            candidate = re.search(rf"(?i)\b{re.escape(label)}\b\s*[:.—-]\s*", text[:18000])
            if candidate:
                start_match = candidate
                break
    if start_match is None:
        return "[未自动定位；不代表原文无此部分]"
    start = start_match.end()
    search_window = text[start:start + limit * 2]
    end_positions = []
    for label in ends:
        candidate = heading_match(search_window, label)
        if candidate:
            end_positions.append(candidate.start())
    end = start + (min(end_positions) if end_positions else min(len(search_window), limit))
    return clean(text[start:end])[:limit]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (TEXT_DIR / "index.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        source = ROOT / row["文本文件"]
        text = source.read_text(encoding="utf-8", errors="ignore")
        header, _, body = text.partition("提取说明:")
        if body:
            body = body.partition("\n")[2]
        else:
            body = text
        chunks = [f'# {row["ID"]} 原文结构化抽取', "", header.strip(), ""]
        for name, (starts, ends, limit) in SECTION_SPECS.items():
            chunks.extend([f"## {name}", "", section(body, starts, ends, limit), ""])
        chunks.extend([
            "## 使用限制", "",
            "本文件是自动定位的原文片段，可能受PDF栏布、页眉或标题格式影响。它用于辅助定位，不取代对原PDF的引文复核。", "",
        ])
        (OUT / f'{row["ID"]}_原文抽取.md').write_text("\n".join(chunks), encoding="utf-8")
        print(row["ID"], flush=True)


if __name__ == "__main__":
    main()
