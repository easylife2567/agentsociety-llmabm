# U补充检验原始结果

父级状态在[run README](../README.md)，解释见[结果报告](../u_results_report.md)，规则与判据见[冻结协议](../u_protocol.md)。全部是固定正文离线代理，LLM调用与网络尝试均为零。

| 直接资产 | 内容 |
|---|---|
| [manifest.json](manifest.json) | 条件、预算、基线及执行脚本/协议/父冻结包SHA256 |
| [completion.json](completion.json) | 108新增单元、108900发帖机会、三原单元验同与实际耗时 |
| [static_mapping.csv](static_mapping.csv)、[static_mapping.json](static_mapping.json) | 30行：6规则设置×5类，精确概率及100000轮抽样 |
| [weekly_metrics.csv](weekly_metrics.csv) | 执行时全条件/类型/周次统计；包含W12预热记录 |
| [trajectory_summary.csv](trajectory_summary.csv) | 117条件单元×5类型，事件后与晚期数量、份额、峰周、曝光 |
| [audited_weekly.csv](audited_weekly.csv) | 独立从逐行动记录重算的周统计 |
| [transfer_diagnostic.csv](transfer_diagnostic.csv) | 事后W13–W18共同尺度供给误差诊断，不作为条件选择或独立验证 |
| [effects.csv](effects.csv) | 逐seed、均值、范围、相对候选/原规则与随机制度差值 |
| [analysis.json](analysis.json) | 完整效应与117原始审计的独立核验；9原单元引用父级旧审计 |
| [action_audits/](action_audits/README.md) | 111新压缩逐行动记录（108实验＋3原规则验同） |
| [cell_metrics/](cell_metrics/README.md) | 对应111单元周统计、审计哈希及执行断言 |

不要覆盖或重复写入该目录。复现实验使用新的输出目录；输入必须取父级frozen，源码取记录commit。两单元实际独立恢复及边界见[u_recovery.json](../u_recovery.json)。
