"""内容修复的离线数值预期：固定归档正文/发言安排，修正细节并保留每次发布。

全四格复算4,400次效用判定；对归档正文离线修正，拒答使用标明来源的兜底；不重新驱动库存或调用LLM。
五类计数仍是作者类型。额外风险命中单列待核查，不自动认作真实错误。
"""
import csv
import hashlib
import importlib.util
import json
import os
import socket
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[1]
OUT = ROOT/'presentation/hypothesis_4/2026-09-30-01-arrival-timing'
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
os.environ['MPLCONFIGDIR'] = str(TASK/'tmp/matplotlib')
os.environ['XDG_CACHE_HOME'] = str(TASK/'tmp')
ATTEMPTS = []


def no_network(*args, **kwargs):
    ATTEMPTS.append(1)
    raise RuntimeError('content numerical audit forbids network')


socket.socket.connect = no_network
socket.socket.connect_ex = no_network


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT/relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


QUALITY = load('content_numerical_quality', 'custom/agents/curation_content_quality.py')
AGENT = load('content_numerical_agent', 'custom/agents/curation_discourse_agent.py').CurationDiscourseAgent
STYLE = load('content_numerical_template', 'hypothesis_4/experiment_1/plot_run_charts.py')
KINDS = [k for k in STYLE.TYPE_ORDER if k != 'noise']
WEEKS = [f'2026-W{w}' for w in range(12, 23)]


def read(path):
    return json.loads(path.read_text())


def write_csv(name, rows):
    with (OUT/name).open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    manifest_path = ROOT/'hypothesis_4/experiment_1/init/arrival_timing_diagnostic/manifest.json'
    fixture_path = TASK/'2026-10-07-02-content-acceptance-fixtures.json'
    samples = read(fixture_path)['records']
    mandatory = {(x['review']['run_id'], str(x['review']['agent_id']), x['review']['week']): x for x in samples}
    hashes = {}
    def lock(path):
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for path in [Path(__file__), fixture_path, manifest_path, ROOT/'custom/agents/curation_content_quality.py',
                 ROOT/'custom/agents/curation_discourse_agent.py', ROOT/'custom/envs/curation_dynamics_space.py',
                 ROOT/'hypothesis_4/experiment_1/plot_run_charts.py']:
        lock(path)
    rows, weekly_rows, checked_samples, summary = [], [], [], {}
    for run in read(manifest_path)['runs']:
        directory = ROOT/run['run_dir']
        state_path = directory/'env/CurationDynamicsSpace/state/ENV_STATE.json'
        lock(state_path)
        actions = {(x['agent_id'], x['week']): x for x in read(state_path)['_arrival_state']['actions']}
        condition = run['arrival_mode']+'-'+run['algorithm']
        counts, archived, extra = Counter(), Counter(), []
        opportunities, max_error = 0, 0.
        for path in sorted((directory/'agents').glob('*/AGENT.json')):
            lock(path)
            doc = read(path); aid = str(doc['id']); profile = doc['profile']
            agent = SimpleNamespace(_agent_type=profile['agent_type'], _params=profile['params'])
            for d in doc['decision_log']:
                a = actions[aid, d['week']]
                n = len(a['feed']); types = Counter(p['type'] for p in a['feed'])
                snap = dict(feed=a['feed'], feed_type_distribution={k: types[k]/n if n else 0. for k in KINDS},
                            personal_stats={'cumulative_exposures': a['cumulative_before']}, event_signal={}, meme_env={})
                u, _ = AGENT._speak_stimulus(agent, snap)
                error = abs(u-d['u']); max_error = max(max_error, error)
                assert error <= 1e-12 and (u >= profile['params']['activity']) == d['speak']
                opportunities += 1
                if not d['posted']:
                    continue
                context = QUALITY.prompt_context(a['feed'])
                # 历史服务结构化拒答字段未留存，静态复核只使用已存完整发布正文。
                response = {'choices': [{'message': {'content': d['content']}, 'finish_reason': 'stop'}]}
                checked = QUALITY.inspect_response(response, context)
                initial_status = checked['content_status']
                candidate = QUALITY.publication_candidate(checked, context) or QUALITY.fallback_content(agent, context)
                assert QUALITY.assess_text(candidate['content'], context)[0] == 'accepted'
                key = run['run_id'], aid, d['week']
                known = key in mandatory
                if known:
                    expected = 'refusal' if mandatory[key]['review']['verdict'] == 'service_refusal' else 'unsupported_detail'
                    assert checked['content_status'] == expected, key
                    checked_samples.append(dict(run_id=key[0], agent_id=aid, week=d['week'],
                                                initial_status=initial_status, final_status='accepted', content_origin=candidate['content_origin'], edits=candidate['detail_edits'], checks=checked['content_checks']))
                elif checked['content_status'] != 'accepted':
                    extra.append(dict(agent_id=aid, week=d['week'], post_id=d['post_id'],
                                      status=checked['content_status'], checks=checked['content_checks']))
                accepted = True
                archived[d['week'], profile['agent_type']] += 1
                counts[d['week'], profile['agent_type']] += accepted
                rows.append(dict(condition=condition, run_id=run['run_id'], agent_id=aid, week=d['week'],
                                 post_id=d['post_id'], author_type=profile['agent_type'], known_issue=known,
                                 initial_status=initial_status, final_status='accepted', content_origin=candidate['content_origin'],
                                 edits=json.dumps(candidate['detail_edits'], ensure_ascii=False), repaired_content=candidate['content'],
                                 checks=json.dumps(checked['content_checks'], ensure_ascii=False),
                                 archived_published=True, statically_accepted=accepted))
        assert opportunities == 1100
        status_counts = dict(Counter(r['initial_status'] for r in rows if r['condition'] == condition))
        summary[condition] = dict(archived_published=sum(archived.values()), preserved_posts=sum(counts.values()),
                                  known_cases=sum(x['run_id'] == run['run_id'] for x in checked_samples),
                                  extra_screen_hits=len(extra), extra_cases_for_review=extra,
                                  initial_status_counts=status_counts, content_origin_counts=dict(Counter(r['content_origin'] for r in rows if r['condition']==condition)), opportunities=opportunities, max_u_error=max_error)
        weekly = [dict(condition=condition, week=w, **{k: counts[w, k] for k in KINDS},
                       total=sum(counts[w, k] for k in KINDS), archived_total=sum(archived[w, k] for k in KINDS)) for w in WEEKS]
        assert sum(w['total'] for w in weekly) == sum(counts.values()) == sum(archived.values())
        assert all(w['total']==w['archived_total'] for w in weekly)
        weekly_rows.extend(weekly)
        # 用户模板仅提供样式；不把旧归档经门控的静态计数称为新仿真产出。
        fig, ax = STYLE.plt.subplots(figsize=(10, 5.4)); x = list(range(11))
        STYLE._death_line(ax, WEEKS)
        ax.stackplot(x, *[[w[k] for w in weekly] for k in KINDS],
                     labels=[STYLE.TYPE_LABEL_EN[k] for k in KINDS], colors=[STYLE.TYPE_COLOR[k] for k in KINDS],
                     edgecolor='white', linewidth=0.6, alpha=0.92, zorder=2)
        ax.plot(x, [w['archived_total'] for w in weekly], color='#444444', ls='--', lw=1.1, label='Archived count', zorder=3)
        for i, w in enumerate(weekly):
            ax.text(i, max(w['total'],w['archived_total'])+1.4, str(w['total']), ha='center', fontsize=9)
        assert max(w['archived_total'] for w in weekly) <= 80
        ax.set_xticks(x, WEEKS, rotation=45); ax.set_ylim(0,80); ax.set_yticks(range(0,81,10))
        ax.set_ylabel('内容修复后保留发布数（条 / 周）')
        ax.set_title(f'内容修复的数值预期（无 LLM · {condition}）', fontsize=13)
        ax.legend(loc='upper right', frameon=False, fontsize=9); STYLE._tidy(ax)
        fig.text(.07,.035, f"100人 · seed 0 · 归档{sum(archived.values())}条 → 保留{sum(counts.values())}条 · 类型=作者身份\n"
                 f"固定原供给；离线修正文；非闭环预测；额外{len(extra)}条细节筛查待核查；timestamp时机方案暂停", fontsize=8, color='#555555')
        fig.tight_layout(rect=(0,.10,1,1))
        stem = f'2026-10-07-0{4+len(summary)}-content-{condition}'
        fig.savefig(OUT/f'{stem}.png',dpi=300)
        svg=OUT/f'{stem}.svg';fig.savefig(svg)
        # 清理SVG导出器的路径行尾空格，不改变矢量图内容。
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
        STYLE.plt.close(fig)
    assert len(checked_samples) == 20 and not ATTEMPTS
    assert len(rows) == 794 and len(weekly_rows) == 44
    for name, digest in hashes.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest
    write_csv('2026-10-07-01-content-decisions.csv',rows)
    write_csv('2026-10-07-02-content-weekly.csv',weekly_rows)
    result = dict(conditions=summary, mandatory_results=checked_samples, source_sha256=hashes,
                  network_attempts=0, model_calls=0, numeric_actions=4400,
                  scope='static detail repair with preserved original supply; refusal uses labelled offline fallback; not closed-loop prediction')
    (OUT/'2026-10-07-03-content-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:{n:v[n] for n in ('archived_published','preserved_posts','known_cases','extra_screen_hits','max_u_error')} for k,v in summary.items()},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
