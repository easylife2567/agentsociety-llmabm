"""在当前位置检查六图最终源码、原生PDF字号与遮挡，不重绘或读取外部数据。"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

OUT = Path(__file__).resolve().parents[1]
STEMS = ['figure_01_framework', 'figure_02_observed_trends',
         'figure_03_observed_platforms', 'figure_04_simulated_trajectories',
         'figure_05_feedback_exposure', 'figure_06_bdr_ablation']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pymupdf-path')
    args = parser.parse_args()
    destination = OUT / 'qa/final_audits'
    destination.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if args.pymupdf_path:
        environment['PYTHONPATH'] = args.pymupdf_path + os.pathsep + environment.get('PYTHONPATH', '')
    scripts = OUT / 'scripts'
    records = []
    for number, stem in enumerate(STEMS, 1):
        resolved = destination / f'{stem}.resolved_source.py'
        resolved.write_text((scripts / 'paper_plot_style.py').read_text() + '\n' +
                            (scripts / f'gen_fig{number}.py').read_text())
        jobs = [
            ('source', 'nature_source_preflight.py', [str(resolved), '--json']),
            ('text', 'audit_pdf_text.py', [str(OUT / f'{stem}.pdf'), '--min-pt', '8', '--json']),
            ('collisions', 'audit_figure_collisions.py', [str(OUT / f'{stem}.pdf'),
                '--json-out', str(destination / f'{stem}.collisions.json')]),
        ]
        for kind, tool, options in jobs:
            result = subprocess.run([sys.executable, str(scripts / tool), *options],
                env=environment, capture_output=True, text=True)
            (destination / f'{stem}.{kind}.log').write_text(result.stdout + result.stderr)
            if kind != 'collisions':
                payload = json.loads(result.stdout)
                (destination / f'{stem}.{kind}.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
            records.append({'figure': stem, 'audit': kind, 'exit_code': result.returncode})
        print(stem, 'checked', flush=True)
    result = {'passed': all(item['exit_code'] == 0 for item in records), 'jobs': records}
    (destination / 'execution.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
