# 盲法判类分析：文本类别 vs 身份标签（W2 整改）

- 判类模型：GLM（`glm-5-3-flash-260828`），生成模型为 `deepseek-v4-flash`。
- 判定标准：与真实帖文打标完全相同的 prompt（AST 取自 `batch_label_v3.py`）。
- 输入：仅正文；不含 arm、身份、周次、四词表。覆盖 1887/1904 条。

## 1. 三种口径下的类别分布

| 口径 | 玩梗 | 悼念 | 教育 | 营销 | 其他 | 噪音 |
|---|---|---|---|---|---|---|
| pool_type（身份，论文现用） | 274 | 318 | 363 | 693 | 239 | 0 |
| env_assigned_type（环境四词表复核） | 32 | 1088 | 14 | 751 | 2 | 0 |
| blind_type（盲法文本判类） | 266 | 531 | 347 | 694 | 48 | 1 |

## 2. 一致性：身份标签到底能不能代表文本

| 比较 | 一致率 | Cohen's κ |
|---|---|---|
| 身份 vs 盲法文本 | 86.5% | 0.822 |
| 身份 vs 环境四词表复核 | 42.2% | 0.233 |
| 环境四词表复核 vs 盲法文本 | 52.8% | 0.314 |

### 身份 → 盲法文本 错配矩阵（行=身份，列=盲法判类，行内占比）

| 身份＼文本 | 玩梗 | 悼念 | 教育 | 营销 | 其他 | 噪音 | 行合计 |
|---|---|---|---|---|---|---|---|
| 玩梗 | 266 (97%) | 0 (0%) | 5 (2%) | 2 (1%) | 0 (0%) | 1 (0%) | 274 |
| 悼念 | 0 (0%) | 318 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 318 |
| 教育 | 0 (0%) | 54 (15%) | 309 (85%) | 0 (0%) | 0 (0%) | 0 (0%) | 363 |
| 营销 | 0 (0%) | 2 (0%) | 0 (0%) | 691 (100%) | 0 (0%) | 0 (0%) | 693 |
| 其他 | 0 (0%) | 157 (66%) | 33 (14%) | 1 (0%) | 48 (20%) | 0 (0%) | 239 |

## 3. 周级玩梗供给份额：身份口径 vs 文本口径（3 seed 均值）

| 臂 | 周 | 身份口径 | 文本口径 |
|---|---|---|---|
| random | W12 | 0.0% | 0.0% |
| random | W13 | 0.0% | 0.0% |
| random | W14 | 0.0% | 0.0% |
| random | W15 | 0.0% | 0.0% |
| random | W16 | 0.0% | 0.0% |
| random | W17 | 0.0% | 0.0% |
| random | W18 | 0.0% | 0.0% |
| random | W19 | 0.0% | 0.0% |
| random | W20 | 4.2% | 4.2% |
| random | W21 | 28.9% | 28.9% |
| random | W22 | 44.3% | 37.6% |
| chronological | W12 | 0.0% | 0.0% |
| chronological | W13 | 0.0% | 0.0% |
| chronological | W14 | 0.0% | 0.0% |
| chronological | W15 | 0.0% | 0.0% |
| chronological | W16 | 0.0% | 0.0% |
| chronological | W17 | 0.0% | 0.0% |
| chronological | W18 | 0.0% | 0.0% |
| chronological | W19 | 0.0% | 0.0% |
| chronological | W20 | 66.2% | 66.2% |
| chronological | W21 | 85.6% | 84.1% |
| chronological | W22 | 83.0% | 83.0% |
| interest | W12 | 0.0% | 0.0% |
| interest | W13 | 0.0% | 0.0% |
| interest | W14 | 0.0% | 0.0% |
| interest | W15 | 0.0% | 0.0% |
| interest | W16 | 5.0% | 5.0% |
| interest | W17 | 1.9% | 1.9% |
| interest | W18 | 0.0% | 0.0% |
| interest | W19 | 4.8% | 4.8% |
| interest | W20 | 70.9% | 66.6% |
| interest | W21 | 82.6% | 79.3% |
| interest | W22 | 82.8% | 81.2% |

## 4. 三臂 DTW：身份口径 vs 文本口径

### 效标 = DeepSeek

| 口径 | 排序（由优到劣） | random 均值±sd [min,max] | chronological 均值±sd [min,max] | interest 均值±sd [min,max] |
|---|---|---|---|---|
| 身份 pool_type | interest > random > chronological | 23.71±3.53 [19.91, 26.89] | 26.89±3.34 [24.06, 30.57] | 21.84±2.17 [19.69, 24.03] |
| 文本 blind_type | interest > random > chronological | 32.44±0.38 [32.16, 32.88] | 34.89±2.40 [32.52, 37.33] | 28.25±5.86 [23.12, 34.64] |

### 效标 = doubao-seed

| 口径 | 排序（由优到劣） | random 均值±sd [min,max] | chronological 均值±sd [min,max] | interest 均值±sd [min,max] |
|---|---|---|---|---|
| 身份 pool_type | random > interest > chronological | 30.40±1.32 [29.38, 31.89] | 38.51±1.66 [36.99, 40.28] | 33.68±1.55 [32.19, 35.28] |
| 文本 blind_type | random > chronological > interest | 32.16±2.31 [29.52, 33.80] | 37.84±5.21 [31.92, 41.75] | 38.04±2.59 [35.30, 40.44] |

### 效标 = GLM

| 口径 | 排序（由优到劣） | random 均值±sd [min,max] | chronological 均值±sd [min,max] | interest 均值±sd [min,max] |
|---|---|---|---|---|
| 身份 pool_type | random > interest > chronological | 25.65±0.83 [25.06, 26.60] | 31.20±2.45 [29.18, 33.92] | 25.98±2.66 [23.38, 28.69] |
| 文本 blind_type | random > interest > chronological | 27.82±1.39 [26.42, 29.20] | 31.77±4.12 [27.07, 34.76] | 30.27±4.86 [24.69, 33.56] |

### 效标 = DeepSeek-V4.1

| 口径 | 排序（由优到劣） | random 均值±sd [min,max] | chronological 均值±sd [min,max] | interest 均值±sd [min,max] |
|---|---|---|---|---|
| 身份 pool_type | random > interest > chronological | 25.60±0.57 [25.11, 26.22] | 33.78±1.73 [32.15, 35.60] | 27.97±2.41 [25.58, 30.40] |
| 文本 blind_type | random > interest > chronological | 27.34±1.41 [25.76, 28.49] | 34.06±2.76 [30.97, 36.27] | 32.07±4.94 [26.41, 35.50] |

