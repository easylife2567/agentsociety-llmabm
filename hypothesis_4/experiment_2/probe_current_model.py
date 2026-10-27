"""最多3次真实模型兼容性测试；复用旧提示，不运行仿真或发布帖子。

用户仅授权接口测试；通过当前.env别名核对后台返回的日期版本标识。
证据已存在时拒绝重跑，不自动重试或替换模型，不修改.env与正式账本。
"""
import asyncio
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / 'model_compatibility_probe.json'
EXPECTED = 'deepseek-v4.1-flash-20261017'
CASES = [('random', 'mourning', '2026-W13'),
         ('interest', 'meme', '2026-W22'),
         ('chronological', 'education', '2026-W14')]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(report):
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


async def main():
    if OUTPUT.exists():
        raise SystemExit('测试证据已存在；不自动重复模型请求')
    from dotenv import dotenv_values
    values = dotenv_values(ROOT / '.env')
    os.environ.update({k: str(v) for k, v in values.items() if v is not None})
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False')
    from agentsociety2.config.config import Config
    spec = importlib.util.spec_from_file_location('probe_quality', ROOT / 'custom/agents/curation_content_quality.py')
    quality = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quality)
    endpoint = urlsplit(values.get('AGENTSOCIETY_LLM_API_BASE') or '')
    old_plan = json.loads((HERE / 'runs/timestamp_v1/runtime_plan.json').read_text())
    selected = []
    for algorithm, kind, week in CASES:
        for source in sorted((HERE / f'runs/timestamp_v1/timestamp_v1_{algorithm}_s0/agents').glob('*/AGENT.json')):
            state = json.loads(source.read_text())
            if state['profile']['agent_type'] != kind:
                continue
            row = next((r for r in state['decision_log'] if r['week'] == week and r.get('posted') and r.get('messages')), None)
            if row:
                selected.append((algorithm, kind, week, source, row))
                break
    assert len(selected) == 3
    report = {
        'scope': '3条旧真实提示的接口/返回格式/有限内容门控测试，不是完整仿真或模型统计等价检验',
        'authorization': '用户2026-10-22允许测试当前模型，并接受与原模型按同一大版本系列使用',
        'execution_authorized_for_simulation': False,
        'expected_backend_model_from_user': EXPECTED,
        'requested_model_alias': Config.LLM_MODEL,
        'service_host': endpoint.hostname, 'api_path': endpoint.path,
        'old_requested_model': old_plan['model'],
        'parameters': {'temperature': 1.0, 'timeout': 60, 'num_retries': 0, 'caching': False, 'stream': False},
        'source_sha256': {str(source.relative_to(ROOT)): digest(source) for _, _, _, source, _ in selected},
        'probe_script_sha256': digest(Path(__file__)),
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'max_requests': 3, 'attempted_requests': 0, 'completed_requests': 0,
        'formal_retry_ledger_touched': False, 'cases': [], 'status': 'testing',
    }
    write(report)
    router = Config.get_router()
    router.num_retries = 0
    for algorithm, kind, week, source, old_row in selected:
        case = {'source': str(source.relative_to(ROOT)), 'algorithm': algorithm,
                'agent_type': kind, 'week': week, 'messages': old_row['messages'],
                'prompt_context': old_row['prompt_context'], 'old_response_model': old_row.get('response_model'),
                'old_generated_content': old_row.get('generated_content'), 'old_published_content': old_row.get('content')}
        report['cases'].append(case)
        report['attempted_requests'] += 1
        write(report)
        started = time.monotonic()
        try:
            response = await router.acompletion(model=Config.LLM_MODEL, messages=old_row['messages'], **report['parameters'])
            checked = quality.inspect_response(response, old_row['prompt_context'])
            candidate = quality.publication_candidate(checked, old_row['prompt_context'])
            usage = response.usage
            case.update(response_model=response.model, response_id=response.id,
                        usage=usage.model_dump() if usage else None,
                        content_checks=checked, publication_candidate=candidate,
                        response_format_compatible=True, nonempty=bool(checked['generated_content'].strip()))
            report['completed_requests'] += 1
        except Exception as exc:
            # 服务异常原文可能包含连接详情；证据只保留类型及状态码，不记录凭据。
            case.update(error_type=type(exc).__name__, status_code=getattr(exc, 'status_code', None))
            report['status'] = 'failed'
        case['elapsed_seconds'] = round(time.monotonic() - started, 3)
        write(report)
        print(json.dumps({k: case.get(k) for k in ('algorithm', 'agent_type', 'response_model', 'error_type', 'elapsed_seconds')}, ensure_ascii=False), flush=True)
        if report['status'] == 'failed':
            break
    report['expected_backend_observed'] = (report['completed_requests'] == 3 and
        all(c.get('response_model') == EXPECTED for c in report['cases']))
    report['status'] = 'passed' if (report['completed_requests'] == 3 and
        all(c.get('nonempty') and c.get('publication_candidate') for c in report['cases'])) else 'failed'
    report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    report['conclusion_limits'] = '服务兼容和少量样本检查不证明新旧权重或输出分布完全相同；保留模型日期版本及批次身份'
    write(report)
    print(json.dumps({'status': report['status'], 'requests': report['attempted_requests'],
                      'expected_backend_observed': report['expected_backend_observed'],
                      'evidence': str(OUTPUT.relative_to(ROOT))}, ensure_ascii=False))
    if report['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    asyncio.run(main())
