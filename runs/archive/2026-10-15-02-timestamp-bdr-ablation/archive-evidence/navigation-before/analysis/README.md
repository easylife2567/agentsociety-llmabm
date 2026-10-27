# timestamp B、D、R同seed配对分析

本目录是当前run内的候选分析工作区。只读九次正式消融和主实验三个timestamp-interest Full；不修改主项目、原始输出、冻结配置或请求账本，不新增LLM调用。实时交接统一见[run README](../README.md)。

优先阅读[中文HTML报告](presentation/hypothesis_4/report_zh.html)或[中文Markdown报告](presentation/hypothesis_4/report_zh.md)。三项预设指标的三个seed方向一致：去B晚期供给平均减少7.00帖/周，去D晚期玩梗型作者发言率减少30.70个百分点，去R衰减后W14–W18全体发言率增加30.07个百分点。解释限定于冻结interest制度及参数；这是闭环总变化，不是可相加的独立贡献。

| 本级资产 | 用途 |
|---|---|
| [presentation/](presentation/hypothesis_4/README.md) | 双语MD/HTML报告、原始配对明细、图表及可嵌入副本 |
| [synthesis/](synthesis/README.md) | 仅整合本次12单元的双语候选综合，不扩大到其他制度 |
| [tools/](tools/README.md) | 可重复执行的纯Python提取、模板绘图、报告和核验；含冻结模板副本和禁网保护 |
| [checks/](checks/README.md) | 27项独立原始记录复算、5394项原始文件哈希、边界和图表检查、CLI回执与真实失败记录 |
| [payloads/](payloads/README.md) | 冻结指标计划、候选结论及绘图契约；新结论未标为用户批准 |
| hypothesis_4/ | CLI定位用假设/实验说明；其中run链接仅是no_b seed0的代表性replay，实际分析源是source_index.json列出的12次 |
| .agentsociety/ | 本目录独立的analysis harness记录，未覆盖主项目或原worktree历史分析状态 |
| .claude/ | 指向项目已有技能的只读定位链接；不复制或重装依赖 |
| [.gitignore](.gitignore) | 忽略可重建链接、绘图库缓存和pycache；不据此删除原始材料 |

图表沿用指定chart3b的Meme橙、Mourning蓝、Education绿、Marketing黄、Other浅蓝及W13事件线。12张逐seed供给图直接调用冻结模板函数，另有4张均值图和3张主比较图；全部供给图0–80轴，真实峰值63，没有裁剪。PNG与可编辑文字的SVG均保存，主图另有PDF。

## 指标、证据与可复算入口

- [paired_differences.csv](presentation/hypothesis_4/data/paired_differences.csv)：每个消融×seed的Full值、消融值和差值，方向恒为消融−Full。
- [paired_summary.csv](presentation/hypothesis_4/data/paired_summary.csv)：三个配对差值的均值、最小和最大，不是置信区间。
- [metric_dictionary.json](presentation/hypothesis_4/data/metric_dictionary.json)：固定窗口、分母、比例与百分点、阅读份额和标签口径。
- [source_index.json](presentation/hypothesis_4/data/source_index.json)：12次实际源、replay/Agent/环境/配置哈希和9项科学配置对照；5394项replay/Agent文件另经核验。
- [final_verification.json](checks/final_verification.json)：13200次机会、660行类型周表、132行总周表、10个零供给周保留、独立复算与零新增调用边界。

在项目根目录读取`.env`的PYTHON_PATH，按以下顺序重建本目录派生结果（不启动仿真）：

```bash
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
BDR_ANALYSIS_ROOT="$PWD/runs/2026-10-15-02-timestamp-bdr-ablation/analysis"
PYTHONPATH="$BDR_ANALYSIS_ROOT/tools/offline_guard" LITELLM_LOCAL_MODEL_COST_MAP=True \
  "$PYTHON_PATH" "$BDR_ANALYSIS_ROOT/tools/extract.py"
PYTHONPATH="$BDR_ANALYSIS_ROOT/tools/offline_guard" LITELLM_LOCAL_MODEL_COST_MAP=True \
  "$PYTHON_PATH" "$BDR_ANALYSIS_ROOT/tools/plot.py"
PYTHONPATH="$BDR_ANALYSIS_ROOT/tools/offline_guard" LITELLM_LOCAL_MODEL_COST_MAP=True \
  "$PYTHON_PATH" "$BDR_ANALYSIS_ROOT/tools/report.py"
PYTHONPATH="$BDR_ANALYSIS_ROOT/tools/offline_guard" LITELLM_LOCAL_MODEL_COST_MAP=True \
  "$PYTHON_PATH" "$BDR_ANALYSIS_ROOT/tools/verify.py"
```

恢复依赖稳定的主项目Full原始输出和本run消融原始输出，具体路径与校验和已登记；不能仅靠报告文件重新产生原始LLM文本。绘图模板已在tools保存，依赖版本见checks/dependencies.json；没有安装新依赖或重建环境。不得将上述分析命令换成run_ablation启动、checkpoint续跑或新模型请求。

## 候选交付与正式签署的区别

本轮完成统计、候选报告、图表及一致性核验，没有伪造独立审阅。用户要求“不新增LLM调用”，所以没有调额外模型reviewer。新结论尚未逐条获得用户确认，harness中三个claim均为approved=false。

[分析技能](../../../.claude/skills/agentsociety-analysis/SKILL.md)规定：“Do not mark analysis complete until `validate-synthesis` passes.” 其produce/synthesis正式签署还要求独立reviewer。当前frame/explore门禁通过，正式流程停在claims；refine/produce/synthesis发布签署未通过，也未将pipeline的analysis写为completed。本轮图表和报告按用户直接授权作为run内候选材料交付，不冒充正式审批或主项目采用。相关CLI预检记录见checks/report-context-dry-run.json。
