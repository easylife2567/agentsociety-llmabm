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
| `R1prompt_V4_1` | `deepseek-v4-1-flash-260910` | 第1轮 | ⏸ 中断于 3,400 / 52,736（6.4%），断点在位、可续跑；此格为旁支，不在「doubao + GLM」两轮计划内 |
| `R1prompt_Seed2_1_lite` | `doubao-seed-2-1-lite-260915` | 第1轮 | ⏳ 待跑 |
| `R1prompt_GLM5_3flash` | `glm-5-3-flash-260828` | 第1轮 | ⏳ 待跑 |

## 续跑

直接重跑同一命令即可：脚本会读断点 JSONL、跳过已完成行。

```bash
PY=$(grep "^PYTHON_PATH=" .env | cut -d'=' -f2); PY=${PY:-python3}
nohup $PY -u data/scripts/batch_label_r1prompt.py <模型ID> <slug> 24 8 > /tmp/<slug>.log 2>&1 &
```

若某轮全部跑完但装配失败（脚本退出码 2），断点仍在，用 `recover_assemble.py <slug>` 重新装配。

## 旁支断点的处置

`R1prompt_V4_1` 的 3,400 条若确认不再需要，删除 `.label_results_R1prompt_V4_1.jsonl`
与 `.label_progress_R1prompt_V4_1.json` 即可（两者均不入库，删除不影响仓库）。
若日后想补齐，重跑上面命令即从 3,400 续起。
