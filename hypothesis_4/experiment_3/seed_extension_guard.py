"""新增21次消融的预算/截止边界；只作检查，不启动或恢复实验。"""
from datetime import datetime, timedelta


def check_limits(budget, *, started_at, now, body_requests, extra_requests, active_runs):
    """未来控制器须传入首次正式启动时间及含失败尝试的累计用量。"""
    assert budget['max_wall_hours'] == 48
    assert budget['max_agent_body_requests'] == 25410
    assert budget['extra_requests_limit'] == 2310
    if not 0 <= body_requests <= 25410:
        raise RuntimeError('正文累计请求超过25410上限')
    if not 0 <= extra_requests <= 2310:
        raise RuntimeError('共享额外请求超过2310上限')
    if not 0 <= active_runs <= 2:
        raise RuntimeError('最多允许两路活动引擎')
    if started_at is None:
        if body_requests or extra_requests or active_runs:
            raise RuntimeError('准备阶段不得产生仿真用量或引擎')
        return None
    start = datetime.fromisoformat(started_at)
    deadline = start + timedelta(hours=48)
    if now >= deadline:
        raise RuntimeError('首次正式启动起48小时保护上限已到')
    if now < start:
        raise RuntimeError('核对时刻早于正式启动')
    return deadline
