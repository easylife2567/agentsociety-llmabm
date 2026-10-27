#!/usr/bin/env python3
"""以独立LibreOffice配置渲染清洁Word，不改全局字体设置或作者原件。"""
from __future__ import annotations
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

OUT = Path(__file__).resolve().parents[1]


def main():
    profile = Path(tempfile.mkdtemp(prefix='agentsociety-word-preview-'))
    (profile / 'user').mkdir()
    # 本机缺少Windows版SimSun。只在临时渲染副本中明确指定已安装的宋体-简，
    # 避免LibreOffice对“宋体”的字体替换不稳定；两份交付Word始终保留“宋体”。
    preview = profile / '悼念退潮之后_完整中文稿.docx'
    w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    with ZipFile(OUT / preview.name) as original, ZipFile(preview, 'w', ZIP_DEFLATED) as target:
        for name in original.namelist():
            data = original.read(name)
            if name.startswith('word/') and name.endswith('.xml'):
                element = etree.fromstring(data)
                for fonts in element.iter('{' + w + '}rFonts'):
                    if fonts.get('{' + w + '}eastAsia') == '宋体':
                        fonts.set('{' + w + '}eastAsia', '宋体-简')
                data = etree.tostring(element, xml_declaration=True, encoding='UTF-8', standalone=True)
            target.writestr(name, data)
    subprocess.run(['/Applications/LibreOffice.app/Contents/MacOS/soffice',
                    '-env:UserInstallation=' + profile.as_uri(), '--headless', '--convert-to',
                    'pdf', '--outdir', str(OUT), str(preview)], check=True)


if __name__ == '__main__':
    main()
