"""禁网核对三臂科学配置、实际模块、时间表和独立路径；不生成LLM正文。"""
from pathlib import Path
from collections import Counter
from unittest.mock import patch
import importlib.util
import json
import os
import socket

RUN = Path(__file__).resolve().parent
WORKSPACE = RUN / 'workspace'


def main():
    from dotenv import dotenv_values
    os.environ.update({k: v for k, v in dotenv_values(RUN / '.env').items() if v is not None})
    os.chdir(WORKSPACE)
    calls = []

    def deny(*args, **kwargs):
        calls.append('blocked')
        raise AssertionError('离线检查禁止联网')

    result = {'arms': [], 'network_attempts': 0, 'llm_calls': 0}
    with patch.object(socket.socket, 'connect', deny), patch.object(socket.socket, 'connect_ex', deny), patch.object(socket, 'create_connection', deny):
        from agentsociety2.registry import scan_and_register_custom_modules, get_registered_env_modules
        from agentsociety2.society.models import InitConfig, StepsConfig
        import yaml
        import inspect
        scan_and_register_custom_modules(WORKSPACE)
        env_cls = dict(get_registered_env_modules())['CurationDynamicsSpace']
        assert Path(inspect.getfile(env_cls)).resolve() == WORKSPACE / 'custom/envs/curation_dynamics_space.py'
        result['env_source'] = inspect.getfile(env_cls)
        init = WORKSPACE / 'hypothesis_4/experiment_4/init'
        steps = StepsConfig.model_validate(yaml.safe_load((init / 'steps.yaml').read_text()))
        assert len(steps.steps) == 693
        common = []
        for path in sorted((init / 'configs').glob('*.json')):
            raw = json.loads(path.read_text())
            cfg = InitConfig.model_validate(raw)
            env = env_cls(**cfg.env_modules[0].kwargs)
            assert env._random_seed == 0
            assert 'random_seed' not in raw['env_modules'][0]['kwargs']
            assert len(cfg.agents) == len(env._agent_types) == len(env._chronological_action_hours) == 100
            assert Counter(env._agent_types.values()) == {'marketing': 23, 'mourning': 22, 'other': 21, 'meme': 19, 'education': 15}
            for agent in cfg.agents:
                assert agent.agent_id == agent.kwargs['id']
                assert agent.kwargs['content_retry_budget']['limit'] == 330
                assert 'experiment_4/runs/cuc_model_v1/' in agent.kwargs['content_retry_budget']['ledger_path']
            normalized = json.loads(json.dumps(raw))
            algorithm = normalized['env_modules'][0]['kwargs'].pop('recommendation_algorithm')
            common.append(normalized)
            result['arms'].append({'algorithm': algorithm, 'agents': 100, 'opportunities': 1100, 'batches': 693, 'effective_seed': 0})
        assert len(common) == 3 and common[0] == common[1] == common[2]
    assert not calls
    result['network_attempts'] = len(calls)
    result['success'] = True
    (RUN / 'model-comparison-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
