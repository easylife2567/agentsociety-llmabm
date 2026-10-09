"""禁网复核W13顺延、官方普通推荐及继承功能，保存可追溯的配置、源码与结果证据。

从项目根用.env解释器执行；只调用unittest与正式本地模块，不运行社会引擎。
报告中的官方阅读计数来自无Agent产出的环境演练，不是LLM实验结果。
"""
import hashlib
import importlib
import json
import os
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TESTS = ROOT / 'custom/tests'
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
sys.path.insert(0, str(TESTS))


def main():
    """拦截网络并执行正式配套功能测试，日志与重复恢复工作区仅存tmp。"""
    attempts = []
    def deny_network(*args, **kwargs):
        attempts.append('blocked connection')
        raise AssertionError('离线检查不允许网络连接')

    temporary = HERE / 'tmp'
    temporary.mkdir(exist_ok=True)
    with patch.object(socket.socket, 'connect', deny_network), \
         patch.object(socket.socket, 'connect_ex', deny_network), \
         patch.object(socket, 'create_connection', deny_network):
        suite = unittest.defaultTestLoader.discover(str(TESTS), pattern='test_*.py')
        with (temporary / 'event-week-tests.log').open('w') as log:
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        module = importlib.import_module('test_event_week_schedule')

    # 冻结当前正式实现与配置；原历史验收JSON继续作为原版本证据。
    paths = [ROOT / 'custom/envs/curation_dynamics_space.py',
             ROOT / 'custom/envs/curation_arrival_schedule.py',
             ROOT / 'custom/agents/curation_arrival_action.py',
             ROOT / 'custom/agents/curation_discourse_agent.py',
             ROOT / 'custom/agents/curation_content_quality.py',
             ROOT / 'custom/envs/curation_mechanisms.py',
             ROOT / 'custom/envs/curation_assets/vocabs.json',
             HERE / 'init/config_params.py', HERE / 'init/manifest.json',
             HERE / '2026-10-09-05-ordinary-official.patch', Path(__file__)]
    paths.extend(TESTS.glob('test_*.py'))
    manifest = json.loads((HERE / 'init/manifest.json').read_text())
    paths.extend(ROOT / name for name in manifest['output_sha256'])
    evidence = {
        'baseline_commit': module.BASELINE,
        'scope': 'W13时间覆盖、官方普通推荐与继承功能；无LLM正文，无Agent反馈产量预测',
        'tests_run': result.testsRun,
        'failures': [{'test': str(test), 'trace': trace} for test, trace in result.failures],
        'errors': [{'test': str(test), 'trace': trace} for test, trace in result.errors],
        'skipped': [{'test': str(test), 'reason': reason} for test, reason in result.skipped],
        'network_connection_attempts': len(attempts), 'llm_calls': 0,
        'event_week_checks': module.RECORD,
        'official_policy': 'ordinary',
        'patch_baseline_commit': '7adc50d08b41e1c3da26d62ec3833d9d6694ad5b',
        'execution_authorized': manifest['execution_authorized'],
        'frozen_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(set(paths))},
    }
    output = HERE / '2026-10-09-06-ordinary-official-verification.json'
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'evidence': str(output.relative_to(ROOT)), 'tests': result.testsRun,
                     'failures': len(result.failures), 'errors': len(result.errors),
                     'network_attempts': len(attempts), 'LLM_calls': 0}, ensure_ascii=False))
    if not result.wasSuccessful() or attempts:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
