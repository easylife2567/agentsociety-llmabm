#!/usr/bin/env python3
"""批量核验候选 DOI 的 Crossref/OpenAlex/Semantic Scholar 元数据及 OA 线索。"""

from __future__ import annotations

import concurrent.futures
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seed_dois.txt"
OUTPUT_JSON = ROOT / "03_元数据交叉核验.json"
OUTPUT_TSV = ROOT / "03_元数据交叉核验.tsv"
USER_AGENT = "AgentSociety-literature-review/0.1 (academic metadata verification)"


def get_json(url: str, timeout: int = 30) -> tuple[dict | None, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except Exception as exc:  # 将提供商降级保存为数据，不中断其他核验
        return None, f"{type(exc).__name__}: {exc}"


def first(value):
    if isinstance(value, list) and value:
        return value[0]
    return value


def crossref(doi: str) -> dict:
    encoded = urllib.parse.quote(doi, safe="")
    data, error = get_json(f"https://api.crossref.org/works/{encoded}")
    if error or not data:
        return {"status": "degraded", "error": error}
    message = data.get("message", {})
    authors = [
        " ".join(part for part in (a.get("given", ""), a.get("family", "")) if part).strip()
        for a in message.get("author", [])
    ]
    date_parts = first(message.get("published-print", {}).get("date-parts")) or first(
        message.get("published-online", {}).get("date-parts")
    ) or first(message.get("issued", {}).get("date-parts")) or []
    return {
        "status": "matched",
        "title": first(message.get("title")) or "",
        "authors": authors,
        "year": date_parts[0] if date_parts else None,
        "venue": first(message.get("container-title")) or "",
        "publisher": message.get("publisher", ""),
        "type": message.get("type", ""),
        "url": message.get("URL", ""),
        "license": [item.get("URL") for item in message.get("license", []) if item.get("URL")],
    }


def openalex(doi: str) -> dict:
    key = urllib.parse.quote(f"https://doi.org/{doi}", safe="")
    data, error = get_json(f"https://api.openalex.org/works/{key}")
    if error or not data:
        return {"status": "degraded" if error and error != "HTTP 404" else "unmatched", "error": error}
    locations = []
    for loc in data.get("locations", []):
        locations.append(
            {
                "pdf_url": loc.get("pdf_url"),
                "landing_page_url": loc.get("landing_page_url"),
                "is_oa": loc.get("is_oa"),
                "version": loc.get("version"),
                "source": (loc.get("source") or {}).get("display_name"),
            }
        )
    best = data.get("best_oa_location") or {}
    return {
        "status": "matched",
        "id": data.get("id"),
        "title": data.get("title", ""),
        "year": data.get("publication_year"),
        "cited_by_count": data.get("cited_by_count"),
        "type": data.get("type"),
        "oa_status": (data.get("open_access") or {}).get("oa_status"),
        "is_oa": (data.get("open_access") or {}).get("is_oa"),
        "best_oa_pdf": best.get("pdf_url"),
        "best_oa_landing": best.get("landing_page_url"),
        "locations": locations,
    }


def semantic_scholar(doi: str) -> dict:
    key = urllib.parse.quote(f"DOI:{doi}", safe=":")
    fields = urllib.parse.quote("paperId,title,year,authors,venue,externalIds,openAccessPdf", safe=",")
    data, error = get_json(f"https://api.semanticscholar.org/graph/v1/paper/{key}?fields={fields}")
    if error or not data:
        return {"status": "degraded" if error and error != "HTTP 404" else "unmatched", "error": error}
    return {
        "status": "matched",
        "paper_id": data.get("paperId"),
        "title": data.get("title", ""),
        "year": data.get("year"),
        "venue": data.get("venue", ""),
        "open_access_pdf": (data.get("openAccessPdf") or {}).get("url"),
    }


def semantic_scholar_batch(dois: list[str]) -> dict[str, dict]:
    fields = "paperId,title,year,authors,venue,externalIds,openAccessPdf"
    url = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=" + urllib.parse.quote(fields, safe=",")
    payload = json.dumps({"ids": [f"DOI:{doi}" for doi in dois]}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            results = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {doi: {"status": "degraded", "error": f"HTTP {exc.code}"} for doi in dois}
    except Exception as exc:
        return {doi: {"status": "degraded", "error": f"{type(exc).__name__}: {exc}"} for doi in dois}
    output = {}
    for doi, data in zip(dois, results):
        if not data:
            output[doi] = {"status": "unmatched", "error": "batch null"}
            continue
        output[doi] = {
            "status": "matched",
            "paper_id": data.get("paperId"),
            "title": data.get("title", ""),
            "year": data.get("year"),
            "venue": data.get("venue", ""),
            "open_access_pdf": (data.get("openAccessPdf") or {}).get("url"),
        }
    return output


def doi_resolution(doi: str) -> dict:
    request = urllib.request.Request(
        f"https://doi.org/{urllib.parse.quote(doi, safe='/')}",
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return {"status": "resolved", "http_status": response.status, "final_url": response.geturl()}
    except urllib.error.HTTPError as exc:
        # 部分出版商拒绝 HEAD，但 DOI 重定向已成功到达出版商站点。
        if exc.code in {401, 403, 405, 406, 429} and "doi.org" not in exc.geturl():
            return {"status": "resolved_restricted", "http_status": exc.code, "final_url": exc.geturl()}
        return {"status": "failed" if exc.code == 404 else "degraded", "http_status": exc.code, "final_url": exc.geturl()}
    except Exception as exc:
        return {"status": "degraded", "error": f"{type(exc).__name__}: {exc}"}


def resolve_core(doi: str) -> dict:
    return {"doi": doi, "crossref": crossref(doi), "openalex": openalex(doi), "doi_resolution": doi_resolution(doi)}


def main() -> None:
    dois = [line.strip().lower() for line in SEEDS.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(resolve_core, dois))

    # 使用公开 batch 端点，减少请求数并保留每条降级状态。
    s2_records = semantic_scholar_batch(dois)
    for record in records:
        record["semantic_scholar"] = s2_records[record["doi"]]

    OUTPUT_JSON.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    headers = [
        "doi", "title", "authors", "year", "venue", "publisher", "crossref", "openalex", "semantic_scholar", "doi_resolution",
        "is_oa", "oa_status", "oa_pdf", "oa_landing", "cited_by_count",
    ]
    rows = ["\t".join(headers)]
    for record in records:
        cr, oa, s2 = record["crossref"], record["openalex"], record["semantic_scholar"]
        row = [
            record["doi"], cr.get("title", "") or oa.get("title", ""), "; ".join(cr.get("authors", [])),
            str(cr.get("year") or oa.get("year") or ""), cr.get("venue", ""), cr.get("publisher", ""),
            cr.get("status", ""), oa.get("status", ""), s2.get("status", ""), record["doi_resolution"].get("status", ""), str(oa.get("is_oa", "")),
            str(oa.get("oa_status", "") or ""), oa.get("best_oa_pdf", "") or s2.get("open_access_pdf", "") or "",
            oa.get("best_oa_landing", "") or "", str(oa.get("cited_by_count", "") or ""),
        ]
        rows.append("\t".join(str(item).replace("\t", " ").replace("\n", " ") for item in row))
    OUTPUT_TSV.write_text("\n".join(rows) + "\n", encoding="utf-8")
    matched = sum(r["crossref"].get("status") == "matched" for r in records)
    oa_count = sum(bool(r["openalex"].get("is_oa")) for r in records)
    print(json.dumps({"records": len(records), "crossref_matched": matched, "open_access_candidates": oa_count, "json": str(OUTPUT_JSON), "tsv": str(OUTPUT_TSV)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
