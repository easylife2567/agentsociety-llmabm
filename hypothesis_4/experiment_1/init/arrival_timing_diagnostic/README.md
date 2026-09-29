# 普通真实帖到达时机诊断：冻结配置

本目录只存四格诊断的输入配置，不替换原主实验配置。研究设计、实时进度与运行授权统一见[任务入口](../../../../runs/2026-09-29-02-injection-timing/README.md)。生成器是[任务专用脚本](../../../../runs/2026-09-29-02-injection-timing/2026-09-30-01-generate-configs.py)，从工作区根目录使用 `.env` 指定的 Python 运行。

| 一级资产 | 职责 |
|---|---|
| `manifest.json` | 冻结四格矩阵、根相对路径、输入及配置哈希、运行顺序、预算、完成性与知识审计要求；runner的唯一批次来源 |
| `population.json` | 四格相同的100个人物、数值参数和时序字段；22人显式离世陈述改成依据所见内容回应 |
| `action_schedule.json` | 100人固定周内小时、63个非空小时及完整693个上海时区行动时刻 |
| `steps.yaml` | W12–W22完整693批；每批一步，tick表示距下一行动批的秒数 |
| `steps_prefix.yaml` | 完整steps的前189批；末步时钟跨度也相同，便于前三周验收后恢复 |
| `arrival_timing_diagnostic_preload_interest_s0.json` | 周初提前资格 × interest，seed 0 |
| `arrival_timing_diagnostic_timestamp_interest_s0.json` | 实际发布时间资格 × interest，seed 0 |
| `arrival_timing_diagnostic_preload_random_s0.json` | 周初提前资格 × random，seed 0 |
| `arrival_timing_diagnostic_timestamp_random_s0.json` | 实际发布时间资格 × random，seed 0 |
| `README.md` | 本级资产和使用约束 |

清单中除推荐算法与到达方式外四格共同设定逐值一致；random仍按自身实现忽略生命周期及议程参数。原始样本、初始池、词表按原路径引用，生成器验证SHA-256，不复制或重新抽样。

引擎将steps文件哈希变化作为警告，并依据持久化步骤游标恢复。runner只能接受manifest记录的 `steps_prefix.yaml → steps.yaml` 扩展，必须先验证前189个步骤完全一致；不得把前缀进程退出当作693批实验完成。运行时服务模型和代码版本由启动器另外冻结，不在生成配置时读取或保存凭据。
