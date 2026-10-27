"""在另一个干净基线worktree核验恢复；不依赖原workspace和原始工作簿。

恢复窗口汇总，并复算current/double_stress的interest s0两个冻结条件。
语义比较完整1100行动与周汇总；gzip文件时间戳不属于科学数据。
"""
import argparse
import asyncio
import gzip
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def decompressed_sha(path):
    with gzip.open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


async def main(task, restored_root):
    dest = task / 'tmp/recovery-output'
    dest.mkdir()
    shutil.copytree(task / 'frozen', dest / 'frozen')
    for name in ('experiment_manifest.json', 'experiment_protocol.md', 'calibration_experiments.py'):
        shutil.copyfile(task / name, dest / name)
    runner = load('restored_calibration_runner', dest / 'calibration_experiments.py')
    manifest = read(dest / 'experiment_manifest.json')
    assert all(runner.sha(restored_root / p) == h for p, h in manifest['code_sha256'].items())
    assert all(runner.sha(dest / 'frozen' / p) == h for p, h in manifest['frozen_inputs_sha256'].items())
    assert runner.sha(dest / 'frozen/observations.json') == manifest['aggregate_sha256']
    assert runner.sha(dest / 'calibration_experiments.py') == manifest['script_sha256']
    runner.baseline(dest)
    assert read(dest / 'baseline_evidence.json') == read(task / 'baseline_evidence.json')
    for name in ('window_checks.csv', 'scale_anchors.csv'):
        assert (dest / name).read_bytes() == (task / name).read_bytes()
    env = load('restored_calibration_environment', restored_root / 'custom/envs/curation_dynamics_space.py')
    agent = load('restored_calibration_agent', restored_root / 'custom/agents/curation_discourse_agent.py')
    anchors = {(r['scale_name'], r['type']): r['B'] for r in read(dest / 'baseline_evidence.json')['scale_anchors']}
    (dest / 'action_audits').mkdir()
    (dest / 'cell_metrics').mkdir()
    checks = []
    for scale in ('current', 'double_stress'):
        rows = await runner.cell(restored_root, dest, env, agent, scale, 'interest', 0, anchors)
        name = f'{scale}_interest_s0'
        assert rows == read(task / f'cell_metrics/{name}.json')['weekly']
        old = decompressed_sha(task / f'action_audits/{name}.jsonl.gz')
        new = decompressed_sha(dest / f'action_audits/{name}.jsonl.gz')
        assert old == new
        checks.append({'cell': name, 'actions': 1100, 'semantic_sha256': old, 'identical': True})
    assert not runner.NETWORK
    result = {'passed': True, 'baseline_commit': manifest['baseline_commit'],
              'fresh_worktree': str(restored_root), 'original_workspace_used': False, 'raw_workbook_used': False,
              'baseline_output_identical': True, 'restored_cells': checks, 'network_attempts': len(runner.NETWORK),
              'model_calls': 0, 'scope': 'all baseline aggregates and two feedback cells; not a second full scientific matrix',
              'runtime': manifest['dependencies']}
    (task / 'recovery_evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', type=Path, required=True)
    ap.add_argument('--restored-root', type=Path, required=True)
    args = ap.parse_args()
    asyncio.run(main(args.run_dir.resolve(), args.restored_root.resolve()))
