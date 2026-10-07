"""内容修复功能验收：历史必查样本、真实行动入口及无网络的环境账本。

服务返回用固定完整正文替代，不验证模型重新生成的质量；旧结果只读。
"""
import importlib.util
import json
import os
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from types import MethodType, SimpleNamespace
import unittest
from unittest.mock import patch

os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT/'runs/2026-09-29-02-injection-timing'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


QUALITY = load('content_test_quality', 'custom/agents/curation_content_quality.py')
AGENT = load('content_test_agent', 'custom/agents/curation_discourse_agent.py').CurationDiscourseAgent
ACTION = load('content_test_arrival', 'custom/agents/curation_arrival_action.py')
ENV = load('content_test_env', 'custom/envs/curation_dynamics_space.py')
FIXTURES = json.loads((TASK/'2026-10-07-02-content-acceptance-fixtures.json').read_text())['records']


def response(text, refusal=None, finish='stop'):
    return SimpleNamespace(model='offline-fixture', usage=None, choices=[SimpleNamespace(
        finish_reason=finish, message=SimpleNamespace(content=text, refusal=refusal))])


class FakeAgent:
    """仅代替服务与路由，数值与生成模板调用实际实现。"""
    def __init__(self, sample, outputs, env=None, publication_success=True):
        self.sample, self.outputs, self.env = sample, deque(outputs), env
        self._id = str(sample['review']['agent_id'])
        self._agent_type = sample['profile']['agent_type']
        self._params = sample['profile']['params']
        self._persona = sample['profile']['persona']
        self._type_vocab = []
        self._config = {'max_content_chars': 300, 'feed_context_n': 5}
        self._chronological_action_hour = None
        self._decision_log, self._step_count, self.writes, self.requests = [], 0, 0, 0
        self.publication_success = publication_success
        self._speak_stimulus = MethodType(AGENT._speak_stimulus, self)
        self._content_messages = MethodType(AGENT._content_messages, self)
        self.name = 'offline-test'

    def get_profile(self):
        return {'arrival_timing': False}

    def _find_feed_dict(self, result):
        return result

    async def acompletion(self, prompts):
        self.requests += 1
        value = self.outputs.popleft()
        if isinstance(value, Exception):
            raise value
        return value

    async def ask_env(self, ctx, instruction, readonly=True, **kwargs):
        if readonly:
            return (await self.env.get_feed(self._id) if self.env else self.sample['snapshot']), ''
        self.writes += 1
        if self.env:
            return await self.env.create_post(self._id, ctx['variables']['content']), ''
        return ({'status': 'success', 'post_id': 123} if self.publication_success else {'status': 'fail'}), ''


class ContentTests(unittest.IsolatedAsyncioTestCase):
    async def test_twenty_historical_cases_on_both_actual_paths(self):
        self.assertEqual(len(FIXTURES), 20)
        for sample in FIXTURES:
            for arrival in (False, True):
                with self.subTest(run=sample['review']['run_id'], aid=sample['review']['agent_id'], arrival=arrival):
                    fake = FakeAgent(sample, [response(sample['decision']['content']), response('看完这些讨论，我想认真听听不同人的经历，再说说自己的想法。')])
                    t = datetime.fromisoformat(sample['decision']['acted_at'])
                    if arrival:
                        fake._chronological_action_hour = t.weekday()*24+t.hour
                        async def generate(agent, prompts):
                            return await agent.acompletion(prompts)
                        with patch.object(ACTION, 'generate_once', generate), patch.object(ACTION, 'reserve_retry', return_value=True):
                            result = await ACTION.act(fake, 0, t)
                    else:
                        result = await AGENT.step(fake, 0, t)
                    expected = 'published'
                    self.assertEqual(result, expected)
                    row = fake._decision_log[-1]
                    self.assertTrue(row['speak'])
                    self.assertTrue(row['posted'])
                    self.assertIsNotNone(row['post_id'])
                    self.assertEqual(fake.writes, 1)
                    self.assertEqual(fake.requests, 2 if sample['review']['verdict'] == 'service_refusal' else 1)
                    self.assertEqual(row['generation_results'][0]['generated_content'], sample['decision']['content'])
                    self.assertEqual(row['content_status'], 'accepted')
                    self.assertEqual(QUALITY.assess_text(row['content'], row['prompt_context'])[0], 'accepted')
                    self.assertEqual(row['content_origin'], 'model_rewrite' if sample['review']['verdict'] == 'service_refusal' else 'local_detail_repair')
                    if sample['review']['verdict'] == 'service_refusal':
                        self.assertEqual(row['generation_results'][1]['purpose'], 'rewrite')
                        self.assertEqual(len(row['generation_results'][1]['messages']), 3)
                    if row['content_origin'] == 'local_detail_repair':
                        self.assertTrue(row['detail_edits'])
                        self.assertGreater(len(row['content']), len(sample['decision']['content'])*0.7)
                    self.assertFalse(QUALITY.ledger_summary(fake._decision_log)['failures'])
                    self.assertIn('只属于发言者', row['messages'][0]['content'])
                    for p in row['prompt_context']:
                        self.assertIn(p['published_at'], row['messages'][1]['content'])
                        self.assertLessEqual(len(p['text']), 120)
                    # 相对日期具体实例同时展示来源和行动时间，而非机械日期替换。
                    if sample['review']['agent_id'] in (56, 43):
                        self.assertIn(sample['decision']['acted_at'], row['messages'][1]['content'])

    def test_legitimate_views_quotes_and_supported_facts_survive(self):
        context = [{'source': 'external', 'text': '张老师41岁，女儿11岁。3月28日举行告别仪式。'}]
        for text in ('我不认同这些说法，不该玩这个梗。', '我无法核实这条消息。',
                     '他引用了“抱歉，这个我写不了”，这不代表我的观点。',
                     '张老师41岁，女儿11岁。', '我今年39岁，觉得身体比工作重要。',
                     '3月28日的告别仪式让人难过。', '昨天看到苏州殡仪馆外的送别队伍。',
                     '前阵子还在听他讲课，现在整理笔记。', '前几天还刷到他直播，感慨万千。', '四月了，该定方向了。',
                     '孩子暑假躺平两个月了。', '我一个五十来岁开店的，身体得顾好。',
                     '别把十八岁的一次选择当成终身判决。', '19岁自由职业也有自己的焦虑。', '张老师这波是懂配方的。19岁自由职业算提前退休还是待充值？那我17岁打工算啥。',
                     '他引用了‘抱歉，这个我写不了’，这不代表我的观点。'):
            self.assertEqual(QUALITY.inspect_response(response(text), context)['content_status'], 'accepted', text)
        self.assertEqual(QUALITY.inspect_response(response('正文', refusal='service refusal'), context)['content_status'], 'refusal')
        self.assertEqual(QUALITY.inspect_response(response('正文', finish='content_filter'), context)['content_status'], 'refusal')
        # 服务拒答在400字之后，仍必须先检查完整返回，不能先截断绕过门控。
        text = '普通观点。'*100+'我不能生成关于真实人物生死的内容。'
        self.assertEqual(QUALITY.inspect_response(response(text), context)['content_status'], 'refusal')

    def test_unknown_historical_time_is_not_fabricated(self):
        agent = FakeAgent(FIXTURES[0], [])
        snap = {'event_time': '2026-04-04T16:00:00+08:00', 'feed': [
            {'post_id': 1, 'week': '2026-W13', 'content': '明天告别仪式', 'source': 'agent', 'event_time': None}]}
        message = QUALITY.messages(agent, snap)[1]['content']
        self.assertIn('时间未知，仅知发布周2026-W13', message)
        self.assertNotIn('发布时间=2026-04-04', message)
        snap['feed'][0].update(source='external', published_at='2026-03-27T10:00:00')
        self.assertIn('2026-03-27T10:00:00+08:00', QUALITY.messages(agent, snap)[1]['content'])

    def test_inconsistent_ledgers_are_rejected(self):
        good = dict(reason='published', posted=True, post_id=1, speak=True,
                    content_status='accepted', generation_attempts=1, attempt_count_scope='completion_calls')
        for overrides in (dict(posted=False, post_id=None), dict(reason='below_threshold'),
                          dict(reason='content_refusal'), dict(content_status='refusal')):
            self.assertTrue(QUALITY.ledger_summary([{**good, **overrides}])['failures'])
        self.assertFalse(QUALITY.ledger_summary([good])['failures'])
        self.assertEqual(QUALITY.ledger_summary([good])['attempts_by_scope']['completion_calls'], 1)

    async def test_technical_retry_then_refusal_keeps_attempts(self):
        fake = FakeAgent(FIXTURES[-1], [TimeoutError(), response(FIXTURES[-1]['decision']['content'])])
        t = datetime.fromisoformat(FIXTURES[-1]['decision']['acted_at'])
        fake._chronological_action_hour = t.weekday()*24+t.hour
        async def generate(agent, prompts):
            return await agent.acompletion(prompts)
        with patch.object(ACTION, 'generate_once', generate), patch.object(ACTION, 'reserve_retry', return_value=True) as retry:
            self.assertEqual(await ACTION.act(fake, 0, t), 'published')
            self.assertEqual(fake._decision_log[0]['generation_attempts'], 2)
            retry.assert_called_once()
            self.assertEqual(await ACTION.act(fake, 0, t), 'arrival decision already recorded')
            self.assertEqual(fake.requests, 2)
            self.assertEqual(fake.writes, 1)
            self.assertEqual(fake._decision_log[0]['content_origin'], 'fallback')

    async def test_failure_accounting_and_publication_confirmation(self):
        cases = [(response(''), True, 'published'),
                 (TimeoutError(), True, 'published'),
                 (response('我不认同这些观点。'), False, 'publication_failed'),
                 (response('我不认同这些观点。'), True, 'published')]
        t = datetime.fromisoformat(FIXTURES[0]['decision']['acted_at'])
        for generated, success, reason in cases:
            fake = FakeAgent(FIXTURES[0], [generated], publication_success=success)
            self.assertEqual(await AGENT.step(fake, 0, t), reason)
            self.assertFalse(QUALITY.ledger_summary(fake._decision_log)['failures'])
            self.assertEqual(await AGENT.step(fake, 0, t), 'decision already recorded')
        bad = FakeAgent(FIXTURES[0], [])
        bad.sample = {**bad.sample, 'snapshot': {}}
        self.assertEqual(await AGENT.step(bad, 0, t), 'action_failed')
        self.assertIsNone(bad._decision_log[0]['speak'])
        bad.sample = {**bad.sample, 'snapshot': {**FIXTURES[0]['snapshot'], 'feed': []}}
        bad._decision_log = []
        self.assertEqual(await AGENT.step(bad, 0, t), 'no_context')
        self.assertEqual(bad.requests, 0)

    async def test_actual_detail_repairs_keep_referents_and_punctuation(self):
        # 原始具体样本约束局部编辑的语义；不是只复检同一正则。
        for aid, week in ((50, '2026-W14'), (64, '2026-W13'), (66, '2026-W13'), (74, '2026-W13'), (97, '2026-W13')):
            if aid == 50:
                path = ROOT/'hypothesis_4/experiment_1/runs/arrival_timing_diagnostic/arrival_timing_diagnostic_timestamp_random_s0/agents/agent_0050/AGENT.json'
                decision = next(d for d in json.loads(path.read_text())['decision_log'] if d['week']==week)
                text, _, _ = QUALITY.repair_details(decision['content'], [])
                self.assertNotIn('第。', text)
            else:
                sample = next(x for x in FIXTURES if x['review']['agent_id']==aid and x['review']['week']==week)
                text, edits, _ = QUALITY.repair_details(sample['decision']['content'], QUALITY.prompt_context(sample['snapshot']['feed']))
                self.assertTrue(edits)
                self.assertNotIn('，。', text)
                if aid == 66:
                    self.assertIn('这场离别太突然了', text)
                if aid == 74:
                    self.assertIn('这场离别来得太突然了', text)
                if aid == 97:
                    self.assertNotIn('同岁', text)
        fake = FakeAgent(FIXTURES[0], [TimeoutError(), response('我不认同这些观点。')])
        t = datetime.fromisoformat(FIXTURES[0]['decision']['acted_at'])
        self.assertEqual(await AGENT.step(fake, 0, t), 'published')
        row = fake._decision_log[0]
        self.assertEqual(row['content_origin'], 'model_retry')
        self.assertEqual(row['generation_results'][1]['purpose'], 'technical_retry')
        self.assertEqual(row['generation_results'][0]['messages'], row['generation_results'][1]['messages'])

    async def test_refusal_filter_and_budget_exhaustion_keep_one_post(self):
        # 模型拒答、过滤、空返回以及技术故障不再取消已经决定的发言。
        for first in (response('正文', refusal='refusal'), response('正文', finish='content_filter'), response(''), TimeoutError()):
            fake = FakeAgent(FIXTURES[-1], [first])
            t = datetime.fromisoformat(FIXTURES[-1]['decision']['acted_at'])
            fake._chronological_action_hour = t.weekday()*24+t.hour
            async def generate(agent, prompts):
                return await agent.acompletion(prompts)
            with patch.object(ACTION, 'generate_once', generate), patch.object(ACTION, 'reserve_retry', return_value=False):
                self.assertEqual(await ACTION.act(fake, 0, t), 'published')
            self.assertEqual(fake.requests, 1)
            self.assertEqual(fake.writes, 1)
            self.assertEqual(fake._decision_log[0]['content_origin'], 'fallback')
            self.assertFalse(QUALITY.ledger_summary(fake._decision_log)['failures'])
        for kind in QUALITY.STYLES:
            agent = SimpleNamespace(_agent_type=kind)
            result = QUALITY.fallback_content(agent, [{'source': 'agent', 'text': '大家各有不同感受。'}])
            self.assertEqual(QUALITY.assess_text(result['content'], [])[0], 'accepted')
            self.assertTrue(result['content'])

    async def test_real_environment_exposure_inventory_and_recirculation(self):
        cfg = json.loads((ROOT/'hypothesis_4/experiment_1/init/arrival_timing_diagnostic/arrival_timing_diagnostic_timestamp_interest_s0.json').read_text())
        env = ENV.CurationDynamicsSpace(**cfg['env_modules'][0]['kwargs'])
        t = datetime(2026, 3, 16, 6)
        await env.init(t)
        aid = sorted(env._chronological_active_agents)[0]
        sample = {**FIXTURES[-1], 'review': {**FIXTURES[-1]['review'], 'agent_id': aid}}
        fake = FakeAgent(sample, [response(sample['decision']['content'])], env=env)
        fake._chronological_action_hour = t.weekday()*24+t.hour
        fake._speak_stimulus = lambda snap: (1., {})
        next_id = env._next_post_id
        async def generate(agent, prompts):
            return await agent.acompletion(prompts)
        with patch.object(ACTION, 'generate_once', generate):
            self.assertEqual(await ACTION.act(fake, 0, t), 'published')
        self.assertEqual(env._next_post_id, next_id+1)
        self.assertEqual(len(env._pending_agent_posts), 1)
        pid = env._pending_agent_posts[0]['post_id']
        self.assertEqual(fake._decision_log[0]['content_origin'], 'fallback')
        await env.step(3600, t)
        self.assertEqual(sum(env._cumulative_exposures[aid].values()), len(env._arrival.state['actions'][0]['feed']))
        self.assertNotIn(pid, env._posts)
        self.assertTrue(any(p['post_id'] == pid for p in env._arrival.state['delayed']))
        # 正常正文仍交给原环境；不把内容修复变成回流规则修改。
        normal = ENV.CurationDynamicsSpace(**cfg['env_modules'][0]['kwargs'])
        await normal.init(t)
        result = await normal.create_post(aid, '升学选择值得认真讨论。')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(normal._pending_agent_posts[-1]['pool_type'], normal._agent_types[aid])
        await normal.step(3600, t)
        self.assertNotIn(result['post_id'], normal._posts)
        self.assertTrue(any(p['post_id'] == result['post_id'] for p in normal._arrival.state['delayed']))


if __name__ == '__main__':
    unittest.main()
