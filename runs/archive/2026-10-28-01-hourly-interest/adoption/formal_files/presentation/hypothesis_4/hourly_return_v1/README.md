# 已采用的三臂小时回流主实验分析

本级承接用户明确采用的小时回流方案与三臂各10seed结果。新版random/interest共20个完整run与历史chronological共10个完整run组成正式比较矩阵；旧周回流结果和旧组件消融各按历史制度保留，不与新版Full混搭。

| 直接资产 | 用途 |
|---|---|
| [report.md](report.md) | 三臂均值、DTW稳定性、玩梗传播结果与限制 |
| [manuscript_impact.md](manuscript_impact.md) | 用户提供DOCX的对应修改评估，正文暂不直接修改 |
| contract.json | 冻结统计口径、五类配色与DTW定义；仅必要正式输入来源 |
| analyze_seed10.py | 从正式manifest和30run实际记录/官方replay重算，禁止网络连接 |
| plot_seed10.py | 原Agent发言量样式三臂均值图与逐seed DTW图 |
| [inputs/](inputs/README.md) | 三项冻结现实效标/审计/DTW函数 |
| [results/](results/README.md) | 330行周表、30run指标、配对、汇总和对齐路径 |
| [assets/](assets/README.md) | 两图PNG/SVG、来源哈希 |
| [verification/](verification/README.md) | 独立核验原件与正式位置实际复算/一致性记录 |

从项目根离线复算，不会启动仿真或发送模型请求：

```bash
/Users/easylife/Project/AgentSociety/AgentSociety2/.venv/bin/python presentation/hypothesis_4/hourly_return_v1/analyze_seed10.py --check
/Users/easylife/Project/AgentSociety/AgentSociety2/.venv/bin/python presentation/hypothesis_4/hourly_return_v1/plot_seed10.py
```

实际验证：正式路径的30run原始记录及官方replay通过，7份数据`--check`逐字节一致；科学数据与落地前逐项一致，两张PNG逐字节一致且已实际查看。首次时序碎片来源缺项及后续补齐记录均保留在verification。

正式矩阵为hypothesis_4/experiment_2/runs/hourly_return_v1/manifest.json，原始结果从正式路径加载；代码与输入不依赖活跃探索run。实际原始metadata与历史审计中的旧绝对路径保留作溯源，不据此加载数据。落地前后数值应相同，合约哈希与来源路径变化分别记录，不用直接比较含路径的整份provenance字节。

DTW以每run独立计算后汇总，误差棒为样本SD，均值轨迹DTW独立列示。兴趣平均拟合优势不等于所有seed第一或晚期玩梗传播最多；同模型seed3–9、去先导seed0和逐一剔除seed检查保留。
