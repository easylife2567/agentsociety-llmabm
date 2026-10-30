"""统一回流的离线功能验收；固定测试正文，不启动社会引擎或调用模型。"""

from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
os.environ['MEM0_TELEMETRY'] = 'False'
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / 'hypothesis_4/experiment_2/init'
NETWORK_ATTEMPTS = []


def reject_network(*args, **kwargs):
    NETWORK_ATTEMPTS.append(repr(args[1:] if len(args) > 1 else args))
    raise AssertionError('小时回流功能验收禁止网络连接')


# 导入阶段同样禁网，避免依赖库尝试下载模型价格表或发送遥测。
with patch('socket.socket.connect', reject_network), patch('socket.create_connection', reject_network):
    spec = importlib.util.spec_from_file_location(
        'hourly_return_test_env', ROOT / 'custom/envs/curation_dynamics_space.py')
    ENV = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ENV)


def make(algorithm='interest', policy='next_batch'):
    doc = json.loads((INIT / f'configs/timestamp_v1_{algorithm}_s0.json').read_text())
    kwargs = doc['env_modules'][0]['kwargs']
    if policy is not None:
        kwargs['arrival_agent_return_policy'] = policy
    return ENV.CurationDynamicsSpace(**kwargs)


def times(env):
    hours = sorted(set(env._chronological_action_hours.values()))
    return [datetime(2026, 3, 16) + timedelta(weeks=week, hours=hour)
            for week in range(11) for hour in hours]


def snapshots(env):
    return deepcopy(env._arrival.state['snapshots'])


async def advance(env, schedule, index):
    moment = schedule[index]
    following = schedule[index + 1] if index + 1 < len(schedule) else datetime(2026, 6, 1)
    await env.step(int((following - moment).total_seconds()), moment)


class HourlyReturnTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.network_guard = patch('socket.socket.connect', reject_network)
        self.connection_guard = patch('socket.create_connection', reject_network)
        self.network_guard.start()
        self.connection_guard.start()
        self.addCleanup(self.network_guard.stop)
        self.addCleanup(self.connection_guard.stop)

    def tearDown(self):
        self.assertEqual(NETWORK_ATTEMPTS, [], '包括导入期在内不得尝试联网')

    def test_policy_is_explicit_and_restricted_to_arrival(self):
        for algorithm in ('random', 'interest', 'chronological'):
            self.assertTrue(make(algorithm)._agent_return_next_batch)
            legacy = make(algorithm, None)
            self.assertEqual(legacy._arrival_agent_return_policy, 'legacy')
            self.assertEqual(legacy._agent_return_next_batch, algorithm == 'chronological')
        with self.assertRaisesRegex(ValueError, 'arrival_agent_return_policy'):
            make(policy='unknown')
        with self.assertRaisesRegex(ValueError, 'requires arrival_timing'):
            ENV.CurationDynamicsSpace(arrival_agent_return_policy='next_batch')

    async def test_all_regimes_freeze_same_hour_and_pool_at_batch_end(self):
        """至少两位同行动者共享旧快照；新帖只需取得资格，不要求被抽中。"""
        for algorithm in ('random', 'interest', 'chronological'):
            with self.subTest(algorithm=algorithm):
                env = make(algorithm)
                schedule = times(env)
                grouped = Counter(env._chronological_action_hours.values())
                index = next(i for i, moment in enumerate(schedule[:63])
                             if grouped[moment.weekday() * 24 + moment.hour] >= 2)
                await env.init(schedule[index])
                before = snapshots(env)
                cumulative_before = deepcopy(env._cumulative_exposures)
                aids = sorted(env._chronological_active_agents)[:2]
                published = []
                for aid in aids:
                    result = await env.create_post(aid, '教育选择应结合个人兴趣与实际情况。')
                    self.assertEqual(result['status'], 'success')
                    self.assertIn('下一小时批次', result['response'])
                    published.append(result['post_id'])
                    self.assertNotIn(result['post_id'], env._posts)
                again = await env.create_post(aids[0], '同小时的第二次调用。')
                self.assertTrue(again['already_posted'])
                self.assertEqual(again['post_id'], published[0])
                self.assertEqual(snapshots(env), before)
                self.assertEqual(env._cumulative_exposures, cumulative_before)
                self.assertTrue(all(post['exposure_count'] == 0 for post in env._posts.values()))
                await advance(env, schedule, index)
                self.assertEqual(env._arrival.state['delayed'], [])
                candidates = set(env._arrival.candidates())
                self.assertTrue(set(published) <= candidates)
                for pid in published:
                    post = env._posts[pid]
                    self.assertEqual(post['published_at'], post['available_at'])
                    self.assertEqual(post['available_week'], '2026-W12')
                    self.assertEqual(post['injected_week'], '2026-W12')
                    self.assertEqual(post['injection_role'], 'agent_prior_batch')
                    self.assertEqual(post['life'], 1.0)
                    self.assertEqual(post['exposure_count'], 0)

    async def test_legacy_random_interest_still_wait_for_next_week(self):
        for algorithm in ('random', 'interest'):
            with self.subTest(algorithm=algorithm):
                env = make(algorithm, None)
                schedule = times(env)
                await env.init(schedule[0])
                aid = sorted(env._chronological_active_agents)[0]
                result = await env.create_post(aid, '这是固定的离线教育观点。')
                self.assertIn('下一周', result['response'])
                for index in range(62):
                    await advance(env, schedule, index)
                    self.assertNotIn(result['post_id'], env._posts)
                await advance(env, schedule, 62)
                self.assertIn(result['post_id'], env._posts)
                post = env._posts[result['post_id']]
                self.assertEqual(post['available_week'], '2026-W13')
                self.assertAlmostEqual(post['life'], 2 ** (-1 / 1.5))
                self.assertEqual(env._arrival.state['delayed'], [])

    async def test_restore_matches_continuous_execution(self):
        for algorithm in ('random', 'interest', 'chronological'):
            with self.subTest(algorithm=algorithm):
                env = make(algorithm)
                schedule = times(env)
                await env.init(schedule[0])
                aid = sorted(env._chronological_active_agents)[0]
                await env.create_post(aid, '希望大家充分了解教育信息后再选择。')
                await advance(env, schedule, 0)
                with tempfile.TemporaryDirectory() as directory:
                    await env.to_workspace(Path(directory))
                    state = json.loads((Path(directory) / ENV._STATE_REL).read_text())
                    self.assertEqual(state['_arrival_agent_return_policy'], 'next_batch')
                    restored = make(algorithm)
                    self.assertTrue(await restored.restore(Path(directory)))
                    self.assertEqual(snapshots(env), snapshots(restored))
                    await advance(env, schedule, 1)
                    await advance(restored, schedule, 1)
                    self.assertEqual(env._arrival.state, restored._arrival.state)
                    self.assertEqual(env._posts, restored._posts)
                    self.assertEqual(env._cumulative_exposures, restored._cumulative_exposures)
                    with self.assertRaisesRegex(ValueError, 'return policy'):
                        await make(algorithm, 'legacy').restore(Path(directory))

    async def test_old_checkpoint_missing_policy_remains_legacy(self):
        for algorithm in ('random', 'interest', 'chronological'):
            with self.subTest(algorithm=algorithm):
                env = make(algorithm, None)
                await env.init(times(env)[0])
                with tempfile.TemporaryDirectory() as directory:
                    await env.to_workspace(Path(directory))
                    path = Path(directory) / ENV._STATE_REL
                    state = json.loads(path.read_text())
                    state.pop('_arrival_agent_return_policy')
                    path.write_text(json.dumps(state))
                    restored = make(algorithm, None)
                    self.assertTrue(await restored.restore(Path(directory)))
                    self.assertEqual(restored._arrival.state, env._arrival.state)
                    with self.assertRaisesRegex(ValueError, 'return policy'):
                        await make(algorithm).restore(Path(directory))

    async def test_complete_windows_conserve_supply_and_unique_actions(self):
        """固定正文走环境入池，不运行Agent/LLM；包含周末和窗口末批。"""
        for algorithm in ('random', 'interest', 'chronological'):
            with self.subTest(algorithm=algorithm):
                env = make(algorithm)
                schedule = times(env)
                await env.init(schedule[0])
                produced = []
                for index, moment in enumerate(schedule):
                    if index in (0, 1, 62, 63, 125, 692):
                        aid = sorted(env._chronological_active_agents)[0]
                        result = await env.create_post(aid, '教育话题需要兼顾信息和个人选择。')
                        self.assertFalse(result['already_posted'])
                        produced.append(result['post_id'])
                    await advance(env, schedule, index)
                state = env._arrival.state
                self.assertEqual(env._chronological_batch_index, 693)
                self.assertEqual(len(state['actions']), 1100)
                self.assertEqual(len({(row['agent_id'], row['week']) for row in state['actions']}), 1100)
                self.assertEqual(len(state['weeks']), 11)
                self.assertEqual(len(produced), 6)
                self.assertEqual(sum(row['agent_supply'] for row in state['weeks']), len(produced))
                self.assertEqual(state['weeks'][-1]['agent_supply'], 1)
                self.assertEqual(len(env._injected_source_keys), 267)
                self.assertEqual(sum(row['injected_count'] for row in state['weeks']), 250)
                self.assertEqual(state['delayed'], [])
                self.assertTrue(set(produced) <= set(env._posts))
                self.assertEqual(sum(post['source'] == 'agent' for post in env._posts.values()), 6)
                for row in state['weeks']:
                    self.assertEqual(env._flow_by_week[row['week']], row['injected_count'] + row['agent_supply'])
                for row in state['actions']:
                    self.assertEqual(row['candidate_future'], 0)
                    self.assertTrue(all(post['published_at'] <= row['acted_at'] and
                                        post['available_at'] <= row['acted_at'] for post in row['feed']))
                    self.assertLessEqual(len(row['feed']), 10)
                self.assertEqual(sum(row['total_exposures'] for row in state['weeks']),
                                 sum(len(row['feed']) for row in state['actions']))

    async def test_chronological_new_policy_preserves_legacy_dynamics(self):
        """同一固定供给逐批比较；策略声明不同不应改变已有时序动力学。"""
        legacy, unified = make('chronological', None), make('chronological')
        schedule = times(legacy)
        await legacy.init(schedule[0])
        await unified.init(schedule[0])
        for index, moment in enumerate(schedule):
            self.assertEqual(snapshots(legacy), snapshots(unified))
            if index % 49 == 0 or index == 692:
                aid = sorted(legacy._chronological_active_agents)[0]
                old = await legacy.create_post(aid, '这是一份固定的教育讨论观点。')
                new = await unified.create_post(aid, '这是一份固定的教育讨论观点。')
                self.assertEqual(old, new)
            await advance(legacy, schedule, index)
            await advance(unified, schedule, index)
        self.assertEqual(legacy._arrival.state, unified._arrival.state)
        self.assertEqual(legacy._posts, unified._posts)
        self.assertEqual(legacy._cumulative_exposures, unified._cumulative_exposures)
        self.assertEqual(legacy._flow_by_week, unified._flow_by_week)


if __name__ == '__main__':
    unittest.main()
