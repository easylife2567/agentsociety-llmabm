# Hypothesis

## Description

群体差异假设：在公众人物死亡事件传播中，圈外群体（初始不熟悉逝者）的认知偏移程度显著高于圈内群体（初始熟悉逝者）；备择情形：若圈内群体偏移程度不低于圈外群体，则表明既有完整认知在碎片化符号冲击下同样发生重构，与常识预设相反，需仿真结果裁定。因变量：各组认知偏移程度；分组变量：与逝者的初始关系距离（熟悉/不熟悉）。

## Rationale

圈内群体（如考研群体）对逝者身份与行为持有完整前置认知，圈外群体（如家长、普通劳动者）仅通过事件爆发后的信息流构建认知。认知心理学与传播学提示，缺乏前置锚点的群体更易被碎片化符号主导（近因效应、可用性偏差）；但圈内群体在认知冲突下也可能发生剧烈认知重构。方向性结论需仿真验证，对应文献索引中群体差异/认知形成主题。

## Experiment Groups

### Group 1: control_insider

**Type:** control

**Description:** 圈内群体：原本熟悉逝者的用户（如考研群体），初始认知程度高、与逝者关系距离近

**Agent Selection Criteria:** agents with familiarity_with_deceased == high


### Group 2: treatment_outsider

**Type:** treatment

**Description:** 圈外群体：原本不熟悉逝者的用户（如家长、普通劳动者），仅通过事件后信息流了解逝者

**Agent Selection Criteria:** agents with familiarity_with_deceased == low

