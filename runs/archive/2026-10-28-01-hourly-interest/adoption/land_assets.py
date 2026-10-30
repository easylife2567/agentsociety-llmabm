"""选择性接收已完成的主实验；只复制和校验，不启动仿真或修改历史证据。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

RUN = Path(__file__).resolve().parents[1]
ROOT = RUN.parents[1]
OUT = ROOT / 'hypothesis_4/experiment_2/runs/hourly_return_v1'
INIT = ROOT / 'hypothesis_4/experiment_2/init/hourly_return_v1'
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, obj):
    content = (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()
    if path.exists() and path.read_bytes() != content:
        raise ValueError(f'拒绝覆盖不同接收记录：{path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def copy(source, target, expected=None):
    expected = expected or digest(source)
    assert source.is_file() and not source.is_symlink(), source
    assert digest(source) == expected, source
    if target.exists():
        assert target.is_file() and digest(target) == expected, target
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    assert digest(target) == expected, target
    return expected


def rel(path):
    return path.relative_to(ROOT).as_posix()


def main():
    # 接收前状态单独保全，不把用户已有差异计入本次补丁。
    baseline = HERE / 'baseline.json'
    if not baseline.exists():
        dirty = subprocess.check_output(['git', 'diff', '--name-only', '-z'], cwd=ROOT).decode().split('\0')
        protected = {}
        for name in dirty:
            if not name or name == 'runs/README.md' or name.startswith(rel(RUN) + '/'):
                continue
            p = ROOT / name
            protected[name] = digest(p) if p.is_file() else None
        write(baseline, dict(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
                             git_status=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT).decode(),
                             protected_existing_differences=protected,
                             mechanism_before={p: digest(ROOT/p) for p in (
                                 'custom/envs/curation_dynamics_space.py','custom/envs/curation_arrival_schedule.py')}))
    patch = HERE / 'mechanism.patch'
    copy(RUN / 'mechanism.patch', patch)
    candidate = read(RUN / 'recovery_manifest.json')['candidate_sha256']
    files = ['custom/envs/curation_dynamics_space.py', 'custom/envs/curation_arrival_schedule.py']
    if any(digest(ROOT/p) != candidate[p] for p in files):
        subprocess.run(['git', 'apply', '--check', str(patch)], cwd=ROOT, check=True)
        subprocess.run(['git', 'apply', str(patch)], cwd=ROOT, check=True)
    assert all(digest(ROOT/p) == candidate[p] for p in files)
    test = 'custom/tests/test_hourly_return.py'
    copy(RUN/'files'/test, ROOT/test, candidate[test])
    configs = {}
    for p in sorted((RUN/'files/hypothesis_4/experiment_2/init/hourly_return_v1/configs').glob('*.json')):
        target = INIT/'configs'/p.name
        configs[rel(target)] = copy(p, target)
    assert len(configs) == 30
    copy(RUN/'files/hypothesis_4/experiment_2/init/hourly_return_v1/manifest.json', INIT/'preparation_manifest.json')
    # 原计划/状态/账本只按原字节接收；历史绝对路径不改写、不当作当前运行入口。
    records = {}
    for group, names in {
        'pilot': ['runtime_plan.json','parallel_revision.json','selected_revision.json','batch_execution.json',
                  'raw_results_manifest.json','extra_attempts.count'],
        'seed_extension': ['runtime_plan.json','batch_execution.json','completion_summary.json',
                           'completion_runs.csv','raw_results_manifest.json','extra_attempts.count'],
        'analysis': ['chronological_reuse_audit.json','contract.json','independent_verification.json'],
    }.items():
        for name in names:
            source = RUN/group/name
            if source.exists():
                target = OUT/'execution_records'/group/name
                records[rel(target)] = copy(source,target)
    historical_relocation = ROOT/'hypothesis_4/experiment_2/runs/timestamp_v1/relocation.json'
    records[rel(historical_relocation)] = digest(historical_relocation)
    history_files = read(historical_relocation)['files']
    complete = read(RUN/'seed_extension/completion_summary.json')
    audit = read(RUN/'analysis/chronological_reuse_audit.json')
    provenance = read(RUN/'analysis/results/provenance.json')
    assert complete['status'] == audit['status'] == 'passed'
    new = {r['run_id']: r for r in read(RUN/'seed_extension/raw_results_manifest.json')['runs']}
    pilot = {r['algorithm']: r for r in read(RUN/'pilot/raw_results_manifest.json')['runs'] if r['status']=='completed'}
    descriptors, copied = [], []
    for row in complete['runs']:
        seed, arm = row['seed'], row['algorithm']
        source = Path(row['preserved_run_dir'])
        target = OUT/row['run_id']
        frozen = pilot[arm]['files_sha256'] if seed == 0 else new[row['run_id']]['files_sha256']
        for name, sha in frozen.items():
            copy(source/name,target/name,sha)
        for directory in (new[row['run_id']].get('directories',[]) if seed else []):
            (target/directory).mkdir(parents=True,exist_ok=True)
        actual = {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
        assert actual == set(frozen), (target,actual.symmetric_difference(frozen))
        descriptors.append(dict(algorithm=arm,seed=seed,run_id=row['run_id'],run_dir=rel(target),
                                origin=row['origin'],expected_models={row['actual_models']:row['posts']},
                                expected_requests=row['body_outer_requests'],frozen=frozen))
        copied.append(dict(run_id=row['run_id'],source_run_dir=str(source),target_run_dir=rel(target),
                           files=len(frozen),files_sha256=frozen))
        print('PASS copy',row['run_id'],len(frozen),flush=True)
    for row in audit['runs']:
        directory = Path(row['run_dir'])
        frozen = {str(Path(p).relative_to(directory)):sha for p,sha in audit['source_sha256'].items()
                  if Path(p).is_relative_to(directory)}
        # 时序核心审计只锁状态；官方replay碎片继承正式迁移清单。
        for entry in history_files:
            path = ROOT/entry['path']
            if path.is_relative_to(directory):
                name = path.relative_to(directory).as_posix()
                assert name not in frozen or frozen[name] == entry['sha256']
                frozen[name] = entry['sha256']
        assert frozen and all(digest(directory/p)==sha for p,sha in frozen.items())
        descriptors.append(dict(algorithm='chronological',seed=row['seed'],run_id=row['run_id'],
            run_dir=rel(directory),origin='reused_formal_timestamp_chronological',expected_models=row['actual_models'],
            expected_requests=row['counts']['body_outer_requests'],frozen=frozen))
    assert len(descriptors)==30 and len({(r['algorithm'],r['seed']) for r in descriptors})==30
    inputs = 'presentation/hypothesis_4/hourly_return_v1/inputs/'
    manifest = dict(status='passed',adopted=True,new_execution_authorized=False,
        scope='hourly-return main experiment; 20 completed random/interest plus 10 reused chronological',
        source_sha256=records,runs=descriptors,reality_csv=inputs+'reality_week_boundary.csv',
        reality_audit=inputs+'reality_measurement_audit.json',dtw_method=inputs+'dtw_method.py',
        mechanism_sha256={p:digest(ROOT/p) for p in files},
        note='原始内部metadata与预算/状态均原字节保留；只读分析使用本manifest当前正式路径，不依赖历史探索目录。')
    write(OUT/'manifest.json',manifest)
    write(OUT/'relocation.json',dict(status='passed',operation='copy_and_verify_no_source_removal',
        copied_runs=copied,chronological_runs_reused=[r['run_dir'] for r in descriptors if r['algorithm']=='chronological'],
        excluded='withdrawn pilot chronological; old weekly-return random/interest; B/D/R',source_sha256=records))
    write(INIT/'manifest.json',dict(status='adopted',new_execution_authorized=False,
        arrival_agent_return_policy='next_batch',configs_sha256=configs,
        actual_results_manifest=rel(OUT/'manifest.json'),
        note='30份机制配置是已验收准备版本；真实seed0/seed1–9的操作预算与实际SOCIETY另见接收结果和execution_records。时序复用旧完整结果，不声称新跑。'))
    protected=read(baseline)['protected_existing_differences']
    assert all((digest(ROOT/p) if (ROOT/p).is_file() else None)==sha for p,sha in protected.items())
    write(HERE/'asset_acceptance.json',dict(status='passed',copied_new_runs=len(copied),
        reused_chronological=10,copied_raw_files=sum(r['files'] for r in copied),
        main_configs=30,mechanism_sha256=manifest['mechanism_sha256'],protected_differences_unchanged=True,
        official_manifest=rel(OUT/'manifest.json'),new_simulations=0,model_requests=0))


if __name__=='__main__':
    main()
