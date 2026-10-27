# 干净基线恢复核验

| 直接资产 | 用途 |
|---|---|
| [RESULT.json](RESULT.json) | 精确commit、45文件核验、三阶段通过、重生成一致和源变更拒绝；临时worktree已安全解除 |
| setup.log、generate.log、verify.log | 从第二个干净worktree实际执行对应阶段的输出 |
| source-rejection.log | 故意给测试副本输入追加换行后，生成器在写输出前拒绝的预期错误；输入随后恢复原字节 |
| [verification/](verification/README.md) | 第二次独立验收所产JSON及继承测试日志副本 |

本核验只使用恢复包、准确Git基线和记录的SDK/官方技能环境，不使用原workspace。输出一致性和所有通过记录保存后，才解除临时worktree；原隔离workspace继续保留。
