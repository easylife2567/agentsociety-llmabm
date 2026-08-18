#!/usr/bin/env python3
"""将已验证的 PDF/HTML 正文转为带来源头的纯文本，供精读与引文定位。"""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "文献全文" / "下载与校验清单.tsv"
OUT = ROOT / "文献全文" / "提取文本"


def pdf_text(path: Path) -> tuple[str, int]:
    document = fitz.open(path)
    pages = [f"\n\n===== PAGE {index + 1} =====\n\n{page.get_text()}" for index, page in enumerate(document)]
    count = document.page_count
    document.close()
    return "".join(pages), count


def html_text(path: Path) -> tuple[str, int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<svg.*?</svg>", " ", text)
    text = re.sub(r"(?i)</?(p|div|section|article|h[1-6]|li|br|tr|blockquote)[^>]*>", "\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, 1


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if row["状态"] == "verified_downloaded"]
    index_rows = []
    for row in rows:
        source = ROOT / row["本地文件"]
        if source.suffix.lower() == ".pdf":
            body, pages = pdf_text(source)
        else:
            body, pages = html_text(source)
        header = (
            f'ID: {row["ID"]}\nDOI: {row["DOI"]}\n中文译名: {row["中文译名"]}\n'
            f'英文原题: {row["英文原题"]}\n原文件: {row["本地文件"]}\n源URL: {row["源URL"]}\n'
            f'提取说明: 仅为机械文本提取，页码标记依原PDF；不代表已完成论证核验。\n'
        )
        target = OUT / f'{row["ID"]}_{re.sub(r"[^A-Za-z0-9_-]+", "_", row["英文原题"])[:80]}.txt'
        target.write_text(header + body, encoding="utf-8")
        index_rows.append((row["ID"], row["DOI"], str(target.relative_to(ROOT)), pages, len(body)))
        print(f'{row["ID"]}: pages={pages}, chars={len(body)}', flush=True)
    with (OUT / "index.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["ID", "DOI", "文本文件", "页数", "字符数"])
        writer.writerows(index_rows)


if __name__ == "__main__":
    main()
