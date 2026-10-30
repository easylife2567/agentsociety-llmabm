"""校验本归档，并在干净临时目录恢复固定基线源码/配置，禁止联网或仿真。"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

RUN = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_manifest():
    entries = json.loads((RUN / 'recovery/files_manifest.json').read_text())['files']
    for entry in entries:
        p = RUN / entry['path']
        if entry['kind'] == 'symlink':
            assert p.is_symlink() and os.readlink(p) == entry['link'], entry['path']
        else:
            assert p.is_file() and sha(p) == entry['sha256'], entry['path']
    return len(entries)


def verify_raw():
    manifest = json.loads((RUN / 'recovery/raw_manifest.json').read_text())
    for entry in manifest['files']:
        p = RUN / entry['target']
        assert p.is_file() and sha(p) == entry['sha256'], entry['target']
    results = []
    for algorithm, expected_posts in [('random', 176), ('chronological', 210), ('interest', 217)]:
        base = RUN / f'raw_outputs/cuc_model_v1/cuc_model_v1_{algorithm}'
        terminal = json.loads((base / 'SOCIETY_STEP.json').read_text())
        assert terminal['completed_step_count'] == 693
        assert json.loads((base / 'pid.json').read_text())['status'] == 'completed'
        env = json.loads((base / 'env/CurationDynamicsSpace/state/ENV_STATE.json').read_text())
        actions = env['_arrival_state']['actions']
        assert len(actions) == len({(str(a['agent_id']), a['week']) for a in actions}) == 1100
        assert len(env['_arrival_state']['weeks']) == 11
        agents = [json.loads(p.read_text()) for p in (base / 'agents').glob('*/AGENT.json')]
        assert len(agents) == 100
        decisions = [row for agent in agents for row in agent['decision_log']]
        assert len(decisions) == 1100
        posts = sum(bool(row.get('posted')) for row in decisions)
        assert posts == expected_posts == sum(env['_total_posts_by_agent'].values())
        assert all(row['reason'] not in ['action_failed', 'publication_failed'] for row in decisions)
        results.append({'algorithm': algorithm, 'steps': 693, 'actions': 1100,
                        'agents': 100, 'posts': posts})
    return {'passed': True, 'files': manifest['count'], 'bytes': manifest['bytes'], 'arms': results}


OFFLINE_CHECK = r'''
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import inspect,json,socket
root=Path.cwd();calls=[]
def deny(*args,**kwargs):
    calls.append('blocked')
    raise AssertionError('Offline restoration forbids network access')
with patch.object(socket.socket,'connect',deny),patch.object(socket.socket,'connect_ex',deny),patch.object(socket,'create_connection',deny):
    from agentsociety2.registry import scan_and_register_custom_modules,get_registered_env_modules
    from agentsociety2.society.models import InitConfig,StepsConfig
    import yaml
    scan_and_register_custom_modules(root)
    cls=dict(get_registered_env_modules())['CurationDynamicsSpace']
    assert Path(inspect.getfile(cls)).resolve()==root/'custom/envs/curation_dynamics_space.py'
    init=root/'hypothesis_4/experiment_4/init'
    steps=StepsConfig.model_validate(yaml.safe_load((init/'steps.yaml').read_text()))
    assert len(steps.steps)==693
    rows=[];normal=[]
    for p in sorted((init/'configs').glob('*.json')):
        raw=json.loads(p.read_text());cfg=InitConfig.model_validate(raw)
        env=cls(**cfg.env_modules[0].kwargs)
        assert env._random_seed==0 and 'random_seed' not in raw['env_modules'][0]['kwargs']
        assert len(cfg.agents)==len(env._agent_types)==len(env._chronological_action_hours)==100
        assert Counter(env._agent_types.values())=={'marketing':23,'mourning':22,'other':21,'meme':19,'education':15}
        for agent in cfg.agents:
            assert agent.agent_id==agent.kwargs['id']
            assert agent.kwargs['content_retry_budget']['limit']==330
        copied=json.loads(json.dumps(raw));arm=copied['env_modules'][0]['kwargs'].pop('recommendation_algorithm')
        normal.append(copied);rows.append({'algorithm':arm,'agents':100,'opportunities':1100,'batches':693,'effective_seed':0})
    assert len(normal)==3 and normal[0]==normal[1]==normal[2]
assert not calls
print(json.dumps({'passed':True,'arms':rows,'network_calls':0,'llm_calls':0,'baseline_custom_loaded':True}))
'''


def offline_check(skip_raw=False):
    # 仅复制固定基线custom与冻结输入；不读取主工作区未提交代码或.env。
    with tempfile.TemporaryDirectory(prefix='population-archive-restore-') as directory:
        restored = Path(directory)
        shutil.copytree(RUN / 'recovery/baseline_source/custom', restored / 'custom')
        preservation = json.loads((RUN / 'recovery/workspace_preservation.json').read_text())
        restored_records = []
        for entry in preservation['files']:
            if skip_raw and entry['target'].startswith('raw_outputs/'):
                continue
            destination = restored / entry['source']
            destination.parent.mkdir(parents=True, exist_ok=True)
            if entry['kind'] == 'symlink':
                destination.symlink_to(entry['link'])
                assert os.readlink(destination) == entry['link']
            else:
                shutil.copy2(RUN / entry['target'], destination)
                assert sha(destination) == entry['sha256']
            restored_records.append(entry['source'])
        for source in (RUN / 'recovery/baseline_source/custom').rglob('*'):
            if source.is_file():
                assert sha(source) == sha(restored / 'custom' / source.relative_to(RUN / 'recovery/baseline_source/custom'))
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(restored),
            WORKSPACE_PATH=str(restored), LITELLM_LOCAL_MODEL_COST_MAP='True',
            MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
            AGENTSOCIETY_LLM_API_KEY='offline-validation',
            AGENTSOCIETY_LLM_API_BASE='https://invalid.example/offline',
            AGENTSOCIETY_LLM_MODEL='offline-validation')
        result = subprocess.run([sys.executable, '-c', OFFLINE_CHECK], cwd=restored,
            env=environment, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        payload['workspace_items_restored'] = len(restored_records)
        payload['raw_restored'] = not skip_raw
        payload['source_sha256'] = {str(p.relative_to(restored)): sha(p)
            for p in restored.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline-check', action='store_true')
    parser.add_argument('--skip-raw', action='store_true', help='仅无原始本地数据的代码副本使用；不宣称原始输出核验')
    parser.add_argument('--report', type=Path, default=RUN / 'recovery/verification_latest.json')
    args = parser.parse_args()
    report = {'passed': False, 'simulation_calls': 0, 'network_calls': 0}
    try:
        report['files_verified'] = verify_manifest()
        report['raw'] = {'skipped': True} if args.skip_raw else verify_raw()
        if args.offline_check:
            report['offline_restore'] = offline_check(args.skip_raw)
        report['passed'] = True
    except Exception as error:
        report['error'] = {'type': type(error).__name__, 'message': str(error)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'files_verified': report.get('files_verified'),
        'raw_verified': bool(report.get('raw', {}).get('passed')), 'offline_check': args.offline_check,
        'report': str(args.report), 'error': report.get('error')}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
