"""汇总独立逐条阅读的判读，检查冻结必查覆盖并统计问题帖直接曝光。

脚本不自动判定语义；关键词只定义覆盖范围，判读来自任务内review记录。
问题帖被展示不等于错误细节被阅读，更不等于造成行为变化，输出不得作因果界限。
"""
import hashlib
import importlib.util
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[2]
OUT = ROOT/'presentation/hypothesis_4/2026-09-30-01-arrival-timing'
spec = importlib.util.spec_from_file_location('frozen_tagger', ROOT/'custom/envs/curation_assets/build_assets.py')
tagger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tagger)


def read(path):
    return json.loads(path.read_text())


def main():
    manifest = read(ROOT/'hypothesis_4/experiment_1/init/arrival_timing_diagnostic/manifest.json')
    vocab = read(ROOT/'custom/envs/curation_assets/vocabs.json')['meme']
    terms = list(manifest['knowledge_audit']['remaining_screen_terms'])
    for name in ('linkage','strong','weak_markers','cautious_numbers','exclude_death_fact'):
        terms.extend(vocab[name])
    terms = sorted(set(t.lower() for t in terms))
    cutoff = datetime.fromisoformat(manifest['official_available_at'])
    reviews, hashes = {}, {}
    for file in sorted(TASK.glob('*semantic*.json')):
        hashes[str(file.relative_to(ROOT))] = hashlib.sha256(file.read_bytes()).hexdigest()
        for record in read(file)['records']:
            key = (record['run_id'],str(record['agent_id']),record['week'])
            assert key not in reviews, key
            reviews[key] = record
    results = {}
    for run in manifest['runs']:
        root = ROOT/run['run_dir']
        ds = []
        for file in sorted((root/'agents').glob('*/AGENT.json')):
            agent = read(file)
            ds.extend(dict(d,agent_id=str(agent['id'])) for d in agent['decision_log'] if d.get('posted'))
        reviewed = [reviews[(run['run_id'],d['agent_id'],d['week'])] for d in ds
                    if (run['run_id'],d['agent_id'],d['week']) in reviews]
        early, hit, nonhit, missed = [], [], [], []
        for d in ds:
            key = (run['run_id'],d['agent_id'],d['week'])
            is_early = d['week']=='2026-W12' or (d['week']=='2026-W13' and datetime.fromisoformat(d['acted_at'])<cutoff)
            layers = (d['content'].lower(),tagger.normalize(d['content']))
            is_hit = any(t in layer for t in terms for layer in layers)
            if is_early: early.append(key)
            if is_hit: hit.append(key)
            if not is_hit: nonhit.append(key)
            if is_early or is_hit:
                if key not in reviews: missed.append(key)
            if key in reviews:
                assert reviews[key]['post_id']==d['post_id']
                if 'content' in reviews[key]: assert reviews[key]['content']==d['content']
                context = reviews[key].get('prompt_context',reviews[key].get('context'))
                if context is not None: assert context==d['prompt_context']
        assert not missed, missed
        samples = {}
        for label, late in (('early',False),('late',True)):
            candidates = [k for k in nonhit if (k[2]>='2026-W19')==late]
            samples[label] = sum(k in reviews for k in candidates)
            assert samples[label]>=min(10,len(candidates))
        # 判读中的无来源细节含错误年龄、活动时间与相对日期，不均称为未来知识泄漏。
        unsupported = [r for r in reviewed if r['verdict'] in ('unsupported','unsupported_event_detail')]
        keys = {f"agent:{r['agent_id']}:{r['week']}" for r in unsupported}
        env = read(root/'env/CurationDynamicsSpace/state/ENV_STATE.json')
        actions = env['_arrival_state']['actions']
        issue_exposures = sum(p['stable_key'] in keys for a in actions for p in a['feed'])
        issue_late = sum(p['stable_key'] in keys for a in actions if a['week']>='2026-W19' for p in a['feed'])
        prompts = sum(c['stable_key'] in keys for d in ds for c in d['prompt_context'])
        results[run['run_id']] = dict(published=len(ds), reviewed=len(reviewed), early_required=len(early),
            screen_hits=len(hit), nonhit_reviewed=samples, uncovered_required=missed,
            verdicts=dict(Counter(r['verdict'] for r in reviewed)),
            uncertain_notes=sum(bool(r.get('uncertain_note')) for r in reviewed),
            unsupported_count=len(unsupported),
            unsupported_records=[{k:r.get(k) for k in ('agent_id','week','post_id','acted_at','unsupported_quote','explanation')} for r in unsupported],
            issue_post_numeric_exposures=issue_exposures, issue_post_late_exposures=issue_late,
            issue_post_actual_prompt_references=prompts)
    result = dict(results=results, total_reviewed=len(reviews), review_sha256=hashes,
        limits='覆盖核验不是自动语义验证；无依据细节率不是无偏污染率；问题帖曝光不证明细节被传递或导致主指标变化。')
    (OUT/'knowledge_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:{x:v[x] for x in ('published','reviewed','early_required','screen_hits','unsupported_count','issue_post_numeric_exposures','issue_post_late_exposures','issue_post_actual_prompt_references')} for k,v in results.items()},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
