#!/usr/bin/env python3
"""从人工核验的 OA 线索下载正文，生成双语文件名并校验题名。"""

from __future__ import annotations

import concurrent.futures
import csv
import hashlib
import html
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "04_全文下载计划.tsv"
LIBRARY = ROOT / "文献全文"
BODY = LIBRARY / "正文"
QUARANTINE = LIBRARY / "需人工复核"
MANIFEST = LIBRARY / "下载与校验清单.tsv"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AcademicResearch/1.0"

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "in", "on", "to", "for", "with", "from", "by", "as",
    "is", "are", "how", "what", "when", "through", "about", "into", "its", "their", "this", "that",
    "social", "media", "study", "case", "effects", "effect", "research", "investigating", "analysis",
}


def safe_piece(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]", "", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value


def truncate_utf8(value: str, byte_limit: int) -> str:
    raw = value.encode("utf-8")
    if len(raw) <= byte_limit:
        return value
    clipped = raw[:byte_limit]
    while clipped:
        try:
            return clipped.decode("utf-8").rstrip() + "…"
        except UnicodeDecodeError:
            clipped = clipped[:-1]
    return ""


def bilingual_stem(row: dict[str, str]) -> str:
    zh = truncate_utf8(safe_piece(row["中文译名"]), 92)
    en = truncate_utf8(safe_piece(row["英文原题"]), 105)
    return f'{row["ID"]}_{row["年份"]}_{zh}__{en}'


def title_tokens(title: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9]+", title.lower())
        if len(token) >= 3 and token not in STOPWORDS
    }


def title_overlap(title: str, text: str) -> float:
    expected = title_tokens(title)
    if not expected:
        return 0.0
    observed = set(re.findall(r"[a-z0-9]+", text.lower()))
    return len(expected & observed) / len(expected)


def verify_pdf(path: Path, title: str) -> tuple[bool, int, float, str]:
    if path.stat().st_size < 20_000 or path.read_bytes()[:4] != b"%PDF":
        return False, 0, 0.0, "不是有效PDF或文件过小"
    try:
        document = fitz.open(path)
        pages = document.page_count
        text = "\n".join(document[index].get_text() for index in range(min(5, pages)))
        document.close()
    except Exception as exc:
        return False, 0, 0.0, f"PDF解析失败: {type(exc).__name__}"
    overlap = title_overlap(title, text)
    if pages <= 0:
        return False, pages, overlap, "PDF页数为0"
    if len(text.strip()) < 300 and overlap < 0.25:
        return False, pages, overlap, "首页缺少可校验文本"
    if overlap < 0.34:
        return False, pages, overlap, "英文原题与首五页文本匹配度过低"
    return True, pages, overlap, "题名与PDF文本匹配"


def html_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="ignore")
    text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def verify_html(path: Path, title: str) -> tuple[bool, float, str]:
    text = html_text(path.read_bytes())
    overlap = title_overlap(title, text[:80_000])
    if len(text) < 8_000:
        return False, overlap, "HTML可读文本过短，可能仅为摘要或登录页"
    if overlap < 0.45:
        return False, overlap, "英文原题与HTML文本匹配度过低"
    return True, overlap, "题名与HTML全文候选匹配"


def download(row: dict[str, str]) -> dict[str, str]:
    result = {
        "ID": row["ID"], "DOI": row["DOI"], "中文译名": row["中文译名"], "英文原题": row["英文原题"],
        "源URL": row["开放全文线索"], "状态": "", "格式": "", "字节数": "", "页数": "", "题名匹配率": "",
        "SHA256": "", "本地文件": "", "说明": "",
    }
    url = row["开放全文线索"].strip()
    if not url:
        result["状态"] = "oa_url_unavailable"
        result["说明"] = row["计划状态"]
        return result

    with tempfile.TemporaryDirectory(prefix=f'lit-{row["ID"]}-') as temp_dir:
        candidate = Path(temp_dir) / "candidate"
        command = [
            "curl", "--http1.1", "-L", "--fail", "--silent", "--show-error", "--max-time", "75", "--retry", "1",
            "--retry-delay", "2", "-A", USER_AGENT, "-o", str(candidate), url,
        ]
        proc = subprocess.run(command, capture_output=True, text=True)
        if proc.returncode != 0 or not candidate.exists():
            result["状态"] = "download_failed"
            result["说明"] = (proc.stderr or f"curl exit {proc.returncode}").strip()[-300:]
            return result

        header = candidate.read_bytes()[:512].lstrip()
        if header.startswith(b"\x1f\x8b"):
            try:
                with tarfile.open(candidate, mode="r:gz") as archive:
                    pdf_members = [
                        member for member in archive.getmembers()
                        if member.isfile() and member.name.lower().endswith(".pdf")
                        and not re.search(r"(supp|append|table|fig)", member.name, re.I)
                    ]
                    if not pdf_members:
                        raise ValueError("OA包内未找到正文PDF")
                    pdf_members.sort(key=lambda member: member.size, reverse=True)
                    extracted = archive.extractfile(pdf_members[0])
                    if extracted is None:
                        raise ValueError("OA包内PDF无法读取")
                    candidate.write_bytes(extracted.read())
                    header = candidate.read_bytes()[:512].lstrip()
            except Exception as exc:
                ok, note, extension = False, f"OA包解析失败: {type(exc).__name__}: {exc}", ".tgz"
                target_root = QUARANTINE
                target_root.mkdir(parents=True, exist_ok=True)
                target = target_root / f"{bilingual_stem(row)}{extension}"
                shutil.move(candidate, target)
                result["状态"], result["格式"], result["字节数"] = "downloaded_needs_review", "TGZ", str(target.stat().st_size)
                result["SHA256"] = hashlib.sha256(target.read_bytes()).hexdigest()
                result["本地文件"], result["说明"] = str(target.relative_to(ROOT)), note
                return result
        stem = bilingual_stem(row)
        if header.startswith(b"%PDF"):
            ok, pages, overlap, note = verify_pdf(candidate, row["英文原题"])
            extension = ".pdf"
            result["格式"], result["页数"], result["题名匹配率"] = "PDF", str(pages), f"{overlap:.2f}"
        elif b"<html" in header.lower() or b"<!doctype" in header.lower():
            ok, overlap, note = verify_html(candidate, row["英文原题"])
            extension = ".html"
            result["格式"], result["题名匹配率"] = "HTML", f"{overlap:.2f}"
        else:
            ok, note, extension = False, "返回内容既非PDF也非HTML", ".bin"

        target_root = BODY if ok else QUARANTINE
        target_root.mkdir(parents=True, exist_ok=True)
        target = target_root / f"{stem}{extension}"
        shutil.move(candidate, target)
        result["状态"] = "verified_downloaded" if ok else "downloaded_needs_review"
        result["字节数"] = str(target.stat().st_size)
        result["SHA256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        result["本地文件"] = str(target.relative_to(ROOT))
        result["说明"] = note
        return result


def main() -> None:
    BODY.mkdir(parents=True, exist_ok=True)
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    with PLAN.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    selected_ids = None
    if len(sys.argv) == 3 and sys.argv[1] == "--ids":
        selected_ids = {item.strip() for item in sys.argv[2].split(",") if item.strip()}
        rows = [row for row in rows if row["ID"] in selected_ids]
    elif len(sys.argv) != 1:
        raise SystemExit("用法: download_bilingual_oa.py [--ids A01,B02,...]")

    prior = {}
    if MANIFEST.exists():
        with MANIFEST.open(encoding="utf-8", newline="") as handle:
            prior = {row["ID"]: row for row in csv.DictReader(handle, delimiter="\t")}
    results = []
    # 小并发批次：降低对单一出版商的瞬时压力。
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(download, row): row["ID"] for row in rows}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f'[{result["ID"]}] {result["状态"]}: {result["说明"]}', flush=True)

    for result in results:
        prior[result["ID"]] = result
    results = sorted(prior.values(), key=lambda item: item["ID"])
    headers = [
        "ID", "DOI", "中文译名", "英文原题", "源URL", "状态", "格式", "字节数", "页数", "题名匹配率", "SHA256", "本地文件", "说明",
    ]
    with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t")
        writer.writeheader()
        writer.writerows(results)
    summary = {}
    for result in results:
        summary[result["状态"]] = summary.get(result["状态"], 0) + 1
    print(f"清单: {MANIFEST}", flush=True)
    print("汇总: " + ", ".join(f"{key}={value}" for key, value in sorted(summary.items())), flush=True)


if __name__ == "__main__":
    main()
