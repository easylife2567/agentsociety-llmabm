#!/usr/bin/env python3
"""Register the phase2 文献调研 corpus (research/) into papers/literature_index.json.

Reads the prior-work corpus built on 2026-08-17 under
research/停止更新公众人物的算法推荐与公众认知/phase2_文献调研/ and converts it
into the pipeline's literature index contract (see
.claude/skills/agentsociety-literature-search/SKILL.md, "Index Contract").

Sources used:
- 03_元数据交叉核验.tsv                -> per-DOI metadata (title, authors, year, venue, OA status...)
- 01_候选文献清单.md                   -> per-ID cluster, relevance, selection status, full-text path
- 07_来源质量矩阵与方法分布_v0.1.md     -> per-ID evidence level + discipline rating (32 full-text only)
- 精读卡片/逐篇深度精读/               -> deep-reading card markdown paths (32)

Provenance: entries are flagged source="prior_work_registration" with prior_id (L001..L067)
so downstream pipeline stages can distinguish them from searches run through this workspace.
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PHASE2 = WORKSPACE / "research/停止更新公众人物的算法推荐与公众认知/phase2_文献调研"
TSV = PHASE2 / "03_元数据交叉核验.tsv"
CANDIDATES = PHASE2 / "01_候选文献清单.md"
QUALITY = PHASE2 / "07_来源质量矩阵与方法分布_v0.1.md"
CARDS_DIR = PHASE2 / "精读卡片/逐篇深度精读"
OUT = WORKSPACE / "papers/literature_index.json"


def _norm(s: str) -> str:
    """Normalize a title for fuzzy matching: unescape entities, drop punctuation/whitespace."""
    s = html.unescape(s)
    s = re.sub(r"[\W_]+", "", s).lower()
    return s


def parse_tsv(path: Path) -> dict[str, dict]:
    """title(normalized) -> metadata row."""
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip()]
    header = rows[0]
    for row in rows[1:]:
        rec = dict(zip(header, row))
        out[_norm(rec["title"])] = rec
    return out


def parse_candidates(path: Path) -> dict[str, dict]:
    """L001..L067 -> candidate info from the markdown table."""
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("| L"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            # ID title authors year source DOI cluster relevance selection verification notes
            out[cells[0]] = {
                "title": _norm(cells[1]),
                "cluster": cells[6],
                "relevance": cells[7],
                "selection": cells[8],
                "note": cells[10],
            }
    return out


def parse_quality(path: Path) -> dict[str, dict]:
    """Cluster ID (A01..D06) -> (evidence_level, rating) for the 32 full-text papers."""
    out: dict[str, dict] = {}
    roman = re.compile(r"^(VII|VI|IV|III|II|V|I)$")
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            cells = [c.strip() for c in line.strip("|").split("|")] if line.startswith("|") else []
            if len(cells) < 6:
                continue
            if not re.match(r"^[A-D]\d{2}$", cells[0] or ""):
                continue  # not a data row (ID lives in column 0)
            if not roman.match(cells[4] or ""):
                continue
            out[cells[0]] = {"evidence_level": cells[4], "rating": cells[5]}
    return out


def parse_cards() -> dict[str, Path]:
    """ID -> card markdown path (relative to workspace root)."""
    out: dict[str, Path] = {}
    for p in sorted(CARDS_DIR.glob("*.md")):
        m = re.match(r"^([A-D]\d{2})_", p.name)
        if m:
            out[m.group(1)] = p.relative_to(WORKSPACE)
    return out


def main() -> int:
    tsv = parse_tsv(TSV)
    cand = parse_candidates(CANDIDATES)
    qual = parse_quality(QUALITY)
    cards = parse_cards()

    entries = []
    failures = []
    for pid in sorted(cand):
        c = cand[pid]
        rec = tsv.get(c["title"])
        if rec is None:
            failures.append(f"{pid}: no TSV title match for {c['title'][:60]}…")
            continue
        full_text = c["selection"] == "全文纳入"
        # Cluster IDs (A01..D06) come from the full-text filename in the note;
        # they are the key both for the deep-reading cards and the quality matrix.
        cluster_id = None
        full_text_path = None
        if full_text:
            m = re.search(r"已取得正文：(.+)", c["note"])
            if m:
                full_text_path = m.group(1).strip()
                # full-text filenames embed the cluster id, e.g. ".../正文/A01_2017_....pdf"
                fm = re.search(r"([A-D]\d{2})_\d{4}_", full_text_path)
                if fm:
                    cluster_id = fm.group(1)
        has_card = cluster_id is not None and cluster_id in cards

        entry: dict = {
            "title": rec["title"],
            "journal": rec["venue"],
            "doi": rec["doi"],
            "source": "prior_work_registration",
            "query": c["cluster"],
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        if has_card:
            entry["file_path"] = str(cards[cluster_id])
            entry["file_type"] = "markdown"
        extra: dict = {
            "authors": [a.strip() for a in rec["authors"].split(";")],
            "year": int(rec["year"]),
            "url": f"https://doi.org/{rec['doi']}",
            "prior_id": pid,
            "concept_cluster": c["cluster"],
            "relevance": c["relevance"],
            "selection_status": "full_text" if full_text else "title_abstract",
            "verification": "VERIFIED",
            "is_oa": rec["is_oa"] == "True",
            "oa_status": rec["oa_status"],
            "cited_by_count": int(rec["cited_by_count"]),
        }
        if full_text_path:
            extra["full_text_file"] = str(PHASE2.relative_to(WORKSPACE) / full_text_path)
        if cluster_id in qual:
            extra.update(qual[cluster_id])
        if cluster_id is not None:
            extra["cluster_id"] = cluster_id  # prior work's A01..D06 id
        entry["extra_fields"] = extra
        entries.append(entry)

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1

    now = datetime.now(timezone.utc).isoformat()
    with OUT.open(encoding="utf-8") as f:
        existing = json.load(f)
    doc = {
        "version": existing.get("version", "1.0"),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "entries": entries,
    }
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")

    n_full = sum(1 for e in entries if e["extra_fields"]["selection_status"] == "full_text")
    n_cards = sum(1 for e in entries if "file_path" in e)
    n_level = sum(1 for e in entries if "evidence_level" in e["extra_fields"])
    print(f"registered {len(entries)} entries; full_text={n_full}, cards={n_cards}, leveled={n_level}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
