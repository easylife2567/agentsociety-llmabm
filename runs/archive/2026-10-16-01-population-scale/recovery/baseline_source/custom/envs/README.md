# 自定义环境

| 资产 | 作用 |
|---|---|
| `curation_dynamics_space.py` | 舆论场环境、工具接口、持久化与周统计 |
| `curation_arrival_schedule.py` | timestamp主实验与到达诊断的小时调度、推荐、分臂回流与行动快照 |
| `curation_mechanisms.py` | 倾向分、生命周期、抽样及表达效用的共享纯函数 |
| `curation_assets/` | 冻结词表和数据处理资产 |
| `curation_dynamics_space_agent_skills/` | 环境附带的Agent技能 |

到达诊断仅由 `schedule_mode=arrival_timing` 启用，普通到达方式由 `arrival_mode` 决定。环境快照保存在官方run的 `env/CurationDynamicsSpace/state/ENV_STATE.json`。

experiment_2的arrival_official_policy=ordinary由本级正式环境和ArrivalSchedule执行：官方不置顶、不进悼念保底，保留普通兴趣候选资格。未配置该字段的历史实验继续使用agenda。对应配置在hypothesis_4/experiment_2/init，本级是运行机制的源码位置。
