# 新一轮打标的产出目录（data/runs/）

每次全量打标在此落地三个文件（`<slug>` 为运行标识）：

| 文件 | 是否入库 | 说明 |
|---|---|---|
| `抖音微博小红书-独立重打标_<slug>.xlsx` | ✅ 入库 | 成品：原表 57 列，前三列替换为该轮判定 |
| `.label_results_<slug>.jsonl` | ❌ 忽略 | 断点：逐行判定结果，续跑依据；可由 `recover_assemble.py <slug>` 重新装配 xlsx |
| `.label_progress_<slug>.json` | ❌ 忽略 | 进度快照，供外部监控读取 |

## 当前状态

| slug | 模型 | 提示词口径 | 状态 |
|---|---|---|---|
| `R1prompt_Seed2_1_lite` | `doubao-seed-2-1-lite-260915` | 第1轮 | ⏳ 待跑 |
| `R1prompt_GLM5_3flash` | `glm-5-3-flash-260828` | 第1轮 | ⏳ 待跑 |

> `R1prompt_V4_1`（deepseek-v4.1 × 第1轮口径）曾跑到 3,400/52,736 后弃用：原标模型（v4-flash）
> 本身已是第 1 轮口径，无需再用 V4.1 补这一格。断点已于 2026-09-27 删除。

## 续跑

直接重跑同一命令即可：脚本会读断点 JSONL、跳过已完成行。

```bash
PY=$(grep "^PYTHON_PATH=" .env | cut -d'=' -f2); PY=${PY:-python3}
nohup $PY -u data/scripts/batch_label_r1prompt.py <模型ID> <slug> 24 8 > /tmp/<slug>.log 2>&1 &
```

若某轮全部跑完但装配失败（脚本退出码 2），断点仍在，用 `recover_assemble.py <slug>` 重新装配。

## 弃跑与清理

断点与进度文件都不入库，删除不影响仓库。若某轮确认不再需要，删掉
`.label_results_<slug>.jsonl` 与 `.label_progress_<slug>.json` 即可；
日后想补，重跑同一命令会从头开始。
