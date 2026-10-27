# 原隔离工作区验收

| 文件 | 用途 |
|---|---|
| validate.json、info.json、prepare.json、run.json、check.json | 现有官方配置工具对应操作结果；run只是生成器，不是LLM运行 |
| setup.json、generate.json及同名log | 官方操作及实际custom加载路径、网络/Provider拦截计数 |
| [verify.json](verify.json) | 最终通过：900实际profile、8100公式检查、45组固定正文发布/空feed、九完整窗口、26继承测试 |
| bdr-functional.json | 九配置差异、实际profile/公式和环境恢复的明细；继承测试前保存 |
| verify.log、inherited-tests.log | 最终执行日志，0失败、0错误、0跳过 |
| verify.failure-01.log、verify.failure-02.log | 合成快照漏meme_env键的定位记录 |
| verify.failure-03.log、inherited-tests.failure-01.log | 继承测试缺历史样本的原始失败，不覆盖或删除 |

九个环境窗口均693批、1100唯一Agent×周机会、11周、未来曝光0、W13悼念22人均在官方资格后行动；无Agent生成回流的窗口用于时间验收，不是闭环产量预测。45组行动使用固定正文调用实际发布路径，另验重复行动、Agent恢复及空feed不生成。
