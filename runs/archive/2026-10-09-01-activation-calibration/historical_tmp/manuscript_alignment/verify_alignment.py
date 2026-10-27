from pathlib import Path
import hashlib
import json
import re
import difflib
import subprocess
import zipfile
import xml.etree.ElementTree as ET

root = Path('/Users/easylife/Project/AgentSociety')
out = root/'runs/2026-10-09-01-activation-calibration/manuscript_alignment'
evidence = json.loads((out/'evidence.json').read_text())
paths = evidence['updated_paths']
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
checks = {}
checks['original_sources_unchanged'] = all(sha(root/p)==v for p,v in evidence['sources_sha256'].items())
checks['before_snapshots_match_recorded_hashes'] = all(sha(out/'before'/p)==v for p,v in evidence['before_sha256'].items())
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
word_counts = {}
for p in evidence['sources_sha256']:
    if not p.endswith('.docx'):
        continue
    with zipfile.ZipFile(root/p) as z:
        doc = ET.fromstring(z.read('word/document.xml'))
        comments = ET.fromstring(z.read('word/comments.xml'))
        note_kind = 'footnote' if 'word/footnotes.xml' in z.namelist() else 'endnote'
        notes = ET.fromstring(z.read('word/'+note_kind+'s.xml'))
        word_counts[p] = {'insertions':len(doc.findall('.//w:ins', ns)),
                          'deletions':len(doc.findall('.//w:del',ns)),
                          'comments':len(comments.findall('w:comment',ns)),
                          'notes':len([f for f in notes.findall('w:'+note_kind,ns) if f.get('{'+ns['w']+'}type') not in ('separator','continuationSeparator')])}
expected = [(7,0,7,14),(24,11,8,4)]
checks['docx_counts_match_audit'] = [tuple(v.values()) for v in word_counts.values()]==expected
man = (root/'paper/manuscript/manuscript.accepted.md').read_text()
old = (out/'before/paper/manuscript/manuscript.accepted.md').read_text()
key = '**（二）研究方法**'
checks['later_chapters_and_old_footnotes_preserved'] = man.split(key,1)[1].split('\n\n<!-- 2026-10-12',1)[0]==old.split(key,1)[1]
checks['abstract_keywords_preserved'] = man.split('**摘要：**',1)[1].split('在社交媒体深度嵌入公共生活的当下',1)[0]==old.split('**摘要：**',1)[1].split('在社交媒体深度嵌入公共生活的当下',1)[0]
checks['prior_revision_notes_preserved'] = all(block in man for block in old.split('**摘要：**',1)[0].split('\n\n')[1:])
refs = re.findall(r'\[\^((?:bg|tf)\d+)\](?!:)',man)
defs = re.findall(r'^\[\^((?:bg|tf)\d+)\]:',man,re.M)
checks['new_footnotes_resolved_once'] = sorted(refs)==sorted(defs) and len(set(defs))==18 and len(defs)==18
bg = (out/'background.accepted.md').read_text().split('[^bg1]:',1)[0].strip()
tf = (out/'framework.accepted.md').read_text().split('[^tf1]:',1)[0].split('\n\n',1)[1].strip()
checks['latest_author_sections_imported'] = bg in man and tf in man
checks['three_research_questions_match'] = all(q in man and q in (root/'TOPIC.md').read_text() for q in [
    '逝者数字形象呈现何种时序结构与演化特征，这一过程在不同平台之间呈现出何种共性与差异？',
    '不同算法推荐机制与用户发帖行为形成的循环交互过程，如何共同塑造逝者数字形象的演化轨迹与玩梗话语扩散格局？',
    '不同算法推荐机制是否会差异化推动网络氛围由庄重悼念向迷因化、戏谑化玩梗方向转变？'])
broken_new_links = []
for p in paths:
    prior = (out/'before'/p).read_text()
    new = (root/p).read_text()
    pat = r'(?<!!)\[[^\]\n]+\]\((<[^>]+>|[^)\n]+)\)'
    oldlinks = set(re.findall(pat, prior))
    for target in set(re.findall(pat,new))-oldlinks:
        target = target.strip('<>')
        if re.match(r'^[a-z]+:',target):
            continue
        target = target.split('#')[0]
        if target and not ((root/p).parent/target).exists():
            broken_new_links.append([p,target])
checks['new_local_links_exist'] = not broken_new_links
gitdiff = subprocess.run(['git','diff','--check'],cwd=root,capture_output=True,text=True)
checks['git_diff_check_passed'] = gitdiff.returncode==0
start_paths = set()
for line in (out/'git_start.txt').read_text().splitlines():
    if line[:2] not in ('??','!!'):
        start_paths.add(line[3:].strip('"'))
current_paths = subprocess.check_output(['git','-c','core.quotepath=false','diff','--name-only'],cwd=root,text=True).splitlines()
checks['new_tracked_diff_paths_within_scope'] = not (set(current_paths)-start_paths-set(paths))
checks['no_code_config_or_data_paths_in_tracked_diff'] = all(p.endswith('.md') for p in current_paths)
checks['staging_unchanged_empty'] = not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root,text=True).strip()
evidence['after_sha256'] = {p:sha(root/p) for p in paths}
evidence['checks'] = checks
evidence['docx_structure_counts'] = word_counts
evidence['broken_new_links'] = broken_new_links
evidence['validation_scope'] = '文稿来源、同步范围、引用及链接检查；未运行模型、代码测试或仿真。'
diff = ''.join(''.join(difflib.unified_diff((out/'before'/p).read_text().splitlines(True), (root/p).read_text().splitlines(True),fromfile='a/'+p,tofile='b/'+p)) for p in paths)
(out/'alignment.diff').write_text(diff)
(out/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':checks, 'docx_counts':word_counts,'broken_new_links':broken_new_links},ensure_ascii=False,indent=2))
assert all(checks.values()), '存在文档核验失败项'
