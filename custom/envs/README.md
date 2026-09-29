# 自定义环境

| 资产 | 作用 |
|---|---|
| `curation_dynamics_space.py` | 舆论场环境、工具接口、持久化与周统计 |
| `curation_arrival_schedule.py` | 到达诊断的小时调度、稳定曝光、次周回流与行动快照 |
| `curation_mechanisms.py` | 倾向分、生命周期、抽样及表达效用的共享纯函数 |
| `curation_assets/` | 冻结词表和数据处理资产 |
| `curation_dynamics_space_agent_skills/` | 环境附带的Agent技能 |

到达诊断仅由 `schedule_mode=arrival_timing` 启用，普通到达方式由 `arrival_mode` 决定。环境快照保存在官方run的 `env/CurationDynamicsSpace/state/ENV_STATE.json`。
