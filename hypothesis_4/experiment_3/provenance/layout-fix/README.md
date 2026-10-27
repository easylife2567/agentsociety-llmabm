# 输出布局修正与重新启动证据

| 直接资产 | 用途 |
|---|---|
| [baseline.json](baseline.json) | 本轮准确Git起点、控制器起始哈希和目标路径；起始控制器未进入HEAD，按实际文件保全 |
| run_ablation.before.py | 本轮起始控制源，与首次失败的runtime_plan哈希一致 |
| run_ablation.final.py | 当前最终控制源，与应用后的控制器一致；从before应用run根output-layout.patch可重建 |
| [control-check.json](control-check.json) | 补丁从起点重新应用、原子镜像/部分JSON、最终镜像哈希、原绝对截止和异常拒绝检查 |
| [cli-entry/](cli-entry/README.md) | 旧布局反例与九个真实官方命令入口的禁网验收 |
| restart-check.json | 第二次启动后的实际模块根、进程/行动、镜像、原失败保全及定时器恢复核对 |
| isolated-pipeline.json | 仅隔离区通过官方CLI登记run_experiment=in_progress的快照 |

SDK和科学配置未改。本轮已有代码只修改run控制器，通过保存的output-layout.patch先check再apply；在独立临时副本重建后与最终源逐字节一致。配置阶段原45文件恢复包保持原样；恢复本控制器时先把before副本放回baseline.json指定目标，再应用该最终补丁。

实际输出现在物理位于隔离workspace，持久镜像在本run results第二次目录；没有通过增加custom副本、指回主项目或放开路径安全策略来绕过403。首次失败目录、日志和源码快照均保留。原截止时刻不延长，重启获用户本次明确授权，不是自动重试。
