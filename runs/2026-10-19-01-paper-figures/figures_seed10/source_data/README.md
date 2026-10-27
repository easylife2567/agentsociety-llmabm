# 图1—5冻结作图数据

| 文件 | 用途 |
|---|---|
| observed_weekly.csv | 图1、2；270行：两平台与合并×18周×五类；count、total_five、share |
| observed_sources.json、observed_checks.json | 原编码来源、筛选账、五类分母与已核验结果 |
| seed10_runs.csv | 图3d、图4；30行，每制度10seed；晚期运行级份额和过程指标 |
| seed10_weekly.csv | 图3a—c；330行，30run×11周，含五种固定作者供给 |
| seed10_arm_summary.csv、seed10_weekly_summary.csv | 汇总参照，主分析必须筛all10；old3/new7是补充口径 |
| seed10_paired_contrasts.csv | 既有配对分析参照，本轮图件未加显著性星号或置信区间 |
| seed10_sources.json、seed10_verification.json | 原分析的3416项来源指纹、重试/恢复选择、旧结果复现和独立核验记录 |
| analysis_summary.json | 用户已采纳的模型版本等价约定及主分析范围 |
| ablation_seed10_metrics.csv | 图5五面板×每条件10种子×Full/干预，共100行，保留分子/分母与单位 |
| ablation_seed10_runs.csv、ablation_seed10_weekly.csv | 40个实际完成run汇总及逐周供给/发言量 |
| ablation_seed10_sources.json | 图5逐源指纹、实际接续目录、40run模型与30项科学配置配对、输出哈希 |

冻结复制自`paper/figures/source_data/`（现实）及`presentation/hypothesis_4/data/`（十组主实验），不修改原文件。CSV字节与原来源输出SHA256一致。来源JSON保留历史路径；运行资产已整理时，通过正式`experiment_2/runs/timestamp_v1/relocation.json`定位，不改原始证据文字。

实际五类分母46,602，原始语料49,930；周内比例先合并计数再求份额。十组主实验是每制度seed0—9，共30次，不含消融。图4接触/参与/跨群体生成帖展示分母每run为760/76/3240。只读表的重新核验见上一级qa；图1—4沿用此前冻结分析；图5重新读取40run环境/Agent，并经80条官方只读SQL对账。

图5重复单位为同一种子内Full与干预的配对；每条件seed 0—9齐全，Full的10次主运行复用一次，不因出现在多个面板而增加样本量。W19—W22分别计算总供给、玩梗型发言率、作者供给份额及其他作者feed中的全部玩梗内容；W14—W18计算全体发言率。主指标遵循experiment_3已冻结定义，新增7种子沿用既有模型版本等价约定。原三种子面板值逐条复现；未修改任何原始输入或完成记录。
