# 打标工作目录（data/）

*建立于 2026-09-27。收拢此前散落在工作区根目录的 LLM 内容打标工作：脚本、提示词、基准标签、
历史轮次产出与对比报告。*

## 这项工作是做什么的

对 2026-01-31 → 2026-05-31 三平台（抖音 16,602 / 小红书 33,328 / 微博 2,806）关键词「张雪峰」的
**52,736 条**抓取结果，逐条判定**数据有效性**（有效/无效/存疑）与**内容类别**
（借势营销、爬取噪音、梗文化讨论、事件悼念讨论、教育观点讨论、其他讨论、存疑）。

标签由大语言模型生成，**无人工编码环节**。已另建人工复编码抽检工具包（`paper/spot_check/`）
以补齐可靠性证据，但人工编码尚未执行。

## 目录结构

```
data/
├── baseline/     第 1 轮（基准）全量已打标表 —— 正文使用的主标签
├── prompts/      两套提示词原文
├── scripts/      打标、重试、装配、一致性对比、溯源校验脚本
├── runs/         新一轮打标的产出与断点（进行中）
├── reports/      关于打标工作本身的评审与说明（现行）
└── archive/      第 2/3/4 轮的结果与报告（已归档，见 archive/README.md）
```

## 轮次总表

| 轮次 | 模型 | 提示词口径 | 调用结构 | 产出 | 状态 |
|---|---|---|---|---|---|
| 第1轮（基准） | `deepseek-v4-flash` | **第1轮口径** | Workflow 子代理，352 批 × 150 行，Read/Write 工具 | `baseline/抖音微博小红书-全量已打标.xlsx` | ✅ 完成 52,736 行 |
| 第2轮 | `doubao-seed-2-1-lite-260915` | 后三轮口径 | API，逐条 | `archive/round2_doubao-seed-2.1-lite/` | ✅ 归档 |
| 第3轮 | `glm-5-3-flash-260828` | 后三轮口径 | API，每 8 条 | `archive/round3_glm-5.3-flash/` | ✅ 归档 |
| 第4轮 | `deepseek-v4-1-flash-260910` | 后三轮口径 | API，每 8 条 | `archive/round4_deepseek-v4.1/` | ✅ 归档 |
| 新一轮 A | `doubao-seed-2-1-lite-260915` | **第1轮口径** | API，每 8 条 | `runs/` | ⏸ 待跑 |
| 新一轮 B | `glm-5-3-flash-260828` | **第1轮口径** | API，每 8 条 | `runs/` | ⏸ 待跑 |

（原「旁支」`deepseek-v4-1-flash-260910` × 第1轮口径 跑到 3,400/52,736 后弃用：原标模型
v4-flash 本身就是第 1 轮口径，这一格已有，无需 V4.1 补。断点已于 2026-09-27 删除。）

**两套口径的差别**（第 1 轮 vs 后三轮，逐项差异见 `prompts/label_prompt_round1.md` §C）：

| | 第1轮口径 | 后三轮口径 |
|---|---|---|
| 类别定义 | 本事件特化（写入雪碧梗、巧乐兹梗、「牢张」、天地银行等专名） | 通用定义 |
| 判定核心 | 「张雪峰在句中扮演什么角色」+「拿掉三个字」辅助判定法 | 六步顺序判定 |
| 判定依据 | 硬性 ≤30 字 | 1—2 句话 |
| 有效性与类别 | 强制耦合，「存疑」自成一类 | 相互独立，无「存疑」 |
| 输入字段 | `match_sentence` + 部分行 `ctx_full_content` | 仅 `title` + `content` |

**为什么现在补跑第1轮口径**：第 1 轮提示词于 2026-09-26 从本机历史 Workflow 脚本中恢复
（`prompts/label_prompt_round1.md`）。此前「原标偏离」既可能来自口径差异、也可能来自模型判定质量，
两者不可分离。用同一提示词在别的模型上重跑，才能把口径效应单独量出来。

## 提示词

| 文件 | 口径 | 来源 |
|---|---|---|
| `prompts/label_prompt_round1.md` | 第1轮（基准） | 2026-09-26 从本机 `~/.claude/projects/…/workflows/scripts/zxf-full-labeling-wf_4953f96e-780.js` 恢复，含全文与 SHA-256 指纹 |
| `prompts/label_prompt.md` | 后三轮 | 工作区原有留存 |

## 脚本

| 脚本 | 用途 |
|---|---|
| `scripts/batch_label_r1prompt.py` | **当前在用**：以第 1 轮提示词 + 第 1 轮输入字段全量打标（提示词除 I/O 两段外逐字保留） |
| `scripts/batch_label_v3.py` | 后三轮所用：后三轮口径提示词、API 每 8 条 |
| `scripts/batch_label_v2.py` / `batch_label.py` | 早期版本（逐条 / 更早），保留备查 |
| `scripts/retry_failed.py`、`retry_failed_glm.py` | 失败行单条重试 |
| `scripts/recover_assemble.py` | 由断点 JSONL 重新装配 xlsx |
| `scripts/analyze_failed_v41.py` | 诊断全程失败行 |
| `scripts/compare_labels.py` | 三方一致性与 κ |
| `scripts/compare_labels4.py` | 四方一致性与 κ、多数投票 |
| `scripts/compare_r1prompt.py` | **口径效应 vs 模型效应分解**（见下） |
| `scripts/prompt_provenance_check.py` | 提示词溯源校验：输出端签名、批次数、行数、ctx 行数 |
| `scripts/check_baseline_alignment.py` | **开跑前预检**：新一轮与基线在提示词 / 输入字段 / 行序 / 基线自身四层是否对齐 |

## 运行方式

```bash
PY=$(grep "^PYTHON_PATH=" .env | cut -d'=' -f2); PY=${PY:-python3}

# 0. 开跑前先跑对齐预检（只读，约 1 分钟）：提示词 / 输入字段 / 行序 / 基线自身
$PY data/scripts/check_baseline_alignment.py

# 1. 全量打标：<模型ID> <slug> [并发] [每次调用条数]
nohup $PY -u data/scripts/batch_label_r1prompt.py doubao-seed-2-1-lite-260915 \
      R1prompt_Seed2_1_lite 24 8 > /tmp/r1prompt_seed.log 2>&1 &

# 环境变量（可选）
#   LABEL_MAX_TOKENS  默认 8000
#   LABEL_TIMEOUT     客户端超时秒数，默认 180；思考型模型建议 600

# 断点续跑：直接重跑同一命令，会跳过 JSONL 中已完成的行
# 装配：脚本末尾自动装配；若中断在装配前，用 recover_assemble.py <slug>
```

产出落在 `runs/`：`抖音微博小红书-独立重打标_<slug>.xlsx`（结构 = 原表 57 列，前三列替换为新判定）、
断点 `.label_results_<slug>.jsonl`、进度 `.label_progress_<slug>.json`。
断点与进度文件已被 `.gitignore` 排除（可复现派生物）；成品 xlsx 入库。

## 效应分解设计（`compare_r1prompt.py`）

```
                  第1轮口径                            后三轮口径
原标模型(v4-flash) 第1轮 = 基准（agentic 150行/批）       —
其它模型           **新一轮 A / B**（API 8条/批）        该模型自己的归档轮次
```

每轮新打标都要跟**同模型**的归档轮次配对，才能把口径单独摘出来：

| 新一轮 | 同模型归档轮 | 该轮调用结构 | 能分离出什么 |
|---|---|---|---|
| A `R1prompt_Seed2_1_lite`（doubao） | 第2轮（doubao，后三轮口径） | 逐条 | 口径 + 调用结构，**不干净** |
| B `R1prompt_GLM5_3flash`（GLM） | 第3轮（GLM，后三轮口径） | 每 8 条 | **纯口径效应** |

- 新一轮 vs 同模型归档轮 → 同模型，**仅口径不同**（A 因第2轮是逐条调用，还混入调用结构差异）
- 新一轮 vs 原标 → 同提示词、同输入字段，**模型与调用结构不同** = 模型+结构效应
- 原标 vs 同模型归档轮 → 两者皆不同，作参照

## 相关但不在本目录

| 位置 | 说明 |
|---|---|
| `datasets/zhangxf_labeled/` | 由基准标签派生的分析数据集（聚类、梗匹配、类型集中度） |
| `paper/spot_check/` | 人工复编码抽检工具包（编码手册、抽样、一致性计算） |
| `paper/REMEDIATION_PLAN.md` | 论文修订计划，含打标口径更正的全过程 |
| 工作区根目录 `词表_{哀悼型,教育型,玩梗型,营销型}_最终版.md` | 四类话语词表；服务于仿真环境的注入资产构建，与 LLM 打标是两条链路，故未并入 |
