# 配置准备与离线证据

| 直接资产 | 用途 |
|---|---|
| [preparation-start.json](preparation-start.json) | 本轮开始的Git状态、主批33项来源哈希、未携入测试差异及凭据边界 |
| [dependencies.json](dependencies.json) | Python、AgentSociety2 2.8.4及依赖版本、SDK commit和官方配置工具哈希 |
| final-check.json | 收尾的33项主来源、45项恢复包、配置/文档链接、Git边界及账本未创建核对 |
| launch-check.json | 正式启动前40项冻结检查及异常状态识别的定向控制器测试；不能代替完整CLI启动验收 |
| automation.json | 30分钟定时器id、创建状态及本次失败停止后的暂停记录 |
| [startup-failure/](startup-failure/README.md) | 首条件官方入口403失败、控制器停止及原始启动源快照，0模型调用 |
| [layout-fix/](layout-fix/README.md) | 输出布局补丁起点/最终源、镜像与剩余预算检查、完整CLI入口禁网验收及第二次启动核对 |
| [parallel/](parallel/README.md) | 两路调度的准确起点、最终源/补丁重放、禁网合成检查、串行接管快照和实际接管检查 |
| [verification/](verification/README.md) | 原隔离worktree的官方操作、九配置功能和继承检查；含真实失败证据 |
| [recovery/](recovery/README.md) | 第二个干净worktree从恢复包重新生成和复验的记录，RESULT.json为核验摘要 |

配置/入口功能验收的真实LLM和网络调用为0；固定返回及无生成调度不能证明模型正文质量、产量或消融效应。正式LLM第二次启动后的真实调用与进度见results/timestamp_bdr_v1_attempt_02，不能沿用验收的零调用计数。

## 本轮遇到并修正的问题

1. 初次setup沿用了进程原WORKSPACE_PATH，registry拒绝加载新路径（403）；验收进程现在将WORKSPACE_PATH和AGENTSOCIETY_WORKSPACE都显式指向自身隔离根，没有修改全局配置或正式代码。
2. 新编写的合成行动快照最初缺少正式接口要求的meme_env键，导致before_decision失败；补齐测试快照后通过。两次定位日志保留于verification/verify.failure-01.log和02.log，没有通过放宽正式快照检查来绕过。
3. 首次继承检查中25项通过、1项因缺少旧诊断的Agent50保存记录报错；将一份原始42KB历史输入冻结到test_inputs并校验SHA256，之后26项全部通过。原失败日志及继承失败详情保留，已有测试未改。

没有为上述问题改动custom、重新标定参数、调用LLM或复制整个历史结果目录。
