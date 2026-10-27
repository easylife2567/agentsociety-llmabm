# 逐行动记录

父级见[结果索引](../README.md)。本目录111个`<condition>_<arm>_s<seed>.jsonl.gz`：108补充条件及3个baseline s0复现。其余6个baseline原单元直接引用run父级action_audits/current文件，不复制。

每行保存固定门槛A、B、全精度U、随机微扰、行动/预热身份、实际feed键/来源/类别、此前累计接触、候选池与发言结果。候选原函数的components_rounded只供展示，决策使用全精度u；替代函数另有全精度D/R。原始记录不能用显示舍入值回推门槛决策。名称条件与矩阵见manifest，逐文件哈希见analysis.json。
