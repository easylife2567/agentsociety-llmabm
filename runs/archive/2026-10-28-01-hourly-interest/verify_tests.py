"""在指定隔离工作区运行回归及新回流功能检查；全程禁止网络。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import unittest
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    output = args.output.resolve()
    assets = Path(__file__).resolve().parent / 'fixtures'
    provenance = json.loads((assets / 'provenance.json').read_text())
    fixture = assets / 'historical_content_sample.json'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == provenance['fixture_sha256']
    target = workspace / provenance['restored_test_path']
    assert target.resolve().is_relative_to(workspace)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fixture, target)
    else:
        # 主工作区的完整历史记录也可满足同一条内容断言，不覆盖它。
        expected = json.loads(fixture.read_text())['decision_log'][0]
        assert expected in [dict(week=r['week'], content=r['content'])
                            for r in json.loads(target.read_text())['decision_log']
                            if r.get('week') == expected['week']]
    (workspace / 'hypothesis_4/experiment_2/tmp').mkdir(exist_ok=True)
    os.chdir(workspace)
    os.environ.update(WORKSPACE_PATH=str(workspace), MEM0_TELEMETRY='False',
                      ANONYMIZED_TELEMETRY='False', LITELLM_LOCAL_MODEL_COST_MAP='True')
    attempts = []

    def blocked(*args, **kwargs):
        attempts.append('blocked socket call')
        raise RuntimeError('offline test forbids network')

    names = ('test_arrival_timing.py', 'test_content_quality.py', 'test_timestamp_main.py',
             'test_event_week_schedule.py', 'test_ordinary_official.py', 'test_hourly_return.py')
    with patch.object(socket.socket, 'connect', blocked), \
            patch.object(socket.socket, 'connect_ex', blocked), \
            patch.object(socket, 'create_connection', blocked):
        loader = unittest.TestLoader()
        suite = unittest.TestSuite(loader.discover('custom/tests', pattern=name) for name in names)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = dict(tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                   skipped=len(result.skipped), network_attempts=len(attempts), llm_calls=0,
                   scientific_simulation_started=False, workspace=str(workspace))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(not result.wasSuccessful() or bool(attempts))


if __name__ == '__main__':
    main()
