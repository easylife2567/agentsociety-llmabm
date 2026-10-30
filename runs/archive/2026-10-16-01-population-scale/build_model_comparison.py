"""冻结当前100人主实验的单组配对输入；只改本轮路径、预算及显式seed字段。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

RUN = Path(__file__).resolve().parent
SOURCE = RUN.parents[1]
WORKSPACE = RUN / 'workspace'
PAYLOAD = RUN / 'model-comparison-init'
EXPERIMENT = Path('hypothesis_4/experiment_4')
ALGORITHMS = ('random', 'chronological', 'interest')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if PAYLOAD.exists():
        raise RuntimeError('已冻结，不覆盖现有输入')
    PAYLOAD.mkdir()
    for name in ('references', 'inputs', 'configs'):
        (PAYLOAD / name).mkdir()
    old = SOURCE / 'hypothesis_4/experiment_2/init'
    for algorithm in ALGORITHMS:
        shutil.copy2(old / f'configs/timestamp_v1_{algorithm}_s0.json', PAYLOAD / f'references/{algorithm}.json')
    for name in ('injection_sample_s0.json', 'initial_sample_weekly_lag_s0.json', 'population_s0.json', 'action_schedule_s0.json'):
        shutil.copy2(old / 'inputs' / name, PAYLOAD / 'inputs' / name)
    shutil.copy2(old / 'steps_s0.yaml', PAYLOAD / 'steps.yaml')
    ledger = str(EXPERIMENT / 'runs/cuc_model_v1/_extra_attempts.count')
    runs, common = [], []
    for algorithm in ALGORITHMS:
        original = json.loads((PAYLOAD / f'references/{algorithm}.json').read_text())
        config = json.loads(json.dumps(original))
        env = config['env_modules'][0]['kwargs']
        assert env.pop('random_seed') == 0
        for key in ('injection_data_path', 'weekly_initial_injection_data_path'):
            env[key] = str(EXPERIMENT / 'init/inputs' / Path(env[key]).name)
        for agent in config['agents']:
            agent['kwargs']['content_retry_budget'] = {'limit': 330, 'ledger_path': ledger}
        normalized = json.loads(json.dumps(config))
        del normalized['env_modules'][0]['kwargs']['recommendation_algorithm']
        common.append(normalized)
        # 只允许以上差异；从新配置反向还原后必须与旧科学配置完全一致。
        restored = json.loads(json.dumps(config))
        restored['env_modules'][0]['kwargs'] = original['env_modules'][0]['kwargs']
        for new_agent, old_agent in zip(restored['agents'], original['agents']):
            new_agent['kwargs']['content_retry_budget'] = old_agent['kwargs']['content_retry_budget']
        assert restored == original
        run_id = f'cuc_model_v1_{algorithm}'
        path = PAYLOAD / f'configs/{run_id}.json'
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n')
        runs.append({'run_id': run_id, 'algorithm': algorithm,
                     'config': str(EXPERIMENT / 'init/configs' / path.name),
                     'steps': str(EXPERIMENT / 'init/steps.yaml'),
                     'run_dir': str(EXPERIMENT / 'runs/cuc_model_v1' / run_id),
                     'expected_batches': 693, 'expected_action_records': 1100,
                     'expected_week_records': 11,
                     'old_reference': f'hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_{algorithm}_s0'})
    assert common[0] == common[1] == common[2]
    shutil.copy2(PAYLOAD / 'configs/cuc_model_v1_interest.json', PAYLOAD / 'init_config.json')
    manifest = {'batch_id': 'cuc_model_v1', 'execution_authorized': True,
                'authorization': '2026-10-16用户明确要求用指定服务跑100人三种策展各一次，仅检验模型服务敏感性',
                'baseline_commit': subprocess.check_output(['git', '-C', str(WORKSPACE), 'rev-parse', 'HEAD'], text=True).strip(),
                'model': 'cuc/deepseek', 'api_base': 'https://openai.cuc.edu.cn/v1',
                'population': 100, 'weeks': 11, 'repeats_per_algorithm': 1,
                'api_seed_sent': False, 'explicit_environment_seed': False,
                'effective_environment_default_seed': 0,
                'input_selection': '旧主批s0的冻结人口、样本、行动表；不重抽，不做seed矩阵',
                'decision_opportunities': 3300, 'extra_requests_limit': 330,
                'formal_requests_upper_bound': 3630, 'service_check_requests': 1,
                'max_wall_hours': 12, 'runs': runs,
                'stop_policy': '引擎失败、动作失败或完成一臂后发现持续服务失败即停止；不自动重启或补跑',
                'source_sha256': {str(p.relative_to(WORKSPACE)): digest(p)
                                  for folder in ('custom/agents', 'custom/envs')
                                  for p in sorted((WORKSPACE / folder).rglob('*')) if p.is_file() and p.suffix in ('.py', '.json')},
                'payload_sha256': {str(p.relative_to(PAYLOAD)): digest(p) for p in sorted(PAYLOAD.rglob('*')) if p.is_file()}}
    (PAYLOAD / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    target = WORKSPACE / EXPERIMENT
    target.mkdir()
    shutil.copytree(PAYLOAD, target / 'init')
    (target / 'EXPERIMENT.md').write_text('100人、11周、三种策展各一次；切换到cuc/deepseek。计划与授权见run根README。\n')
    (target / 'README.md').write_text('本实验在隔离run中执行；init为冻结输入，runs为原始输出。未获正式采用。\n')
    print(json.dumps({'runs': 3, 'opportunities': 3300, 'payload': str(PAYLOAD)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
