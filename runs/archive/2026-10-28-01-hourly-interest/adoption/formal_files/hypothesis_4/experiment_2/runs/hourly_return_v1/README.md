# 统一小时回流的正式主实验结果

用户于2026-10-29明确授权将小时回流方案和完成结果落地到主工作区。父级[实验README](../../README.md)是实时状态入口。

本级接收随机/兴趣各10个完整seed（先导seed0和新增seed1–9），保留原run_id及所有原始文件；时序10seed继续引用兄弟目录timestamp_v1的既有完整结果，不复制成“新跑时序”。30个比较单元的实际路径、模型及冻结文件见manifest.json。撤回的部分时序、旧周回流随机/兴趣及组件消融不进入本矩阵。

| 直接资产 | 用途 |
|---|---|
| manifest.json | 30run实际正式路径、每run冻结原始SHA、模型/请求及正式现实输入路径；供只读复算使用 |
| relocation.json | 20份复制来源→正式位置的逐文件哈希、时序10份复用位置；原位置没有删除 |
| execution_records/ | 原pilot、补种子计划/状态/账本及完成/审计证据的原字节副本；内部历史绝对路径仅供溯源 |
| hourly_return_pilot_random_s0/、hourly_return_pilot_interest_s0/ | 两个已完成先导seed0，保留原名 |
| hourly_return_v1_random_s1/ … s9/ | 九个新增随机完整运行 |
| hourly_return_v1_interest_s1/ … s9/ | 九个新增兴趣完整运行 |

完整原始输出被本级.gitignore忽略，但属于必要证据，不能清理为缓存。原始metadata、日志、SOCIETY、checkpoint和replay中的历史路径不改写；分析从manifest解析正式位置，不依赖探索run或其workspace。

本次复制并核对20个原始run，随机1702帖、兴趣2185帖；时序复用2154帖，共6041帖。每run均693步、1100唯一行动/决策、100人、11周。成功正文中新两臂均261017；历史时序seed0–2返回无日期别名，seed3–9为261017，分析另列同版7seed。正式结果与[分析报告](../../../../presentation/hypothesis_4/hourly_return_v1/README.md)相互回指。

本级没有新运行授权，也不提供会自动启动实验的入口。历史extra账本分别保留，不清零、不合并额度。新代码缺省legacy以兼容历史配置，新版主实验的30份配置显式next_batch。
