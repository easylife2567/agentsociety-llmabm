"""共享内容输入与发布前检查：时间/身份溯源、服务拒答、有限事实支持。

只处理生成消息和返回，不读推荐参数或改变选帖/回流。检查通过不等于语义金标；
可识别的风险终止发布并保留原文，不用猜测的事实替换。历史缺时刻保持未知。
"""
from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

STYLES = {
    'meme': '用轻快、幽默或反讽回应所见内容，不引入来源没有的具体事件梗。',
    'mourning': '语气克制；只有所见来源支持离世事实才表达悼念，否则回应实际所见内容。',
    'marketing': '围绕实际所见讨论介绍课程、资料或咨询，可以给出行动号召。',
    'education': '理性讨论所见教育、升学或就业观点，表达自己的立场。',
    'other': '以普通路人口吻回应实际所见内容。',
}
# 这些模式对应已发生的缺陷类型，不按Agent ID或历史问题正文建立黑名单。
AGE = re.compile(r'\d{1,3}\s*岁|[一二三四五六七八九十百两]{1,5}(?:来岁|多岁|岁|出头)')
EVENT_RELATIVE = re.compile(r'(?:昨天|明天|前天|后天|今早|明早|昨晚|今晚)[^。！？；\n]{0,20}(?:去世|离世|告别|殡仪馆|送别|葬礼|追悼|队伍)')
ELAPSED = re.compile(r'(?:\d+|[一二三四五六七八九十两]+)(?:个月|周|年|天)了')
RECENT_ACTIVITY = re.compile(r'(?:前几天|前阵子|前两天|近日)[^。！？；\n]{0,8}(?:还在讲|直播|讲课)')
HOT_STATUS = re.compile(r'(?:又)?上热搜(?:了)?|(?:登上|冲上)热搜')
REFUSAL = re.compile(r'(?:我|本模型|作为AI|作为人工智能)[^。！？\n]{0,12}(?:不能|无法|不会|不想|不愿)[^。！？\n]{0,15}(?:生成|撰写|创作|提供)[^。！？\n]{0,60}(?:内容|帖子|文本)')


def value(obj, name, default=None):
    """兼容SDK对象与结构化服务结果，不把返回对象的真值当发布成功。"""
    return obj.get(name, default) if isinstance(obj, dict) else getattr(obj, name, default)


def clock_time(t):
    """引擎无时区模拟时钟按配置的上海时间解释，不当作现实观测时刻。"""
    if isinstance(t, str):
        t = datetime.fromisoformat(t)
    return (t.replace(tzinfo=ZoneInfo('Asia/Shanghai')) if t.tzinfo is None else t).isoformat()


def prompt_context(feed, limit=5):
    """保持至多5×120字正文；稳定键和时间来自环境，未知时间不回填。"""
    context = []
    for p in feed[:max(0, min(5, limit))]:
        kind = p.get('source') or ('agent' if p.get('injection_role') == 'agent_previous_week' else 'unknown')
        context.append({'stable_key': p.get('stable_key', f"post:{p.get('post_id', '?')}"),
                        'published_at': clock_time(p.get('published_at') or p.get('event_time')) if p.get('published_at') or p.get('event_time') else None,
                        'week': p.get('week'), 'source': kind,
                        'text': str(p.get('content', '')).strip().replace('\n', ' ')[:120],
                        'author': p.get('author_handle', '?'), 'is_official': bool(p.get('is_official'))})
    return context


def messages(agent, snap, limit=5, max_chars=300):
    """把身份与来源时间送入实际请求；词库仅可选已在可见正文出现的词。"""
    context = prompt_context(snap.get('feed') or [], limit)
    lines = []
    for p in context:
        stamp = p['published_at'] or f"时间未知，仅知发布周{p['week']}"
        source = ('Agent转述（未独立核实）' if p['source'] == 'agent' else
                  '外部来源（不自动等于事实）' if p['source'] == 'external' else '来源类型未知（不可作为事实依据）')
        if p['is_official']:
            source += '；官方标记，讣告20:00为模型约定'
        lines.append(f"- [{p['stable_key']} 发布时间={stamp}；{source}] @{p['author']}：{p['text']}")
    system = (f"你扮演中文社交媒体用户。人设：{agent._persona}\n{STYLES[agent._agent_type]}\n"
              '人设年龄、职业、家庭经历只属于发言者，不是被讨论人物的事实。只回应提供的来源，'
              '不凭背景知识补年龄、近期活动、热搜或事件日期。Agent转述不能自动当成已核实事实。')
    user = (f"当前模拟行动时间={snap.get('event_time') or '未知'}。\n你看到的帖子：\n"+'\n'.join(lines)+
            '\n来源发布时间不是事件发生时间。“昨天/明天”只能按原发帖语境理解，不能照搬到当前时间；'
            '事件时间有明确依据时用绝对日期，转载/引语指代不明时不补日期或年龄，不机械换算。'
            f'请基于这些内容写不超过{max_chars}字的帖子，只输出正文；无内容时不自由补事件事实。')
    visible = '\n'.join(p['text'] for p in context)
    words = [w for w in getattr(agent, '_type_vocab', []) if w and w in visible]
    if words:
        user += '\n可自然选用来源已出现的常用词：'+'、'.join(words)
    return [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]


def assess_text(text, context):
    """有限检查：未在外部片段出现的年龄/活动/热搜，及事件日期错位风险。

    精确字符串支持只验证可见依据，不保证指代对象或外部来源真实。相对事件日期要求
    改为有据绝对日期或不补细节；不自动把它按来源发布时间换算。
    """
    # 引用服务拒答不是本人拒答；完整返回仍留在账本供人工核查。
    plain = re.sub(r"“[^”]*”|‘[^’]*’|「[^」]*」|『[^』]*』|\"[^\"]*\"|'[^']*'", '', text, flags=re.S)
    if REFUSAL.search(plain) or re.match(r'^\s*抱歉[，,。！!\s]*这个我写不了', plain):
        return 'refusal', ['service_refusal_text']
    external = '\n'.join(p['text'] for p in context if p.get('source') == 'external' or p.get('is_official'))
    checks = []
    for m in AGE.finditer(text):
        # 仅检查被讨论人物/家人的年龄；个人自述和一般教育年龄段不属于事件事实。
        before = text[max(0, m.start()-12):m.start()]
        left = re.split(r'[。！？；\n]', text[max(0, m.start()-24):m.start()])[-1]
        right = re.split(r'[。！？；\n]', text[m.end():m.end()+24])[0]
        local = left+m.group()+right
        if re.search(r'我(?:一个|今年|已经|才|现在|也)?\s*$', before):
            continue
        if not re.search(r'张雪峰|张老师|女儿|同行|他|去世|离世|走了|走得|没了|猝死|说走|这个年纪|太早|讣告|不适|抢救|人就不行|太突然|孩子还那么小', local):
            continue
        if m.group() not in external:
            checks.append('unsupported_age:'+m.group())
    # 阅读发生在昨天不等于告别仪式发生在昨天；保留作者自己的阅读经历。
    for m in EVENT_RELATIVE.finditer(text):
        if not re.search(r'看到|看见|刷到|听到|读到', m.group()):
            checks.append('event_relative_date_requires_absolute_or_omission')
    for m in ELAPSED.finditer(text):
        prefix = text[:m.start()].strip()
        local = text[max(0, m.start()-20):m.end()+20]
        event_elapsed = (not prefix or prefix == '第') and re.search(r'张雪峰|张老师|离世|去世|送他|悼念', text)
        if (event_elapsed or re.search(r'离世|去世|周年|悼念', local)) and m.group() not in external:
            checks.append('unsupported_elapsed_time:'+m.group())
    for m in RECENT_ACTIVITY.finditer(text):
        # “还在听他讲课”是读者行为，不等于人物近期仍在讲课。
        if not re.search(r'听|看|刷到|读到', m.group()) and m.group() not in external:
            checks.append('unsupported_recent_activity:'+m.group())
    if HOT_STATUS.search(text) and '热搜' not in external:
        checks.append('unsupported_hot_status')
    return ('unsupported_detail' if checks else 'accepted'), checks


def inspect_response(response, context, max_chars=400):
    """完整服务返回先检查再截断；显式拒答/过滤不因正文非空而成为正常帖子。"""
    choices = value(response, 'choices', []) or []
    choice = choices[0] if choices else {}
    message = value(choice, 'message', {}) or {}
    raw = value(message, 'content', '') or ''
    if not isinstance(raw, str):
        raise TypeError('content must be text')
    text = raw.strip().strip('"“”')
    finish = value(choice, 'finish_reason')
    refusal = value(message, 'refusal')
    if refusal or finish == 'content_filter':
        status, checks = 'refusal', ['provider_refusal' if refusal else 'content_filter']
    else:
        status, checks = assess_text(text, context) if text else ('empty', [])
    return {'generated_content': raw, 'content_status': status, 'content_checks': checks,
            'provider_refusal': refusal, 'finish_reason': finish,
            'content': text[:max_chars] if status == 'accepted' else ''}


def published_result(result):
    """只有明确成功且有ID的环境返回计为发布，路由摘要不能替代确认。"""
    if isinstance(result, dict):
        if result.get('status') == 'success' and result.get('post_id') is not None:
            return result
        for name, item in result.items():
            if name != 'variables':
                found = published_result(item)
                if found:
                    return found
    elif isinstance(result, list):
        for item in result:
            found = published_result(item)
            if found:
                return found
    return None


def ledger_summary(rows):
    """核对新账本互斥结果；保留旧账本兼容，拒答/风险不等于低效用沉默。"""
    counts, failures = {}, []
    speaking = {'content_refusal', 'content_rejected', 'generation_failed', 'publication_failed', 'published'}
    reasons = speaking | {'below_threshold', 'no_context', 'action_failed'}
    for r in rows:
        if 'content_status' not in r:
            continue
        reason = r.get('reason')
        counts[reason] = counts.get(reason, 0)+1
        if reason not in reasons:
            failures.append('unknown content outcome')
        posted = r.get('posted') is True
        if (reason == 'published') != posted or posted != (r.get('post_id') is not None):
            failures.append('publication outcome/id mismatch')
        if posted and r['content_status'] != 'accepted':
            failures.append('rejected content published')
        if reason in speaking and r.get('speak') is not True:
            failures.append('post-decision outcome without speaking intent')
        if reason == 'below_threshold' and r.get('speak') is not False:
            failures.append('threshold decision mismatch')
        if reason == 'no_context' and r.get('speak') is not None:
            failures.append('context decision mismatch')
        if reason == 'action_failed' and r.get('failure_phase') == 'before_decision' and r.get('speak') is not None:
            failures.append('pre-decision failure mismatch')
        expected = {'content_refusal': 'refusal', 'content_rejected': 'unsupported_detail',
                    'published': 'accepted', 'publication_failed': 'accepted',
                    'no_context': 'not_generated', 'below_threshold': 'not_generated'}
        if reason in expected and r['content_status'] != expected[reason]:
            failures.append('content outcome mismatch')
    # 新账本的每次行动恰属一个最终结果；外层调用数和实际请求数分别标明口径。
    return {'counts': counts, 'failures': sorted(set(failures)), 'classified_actions': sum(counts.values()),
            'speak_opportunities': sum(r.get('speak') is True for r in rows if 'content_status' in r),
            'attempts_by_scope': {scope: sum(r.get('generation_attempts', 0) for r in rows if r.get('attempt_count_scope') == scope)
                                 for scope in ('completion_calls', 'provider_requests')}}
