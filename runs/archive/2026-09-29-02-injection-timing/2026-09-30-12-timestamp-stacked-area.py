"""按既有chart3b模板绘制timestamp两臂的Agent周发帖量。

直接复用模板函数，保持五类配色、堆叠顺序、事件线和0–80纵轴。
只计成功发布，按固定作者类型分组；真实帖按发布时间到达，Agent帖次周回流。
"""
import csv
import hashlib
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[2]
OUT = ROOT/'presentation/hypothesis_4/2026-09-30-01-arrival-timing'
# 将绘图库临时缓存留在任务tmp，不写入用户全局配置目录。
cache = TASK/'tmp/matplotlib'
cache.mkdir(parents=True, exist_ok=True)
os.environ['MPLCONFIGDIR'] = str(cache)
os.environ['XDG_CACHE_HOME'] = str(TASK/'tmp')
spec = importlib.util.spec_from_file_location('run_chart_template', ROOT/'hypothesis_4/experiment_1/plot_run_charts.py')
template = importlib.util.module_from_spec(spec)
spec.loader.exec_module(template)


def main():
    manifest = json.loads((ROOT/'hypothesis_4/experiment_1/init/arrival_timing_diagnostic/manifest.json').read_text())
    hashes = json.loads((OUT/'input_hashes.json').read_text())
    types = [kind for kind in template.TYPE_ORDER if kind != 'noise']
    rows = []
    for run in manifest['runs']:
        if run['arrival_mode'] != 'timestamp':
            continue
        state_path = ROOT/run['run_dir']/'env/CurationDynamicsSpace/state/ENV_STATE.json'
        assert hashlib.sha256(state_path.read_bytes()).hexdigest() == hashes[str(state_path.relative_to(ROOT))]
        weekly = json.loads(state_path.read_text())['_arrival_state']['weeks']
        assert [w['week'] for w in weekly] == [f'2026-W{w}' for w in range(12,23)]
        # 从逐行动表独立计数，避免模板缺字段时默认为零而画出假曲线。
        with (OUT/'decisions.csv').open() as file:
            counts = Counter((d['week'],d['type']) for d in csv.DictReader(file)
                             if d['condition'] == f"timestamp-{run['algorithm']}" and d['posted'] == 'True')
        for week in weekly:
            values = {kind:week[f'agent_supply_{kind}'] for kind in types}
            assert all(values[kind] == counts[week['week'],kind] for kind in types)
            assert sum(values.values()) == week['agent_supply']
            rows.append(dict(run_id=run['run_id'],week=week['week'],**values,total=week['agent_supply']))
        name = f"timestamp_{run['algorithm']}_s0"
        path = OUT/f'{name}__chart3b_agent_supply_stacked_area.png'
        template.chart3b_agent_supply_stacked_area(weekly,name,path)
        print(f"{name}: {len(weekly)}周，成功发帖{sum(w['agent_supply'] for w in weekly)}，{path}")
    with (OUT/'timestamp_agent_supply_by_type.csv').open('w',newline='') as file:
        writer = csv.DictWriter(file,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    main()
