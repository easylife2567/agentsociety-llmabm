"""从准确Git对象导出纯净源码，独立恢复两项U候选离线单元。"""
import asyncio
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


async def verify(run_dir):
    with tempfile.TemporaryDirectory(prefix='u-recovery-',dir=run_dir/'tmp') as temp:
        temp=Path(temp);root=temp/'baseline';restored=temp/'run';out=restored/'u_results'
        original=json.loads((run_dir/'experiment_manifest.json').read_text())
        for path in original['code_sha256']:
            dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True)
            content=subprocess.check_output(['git','show',f"{original['baseline_commit']}:{path}"],cwd=run_dir)
            dest.write_bytes(content)
        restored.mkdir();out.mkdir();(out/'action_audits').mkdir();(out/'cell_metrics').mkdir()
        shutil.copytree(run_dir/'frozen',restored/'frozen')
        for name in ('calibration_experiments.py','u_experiments.py','baseline_evidence.json','experiment_manifest.json'):
            shutil.copyfile(run_dir/name,restored/name)
        sys.path.insert(0,str(restored))
        spec=importlib.util.spec_from_file_location('restored_u',restored/'u_experiments.py')
        runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
        assert all(runner.sha(root/p)==h for p,h in original['code_sha256'].items())
        env=runner.module('restored_u_env',root/'custom/envs/curation_dynamics_space.py')
        agent=runner.module('restored_u_agent',root/'custom/agents/curation_discourse_agent.py')
        runner.static_check(restored,out)
        assert runner.read(out/'static_mapping.json')==runner.read(run_dir/'u_results/static_mapping.json')
        results=[]
        for condition in ('soft_warm','no_feedback'):
            rows=await runner.cell(root,out,env,agent,condition,'interest',0)
            name=f'{condition}_interest_s0'
            assert runner.audit_read(out/f'action_audits/{name}.jsonl.gz')==runner.audit_read(run_dir/f'u_results/action_audits/{name}.jsonl.gz')
            assert rows==runner.read(run_dir/f'u_results/cell_metrics/{name}.json')['weekly']
            results.append(dict(condition=condition,arm='interest',seed=0,actions=1100,post_opportunities=1000,all_actions_and_weekly_rows_identical=True))
        assert not runner.NETWORK
        runner.write(run_dir/'u_recovery.json',dict(baseline=original['baseline_commit'],source='git show exact committed objects; no original workspace or main uncommitted source',static_all_rows_identical=True,cells=results,network_attempts=0,model_calls=0,full_matrix_rerun=False))
        print('Recovered static checks and two cells independently; no LLM/network')


if __name__=='__main__':
    asyncio.run(verify(Path(__file__).resolve().parent))
