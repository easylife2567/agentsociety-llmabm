# 隔离工作区保全

原workspace有价值tracked/untracked状态逐项保全。机器进度仅作历史恢复，不覆盖主区状态。

- .agentsociety/：进度、候选claims/分析配置、17条运行记录和13个历史锁。
- hypothesis_4/experiment_4/：原配置和实验导航；runs/cuc_model_v1相对映射到本归档raw_outputs。
- hypothesis_4_cuc/：假设与实验相对链接。
- presentation/hypothesis_4_cuc/、synthesis/：全部报告、图、数据与综合。
- custom：指向固定基线源码快照。

原位置/新位置/字节指纹及原symlink字符串见../recovery/workspace_preservation.json。本目录不是可启动实验的Git worktree；原登记在核验后解除。
