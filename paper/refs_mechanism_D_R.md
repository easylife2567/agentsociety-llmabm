# 决策模型 D / R 两因子的文献依据（可直接引用版）

> 生成日期：2026-09-15
> 用途：`锚定式事件表达激活模型.md` 与论文 Method 节的参考文献来源
> 核验状态：6 条 DOI 经 Crossref API 逐字段核验（标题／作者／刊名／卷期页），
> Blanco (2005) 经 MPRA 官方页面核验。核验日期 2026-09-15。

---

## 一、参数—文献对应表

| 参数 | 机制 | 直接依据文献 | 代码出处 |
|---|---|---|---|
| **D** | 沉默螺旋：同类气候共振放大表达收益、少数派处境抑制收益、D<0 即孤立成本 | Noelle-Neumann (1974)（机制层）；Blanco (2005)（收益—孤立成本门槛 c/(b+c)）；Sohn & Geidner (2016)、Cabrera et al. (2021)（有界 logistic 映射路线）；Granovetter (1978)（异质行动门槛） | `custom/envs/curation_mechanisms.py::spiral_factor`；`custom/agents/curation_discourse_agent.py:53–56` |
| **R** | 注意力衰减：重复同类曝光对事件冲击偏离的折减 | Wu & Huberman (2007)；Candia et al. (2019) | `custom/envs/curation_mechanisms.py::fatigue_factor`；`custom/agents/curation_discourse_agent.py:58` |

> **D 不是单篇来源**：D 的完整公式是本研究的多条理论—计算路线的综合操作化，
> 不可归给上表中任何单篇论文（见 `锚定式事件表达激活模型.md` §13「暂不能直接主张的内容」第 1 条）。
> 只有 **R** 是"两篇文献"式的直接依据。

---

## 二、APA 7（英文投稿直接粘贴）

Granovetter, M. (1978). Threshold models of collective behavior. *American Journal of Sociology, 83*(6), 1420–1443. https://doi.org/10.1086/226707

Blanco, I. (2005). *The silence that precedes hypocrisy: A formal model of the spiral of silence theory* (MPRA Paper No. 45452). University Library of Munich. https://mpra.ub.uni-muenchen.de/45452/

Wu, F., & Huberman, B. A. (2007). Novelty and collective attention. *Proceedings of the National Academy of Sciences, 104*(45), 17599–17601. https://doi.org/10.1073/pnas.0704916104

Noelle-Neumann, E. (1974). The spiral of silence: A theory of public opinion. *Journal of Communication, 24*(2), 43–51. https://doi.org/10.1111/j.1460-2466.1974.tb00367.x

Sohn, D., & Geidner, N. (2016). Collective dynamics of the spiral of silence: The role of ego-network size. *International Journal of Public Opinion Research, 28*(1), 25–45. https://doi.org/10.1093/ijpor/edv005

Candia, C., Jara-Figueroa, C., Rodriguez-Sickert, C., Barabási, A.-L., & Hidalgo, C. A. (2019). The universal decay of collective memory and attention. *Nature Human Behaviour, 3*(1), 82–91. https://doi.org/10.1038/s41562-018-0474-5

Cabrera, B., Ross, B., Röchert, D., Brünker, F., & Stieglitz, S. (2021). The influence of community structure on opinion expression: An agent-based model. *Journal of Business Economics, 91*(9), 1331–1355. https://doi.org/10.1007/s11573-021-01064-7

（按第一作者姓氏字母序；若按在文中首次出现排序，依次为：Noelle-Neumann → Blanco → Sohn & Geidner → Cabrera et al. → Granovetter → Wu & Huberman → Candia et al.）

---

## 三、BibTeX（LaTeX / Overleaf 直接粘贴，同目录 `refs_mechanism_D_R.bib`）

```bibtex
@article{noelleneumann1974spiral,
  author  = {Noelle-Neumann, Elisabeth},
  title   = {The Spiral of Silence: A Theory of Public Opinion},
  journal = {Journal of Communication},
  volume  = {24}, number = {2}, pages = {43--51}, year = {1974},
  doi     = {10.1111/j.1460-2466.1974.tb00367.x}
}

@techreport{blanco2005silence,
  author      = {Blanco, Iv{\'a}n},
  title       = {The Silence That Precedes Hypocrisy: A Formal Model of the Spiral of Silence Theory},
  institution = {University Library of Munich},
  type        = {MPRA Paper}, number = {45452}, year = {2005},
  url         = {https://mpra.ub.uni-muenchen.de/45452/}
}

@article{sohn2016collective,
  author  = {Sohn, Dongyoung and Geidner, Nick},
  title   = {Collective Dynamics of the Spiral of Silence: The Role of Ego-Network Size},
  journal = {International Journal of Public Opinion Research},
  volume  = {28}, number = {1}, pages = {25--45}, year = {2016},
  doi     = {10.1093/ijpor/edv005}
}

@article{cabrera2021influence,
  author  = {Cabrera, Benjamin and Ross, Bj{\"o}rn and R{\"o}chert, Daniel
             and Br{\"u}nker, Felix and Stieglitz, Stefan},
  title   = {The Influence of Community Structure on Opinion Expression: An Agent-Based Model},
  journal = {Journal of Business Economics},
  volume  = {91}, number = {9}, pages = {1331--1355}, year = {2021},
  doi     = {10.1007/s11573-021-01064-7}
}

@article{granovetter1978threshold,
  author  = {Granovetter, Mark},
  title   = {Threshold Models of Collective Behavior},
  journal = {American Journal of Sociology},
  volume  = {83}, number = {6}, pages = {1420--1443}, year = {1978},
  doi     = {10.1086/226707}
}

@article{wu2007novelty,
  author  = {Wu, Fang and Huberman, Bernardo A.},
  title   = {Novelty and Collective Attention},
  journal = {Proceedings of the National Academy of Sciences},
  volume  = {104}, number = {45}, pages = {17599--17601}, year = {2007},
  doi     = {10.1073/pnas.0704916104}
}

@article{candia2019universal,
  author  = {Candia, Cristian and Jara-Figueroa, C. and Rodriguez-Sickert, Carlos
             and Barab{\'a}si, Albert-L{\'a}szl{\'o} and Hidalgo, C{\'e}sar A.},
  title   = {The Universal Decay of Collective Memory and Attention},
  journal = {Nature Human Behaviour},
  volume  = {3}, number = {1}, pages = {82--91}, year = {2019},
  doi     = {10.1038/s41562-018-0474-5}
}
```

---

## 四、GB/T 7714-2015（顺序编码制，中文期刊备用）

```
[1] NOELLE-NEUMANN E. The spiral of silence: a theory of public opinion[J].
    Journal of Communication, 1974, 24(2): 43-51.
[2] BLANCO I. The silence that precedes hypocrisy: a formal model of the spiral
    of silence theory[R/OL]. Munich: University Library of Munich, 2005
    [2026-09-15]. https://mpra.ub.uni-muenchen.de/45452/.
[3] SOHN D, GEIDNER N. Collective dynamics of the spiral of silence: the role of
    ego-network size[J]. International Journal of Public Opinion Research,
    2016, 28(1): 25-45.
[4] CABRERA B, ROSS B, RÖCHERT D, et al. The influence of community structure on
    opinion expression: an agent-based model[J]. Journal of Business Economics,
    2021, 91(9): 1331-1355.
[5] GRANOVETTER M. Threshold models of collective behavior[J]. American Journal
    of Sociology, 1978, 83(6): 1420-1443.
[6] WU F, HUBERMAN B A. Novelty and collective attention[J]. Proceedings of the
    National Academy of Sciences, 2007, 104(45): 17599-17601.
[7] CANDIA C, JARA-FIGUEROA C, RODRIGUEZ-SICKERT C, et al. The universal decay
    of collective memory and attention[J]. Nature Human Behaviour, 2019,
    3(1): 82-91.
```

---

## 五、引用时必须注意的三条边界

1. **D 是复合锚点，不是单篇公式**。不可写"依据 Noelle-Neumann (1974) 的公式"——该文未给出可照搬的数值公式；
   `tanh`、k=1.5、α_D=0.4297 均为本研究操作化选择。
2. **R 是单指数衰减，两篇来源都不是单指数**。Wu & Huberman (2007) 报告的是新颖性衰减（拉伸指数形态），
   Candia et al. (2019) 提出的是两段式（biexponential）衰减模型。本研究 R = exp(−λ·E/15) 是以单指数
   对"注意力余量"的操作化，不是复现任一论文的衰减函数。建议写法：
   "以单指数形式操作化重复曝光疲劳，其衰减过程依据该文献传统"。
3. **Blanco (2005) 是 MPRA 工作论文，非同行评审期刊论文**。引用时应如实标注文献性质
   （APA 用 `[techreport]` / 斜体标题；GB/T 7714 用 `[R/OL]`）。

---

## 六、核验记录

| 条目 | 核验方式 | 结果 |
|---|---|---|
| Noelle-Neumann 1974 | Crossref `10.1111/j.1460-2466.1974.tb00367.x` | J. Communication, 24(2), 43–51 ✔ |
| Blanco 2005 | MPRA 官网条目页 | MPRA Paper 45452, 2005 ✔ |
| Sohn & Geidner 2016 | Crossref `10.1093/ijpor/edv005` + OUP 期号页 | IJPPOR 28(1), 25–45, Spring 2016（在线首发 2015-03-12）✔ |
| Cabrera et al. 2021 | Crossref `10.1007/s11573-021-01064-7` | J. Bus. Econ. 91(9), 1331–1355 ✔ |
| Granovetter 1978 | Crossref `10.1086/226707` | AJS 83(6), 1420–1443 ✔ |
| Wu & Huberman 2007 | Crossref `10.1073/pnas.0704916104` | PNAS 104(45), 17599–17601 ✔ |
| Candia et al. 2019 | Crossref `10.1038/s41562-018-0474-5` | Nat. Hum. Behav. 3(1), 82–91（在线首发 2018-12-10）✔ |
