"""只供完整官方CLI入口验收：禁网，在Ray/模型初始化边界接管并检查真实模块。"""
import json
import os
from pathlib import Path
import sys


def deny_network(event, args):
    if event in {'socket.connect','socket.sendto','socket.getaddrinfo'}:
        with open(os.environ['BDR_ENTRY_NETWORK_LOG'],'a') as file:
            file.write(event+'\n')
        raise RuntimeError('完整CLI离线验收禁止网络访问')


sys.addaudithook(deny_network)

if os.environ.get('BDR_ENTRY_CHECK')=='1':
    from datetime import datetime, timedelta
    import inspect
    from unittest.mock import patch
    from agentsociety2.config import llm_dispatcher
    from agentsociety2.registry import get_registered_env_modules, get_registered_agent_modules

    async def verify_at_model_boundary():
        # SDK真实main已完成参数/环境校验、schema、steps、custom扫描和安全路径检查。
        cli = sys.modules['__main__']
        root = Path(os.environ['WORKSPACE_PATH']).resolve()
        def arg(name): return Path(sys.argv[sys.argv.index(name)+1]).resolve()
        directory,config_path,steps_path = arg('--run-dir'),arg('--config'),arg('--steps')
        assert directory.is_relative_to(root)
        runner = cli.ExperimentRunner.__new__(cli.ExperimentRunner)
        parsed = runner._load_config(config_path)
        steps = runner._load_steps(steps_path)
        env_cls = dict(get_registered_env_modules())['CurationDynamicsSpace']
        agent_cls = dict(get_registered_agent_modules())['CurationDiscourseAgent']
        paths = {'env':str(Path(inspect.getfile(env_cls)).resolve()),
                 'agent':str(Path(inspect.getfile(agent_cls)).resolve())}
        assert all(Path(p).is_relative_to(root/'custom') for p in paths.values())
        specs,name = runner._build_agent_specs([a.model_dump() for a in parsed.agents])
        assert name=='CurationDiscourseAgent' and len(specs)==100
        for spec in specs:
            target = directory/'agents'/f'agent_{int(spec["id"]):04d}'
            agent_cls.create(target,spec['profile'],spec['config'])
            with patch.object(agent_cls,'_bind_services'):
                agent = await agent_cls.from_workspace(target,None)
            assert agent._params==spec['profile']['params']
        kwargs = parsed.env_modules[0].kwargs
        env = env_cls(**kwargs)
        clock = datetime.fromisoformat(steps.start_t)
        await env.init(clock)
        assert len(steps.steps)==693
        for step in steps.steps:
            assert step.type=='run' and step.num_steps==1
            await env.step(step.tick,clock)
            clock += timedelta(seconds=step.tick)
        actions = env._arrival.state['actions']
        assert len(actions)==len({(a['agent_id'],a['week']) for a in actions})==1100
        assert len(env._arrival.state['weeks'])==11
        assert all(a['candidate_future']==0 for a in actions)
        assert clock==datetime(2026,6,1)
        checkpoint = directory/'env/CurationDynamicsSpace'
        await env.to_workspace(checkpoint)
        restored = env_cls(**kwargs)
        assert await restored.restore(checkpoint)
        assert restored._arrival.state==env._arrival.state
        report = dict(success=True,official_cli_main=True,run_dir=str(directory),workspace=str(root),
                      modules=paths,config=str(config_path),steps=str(steps_path),profiles=100,
                      environment_batches=693,unique_actions=1100,weeks=11,future_exposures=0,
                      checkpoint_restore_equal=True,network_attempts=0,LLM_calls=0,
                      stopped_before_ray_and_provider=True,
                      scope='完整真实CLI入口/模块/路径/配置/人口及无生成环境全窗；不运行真实Ray与模型服务')
        Path(os.environ['BDR_ENTRY_REPORT']).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        runner.pid_file = directory/'pid.json'
        runner._update_pid_file('offline_entry_verified',LLM_calls=0)
        raise SystemExit(0)

    llm_dispatcher.init_dispatchers = verify_at_model_boundary
