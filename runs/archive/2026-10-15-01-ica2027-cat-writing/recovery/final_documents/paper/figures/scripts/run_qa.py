#!/usr/bin/env python3
"""离线核对已导出PDF：字体、文本碰撞、面板对齐及可编辑SVG。

依赖PyMuPDF。若项目环境没有安装，可用 --pymupdf-path 指向既有缓存包目录；
该参数只影响本进程与审计子进程，不修改环境或安装依赖。
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
QA = OUT / "qa"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pymupdf-path", type=Path)
    args = parser.parse_args()
    environment = os.environ.copy()
    if args.pymupdf_path:
        sys.path.insert(0, str(args.pymupdf_path))
        environment["PYTHONPATH"] = str(args.pymupdf_path) + os.pathsep + environment.get("PYTHONPATH", "")
    try:
        fitz = importlib.import_module("fitz")
    except ImportError as exc:
        raise SystemExit("PDF几何检查需要PyMuPDF；可用 --pymupdf-path 指向现有包目录。") from exc
    records = []
    source = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_figure.py"), str(SCRIPTS / "build_figures.py"), "--json"],
        capture_output=True, text=True, env=environment, check=False)
    source_report = json.loads(source.stdout)
    (QA / "source_preflight.json").write_text(json.dumps(source_report, indent=2) + "\n", encoding="utf-8")
    if source.returncode:
        raise SystemExit("绘图源码预检查存在FAIL，见qa/source_preflight.json")
    for pdf in sorted(OUT.glob("figure_*.pdf")):
        stem = pdf.stem
        glyph_run = subprocess.run(
            [sys.executable, str(SCRIPTS / "audit_pdf_text.py"), str(pdf), "--min-pt", "5", "--json"],
            capture_output=True, text=True, env=environment, check=False)
        glyph = json.loads(glyph_run.stdout)
        (QA / f"{stem}.fonts.json").write_text(json.dumps(glyph, indent=2) + "\n", encoding="utf-8")
        collision_run = subprocess.run(
            [sys.executable, str(SCRIPTS / "audit_figure_collisions.py"), str(pdf),
             "--json-out", str(QA / f"{stem}.collisions.json"),
             "--overlay-pdf", str(QA / f"{stem}.collisions.pdf")],
            capture_output=True, text=True, env=environment, check=False)
        collision = json.loads((QA / f"{stem}.collisions.json").read_text())
        alignment = json.loads((QA / f"{stem}.alignment.json").read_text())
        svg_root = ET.parse(OUT / f"{stem}.svg").getroot()
        text_count = len(svg_root.findall(".//{http://www.w3.org/2000/svg}text"))
        doc = fitz.open(pdf)
        width, height = doc[0].rect.width * 25.4 / 72, doc[0].rect.height * 25.4 / 72
        expected_width = 183 if stem.startswith("figure_05") else 180
        assert abs(width - expected_width) < .05
        assert doc[0].get_text().strip() and text_count > 0
        doc.close()
        records.append({"figure": stem, "font_exit_code": glyph_run.returncode,
                        "collision_exit_code": collision_run.returncode,
                        "collision_verdict": collision.get("verdict"),
                        "alignment_verdict": alignment.get("verdict"),
                        "svg_text_elements": text_count,
                        "physical_size_mm": [round(width, 3), round(height, 3)]})
        print(stem, "font", glyph_run.returncode, "collision", collision_run.returncode,
              "editable SVG text", text_count)
    summary = {"pymupdf_version": fitz.VersionBind, "figures": records,
               "pass": all(r["font_exit_code"] == r["collision_exit_code"] == 0 for r in records)}
    (QA / "export_checks.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if not summary["pass"]:
        raise SystemExit("仍有导出检查FAIL，须修复后重新渲染并检查。")


if __name__ == "__main__":
    main()
