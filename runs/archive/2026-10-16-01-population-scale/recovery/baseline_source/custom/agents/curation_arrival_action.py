"""到达时机诊断的单次行动：有限上下文生成、重试上限与确认发布。

数值效用继续调用 Agent 的同源实现；本模块只负责时间有效的提示与可审计执行。
"""
from __future__ import annotations

import fcntl
import json
import os
import time
from pathlib import Path

# 两类行动路径共用内容溯源与门控，不改变各自数值和调度机制。
import importlib.util
_spec = importlib.util.spec_from_file_location('curation_content_quality', Path(__file__).with_name('curation_content_quality.py'))
quality = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(quality)
prompt_context = quality.prompt_context
messages = quality.messages
published_result = quality.published_result


def reserve_retry(limit=440, path=None):
    """并发Worker共用内容重写/技术重试额度；上限与ledger取冻结配置。"""
    limit = int(limit)
    if limit < 0:
        raise ValueError('extra request limit must be nonnegative')
    path = path or os.environ.get('CURATION_RETRY_LEDGER')
    if not path:
        return False
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('a+') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.seek(0)
        count = int(file.read() or '0')
        if count >= limit:
            return False
        file.seek(0)
        file.truncate()
        file.write(str(count + 1))
        file.flush()
        os.fsync(file.fileno())
        return True


async def generate_once(agent, prompts):
    """复用已绑定Router与限流器，单次只发一个请求；重试由本实验显式计数。

    框架 LLMClient.call 至少内置一次重试，不能用它实现全批440次上限。
    此处沿用同一连接、token账本和限流器，只把重试放在可审计的外层。
    """
    client = agent._dispatcher
    client._ensure_runtime()
    sem = client._sem
    await sem.acquire()
    started = time.monotonic()
    failed = False
    try:
        response = await client._router.acompletion(
            model=agent._model_name, messages=prompts, stream=False,
            timeout=60, temperature=1.0, num_retries=0, caching=False)
        client._record_tokens(agent._model_name, response)
        return response
    except Exception:
        failed = True
        raise
    finally:
        sem.record_latency((time.monotonic() - started) * 1000, is_error=failed)
        await sem.release(overloaded=failed)


async def act(agent, tick, t):
    """每人每周一次，合法空feed与服务故障分别记账；重复恢复不重新采样。"""
    hour = t.weekday() * 24 + t.hour
    week = f'{t.isocalendar().year}-W{t.isocalendar().week:02d}'
    # profile 与环境配置由同一冻结表生成；只替换本周机会，不新增决策。
    overrides = getattr(agent, '_profile', {}).get('chronological_action_hour_overrides', {})
    action_hour = overrides.get(week, agent._chronological_action_hour)
    if hour != action_hour:
        return 'inactive arrival batch'
    if any(r.get('week') == week for r in agent._decision_log):
        return 'arrival decision already recorded'
    agent._step_count += 1
    row = {'week': week, 'tick': tick, 'acted_at': quality.clock_time(t), 'speak': None,
           'posted': False, 'post_id': None, 'reason': '', 'generation_attempts': 0,
           'attempt_count_scope': 'provider_requests', 'generation_status': 'not_requested', 'content_status': 'not_generated', 'generation_results': []}
    phase = 'before_decision'
    try:
        result, _ = await agent.ask_env(
            {'variables': {'agent_id': str(agent._id)}},
            "Please call get_feed() using agent_id from ctx['variables'] to get my current weekly feed snapshot.",
            readonly=True, template_mode=True)
        snap = agent._find_feed_dict(result)
        if snap is None or snap.get('week') != week:
            raise RuntimeError('feed unavailable or wrong week')
        row.update(acted_at=snap['event_time'], prompt_context=prompt_context(snap['feed']))
        if not snap['feed']:
            row.update(reason='no_context', u=None, components=None)
            return 'no_context'
        u, comps = agent._speak_stimulus(snap)
        speak = u >= agent._params['activity']
        phase = 'after_decision'
        row.update(u=u, components=comps, threshold=agent._params['activity'], speak=speak,
                   reason='speak' if speak else 'below_threshold')
        if not speak:
            return 'below_threshold'
        prompts = messages(agent, snap)
        row['messages'] = prompts
        # 三臂共用profile登记的独立ledger；未登记时保留既有诊断额度。
        budget = getattr(agent, '_profile', {}).get('content_retry_budget')
        reserve_extra = (lambda: reserve_retry(limit=budget['limit'], path=budget['ledger_path'])) if budget else reserve_retry
        await quality.prepare_publication(agent, row, lambda p: generate_once(agent, p), reserve_extra)
        content = row['content']
        phase = 'publication'
        result, _ = await agent.ask_env(
            {'variables': {'agent_id': str(agent._id), 'content': content}},
            "Please call create_post() using agent_id and content from ctx['variables'] to publish my post.",
            readonly=False, template_mode=True)
        published = published_result(result)
        row.update(content=content, posted=bool(published), reason='published' if published else 'publication_failed')
        if published:
            row['post_id'] = published['post_id']
        return row['reason']
    except Exception as exc:
        row.update(reason='publication_failed' if phase == 'publication' else 'action_failed',
                   failure_phase=phase, error_type=type(exc).__name__)
        if phase == 'before_decision':
            row.update(speak=None, u=None, components=None)
        return row['reason']
    finally:
        agent._decision_log.append(row)
