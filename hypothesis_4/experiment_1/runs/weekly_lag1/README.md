# weekly_lag1 当前正式批

设计：普通真实帖与Agent帖均采用一期传播滞后，W13唯一官方讣告当周进入。只重跑受影响的`interest`和`random`，每臂3个seed，共6个run；`chronological`未修改，不混入本批完成性判定。

```text
weekly_lag1/
├── weekly_lag1_interest_s{0,1,2}/   # 原始run，Git忽略
├── weekly_lag1_random_s{0,1,2}/     # 原始run，Git忽略
└── _derived/
    ├── monitor/                      # 状态与完成性快照
    ├── data/                         # 逐run CSV
    └── charts/                       # 逐run图
```

权威配置清单：`../../init/configs/weekly_lag1_manifest.json`。批跑入口：`../../run_weekly_lag_batch.py`。AgentSociety官方单run兼容入口`../../run`指向`weekly_lag1_interest_s0`。

只有当6个run全部达到11/11周、每个replay包含1100行Agent状态和11行环境状态后，本批才可升格为最新正式证据。
