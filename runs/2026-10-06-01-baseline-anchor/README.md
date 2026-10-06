# 常态锚点：独立数值探索run

## 目标与授权

用户于2026-10-06要求“新开一条run来做试验”，选中的是不依赖W13峰值换算、用已有记录检查新B是否改变发言判定的无LLM诊断。本任务独立于注入时机；不修改正式Agent/环境/冻结配置，不替换anchored_v1，不启动付费生成、不重新拟合alpha_D或lambda。

## 一级资产

| 资产 | 职责 |
|---|---|
| README.md | 授权、进度、决策与交接 |
| [2026-10-06-01-baseline-anchor-check.md](2026-10-06-01-baseline-anchor-check.md) | 实施前口径、验收与同主题结果报告 |
| [2026-10-06-02-check.py](2026-10-06-02-check.py) | 只读输入、计算两种候选B、固定曝光路径逐行动对照 |
| `tmp/` | 可丢弃临时核验，不保存唯一证据 |

正式分析产物保存于[presentation对应目录](../../presentation/hypothesis_4/2026-10-06-01-baseline-anchor/README.md)，通过本入口引用；不创建伪引擎replay。

## 进度与交接

当前数值检查已完成并通过独立终审。9900条旧判定复原零不一致；候选人口尺度／同队列口径分别改变110／220条营销开口判定，无其他类型变化；玩梗人数条件差不变但份额差随营销分母减少增大。原始4次content_empty与18次空feed保留分账。无LLM、无正式代码或冻结配置修改。

方案经独立`baseline_check_review`审查PASS。已采纳使用整数曝光数/实际槽数重建气候建议；旧开口与decision_log.speak一致、posted与replay.spoke一致，生成失败不混入发言判定。工作簿前期类别计数与冻结基准一致，人口计数与原统计一致。

独立终审`baseline_check_review`为PASS：直接读取工作簿复算队列与作者周、逐条用数学公式复算9900条旧/新判定、核对来源哈希及weekly/summary聚合，数字一致；PNG已目视确认统一纵轴和数值诊断标注。用户追加的Agent发言量趋势图已交付PNG/SVG。父级导航、文件链接与Git差异格式检查通过；仅提交本任务资产，不自动推送。

CLI机器阶段为analysis/in_progress、verification partial。官方analysis intake因已有claims阶段阻塞（回执`.agentsociety/analysis/runs/run_20261006t132919_bfcddc5689.json`）；query-data在沙箱内外均报SQLite disk I/O error。本任务以原始分片JSONL与AGENT.json独立读取，不修改harness或宣称全项目analysis完成。

已发现口径边界：人口构成使用W12–W22全窗单类型用户，排除噪音后31770人；此构成包含事件后信息。替换W13峰值尺子不等于消除全部事后信息。固定曝光复算不模拟内容变化及后续推荐反馈。

下一步：审核[同主题结果报告](2026-10-06-01-baseline-anchor-check.md)中的候选取舍与人数/份额边界。尚未采纳新B或重新标定；新增完整LLM运行另行确定。
