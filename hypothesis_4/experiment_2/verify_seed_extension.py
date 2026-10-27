"""禁网验收主实验 seed 3–9；不启动社会引擎、Ray或模型服务。

全窗仅运行本地环境到达/推荐过程，不生成Agent帖子，不能作为科研结果。
当前模型配置与旧批的差异单列，不把离线验收写成后台模型兼容性证明。
"""
import asyncio
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import importlib.metadata
import importlib.util
import inspect
import io
import json
import os
from pathlib import Path
import platform
import socket
import sys
import tempfile
import traceback
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INIT = HERE / 'init'
OUTPUT = HERE / 'seed_extension_verification.json'
REPORT = {'execution_authorized': False, 'llm_calls': 0, 'network_connection_attempts': 0,
          'scope': '新增21配置与本地环境功能验收；无生成、无Agent反馈，不是LLM仿真',
          'checks': [], 'windows': [], 'errors': []}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(name, condition, details=None):
    if not condition:
        raise AssertionError(name)
    REPORT['checks'].append({'name': name, 'passed': True, 'details': details})


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def runtime_conditions():
    """只保存非敏感模型标识、接口主机/路径和文件哈希，不输出密钥或环境全文。"""
    from dotenv import dotenv_values
    import agentsociety2
    from agentsociety2.society import cli, models
    from agentsociety2.config import config as sdk_config

    old = read(HERE / 'runs/timestamp_v1/execution_records/seed0_2/runtime_plan.json')
    configured = dotenv_values(ROOT / '.env')
    endpoint = urlsplit(configured.get('AGENTSOCIETY_LLM_API_BASE') or '')
    counts = {}
    for run in old['runs']:
        returned = Counter()
        for path in sorted((ROOT / run['run_dir'] / 'agents').glob('*/AGENT.json')):
            for row in read(path).get('decision_log', []):
                if row.get('response_model'):
                    returned[row['response_model']] += 1
        counts[run['run_id']] = dict(returned)
    configured_model = configured.get('AGENTSOCIETY_LLM_MODEL')
    source_paths = [Path(cli.__file__), Path(models.__file__), Path(sdk_config.__file__),
                    Path(sdk_config.__file__).with_name('llm_dispatcher.py'),
                    ROOT / 'AgentSociety2/uv.lock']
    result = {
        'old_requested_model': old['model'], 'old_service_host': old['service_host'],
        'old_response_models_by_run': counts,
        'current_configured_model': configured_model,
        'current_service_host': endpoint.hostname, 'current_api_path': endpoint.path,
        'credential_present': bool(configured.get('AGENTSOCIETY_LLM_API_KEY')),
        'configured_request_model_matches_old': configured_model == old['model'],
        'service_host_matches_old': endpoint.hostname == old['service_host'],
        'old_api_path': None, 'old_api_path_status': '旧主批运行计划未冻结完整API路径，无法离线核对',
        'backend_equivalence': 'unverified_without_provider_evidence',
        'current_python': sys.executable, 'current_python_version': platform.python_version(),
        'current_agentsociety2_version': importlib.metadata.version('agentsociety2'),
        'current_agentsociety2_source': agentsociety2.__file__,
        'old_sdk_version_status': '旧主批未记录可核对的包版本，当前版本仅作本次快照',
        'current_runtime_sha256': {str(p.relative_to(ROOT)): digest(p) for p in source_paths if p.exists()},
        'required_before_launch': [
            '明确采用原完整请求模型标识；不要直接沿用当前不同的.env默认模型',
            '核实当前API路径支持原模型，并记录新批实际response_model；离线不发送探针',
            '启动前重新核对源码/输入/运行库哈希，单独授权运行时限及调用预算',
            '使用新增manifest的独立输出与账本；旧九次启动器不能直接用于本批',
        ],
        'proposed_execution_conditions': {
            'required_model': old['model'], 'serial': True, 'batch_size': 100,
            'AGENTSOCIETY_LLM_RAY_MAX_WORKERS': '4', 'AGENTSOCIETY_LLM_RAY_CONCURRENCY': '16',
            'LITELLM_LOCAL_MODEL_COST_MAP': 'True', 'MEM0_TELEMETRY': 'False',
            'ANONYMIZED_TELEMETRY': 'False', 'temperature': 1.0, 'timeout_seconds': 60,
            'num_retries': 0, 'caching': False, 'stream': False,
            'object_store_memory_bytes': 1000000000, 'max_wall_hours': None,
            'note': '调用参数从原冻结行动源码核对；线程与batch沿用原启动器；时限待运行授权',
        },
        'ready_to_launch': False,
    }
    checked('旧主批源码及输入33项哈希仍匹配',
            all(digest(ROOT / p) == h for p, h in old['source_sha256'].items()), len(old['source_sha256']))
    checked('旧九次实际结果均有可核对的模型返回标识', len(counts) == 9 and all(counts.values()), counts)
    return result


async def verify():
    from agentsociety2.registry import (scan_and_register_custom_modules,
                                       get_registered_env_modules, get_registered_agent_modules)
    from agentsociety2.society.cli import ExperimentRunner
    from agentsociety2.society.models import StepsConfig
    import yaml

    manifest = read(INIT / 'manifest_seed3_9.json')
    checked('仅准备三臂seed3–9，未授权执行',
            manifest['execution_authorized'] is False and len(manifest['runs']) == 21)
    scan_and_register_custom_modules(ROOT)
    env_cls = dict(get_registered_env_modules())['CurationDynamicsSpace']
    agent_cls = dict(get_registered_agent_modules())['CurationDiscourseAgent']
    checked('registry加载正式custom模块',
            Path(inspect.getfile(env_cls)).resolve() == ROOT / 'custom/envs/curation_dynamics_space.py'
            and Path(inspect.getfile(agent_cls)).resolve() == ROOT / 'custom/agents/curation_discourse_agent.py')
    official = load('official_seed_config_check', ROOT / '.claude/skills/agentsociety-experiment-config/scripts/config.py')
    official._ensure_agentsociety2()
    REPORT['official_default_checks'] = {
        'validate': official.action_validate(ROOT, '4', '2'),
        'check': official.action_check(ROOT, '4', '2'),
    }
    checked('官方experiment-config validate/check通过（旧默认入口）',
            all(r['success'] for r in REPORT['official_default_checks'].values()))
    REPORT['runtime_conditions'] = runtime_conditions()
    REPORT['manifest_sha256'] = digest(INIT / 'manifest_seed3_9.json')
    checked('新增输出哈希匹配',
            all(digest(ROOT / p) == h for p, h in manifest['output_sha256'].items()), len(manifest['output_sha256']))

    old_config = read(INIT / 'configs/timestamp_v1_interest_s0.json')
    runner = ExperimentRunner.__new__(ExperimentRunner)
    profile_count = 0
    normalized_by_seed = {}
    seen_run_dirs = set()
    with tempfile.TemporaryDirectory(dir=HERE / 'tmp', prefix='seed-check-') as folder:
        for run in manifest['runs']:
            config_path = ROOT / run['config']
            raw = read(config_path)
            parsed = runner._load_config(config_path)
            steps = StepsConfig.model_validate(yaml.safe_load((ROOT / run['steps']).read_text()))
            specs, name = runner._build_agent_specs([a.model_dump() for a in parsed.agents])
            assert len(specs) == 100 and name == 'CurationDiscourseAgent'
            assert all(a['agent_id'] == a['kwargs']['id'] for a in raw['agents'])
            normalized = deepcopy(raw)
            algorithm = normalized['env_modules'][0]['kwargs'].pop('recommendation_algorithm')
            seed = normalized['env_modules'][0]['kwargs']['random_seed']
            assert seed == run['seed'] and algorithm == run['algorithm'] and seed in range(3, 10)
            if seed in normalized_by_seed:
                assert normalized == normalized_by_seed[seed]
            else:
                normalized_by_seed[seed] = normalized
            scientific = deepcopy(raw)
            baseline = deepcopy(old_config)
            for doc in (scientific, baseline):
                kwargs = doc['env_modules'][0]['kwargs']
                for key in ('recommendation_algorithm', 'random_seed', 'injection_data_path',
                            'weekly_initial_injection_data_path'):
                    kwargs.pop(key)
                for agent in doc['agents']:
                    agent['kwargs'].pop('content_retry_budget')
            assert scientific == baseline, '除seed、输入路径、算法和独立预算外不得改变原科学配置'
            ledger_paths = set()
            for spec in specs:
                budget = spec['profile']['content_retry_budget']
                assert budget['limit'] == 2310
                ledger_paths.add(budget['ledger_path'])
                path = Path(folder) / str(profile_count)
                agent_cls.create(path, spec['profile'], spec['config'])
                with patch.object(agent_cls, '_bind_services'):
                    agent = await agent_cls.from_workspace(path, None)
                assert agent._profile['content_retry_budget'] == budget
                assert agent._profile.get('chronological_action_hour_overrides', {}) == spec['profile'].get('chronological_action_hour_overrides', {})
                profile_count += 1
            assert len(ledger_paths) == 1
            ledger = ROOT / next(iter(ledger_paths))
            assert 'timestamp_v1_seed3_9' in str(ledger) and not ledger.exists()
            directory = ROOT / run['run_dir']
            assert directory not in seen_run_dirs and not directory.exists()
            seen_run_dirs.add(directory)
            env = env_cls(**parsed.env_modules[0].kwargs)
            assert env._arrival_official_policy == 'ordinary'
            t = datetime.fromisoformat(str(steps.start_t))
            assert len(steps.steps) == 693
            await env.init(t)
            assert len(env._posts) == 17
            empty = []
            for step in steps.steps:
                assert step.type == 'run' and step.num_steps == 1
                if not env._chronological_active_agents:
                    empty.append(t.isoformat())
                await env.step(int(step.tick), t)
                t += timedelta(seconds=int(step.tick))
            assert t == datetime(2026, 6, 1)
            state = env._arrival.state
            assert len(state['actions']) == 1100 and len(state['weeks']) == 11
            assert len({(r['agent_id'], r['week']) for r in state['actions']}) == 1100
            assert env._chronological_batch_index == 693
            assert len(env._injected_source_keys) == 267
            assert sum(w['injected_count'] for w in state['weeks']) == 250
            assert empty == ['2026-03-23T18:00:00']
            mourning = [r for r in state['actions'] if r['week'] == '2026-W13' and r['agent_type'] == 'mourning']
            assert len(mourning) == 22 and all(r['acted_at'] > '2026-03-24T20:00:00+08:00' for r in mourning)
            for row in state['actions']:
                assert len(row['feed']) <= 10 and row['candidate_future'] == 0
                assert all(p['published_at'] <= row['acted_at'] and p['available_at'] <= row['acted_at'] for p in row['feed'])
                assert row['pinned_keys'] == []
                assert all(p['stable_key'] not in row['floor_keys'] for p in row['feed'] if p['is_official'])
                if algorithm != 'interest':
                    assert row['floor_keys'] == []
            assert sum(w['total_exposures'] for w in state['weeks']) == sum(len(r['feed']) for r in state['actions'])
            REPORT['windows'].append({'run_id': run['run_id'], 'seed': seed, 'algorithm': algorithm,
                                      'batches': 693, 'unique_actions': 1100, 'weeks': 11,
                                      'injected_window_posts': 250, 'initial_posts': 17,
                                      'future_exposures': 0, 'mourning_after_official': 22,
                                      'official_seen_by_mourning': sum(any(p['is_official'] for p in r['feed']) for r in mourning)})
            print('PASS', run['run_id'], flush=True)
    checked('21配置官方schema/steps及完整环境窗口通过', len(REPORT['windows']) == 21)
    checked('2100份真实CLI profile工作区创建/恢复通过', profile_count == 2100, profile_count)
    checked('7组同seed三臂严格配对，科学固定项保持', set(normalized_by_seed) == set(range(3, 10)))
    checked('独立输出/预算账本均尚未创建', len(seen_run_dirs) == 21)
    # 新批沿用原机制；只复验与续批直接相关的批次隔离、分臂回流/恢复和额度耗尽。
    sys.path.insert(0, str(ROOT / 'custom/tests'))
    import test_timestamp_main
    suite = unittest.TestSuite(test_timestamp_main.MainTimestampTests(name) for name in (
        'test_chronological_stable_order_and_same_batch_visibility',
        'test_recirculation_and_restore_preserve_each_regime',
        'test_profile_budget_is_shared_and_exhaustion_keeps_speech'))
    stream = io.StringIO()
    result = await asyncio.to_thread(unittest.TextTestRunner(stream=stream, verbosity=2).run, suite)
    REPORT['inherited_mechanism_checks'] = {'tests_run': result.testsRun, 'log': stream.getvalue(),
                                             'failures': len(result.failures), 'errors': len(result.errors)}
    checked('同批隔离、分臂回流/恢复、共享额度耗尽定向复验通过', result.wasSuccessful() and result.testsRun == 3)
    before_path = HERE / 'tmp/seed_extension_before.json'
    # 首次任务盘点作为持久证据保存到本报告；后续重验不依赖tmp仍在。
    before = read(before_path) if before_path.exists() else read(OUTPUT)['preserved_before_sha256']
    checked('旧主批与消融已盘点资产字节保持', all(digest(ROOT / p) == h for p, h in before.items()), len(before))
    REPORT['preserved_before_sha256'] = before


def main():
    os.chdir(ROOT)
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False')
    (HERE / 'tmp').mkdir(exist_ok=True)

    def deny_network(*args, **kwargs):
        REPORT['network_connection_attempts'] += 1
        raise AssertionError('离线检查禁止网络连接')

    async def deny_llm(*args, **kwargs):
        REPORT['llm_calls'] += 1
        raise AssertionError('离线检查禁止模型调用')

    try:
        with patch.object(socket.socket, 'connect', deny_network), \
             patch.object(socket.socket, 'connect_ex', deny_network), \
             patch.object(socket, 'create_connection', deny_network):
            import litellm
            with patch.object(litellm.Router, 'acompletion', deny_llm), \
                 patch.object(litellm, 'acompletion', deny_llm):
                asyncio.run(verify())
        checked('网络与LLM尝试均为零', REPORT['network_connection_attempts'] == REPORT['llm_calls'] == 0)
        REPORT['status'] = 'passed'
    except Exception:
        REPORT['status'] = 'failed'
        REPORT['errors'].append(traceback.format_exc())
    REPORT['verifier_sha256'] = digest(Path(__file__))
    OUTPUT.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': REPORT['status'], 'windows': len(REPORT['windows']),
                      'checks': len(REPORT['checks']), 'network_attempts': REPORT['network_connection_attempts'],
                      'llm_calls': REPORT['llm_calls'], 'report': str(OUTPUT.relative_to(ROOT))}, ensure_ascii=False))
    if REPORT['status'] != 'passed':
        print(REPORT['errors'][-1], file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
