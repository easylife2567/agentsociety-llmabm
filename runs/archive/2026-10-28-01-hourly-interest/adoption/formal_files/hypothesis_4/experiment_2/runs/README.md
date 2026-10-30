# 正式主实验运行资产

父级状态见[实验README](../README.md)。

| 目录 | 用途 |
|---|---|
| [hourly_return_v1/](hourly_return_v1/README.md) | 当前统一小时回流主实验：新随机/兴趣20次原始结果与时序10次复用矩阵，保留原始来源和执行记录 |
| [timestamp_v1/](timestamp_v1/README.md) | 旧回流制度三臂30次完整结果，保留恢复、中断及执行历史；其中时序10次亦由新版复用 |

seed3–9已于2026-10-24并入timestamp_v1，不再单列timestamp_v1_seed3_9实验目录。旧证据中的历史路径通过timestamp_v1/relocation.json定位，原字节保持。
