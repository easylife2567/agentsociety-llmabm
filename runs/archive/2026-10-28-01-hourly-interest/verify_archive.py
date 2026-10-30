"""离线核对小时回流run的恢复包和归档原始镜像，不使用旧绝对路径。"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess


RUN = Path(__file__).resolve().parent
RAW_PREFIXES = ('pilot/results/', 'seed_extension/results/',
                'pilot/agent_supply/inputs/chronological_s0/')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(RUN.resolve()):
        raise ValueError(f'路径超出归档run：{path}')
    return resolved


def verify_bundle():
    manifest = read(RUN / 'recovery_manifest.json')
    assert sha(local(RUN / manifest['patch'])) == manifest['patch_sha256']
    for key, prefix in [('files_sha256', 'files'), ('validation_skills_sha256', 'validation_skills')]:
        for name, digest in manifest[key].items():
            assert sha(local(RUN / prefix / name)) == digest, name
    return {'baseline_commit': manifest['baseline_commit'], 'patch_matches': True,
            'files_verified': len(manifest['files_sha256']),
            'skills_verified': len(manifest['validation_skills_sha256']),
            'candidate_files': len(manifest['candidate_sha256'])}


def verify_raw():
    records = []
    for batch in ['pilot', 'seed_extension']:
        manifest = read(RUN / batch / 'raw_results_manifest.json')
        assert manifest['status'] == 'passed'
        for row in manifest['runs']:
            # 历史manifest字节保持，仅按已冻结snapshot/run_id定位现在的镜像。
            relative = Path(row['snapshot']) if batch == 'pilot' else Path('results') / row['run_id']
            directory = local(RUN / batch / relative)
            expected = row['files_sha256']
            actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
            assert actual == set(expected), f'原始文件集合改变：{directory.name}'
            size = 0
            for name, digest in expected.items():
                path = local(directory / name)
                assert sha(path) == digest, f'{directory.name}/{name}'
                size += path.stat().st_size
            records.append({'batch': batch, 'run_id': directory.name,
                'status': row.get('status', 'completed'), 'files': len(expected), 'bytes': size})
    return {'runs': records, 'run_count': len(records),
            'file_count': sum(r['files'] for r in records),
            'bytes': sum(r['bytes'] for r in records)}


def verify_analysis_sources(include_raw):
    contract = read(RUN / 'pilot/agent_supply/three_arm_contract.json')
    checked, skipped, size = 0, 0, 0
    for row in contract['frozen_sources']:
        if not include_raw and row['frozen'].startswith('inputs/chronological_s0/'):
            skipped += 1
            continue
        path = local(RUN / 'pilot/agent_supply' / row['frozen'])
        assert sha(path) == row['sha256'], row['frozen']
        checked += 1
        size += path.stat().st_size
    return {'verified_files': checked, 'skipped_raw_files': skipped, 'bytes': size}


def verify_preserved_files(include_raw):
    relocation = read(RUN / 'evidence/archive/relocation.json')
    inventory = local(RUN / relocation['protected_inventory'])
    assert sha(inventory) == relocation['protected_inventory_sha256']
    expected = json.loads(gzip.decompress(inventory.read_bytes()))
    checked, skipped = 0, 0
    for name, digest in expected.items():
        if not include_raw and name.startswith(RAW_PREFIXES):
            skipped += 1
            continue
        assert sha(local(RUN / name)) == digest, name
        checked += 1
    return {'verified_files': checked, 'skipped_local_raw_files': skipped,
            'historical_paths_and_original_bytes_unchanged': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata-only', action='store_true',
                        help='仅核对恢复材料；用于未下载本地原始镜像的Git克隆')
    parser.add_argument('--repo', type=Path, help='可选Git仓库，用于核对基线对象及raw忽略规则')
    parser.add_argument('--output', type=Path, default=RUN / 'evidence/archive/verify_after_move.json')
    args = parser.parse_args()
    result = {'passed': False, 'simulation_calls': 0, 'network_calls': 0,
              'raw_checked': not args.metadata_only}
    try:
        result['recovery'] = verify_bundle()
        if not args.metadata_only:
            result['raw'] = verify_raw()
        result['frozen_analysis_sources'] = verify_analysis_sources(not args.metadata_only)
        result['preserved_files'] = verify_preserved_files(not args.metadata_only)
        if args.repo:
            repo = args.repo.resolve()
            subprocess.run(['git', 'cat-file', '-e', result['recovery']['baseline_commit'] + '^{commit}'],
                           cwd=repo, check=True, capture_output=True)
            paths = [RUN / 'pilot/results', RUN / 'seed_extension/results',
                     RUN / 'pilot/agent_supply/inputs/chronological_s0']
            result['raw_ignored_by_git'] = {}
            for path in paths:
                probe = next((p for p in path.rglob('*') if p.is_file()), path / 'example.json')
                relative = probe.resolve().relative_to(repo)
                status = subprocess.run(['git', 'check-ignore', '-q', str(relative)], cwd=repo).returncode
                assert status == 0, f'原始镜像未被Git忽略：{relative}'
                result['raw_ignored_by_git'][str(path.relative_to(RUN))] = True
            result['env_ignored_by_git'] = subprocess.run(
                ['git', 'check-ignore', '-q', str((RUN / '.env').relative_to(repo))],
                cwd=repo).returncode == 0
            assert result['env_ignored_by_git'], '.env未被Git忽略'
        result['passed'] = True
    except Exception as exc:
        result['error'] = {'type': type(exc).__name__, 'message': str(exc)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'raw_checked': result['raw_checked'],
                      'raw_files': result.get('raw', {}).get('file_count'),
                      'report': str(args.output), 'error': result.get('error')}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
