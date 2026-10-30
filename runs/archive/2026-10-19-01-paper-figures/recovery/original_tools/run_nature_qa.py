"""对同一最终PDF执行nature源码、文字与碰撞检查并保留报告。"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

OUT = Path(__file__).resolve().parents[1]
SCRIPTS = OUT / 'scripts'
QA = OUT / 'qa/revision_dark2_compact/nature_qa'
STEMS = ['figure_02_observed_trends', 'figure_03_observed_platforms',
         'figure_04_simulated_trajectories', 'figure_05_feedback_exposure',
         'figure_06_bdr_ablation']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pymupdf-path')
    parser.add_argument('--qa-dir', type=Path, default=QA)
    args = parser.parse_args()
    qa_dir = args.qa_dir
    qa_dir.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if args.pymupdf_path:
        environment['PYTHONPATH'] = args.pymupdf_path + os.pathsep + environment.get('PYTHONPATH', '')
    reports = []
    jobs = [('shared_style', 'source', SCRIPTS / 'nature_source_preflight.py', [str(SCRIPTS / 'paper_plot_style.py'), '--json'])]
    for number, stem in zip(range(2, 7), STEMS):
        # 静态预检不解析本地import，因此按实际依赖拼接同一绘图源后审计。
        resolved = qa_dir / f'{stem}.resolved_source.py'
        resolved.write_text((SCRIPTS / 'paper_plot_style.py').read_text() + '\n' +
                            (SCRIPTS / f'gen_fig{number}.py').read_text())
        jobs += [
            (stem, 'source', SCRIPTS / 'nature_source_preflight.py', [str(resolved), '--json']),
            (stem, 'text', SCRIPTS / 'audit_pdf_text.py', [str(OUT / f'{stem}.pdf'), '--min-pt', '8', '--json']),
            (stem, 'collisions', SCRIPTS / 'audit_figure_collisions.py', [str(OUT / f'{stem}.pdf'), '--json-out', str(qa_dir / f'{stem}.collisions.json')]),
        ]
    for stem, kind, tool, options in jobs:
        result = subprocess.run([sys.executable, str(tool), *options], env=environment, capture_output=True, text=True)
        (qa_dir / f'{stem}.{kind}.log').write_text(result.stdout + result.stderr)
        if kind != 'collisions':
            try:
                payload = json.loads(result.stdout)
                (qa_dir / f'{stem}.{kind}.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
            except json.JSONDecodeError:
                pass
        reports.append({'figure': stem, 'audit': kind, 'exit_code': result.returncode})
        print(stem, kind, result.returncode)
    (qa_dir / 'audit_execution.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')
    if any(record['exit_code'] != 0 for record in reports):
        sys.exit(1)


if __name__ == '__main__':
    main()
