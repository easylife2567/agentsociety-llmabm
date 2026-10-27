"""仅执行一次已授权的最小接口测试；不运行仿真，不发布帖子。"""
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / 'checks/model_probe_seed3_9.json'
OFFLINE = HERE / 'checks/seed3_9_offline_verification.json'
LEDGER = HERE / 'runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9/_extra_attempts.count'
EXPECTED_ALIAS = 'deepseek-v4.1-flash'
EXPECTED_RETURN = 'deepseek-v4-1-flash-261017'


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write(report):
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


async def main(correct_token_cap=False):
    global OUTPUT
    original_output = OUTPUT
    if correct_token_cap:
        first = json.loads(original_output.read_text())
        assert first['completed_requests'] == 1 and first.get('response_model') == EXPECTED_RETURN
        assert first['status'] == 'failed' and not first.get('content')
        assert first['usage']['completion_tokens'] == 8
        OUTPUT = HERE / 'checks/model_probe_seed3_9_token_cap_correction.json'
    if OUTPUT.exists():
        raise SystemExit('接口测试证据已存在；不自动重复请求')
    assert json.loads(OFFLINE.read_text())['status'] == 'passed', '先完成离线验收'
    before = LEDGER.read_bytes()
    assert before == b'0', '准备阶段独立账本应保持0'
    from dotenv import dotenv_values
    values = dotenv_values(ROOT / '.env')
    assert values.get('AGENTSOCIETY_LLM_MODEL') == EXPECTED_ALIAS
    assert values.get('AGENTSOCIETY_LLM_API_KEY')
    os.environ.update({k: str(v) for k, v in values.items() if v is not None})
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False',
                      ANONYMIZED_TELEMETRY='False')
    from agentsociety2.config.config import Config
    endpoint = urlsplit(Config.LLM_API_BASE)
    parameters = dict(max_tokens=128 if correct_token_cap else 8, temperature=1.0, timeout=60,
                      num_retries=0, caching=False, stream=False)
    report = dict(authorization='用户2026-10-24授权准备消融及最小接口测试，明确暂不启动仿真',
                  scope='一次短文本接口/返回模型核对；非仿真或正文生成实验',
                  execution_authorized_for_simulation=False, requested_model=Config.LLM_MODEL,
                  expected_response_model=EXPECTED_RETURN, service_host=endpoint.hostname,
                  api_path=endpoint.path, parameters=parameters, max_requests=1,
                  attempted_requests=0, completed_requests=0, simulation_requests=0,
                  counted_in_formal_body_budget=False, status='testing', started_at=stamp(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  token_cap_correction=correct_token_cap,
                  original_probe_record=str(original_output.relative_to(ROOT)) if correct_token_cap else None,
                  correction_reason='首个8-token探针全部用于推理而无可见正文；仅修正测试上限，非服务失败重试或仿真重跑' if correct_token_cap else None)
    # 在任何网络请求前落盘；失败或中断后不自动再试。
    with OUTPUT.open('x') as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    try:
        router = Config.get_router()
        router.num_retries = 0
        router.fallbacks = []
        report['attempted_requests'] = 1
        write(report)
        response = await router.acompletion(model=Config.LLM_MODEL,
                    messages=[{'role': 'user', 'content': '请只回复OK。'}], **parameters)
        content = response.choices[0].message.content or ''
        report.update(completed_requests=1, response_model=response.model,
                      content=content, usage=response.usage.model_dump() if response.usage else None)
        assert response.model == EXPECTED_RETURN, '实际返回模型标识变化'
        assert content.strip().strip('。.!！') == 'OK', '最小响应格式不符'
        report['status'] = 'passed'
    except Exception as exc:
        # 异常原文可能带连接信息，仅保存类型和状态码。
        report.update(status='failed', error_type=type(exc).__name__,
                      status_code=getattr(exc, 'status_code', None))
    finally:
        report['formal_ledger_unchanged'] = LEDGER.read_bytes() == before
        if not report['formal_ledger_unchanged']:
            report['status'] = 'failed'
        report['finished_at'] = stamp()
        write(report)
    print(json.dumps({k: report.get(k) for k in
                      ('status', 'attempted_requests', 'response_model', 'usage', 'formal_ledger_unchanged')},
                     ensure_ascii=False))
    if report['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--correct-token-cap', action='store_true',
                        help='仅对已记录的8-token推理截断作一次128-token探针修正，原记录不覆盖')
    args = parser.parse_args()
    asyncio.run(main(args.correct_token_cap))
