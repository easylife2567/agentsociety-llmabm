# weekly_lag1 实现审阅单

日期：2026-09-27。状态：代码与配置就绪，正式实验未启动。

## 实际改了什么

`CurationDynamicsSpace`新增三个默认关闭的周级配置项：普通真实帖滞后周数、首周历史样本路径、同周进入的官方帖子ID。只有6份新`interest/random`配置开启它们，旧配置仍按原周注入，`chronological`仍走原小时级路径。

新路径会同时保存三个周字段：`source_week`是帖子产生周，`available_week`是具备推荐资格的周，`injected_week`是实际进入池的周。帖子年龄始终从`source_week`计算。checkpoint还保存注入策略和已进入的外部source key；策略不匹配时拒绝恢复，防止混用旧run目录。

## 本轮输入如何流动

| 模拟周 | 本轮新进入的外部内容 | 数量 |
|---|---|---:|
| W12 | W11初始化历史 | 17 |
| W13 | W12普通帖 + W13官方讣告 | 18 |
| W14 | W13普通帖，不含已进入的讣告 | 34 |
| W15–W22 | 依次来自上一周普通帖 | 30, 24, 22, 19, 18, 18, 20, 23 |

窗口内合计243条。源于W22的24条普通帖子保留在原250条样本中，但要到W23才能进入，所以本轮不会使用。

## 已通过的检查

- 3份W11样本各17条，来源均为W11；每seed独立抽样。
- 6份配置除新增的三个时机字段外，与对应`anchored_v1`基线逐值一致。
- W15普通真实帖在W15不可见，在W16进入且仍记录为W15来源。
- W15真实帖和W15 Agent帖在W16首次可见时生命值相同，均为1周龄。
- 讣告只在W13进入一次；interest在W13置顶，random不置顶；W14不重复、不延长置顶。
- 实际逐周进入量为17/18/34/30/24/22/19/18/18/20/23，总量243。
- checkpoint恢复后不重复注入初始化内容、普通真实帖或讣告。
- 旧版完整离线门禁25/25通过；AgentSociety配置`validate`和`check`通过。
- 专用批跑入口只执行过`--dry-run`，列出的6个run全部为pending。

## 审核通过后才会执行

运行入口：

```bash
$PYTHON_PATH hypothesis_4/experiment_1/run_weekly_lag_batch.py --with-monitor
```

它只会启动`weekly_lag1_interest_s0..s2`和`weekly_lag1_random_s0..s2`，输出到独立的`runs/weekly_lag1/`目录，不覆盖旧结果。
