"""W13共同顺延验收：局部时间覆盖、实际行动入口与冻结配置。

环境全窗只累计曝光，不生成模型正文；CLI解析和Agent工作区使用正式实现。
RECORD保存数值检查摘要供实验验收记录引用，不作为闭环仿真结果。
"""
from copy import deepcopy
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import tempfile
from types import MethodType
import unittest
from unittest.mock import patch

from test_timestamp_main import ACTION, CONTENT_TEST, ENV, INIT, ROOT, config, make, times

BASELINE = '1539418abf98800d4a3284317c68e8e5ff91319f'
OVERRIDES = {'70': 61, '21': 67, '22': 96, '20': 113, '56': 166}
WEEK = '2026-W13'
OFFICIAL = '2026-03-24T20:00:00+08:00'
RECORD = {'windows': [], 'parsed_profiles': 0}


class EventWeekTests(unittest.IsolatedAsyncioTestCase):
    def test_only_five_weekly_opportunities_change(self):
        """逐配置对照Git基线，确保没有顺便改变人口、公式参数、feed或步骤。"""
        for seed in range(3):
            for algorithm in ('random', 'chronological', 'interest'):
                path = f'hypothesis_4/experiment_2/init/configs/timestamp_v1_{algorithm}_s{seed}.json'
                before = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT))
                after = deepcopy(config(algorithm, seed))
                env = after['env_modules'][0]['kwargs']
                self.assertEqual(env.pop('arrival_official_policy'), 'ordinary')
                self.assertEqual(env.pop('chronological_action_hour_overrides'), {WEEK: OVERRIDES})
                changed = []
                for agent in after['agents']:
                    aid = str(agent['agent_id'])
                    entry = agent['kwargs'].pop('chronological_action_hour_overrides', None)
                    if entry is not None:
                        changed.append(aid)
                        self.assertEqual(entry, {WEEK: OVERRIDES[aid]})
                self.assertEqual(set(changed), set(OVERRIDES))
                self.assertEqual(after, before)
            step_path = f'hypothesis_4/experiment_2/init/steps_s{seed}.yaml'
            self.assertEqual((ROOT / step_path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASELINE}:{step_path}'], cwd=ROOT))

    async def test_nine_windows_cover_all_mourning_agents_after_official(self):
        """逐条核验1100机会与22人事件后时刻；三臂官方都没有强制槽。"""
        RECORD['windows'] = []
        for seed in range(3):
            for algorithm in ('random', 'chronological', 'interest'):
                env = make(algorithm, seed)
                schedule = times(env)
                await env.init(schedule[0])
                empty = []
                for i, moment in enumerate(schedule):
                    if not env._chronological_active_agents:
                        empty.append(moment.isoformat())
                    following = schedule[i + 1] if i + 1 < len(schedule) else datetime(2026, 6, 1)
                    await env.step(int((following - moment).total_seconds()), moment)
                rows = env._arrival.state['actions']
                self.assertEqual(len(rows), 1100)
                self.assertEqual(len({(r['agent_id'], r['week']) for r in rows}), 1100)
                self.assertEqual(env._chronological_batch_index, 693)
                self.assertEqual(len(env._arrival.state['weeks']), 11)
                self.assertEqual(empty, ['2026-03-23T18:00:00'])
                for row in rows:
                    aid = row['agent_id']
                    moment = datetime.fromisoformat(row['acted_at'])
                    expected = OVERRIDES[aid] if row['week'] == WEEK and aid in OVERRIDES else env._chronological_action_hours[aid]
                    self.assertEqual(moment.weekday() * 24 + moment.hour, expected)
                    self.assertLessEqual(len(row['feed']), 10)
                    self.assertEqual(row['candidate_future'], 0)
                    self.assertTrue(all(p['available_at'] <= row['acted_at'] and
                                        p['published_at'] <= row['acted_at'] for p in row['feed']))
                    if algorithm != 'interest':
                        self.assertEqual(row['pinned_keys'], [])
                        self.assertEqual(row['floor_keys'], [])
                mourning = [r for r in rows if r['week'] == WEEK and r['agent_type'] == 'mourning']
                self.assertEqual(len(mourning), 22)
                self.assertTrue(all(r['acted_at'] > OFFICIAL for r in mourning))
                seen = [r for r in mourning if any(p['is_official'] for p in r['feed'])]
                if algorithm == 'interest':
                    for row in rows:
                        self.assertEqual(row['pinned_keys'], [])
                        official = [p for p in row['feed'] if p['is_official']]
                        self.assertLessEqual(len(official), 1)
                        self.assertTrue(all(p['stable_key'] not in row['floor_keys'] for p in official))
                        self.assertEqual([p['stable_key'] for p in ACTION.prompt_context(row['feed'])],
                                         [p['stable_key'] for p in row['feed'][:5]])
                RECORD['windows'].append({'algorithm': algorithm, 'seed': seed,
                    'batches': 693, 'unique_actions': 1100, 'weeks': 11,
                    'mourning_after_official': 22, 'mourning_official_in_feed': len(seen),
                    'future_exposures': 0, 'empty_batches': empty,
                    'scope': '无Agent生成与回流的环境功能演练'})

    async def test_actual_cli_profiles_and_agent_workspaces_preserve_overrides(self):
        """正式schema、CLI profile拆分及900个Agent工作区读取均不丢覆盖字段。"""
        from agentsociety2.registry import scan_and_register_custom_modules
        from agentsociety2.society.cli import ExperimentRunner
        scan_and_register_custom_modules(ROOT)
        count = 0
        with tempfile.TemporaryDirectory(dir=INIT.parent / 'tmp') as folder:
            runner = ExperimentRunner.__new__(ExperimentRunner)
            for seed in range(3):
                for algorithm in ('random', 'chronological', 'interest'):
                    parsed = runner._load_config(INIT / f'configs/timestamp_v1_{algorithm}_s{seed}.json')
                    specs, name = runner._build_agent_specs([a.model_dump() for a in parsed.agents])
                    self.assertEqual(name, 'CurationDiscourseAgent')
                    self.assertEqual(len(specs), 100)
                    for spec in specs:
                        path = Path(folder) / str(count)
                        cls = CONTENT_TEST.AGENT
                        cls.create(path, spec['profile'], spec['config'])
                        with patch.object(cls, '_bind_services'):
                            agent = await cls.from_workspace(path, None)
                        aid = str(agent._id)
                        expected = {WEEK: OVERRIDES[aid]} if aid in OVERRIDES else {}
                        self.assertEqual(agent._profile.get('chronological_action_hour_overrides', {}), expected)
                        self.assertEqual(agent._chronological_action_hour,
                                         parsed.env_modules[0].kwargs['chronological_action_hours'][aid])
                        count += 1
        self.assertEqual(count, 900)
        RECORD['parsed_profiles'] = count

    async def test_actual_action_gate_and_restored_decision_do_not_repeat(self):
        """五人的旧小时关闭、新小时正常判定；W12/W14回原小时，恢复不再决策。"""
        cls = CONTENT_TEST.AGENT
        for aid, new_hour in OVERRIDES.items():
            profile = next(a['kwargs'] for a in config()['agents'] if str(a['agent_id']) == aid)
            with tempfile.TemporaryDirectory(dir=INIT.parent / 'tmp') as folder:
                path = Path(folder)
                cls.create(path, profile, {})
                with patch.object(cls, '_bind_services'):
                    agent = await cls.from_workspace(path, None)
                # 门槛设为极大值仅用于避免模型调用，效用仍执行正式数值函数。
                agent._params['activity'] = 1e9
                active_time = None
                async def fake_env(obj, context, instruction, **kwargs):
                    self.assertIn('get_feed', instruction)
                    week = f'{active_time.isocalendar().year}-W{active_time.isocalendar().week:02d}'
                    return {'week': week, 'meme_env': {}, 'event_time': active_time.isoformat() + '+08:00',
                        'feed': [{'stable_key': 'external:test', 'content': '关注教育话题。',
                                  'published_at': '2026-03-15T10:00:00+08:00'}],
                        'feed_type_distribution': {'education': 1.0},
                        'personal_stats': {'cumulative_exposures': {}}}, ''
                agent.ask_env = MethodType(fake_env, agent)
                for week_index in (0, 1, 2):
                    monday = datetime(2026, 3, 16) + timedelta(weeks=week_index)
                    old = monday + timedelta(hours=agent._chronological_action_hour)
                    if week_index == 1:
                        self.assertEqual(await ACTION.act(agent, 1, old), 'inactive arrival batch')
                        active_time = monday + timedelta(hours=new_hour)
                    else:
                        active_time = old
                    self.assertEqual(await ACTION.act(agent, 1, active_time), 'below_threshold')
                self.assertEqual(len(agent._decision_log), 3)
                await agent.to_workspace(path)
                with patch.object(cls, '_bind_services'):
                    restored = await cls.from_workspace(path, None)
                self.assertEqual(await ACTION.act(restored, 1, active_time), 'arrival decision already recorded')
                self.assertEqual(len(restored._decision_log), 3)

    async def test_w13_restore_equivalence_and_mismatched_schedule_rejected(self):
        """W13已进入覆盖时段后恢复，状态/曝光一致；换表恢复明确失败。"""
        for algorithm in ('random', 'chronological', 'interest'):
            env = make(algorithm)
            schedule = times(env)
            await env.init(schedule[0])
            cut = schedule.index(datetime(2026, 3, 25, 13))
            for i in range(cut):
                await env.step(int((schedule[i + 1] - schedule[i]).total_seconds()), schedule[i])
            with tempfile.TemporaryDirectory(dir=INIT.parent / 'tmp') as folder:
                await env.to_workspace(Path(folder))
                restored = make(algorithm)
                self.assertTrue(await restored.restore(Path(folder)))
                wrong = deepcopy(config(algorithm)['env_modules'][0]['kwargs'])
                wrong.pop('chronological_action_hour_overrides')
                with self.assertRaisesRegex(ValueError, 'checkpoint action overrides'):
                    await ENV.CurationDynamicsSpace(**wrong).restore(Path(folder))
                for i in range(cut, cut + 8):
                    seconds = int((schedule[i + 1] - schedule[i]).total_seconds())
                    await env.step(seconds, schedule[i])
                    await restored.step(seconds, schedule[i])
                self.assertEqual(env._arrival.state, restored._arrival.state)
                self.assertEqual(env._cumulative_exposures, restored._cumulative_exposures)

    def test_invalid_override_does_not_silently_drop_an_opportunity(self):
        """未知Agent、窗口外周、无step小时及非arrival入口不能接受覆盖。"""
        base = config()['env_modules'][0]['kwargs']
        for entry in ({WEEK: {'999': 61}}, {'2026-W23': {'70': 61}}, {WEEK: {'70': 0}}):
            with self.assertRaises(ValueError):
                ENV.CurationDynamicsSpace(**dict(base, chronological_action_hour_overrides=entry))
        # 单独核验周时刻覆盖，避免普通官方的入口约束先于本约束触发。
        legacy = dict(base, schedule_mode='legacy')
        legacy.pop('arrival_official_policy')
        with self.assertRaisesRegex(ValueError, 'require arrival_timing'):
            ENV.CurationDynamicsSpace(**legacy)
