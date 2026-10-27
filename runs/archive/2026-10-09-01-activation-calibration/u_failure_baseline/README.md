# 首轮复现失败保全

首次运行在random s0原规则等同检查中停止，尚未开始108个科学条件。原因是profile保存B=0.7678，既有标定复算B=0.7677999999999999；全字段严格等同比较检出差异。改为读取既有baseline_evidence精确B后，三制度3300条记录全部逐字段一致，未改变科学矩阵或判据。

本目录保留SHA256与当时manifest严格一致的[u_experiments.failed.py](u_experiments.failed.py)（失败版本，勿作为当前入口）、当时manifest.json、static_mapping.csv/json、action_audits/baseline_random_s0.jsonl.gz和cell_metrics/baseline_random_s0.json。原失败日志在[u_failure_baseline.log](../u_failure_baseline.log)，有效结果在[u_results](../u_results/README.md)。本失败包不得当作已完成实验结果。
