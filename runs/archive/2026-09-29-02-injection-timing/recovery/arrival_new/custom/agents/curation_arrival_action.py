"""到达时机诊断的单次行动：有限上下文生成、重试上限与确认发布。

数值效用继续调用 Agent 的同源实现；本模块只负责时间有效的提示与可审计执行。
"""
from __future__ import annotations

import fcntl
import json
import os
import time
from pathlib import Path

STYLES = {
    'meme': '用轻快、幽默或反讽的口吻回应所见内容，不凭空引入具体事件梗。',
    'mourning': '语气克制、重视情感。仅在所见内容支持离世事实时回应悼念，否则回应实际所见内容。',
    'marketing': '围绕所见讨论介绍课程、资料或咨询服务，可以给出行动号召。',
    'education': '理性讨论所见内容中的教育、升学或就业观点，有明确立场。',
    'other': '以普通路人的口吻回应所见内容，表达日常看法。',
}


def prompt_context(feed):
    """实际生成上下文固定最多五条、每条120字，并记录稳定来源键。"""
    return [{'stable_key': p['stable_key'], 'published_at': p['published_at'],
             'text': str(p.get('content', '')).strip().replace('\n', ' ')[:120],
             'author': p.get('author_handle', '?'), 'is_official': p.get('is_official', False)}
            for p in feed[:5]]


def messages(agent, snap):
    context = prompt_context(snap['feed'])
    lines = '\n'.join(f"- {'【官方】' if p['is_official'] else ''}@{p['author']}：{p['text']}" for p in context)
    return [
        {'role': 'system', 'content': f'你扮演中文社交媒体用户。人设：{agent._persona}\n{STYLES[agent._agent_type]}\n只回应提供的帖子，不凭自己的背景知识补充未出现的事件事实。'},
        {'role': 'user', 'content': f"当前模拟时间为{snap['event_time']}。你看到的帖子：\n{lines}\n请基于这些内容写不超过300字的帖子，只输出正文。"}]


def reserve_retry():
    """并发Worker共享额外生成次数；仅失败重试使用，全批最多440次。"""
    path = os.environ.get('CURATION_RETRY_LEDGER')
    if not path:
        return False
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('a+') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.seek(0)
        count = int(file.read() or '0')
        if count >= 440:
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


def published_result(value):
    """仅接受环境明确成功且返回帖子ID；路由摘要不等于发布成功。"""
    if isinstance(value, dict):
        if value.get('status') == 'success' and value.get('post_id') is not None:
            return value
        for key, item in value.items():
            if key != 'variables':
                result = published_result(item)
                if result:
                    return result
    elif isinstance(value, list):
        for item in value:
            result = published_result(item)
            if result:
                return result
    return None


async def act(agent, tick, t):
    """每人每周一次，合法空feed与服务故障分别记账；重复恢复不重新采样。"""
    hour = t.weekday() * 24 + t.hour
    if hour != agent._chronological_action_hour:
        return 'inactive arrival batch'
    week = f'{t.isocalendar().year}-W{t.isocalendar().week:02d}'
    if any(r.get('week') == week for r in agent._decision_log):
        return 'arrival decision already recorded'
    agent._step_count += 1
    row = {'week': week, 'tick': tick, 'acted_at': t.isoformat(), 'speak': False,
           'posted': False, 'reason': '', 'generation_attempts': 0}
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
        row.update(u=u, components=comps, threshold=agent._params['activity'], speak=speak,
                   reason='speak' if speak else 'below_threshold')
        if not speak:
            return 'below_threshold'
        prompts = messages(agent, snap)
        row['messages'] = prompts
        content = ''
        for attempt in range(2):
            if attempt and not reserve_retry():
                break
            row['generation_attempts'] += 1
            try:
                response = await generate_once(agent, prompts)
                content = (response.choices[0].message.content or '').strip().strip('"“”')[:400]
                row['response_model'] = getattr(response, 'model', None)
                usage = getattr(response, 'usage', None)
                row['usage'] = usage.model_dump() if hasattr(usage, 'model_dump') else None
                if content:
                    break
            except Exception as exc:
                row['generation_error'] = type(exc).__name__
        if not content:
            row['reason'] = 'generation_failed'
            return 'generation_failed'
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
        row.update(reason='action_failed', error_type=type(exc).__name__)
        return 'action_failed'
    finally:
        agent._decision_log.append(row)
