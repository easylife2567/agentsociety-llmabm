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
| `R1prompt_Seed2_1_lite` | `doubao-seed-2-1-lite-260915` | 第1轮 | ✅ 完成 52,733/52,736（3 条服务端内容过滤，见下） |
| `R1prompt_GLM5_3flash` | `glm-5-3-flash-260828` | 第1轮 | ⏳ 待跑 |

### 本轮 3 条「未判定」行

`R1prompt_Seed2_1_lite` 有 3 行（11772、21741、21745）**无法通过该端点判定**：服务端内容过滤
在生成前即拦截（`finish_reason=content_filter`、`completion_tokens=0`、亚秒返回），换批次、
重复 8 次、换提示词口径均被拦。经用户确认，这 3 行在产出表中以
`数据有效性=未判定 / 内容类别=未判定 / 判定依据=[服务端内容过滤]` **显式留痕，不伪造标签**；
`compare_r1prompt.py` 按行索引在三个文件上同步剔除，不参与任何统计（占 0.0057%）。

另有 16 条曾整批拒答，其中 13 条按**原批次去掉触发行的分组**重打成功，调用结构保持 8 条/批。

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
