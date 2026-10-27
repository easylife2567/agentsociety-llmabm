# 图5：十种子消融图件及交付扩展

2026-10-26用户确认图5实验已跑完，要求按现有科研图规范补制。本次新增图5脚本与原始结果提取脚本，在原制图run内读取40个实际完成运行单元：10个复用Full和30个B/D/R干预。图1—4、其CSV、旧三种子候选与修订Word字节保持。

| 资产 | 用途 |
|---|---|
| baseline.json | Git基线、两个既有代码文件的任务起点指纹及受保护资产指纹 |
| baseline/scripts/ | validate_delivery.py、package_delivery.py的任务起点精确副本 |
| fig5_delivery_extension.patch | 相对上述副本的最终代码补丁，仅扩展五图验收与打包 |
| checks.json | 补丁独立重放、旧资产未变、40run/10seed身份与新提取脚本指纹 |

基线commit为69d243955d341444ae769fae5bf23dc160465cd6。本run原脚本仍未跟踪，恢复起点以所存实际副本为准；最终补丁已通过git apply --check、应用并在仅含两个起始文件的临时目录中重放，与最终文件逐字节一致。新增gen_fig5.py与extract_fig5_seed10.py直接保留最终实现；图5绘图仅需本级上两级的冻结CSV，共享样式不变。完整复算依赖来源JSON所列原始资产，交付ZIP内CSV足以离线重绘，不声称ZIP包含全部原始仿真。

实际数据核验见上一级fig5_extraction.json；新版图面与指定模型审查见上一级REVIEW.md；五图结构和排版检查见delivery_checks.json。数据对账覆盖4,000份Agent、44,000条唯一决策、80条官方只读SQL及18,108项既有来源指纹，没有重新运行仿真或改动正式分析流水线。
