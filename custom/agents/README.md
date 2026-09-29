# 自定义 Agent

| 资产 | 作用 |
|---|---|
| `curation_discourse_agent.py` | 固定类型话语参与者、同源数值效用及标准引擎接口 |
| `curation_arrival_action.py` | 到达时机诊断的有限上下文生成、重试预算及发布确认 |
| `curation_personas.py` | 人物模板与群体参数 |

运行入口使用实验配置中的 `CurationDiscourseAgent`。只有profile中显式启用 `arrival_timing` 才使用到达诊断行动流程。缓存目录不属于研究资产。
