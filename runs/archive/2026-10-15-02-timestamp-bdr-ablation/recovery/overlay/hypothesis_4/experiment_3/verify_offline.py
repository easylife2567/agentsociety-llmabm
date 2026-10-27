"""九份消融的官方配置、实际Agent、全窗调度及继承功能验收。

从隔离工作区运行。网络由sitecustomize及本进程审计钩子阻断；所有正文为固定返回，
不是LLM仿真、模型质量评估或消融效应估计。不修改研究流水线。
"""
from __future__ import annotations

import argparse
import asyncio
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import importlib.util
import inspect
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import MethodType, SimpleNamespace
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INIT = HERE / 'init'
OUT = HERE / 'verification'
OUT.mkdir(exist_ok=True)
os.chdir(ROOT)
os.environ.update(MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
                  LITELLM_LOCAL_MODEL_COST_MAP='True', AGENTSOCIETY_WORKSPACE=str(ROOT), WORKSPACE_PATH=str(ROOT))
NETWORK = OUT / 'network_attempts.log'
os.environ['BDR_NETWORK_AUDIT'] = str(NETWORK)
os.environ['PYTHONPATH'] = str(HERE / 'offline_guard')
# 子进程不继承任何API凭据；工作区不放.env。
for key in list(os.environ):
    if key.endswith('API_KEY') or key.startswith('AGENTSOCIETY_LLM_'):
        os.environ.pop(key)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load('bdr_offline_guard', HERE / 'offline_guard/sitecustomize.py')


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n')


def ensure(value, message):
    if not value:
        raise AssertionError(message)


async def verify(api, agent_cls, env_cls):
    """验证真实profile加载和行为公式；无生成的全窗只用于时间/记账验收。"""
    from agentsociety2.society.cli import ExperimentRunner
    from agentsociety2.society.models import InitConfig, StepsConfig
    import yaml
    manifest = read(INIT / 'manifest.json')
    ensure(not manifest['execution_authorized'], '执行授权必须为false')
    records = []
    profiles = formulas = action_cases = fixed_responses = 0
    runner = ExperimentRunner.__new__(ExperimentRunner)
    action = load('bdr_actual_action', ROOT / 'custom/agents/curation_arrival_action.py')
    wanted = {'no_b': 'baseline_utility', 'no_d': 'spiral_scale', 'no_r': 'decay'}
    configs = sorted((INIT / 'configs').glob('*.json'))
    ensure(len(configs) == 9, '必须恰好九份配置')
    with tempfile.TemporaryDirectory(dir=HERE) as temp:
        temp = Path(temp)
        for path in configs:
            doc = read(path)
            condition = next(c for c in wanted if '_' + c + '_' in path.stem)
            seed = int(path.stem[-1])
            source = read(INIT / f'reference/timestamp_v1_interest_s{seed}.json')
            normalized = deepcopy(doc)
            env_kw = normalized['env_modules'][0]['kwargs']
            src_kw = source['env_modules'][0]['kwargs']
            for key in ('injection_data_path', 'weekly_initial_injection_data_path'):
                ensure(digest(ROOT / env_kw[key]) == digest(ROOT / src_kw[key]), key)
                env_kw[key] = src_kw[key]
            for before, after in zip(source['agents'], normalized['agents'], strict=True):
                ensure(after['kwargs']['params'][wanted[condition]] == 0.0, '未置零')
                after['kwargs']['params'][wanted[condition]] = before['kwargs']['params'][wanted[condition]]
                budget = after['kwargs']['content_retry_budget']
                ensure(budget == {'limit': 990, 'ledger_path': 'hypothesis_4/experiment_3/runs/timestamp_bdr_v1/_extra_attempts.count'}, '预算或隔离账本错误')
                budget['ledger_path'] = before['kwargs']['content_retry_budget']['ledger_path']
            ensure(normalized == source, '存在指定参数和操作路径以外差异: ' + path.name)
            parsed = InitConfig.model_validate(doc)
            steps = StepsConfig.model_validate(yaml.safe_load((INIT / f'steps_s{seed}.yaml').read_text()))
            ensure(len(steps.steps) == 693, '步骤数错误')
            # 每份配置分别经过官方check，而非只验默认首份。
            with patch.object(api, 'get_experiment_paths', return_value={
                'init_config': path, 'steps_yaml': INIT / f'steps_s{seed}.yaml'}):
                official = api.action_check(ROOT, '4', '3')
            ensure(official['success'], str(official))
            specs, name = runner._build_agent_specs([a.model_dump() for a in parsed.agents])
            ensure(name == 'CurationDiscourseAgent' and len(specs) == 100, 'CLI拆分错误')
            selected = {}
            for spec in specs:
                folder = temp / f'{path.stem}_{spec["id"]}'
                agent_cls.create(folder, spec['profile'], spec['config'])
                with patch.object(agent_cls, '_bind_services'):
                    agent = await agent_cls.from_workspace(folder, None)
                ensure(agent._params == spec['profile']['params'], 'profile参数实际加载不符')
                ensure(agent._params[wanted[condition]] == 0, '零值被默认值覆盖')
                own = agent._agent_type
                for share in (0.0, 0.2, 1.0):
                    for cumulative in (0, 15, 150):
                        snapshot = {'feed': [{'content': '固定离线素材'}], 'feed_type_distribution': {own: share},
                                    'personal_stats': {'cumulative_exposures': {own: cumulative}}}
                        utility, comp = agent._speak_stimulus(snapshot)
                        pop = doc['env_modules'][0]['kwargs']['agent_types']
                        base = sum(t == own for t in pop.values()) / 100
                        prm = agent._params
                        d = 1 + prm['spiral'] * prm['spiral_scale'] * math.tanh(1.5 * (share-base)/max(base, .05))
                        r = math.exp(-prm['decay'] * cumulative / 15)
                        expected = r*d if condition == 'no_b' else prm['baseline_utility']+r*(1-prm['baseline_utility']) if condition == 'no_d' else d
                        ensure(math.isclose(utility, expected, abs_tol=1e-12), '效用公式不符')
                        if condition == 'no_d': ensure(d == 1, 'D应恒为1')
                        if condition == 'no_r': ensure(r == 1, 'R应恒为1')
                        formulas += 1
                if own not in selected and agent._params['activity'] < 1:
                    selected[own] = (agent, folder)
                profiles += 1
            ensure(len(selected) == 5, '每条件须覆盖五类行动')
            for own, (agent, folder) in selected.items():
                moment = datetime(2026, 3, 16) + timedelta(hours=agent._chronological_action_hour)
                snapshot = {'week': '2026-W12', 'meme_env': {}, 'event_time': moment.isoformat()+'+08:00',
                    'feed': [{'stable_key': 'external:fixture', 'source': 'external',
                              'published_at': '2026-03-15T10:00:00+08:00',
                              'content': '关于教育选择，我觉得应结合自身情况认真考虑。'}],
                    'feed_type_distribution': {own: 1.0}, 'personal_stats': {'cumulative_exposures': {}}}
                env = env_cls(**doc['env_modules'][0]['kwargs'])
                await env.init(moment)
                async def ask(obj, ctx, instruction, readonly=True, **kwargs):
                    return (snapshot if readonly else await env.create_post(str(obj._id), ctx['variables']['content'])), ''
                agent.ask_env = MethodType(ask, agent)
                async def fixed_generate(obj, prompts):
                    nonlocal fixed_responses
                    fixed_responses += 1
                    return SimpleNamespace(model='offline-fixed-fixture', usage=None, choices=[SimpleNamespace(
                        finish_reason='stop', message=SimpleNamespace(content='读完这些讨论，我想先听听大家的经历，再认真考虑自己的选择。', refusal=None))])
                with patch.object(action, 'generate_once', fixed_generate):
                    outcome = await action.act(agent, 1, moment)
                    ensure(outcome == 'published', f'固定正文未实际发布 {path.stem}/{own}: {outcome}; {agent._decision_log[-1]}')
                    row = agent._decision_log[-1]
                    ensure(row['speak'] and row['posted'] and row['post_id'] is not None, '发布确认缺失')
                    ensure(await action.act(agent, 1, moment) == 'arrival decision already recorded', '重复行动未阻止')
                    await agent.to_workspace(folder)
                    with patch.object(agent_cls, '_bind_services'):
                        restored_agent = await agent_cls.from_workspace(folder, None)
                    ensure(await action.act(restored_agent, 1, moment) == 'arrival decision already recorded', 'Agent恢复后重复')
                    ensure(not action.quality.ledger_summary(agent._decision_log)['failures'], '发布记账不守恒')
                    # 空feed不调用生成，且没有发言判断；是独立行动记录，不复用已行动周。
                    agent._decision_log = []
                    snapshot['feed'] = []
                    before = fixed_responses
                    ensure(await action.act(agent, 1, moment) == 'no_context', '空feed语义错误')
                    ensure(fixed_responses == before and agent._decision_log[-1]['speak'] is None, '空feed触发生成')
                action_cases += 1
            env = env_cls(**doc['env_modules'][0]['kwargs'])
            times = [datetime(2026, 3, 16)+timedelta(weeks=w, hours=h)
                     for w in range(11) for h in sorted(set(env._chronological_action_hours.values()))]
            await env.init(times[0])
            ensure(len(env._posts) == 17, '初始历史池错误')
            empty = []
            for i, moment in enumerate(times):
                if not env._chronological_active_agents: empty.append(moment.isoformat())
                next_time = times[i+1] if i+1 < len(times) else datetime(2026, 6, 1)
                await env.step(int((next_time-moment).total_seconds()), moment)
                if i == 130:
                    checkpoint = temp / (path.stem+'_env')
                    await env.to_workspace(checkpoint)
                    restored_env = env_cls(**doc['env_modules'][0]['kwargs'])
                    ensure(await restored_env.restore(checkpoint), '环境恢复失败')
                    ensure(restored_env._arrival.state == env._arrival.state, '环境恢复时状态变化')
                elif 130 < i <= 138:
                    await restored_env.step(int((next_time-moment).total_seconds()), moment)
                    ensure(restored_env._arrival.state == env._arrival.state, '环境恢复后轨迹不一致')
                    ensure(restored_env._cumulative_exposures == env._cumulative_exposures, '恢复后累计接触不一致')
            rows = env._arrival.state['actions']
            ensure(len(rows) == len({(r['agent_id'],r['week']) for r in rows}) == 1100, '行动丢失/重复')
            ensure(len(env._arrival.state['weeks']) == 11 and env._chronological_batch_index == 693, '周/批数错误')
            ensure(empty == ['2026-03-23T18:00:00'], '空批次改变')
            ensure(len(env._injected_source_keys) == 267, '窗口注入未排空')
            ensure(sum(w['injected_count'] for w in env._arrival.state['weeks']) == 250, '真实帖注入数错误')
            for row in rows:
                ensure(row['candidate_future'] == 0, '存在未来候选')
                ensure(not row['pinned_keys'], '官方被置顶')
                ensure(all(p['available_at'] <= row['acted_at'] and p['published_at'] <= row['acted_at'] for p in row['feed']), '未来曝光')
                ensure(all(not p['is_official'] or p['stable_key'] not in row['floor_keys'] for p in row['feed']), '官方进入保底')
            mourning = [r for r in rows if r['week']=='2026-W13' and r['agent_type']=='mourning']
            ensure(len(mourning)==22 and all(r['acted_at']>'2026-03-24T20:00:00+08:00' for r in mourning), 'W13顺延丢失')
            ensure(sum(w['total_exposures'] for w in env._arrival.state['weeks']) == sum(len(r['feed']) for r in rows), '曝光不守恒')
            records.append({'run_id':path.stem,'official_check':official,'batches':693,'unique_actions':1100,
                'weeks':11,'future_exposures':0,'w13_mourning_after_official':22,
                'environment_restore_equal':True,'scope':'无Agent生成回流的调度功能演练'})
    return {'windows':records,'actual_profiles':profiles,'synthetic_formula_checks':formulas,
            'fixed_publication_and_empty_feed_cases':action_cases,'fixed_responses':fixed_responses}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['setup','generate','verify'])
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    # 导入前网络钩子已生效；Provider入口额外封锁，不能把误调用吞成兜底通过。
    import litellm
    calls = []
    async def forbid_provider(*a, **kw):
        calls.append('provider_call_blocked')
        raise RuntimeError('真实LLM调用在离线验收中被禁止')
    from agentsociety2.registry import scan_and_register_custom_modules, get_registered_agent_modules, get_registered_env_modules
    scan_and_register_custom_modules(ROOT)
    agents = dict(get_registered_agent_modules()); envs = dict(get_registered_env_modules())
    agent_cls, env_cls = agents['CurationDiscourseAgent'], envs['CurationDynamicsSpace']
    locations = {'agent':str(Path(inspect.getfile(agent_cls)).resolve()),'env':str(Path(inspect.getfile(env_cls)).resolve())}
    ensure(all(Path(p).is_relative_to(ROOT/'custom') for p in locations.values()), '加载了隔离区外模块')
    api = load('bdr_official_config', ROOT/'.claude/skills/agentsociety-experiment-config/scripts/config.py')
    api._ensure_agentsociety2()
    with patch.object(litellm, 'acompletion', forbid_provider), patch.object(litellm.Router, 'acompletion', forbid_provider):
        if args.phase in ('setup','generate'):
            actions = ('validate','info') if args.phase == 'setup' else ('prepare','run','check')
            result = {}
            for name in actions:
                item = getattr(api,'action_'+name)(ROOT,'4','3')
                write(OUT/(name+'.json'),item)
                ensure(item.get('success',True), str(item))
                result[name] = {'success':True}
        else:
            result = asyncio.run(verify(api,agent_cls,env_cls))
            write(OUT/'bdr-functional.json', result)
            # 复用已冻结基线的内容修复、共同时间和官方普通推荐检查，不携入主工作区测试差异。
            for fixture in read(HERE/'test_inputs/manifest.json')['files']:
                source = HERE/'test_inputs'/fixture['fixture']
                ensure(digest(source) == fixture['sha256'], '历史测试输入哈希不符')
                target = ROOT/fixture['target']
                ensure(target.resolve().is_relative_to(ROOT), '历史测试输入目标越界')
                if target.exists():
                    ensure(digest(target) == fixture['sha256'], '历史测试输入目标已存在不同内容')
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
            sys.path.insert(0,str(ROOT/'custom/tests'))
            suite = unittest.defaultTestLoader.loadTestsFromNames([
                'test_timestamp_main','test_event_week_schedule','test_ordinary_official','test_content_quality'])
            (ROOT/'hypothesis_4/experiment_2/tmp').mkdir(exist_ok=True)
            with (OUT/'inherited-tests.log').open('w') as log:
                tests = unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
            result['inherited_tests'] = {'run':tests.testsRun,'failures':len(tests.failures),'errors':len(tests.errors),'skipped':len(tests.skipped)}
            ensure(tests.wasSuccessful(), '继承功能检查失败，见inherited-tests.log')
        ensure(not calls, '出现真实Provider调用尝试')
        ensure(not NETWORK.exists() or not NETWORK.read_text(), '出现网络尝试')
        result.update(success=True,phase=args.phase,loaded_modules=locations,provider_calls=0,network_attempts=0,
                      llm_execution_authorized=False,scope='配置与固定返回离线功能验收')
        write(OUT/(args.phase+'.json'),result)
        print(json.dumps({'phase':args.phase,'success':True,'actual_profiles':result.get('actual_profiles'),
                          'windows':len(result.get('windows',[])),'inherited_tests':result.get('inherited_tests'),
                          'network_attempts':0,'LLM_calls':0},ensure_ascii=False))


if __name__ == '__main__':
    main()
