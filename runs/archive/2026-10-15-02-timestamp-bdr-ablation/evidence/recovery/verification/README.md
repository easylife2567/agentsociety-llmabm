# 独立恢复验收产物

| 文件组 | 用途 |
|---|---|
| validate.json、info.json、prepare.json、run.json、check.json | 恢复后再次执行的官方配置操作结果 |
| setup.json、generate.json | 恢复后实际custom加载路径及阶段通过记录 |
| [verify.json](verify.json)、bdr-functional.json | 恢复后900 profile、8100公式、45固定返回行动、九窗口及26继承测试结果 |
| inherited-tests.log | 恢复后26项测试全部通过的执行日志 |

该目录是恢复核验时原样复制的证据，没有真实LLM请求、正式消融曲线或新模型产量。
