#!/usr/bin/env python3
"""基于已验证正文生成来源质量矩阵、方法分布和资助/利益冲突记录。"""

from __future__ import annotations

from collections import Counter

from build_annotated_bibliography import ANNOTATIONS, ROOT, load_rows


OUTPUT = ROOT / "07_来源质量矩阵与方法分布_v0.1.md"


METHOD = {
    "A01": "概念/理论", "A03": "定性/案例", "A06": "定性/案例", "A08": "定性/案例",
    "A09": "平台审计/计算观察", "A10": "定性/案例", "A11": "概念/理论", "A12": "平台审计/计算观察",
    "B01": "平台审计/计算观察", "B02": "平台审计/计算观察", "B03": "平台审计/计算观察",
    "B04": "定性/案例", "B05": "平台审计/计算观察", "B07": "概念/理论", "B08": "概念/理论",
    "B09": "定性/案例", "B10": "定性/案例", "B12": "平台审计/计算观察", "B13": "平台审计/计算观察",
    "B14": "平台审计/计算观察", "B17": "定性/案例", "B18": "平台审计/计算观察", "B19": "随机/在线实验",
    "B20": "平台审计/计算观察", "C03": "随机/在线实验", "C04": "概念/理论", "C05": "定性/案例",
    "D01": "随机/在线实验", "D03": "随机/在线实验", "D04": "随机/在线实验", "D05": "随机/在线实验", "D06": "随机/在线实验",
}


PLATFORM = {
    "A01": "跨平台/数字来生", "A03": "Facebook", "A06": "X/Twitter", "A08": "网络致敬页", "A09": "Twitter",
    "A10": "社交媒体回忆", "A11": "平台记忆（理论）", "A12": "Facebook/Twitter", "B01": "新闻推荐模拟",
    "B02": "YouTube", "B03": "YouTube", "B04": "YouTube", "B05": "Twitter", "B07": "跨平台", "B08": "跨平台",
    "B09": "算法审计生态", "B10": "多平台", "B12": "TikTok", "B13": "TikTok", "B14": "TikTok", "B17": "TikTok",
    "B18": "抖音/TikTok/B站", "B19": "Twitter", "B20": "YouTube", "C03": "模拟社交媒体", "C04": "跨平台",
    "C05": "Tumblr", "D01": "微信", "D03": "模拟Facebook", "D04": "实验室", "D05": "模拟社交媒体", "D06": "实验室",
}


# 仅依当前保存正文中能定位的声明填写；“未定位”不等于“无”。
DISCLOSURE = {
    "A01": ("未定位", "未定位"), "A03": ("未定位", "未定位"), "A06": ("未定位", "未定位"),
    "A08": ("未定位", "未定位"), "A09": ("SSHRC", "声明无"), "A10": ("声明无资助", "未定位"),
    "A11": ("声明无资助", "声明无"), "A12": ("以色列科技部/科学基金", "声明无"),
    "B01": ("ERC/阿姆斯特丹大学", "声明无"), "B02": ("QUT/ARC", "声明无"),
    "B03": ("美国国防/科学资助+澳防务项目", "声明无；议题相关中度标记"),
    "B04": ("未定位", "未定位"), "B05": ("CFM/法国区域机构", "声明无"),
    "B07": ("ERC/欧委会/公益基金", "声明无"), "B08": ("维也纳科技基金", "声明无"),
    "B09": ("未定位", "未定位"), "B10": ("NSF–Amazon/Amazon/Cisco", "未定位；行业资助中度标记"),
    "B12": ("大学资源；无正式资助声明", "未定位"), "B13": ("未定位", "未定位"),
    "B14": ("未定位", "未定位"), "B17": ("Tencent奖学金+ARC", "声明无；平台行业高关联标记"),
    "B18": ("未定位", "声明无"), "B19": ("Twitter内部研究", "Twitter雇员+付费顾问；高关联标记"),
    "B20": ("巴西公共资助+Google研究奖", "未定位；行业资助中度标记"),
    "C03": ("阿姆斯特丹大学", "声明无"), "C04": ("未定位", "未定位"), "C05": ("声明无资助", "声明无"),
    "D01": ("中国国家社科基金重大项目", "未定位"), "D03": ("SSHRC/NIMH/Templeton/DARPA", "未定位"),
    "D04": ("大学经费", "声明无"), "D05": ("德国州政府/大学项目", "声明无"),
    "D06": ("Wellcome Trust", "未定位"),
}


def main() -> None:
    plan, rows = load_rows()
    ids = [row["ID"] for row in rows]
    for name, mapping in [("METHOD", METHOD), ("PLATFORM", PLATFORM), ("DISCLOSURE", DISCLOSURE)]:
        missing = sorted(set(ids) - set(mapping))
        if missing:
            raise SystemExit(f"{name}缺少条目: {missing}")

    method_counts = Counter(METHOD[id_] for id_ in ids)
    grade_counts = Counter(ANNOTATIONS[id_][6] for id_ in ids)
    level_counts = Counter(ANNOTATIONS[id_][5] for id_ in ids)
    lines = [
        "# 来源质量矩阵与方法分布（v0.1）", "",
        f"> 对{len(ids)}篇已取得并验证正文的文献进行评级。Level是研究设计层级，A/B是针对本研究问题的学科适配综合评级，两者不可混同。", "",
        "## 总体判断", "",
        f"- 综合评级：A = {grade_counts['A']}，B = {grade_counts['B']}，C/D/F = {sum(grade_counts[x] for x in ['C', 'D', 'F'])}。",
        "- 未发现明显掠夺性期刊或伪造出版源线索；这是风险筛查，不等于为单篇结论背书。",
        "- 所有文献都已经Crossref与OpenAlex匹配；B02未被Semantic Scholar匹配，但其DOI、Crossref、OpenAlex与已下载原文一致，不视为虚构。",
        "- 资助/利益冲突栏仅记录当前保存正文中能定位的声明；“未定位”不得解读为“不存在”。", "",
        "## 方法分布", "",
    ]
    for method, count in method_counts.most_common():
        lines.append(f"- {method}：{count}/{len(ids)}（{count / len(ids):.0%}）。")
    lines.extend([
        "", "方法维度最高集中度低于70%，未触发分布偏斜预警。但平台地域信息并未对所有文献一致报告，因此不对地域分布做强行推断。", "",
        "## 来源质量矩阵", "",
        "| ID | 简称 | 平台/场景 | 方法 | Level | 综合评级 | 出版源风险 | 资助 | COI/关联风险 |",
        "|---|---|---|---|---:|---:|---|---|---|",
    ])
    for row in rows:
        id_ = row["ID"]
        funding, coi = DISCLOSURE[id_]
        level, grade = ANNOTATIONS[id_][5], ANNOTATIONS[id_][6]
        title = plan[id_]["中文译名"]
        short = title if len(title) <= 22 else title[:21] + "…"
        lines.append(f"| {id_} | {short} | {PLATFORM[id_]} | {METHOD[id_]} | {level} | {grade} | 低，未见异常 | {funding} | {coi} |")

    lines.extend([
        "", "## 与结论最相关的利益关联标记", "",
        "- **B19**：主要作者受雇于Twitter，另一作者是Twitter付费顾问；同时，它拥有本文献库中最强的平台内随机对照证据。使用时应同时保留“识别强”与“独立性有限”两个判断。",
        "- **B17**：收到Tencent资助的研究奖学金，并声明无竞争利益。由于它直接研究TikTok网红与可见性劳动，平台行业资助需高关联标记，但不构成自动排除理由。",
        "- **B10/B20**：分别获得Amazon/Cisco与Google研究奖类资助；原文中未定位到正式COI声明，因此按中度行业关联保留。",
        "- **B03**：获得多项美国国防与澳大利亚防务资助，而研究题材涉及地缘政治叙事；作者声明无利益冲突，但题材—资助方的关联应在解释时保留。", "",
        "## 证据等级计数", "",
    ])
    level_order = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}
    for level in sorted(level_counts, key=lambda x: level_order[x]):
        lines.append(f"- Level {level}：{level_counts[level]}篇。")
    lines.extend([
        "", "## 阶段限制", "",
        "- 当前评级仅覆盖32篇已取得正文的文献；另35条题录已验证但未取得可验证正文，不对其原文结论或COI作肯定声称。",
        "- 强因果证据主要来自Twitter政治内容排名、多模态错误信息、重复曝光与陌生人资料实验；它们均非“张雪峰去世后的抖音”直接实验。",
        "- 中文本土传播学证据与抖音平台内资料仍不足。", "",
        "## Material Passport", "", "- Origin Skill: academic-research-suite / deep-research / source_verification_agent",
        "- Origin Mode: lit-review", "- Origin Date: 2026-08-17", "- Verification Status: 32_ORIGINALS_REVIEWED_FOR_QUALITY",
        "- Version Label: source_quality_matrix_v0.1", "- Upstream Dependencies: annotated_bibliography_v0.1, download_manifest_v0.2", "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"写入 {OUTPUT}，条目 {len(ids)}")


if __name__ == "__main__":
    main()
