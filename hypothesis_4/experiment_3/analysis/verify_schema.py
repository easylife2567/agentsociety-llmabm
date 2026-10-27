"""在正式位置调用官方配置检查，核对九份冻结配置和实际模块来源；不启动仿真。"""
from pathlib import Path
import hashlib
import importlib.util
import inspect
import json
import os
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
assert os.environ.get('BDR_ANALYSIS_OFFLINE_GUARD') == 'active'
os.environ.update(WORKSPACE_PATH=str(ROOT), AGENTSOCIETY_WORKSPACE=str(ROOT),
                  MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False')

from agentsociety2.registry import (scan_and_register_custom_modules,
    get_registered_agent_modules, get_registered_env_modules)
scan_and_register_custom_modules(ROOT)
spec = importlib.util.spec_from_file_location('official_config', ROOT / '.claude/skills/agentsociety-experiment-config/scripts/config.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
api._ensure_agentsociety2()
generator_spec = importlib.util.spec_from_file_location('frozen_generator', HERE / 'init/config_params.py')
generator = importlib.util.module_from_spec(generator_spec)
generator_spec.loader.exec_module(generator)
generator.verify_sources()
manifest = json.loads((HERE / 'init/manifest.json').read_text())
for name, expected in manifest['output_sha256'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name

modules = {
    'agent': dict(get_registered_agent_modules())['CurationDiscourseAgent'],
    'env': dict(get_registered_env_modules())['CurationDynamicsSpace'],
}
locations = {k: str(Path(inspect.getfile(v)).resolve()) for k, v in modules.items()}
assert all(Path(p).is_relative_to(ROOT / 'custom') for p in locations.values())
records = []
for row in manifest['runs']:
    paths = {'init_config': ROOT / row['config'], 'steps_yaml': ROOT / row['steps']}
    with patch.object(api, 'get_experiment_paths', return_value=paths):
        result = api.action_check(ROOT, '4', '3')
    assert result['success'], (row['run_id'], result)
    records.append({'run_id': row['run_id'], 'official_check': result})
assert len(records) == 9
out = {'passed': True, 'loaded_modules': locations, 'configs': records,
       'source_lock_and_frozen_outputs_match': True, 'LLM_calls': 0,
       'scope': 'official config/schema/693-step/module checks at formal paths; no Ray or model initialization'}
(HERE / 'checks/formal_schema.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': True, 'official_configs': 9, 'loaded_modules': locations, 'LLM_calls': 0}, ensure_ascii=False))
