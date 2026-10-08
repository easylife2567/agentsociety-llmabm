"""timestamp主实验功能验收：九配置、真实时钟、分臂回流与共享请求额度。

只使用正式环境和固定测试正文，不调用LLM；全窗演练验证运行完整性，
不把测试文字或零生成的产量当作科研预测。
"""
import asyncio
import importlib.util
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT/'hypothesis_4/experiment_2/init'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ENV = load('main_timestamp_env', 'custom/envs/curation_dynamics_space.py')
ACTION = load('main_timestamp_action', 'custom/agents/curation_arrival_action.py')
CONTENT_TEST = load('main_content_fixtures', 'custom/tests/test_content_quality.py')


def config(algorithm='interest', seed=0):
    return json.loads((INIT/f'configs/timestamp_v1_{algorithm}_s{seed}.json').read_text())


def make(algorithm='interest', seed=0):
    return ENV.CurationDynamicsSpace(**config(algorithm, seed)['env_modules'][0]['kwargs'])


def times(env):
    hours = sorted(set(env._chronological_action_hours.values()))
    return [datetime(2026, 3, 16)+timedelta(weeks=w, hours=h) for w in range(11) for h in hours]


def keys(env):
    return {aid: [p['stable_key'] for p in snap['feed']]
            for aid, snap in env._arrival.state['snapshots'].items()}


class MainTimestampTests(unittest.IsolatedAsyncioTestCase):
    def test_paired_matrix_and_input_hashes(self):
        """人口/参数/时刻/样本配对，推荐制度仍是唯一分臂配置键。"""
        import hashlib
        manifest = json.loads((INIT/'manifest.json').read_text())
        self.assertEqual(len(manifest['runs']), 9)
        for seed in range(3):
            docs = [config(a, seed) for a in ('interest', 'random', 'chronological')]
            self.assertTrue(all(d['agents'] == docs[0]['agents'] for d in docs))
            normalized = []
            for doc in docs:
                kwargs = dict(doc['env_modules'][0]['kwargs'])
                kwargs.pop('recommendation_algorithm')
                normalized.append(kwargs)
                self.assertTrue(all(a['kwargs']['arrival_timing'] for a in doc['agents']))
                self.assertTrue(all(a['kwargs']['content_retry_budget']['limit'] == 990 for a in doc['agents']))
            self.assertTrue(all(k == normalized[0] for k in normalized))
        for path, expected in manifest['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), expected, path)

    async def test_nine_complete_windows_have_no_future_exposure(self):
        """无生成演练仍走真实到达、周末排空、曝光累计与周写入路径。"""
        for seed in range(3):
            for algorithm in ('interest', 'random', 'chronological'):
                with self.subTest(seed=seed, algorithm=algorithm):
                    env = make(algorithm, seed)
                    schedule = times(env)
                    await env.init(schedule[0])
                    self.assertEqual(len(env._posts), 17)
                    for i, moment in enumerate(schedule):
                        following = schedule[i+1] if i+1 < len(schedule) else datetime(2026, 6, 1)
                        await env.step(int((following-moment).total_seconds()), moment)
                    state = env._arrival.state
                    self.assertEqual(env._chronological_batch_index, len(schedule))
                    self.assertEqual(len(state['actions']), 1100)
                    self.assertEqual(len(state['weeks']), 11)
                    self.assertEqual(len({(r['agent_id'], r['week']) for r in state['actions']}), 1100)
                    self.assertEqual(len(env._injected_source_keys), 267)
                    self.assertEqual(sum(w['injected_count'] for w in state['weeks']), 250)
                    for row in state['actions']:
                        self.assertEqual(row['candidate_future'], 0)
                        self.assertTrue(all(p['published_at'] <= row['acted_at'] and
                                            p['available_at'] <= row['acted_at'] for p in row['feed']))
                    self.assertEqual(sum(w['total_exposures'] for w in state['weeks']),
                                     sum(len(r['feed']) for r in state['actions']))

    async def test_chronological_stable_order_and_same_batch_visibility(self):
        env, reordered = make('chronological'), make('chronological')
        first = times(env)[0]
        await env.init(first)
        await reordered.init(first)
        reordered._posts = {pid+1000: {**p, 'post_id': pid+1000}
                            for pid, p in reversed(list(env._posts.items()))}
        # 把全部发布时间设成并列，直接验收稳定键而非存储顺序破并列。
        for obj in (env, reordered):
            for p in obj._posts.values():
                p['published_at'] = '2026-03-15T10:00:00+08:00'
            obj._arrival.open_batch(first)
        self.assertEqual(keys(env), keys(reordered))
        aid = sorted(env._chronological_active_agents)[0]
        before = keys(env)
        posted = await env.create_post(aid, '看完教育话题，想补充一个选择专业的观点。')
        self.assertNotIn(posted['post_id'], env._posts)
        self.assertEqual(keys(env), before)
        next_moment = times(env)[1]
        await env.step(int((next_moment-first).total_seconds()), first)
        self.assertIn(posted['post_id'], env._posts)
        stable = f"agent:{aid}:2026-W12"
        self.assertTrue(any(stable in feed for feed in keys(env).values()))
        self.assertEqual(env._arrival.state['delayed'], [])

    async def test_recirculation_and_restore_preserve_each_regime(self):
        for algorithm in ('interest', 'random', 'chronological'):
            env = make(algorithm)
            schedule = times(env)
            await env.init(schedule[0])
            aid = sorted(env._chronological_active_agents)[0]
            posted = await env.create_post(aid, '我觉得教育选择需要结合个人实际情况。')
            await env.step(int((schedule[1]-schedule[0]).total_seconds()), schedule[0])
            self.assertEqual(posted['post_id'] in env._posts, algorithm == 'chronological')
            with tempfile.TemporaryDirectory() as directory:
                await env.to_workspace(Path(directory))
                restored = make(algorithm)
                self.assertTrue(await restored.restore(Path(directory)))
                await env.step(int((schedule[2]-schedule[1]).total_seconds()), schedule[1])
                await restored.step(int((schedule[2]-schedule[1]).total_seconds()), schedule[1])
                self.assertEqual(env._arrival.state, restored._arrival.state)
                self.assertEqual(env._posts, restored._posts)
            if algorithm != 'chronological':
                for i in range(2, 63):
                    await env.step(int((schedule[i+1]-schedule[i]).total_seconds()), schedule[i])
                self.assertIn(posted['post_id'], env._posts)
                self.assertEqual(env._posts[posted['post_id']]['available_week'], '2026-W13')

    async def test_chronological_weekly_supply_flow_is_conserved(self):
        """时序帖当周入池，跨周观测只计本周新增供给，stock按窗口累积。"""
        env = make('chronological')
        schedule = times(env)
        await env.init(schedule[0])
        published = []
        for i, moment in enumerate(schedule[:126]):
            if i in (0, 1, 63):
                aid = sorted(env._chronological_active_agents)[0]
                result = await env.create_post(aid, '我想分享对教育选择的一点看法。')
                published.append(result['post_id'])
            await env.step(int((schedule[i+1]-moment).total_seconds()), moment)
        self.assertEqual(len(env._arrival.state['weeks']), 2)
        for week, count in (('2026-W12', 2), ('2026-W13', 1)):
            row = next(r for r in env._arrival.state['weeks'] if r['week'] == week)
            self.assertEqual(env._flow_by_week[week], row['injected_count']+count)
            self.assertEqual(row['agent_supply'], count)
        # W13存量窗口覆盖这两周；实际发布ID均在池内且不会被周计数重复累计。
        self.assertTrue(all(pid in env._posts for pid in published))
        self.assertEqual(env._meme_env['stock'], sum(env._flow_by_week.values()))

    async def test_profile_budget_is_shared_and_exhaustion_keeps_speech(self):
        """测试配置额度从profile进入真实生成路径，三臂共用一个ledger。"""
        sample = CONTENT_TEST.FIXTURES[0]
        with tempfile.TemporaryDirectory() as directory:
            ledger = str(Path(directory)/'extra.count')
            for algorithm in ('interest', 'random', 'chronological'):
                agent = CONTENT_TEST.FakeAgent(sample, [RuntimeError('offline service failure'),
                                                      CONTENT_TEST.response('看完讨论，我想听听大家的教育选择经历。')])
                agent._profile = {'content_retry_budget': {'limit': 2, 'ledger_path': ledger}}
                agent._params = {'activity': 0.0}
                agent._speak_stimulus = lambda snap: (1., {})
                moment = datetime.fromisoformat(sample['snapshot']['event_time'])
                agent._chronological_action_hour = moment.weekday()*24+moment.hour
                async def generate(obj, prompts):
                    return await obj.acompletion(prompts)
                with patch.object(ACTION, 'generate_once', generate):
                    self.assertEqual(await ACTION.act(agent, 0, moment), 'published')
                self.assertEqual(agent.requests, 2 if algorithm != 'chronological' else 1)
                self.assertTrue(agent._decision_log[0]['posted'])
                self.assertEqual(agent.writes, 1)
                if algorithm == 'chronological':
                    self.assertEqual(agent._decision_log[0]['content_origin'], 'fallback')
            self.assertEqual(Path(ledger).read_text(), '2')
            self.assertFalse(ACTION.reserve_retry(limit=2, path=ledger))
        # 旧未传预算时的440上限仍兼容既有冻结诊断。
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory)/'old.count'
            ledger.write_text('439')
            with patch.dict(os.environ, {'CURATION_RETRY_LEDGER': str(ledger)}):
                self.assertTrue(ACTION.reserve_retry())
                self.assertFalse(ACTION.reserve_retry())


if __name__ == '__main__':
    unittest.main()
