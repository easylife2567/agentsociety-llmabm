# 归档：正式 9-run 批跑之前的单 run CSV 导出

来源：烟测 `interest_s0`（2026-09-12，R=15 定标前）经 `plot_run_charts.py` 导出。

移出 `data/` 顶层的原因：`plot_run_charts.py` 早期把周度表写成 `data/` 下的**固定
文件名**，9 个正式 run 顺序导出时会互相覆盖（最后跑完的 run 静默胜出）。已改为
按 run 分目录 `data/<run_id>/weekly_*.csv`；这些旧文件留在顶层会被误当作正式产物。

保留作审计线索，不参与当前分析。
