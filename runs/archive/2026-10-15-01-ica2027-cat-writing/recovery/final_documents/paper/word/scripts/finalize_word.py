#!/usr/bin/env python3
"""完成新生成Word的原格式修订及跨平台字体回退；不写入作者原件。"""
from __future__ import annotations
import copy
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

OUT = Path(__file__).resolve().parents[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}


def tag(name):
    return '{' + W + '}' + name


def accepted_text(element):
    result = []
    for node in element.iter():
        if node.tag in (tag('t'), '{http://schemas.openxmlformats.org/officeDocument/2006/math}t'):
            if not any(p.tag == tag('del') for p in node.iterancestors()):
                result.append(node.text or '')
    return ''.join(result)


def serialize(element):
    return etree.tostring(element, encoding='UTF-8', xml_declaration=True, standalone=True)


def main():
    article = json.loads((OUT / 'article.review.json').read_text())
    for review in [True, False]:
        name = '悼念退潮之后_完整中文稿' + ('_保留批注修订' if review else '') + '.docx'
        target = OUT / name
        with ZipFile(target) as source:
            files = {name: source.read(name) for name in source.namelist()}
        settings = etree.fromstring(files['word/settings.xml'])
        for node in settings.findall(tag('revisionView')):
            settings.remove(node)
        view = etree.SubElement(settings, tag('revisionView'))
        for key, value in {'markup': '0', 'comments': '1' if review else '0', 'insDel': '0', 'formatting': '0'}.items():
            view.set(tag(key), value)
        tracking = settings.find(tag('trackRevisions'))
        if review and tracking is None:
            etree.SubElement(settings, tag('trackRevisions'))
        elif not review and tracking is not None:
            settings.remove(tracking)
        # 仅关闭拼写波浪线的打印噪音，文字和审阅信息均保留。
        for key in ('hideSpellingErrors', 'hideGrammaticalErrors'):
            if settings.find(tag(key)) is None:
                etree.SubElement(settings, tag(key))
        order = ['displayBackgroundShape', 'hideSpellingErrors', 'hideGrammaticalErrors',
                 'revisionView', 'trackRevisions', 'evenAndOddHeaders', 'compat']
        for node in sorted(list(settings), key=lambda x: order.index(etree.QName(x).localname)
                           if etree.QName(x).localname in order else len(order)):
            settings.remove(node)
            settings.append(node)
        files['word/settings.xml'] = serialize(settings)
        fonts = etree.fromstring(files['word/fontTable.xml'])
        song = next((font for font in fonts if font.get(tag('name')) == '宋体'), None)
        if song is None:
            song = etree.SubElement(fonts, tag('font'))
            song.set(tag('name'), '宋体')
        alt = song.find(tag('altName'))
        if alt is None:
            alt = etree.SubElement(song, tag('altName'))
        alt.set(tag('val'), '宋体-简')
        family = song.find(tag('family'))
        if family is None:
            family = etree.SubElement(song, tag('family'))
        family.set(tag('val'), 'roman')
        files['word/fontTable.xml'] = serialize(fonts)
        count = 0
        if review:
            document = etree.fromstring(files['word/document.xml'])
            # 原稿插入的“幽默”在本次有依据的概述统一中删除。保留为原插入内的新删除，
            # 从而既能接受当前稿，也能在Word中逐层回看原作者的这条修订。
            source_reviews = json.loads((OUT / 'source_reviews.json').read_text())['sources']
            historical = next(r for r in source_reviews[0]['revision_elements']
                              if r['xml_type'] == 'ins' and r['id'] == '5')
            candidates = [n for n in document.findall('.//w:del', NS)
                          if '幽默' in ''.join(n.itertext())]
            if len(candidates) != 1:
                raise ValueError('被后续删除的原插入无法唯一定位')
            deletion = candidates[0]
            deleted_text = deletion.find('.//w:delText', NS)
            before, after = deleted_text.text.split('幽默', 1)
            parent, index = deletion.getparent(), deletion.getparent().index(deletion)
            replacement = []
            if before:
                left = copy.deepcopy(deletion)
                left.set(tag('id'), '7000')
                left.find('.//w:delText', NS).text = before
                replacement.append(left)
            original_insert = etree.Element(tag('ins'))
            for attr, value in {'id': '7001', 'author': historical['author'], 'date': historical['date']}.items():
                original_insert.set(tag(attr), value)
            inner_delete = copy.deepcopy(deletion)
            inner_delete.set(tag('id'), '7002')
            inner_delete.find('.//w:delText', NS).text = '幽默'
            original_insert.append(inner_delete)
            replacement.append(original_insert)
            if after:
                right = copy.deepcopy(deletion)
                right.set(tag('id'), '7003')
                right.find('.//w:delText', NS).text = after
                replacement.append(right)
            parent.remove(deletion)
            for new_index, node in enumerate(replacement, index):
                parent.insert(new_index, node)
            mapping_path = OUT / 'qa/word_revision_mapping.json'
            mapping = json.loads(mapping_path.read_text())
            mapping.append({'word_id': 7001, 'group_id': 'source_insert_removed_by_current_edit',
                            'type': 'insert', 'author': historical['author'], 'date': historical['date'],
                            'source': source_reviews[0]['source_path'], 'source_revision_id': historical['id'],
                            'nested_current_deletion_id': 7002})
            mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n')
            paragraphs = document.findall('.//w:body/w:p', NS)
            for index, paragraph in enumerate(paragraphs):
                style = paragraph.find('w:pPr/w:pStyle', NS)
                if style is not None and style.get(tag('val')) == 'LegacyDeletion':
                    properties = paragraph.find(tag('pPr'))
                    mark = etree.SubElement(properties, tag('rPr'))
                    deleted_mark = etree.SubElement(mark, tag('del'))
                    deleted_mark.set(tag('id'), str(8000 + index))
                    deleted_mark.set(tag('author'), 'Claude')
                    deleted_mark.set(tag('date'), '2026-10-18T00:00:00Z')
            for block in article['blocks']:
                if not block.get('format_revisions'):
                    continue
                matching = [p for p in paragraphs if accepted_text(p) == block['text']]
                if len(matching) != 1:
                    raise ValueError('原段落格式修订没有唯一对应段：' + block['id'])
                para = matching[0]
                props = para.find(tag('pPr'))
                for original in block['format_revisions']:
                    change = etree.fromstring(original['xml'].encode())
                    change.set(tag('id'), str(6000 + count))
                    props.append(copy.deepcopy(change))
                    count += 1
            files['word/document.xml'] = serialize(document)
        temp = target.with_suffix('.building.docx')
        with ZipFile(temp, 'w', ZIP_DEFLATED) as dest:
            for key, value in files.items():
                dest.writestr(key, value)
        temp.replace(target)
        print(name, 'original paragraph format revisions:', count)


if __name__ == '__main__':
    main()
