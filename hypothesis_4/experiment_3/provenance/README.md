# 来源、失败与路径映射

本目录保存采用前事实，不作为正式启动或分析入口。original_run_ablation.py及两份patch只用于还原历史控制器，含旧隔离路径和旧预算，不在主工作区执行。

| 直接资产 | 用途 |
|---|---|
| failed_attempt_01/、startup-failure/ | 首次403失败及调用0的依据，非有效第十次实验 |
| layout-fix/、parallel/ | 完整CLI离线验收与串行到两路的交接原始证据 |
| exploration_baseline.json | 原Git基线、33项主批来源及完成状态 |
| analysis_baseline.json、candidate_final_verification.json | 原分析起点、账本和真实通过范围，不冒充正式复验 |
| original_source_index.json | 采用前12单元来源索引，原私有路径保持 |
| original_experiment_plan.md、original_batch_README.md | 原设计与批次目录说明，不作当前进度 |
| original_run_ablation.py、output-layout.patch、parallel-control.patch | 原控制器及两轮修正恢复材料，未选作正式重跑入口 |
| path_map.json | 原物理/镜像/配置/分析位置到正式位置的对应关系 |

独立复算入口在../analysis，当前源索引在正式presentation的data/source_index.json。原始证据中的其他历史路径按映射解释，不批量改写冻结记录；本目录未复制.env或任何凭据。
