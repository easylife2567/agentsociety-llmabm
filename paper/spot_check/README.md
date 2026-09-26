# 人工复编码抽检工具包（spot check）

*建立于 2026-09-25。对应 `paper/REMEDIATION_PLAN.md` 动作 1 的唯一未完成项。*

## 状态：工具已就绪，**人工编码尚未执行**

现有六类标签为 LLM 生成，无人工编码环节（四轮跨模型：与原标 κ = 0.430–0.511，但原标提示词与
后三轮不同且未留存，该区间含口径差异；判定标准逐字相同的后三轮之间 κ = 0.668–0.767）。本目录用于补齐
人工复编码可靠性证据。**在编码者返回数据之前，任何"人工编码"表述都不成立**，
`AGREEMENT_REPORT.md` 尚未生成（仓库中不应存在该文件）。

## 文件

| 文件 | 作用 |
|---|---|
| `CODEBOOK.md` | 编码手册：类别定义、判定顺序、6 条边界规则、反例表 |
| `draw_spot_check_sample.py` | 分层（平台×周）盲化抽样，产出编码表与答案表 |
| `compute_agreement.py` | 计算编码者间与"编码者×模型"的 κ、混淆矩阵，并做关键结论敏感性 |
| `sample/coderA.csv`、`sample/coderB.csv` | 编码表（内容相同、顺序各自打乱；**不含**周次/平台/模型标签） |
| `sample/key.csv` | 答案表（**编码者不得查看**） |

## 执行步骤

```bash
# 1) 抽样（已执行，n=400；如需重抽可改 --seed）
python draw_spot_check_sample.py --n 400 --coders 2 --seed 20260925

# 2) 两名编码者各自独立填写 sample/coder{A,B}.csv 的 category / valid / note 三列
#    要求：盲于周次与研究假设；不得互相讨论；不得查证事件时间线

# 3) 收回后计算（可选第三人裁定文件）
python compute_agreement.py --a sample/coderA.csv --b sample/coderB.csv --key sample/key.csv
#    --adjudicated sample/adjudicated.csv
```

## 报告要求（见 CODEBOOK.md §8）

- 类别级与有效性级：一致率 + Cohen's κ（或 Krippendorff's α）+ 逐类混淆矩阵
- 玩梗类在「模型三轮 + 人工两轮 + 裁定」各口径下的份额区间
- 关键结论敏感性：**W19–W22 相对事件前基线的抬升是否在人工编码下同样出现**；
  周级起爆周仅作描述性参照（分层样本每周仅数条，功效很低）

## 自检记录

2026-09-25 已用合成标签（模型标签加 10%/20% 噪声）跑通全流程，验证列名对齐、κ 计算、
混淆矩阵与相位敏感性输出正常；**合成产物已删除**，不得作为证据引用。
