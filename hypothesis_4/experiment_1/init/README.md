# 实验配置与冻结输入

后续采用timestamp_v1主设计，见[EXPERIMENT.md](../EXPERIMENT.md)。本目录尚未生成该版本配置；现有默认配置和生成脚本不等同新设计的可启动入口。新配置准备需独立manifest和预算，不导入会覆盖旧配置的生成器。

| 资产 | 作用 |
|---|---|
| [arrival_timing_diagnostic/](arrival_timing_diagnostic/README.md) | 独立四格到达时机诊断配置、行动表及manifest |
| `configs/` | 已有批次的分臂配置与清单 |
| `config_params.py` | 既有主实验配置生成入口；导入可能写配置，不用于本次诊断 |
| `holdout_config.py` | 既有留出条件配置生成入口 |
| `weekly_lag_config.py` | 既有周滞后条件生成入口 |
| `weekly_lag_event_v2_config.py` | 历史事件修订配置生成入口 |
| `init_config.json` | 既有默认配置；新诊断通过独立路径启动 |
| `injection_sample_s0.json`、`injection_sample_s1.json`、`injection_sample_s2.json` | 各seed冻结真实帖样本 |
| `injection_sample_holdout_s0.json`、`injection_sample_holdout_s1.json`、`injection_sample_holdout_s2.json` | 各seed留出样本 |
| `initial_sample_weekly_lag_s0.json`、`initial_sample_weekly_lag_s1.json`、`initial_sample_weekly_lag_s2.json` | 各seed历史初始池 |
| `steps.yaml` | 既有周级步骤 |
| `steps_chronological_hourly.yaml` | 既有chronological小时步骤 |
| `steps_weekly_lag.yaml` | 既有周滞后步骤 |
| `steps_weekly_lag1_event_v2.yaml` | 历史事件修订步骤 |

缓存文件不属于研究资产。启动到达诊断以其独立manifest为准，不更新主实验默认配置或兼容run链接。
