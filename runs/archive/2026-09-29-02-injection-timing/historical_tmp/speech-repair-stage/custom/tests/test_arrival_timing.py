"""到达时机验收：真实冻结输入、时间边界、批次快照及恢复等价性。"""
import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / 'hypothesis_4/experiment_1/init/arrival_timing_diagnostic'

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ENV = load_module('arrival_test_env', ROOT / 'custom/envs/curation_dynamics_space.py')
ACTION = load_module('arrival_test_action', ROOT / 'custom/agents/curation_arrival_action.py')


def make(mode='timestamp', alg='interest'):
    doc = json.loads((CFG / f'arrival_timing_diagnostic_{mode}_{alg}_s0.json').read_text())
    return ENV.CurationDynamicsSpace(**doc['env_modules'][0]['kwargs'])


def feeds(env):
    return {aid: [p['stable_key'] for p in snap['feed']] for aid, snap in env._arrival.state['snapshots'].items()}


class TimingTests(unittest.IsolatedAsyncioTestCase):
    async def test_initial_and_official_boundary(self):
        for mode, count in [('timestamp', 17), ('preload', 34)]:
            e = make(mode)
            await e.init(datetime(2026, 3, 16, 6))
            self.assertEqual(len(e._posts), count)
            self.assertTrue(all(abs(p['life'] - 2 ** (-1/1.5)) < 1e-10 for p in e._posts.values() if p['injection_role'] == 'initial_history'))
            # 两条件官方时刻一致，时刻之前无置顶/保底。
            e._arrival.start_week('2026-W13')
            before = datetime(2026, 3, 24, 19)
            e._arrival.inject_until(before)
            e._arrival.open_batch(before)
            self.assertEqual(e._pinned_ids, [])
            self.assertEqual(e._event_floor_ids, [])
            after = before + timedelta(hours=1)
            e._arrival.inject_until(after)
            e._arrival.open_batch(after)
            self.assertEqual(len(e._pinned_ids), 1)

    async def test_stable_candidates_batch_order_and_delayed_posts(self):
        for alg in ('interest', 'random'):
            a, b = make('timestamp', alg), make('preload', alg)
            start = datetime(2026, 3, 16, 6)
            await a.init(start)
            await b.init(start)
            # 使候选科学内容相同，仅存储ID与插入顺序不同。
            b._posts = {pid + 1000: {**p, 'post_id': pid + 1000} for pid, p in reversed(list(a._posts.items()))}
            b._chronological_action_hours = dict(reversed(list(a._chronological_action_hours.items())))
            b._arrival.open_batch(start)
            self.assertEqual(feeds(a), feeds(b))
            self.assertTrue(all(p['exposure_count'] == 0 for p in a._posts.values()))
            aid = sorted(a._chronological_active_agents)[0]
            published = await a.create_post(aid, '关于升学选择，我想补充一个教育观点。')
            self.assertEqual(published['status'], 'success')
            again = await a.create_post(aid, '另一份内容')
            self.assertEqual(again['post_id'], published['post_id'])
            await a.step(3600, start)
            self.assertNotIn(published['post_id'], a._posts)
            self.assertEqual(len(a._arrival.state['delayed']), 1)
            a._arrival.start_week('2026-W13')
            a._arrival.open_batch(start + timedelta(days=7))
            p = a._posts[published['post_id']]
            self.assertAlmostEqual(p['life'], 2 ** (-1/1.5))
            a._arrival.open_batch(start + timedelta(days=7))
            self.assertAlmostEqual(p['life'], 2 ** (-1/1.5))

    async def test_restore_matches_uninterrupted(self):
        a = make()
        start = datetime(2026, 3, 16, 6)
        await a.init(start)
        aid = sorted(a._chronological_active_agents)[0]
        await a.create_post(aid, '我对教育话题有一点补充。')
        await a.step(3600, start)
        with tempfile.TemporaryDirectory() as directory:
            await a.to_workspace(Path(directory))
            b = make()
            self.assertTrue(await b.restore(Path(directory)))
            self.assertEqual(feeds(a), feeds(b))
            await a.step(3600, start + timedelta(hours=1))
            await b.step(3600, start + timedelta(hours=1))
            self.assertEqual(a._arrival.state, b._arrival.state)
            self.assertEqual(a._posts, b._posts)
            self.assertEqual(a._cumulative_exposures, b._cumulative_exposures)

    async def test_complete_window_and_final_arrivals(self):
        e = make()
        start = datetime(2026, 3, 16, 6)
        await e.init(start)
        hours = sorted(set(e._chronological_action_hours.values()))
        times = [datetime(2026, 3, 16) + timedelta(weeks=w, hours=h) for w in range(11) for h in hours]
        for i, t in enumerate(times):
            nxt = times[i+1] if i+1 < len(times) else datetime(2026, 6, 1)
            await e.step(int((nxt-t).total_seconds()), t)
        state = e._arrival.state
        self.assertEqual(e._chronological_batch_index, 693)
        self.assertEqual(len(state['actions']), 1100)
        self.assertEqual(len(state['weeks']), 11)
        self.assertEqual(len(e._injected_source_keys), 267)
        self.assertEqual(sum(w['injected_count'] for w in state['weeks']), 250)
        self.assertEqual(len({(r['agent_id'], r['week']) for r in state['actions']}), 1100)
        for row in state['actions']:
            self.assertTrue(all(p['published_at'] <= row['acted_at'] for p in row['feed']))
        self.assertEqual(sum(w['total_exposures'] for w in state['weeks']), sum(len(r['feed']) for r in state['actions']))

    async def test_empty_and_short_feed(self):
        e = make()
        await e.init(datetime(2026, 3, 16, 6))
        e._posts = dict(list(e._posts.items())[:2])
        e._arrival.open_batch(datetime(2026, 3, 16, 6))
        aid = sorted(e._chronological_active_agents)[0]
        snap = await e.get_feed(aid)
        self.assertEqual(len(snap['feed']), 2)
        self.assertAlmostEqual(sum(snap['feed_type_distribution'].values()), 1.)
        e._posts = {}
        e._arrival.open_batch(datetime(2026, 3, 16, 6))
        self.assertEqual((await e.get_feed(aid))['feed'], [])

    async def test_legacy_not_activated(self):
        cfg = json.loads((CFG.parent / 'configs/anchored_v1_interest_s0.json').read_text())
        e = ENV.CurationDynamicsSpace(**cfg['env_modules'][0]['kwargs'])
        await e.init(datetime(2026, 3, 16))
        self.assertIsNone(e._arrival)
        self.assertEqual(len(e._feeds), 100)
        self.assertEqual(len(e._posts), 17)

    async def test_prompt_budget_and_success_parser(self):
        e = make('preload')
        await e.init(datetime(2026, 3, 16, 6))
        snap = await e.get_feed(sorted(e._chronological_active_agents)[0])
        class Agent:
            _persona = '测试用户'
            _agent_type = 'mourning'
        prompt = ACTION.messages(Agent(), snap)
        self.assertEqual(len(ACTION.prompt_context(snap['feed'])), 5)
        self.assertNotIn('同类内容占比', str(prompt))
        self.assertNotIn('存量', str(prompt))
        self.assertIsNone(ACTION.published_result({'status': 'success', 'summary': 'done'}))
        self.assertIsNotNone(ACTION.published_result({'x': {'status': 'success', 'post_id': 1}}))

    async def test_action_failures_empty_context_and_retry(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        e = make()
        start = datetime(2026, 3, 16, 6)
        await e.init(start)
        aid = sorted(e._chronological_active_agents)[0]
        class Agent:
            _chronological_action_hour = 6
            _decision_log = []
            _step_count = 0
            _id = int(aid)
            _params = {'activity': 0.5}
            _persona = '测试用户'
            _agent_type = 'other'
            def _find_feed_dict(self, result): return result
            def _speak_stimulus(self, snap): return 1., {}
            async def ask_env(self, context, instruction, **kwargs):
                if 'get_feed' in instruction: return await e.get_feed(aid), ''
                return await e.create_post(aid, context['variables']['content']), ''
        agent = Agent()
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='我对教育有一点看法'))], model='frozen-test', usage=None)
        async def fake_generate(*args): return response
        with patch.object(ACTION, 'generate_once', fake_generate):
            self.assertEqual(await ACTION.act(agent, 3600, start), 'published')
            self.assertTrue(agent._decision_log[0]['posted'])
            await ACTION.act(agent, 3600, start)
            self.assertEqual(len(agent._decision_log), 1)
        agent._decision_log = []
        attempts = []
        async def fail_generate(*args):
            attempts.append(1)
            raise RuntimeError('frozen fake service failure')
        with patch.object(ACTION, 'generate_once', fail_generate), patch.object(ACTION, 'reserve_retry', return_value=True):
            self.assertEqual(await ACTION.act(agent, 3600, start), 'published')
            self.assertEqual(len(attempts), 2)
            self.assertTrue(agent._decision_log[0]['posted'])
            self.assertEqual(agent._decision_log[0]['content_origin'], 'fallback')
        agent._decision_log = []
        attempts.clear()
        with patch.object(ACTION, 'generate_once', fail_generate), patch.object(ACTION, 'reserve_retry', return_value=False):
            await ACTION.act(agent, 3600, start)
            self.assertEqual(len(attempts), 1)
        # 缺内容是单独的合法机会，不得触发生成或赋虚假效用零值。
        agent._decision_log = []
        e._posts = {}
        e._arrival.open_batch(start)
        self.assertEqual(await ACTION.act(agent, 3600, start), 'no_context')
        self.assertIsNone(agent._decision_log[0]['u'])

    async def test_metrics_empty_and_different_candidate_pools(self):
        audit = load_module('test_audit', ROOT / 'runs/2026-09-29-02-injection-timing/2026-09-30-02-audit.py')
        rows = [{'feed': [{'type': 'meme'}, {'type': 'other'}], 'candidate_count': 10, 'candidate_meme': 2},
                {'feed': [], 'candidate_count': 0, 'candidate_meme': 0}]
        result = audit.metrics(rows)
        self.assertEqual(result['Y'], .5)
        self.assertEqual(result['S'], .5)
        self.assertAlmostEqual(result['E'], .4)
        self.assertAlmostEqual(result['A'], .3)
        rows[0]['candidate_meme'] = 5
        self.assertEqual(audit.metrics(rows)['A'], 0.)
        self.assertIsNone(audit.metrics(rows[1:])['A'])
        self.assertEqual(audit.metrics(rows[1:])['Y'], 0.)

if __name__ == '__main__':
    unittest.main()
