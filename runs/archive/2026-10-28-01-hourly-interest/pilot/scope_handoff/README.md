# 缩减为随机/兴趣的现场与恢复材料

实时状态统一见run README；本级仅索引范围变更证据，不另建人工进度表。

| 资产 | 用途 |
|---|---|
| before-scope-state.json | root暂停旧并行父后的状态，随机未中断 |
| withdrawal-request.json | 用户撤回时序的指令、目标PID及仅对时序SIGINT记录 |
| withdrawn_chronological.json | 时序退出后的69步/107行动/30帖/30次已持久化正文请求、原始SHA256；不作为完整条件 |
| parallel-state.json | 新控制器交接前保存的旧并行状态 |
| scope-handoff-before.json | 保留的随机PID或完成结果、原起点/截止及撤回消耗 |
| live-check.json | 当前两臂接管后真实进度、已完成随机及累计请求核对 |
| analysis_start/ | 修改前分析/绘图脚本的实际起点副本及SHA256，供分析补丁恢复 |
| analysis_restore/ | 按保存起点独立应用分析补丁的核验副本，不用于科研仿真 |
| analysis_patch_check.json | 分析补丁check/apply及最终3文件哈希一致性证据 |
| analysis_patch_check_final.json | 元数据修正后最终补丁从保存起点独立重放，3文件一致 |
| metadata_start/ | 图表来源行数和索引修正前的两脚本实际起点 |
| selected_analysis_before_metadata.patch | 元数据修正前的分析补丁历史副本，最终补丁在上级selected_analysis.patch |

原时序日志、Agent和checkpoint保留在原隔离输出目录，不删除、不补为完整结果。原三份配置和计划不改，当前有效范围由上级selected_revision.json追加限定。
