#!/usr/bin/env python3
"""把原作者Word的批注与文字修订映射到新合稿，原始文档只读。

匹配只忽略空白、引号字形及排版标记；正文的修改依据记录于assembly_changes.json。
"""
from __future__ import annotations
import copy
import difflib
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
NOW = '2026-10-18T00:00:00Z'


def normalized(text):
    text = re.sub(r'\[\^[^\]]+\]', '', text)
    text = text.replace('**', '').replace('\\(', '').replace('\\)', '')
    text = text.translate(str.maketrans({'“': '"', '”': '"', '‘': "'", '’': "'", '—': '-', '–': '-'}))
    return re.sub(r'\s+', '', text)


def clean_source(text):
    return re.sub(r'\[\^[^\]]+\]', '', text).replace('**', '').strip()


def offset_mapper(source, target):
    # 使用最长相等片段定位；引文新增和空白变化落在相邻边界，不重写原有删除文本。
    operations = difflib.SequenceMatcher(None, source, target, autojunk=False).get_opcodes()
    def convert(position):
        if position <= 0:
            return 0
        if position >= len(source):
            return len(target)
        for kind, a, b, c, d in operations:
            if a <= position <= b:
                if kind == 'equal':
                    return c + position - a
                return c + round((position - a) / max(b - a, 1) * (d - c))
        return len(target)
    return convert


def main():
    article = json.loads((OUT / 'article.json').read_text())
    sources = json.loads((OUT / 'source_reviews.json').read_text())['sources']
    article = copy.deepcopy(article)
    blocks = article['blocks']
    comments, matches, unmatched, revisions = [], [], [], []
    comment_id = 0
    revision_id = 1
    used = set()
    for source_index, source in enumerate(sources):
        mapping = {}
        for p in source['paragraphs']:
            original = p['accepted_text']
            if not original.strip():
                continue
            candidates = []
            for block_index, block in enumerate(blocks):
                if block.get('kind') not in ('paragraph', 'heading1', 'heading2', 'research_question'):
                    continue
                if (source_index, block_index) in used:
                    continue
                candidate = clean_source(block.get('source_text', block.get('text', '')))
                score = difflib.SequenceMatcher(None, normalized(original), normalized(candidate), autojunk=False).ratio()
                candidates.append((score, block_index))
            score, block_index = max(candidates, default=(0, -1))
            significant = any(t['type'] in ('insert', 'delete') for t in p['tokens']) or bool(p['comment_markers'])
            if score < .84:
                if significant:
                    unmatched.append({'source': source['source_path'], 'paragraph': p['paragraph_index'], 'score': score, 'text': original})
                continue
            used.add((source_index, block_index))
            target = blocks[block_index]
            mapper = offset_mapper(original, target['text'])
            mapping[p['paragraph_index']] = (block_index, mapper)
            matches.append({'source': source['source_path'], 'paragraph': p['paragraph_index'],
                            'block_id': target['id'], 'score': score, 'has_reviews': significant})
            insert_groups = {}
            for token in p['tokens']:
                if token['type'] not in ('insert', 'delete'):
                    continue
                metadata = {'id': revision_id, 'author': token.get('author') or '原稿修订',
                            'date': token.get('date') or NOW, 'source': source['source_path'],
                            'source_revision_id': token.get('original_id')}
                start = mapper(token['accepted_offset'])
                if token['type'] == 'insert':
                    key = (token.get('original_id'), metadata['author'], metadata['date'])
                    end = mapper(token['accepted_offset'] + len(token['text']))
                    if key in insert_groups and insert_groups[key]['end'] == start:
                        insert_groups[key]['end'] = end
                    else:
                        entry = {**metadata, 'start': start, 'end': end}
                        insert_groups[key] = entry
                        target.setdefault('revisions', []).append(entry)
                        revisions.append({**metadata, 'type': 'insert', 'block_id': target['id'], 'original_text': token['text']})
                        revision_id += 1
                else:
                    target.setdefault('deletions', []).append({**metadata, 'at': start, 'text': token['text']})
                    revisions.append({**metadata, 'type': 'delete', 'block_id': target['id'], 'original_text': token['text']})
                    revision_id += 1
            for change in p.get('paragraph_mark_revisions', []):
                target.setdefault('paragraph_mark_revisions', []).append(change)
            # 原段落属性修订另保留其XML，由最终打包步骤接回对应新段。
            for revision in source['revision_elements']:
                if revision['paragraph_index'] == p['paragraph_index'] and revision['xml_type'] == 'pPrChange':
                    target.setdefault('format_revisions', []).append(revision)
        for comment in source['comments']:
            anchor = next(a for a in source['comment_anchors'] if a['id'] == comment['id'])
            start, end = anchor['starts'][0], anchor['ends'][0]
            if start['paragraph_index'] not in mapping or end['paragraph_index'] not in mapping:
                raise ValueError(f"原稿批注无法定位：{source['source_path']} #{comment['id']}")
            bi, mapper = mapping[start['paragraph_index']]
            if end['paragraph_index'] != start['paragraph_index']:
                raise ValueError('本次原批注应均在同段范围')
            left, right = mapper(start['accepted_offset']), mapper(end['accepted_offset'])
            comments.append({'id': comment_id, 'author': comment['author'], 'date': comment['date'],
                             'initials': comment['initials'], 'text': comment['text'],
                             'source': source['source_path'], 'source_comment_id': comment['id'],
                             'original_excerpt': anchor.get('accepted_excerpt', '')})
            blocks[bi].setdefault('comments', []).append({'id': comment_id, 'start': left, 'end': max(left, right)})
            comment_id += 1
    if unmatched:
        raise ValueError('存在带修订或批注但未匹配的原段落：' + json.dumps(unmatched, ensure_ascii=False))

    # 本轮的摘要替换与两处口径统一保留为修订；旧长方法段的去除记入完整批注。
    editorial = []
    for block in blocks:
        if block.get('kind') == 'abstract':
            source_text = re.sub(r'^摘要[：:]\s*', '', clean_source(block.get('source_text', '')))
            if source_text and source_text != block['text']:
                block.setdefault('deletions', []).append({'id': revision_id, 'author': 'Claude', 'date': NOW,
                                                        'at': 0, 'text': source_text})
                revision_id += 1
                block.setdefault('revisions', []).append({'id': revision_id, 'author': 'Claude', 'date': NOW,
                                                        'start': 0, 'end': len(block['text'])})
                revision_id += 1
        for correction in block.get('editorial_changes', []):
            editorial.append({'block_id': block['id'], **correction})

    for change in article.get('changes', []):
        if change.get('action') not in ('minimal_content_alignment', 'replace_legacy_keywords'):
            continue
        block = next(b for b in blocks if b['id'] == change['block_id'])
        old = clean_source(change['source_text'])
        if block['kind'] == 'keywords':
            old = re.sub(r'^关键词[：:]\s*', '', old)
        new = block['text']
        for operation, a, b, c, d in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
            if operation == 'equal':
                continue
            if b > a:
                block.setdefault('deletions', []).append({'id': revision_id, 'author': 'Claude', 'date': NOW,
                                                         'at': c, 'text': old[a:b]})
                revision_id += 1
            if d > c:
                trimmed = []
                for original in block.get('revisions', []):
                    if original['end'] <= c or original['start'] >= d:
                        trimmed.append(original)
                    else:
                        if original['start'] < c:
                            trimmed.append({**original, 'end': c})
                        if original['end'] > d:
                            trimmed.append({**original, 'start': d})
                block['revisions'] = trimmed + [{'id': revision_id, 'author': 'Claude', 'date': NOW,
                                               'start': c, 'end': d}]
                revision_id += 1
            editorial.append({'block_id': block['id'], 'old': old[a:b], 'new': new[c:d], 'reason': change['reason']})

    def new_comment(block, text, author='合稿记录'):
        nonlocal comment_id
        comments.append({'id': comment_id, 'author': author, 'date': NOW, 'initials': '', 'text': text,
                         'source': 'current_markdown_or_assembly'})
        block.setdefault('comments', []).append({'id': comment_id, 'start': 0, 'end': min(len(block.get('text', '')), 4)})
        comment_id += 1

    for note in article.get('internal_notes', []):
        text = note if isinstance(note, str) else note.get('text', str(note))
        # 版本说明默认锚到摘要，历史身份保持在评论文字中。
        anchor = next(b for b in blocks if b['kind'] == 'abstract')
        new_comment(anchor, '可检索稿原版本说明\n' + text)
    for change in article.get('changes', []):
        text = change if isinstance(change, str) else json.dumps(change, ensure_ascii=False, indent=2)
        if any(word in text for word in ('二（三）', '二（四）', '旧二', '摘要', 'Bou-Franch', '5.2', '49,930', '附录')):
            anchor = next(b for b in blocks if b['kind'] == 'abstract')
            new_comment(anchor, '本次合稿处理\n' + text)
    article['comments'] = comments
    article['review_source_matches'] = matches
    (OUT / 'article.review.json').write_text(json.dumps(article, ensure_ascii=False, indent=2) + '\n')
    report = {'source_comments': sum(len(s['comments']) for s in sources),
              'restored_source_comments': sum(c.get('source_comment_id') is not None for c in comments),
              'total_comments': len(comments), 'source_revision_groups': revisions,
              'matched_paragraphs': matches, 'unmatched_reviewed_paragraphs': unmatched,
              'paragraph_format_revisions': sum(len(b.get('format_revisions', [])) for b in blocks),
              'editorial_changes': editorial}
    (OUT / 'qa/review_preservation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('source_comments', 'restored_source_comments', 'total_comments', 'paragraph_format_revisions')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
