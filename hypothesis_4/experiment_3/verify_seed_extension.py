"""新增21配置禁网验收；不运行Agent行动、环境step、Ray或LLM。"""
import asyncio
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import importlib.util
import inspect
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import traceback
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / 'checks/seed3_9_offline_verification.json'
MANIFEST = HERE / 'init/manifest_seed3_9.json'
REPORT = dict(status='checking', simulation_started=False, execution_authorized=False,
              llm_calls=0, network_attempts=0, agent_actions=0, environment_steps=0,
              ray_started=False, configs=[], errors=[])


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def verify():
    import yaml
    import agentsociety2
    from agentsociety2.registry import (scan_and_register_custom_modules,
        get_registered_agent_modules, get_registered_env_modules)
    from agentsociety2.society.cli import ExperimentRunner
    from agentsociety2.society.models import StepsConfig
    from seed_extension_guard import check_limits
    scan_and_register_custom_modules(ROOT)
    agent_cls = dict(get_registered_agent_modules())['CurationDiscourseAgent']
    env_cls = dict(get_registered_env_modules())['CurationDynamicsSpace']
    locations = {k: str(Path(inspect.getfile(v)).resolve())
                 for k, v in {'agent': agent_cls, 'env': env_cls}.items()}
    assert locations['agent'] == str(ROOT / 'custom/agents/curation_discourse_agent.py')
    assert locations['env'] == str(ROOT / 'custom/envs/curation_dynamics_space.py')
    REPORT['runtime'] = dict(python=sys.executable, sdk_version=importlib.metadata.version('agentsociety2'),
                            sdk_source=agentsociety2.__file__, loaded_modules=locations)
    spec = importlib.util.spec_from_file_location('official_config_check',
        ROOT / '.claude/skills/agentsociety-experiment-config/scripts/config.py')
    official = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(official)
    official._ensure_agentsociety2()
    assert official.action_validate(ROOT, '4', '3')['success']
    m = read(MANIFEST)
    assert m['execution_authorized'] is False
    assert [(r['seed'], r['condition']) for r in m['runs']] == [
        (s, c) for s in range(3, 10) for c in ('no_b', 'no_d', 'no_r')]
    assert all(digest(ROOT / p) == h for group in
        ('source_sha256', 'mechanism_sha256', 'output_sha256', 'old_assets_unchanged_sha256')
        for p, h in m[group].items())
    b = m['budget']
    ledger = ROOT / b['ledger_path']
    assert ledger.read_bytes() == b'0'
    assert b['started_at'] is None and b['deadline_at'] is None and not b['execution_authorized']
    assert b['decision_opportunities'] == 21 * 100 * 11 == 23100
    assert b['max_agent_body_requests'] == 23100 + b['extra_requests_limit'] == 25410
    old_ledger = HERE / 'runs/timestamp_bdr_v1_attempt_02/_extra_attempts.count'
    assert old_ledger.read_text().strip() == '5' and old_ledger != ledger
    now = datetime(2026, 10, 24, tzinfo=timezone.utc)
    assert check_limits(b, started_at=None, now=now, body_requests=0, extra_requests=0, active_runs=0) is None
    assert check_limits(b, started_at=now.isoformat(), now=now + timedelta(hours=47),
        body_requests=25410, extra_requests=2310, active_runs=2) == now + timedelta(hours=48)
    cases = [dict(now=now + timedelta(hours=48), body_requests=0, extra_requests=0, active_runs=0),
             dict(now=now, body_requests=25411, extra_requests=0, active_runs=0),
             dict(now=now, body_requests=0, extra_requests=2311, active_runs=0),
             dict(now=now, body_requests=0, extra_requests=0, active_runs=3)]
    for args in cases:
        try:
            check_limits(b, started_at=now.isoformat(), **args)
        except RuntimeError:
            pass
        else:
            raise AssertionError('预算/截止/并行越界未拒绝')
    REPORT['limit_boundary_checks'] = dict(passed=True, rejected_cases=len(cases),
        deadline_starts_at='future first formal launch', ledger_value=0, old_ledger_value=5)
    runner = ExperimentRunner.__new__(ExperimentRunner)
    param = {'no_b': 'baseline_utility', 'no_d': 'spiral_scale', 'no_r': 'decay'}
    profiles = 0
    fulls = {}
    with tempfile.TemporaryDirectory(dir=HERE / 'checks', prefix='.seed3_9_profile_check_') as tmp:
        for row in m['runs']:
            assert not (ROOT / row['run_dir']).exists(), row['run_id']
            full = read(ROOT / row['full_reference'])
            raw = read(ROOT / row['config'])
            normalized = deepcopy(raw)
            for original, changed in zip(full['agents'], normalized['agents']):
                key = param[row['condition']]
                assert changed['kwargs']['params'][key] == 0.0
                assert original['kwargs']['params'][key] != 0.0
                assert changed['kwargs']['content_retry_budget'] == {'limit': 2310, 'ledger_path': b['ledger_path']}
                changed['kwargs']['params'][key] = original['kwargs']['params'][key]
                changed['kwargs']['content_retry_budget'] = original['kwargs']['content_retry_budget']
            assert normalized == full, row['run_id']
            assert {a['agent_id'] for a in raw['agents']} == set(range(1, 101))
            assert all(a['agent_id'] == a['kwargs']['id'] for a in raw['agents'])
            assert raw['env_modules'] == full['env_modules']
            paths = {'init_config': ROOT / row['config'], 'steps_yaml': ROOT / row['steps']}
            with patch.object(official, 'get_experiment_paths', return_value=paths):
                result = official.action_check(ROOT, '4', '3')
            assert result['success'], (row['run_id'], result)
            parsed = runner._load_config(ROOT / row['config'])
            steps = StepsConfig.model_validate(yaml.safe_load((ROOT / row['steps']).read_text()))
            assert len(steps.steps) == 693
            t = datetime.fromisoformat(str(steps.start_t))
            assert t == datetime(2026, 3, 16, 6)
            for step in steps.steps:
                assert step.type == 'run' and step.num_steps == 1
                t += timedelta(seconds=int(step.tick))
            assert t == datetime(2026, 6, 1)
            specs, name = runner._build_agent_specs([a.model_dump() for a in parsed.agents])
            assert len(specs) == 100 and name == 'CurationDiscourseAgent'
            for agent_spec in specs:
                path = Path(tmp) / str(profiles)
                agent_cls.create(path, agent_spec['profile'], agent_spec['config'])
                with patch.object(agent_cls, '_bind_services'):
                    agent = await agent_cls.from_workspace(path, None)
                assert agent._profile == agent_spec['profile']
                assert agent._params[param[row['condition']]] == 0.0
                assert agent._decision_log == [] and agent._step_count == 0
                profiles += 1
            if row['seed'] not in fulls:
                full_dir = ROOT / row['full_run_dir']
                if row['seed'] == 6:
                    assert full_dir.name == 'timestamp_v1_interest_s6_resume1'
                assert read(full_dir / 'pid.json')['status'] == 'completed'
                assert read(full_dir / 'SOCIETY_STEP.json')['step_count'] == 693
                arrival = read(full_dir / 'env/CurationDynamicsSpace/state/ENV_STATE.json')['_arrival_state']
                assert len(arrival['weeks']) == 11 and len(arrival['actions']) == 1100
                assert len({(str(a['agent_id']), a['week']) for a in arrival['actions']}) == 1100
                decisions = set()
                files = list((full_dir / 'agents').glob('*/AGENT.json'))
                assert len(files) == 100
                count = 0
                for f in files:
                    a = read(f)
                    for d in a['decision_log']:
                        count += 1
                        decisions.add((str(a['id']), d['week']))
                        assert d.get('reason') not in ('action_failed', 'publication_failed')
                assert count == len(decisions) == 1100
                fulls[row['seed']] = row['full_run_dir']
            REPORT['configs'].append(dict(run_id=row['run_id'], official_check=result,
                unique_scientific_parameter=param[row['condition']], agent_profiles_restored=100,
                steps=693, simulated_engine_steps=0, full_run_dir=row['full_run_dir']))
            print('PASS', row['run_id'], flush=True)
    REPORT.update(profiles_created_and_restored=profiles, fulls_reverified=fulls)
    assert profiles == 2100 and len(fulls) == 7
    prior = read(HERE / 'checks/seed3_9_preservation_before.json')['sha256']
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert all(pool.map(lambda pair: digest(ROOT / pair[0]) == pair[1], prior.items()))
    REPORT['preserved_original_files'] = len(prior)
    assert ledger.read_bytes() == b'0' and old_ledger.read_text().strip() == '5'
    REPORT['manifest_sha256'] = digest(MANIFEST)
    REPORT['diagnostic_corrections'] = {'first_check': '验收器误将冻结steps的06:00起点写为午夜，已修正；配置不变。首轮失败证据单独保留。', 'outside_guard_diagnostic_import': '一次诊断SDK导入触发默认远程价格表读取并超时；未调用LLM，后续显式LITELLM_LOCAL_MODEL_COST_MAP=True。', 'guarded_acceptance_network_attempts': 0}


def main():
    os.chdir(ROOT)
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False',
                      ANONYMIZED_TELEMETRY='False', WORKSPACE_PATH=str(ROOT),
                      AGENTSOCIETY_WORKSPACE=str(ROOT))
    def deny_network(*args, **kwargs):
        REPORT['network_attempts'] += 1
        raise AssertionError('离线验收禁止网络')
    async def deny_llm(*args, **kwargs):
        REPORT['llm_calls'] += 1
        raise AssertionError('离线验收禁止模型调用')
    try:
        with patch.object(socket.socket, 'connect', deny_network), \
             patch.object(socket.socket, 'connect_ex', deny_network), \
             patch.object(socket, 'create_connection', deny_network):
            import litellm
            with patch.object(litellm.Router, 'acompletion', deny_llm), \
                 patch.object(litellm, 'acompletion', deny_llm):
                asyncio.run(verify())
        assert REPORT['network_attempts'] == REPORT['llm_calls'] == 0
        REPORT['status'] = 'passed'
    except Exception:
        REPORT['status'] = 'failed'
        REPORT['errors'].append(traceback.format_exc())
    REPORT['verifier_sha256'] = digest(Path(__file__))
    OUTPUT.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2, default=str) + '\n')
    print(json.dumps({k: REPORT.get(k) for k in ('status', 'profiles_created_and_restored',
        'preserved_original_files', 'network_attempts', 'llm_calls', 'agent_actions', 'environment_steps')}, ensure_ascii=False))
    if REPORT['status'] != 'passed':
        print(REPORT['errors'][-1], file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
