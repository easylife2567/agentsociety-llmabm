"""官方普通推荐验收：取消特殊槽，保留评分资格和历史兼容。

只操作正式环境的测试实例；小候选池用于证明普通槽可选中或漏读，
不把这些固定构造或全窗零生成演练当作发帖量预测。
"""
from datetime import datetime
import inspect
from pathlib import Path
import tempfile
import unittest

from test_timestamp_main import ENV, INIT, ROOT, config, make


async def event_environment(policy='ordinary'):
    """先开场，再按共同20:00门控进入事件周，官方尚未被提前注入。"""
    kwargs = dict(config()['env_modules'][0]['kwargs'])
    if policy == 'agenda':
        kwargs.pop('arrival_official_policy')
    env = ENV.CurationDynamicsSpace(**kwargs)
    await env.init(datetime(2026, 3, 16, 6))
    env._arrival.start_week('2026-W13')
    return env


class OrdinaryOfficialTests(unittest.IsolatedAsyncioTestCase):
    async def test_official_is_ordinary_in_candidate_and_feed_sampling(self):
        """实际官方不占特殊槽；固定floor时，普通抽样不使用官方标记。"""
        env = await event_environment()
        before, after = datetime(2026, 3, 24, 19), datetime(2026, 3, 25, 13)
        env._arrival.inject_until(before)
        env._arrival.open_batch(before)
        self.assertFalse(any(p['is_official'] for p in env._posts.values()))
        env._arrival.inject_until(after)
        env._arrival.open_batch(after)
        official = next(pid for pid, p in env._posts.items() if p['is_official'])
        candidates = env._arrival.candidates()
        self.assertIn(official, candidates)
        self.assertEqual(env._pinned_ids, [])
        self.assertNotIn(official, env._event_floor_ids)
        self.assertEqual(len(env._event_floor_ids), 5)
        self.assertLessEqual(env._posts[official]['available_at'], after.isoformat() + '+08:00')
        # 只切换普通评分层标记，不重建floor；官方的议程排除规则另行断言。
        original = {aid: [p['stable_key'] for p in env._arrival.feed(aid, candidates)]
                    for aid in env._agent_types}
        env._posts[official]['is_official'] = False
        comparison = {aid: [p['stable_key'] for p in env._arrival.feed(aid, candidates)]
                      for aid in env._agent_types}
        self.assertEqual(original, comparison)

    async def test_ordinary_slot_can_select_or_miss_official(self):
        """确定性小池正反例：没有把官方禁推，也不为官方保留普通槽。"""
        env = await event_environment()
        after = datetime(2026, 3, 25, 13)
        env._arrival.inject_until(after)
        env._arrival.open_batch(after)
        official = next(pid for pid, p in env._posts.items() if p['is_official'])
        other = next(pid for pid, p in env._posts.items() if not p['is_official'])
        env._feed_size, env._interest_sample_temp = 1, 0
        env._interest_noise_eps = 0
        env._pinned_ids, env._event_floor_ids = [], []
        for pid in (official, other):
            env._posts[pid].update(life=1.0, exposure_count=0)
            env._posts[pid]['tendencies'] = {'mourning': 0.0}
        env._posts[official]['tendencies']['mourning'] = 1.0
        key = env._posts[official]['stable_key']
        self.assertEqual(env._arrival.feed('70', [official, other])[0]['stable_key'], key)
        env._posts[official]['tendencies']['mourning'] = 0.0
        env._posts[other]['tendencies']['mourning'] = 1.0
        self.assertNotEqual(env._arrival.feed('70', [official, other])[0]['stable_key'], key)

    async def test_historical_agenda_and_checkpoint_policy(self):
        """默认历史路径仍置顶；ordinary恢复连续，改策略恢复明确拒绝。"""
        for policy in ('agenda', 'ordinary'):
            env = await event_environment(policy)
            after = datetime(2026, 3, 25, 13)
            env._arrival.inject_until(after)
            env._arrival.open_batch(after)
            self.assertEqual(bool(env._pinned_ids), policy == 'agenda')
            if policy == 'agenda':
                self.assertTrue(all(s['feed'][0]['is_official'] for s in env._arrival.state['snapshots'].values()))
            with tempfile.TemporaryDirectory(dir=INIT.parent / 'tmp') as folder:
                await env.to_workspace(Path(folder))
                restored = await event_environment(policy)
                self.assertTrue(await restored.restore(Path(folder)))
                self.assertEqual(restored._arrival.state, env._arrival.state)
                wrong = await event_environment('ordinary' if policy == 'agenda' else 'agenda')
                with self.assertRaisesRegex(ValueError, 'checkpoint official policy'):
                    await wrong.restore(Path(folder))
                if policy == 'agenda':
                    # 历史checkpoint缺字段时应继续以默认agenda解释。
                    import json
                    state_path = Path(folder) / 'state/ENV_STATE.json'
                    state = json.loads(state_path.read_text())
                    state.pop('_arrival_official_policy')
                    state_path.write_text(json.dumps(state))
                    self.assertTrue(await restored.restore(Path(folder)))

    def test_actual_registry_resolves_formal_modules_from_custom(self):
        """扫描真实registry后检查类源码，配置目录没有替代正式运行类。"""
        from agentsociety2.registry import (scan_and_register_custom_modules,
                                           get_registered_env_modules, get_registered_agent_modules)
        scan_and_register_custom_modules(ROOT)
        for modules, name, expected in (
            (get_registered_env_modules(), 'CurationDynamicsSpace', ROOT / 'custom/envs/curation_dynamics_space.py'),
            (get_registered_agent_modules(), 'CurationDiscourseAgent', ROOT / 'custom/agents/curation_discourse_agent.py'),
        ):
            cls = dict(modules)[name]
            self.assertEqual(Path(inspect.getfile(cls)).resolve(), expected.resolve())

    def test_invalid_or_unsupported_policy_is_rejected(self):
        """拼错策略不能静默回到置顶；常规legacy入口不接受ordinary。"""
        kwargs = config()['env_modules'][0]['kwargs']
        for changed in ({'arrival_official_policy': 'other'}, {'schedule_mode': 'legacy'}):
            with self.assertRaises(ValueError):
                ENV.CurationDynamicsSpace(**dict(kwargs, **changed))
