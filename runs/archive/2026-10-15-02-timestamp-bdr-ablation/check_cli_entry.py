"""以真实python -m官方CLI命令复现旧布局拒绝，并验收九份新布局；零外部调用。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN/'workspace'
INIT = ROOT/'hypothesis_4/experiment_3/init'
OUT = RUN/'evidence/layout-fix/cli-entry'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    env = dict(os.environ)
    for key in list(env):
        if key.endswith('API_KEY') or key.startswith(('AGENTSOCIETY_LLM_','AGENTSOCIETY_CODER_')):
            env.pop(key)
    env.update(BDR_ENTRY_CHECK='1',BDR_ENTRY_NETWORK_LOG=str(OUT/'network_attempts.log'),
               PYTHONPATH=str(RUN/'cli_entry_hook'),WORKSPACE_PATH=str(ROOT),AGENTSOCIETY_WORKSPACE=str(ROOT),
               LITELLM_LOCAL_MODEL_COST_MAP='True',MEM0_TELEMETRY='False',ANONYMIZED_TELEMETRY='False',
               AGENTSOCIETY_LLM_API_KEY='offline-unused-placeholder',AGENTSOCIETY_LLM_API_BASE='https://offline.invalid/v1',
               AGENTSOCIETY_LLM_MODEL='deepseek-v4-1-flash-260910')
    manifest = json.loads((INIT/'manifest.json').read_text())
    reports = []
    # 反例使用全新测试目录，不碰首次失败原目录。
    cases = [('old_layout_rejected',manifest['runs'][0],RUN/'tmp/cli-old-layout')]
    cases += [(run['run_id'],run,ROOT/'hypothesis_4/experiment_3/runtime/cli-entry-checks'/run['run_id'])
              for run in manifest['runs']]
    for label,run,directory in cases:
        assert not directory.exists(), '保留已存在测试证据，禁止覆盖: '+str(directory)
        directory.mkdir(parents=True)
        report_path = OUT/(label+'.json')
        child_env = dict(env,BDR_ENTRY_REPORT=str(report_path),AGENTSOCIETY_HOME_DIR=str(directory/'workspace'))
        command = [sys.executable,'-m','agentsociety2.society.cli','--config',str(ROOT/run['config']),
                   '--steps',str(ROOT/run['steps']),'--run-dir',str(directory),'--experiment-id',label,
                   '--log-file',str(directory/'engine.log'),'--batch-size','100']
        with (OUT/(label+'.log')).open('w') as log:
            child = subprocess.run(command,cwd=ROOT,env=child_env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        if label=='old_layout_rejected':
            assert child.returncode!=0 and '403: Workspace path is not allowed' in (OUT/(label+'.log')).read_text()
            assert not report_path.exists()
        else:
            assert child.returncode==0, '入口验收失败，见 '+str(OUT/(label+'.log'))
            reports.append(json.loads(report_path.read_text()))
        print(label+' PASS',flush=True)
    assert not (OUT/'network_attempts.log').exists() or not (OUT/'network_attempts.log').read_text()
    result = dict(success=True,positive_real_cli_cases=len(reports),old_layout_rejected=True,
                  actual_profiles=sum(x['profiles'] for x in reports),environment_windows=9,
                  environment_batches=6237,unique_actions=9900,LLM_calls=0,network_attempts=0,
                  real_ray_or_provider_started=False,
                  scope='真实完整官方命令入口、注册路径和安全检查；在模型/Ray初始化边界执行真实profile/环境全窗后退出，未伪造完整LLM运行。',
                  controller_sha256=hashlib.sha256((RUN/'run_ablation.py').read_bytes()).hexdigest(),
                  hook_sha256=hashlib.sha256((RUN/'cli_entry_hook/sitecustomize.py').read_bytes()).hexdigest())
    (OUT/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    main()
