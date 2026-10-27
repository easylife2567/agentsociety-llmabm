# 实际官方CLI入口禁网验收

| 直接资产 | 用途 |
|---|---|
| [RESULT.json](RESULT.json) | 九个新布局入口通过、旧布局拒绝、900实际profile、九全窗及零网络/LLM摘要 |
| old_layout_rejected.log | 在新的测试目录复现旧布局403，不覆盖原失败日志 |
| timestamp_bdr_v1_interest_no_b_s0等九份JSON | 各配置的实际SDK main路径、真实模块来源、profile、693环境批次/1100机会/11周及恢复核对 |
| 对应九份log | 完整官方python -m命令实际执行的日志 |

真实CLI读取原冻结config和steps、验证环境和路径、扫描隔离custom后，在模型/Ray初始化边界由专用钩子接管；钩子使用真实Agent和环境类完成全窗验收再退出。没有创建Ray集群或请求模型，不能将这些窗口称为九次完整LLM仿真。正式运行不加载此钩子，实际启动后的记录另存第二次results。
