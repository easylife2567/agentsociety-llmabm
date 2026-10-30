# 实际验收与恢复证据

所有测试均为离线功能检查，不是LLM仿真结果。失败记录保留；候选实现通过以attempt2及recovery记录为准；2026-10-30归档前又在新空目录完成独立恢复、42项测试与60配置/600 profile验收，见[archive/](archive/README.md)。

| 文件 | 用途 |
|---|---|
| [config_validation.json](config_validation.json) | 60配置与600profile官方禁网验收、模块来源及运行时 |
| [config_validation.log](config_validation.log) | 配置验收日志 |
| [final_state.json](final_state.json) | 保护文件、候选、验收、Git状态与未启动边界的最终核对 |
| [hourly-tests-attempt1.log](hourly-tests-attempt1.log) | 7项新增回流测试首轮通过日志 |
| [legacy_regression.json](legacy_regression.json) | 首轮35项检查的环境错误统计，保留原证据 |
| [legacy_regression.log](legacy_regression.log) | 首轮缺测试输入/tmp及WORKSPACE_PATH不匹配的完整日志 |
| [recovery_attempt1.log](recovery_attempt1.log) | 首次恢复因绝对技能链接被安全解包拒绝的记录 |
| [recovery_config_validation.json](recovery_config_validation.json) | 独立恢复60配置与600profile官方验收 |
| [recovery_config_validation.log](recovery_config_validation.log) | 独立恢复配置验收日志 |
| [recovery_structure.json](recovery_structure.json) | 干净基线应用补丁与镜像的78文件一致性 |
| [recovery_structure.log](recovery_structure.log) | 恢复结构核验日志 |
| [recovery_tests.json](recovery_tests.json) | 独立恢复42项测试统计 |
| [recovery_tests.log](recovery_tests.log) | 独立恢复42项完整日志 |
| [regression_attempt2.json](regression_attempt2.json) | 42项新旧测试全部通过统计 |
| [regression_attempt2.log](regression_attempt2.log) | 42项通过的完整日志 |
| [review.md](review.md) | 独立只读审查结论 |

| [archive/](archive/README.md) | 本轮独立恢复、原始SHA、worktree精确保全与安全解除登记、迁移及凭据核对 |
