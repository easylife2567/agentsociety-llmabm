#!/usr/bin/env python3
"""从已采用Markdown只读装配Word合稿源，不改动原稿或实验资产。

从项目根运行：
    AgentSociety2/.venv/bin/python paper/word/scripts/assemble_article.py

本脚本生成主体块及修订依据。正式参考文献块由同轮书目整理步骤接入，
reference_ids保留正文原脚注标识及首次出现顺序，便于对应书目来源。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ABSTRACT = (
    "公众人物离世后，持续的社交媒体讨论如何改变其公共呈现，需要同时考察内容构成与传播过程。"
    "以张雪峰为例，本文结合抖音和小红书49,930条帖文的内容分析，以及大语言模型多智能体仿真，"
    "研究逝者数字表征的时序演化与生成机制。现实样本呈现事件期悼念集中、玩梗随后增长的共同顺序，"
    "两平台的晚期内容构成则存在差异。仿真在共同输入与固定群体条件下比较随机、时序和兴趣制度的九次运行，"
    "并通过九次组件消融考察表达规则。时序和兴趣制度均形成晚期玩梗型作者供给占多数的格局，"
    "随机制度的相应供给较少。过程记录与消融显示，个人接触、表达参与和生成帖再流通相互连接，"
    "参与时机与持续程度的变化共同重组后续供给及可见位置。研究据此将逝后关注的延续推进到公共表征如何重组的问题，"
    "为理解策展制度与用户表达的循环关系提供机制参照。"
)
KEYWORDS = ["数字哀悼", "公共表征", "算法策展", "传播反馈", "多智能体仿真"]
FIGURE_FILES = {
    1: "figure_01_observed_pooled.png",
    2: "figure_02_observed_platforms.png",
    3: "figure_03_simulated_trajectories.png",
    4: "figure_04_feedback_exposure.png",
    5: "figure_05_bdr_ablation.png",
}

# 只给缺少年份的既有叙述式引用补年份，不改写作者已经采用的论述。
NARRATIVE_YEARS = {
    "bg1": ("Uwalaka发现", "Uwalaka（2023）发现"),
    "bg2": ("Clancy对", "Clancy（2024）对"),
    "bg3": ("高嘉潞指出", "高嘉潞（2024）指出"),
    "bg4": ("Adriaansen和Smit指出", "Adriaansen和Smit（2025）指出"),
    "bg5": ("Eriksson Krutrök提出", "Eriksson Krutrök（2021）提出"),
    "bg6": ("West等追踪", "West等（2021）追踪"),
    "bg7": ("Shifman指出", "Shifman（2013）指出"),
    "bg8": ("Jenkins的参与式文化研究", "Jenkins（2006）的参与式文化研究"),
    "bg9": ("Nissenbaum等指出", "Nissenbaum等（2017）指出"),
    "bg10": ("Bou-Franch和Yus对", "Bou-Franch和Yus（2025）对"),
    "bg11": ("Metzler和Garcia指出", "Metzler和Garcia（2024）指出"),
    "bg13": ("Huszár等基于", "Huszár等（2022）基于"),
    "bg14": ("Hosseinmardi等利用", "Hosseinmardi等（2024）利用"),
}
PARENTHETICAL = {
    "bg12": "（李红涛等，2024）",
    "tf3": "（Noelle-Neumann，1974；Matthes等，2018）",
    "tf4": "（Wu与Huberman，2007；West等，2021）",
}


def normalize(text: str) -> str:
    """解除Markdown手动硬换行，保留英文词间空格及行内数学。"""
    text = text.strip()
    text = re.sub(r"(?<=[\u3400-\u9fff，。；：、！？）])\s*\n\s*(?=[\u3400-\u9fff（])", "", text)
    return re.sub(r"\s+", " ", text).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def captions_from(text: str) -> dict[int, dict[str, str]]:
    captions = {}
    for number in range(1, 6):
        match = re.search(
            rf"^## 图{number}\n\n\*\*([^\n]+)\*\*\n\n(.*?)\n\n\*\*Figure {number}\.",
            text, re.M | re.S,
        )
        if match is None:
            raise ValueError(f"正式中文图注缺失：图{number}")
        captions[number] = {"title": match[1], "caption": normalize(match[2])}
    return captions


def table_from(text: str) -> dict:
    match = re.search(
        r"\*\*表1　([^\n]+)\*\*\n\n(\|.*?)(?=\n\n注：)", text, re.S,
    )
    if match is None:
        raise ValueError("第四章（一）定稿中缺少表1")
    lines = match[2].strip().splitlines()
    split = lambda line: [part.strip() for part in line.strip().strip("|").split("|")]
    headers = split(lines[0])
    rows = [split(line) for line in lines[2:]]
    note_match = re.search(r"\n\n注：(.*?)(?=\n\n)", text[match.end():], re.S)
    if note_match is None:
        raise ValueError("表1缺少已确认表注")
    note = normalize(note_match[1]).split("正式主稿仅保留表位与表题")[0].strip()
    if len(headers) != 3 or len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise ValueError("表1结构与已采用三制度表不符")
    return {"number": 1, "title": match[1], "headers": headers, "rows": rows, "note": note,
            "accepted_source_text": match.group(0) + "\n\n注：" + note}


def article_markdown(article: dict) -> str:
    parts = ["# " + article["title"]]
    for block in article["blocks"]:
        kind, text = block["kind"], block["text"]
        if kind == "abstract":
            parts.append("**摘要：**" + text)
        elif kind == "keywords":
            parts.append("**关键词：**" + text)
        elif kind in {"heading1", "heading2"}:
            parts.append(("## " if kind == "heading1" else "### ") + text)
        elif kind == "research_question":
            parts.append(f"{block['number']}. {text}")
        elif kind == "equation":
            parts.append("\\[\n" + text + "\n\\]")
        elif kind == "figure":
            parts.extend([
                f"![图{block['number']}　{block['title']}]({block['path']})",
                f"**图{block['number']}　{block['title']}**",
                "注：" + block["caption"],
            ])
        elif kind == "table":
            table_lines = [f"**表{block['number']}　{block['title']}**", "",
                           "| " + " | ".join(block["headers"]) + " |",
                           "| " + " | ".join(["---"] * len(block["headers"])) + " |"]
            table_lines += ["| " + " | ".join(row) + " |" for row in block["rows"]]
            parts.extend(["\n".join(table_lines), "注：" + block["note"]])
        else:
            parts.append(text)
    return "\n\n".join(parts) + "\n"


def assemble(root: Path) -> dict:
    source = root / "paper/manuscript/manuscript.accepted.md"
    caption_path = root / "paper/figures/CAPTIONS.md"
    accepted_path = root / "runs/2026-10-15-01-ica2027-cat-writing/section_4_1.accepted.md"
    structure = root / "runs/2026-10-15-01-ica2027-cat-writing/ARTICLE_STRUCTURE.md"
    original = source.read_text(encoding="utf-8")
    original_sha = sha256(source)
    captions = captions_from(caption_path.read_text(encoding="utf-8"))
    table = table_from(accepted_path.read_text(encoding="utf-8"))
    notes, changes, blocks, reference_ids = [], [], [], []

    def change(action: str, reason: str, before: str, after: str = "", block_id: str | None = None) -> None:
        changes.append({"id": f"change_{len(changes) + 1:03d}", "action": action,
                        "reason": reason, "source_text": before, "replacement_text": after,
                        "block_id": block_id})

    def note(kind: str, raw: str, reason: str) -> None:
        notes.append({"id": f"note_{len(notes) + 1:03d}", "kind": kind,
                      "source_text": raw, "text": normalize(re.sub(r"(?m)^> ?", "", raw)),
                      "reason": reason})

    # 脚注定义不属于正文，先保存使用前的定义供下游书目映射复核。
    references_at = original.index("**参考文献**")
    body, reference_text = original[:references_at], original[references_at:]
    original_definitions = {
        m[1]: normalize(re.sub(r"<!--.*?-->", "", m[2], flags=re.S))
        for m in re.finditer(r"^\[\^([^\]]+)\]: (.*?)(?=^\[\^|\Z)", reference_text, re.M | re.S)
    }
    for comment in re.findall(r"<!--.*?-->", original, re.S):
        note("html_comment", comment, "内部来源说明移出排版正文")
        change("move_html_comment", "内部来源注释保留为评论依据，不进入清洁正文", comment)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)

    old_start = body.index("**（三）观测指标与模型评价**")
    old_stop = body.index("**三、数字形象的时序演化与平台差异**", old_start)
    old_sections = body[old_start:old_stop].rstrip()
    note("superseded_sections", old_sections, "旧二（三）（四）保留历史身份；现行方法由二（二）、第四章（一）及图注承接")
    change("omit_superseded_sections", "旧测量和旧实验结果不并入当前Word合稿", old_sections)
    body = body[:old_start] + body[old_stop:]
    appendix_start = body.index("**附录**")
    appendix = body[appendix_start:].strip()
    note("appendix_placeholder", appendix, "仅含本机路径及排版残留，不是当前timestamp补充材料")
    change("omit_internal_appendix_placeholder", "不将本机附录提示和反斜杠残留作为正式文章内容", appendix)
    body = body[:appendix_start]

    figure_sources = {}
    figure_pattern = re.compile(
        r"^> 【图([1-5])图位预留[^\n]*\n\n\*\*图\1[^\n]*\*\*\n\n(?:拟定图注：|注：)[^\n]+",
        re.M,
    )

    def replace_figure(match: re.Match) -> str:
        number = int(match[1])
        if number in figure_sources:
            raise ValueError(f"重复图位：图{number}")
        figure_sources[number] = match.group(0)
        return f"@@FIGURE_{number}@@"

    body = figure_pattern.sub(replace_figure, body)
    if sorted(figure_sources) != [1, 2, 3, 4, 5]:
        raise ValueError("主稿未完整识别五个已确认图位")
    table_match = re.search(r"^> 【表1表位预留[^\n]*\n\n\*\*表1[^\n]*\*\*", body, re.M)
    if table_match is None:
        raise ValueError("主稿未识别表1图位")
    table_source = table_match.group(0)
    body = body[:table_match.start()] + "@@TABLE_1@@" + body[table_match.end():]

    def citations(text: str) -> str:
        ids = re.findall(r"\[\^([^\]]+)\]", text)
        for ident in ids:
            if ident not in original_definitions:
                raise ValueError(f"正文引用缺少原书目定义：{ident}")
            if ident not in reference_ids:
                reference_ids.append(ident)
            if ident in NARRATIVE_YEARS:
                before, after = NARRATIVE_YEARS[ident]
                text = text.replace(before, after, 1)
            marker = f"[^{ident}]"
            text = text.replace(marker, PARENTHETICAL.get(ident, ""))
        return text

    title = ""
    for raw in re.split(r"\n\s*\n", body.strip()):
        raw = raw.strip()
        if not raw:
            continue
        if raw.startswith(">"):
            note("version_note", raw, "保留于合稿源内部注释，不进入清洁正文")
            change("move_version_note", "内部版本与状态说明移作Word内部评论依据", raw)
            continue
        if not title:
            if not raw.startswith("**悼念退潮之后"):
                raise ValueError("首段不是已确认文章题名")
            title = raw.removeprefix("**").removesuffix("**")
            continue
        block_id = f"b{len(blocks) + 1:03d}"
        base = {"id": block_id, "source_text": raw}
        if re.fullmatch(r"@@FIGURE_[1-5]@@", raw):
            number = int(re.search(r"\d", raw)[0])
            base.update({"kind": "figure", "text": captions[number]["caption"], "number": number,
                         "path": "../figures/" + FIGURE_FILES[number], **captions[number],
                         "source_text": figure_sources[number], "caption_source": str(caption_path.relative_to(root))})
            change("replace_figure_placeholder", "插入本轮五图并采用CAPTIONS中文正式图注", figure_sources[number],
                   f"图{number}　{base['title']}\n{base['caption']}", block_id)
        elif raw == "@@TABLE_1@@":
            base.update({"kind": "table", "text": table["title"], **table,
                         "source_text": table_source, "table_source": str(accepted_path.relative_to(root))})
            change("fill_accepted_table", "落实第四章（一）已经确认的三制度表，不新造参数", table_source,
                   table["accepted_source_text"], block_id)
        elif raw.startswith("**摘要：**"):
            base.update({"kind": "abstract", "text": ABSTRACT})
            change("replace_legacy_abstract", "摘要与当前两平台分析、九主实验和九消融及最新结论对齐", raw, ABSTRACT, block_id)
        elif raw.startswith("**关键词：**"):
            base.update({"kind": "keywords", "text": "；".join(KEYWORDS), "items": KEYWORDS})
            change("replace_legacy_keywords", "关键词反映当前论文研究对象与解释框架", raw, base["text"], block_id)
        elif raw.startswith("\\[") and raw.endswith("\\]"):
            base.update({"kind": "equation", "text": "U_{it}=B_i+R_{it}(D_{it}-B_i)."})
        elif re.fullmatch(r"\*\*[一二三四五]、[^\n]+\*\*", raw):
            base.update({"kind": "heading1", "text": raw[2:-2]})
        elif re.fullmatch(r"\*\*（[一二三四五]）[^\n]+\*\*", raw):
            base.update({"kind": "heading2", "text": raw[2:-2]})
        else:
            text = normalize(raw)
            question = re.match(r"^([1-3])\.\s+(.+)$", text)
            if question:
                base.update({"kind": "research_question", "number": int(question[1]), "text": question[2]})
            else:
                base.update({"kind": "paragraph", "text": text})
            for before, after, reason in [
                ("抖音、微博、小红书等中国主流社交平台共5.2万条帖文", "抖音和小红书共49,930条帖文",
                 "统一绪论的现实样本范围；三来源仿真冻结输入按第四章原文保留"),
                ("悼亡场景中的幽默表达可以同时包含哀悼、戏仿、批评和政治评价",
                 "围绕死亡的迷因能够承载批评、抗议与群体联结",
                 "第一章该处文献概述与已采用第五章确认表述统一"),
            ]:
                if before in base["text"]:
                    modified = base["text"].replace(before, after, 1)
                    change("minimal_content_alignment", reason, base["text"], modified, block_id)
                    base["text"] = modified
            before_citation = base["text"]
            base["source_reference_ids"] = re.findall(r"\[\^([^\]]+)\]", before_citation)
            base["text"] = citations(before_citation)
            if base["text"] != before_citation:
                change("format_author_year_citations", "保留已有作者年份，补齐缺失叙述年份并移除Markdown脚注标记",
                       before_citation, base["text"], block_id)
        blocks.append(base)

    if len([c for c in changes if c["action"] == "minimal_content_alignment"]) != 2:
        raise ValueError("本轮两处最小内容对齐没有各执行一次")
    if len(reference_ids) != 22:
        raise ValueError(f"当前正文引用应为22个既有脚注标识，实际为{len(reference_ids)}")
    counts = Counter(block["kind"] for block in blocks)
    if (counts["figure"], counts["table"], counts["equation"], counts["research_question"]) != (5, 1, 1, 3):
        raise ValueError(f"合稿块数与确认范围不符：{counts}")
    for block in blocks:
        if re.search(r"\[\^|@@FIGURE|@@TABLE|^> |<!--", block["text"]):
            raise ValueError(f"正文残留内部标记：{block['id']}")
    if sha256(source) != original_sha:
        raise ValueError("装配期间原主稿发生变化，不能交付旧版本合稿")
    inputs = [source, caption_path, accepted_path, structure]
    inputs += [root / "paper/figures" / FIGURE_FILES[n] for n in range(1, 6)]
    return {
        "title": title, "blocks": blocks, "reference_ids": reference_ids,
        "internal_notes": notes, "changes": changes,
        "inputs": [{"path": str(path.relative_to(root)), "sha256": sha256(path)} for path in inputs],
        "reference_sources": {ident: original_definitions[ident] for ident in reference_ids},
        "reference_status": "Body assembled; root agent appends the separately prepared APA reference blocks.",
        "source_manuscript_sha256": original_sha,
        "assembly_schema_version": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.project_root.resolve()
    out = root / "paper/word"
    out.mkdir(parents=True, exist_ok=True)
    article = assemble(root)
    references = json.loads((out / "references.json").read_text(encoding="utf-8"))
    if len(references) != 22:
        raise ValueError("合稿应配有22项去重书目")
    article["bibliography_ids"] = [item["id"] for item in references]
    article["reference_status"] = "22 distinct APA references are provided in references.json and included in the Word and Markdown outputs."
    (out / "article.json").write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = article_markdown(article) + "\n\n## 参考文献\n\n"
    markdown += "\n\n".join(item["text"] for item in sorted(references, key=lambda item: item["sortkey"])) + "\n"
    (out / "manuscript.full.zh.md").write_text(markdown, encoding="utf-8")
    change_report = {key: article[key] for key in ("inputs", "source_manuscript_sha256", "internal_notes", "changes")}
    change_report["block_counts"] = dict(Counter(block["kind"] for block in article["blocks"]))
    change_report["reference_ids"] = article["reference_ids"]
    change_report["reference_status"] = article["reference_status"]
    (out / "assembly_changes.json").write_text(json.dumps(change_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"blocks": change_report["block_counts"], "reference_ids": article["reference_ids"],
                      "internal_notes": len(article["internal_notes"]), "changes": len(article["changes"]),
                      "source_unchanged": sha256(root / "paper/manuscript/manuscript.accepted.md") == article["source_manuscript_sha256"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
