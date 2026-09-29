"""到达时机诊断的小时调度：确定性曝光、次周回流与可恢复的行动审计。

本组件由 CurationDynamicsSpace 显式启用，共享其判类、倾向分和效用输入，
不改变其他调度路径。时钟内部统一为上海当地无时区 datetime，日志附 +08:00。
"""
from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta, timezone

TYPES = ('meme', 'mourning', 'education', 'marketing', 'other', 'noise')
SHANGHAI = timezone(timedelta(hours=8))
OFFICIAL_TIME = datetime(2026, 3, 24, 20)


def local_time(value):
    """解析有时区时间；无时区引擎时间约定为上海当地时间。"""
    value = datetime.fromisoformat(str(value).replace('Z', '+00:00')) if not isinstance(value, datetime) else value
    return value.astimezone(SHANGHAI).replace(tzinfo=None) if value.tzinfo else value


def stamp(value):
    return local_time(value).replace(tzinfo=SHANGHAI).isoformat(timespec='seconds')


def monday(value):
    value = local_time(value)
    return value.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=value.weekday())


class ArrivalSchedule:
    """把推荐资格与推荐算法分开；所有持久动态数据集中在 state 中。"""

    def __init__(self, env, mode):
        self.e = env
        if mode not in ('preload', 'timestamp'):
            raise ValueError('arrival_mode must be preload or timestamp')
        if env._recommendation_algorithm not in ('interest', 'random'):
            raise ValueError('arrival timing supports interest/random')
        if set(env._agent_types) != set(env._chronological_action_hours):
            raise ValueError('行动表与人口不一致')
        self.mode = mode
        self.state = {'mode': mode, 'cursor': 0, 'delayed': [], 'actions': [],
                      'weeks': [], 'snapshots': {}, 'week_posts': [], 'week_start_states': {}}
        # 外部稳定键跨到达模式一致，原始周标签仅保留作审计。
        self.events = []
        self.history = []
        seen = set()
        for initial, source in ((True, env._weekly_initial_injection_by_week),
                                (False, env._injection_by_week)):
            for rows in source.values():
                for row in rows:
                    key = 'external:' + str(row['pid'])
                    if key in seen:
                        raise ValueError('重复外部源键: ' + key)
                    seen.add(key)
                    official = bool(row.get('is_official'))
                    if not row.get('published_at') and not official:
                        raise ValueError('普通帖子缺发布时间: ' + key)
                    published = OFFICIAL_TIME if official else local_time(row['published_at'])
                    available = published if initial or official or mode == 'timestamp' else monday(published)
                    item = (available, published, key, row)
                    (self.history if initial else self.events).append(item)
        self.events.sort(key=lambda x: (x[0], x[2]))
        self.history.sort(key=lambda x: x[2])

    def rng(self, aid, purpose):
        """按用途独立随机流，避免候选数或批内遍历顺序推进共同随机游标。"""
        key = f'{self.e._random_seed}|{self.e._current_week}|{aid}|{purpose}'
        return random.Random(int.from_bytes(hashlib.sha256(key.encode()).digest(), 'big'))

    def add_external(self, item, initial=False):
        e = self.e
        available, published, key, row = item
        if key in e._injected_source_keys:
            raise ValueError('重复注入: ' + key)
        pid = e._next_post_id
        e._next_post_id += 1
        content = str(row.get('content', ''))
        week = e._week_for_time(published)
        ptype = row.get('type', 'other')
        if ptype not in TYPES:
            raise ValueError('无效外部类型')
        e._posts[pid] = {
            'post_id': pid, 'stable_key': key, 'source_pid': row['pid'], 'source': 'external',
            'author_id': 'ext_' + str(row.get('author', 'unknown')),
            'author_handle': str(row.get('author', 'unknown')), 'content': content,
            'type': ptype, 'assigned_type': ptype, 'type_mismatch': False,
            'tendencies': e._compute_tendencies(content), 'week': week,
            'source_week': row.get('week'), 'available_week': e._week_for_time(available),
            'injected_week': e._current_week, 'injection_role': 'initial_history' if initial else 'window_real',
            'published_at': stamp(published), 'available_at': stamp(available),
            'event_time': stamp(published), 'is_official': bool(row.get('is_official')),
            'exposure_count': 0, 'life': 1., 'tick_produced': 0,
        }
        e._injected_source_keys.add(key)
        if not initial:
            e._injected_this_week[ptype] += 1
            e._injected_this_week_ids.append(pid)
            if row.get('is_official'):
                e._official_pinned.setdefault(week, []).append(pid)
                e._official_injected_this_week += 1

    def inject_until(self, cutoff):
        while self.state['cursor'] < len(self.events):
            item = self.events[self.state['cursor']]
            if item[0] > cutoff:
                break
            self.add_external(item)
            self.state['cursor'] += 1

    def start_week(self, week):
        """复用周聚合字段；实际注入计数从零开始，不预报未来供给。"""
        e = self.e
        e._start_chronological_week(week)
        e._injected_this_week = dict.fromkeys(TYPES, 0)
        self.state['week_posts'] = []
        # 延迟账本仅在周界释放；新帖当周从未出现在推荐池。
        retained = []
        released = set()
        for p in self.state['delayed']:
            if p['available_week'] <= week:
                e._posts[p['post_id']] = p
                released.add(p['post_id'])
            else:
                retained.append(p)
        self.state['delayed'] = retained
        e._agent_posts_pooled_prev = released

    def candidates(self):
        e = self.e
        ids = list(e._posts) if e._recommendation_algorithm == 'random' else e._live_candidates()
        return sorted(ids, key=lambda pid: e._posts[pid]['stable_key'])

    def item(self, pid):
        e = self.e
        p = e._posts[pid]
        result = e._feed_item(pid)
        result.update({k: p[k] for k in ('stable_key', 'source', 'published_at', 'available_at', 'source_week')})
        return result

    def feed(self, aid, candidates):
        e = self.e
        if e._recommendation_algorithm == 'random':
            ids = self.rng(aid, 'uniform').sample(candidates, min(e._feed_size, len(candidates)))
        else:
            ids = (e._pinned_ids + e._event_floor_ids)[:e._feed_size]
            scored = []
            for pid in candidates:
                if pid in ids:
                    continue
                p = e._posts[pid]
                # 采用同源兴趣分与softmax抽样，仅随机源与并列键独立固定。
                score = (e._alpha * p['tendencies'].get(e._agent_types[aid], 0.) + e._gamma) * e._post_vitality(pid)
                score += self.rng(aid, 'noise:' + p['stable_key']).uniform(-e._interest_noise_eps, e._interest_noise_eps)
                scored.append((score, pid))
            scored.sort(key=lambda pair: (-pair[0], e._posts[pair[1]]['stable_key']))
            n = e._feed_size - len(ids)
            if scored and n > 0:
                if e._interest_sample_temp <= 0:
                    ids += [pid for _, pid in scored[:n]]
                else:
                    # 从环境加载的共享机制取得权重，避免复制数值算法。
                    weights = e._arrival_mech.softmax_weights([s for s, _ in scored], e._interest_sample_temp)
                    ids += e._arrival_mech.weighted_sample_without_replacement(
                        [pid for _, pid in scored], weights, n, self.rng(aid, 'weighted'))
        return [self.item(pid) for pid in ids]

    def open_batch(self, event_time):
        e = self.e
        e._current_event_time = local_time(event_time)
        e._posted_this_step = set()
        hour = event_time.weekday() * 24 + event_time.hour
        e._chronological_active_agents = {aid for aid, h in e._chronological_action_hours.items() if h == hour}
        for p in e._posts.values():
            age = (monday(event_time).date() - datetime.fromisocalendar(int(p['week'][:4]), int(p['week'][-2:]), 1).date()).days // 7
            p['life'] = 2 ** (-age / e._life_half_life_weeks)
        candidates = self.candidates()
        e._feed_live_pool = len(candidates)
        e._pinned_ids, e._event_floor_ids = [], []
        if e._recommendation_algorithm == 'interest' and event_time >= OFFICIAL_TIME:
            e._pinned_ids = sorted(e._compute_pinned_ids(e._current_week), key=lambda pid: e._posts[pid]['stable_key'])
            if e._current_week == e._event_week:
                floor = [pid for pid in candidates if pid not in e._pinned_ids and e._posts[pid]['type'] != 'noise']
                floor.sort(key=lambda pid: (-e._posts[pid]['tendencies'].get('mourning', 0.), e._posts[pid]['stable_key']))
                e._event_floor_ids = floor[:e._event_week_mourning_floor]
        self.state['snapshots'] = {}
        pool_meme = sum(e._posts[pid]['type'] == 'meme' for pid in candidates)
        future = sum(local_time(e._posts[pid]['published_at']) > event_time for pid in candidates)
        if e._current_week not in self.state['week_start_states']:
            self.state['week_start_states'][e._current_week] = {
                'acted_at': stamp(event_time), 'cumulative_exposures': {a: dict(c) for a, c in e._cumulative_exposures.items()},
                'agent_supply': dict(e._total_posts_by_agent), 'candidate_keys': [e._posts[pid]['stable_key'] for pid in candidates]}
        # 全批feed装配期间不修改任何帖曝光或个人累计状态。
        for aid in sorted(e._chronological_active_agents):
            feed = self.feed(aid, candidates)
            counts = {kind: sum(p['type'] == kind for p in feed) for kind in TYPES}
            e._feeds[aid] = feed
            e._exposure_counts_tick[aid] = counts
            e._climate_shares[aid] = {kind: c / len(feed) if feed else 0. for kind, c in counts.items()}
            self.state['snapshots'][aid] = {
                'agent_id': aid, 'agent_type': e._agent_types[aid], 'week': e._current_week,
                'acted_at': stamp(event_time), 'feed': feed, 'candidate_count': len(candidates),
                'candidate_meme': pool_meme, 'candidate_future': future,
                'candidate_external': sum(e._posts[pid]['source'] == 'external' for pid in candidates),
                'lifecycle_excluded': len(e._posts) - len(candidates),
                'pinned_keys': [e._posts[p]['stable_key'] for p in e._pinned_ids],
                'floor_keys': [e._posts[p]['stable_key'] for p in e._event_floor_ids],
                'cumulative_before': dict(e._cumulative_exposures.get(aid, dict.fromkeys(TYPES, 0))),
                'injected_so_far': len(e._injected_this_week_ids),
            }

    def get_feed(self, aid):
        e = self.e
        snap = self.state['snapshots'].get(str(aid))
        if snap is None:
            return {'status': 'fail', 'reason': 'inactive agent'}
        return {'status': 'success', 'week': snap['week'], 'event_time': snap['acted_at'],
                'event_signal': {}, 'meme_env': {}, 'feed': snap['feed'],
                'own_spoke': e._spoke_this_tick.get(str(aid), False), 'own_last_post': None,
                'feed_type_distribution': e._climate_shares[str(aid)],
                'global_supply_shares': {}, 'global_exposure_shares': {},
                'personal_stats': {'cumulative_exposures': snap['cumulative_before']}}

    async def init(self, start):
        self.start_week(self.e._week_for_time(start))
        for item in self.history:
            if item[1] >= monday(start):
                raise ValueError('初始池含窗口内帖子')
            self.add_external(item, initial=True)
        self.inject_until(local_time(start))
        self.open_batch(local_time(start))

    async def finish_week(self, t):
        e = self.e
        merged = self.state['week_posts']
        e._step_index += 1
        e._meme_env = e._compute_meme_env(e._current_week)
        row = e._env_row(e._current_week, merged)
        self.state['weeks'].append(row)
        await e._write_env_state(e._step_index, t, **row)
        # 每人的气候与feed在一周只写入一次，保持其行动时刻快照。
        agent_rows = e._agent_rows(e._current_week, merged)
        for agent_row in agent_rows:
            # 行动快照不下发全局环境；效用日志中这些非决策观测回退为1。
            for field in ('meme_env_abundance_seen', 'meme_env_emptiness_seen', 'meme_env_gain_seen'):
                agent_row[field] = 1.0
        await e._write_agent_state_batch(e._step_index, t, agent_rows)

    async def step(self, tick, t):
        e = self.e
        for aid, snap in self.state['snapshots'].items():
            for item in snap['feed']:
                p = e._posts[item['post_id']]
                if local_time(p['available_at']) > local_time(snap['acted_at']):
                    raise ValueError('尚不可用帖子曝光')
                p['exposure_count'] += 1
                e._seen_by_agent.setdefault(aid, set()).add(item['post_id'])
                cum = e._cumulative_exposures.setdefault(aid, dict.fromkeys(TYPES, 0))
                cum[item['type']] += 1
                age = (monday(t).date() - datetime.fromisocalendar(int(p['week'][:4]), int(p['week'][-2:]), 1).date()).days // 7
                e._exposure_age_buckets['age3plus' if age >= 3 else f'age{age}'] += 1
            self.state['actions'].append(snap)
        # 发布成功记录与可推荐帖子分账；同周任何后续小时都不可提前读取。
        for rec in e._pending_agent_posts:
            aid = rec['agent_id']
            available = monday(t) + timedelta(days=7)
            self.state['delayed'].append({
                **rec, 'stable_key': f"agent:{aid}:{rec['week']}", 'source': 'agent',
                'author_id': aid, 'author_handle': aid, 'type': rec['pool_type'],
                'source_week': rec['week'], 'available_week': e._week_for_time(available),
                'injected_week': e._week_for_time(available), 'injection_role': 'agent_previous_week',
                'published_at': stamp(t), 'available_at': stamp(available),
                'is_official': False, 'life': 1., 'exposure_count': 0})
            self.state['week_posts'].append(rec)
            e._total_posts_by_agent[aid] = e._total_posts_by_agent.get(aid, 0) + 1
        e._pending_agent_posts = []
        e._chronological_batch_index += 1
        final = e._chronological_batch_index == e._chronological_total_batches
        next_time = local_time(t) + timedelta(seconds=tick)
        if final or e._week_for_time(next_time) != e._current_week:
            self.inject_until(monday(t) + timedelta(days=7) - timedelta(microseconds=1))
            await self.finish_week(t)
            if final:
                e._chronological_active_agents = set()
                self.state['snapshots'] = {}
                return
            self.start_week(e._week_for_time(next_time))
        self.inject_until(next_time)
        self.open_batch(next_time)
