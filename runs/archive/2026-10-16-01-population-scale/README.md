# 人口规模与模型服务敏感性实验（已归档）

2026-10-30按用户“所有根级run归档”指令归档。原先讨论500/1000人，随后只实施获授权的100人、CUC服务、random/chronological/interest各一次；500/1000人扩容未实施。

## 结果与采用边界

三臂均完成693步、11周、1100次唯一行动，发布176/210/217帖，共603帖。主要制度排序保持，兴趣制度存在局部变化；没有模型质量等价、跨seed稳健或价格比较结论。报告及3条claims仍为未正式采用的候选，approved:false保留。归档和提交不等于采用，不改变正式custom、实验参数/结果或主区机器流水线。

历史每30分钟汇报heartbeat `cuc-30` 已核实为PAUSED。无新实验、LLM或网络调用。原始失败/超时恢复、SDK初始化调用与正文预算说明保留。

## 本级资产

| 资产 | 用途 |
|---|---|
| [model-comparison-analysis/](model-comparison-analysis/README.md) | 双语主报告、综合、指标、图、正文审读及独立审查 |
| [model-comparison-init/](model-comparison-init/README.md) | 冻结三臂配置、人口、真实输入、行动表、steps与manifest |
| raw_outputs/ | 本机原始输出2710文件、93,889,605字节；Git忽略，不随GitHub上传 |
| [workspace_snapshot/](workspace_snapshot/README.md) | 完整有价值工作区状态：实验/假设、分析记录、报告、综合、进度与链接 |
| [recovery/](recovery/README.md) | 基线源码、清单、映射、进度补丁及恢复验证 |
| [verify_population_archive.py](verify_population_archive.py) | 新安全入口，哈希/终态核对与临时目录禁网配置恢复 |
| model-comparison-execution.json、model-comparison-completion-verification.json | 原始监督器与终态记录，字段/时间保持 |
| initial-evidence.json、initial-git-status.txt、model-comparison-analysis-plan.md | 起点、规模讨论和预设分析口径 |
| build_model_comparison.py、check_model_comparison.py、run_model_comparison.py | 历史准备/运行源码，原字节保留，不作归档默认入口 |
| configuration-check*.log、service-check.json、pipeline-update.log、model-comparison-runtime-notes.json | 配置错误/修正、探测、SDK辅助调用与预算证据 |
| .env | 仅本机保留0600、Git忽略；不进入恢复包/GitHub |

## 独立恢复

基线为69d243955d341444ae769fae5bf23dc160465cd6。固定基线custom完整副本在recovery/baseline_source；全部新增工作区文件及原链接逐项保全，不依赖主区未提交改动。新入口--offline-check在空临时目录恢复源码/配置/状态和本机raw，并阻止全部socket连接，核验三臂100人、693批、3300机会；不运行LLM或仿真。

GitHub代码副本可用--skip-raw核验源码/报告/冻结配置；完整原始验证须从本机完整归档复制raw_outputs，并按recovery/raw_manifest.json逐文件核对。旧模型比较输入是正式experiment_2的稳定冻结资产，原SHA在source_index中。

旧路径workspace映射到workspace_snapshot/raw_outputs，详见recovery/path_map.json。历史manifest/checkpoint/源索引/日志原字节保留，不批改路径。原extract/build_appendices/报告写出脚本含历史workspace/层级约定，作为历史源码保留，不在归档中直接执行以重写冻结产物。当前默认入口仅为新的安全核验脚本。

归档前完整README见recovery/pre_archive_README.md；实际保全/恢复/worktree移除结果见recovery/archive_verification.json。
