#!/usr/bin/env python3
"""检查交付Word的正文、字体设置、图表、评论及修订映射；检查PDF页面。"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
from lxml import etree

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NS = {'w': W}


def text(element):
    return ''.join(n.text or '' for n in element.iter()
                   if n.tag in ('{' + W + '}t', '{' + M + '}t')
                   and not any(a.tag == '{' + W + '}del' for a in n.iterancestors()))


def main():
    article = json.loads((OUT / 'article.review.json').read_text())
    files = {}
    checks = {}
    for review in [True, False]:
        stem = '悼念退潮之后_完整中文稿' + ('_保留批注修订' if review else '')
        path = OUT / (stem + '.docx')
        with ZipFile(path) as z:
            document = etree.fromstring(z.read('word/document.xml'))
            styles = etree.fromstring(z.read('word/styles.xml'))
            comments = etree.fromstring(z.read('word/comments.xml')) if 'word/comments.xml' in z.namelist() else None
            fonts = styles.find('.//w:docDefaults/w:rPrDefault/w:rPr/w:rFonts', NS)
            size = styles.find('.//w:docDefaults/w:rPrDefault/w:rPr/w:sz', NS)
            assert fonts.get('{' + W + '}eastAsia') == '宋体'
            assert fonts.get('{' + W + '}ascii') == fonts.get('{' + W + '}hAnsi') == 'Times New Roman'
            assert size.get('{' + W + '}val') == '24'
            assert len(document.findall('.//w:drawing', NS)) == 5
            assert len(document.findall('.//w:tbl', NS)) == 1
            assert len(document.findall('.//w:tbl/w:tr', NS)) == 4
            media_hashes = {hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist() if name.startswith('word/media/') and name.endswith('.png')}
            expected_images = {hashlib.sha256((OUT / b['path']).read_bytes()).hexdigest() for b in article['blocks'] if b['kind'] == 'figure'}
            assert media_hashes == expected_images
            body = text(document)
            files[review] = body
            assert not re.search(r'未完成人工复编码|5\.2万|三大社交平台5万|图位预留|表位预留|\[\^', body)
            source_count = 0
            if review:
                comment_nodes = {int(c.get('{' + W + '}id')): c for c in comments.findall('w:comment', NS)}
                for comment in article['comments']:
                    node = comment_nodes[comment['id']]
                    actual = '\n'.join(text(p) for p in node.findall('w:p', NS))
                    assert actual == comment['text'], (comment['id'], actual, comment['text'])
                    assert node.get('{' + W + '}author') == comment['author']
                    assert datetime.fromisoformat(node.get('{' + W + '}date').replace('Z', '+00:00')) == datetime.fromisoformat(comment['date'].replace('Z', '+00:00'))
                    source_count += comment.get('source_comment_id') is not None
                assert source_count == 15
                starts = [n.get('{' + W + '}id') for n in document.findall('.//w:commentRangeStart', NS)]
                ends = [n.get('{' + W + '}id') for n in document.findall('.//w:commentRangeEnd', NS)]
                assert Counter(starts) == Counter(ends) == Counter(str(c['id']) for c in article['comments'])
                source_preservation = json.loads((OUT / 'qa/review_preservation.json').read_text())
                mapping = json.loads((OUT / 'qa/word_revision_mapping.json').read_text())
                expected = {(r['source'], r['source_revision_id'], r['type']) for r in source_preservation['source_revision_groups']}
                restored = {(r.get('source'), r.get('source_revision_id'), r['type']) for r in mapping if r.get('source')}
                assert expected == restored and len(expected) == 42
                assert len(document.findall('.//w:pPrChange', NS)) == 1
            else:
                assert not document.findall('.//w:ins', NS) and not document.findall('.//w:del', NS)
                assert comments is None or len(comments) == 0
            checks[stem] = {'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                            'figures': 5, 'tables': 1, 'source_comments': source_count,
                            'default_font': {'chinese': '宋体', 'latin': 'Times New Roman', 'pt': 12}}
    assert files[True] == files[False], '接受修订后两份Word正文应完全一致'
    source = ROOT / 'paper/manuscript/manuscript.accepted.md'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == article['source_manuscript_sha256']
    for source_review in json.loads((OUT / 'source_reviews.json').read_text())['sources']:
        assert hashlib.sha256((ROOT / source_review['source_path']).read_bytes()).hexdigest() == source_review['source_sha256']
    sys.path.insert(0, '/Users/easylife/.cache/uv/archive-v0/gazd_6nNK5VOozdKrmrr4')
    import fitz
    pdf = fitz.open(OUT / '悼念退潮之后_完整中文稿.pdf')
    page_info, image_pages, font_counts = [], [], Counter()
    for i, page in enumerate(pdf):
        content = page.get_text('dict')
        image_count = len([b for b in content['blocks'] if b['type'] == 1])
        if image_count:
            image_pages.append(i + 1)
        for block in content['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    font_counts[(span['font'], round(span['size'], 1))] += len(span['text'])
                    x0, y0, x1, y1 = span['bbox']
                    assert x0 >= 0 and y0 >= 0 and x1 <= page.rect.width + .1 and y1 <= page.rect.height + .1
        page.get_pixmap(dpi=100).save(OUT / 'qa' / f'page_{i+1:02}.png')
        page_info.append({'page': i + 1, 'characters': len(page.get_text()), 'images': image_count})
    assert sum(p['images'] for p in page_info) == 5
    assert any('Songti' in k[0] and k[1] == 12 for k in font_counts)
    assert any('TimesNewRoman' in k[0] and k[1] == 12 for k in font_counts)
    report = {'docx': checks, 'accepted_body_identical': True, 'original_source_files_unchanged': True,
              'source_text_revision_groups_restored': 42, 'source_paragraph_format_revisions_restored': 1,
              'pdf_pages': len(pdf), 'figure_pages': image_pages, 'pdf_page_checks': page_info,
              'pdf_fonts': [{'name': k[0], 'pt': k[1], 'characters': v} for k, v in font_counts.most_common()],
              'reference_count': len(json.loads((OUT / 'references.json').read_text())), 'status': 'PASS'}
    (OUT / 'qa/word_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['accepted_body_identical', 'pdf_pages', 'figure_pages', 'reference_count', 'status']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
