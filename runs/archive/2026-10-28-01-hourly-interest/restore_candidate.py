"""从记录的Git基线、最终补丁和文件镜像恢复候选；不启动任何实验。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    run = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=run.parents[1])
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo, destination, output = args.repo.resolve(), args.destination.resolve(), args.output.resolve()
    if destination.exists():
        raise ValueError('恢复目标必须尚不存在；不覆盖或清理既有目录')
    manifest = json.loads((run / 'recovery_manifest.json').read_text())
    patch = run / manifest['patch']
    assert digest(patch) == manifest['patch_sha256']
    for name, expected in manifest['files_sha256'].items():
        assert digest(run / 'files' / name) == expected, name
    for name, expected in manifest['validation_skills_sha256'].items():
        assert digest(run / 'validation_skills' / name) == expected, name
    destination.mkdir(parents=True)
    archive = subprocess.Popen(['git', 'archive', manifest['baseline_commit'], *manifest['base_paths']],
                               cwd=repo, stdout=subprocess.PIPE)
    with tarfile.open(fileobj=archive.stdout, mode='r|') as stream:
        stream.extractall(destination, filter='data')
    if archive.wait() != 0:
        raise RuntimeError('基线导出失败，保留目标供检查')
    # 防止Git从恢复目录向上找到主工作区；补丁只对独立导出的文件生效。
    environment = dict(os.environ, GIT_CEILING_DIRECTORIES=str(destination.parent))
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=destination, env=environment, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=destination, env=environment, check=True)
    for name in manifest['files_sha256']:
        target = destination / name
        assert target.resolve().is_relative_to(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run / 'files' / name, target)
    for name in manifest['validation_skills_sha256']:
        target = destination / '.claude/skills' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run / 'validation_skills' / name, target)
    for name, expected in manifest['candidate_sha256'].items():
        assert digest(destination / name) == expected, name
    report = dict(status='passed', baseline_commit=manifest['baseline_commit'],
                  destination=str(destination), patch_check=True,
                  candidate_files_verified=len(manifest['candidate_sha256']),
                  files_from_bundle=len(manifest['files_sha256']),
                  depends_on_original_workspace=False, simulation_started=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
