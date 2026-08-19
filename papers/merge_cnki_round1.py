#!/usr/bin/env python3
"""Merge CNKI round-1 exports (q1-q6) into papers/literature_index.json.

Reads papers/cnki_export/q{1..6}.txt (NoteExpress format) and appends
deduplicated records with source="cnki_wanfang_round1". Dedup keys:
normalized (title, first author) within and across queries, plus title-match
against the existing 67 prior-work entries (L001-L067, mostly English).

Provenance: every record keeps its query expression, record type, CNKI URL/DOI,
and an honesty-correct selection_status=title_abstract (题录级，未精读).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
EXPORT = WORKSPACE / "papers/cnki_export"
OUT = WORKSPACE / "papers/literature_index.json"

QUERIES = {
    "q1": "SU=(网络悼念 + 数字遗产 + 数字来生 + 身后身份 + 数字死亡)（学术期刊口径）",
    "q2": "SU=(名人 + 明星 + 公众人物) * (社交媒体 + 短视频 + 抖音) * (去世 + 死亡 + 逝世 + 离世)",
    "q3": "SU=(张雪峰 + 公众人物) * (算法推荐 + 信息茧房 + 流量)",
    "q4": "SU=短视频 * (去语境化 + 碎片化叙事 + 标签化)",
    "q5": "SU=(算法推荐 + 推荐算法) * (重复曝光 + 内容同质化 + 回声室 + 茧房)（近5年口径）",
    "q6": "SU=(首因效应 + 第一印象 + 印象形成) * (社交媒体 + 网络)",
}

RELEVANCE_GROUPS = {
    "q1": "中文数字哀悼/数字遗产",
    "q2": "本土名人死亡传播",
    "q3": "个案本土研究（公众人物×算法流量）",
    "q4": "短视频叙事机制（去语境化/碎片化/标签化）",
    "q5": "算法曝光机制（茧房/回声室/同质化）",
    "q6": "首因/印象形成（社交媒体/网络）",
}

VENUE_TYPES = {
    "Journal Article": "journal",
    "Newspaper Article": "newspaper",
    "Thesis": "thesis",
    "Book": "book",
    "Conference Proceedings": "conference",
}


def norm(s: str) -> str:
    return re.sub(r"[\W_]+", "", s or "").lower()


def parse_blocks(text: str) -> list[dict[str, str]]:
    # 按行首的 {Reference Type}: 分割，且保留类型值在块首
    parts = re.split(r"(?m)^\{Reference Type\}:\s*", text)
    recs = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.splitlines()
        fields: dict[str, str] = {}
        m0 = re.match(r"^([^\n{]+)$", lines[0].strip()) if lines else None
        if m0:
            fields["Reference Type"] = lines[0].strip()
            lines = lines[1:]
        for line in lines:
            m = re.match(r"\{([^}]+)\}:\s*(.*)", line)
            if m:
                fields[m.group(1)] = m.group(2).strip()
        recs.append(fields)
    return recs


def pick_year(f: dict[str, str]):
    for key in ("Year", "Date"):
        if f.get(key):
            m = re.search(r"(\d{4})", f[key])
            if m:
                return int(m.group(1))
    return None


def venue_of(f: dict[str, str], vtype: str) -> str | None:
    if vtype == "journal":
        return f.get("Journal") or f.get("Secondary Title")
    if vtype == "newspaper":
        return f.get("Secondary Title") or f.get("Publisher")
    if vtype in ("thesis", "book"):
        return f.get("Publisher")
    if vtype == "conference":
        # NoteExpress 会议论文的会议名称在 {Secondary Title}，地点在 {Place Published}
        return f.get("Journal") or f.get("Secondary Title") or f.get("Place Published") or f.get("Publisher")
    return None


def make_entry(f: dict[str, str], qid: str, rt: str) -> dict:
    vtype = VENUE_TYPES.get(rt, rt.lower().replace(" ", "_"))
    authors = [a.strip() for a in (f.get("Author") or "").split(";") if a.strip()]
    year = pick_year(f)
    venue = venue_of(f, vtype)
    extra: dict = {
        "authors": authors,
        "record_type": rt,
        "venue_type": vtype,
        "selection_status": "title_abstract",
        "verification": "CNKI_EXPORT",  # 数据库直出题录，未逐条独立核验
        "relevance_group": RELEVANCE_GROUPS[qid],
    }
    if year is not None:
        extra["year"] = year
    if f.get("URL"):
        extra["url"] = f["URL"]
    if f.get("DOI"):
        extra["doi"] = f["DOI"]
    if f.get("Keywords"):
        extra["keywords"] = [k.strip() for k in f["Keywords"].split(";") if k.strip()]
    if f.get("Tertiary Author"):  # 学位论文导师
        extra["supervisor"] = f["Tertiary Author"]
    if f.get("Type of Work"):  # 硕/博
        extra["degree"] = f["Type of Work"]

    entry: dict = {
        "title": f.get("Title") or "?",
        "source": "cnki_wanfang_round1",
        "query": f"{qid}: {QUERIES[qid]}",
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    if f.get("Abstract"):
        entry["abstract"] = f["Abstract"]
    if venue:
        entry["journal"] = venue
    entry["extra_fields"] = extra
    return entry


def main() -> int:
    # 1) parse all exports
    parsed: dict[str, list[dict]] = {}
    for qid in QUERIES:
        path = EXPORT / f"{qid}.txt"
        if not path.exists():
            print(f"SKIP {qid}: {path} missing", file=sys.stderr)
            continue
        blocks = parse_blocks(path.read_text(encoding="utf-8"))
        recs = []
        for b in blocks:
            rt = b.get("Reference Type", "?")
            vtype = VENUE_TYPES.get(rt)
            if vtype is None:
                print(f"WARN {qid}: unknown type {rt!r} for {b.get('Title','')[:40]}", file=sys.stderr)
                vtype = rt.lower().replace(" ", "_")
            recs.append(make_entry(b, qid, rt))
        parsed[qid] = recs

    total_raw = sum(len(v) for v in parsed.values())

    # 2) dedup within+across queries by (norm title, norm first author)
    seen: dict[tuple[str, str], dict] = {}
    merged: dict[tuple[str, str], list[str]] = {}
    for qid in QUERIES:
        for e in parsed.get(qid, []):
            authors = e["extra_fields"].get("authors", [])
            key = (norm(e["title"]), norm(authors[0]) if authors else "")
            if key in seen:
                merged.setdefault(key, [seen[key]["query"].split(":")[0]])
                merged[key].append(qid)
                seen[key]["query"] += f" | {qid}: {QUERIES[qid]}"
                continue
            seen[key] = e
    entries_new = list(seen.values())
    n_dups = total_raw - len(entries_new)
    n_merged = sum(len(v) - 1 for v in merged.values())

    # 3) dedup vs existing 67 entries (title-normalized)
    with OUT.open(encoding="utf-8") as f:
        doc = json.load(f)
    existing_titles = {norm(e["title"]) for e in doc["entries"]}
    kept, n_overlap = [], 0
    for e in entries_new:
        if norm(e["title"]) in existing_titles:
            n_overlap += 1
            continue
        kept.append(e)

    # 4) write back
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    doc["entries"] = doc["entries"] + kept
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")

    per_query = {qid: len(parsed.get(qid, [])) for qid in QUERIES}
    print(json.dumps({
        "per_query_raw": per_query,
        "total_raw": total_raw,
        "in_query_dups": n_dups,
        "cross_query_merged": n_merged,
        "after_dedup": len(entries_new),
        "overlap_with_prior67": n_overlap,
        "appended": len(kept),
        "index_total": len(doc["entries"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
