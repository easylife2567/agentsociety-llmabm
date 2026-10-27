# Report context (auto-generated)

Use this digest when drafting `report_zh.md` / `report_en.md` and `report_zh.html` / `report_en.html`. Synthesize tool outputs into prose — do not paste raw EDA wholesale.

## Section: data

### seed10_explore.md (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_explore.md`

# 三臂10seed探索与口径复验

范围为30次完整主实验、330个run×week，3000份Agent工作区，总成功发布6041帖。新批原失败random_s7不进入科学汇总；interest_s6采用resume1副本。旧99行周表和原论文图3/4的9行晚期供给及接触指标均逐格一致。

核心窗仍W19–W22，作者类型posted供给；晚期份额先各seed内作比再均值。每run玩梗发帖率分母76机会，同类所见分母760槽，跨群体生成玩梗帖再展示分母3240槽；10数值槽位不等于LLM读取的前5条。

初步方向：旧3和新7内兴趣、时序均高于随机，时序总体高于兴趣。旧3晚期玩梗份额随机10.32%、兴趣65.61%、时序73.30%；新7为10.98%、69.70%、75.74%。不能把模型与seed范围混杂的批次均值差归因模型升级。

统计单位是seed；固定15个配对指标×对比/层（五指标含帖数与发帖率的线性重复，校正偏保守），精确双侧符号翻转检验须假设零差对称，t均值区间须作分布近似。旧3、新7精确p值分辨率有限，新7的15项Holm校正均未过0.05；混合10seed的p不能当跨模型等价证据。剔除任意一个seed后的均值方向仍正。

官方harness旧H4E1停在claims，使本轮intake实际返回BLOCKED_BY_PHASE；先保存seed10_prior_harness.json及state.pre_seed10.yaml再重新intake。intake只支持experiment_2/run/replay且该路径不存在，CLI没有多run数据源入口；仅用已安装state API把db_path设为本轮可追溯的seed10_metrics.sqlite，未改研究progress JSON或原始run，其他阶段操作仍用官方CLI。

### seed10_sources.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_sources.json`

{
  "created_at": "2026-10-23T07:12:37.204153+00:00",
  "scope": "main-only; 30 completed conditions; no ablation",
  "query": "SELECT week, agent_supply, agent_supply_meme, agent_supply_mourning, agent_supply_education, agent_supply_marketing, agent_supply_other FROM curation_dynamics_env_state ORDER BY week",
  "script_sha256": "5d1df6ec801f984163a2ed7369938ea00b24e71f3a040fc05eff395276e3bef7",
  "original_measurement_script": "paper/figures/scripts/prepare_simulation.py",
  "original_measurement_script_sha256": "fd2e925bffc5084139e25b64e810a150dd3627351867a89cdc1fa69b507797c9",
  "old_weekly_and_paper_metrics_reproduced": true,
  "runs": [
    {
      "run_id": "timestamp_v1_random_s0",
      "arm": "random",
      "seed": 0,
      "cohort": "old3",
      "request_model": "deepseek-v4-1-flash-260910",
      "response_models": "deepseek-v4-1-flash",
      "run_dir": "hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_random_s0",
      "total_posts": 176,
      "body_requests": 177,
      "late_meme_posts": 4,
      "late_total_posts": 30,
      "late_meme_share": 0.13333333333333333,
      "own_share": 0.03289473684210526,
      "meme_post_rate": 0.05263157894736842,
      
…(truncated)

### seed10_runs.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_runs.csv`

run_id,arm,seed,cohort,request_model,response_models,run_dir,total_posts,body_requests,late_meme_posts,late_total_posts,late_meme_share,own_share,meme_post_rate,cross_generated_share,all_feed_meme_share,w13_mourning_posts,w13_mourning_rate,mourning_peak_week
timestamp_v1_random_s0,random,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_random_s0,176,177,4,30,0.133333333333,0.0328947368421,0.0526315789474,0.000925925925926,0.0295,2,0.0909090909091,2026-W14
timestamp_v1_chronological_s0,chronological,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_chronological_s0,210,210,41,59,0.694915254237,0.389473684211,0.539473684211,0.221604938272,0.3955,21,0.954545454545,2026-W13
timestamp_v1_interest_s0,interest,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_interest_s0,214,214,34,54,0.62962962963,0.246052631579,0.447368421053,0.0608024691358,0.19875,21,0.954545454545,2026-W13
timestamp_v1_random_s1,random,1,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/time
…(truncated)

### seed10_weekly.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_weekly.csv`

week,agent_supply,agent_supply_meme,agent_supply_mourning,agent_supply_education,agent_supply_marketing,agent_supply_other,run_id,arm,seed,cohort,request_model,response_models,run_dir
2026-W12,24,0,0,5,19,0,timestamp_v1_random_s0,random,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_random_s0
2026-W13,27,0,2,11,13,1,timestamp_v1_random_s0,random,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_random_s0
2026-W14,29,0,8,8,10,3,timestamp_v1_random_s0,random,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_random_s0
2026-W15,19,0,5,5,6,3,timestamp_v1_random_s0,random,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_random_s0
2026-W16,19,0,7,5,4,3,timestamp_v1_random_s0,random,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_random_s0
2026-W17,16,0,7,2,3,4,timestamp_v1_random_s0,random,0,old3,deepseek-v4-1-flash-260910,deepseek-v4-1-flash,hypothesis_4/experiment_2/runs/timestamp_
…(truncated)

### seed10_arm_summary.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_arm_summary.csv`

cohort,arm,metric,n,mean,sd,minimum,maximum,ci_low,ci_high
old3,random,late_meme_posts,3,3,1.73205080757,1,4,-1.3026527297,7.3026527297
old3,random,late_meme_share,3,0.103241968759,0.056148578131,0.0384615384615,0.137931034483,-0.0362388316353,0.242722769154
old3,random,own_share,3,0.0320175438596,0.0053176998478,0.0263157894737,0.0368421052632,0.0188076451281,0.0452274425912
old3,random,meme_post_rate,3,0.0394736842105,0.0227901422049,0.0131578947368,0.0526315789474,-0.017140167496,0.0960875359171
old3,random,cross_generated_share,3,0.0011316872428,0.00124736169269,0,0.00246913580247,-0.00196693097818,0.00423030546377
old3,random,total_posts,3,174.333333333,1.52752523165,173,176,170.5387503,178.127916367
old3,random,w13_mourning_posts,3,4,1.73205080757,2,5,-0.302652729696,8.3026527297
old3,random,all_feed_meme_share,3,0.0321666666667,0.00289755644179,0.0295,0.03525,0.0249687374378,0.0393645958955
old3,chronological,late_meme_posts,3,43,2,41,45,38.0317245766,47.9682754234
old3,chronological,late_meme_share,3,0.733002142996,0.0346659456413,0.694915254237,0.762711864407,0.646887160116,0.819117125876
old3,chronological,own_share,3,0.420175438596,0.028596356689,0.389473684211,0.4460526
…(truncated)

### seed10_paired_contrasts.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_paired_contrasts.csv`

cohort,contrast,metric,n,mean,sd,minimum,maximum,ci_low,ci_high,positive,zero,negative,permutation_p,leave_one_out_min,leave_one_out_max,holm_p
old3,interest-random,late_meme_posts,3,33.3333333333,3.51188458428,30,37,24.6093283983,42.0573382684,3,0,0,0.25,31.5,35,1
old3,chronological-random,late_meme_posts,3,40,3.60555127546,37,44,31.0433141051,48.9566858949,3,0,0,0.25,38,41.5,1
old3,chronological-interest,late_meme_posts,3,6.66666666667,4.50924975282,2,11,-4.53493069588,17.8682640292,3,0,0,0.25,4.5,9,1
old3,interest-random,late_meme_share,3,0.55290051252,0.0679136487674,0.496296296296,0.628205128205,0.384193656476,0.721607368564,3,0,0,0.25,0.515248204677,0.581202620632,1
old3,chronological-random,late_meme_share,3,0.629760174237,0.0844659073043,0.561581920904,0.724250325945,0.419935228548,0.839585119926,3,0,0,0.25,0.582515098383,0.663849300904,1
old3,chronological-interest,late_meme_share,3,0.0768596617172,0.0167328724851,0.0652856246077,0.0960451977401,0.0352929021515,0.118426421283,3,0,0,0.25,0.0672668937058,0.082646680272,1
old3,interest-random,own_share,3,0.219736842105,0.0186545353668,0.205263157895,0.240789473684,0.173396407306,0.266077276905,3,0,0,0.25,0.209210526316,0.2269
…(truncated)

### eda_quick_stats.md (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_quick_stats/eda_quick_stats.md`

## Data Overview

- **Data path**: presentation/hypothesis_4/data/seed10_metrics.sqlite
- **Tables**: 2
- **Total Rows**: 360

### Dataset: `seed10_run_metrics` (30 rows)
- Table: `seed10_run_metrics`
Sample data (first rows):
  Row 1:
  - run_id: timestamp_v1_random_s0
  - arm: random
  - seed: 0
  - cohort: old3
  - request_model: deepseek-v4-1-flash-260910
  Row 2:
  - run_id: timestamp_v1_chronological_s0
  - arm: chronological
  - seed: 0
  - cohort: old3
  - request_model: deepseek-v4-1-flash-260910
  Row 3:
  - run_id: timestamp_v1_interest_s0
  - arm: interest
  - seed: 0
  - cohort: old3
  - request_model: deepseek-v4-1-flash-260910

**Numeric Stats**:
  - `seed` (`seed`): min=0, max=9, avg=4.5
  - `total_posts` (`total_posts`): min=158, max=231, avg=201.3667
  - `body_requests` (`body_requests`): min=158, max=231, avg=201.7667
  - `late_meme_posts` (`late_meme_posts`): min=1, max=52, avg=28.7667
  - `late_total_posts` (`late_total_posts`): min=23, max=69, avg=47.9667
  - `late_meme_share` (`late_meme_share`): min=0.038461538461538464, max=0.78125, avg=0.5142
  - `own_share` (`own_share`): min=0.02236842105263158, max=0.4789473684210526, avg=0.2439
  - `meme_post_rate` (`m
…(truncated)

### analysis_sources.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/analysis_sources.json`

{
  "schema_version": 1,
  "batch_id": "anchored_v1",
  "classification": "superseded_formal",
  "design": "3 recommendation algorithms x 3 seeds",
  "status": "completed_archived",
  "official_single_run_compatibility": {
    "path": "hypothesis_4/experiment_1/run",
    "target": "runs/weekly_lag1/weekly_lag1_interest_s0",
    "role": "current weekly_lag1 AgentSociety single-run compatibility entry",
    "limitation": "The target becomes readable after the new run starts; archived anchored_v1 evidence is not the latest formal batch."
  },
  "formal_runs": [
    {
      "run_id": "anchored_v1_random_s0",
      "algorithm": "random",
      "seed": 0,
      "engine_batches": 11,
      "weekly_points": 11,
      "replay": "archive/hypothesis_4_experiment_1_batches/formal_superseded/anchored_v1/raw/anchored_v1_random_s0/replay"
    },
    {
      "run_id": "anchored_v1_random_s1",
      "algorithm": "random",
      "seed": 1,
      "engine_batches": 11,
      "weekly_points": 11,
      "replay": "archive/hypothesis_4_experiment_1_batches/formal_superseded/anchored_v1/raw/anchored_v1_random_s1/replay"
    },
    {
      "run_id": "anchored_v1_random_s2",
      "algorithm": "random",
   
…(truncated)

### analysis_summary.json (`summary`, phase=explore)
- path: `presentation/hypothesis_4/data/analysis_summary.json`

{
  "summary": "本研究按用户确认将新旧模型版本视为等价，三臂各10seed合并作为主分析。原W19–W22作者供给/接触口径下，兴趣与时序相对随机的方向稳定；当前时序制度结果较高，但其排序与生成帖更快入池、周内回流及候选规则同时变化，不能单独归因于时序排序。",
  "key_findings": [
    "30次完整运行、330个run×week、3000份Agent工作区和6041篇成功发布帖；旧论文图3/4逐格复现通过，消融未更新。",
    "晚期玩梗作者帖数随机/时序/兴趣为3.1/45.4/37.8；供给份额10.780%/75.011%/68.472%，兴趣与时序相对随机在10/10seed及新增7/7seed均为正。",
    "时序相对兴趣供给份额均值+6.539pp，t近似95%区间3.592–9.487；9正1负（seed5），同类所见与跨群体生成玩梗再展示均10正。",
    "合计10seed每项配对均值方向在逐一剔除seed后保持；15项精确符号翻转经Holm校正均p=0.029296875。旧3/新7分层仅作补充批次稳健性检查。",
    "已采纳模型版本等价口径，以每臂10seed为主分析；精确请求与返回标识保留在原来源清单。外部真实帖三臂共享发布时间，生成帖则时序批末入池、后续小时可见，随机/兴趣次周可见。"
  ],
  "limitations": "时序制度的排序、生成帖入池资格及周内回流未分离；较高玩梗传播可能部分来自更快入池，现有结果不能分解或量化机制贡献。仿真限本次100人、11周和冻结制度；固定作者类型不是正文独立语义分类，10槽数值feed不等于提示前5条或实际阅读；再展示不是回流净因果贡献。seed是重复单位，t区间为小样本近似，符号翻转仍需可交换/对称条件，五指标含线性冗余。失败尝试排除科学汇总，未重跑仿真或改动消融。",
  "evidence_index_path": "presentation/hypothesis_4/data/evidence_index.json",
  "model_equivalence": {
    "status": "equivalent_for_this_study",
    "basis": "explicit_user_decision",
    "decision_date": "2026-10-24",
    "primary_analysis": "pooled_seed0_9_per_arm",
    "seeds_per_arm": 10,
    "empirical_equivalence_test_performed": false,
    "provenance_source": "data/seed10
…(truncated)

### eda_figure_01_weekly_lag_meme_trajectory.png (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/eda_figure_01_weekly_lag_meme_trajectory.png`

(binary file eda_figure_01_weekly_lag_meme_trajectory.png)

### eda_figure_01_weekly_lag_meme_trajectory.svg (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/eda_figure_01_weekly_lag_meme_trajectory.svg`

(binary file eda_figure_01_weekly_lag_meme_trajectory.svg)

### eda_figure_02_weekly_lag_event_and_arm_gap.png (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/eda_figure_02_weekly_lag_event_and_arm_gap.png`

(binary file eda_figure_02_weekly_lag_event_and_arm_gap.png)

### eda_figure_02_weekly_lag_event_and_arm_gap.svg (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/eda_figure_02_weekly_lag_event_and_arm_gap.svg`

(binary file eda_figure_02_weekly_lag_event_and_arm_gap.svg)

### eda_figure_03_weekly_lag_agent_supply_stacked_area.png (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/eda_figure_03_weekly_lag_agent_supply_stacked_area.png`

(binary file eda_figure_03_weekly_lag_agent_supply_stacked_area.png)

### eda_figure_03_weekly_lag_agent_supply_stacked_area.svg (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/eda_figure_03_weekly_lag_agent_supply_stacked_area.svg`

(binary file eda_figure_03_weekly_lag_agent_supply_stacked_area.svg)

### seed10_analyze.py (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_analyze.py`

(binary file seed10_analyze.py)

### seed10_figure_contracts.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_figure_contracts.json`

[
  {
    "contract_id": "seed10_fc1",
    "claim_id": "seed10_c1",
    "core_finding": "新增7seed与旧3seed的周玩梗供给轨迹保持时序/兴趣高于随机；合计10不是独立新样本。",
    "scope": "single chart",
    "chart_role": "trend",
    "evidence_source": "data/seed10_weekly_summary.csv",
    "analysis_scope": "W12–W22; old3,new7,all10",
    "figure_archetype": "three cohort facets with mean and min-max band",
    "visual_center": "late W19–W22 separation from random",
    "audience": "experiment report",
    "highlight": "late window",
    "axes_grouping": "same y=0–20 posts, x=W12–W22",
    "legend_strategy": "shared arm legend",
    "reviewer_check": "shade is actual seed range, not confidence interval; author type not semantics",
    "output_files": [
      "charts/chart_01_seed10_trajectories.png"
    ]
  },
  {
    "contract_id": "seed10_fc2",
    "claim_id": "seed10_c3",
    "core_finding": "三臂各10seed按用户确认的模型等价口径作为主分析；旧3与新7的制度排序一致，分批图仅作补充检查。",
    "scope": "single chart",
    "chart_role": "comparison",
    "evidence_source": "data/seed10_runs.csv; data/seed10_arm_summary.csv",
    "analysis_scope": "W19–W22 five original metrics",
    "figure_archetype": "five metric facets; old3,new7,all10",
    "visual_center"
…(truncated)

### seed10_metrics.sqlite (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_metrics.sqlite`

(binary file seed10_metrics.sqlite)

### seed10_prior_harness.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_prior_harness.json`

{
  ".agentsociety/analysis/hypothesis_4/state.yaml": {
    "sha256": "92d2670b802e9be671510241f10fa875382ce6c12e46ac635011e6dd068c4acb",
    "text": "hypothesis_id: '4'\nexperiment_id: '1'\ndb_path: /Users/easylife/Project/AgentSociety/hypothesis_4/experiment_1/run/replay\ncurrent_phase: claims\nhypothesis_release: not_started\nchart_count: 0\nmax_charts: 0\nfigure_contracts: []\nphase_attestations:\n  frame:\n    phase: frame\n    status: DONE\n    key_findings:\n    - 用户要求查看正式实验图，因此分析问题聚焦于weekly_lag1中interest与random的三seed聚合比较。\n    - 主指标预先锁定为玩梗供给份额、曝光份额、玩梗群体发言率和策展偏差。\n    - 旧chronological未按新时机重跑，不进入本轮主比较。\n    artifacts_read: []\n    artifacts_written:\n    - .agentsociety/analysis/hypothesis_4/analysis_plan.yaml\n    blocking_reason: null\n    recommended_next_step: null\n    rubric:\n      research_question_confirmed: 用户明确要求对已完成正式实验做图；图表问题依照当前实验目的固定为interest与random在统一一期滞后下的差异。\n      success_criteria: 图表必须使用6个正式run、按臂聚合3个seed、显示波动范围与真实基准，并清楚标注仿真和三seed限制。\n    artifact_fingerprint: 699697042c8ca8b4f8448294\n    completed_at: '2026-09-28T01:44:01.558321Z'\n  explore:\n    phase: explore\n    status: DONE\n    key_findings:\n    - 6个正式run均提供11周完整数据，共66个run-week观测；两臂各3个seed。\n    
…(truncated)

### seed10_verification.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_verification.json`

{
  "checked_at": "2026-10-23T07:29:03.920473+00:00",
  "metric_audit_verdict": "PASS",
  "independent_reviewer": "metric_audit",
  "source_hashes_rechecked": 3416,
  "checks": [
    "30 actual completed paths / 3000 Agent files / 330 weekly rows consistent",
    "old 99x6 weekly cells and old paper 9x6 late/exposure metrics reproduced",
    "72 arm summaries and 45 paired comparisons independently recomputed",
    "all enumerated sign-flip, per-cohort 15 Holm, directions, leave-one-out agree",
    "resume1 and retry1 selected; failed original excluded",
    "old response undated; new response261017"
  ],
  "reference_sha256": {
    "paper/figures/source_data/simulation_late.csv": "b81087b6ef641287293e2550f8021a9c3a9619b87d930d27dd2b9be618dc6316",
    "paper/figures/source_data/simulation_exposure.csv": "eed64451d581fbc824194601191c1e1883270f9c66e5d99d9347cea2bdd6c33c",
    "paper/figures/source_data/simulation_weekly.csv": "7445ce9b8d0169981e19b40dd6440a5a5e2599901b947e96338f5fd2faa45ac0",
    "paper/figures/source_data/simulation_sources.json": "15f8eed531f095d1dc38b8696241638f43b6452a6ea64917877eda5048d18b09",
    "presentation/hypothesis_4/data/timestamp_v1_agent_supply_by_run_
…(truncated)

### seed10_weekly_summary.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/seed10_weekly_summary.csv`

cohort,arm,week,n,agent_supply_mean,agent_supply_min,agent_supply_max,agent_supply_meme_mean,agent_supply_meme_min,agent_supply_meme_max,agent_supply_mourning_mean,agent_supply_mourning_min,agent_supply_mourning_max,agent_supply_education_mean,agent_supply_education_min,agent_supply_education_max,agent_supply_marketing_mean,agent_supply_marketing_min,agent_supply_marketing_max,agent_supply_other_mean,agent_supply_other_min,agent_supply_other_max
old3,chronological,2026-W12,3,26,24,28,0,0,0,0,0,0,7,5,9,19,19,19,0,0,0
old3,chronological,2026-W13,3,43.6666666667,33,51,0,0,0,18.3333333333,15,21,6.33333333333,3,9,11,10,12,8,4,11
old3,chronological,2026-W14,3,36.6666666667,31,40,0,0,0,7.66666666667,6,10,8.33333333333,7,9,5.33333333333,5,6,15.3333333333,11,18
old3,chronological,2026-W15,3,18.6666666667,16,21,0,0,0,1.66666666667,0,4,5,5,5,8,4,10,4,1,6
old3,chronological,2026-W16,3,13.6666666667,11,19,0,0,0,1.66666666667,0,5,4.33333333333,4,5,7.33333333333,6,9,0.333333333333,0,1
old3,chronological,2026-W17,3,11,10,12,0,0,0,0.666666666667,0,2,3.33333333333,3,4,4,4,4,3,1,5
old3,chronological,2026-W18,3,4.33333333333,4,5,0,0,0,0,0,0,0.333333333333,0,1,4,4,4,0,0,0
old3,chronological,2026-W19,3,
…(truncated)

### timestamp_v1_agent_supply_arm_week_mean.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/timestamp_v1_agent_supply_arm_week_mean.csv`

﻿arm,n_seeds,week,agent_supply,agent_supply_meme,agent_supply_mourning,agent_supply_education,agent_supply_marketing,agent_supply_other
random,3,2026-W12,25.333333333333332,0.0,0.0,6.333333333333333,19.0,0.0
random,3,2026-W13,26.666666666666668,0.0,4.0,9.0,13.0,0.6666666666666666
random,3,2026-W14,28.333333333333332,0.0,8.0,7.0,9.0,4.333333333333333
random,3,2026-W15,21.0,0.0,5.666666666666667,5.0,5.333333333333333,5.0
random,3,2026-W16,18.0,0.3333333333333333,6.666666666666667,4.333333333333333,4.333333333333333,2.3333333333333335
random,3,2026-W17,15.666666666666666,0.0,5.0,3.6666666666666665,3.6666666666666665,3.3333333333333335
random,3,2026-W18,11.0,0.0,2.6666666666666665,3.0,3.0,2.3333333333333335
random,3,2026-W19,10.333333333333334,0.0,2.0,2.6666666666666665,3.0,2.6666666666666665
random,3,2026-W20,6.0,0.0,1.3333333333333333,1.3333333333333333,3.0,0.3333333333333333
random,3,2026-W21,6.0,1.0,0.3333333333333333,1.3333333333333333,3.0,0.3333333333333333
random,3,2026-W22,6.0,2.0,0.3333333333333333,0.3333333333333333,3.0,0.3333333333333333
chronological,3,2026-W12,26.0,0.0,0.0,7.0,19.0,0.0
chronological,3,2026-W13,43.666666666666664,0.0,18.333333333333332,6.333333333333333,11.
…(truncated)

### timestamp_v1_agent_supply_by_run_week.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/timestamp_v1_agent_supply_by_run_week.csv`

﻿run_id,arm,seed,week,agent_supply,agent_supply_meme,agent_supply_mourning,agent_supply_education,agent_supply_marketing,agent_supply_other
timestamp_v1_random_s0,random,0,2026-W12,24,0,0,5,19,0
timestamp_v1_random_s0,random,0,2026-W13,27,0,2,11,13,1
timestamp_v1_random_s0,random,0,2026-W14,29,0,8,8,10,3
timestamp_v1_random_s0,random,0,2026-W15,19,0,5,5,6,3
timestamp_v1_random_s0,random,0,2026-W16,19,0,7,5,4,3
timestamp_v1_random_s0,random,0,2026-W17,16,0,7,2,3,4
timestamp_v1_random_s0,random,0,2026-W18,12,0,5,3,3,1
timestamp_v1_random_s0,random,0,2026-W19,10,0,1,2,3,4
timestamp_v1_random_s0,random,0,2026-W20,6,0,2,1,3,0
timestamp_v1_random_s0,random,0,2026-W21,6,1,0,2,3,0
timestamp_v1_random_s0,random,0,2026-W22,8,3,1,1,3,0
timestamp_v1_random_s1,random,1,2026-W12,28,0,0,9,19,0
timestamp_v1_random_s1,random,1,2026-W13,27,0,5,8,13,1
timestamp_v1_random_s1,random,1,2026-W14,26,0,5,7,9,5
timestamp_v1_random_s1,random,1,2026-W15,19,0,4,3,5,7
timestamp_v1_random_s1,random,1,2026-W16,18,0,7,3,4,4
timestamp_v1_random_s1,random,1,2026-W17,14,0,3,5,4,2
timestamp_v1_random_s1,random,1,2026-W18,12,0,2,3,3,4
timestamp_v1_random_s1,random,1,2026-W19,10,0,2,3,3,2
timestamp_v1_random_s1,random,1
…(truncated)

### timestamp_v1_agent_supply_sources.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/timestamp_v1_agent_supply_sources.json`

{
  "batch": "hypothesis_4/experiment_2/runs/timestamp_v1",
  "query": "SELECT week, agent_supply, agent_supply_meme, agent_supply_mourning, agent_supply_education, agent_supply_marketing, agent_supply_other FROM curation_dynamics_env_state ORDER BY week",
  "figure_contract": {
    "purpose": "描述三种正式策展制度下W12–W22五类Agent实际发帖量及其变化。",
    "scope": "9个单次运行图、3个制度内三seed算术均值图；均值不表示单次实测整数。",
    "measure": "按固定Agent类型pool_type统计成功发布；排除外部注入帖、历史池和官方输入。",
    "style": "复用原chart3b函数，五类顺序/配色、W13事件线、0–80纵轴不变。",
    "limitations": "仿真描述性轨迹；作者类型不是正文语义重分类；3次重复均值不含置信区间。"
  },
  "template": {
    "path": "hypothesis_4/experiment_1/plot_run_charts.py",
    "sha256": "3f3617a02452e4af9da28ad54211059b35caef92e8c74b8ecf3dab5e14e9e6aa"
  },
  "script": {
    "path": "presentation/hypothesis_4/charts/timestamp_v1_plot_agent_supply.py",
    "sha256": "9abd2766eea1c848a7fcb849bef82ece4646628c199b8bcca2d667a40d083271"
  },
  "batch_execution_sha256": "91e69c2f4077d44c4982302b78aca19c7124ade646d587d527d97bf7264d92eb",
  "runs": [
    {
      "run_id": "timestamp_v1_random_s0",
      "weeks": 11,
      "actions": 1100,
      "posts": 176,
      "weekly_peak": 29,
      "decision_log_crosscheck": "PASS: all 11 w
…(truncated)

### weekly_lag1_agent_supply_by_type.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_agent_supply_by_type.csv`

arm,week,week_num,type,agent_posts_mean,agent_posts_min,agent_posts_max,agent_posts_std
interest,2026-W12,12,education,3.3333333333333335,3,4,0.5773502691896257
interest,2026-W12,12,marketing,19.0,19,19,0.0
interest,2026-W12,12,meme,0.0,0,0,0.0
interest,2026-W12,12,mourning,0.0,0,0,0.0
interest,2026-W12,12,other,0.0,0,0,0.0
interest,2026-W13,13,education,7.666666666666667,4,13,4.725815626252609
interest,2026-W13,13,marketing,13.333333333333334,13,14,0.5773502691896258
interest,2026-W13,13,meme,0.0,0,0,0.0
interest,2026-W13,13,mourning,1.0,1,1,0.0
interest,2026-W13,13,other,0.0,0,0,0.0
interest,2026-W14,14,education,9.666666666666666,9,11,1.1547005383792517
interest,2026-W14,14,marketing,8.0,8,8,0.0
interest,2026-W14,14,meme,0.0,0,0,0.0
interest,2026-W14,14,mourning,8.666666666666666,5,13,4.041451884327381
interest,2026-W14,14,other,1.3333333333333333,0,2,1.1547005383792517
interest,2026-W15,15,education,5.666666666666667,5,6,0.5773502691896257
interest,2026-W15,15,marketing,5.0,4,6,1.0
interest,2026-W15,15,meme,0.0,0,0,0.0
interest,2026-W15,15,mourning,14.0,12,17,2.6457513110645907
interest,2026-W15,15,other,5.333333333333333,3,7,2.081665999466133
interest,2026-W16,16,education,5.0
…(truncated)

### weekly_lag1_arm_week_summary.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_arm_week_summary.csv`

arm,week,week_num,supply_share_meme_mean,supply_share_meme_min,supply_share_meme_max,supply_share_meme_std,exposure_share_meme_mean,exposure_share_meme_min,exposure_share_meme_max,exposure_share_meme_std,meme_spoke_rate_mean,meme_spoke_rate_min,meme_spoke_rate_max,meme_spoke_rate_std,bias_meme_mean,bias_meme_min,bias_meme_max,bias_meme_std,supply_share_mourning_mean,supply_share_mourning_min,supply_share_mourning_max,supply_share_mourning_std,exposure_share_mourning_mean,exposure_share_mourning_min,exposure_share_mourning_max,exposure_share_mourning_std,total_supply_mean,total_supply_min,total_supply_max,total_supply_std,benchmark_meme_share,benchmark_mourning_share
interest,2026-W12,12,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,39.333333333333336,39,40,0.5773502691896247,0.0,0.0
interest,2026-W13,13,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.05042735042735036,0.0444444444444444,0.0555555555555555,0.005604648311369222,0.10000000000000002,0.1,0.1,0.0,40.0,36,45,4.58257569495584,0.0135185185185185,0.4364814814814815
interest,2026-W14,14,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.3662225
…(truncated)

### README.md (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/README.md`

# weekly_lag1_event_v2：Agent 发帖量预测与中间产物

## 当前结论：整体滞后方案已撤回并归档

用户将预测图与 `anchored_v1_interest_s0` 正式结果对比后指出，单纯解决注入时机不应改写整体动力学曲线。正式数据复核确认，差异来自整体滞后设计，而不是绘图误差。

请先查看：

- `timing_rethink/formal_timing_rethink.png`：`anchored_v1`与已完成`weekly_lag1`正式结果的对齐诊断。
- `timing_rethink/formal_timing_comparison.csv`：两轮正式结果的三种子周度均值。
- `timing_rethink/formal_timing_diagnostics.json`：原周标签与向前对齐一周后的相关系数和RMSE。
- `hypothesis_4/experiment_1/INJECTION_TIMING_REDESIGN_REVIEW.md`：重新设计建议。

`prediction_corrected/`中的图准确表达了“整体延迟一周”方案的代理走势，但该方案已撤回并归档，因此这张图不能视为当前实验的预测图。

当前正式方案已经恢复为 `anchored_v1` 的周级刺激—响应顺序：同周真实帖作为外部环境先进入并冻结所有Agent的feed；当周Agent帖在所有Agent行动结束后统一提交，从下一周起才影响其他Agent。这样可以消除Agent之间的同一步顺序偏差，同时保留原正式模拟的周度趋势。

## 预测边界

这是实验前的机制代理预测，没有调用LLM。程序执行正式环境的feed装配和确定性发言规则，但用上一轮已完成实验中各类Agent帖的分类倾向中位数代替新生成文本。因此，它适合检查峰值是否被配置强制制造、延迟方向和数量级，不应当作正式实验结果。

## 已撤回版本

`withdrawn_mechanical_scenario/`保存了原先使用5个等效悼念槽位生成的图表。该版本会把两组22个mourning Agent全部推过发言门槛，W13约42帖的峰值主要由参数机械叠加形成，已经撤回，不可用于论文或实验预期。

对应的敏感性诊断见`event_signal_salience_sensitivity.csv`。

## 文件夹说明

- `timing_rethink/`：正式结果的时序对齐诊断和重新设计证据。
- `prediction_corrected/`：整体延迟方案的代理预测；因方案正在撤回，仅作诊断。
- `withdrawn_mechanical_scenario/`：已撤回的错误预测，仅供审计。
- `event_signal_salience_sensitivity.csv
…(truncated)

### INJECTION_TIMING_REDESIGN_REVIEW.md (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/design_inputs/INJECTION_TIMING_REDESIGN_REVIEW.md`

# 注入时机重新设计审阅

## 结论

2026-09-28 已决定撤回“所有真实帖整体延迟一周”的 `weekly_lag1_event_v2` 方案，并恢复 `anchored_v1` 的周级刺激—响应顺序。需要修正的是论文中的时间语义说明，而不是把真实帖子整体后移。

推荐的周级顺序是：

1. 将来源周为 $W_t$ 的真实帖子作为该周的外生刺激载入环境。
2. 在任何 Agent 行动前冻结该周全部 Agent 的 feed 快照。
3. 所有 Agent 基于冻结快照各自决定是否发言并生成内容。
4. 当周 Agent 帖先进入 pending buffer；本周所有 Agent 完成后再统一并入帖子池。
5. 因此，当周 Agent 帖最早从 $W_{t+1}$ 起影响其他 Agent，任何 Agent 都看不到同一步中稍早生成的同伴帖子。

该顺序把真实帖子定义为实验输入，把 Agent 帖定义为模型响应。两者角色不同，不要求同时进入同一决策快照。周级模型表达的是“Agent对该周外部舆论环境的响应”，不声称复原一周内每条帖子的分钟级先后顺序。

## 为什么整体延迟改变了曲线

这次差异来自实验设计本身，不是绘图误差。

以 interest_s0 为例：

- `anchored_v1` 正式结果总量为：28、42、34、22、20、12、8、7、16、23、21。
- 已完成的 `weekly_lag1` 正式结果为：22、21、30、31、22、17、16、7、8、15、23。
- 当前无事件效用加成的代理结果为：22、19、31、37、23、16、14、7、3、17、22、20。

代理结果与已经完成的 `weekly_lag1` 正式结果接近，说明预测图呈现的是滞后设计的真实结构变化。

整体延迟造成了四个同时发生的变化：

1. W12不再使用W12真实帖，而改用W11初始化样本，起点的教育等内容结构发生变化。
2. W13官方讣告被保留在W13，但其他W13真实帖延迟到W14，同一个事件周的内容被拆成两个到达批次。
3. W14由Agent生成的响应帖在W15才可见，原本集中的响应进一步摊到W15。
4. 发言采用确定性门槛，并受累计曝光和疲劳影响。早一周的细小差异会改变后续哪些Agent跨过门槛，所以结果不是原曲线的机械平移。

三种子正式结果也支持这一解释。interest在原周标签下，`anchored_v1`与`weekly_lag1`总量相关系数为0.690；把滞后结果向前对齐一周后，相关系数提高到0.962，RMSE从7.41降到4.29。random对齐后的相关系数为0.959。也就是说，宏观趋势确实大体保留，但在行动周坐标上被平移，并且W13事件峰被拆散。

用户提供的 `anchored_v1_intere
…(truncated)

### WEEKLY_LAG_IMPLEMENTATION_REVIEW.md (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/design_inputs/WEEKLY_LAG_IMPLEMENTATION_REVIEW.md`

# weekly_lag1 实现审阅单

日期：2026-09-27；2026-09-28 更新。状态：6 个正式 run 已完成，随后因研究对象发生偏移而归档为信息延迟敏感性批。

## 实际改了什么

`CurationDynamicsSpace`新增三个默认关闭的周级配置项：普通真实帖滞后周数、首周历史样本路径、同周进入的官方帖子ID。只有6份新`interest/random`配置开启它们，旧配置仍按原周注入，`chronological`仍走原小时级路径。

新路径会同时保存三个周字段：`source_week`是帖子产生周，`available_week`是具备推荐资格的周，`injected_week`是实际进入池的周。帖子年龄始终从`source_week`计算。checkpoint还保存注入策略和已进入的外部source key；策略不匹配时拒绝恢复，防止混用旧run目录。

## 本轮输入如何流动

| 模拟周 | 本轮新进入的外部内容 | 数量 |
|---|---|---:|
| W12 | W11初始化历史 | 17 |
| W13 | W12普通帖 + W13官方讣告 | 18 |
| W14 | W13普通帖，不含已进入的讣告 | 34 |
| W15–W22 | 依次来自上一周普通帖 | 30, 24, 22, 19, 18, 18, 20, 23 |

窗口内合计243条。源于W22的24条普通帖子保留在原250条样本中，但要到W23才能进入，所以本轮不会使用。

## 已通过的检查

- 3份W11样本各17条，来源均为W11；每seed独立抽样。
- 6份配置除新增的三个时机字段外，与对应`anchored_v1`基线逐值一致。
- W15普通真实帖在W15不可见，在W16进入且仍记录为W15来源。
- W15真实帖和W15 Agent帖在W16首次可见时生命值相同，均为1周龄。
- 讣告只在W13进入一次；interest在W13置顶，random不置顶；W14不重复、不延长置顶。
- 实际逐周进入量为17/18/34/30/24/22/19/18/18/20/23，总量243。
- checkpoint恢复后不重复注入初始化内容、普通真实帖或讣告。
- 旧版完整离线门禁25/25通过；AgentSociety配置`validate`和`check`通过。
- 在本审阅单最初形成时，专用批跑入口只执行过`--dry-run`，列出的6个run均为pending；随后6个run已全部完成并归档。

## 历史运行入口

运行入口：

```bash
$PYTHON_PATH hypothesis_4/experiment_1/run_weekly_lag_batch.py --with-monitor
```

该入口曾
…(truncated)

### weekly_lag1_event_v2_manifest.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/design_inputs/weekly_lag1_event_v2_manifest.json`

{
  "experiment": "hypothesis_4/experiment_1",
  "round": "weekly_lag1_event_v2",
  "parent_round": "anchored_v1",
  "comparison_round": "weekly_lag1",
  "design": "普通真实帖与 Agent 帖均在来源周后一周首次可见；W13 唯一官方讣告仍同周进入。不以外生事件槽位直接改变任何 Agent 的发言效用，旧的 interest-only 哀悼保底关闭。W23 仅作 drain/readout，接收 W22 延迟帖，不注入 W23 来源外部帖；chronological 保持原设计且不重跑。",
  "run_ids": [
    "weekly_lag1_event_v2_interest_s0",
    "weekly_lag1_event_v2_interest_s1",
    "weekly_lag1_event_v2_interest_s2",
    "weekly_lag1_event_v2_random_s0",
    "weekly_lag1_event_v2_random_s1",
    "weekly_lag1_event_v2_random_s2"
  ],
  "protected_weekly_lag1_sha256": {
    "hypothesis_4/experiment_1/init/configs/weekly_lag1_interest_s0.json": "c397da193c30bc37806827584c83f56e172c1af0d4bc490b70fa9c4d00c15621",
    "hypothesis_4/experiment_1/init/configs/weekly_lag1_interest_s1.json": "bc8a9d1ac40892be4afed3753ed36f0885f1cdff60ec94f36fe6ab76f401da91",
    "hypothesis_4/experiment_1/init/configs/weekly_lag1_interest_s2.json": "0c17a8182c981f2988bc9c1a21551ebf783d84aa18e63777d6dc61450f70ded1",
    "hypothesis_4/experiment_1/init/configs/weekly_lag1_random_s0.json": "952fa035244cf43de6dea6b4f02d18972b910dfa0901dac01a18a9ada7df6792",
    "hypo
…(truncated)

### event_signal_salience_sensitivity.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/event_signal_salience_sensitivity.csv`

salience_slots,arm,mourning_posts,education_posts,marketing_posts,other_posts,meme_posts,total_posts,status
0.0,interest,1.0,6.3333,13.3333,0.0,0.0,20.6667,no_event_utility_adjustment
0.0,random,0.6667,7.0,13.0,0.0,0.0,20.6667,no_event_utility_adjustment
0.5,interest,3.0,6.3333,13.3333,0.0,0.0,22.6667,sensitivity_only
0.5,random,1.0,7.0,13.0,0.0,0.0,21.0,sensitivity_only
1.0,interest,8.0,6.3333,13.3333,0.0,0.0,27.6667,sensitivity_only
1.0,random,1.3333,7.0,13.0,0.0,0.0,21.3333,sensitivity_only
1.5,interest,12.0,6.3333,13.3333,0.0,0.0,31.6667,sensitivity_only
1.5,random,2.0,7.0,13.0,0.0,0.0,22.0,sensitivity_only
2.0,interest,19.0,6.3333,13.3333,0.0,0.0,38.6667,sensitivity_only
2.0,random,7.0,7.0,13.0,0.0,0.0,27.0,sensitivity_only
3.0,interest,22.0,6.3333,13.3333,0.0,0.0,41.6667,sensitivity_only
3.0,random,15.6667,7.0,13.0,0.0,0.0,35.6667,sensitivity_only
5.0,interest,22.0,6.3333,13.3333,0.0,0.0,41.6667,withdrawn_config_value
5.0,random,22.0,7.0,13.0,0.0,0.0,42.0,withdrawn_config_value

### manifest.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/manifest.json`

{
  "bundle": "weekly_lag1_event_v2_prediction",
  "updated_at": "2026-09-28T14:17:25+08:00",
  "status": "archived_superseded_not_for_main_inference",
  "recommended_design": "anchored_v1 restored as current weekly stimulus-response design",
  "organization_rule": "AgentSociety single-experiment analysis artifacts under presentation/hypothesis_4/data",
  "file_count_excluding_manifest": 39,
  "files": [
    {
      "path": "README.md",
      "category": "documentation",
      "source": "authored in review bundle",
      "bytes": 2943,
      "sha256": "26d2321202e8c1e443fdecf5f96491489800a524117c2b9c805c46b2772ab668"
    },
    {
      "path": "design_inputs/INJECTION_TIMING_REDESIGN_REVIEW.md",
      "category": "design_input_copy",
      "source": "hypothesis_4/experiment_1/INJECTION_TIMING_REDESIGN_REVIEW.md",
      "bytes": 6034,
      "sha256": "38629578b2d8c57626af30197d6c2392c93f50c4162286d1e2aebb53b591bc88"
    },
    {
      "path": "design_inputs/WEEKLY_LAG_IMPLEMENTATION_REVIEW.md",
      "category": "design_input_copy",
      "source": "hypothesis_4/experiment_1/WEEKLY_LAG_IMPLEMENTATION_REVIEW.md",
      "bytes": 2535,
      "sha256": "7a669330e8cf7930defb4f7a74a3e235f
…(truncated)

### predicted_agent_posts_by_type.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prediction_corrected/predicted_agent_posts_by_type.csv`

﻿arm,week,week_num,type,agent_posts_mean,agent_posts_min,agent_posts_max,agent_posts_std
interest,2026-W12,12,meme,0.0,0,0,0.0
interest,2026-W12,12,mourning,0.0,0,0,0.0
interest,2026-W12,12,education,3.3333333333333335,3,4,0.5773502691896257
interest,2026-W12,12,marketing,19.0,19,19,0.0
interest,2026-W12,12,other,0.0,0,0,0.0
interest,2026-W13,13,meme,0.0,0,0,0.0
interest,2026-W13,13,mourning,1.0,1,1,0.0
interest,2026-W13,13,education,6.333333333333333,4,8,2.0816659994661326
interest,2026-W13,13,marketing,13.333333333333334,13,14,0.5773502691896257
interest,2026-W13,13,other,0.0,0,0,0.0
interest,2026-W14,14,meme,0.0,0,0,0.0
interest,2026-W14,14,mourning,9.666666666666666,9,11,1.1547005383792515
interest,2026-W14,14,education,8.666666666666666,8,9,0.5773502691896257
interest,2026-W14,14,marketing,9.0,8,10,1.0
interest,2026-W14,14,other,2.6666666666666665,2,4,1.1547005383792515
interest,2026-W15,15,meme,0.0,0,0,0.0
interest,2026-W15,15,mourning,14.0,13,16,1.7320508075688772
interest,2026-W15,15,education,8.0,8,8,0.0
interest,2026-W15,15,marketing,4.666666666666667,4,5,0.5773502691896257
interest,2026-W15,15,other,8.666666666666666,7,11,2.0816659994661326
interest,2026-W16,16,meme,0.0,
…(truncated)

### predicted_agent_posts_run_level.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prediction_corrected/predicted_agent_posts_run_level.csv`

﻿run_id,arm,seed,week,week_num,type,agent_posts,mean_utility,mean_threshold,mean_observed_share,mean_effective_share,event_signal_active,proxy_content_tendency_source
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,meme,0,0.5383673110236563,0.9668,0.0,0.0,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,mourning,0,0.6853932670849768,0.9641590909090909,0.0,0.0,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,education,3,0.8711484343082997,0.9470133333333333,0.06666666666666667,0.06666666666666667,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,marketing,19,1.083194103663848,0.9538391304347825,0.8086956521739131,0.8086956521739131,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,other,0,0.4196413699855122,0.9515476190476191,0.0,0.0,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W13,13,meme,0,0.5383673110236563,0.9668,0.0,0.0,True,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W13,13,mourning,1,0.7657070988126494,0
…(truncated)

### predicted_agent_posts_total.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prediction_corrected/predicted_agent_posts_total.csv`

﻿arm,week,week_num,total_agent_posts_mean,total_agent_posts_min,total_agent_posts_max,total_agent_posts_std
interest,2026-W12,12,22.333333333333332,22,23,0.5773502691896257
interest,2026-W13,13,20.666666666666668,19,22,1.5275252316519468
interest,2026-W14,14,30.0,28,31,1.7320508075688772
interest,2026-W15,15,35.333333333333336,32,37,2.8867513459481287
interest,2026-W16,16,23.666666666666668,23,25,1.1547005383792515
interest,2026-W17,17,18.333333333333332,16,20,2.0816659994661326
interest,2026-W18,18,12.0,11,14,1.7320508075688772
interest,2026-W19,19,6.0,5,7,1.0
interest,2026-W20,20,3.6666666666666665,3,5,1.1547005383792515
interest,2026-W21,21,16.0,14,17,1.7320508075688772
interest,2026-W22,22,22.333333333333332,22,23,0.5773502691896257
interest,2026-W23,23,20.0,19,21,1.0
random,2026-W12,12,23.333333333333332,22,24,1.1547005383792515
random,2026-W13,13,20.666666666666668,19,22,1.5275252316519468
random,2026-W14,14,25.0,23,28,2.6457513110645907
random,2026-W15,15,21.666666666666668,17,25,4.163331998932265
random,2026-W16,16,17.333333333333332,14,19,2.8867513459481287
random,2026-W17,17,17.0,13,19,3.4641016151377544
random,2026-W18,18,12.0,10,15,2.6457513110645907
random,2026-W19,19,
…(truncated)

### prediction_summary.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prediction_corrected/prediction_summary.json`

{
  "artifact_status": "mechanism_only_proxy_prediction_not_experiment_result",
  "round": "weekly_lag1_event_v2",
  "weeks": [
    "2026-W12",
    "2026-W13",
    "2026-W14",
    "2026-W15",
    "2026-W16",
    "2026-W17",
    "2026-W18",
    "2026-W19",
    "2026-W20",
    "2026-W21",
    "2026-W22",
    "2026-W23"
  ],
  "seeds": [
    0,
    1,
    2
  ],
  "arms": [
    "interest",
    "random"
  ],
  "method": "Frozen v2 feed assembly and deterministic speaking rule; Agent-authored feedback uses median type-tendency vectors from the six completed weekly_lag1 runs; no LLM calls and no utility-level event boost.",
  "utility_level_event_boost": false,
  "prototype_tendencies": {
    "meme": {
      "mourning": 0.1207,
      "marketing": 0.6784,
      "education": 0.4485,
      "meme": 5.3223
    },
    "mourning": {
      "mourning": 2.7027,
      "marketing": 0.2809,
      "education": 1.1477,
      "meme": 0.0
    },
    "education": {
      "mourning": 0.0,
      "marketing": 1.2411,
      "education": 3.8934,
      "meme": 0.0
    },
    "marketing": {
      "mourning": 0.0,
      "marketing": 4.7511,
      "education": 1.7176,
      "meme": 0.0
    },
    "other": {
      
…(truncated)

### weekly_lag1_event_v2_agent_post_volume_prediction.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prediction_corrected/weekly_lag1_event_v2_agent_post_volume_prediction.png`

(binary file weekly_lag1_event_v2_agent_post_volume_prediction.png)

### weekly_lag1_event_v2_agent_post_volume_prediction.svg (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prediction_corrected/weekly_lag1_event_v2_agent_post_volume_prediction.svg`

(binary file weekly_lag1_event_v2_agent_post_volume_prediction.svg)

### weekly_lag1_interest_s0__chart3b_agent_supply_stacked_area.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_per_run/weekly_lag1_interest_s0__chart3b_agent_supply_stacked_area.png`

(binary file weekly_lag1_interest_s0__chart3b_agent_supply_stacked_area.png)

### weekly_lag1_interest_s1__chart3b_agent_supply_stacked_area.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_per_run/weekly_lag1_interest_s1__chart3b_agent_supply_stacked_area.png`

(binary file weekly_lag1_interest_s1__chart3b_agent_supply_stacked_area.png)

### weekly_lag1_interest_s2__chart3b_agent_supply_stacked_area.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_per_run/weekly_lag1_interest_s2__chart3b_agent_supply_stacked_area.png`

(binary file weekly_lag1_interest_s2__chart3b_agent_supply_stacked_area.png)

### weekly_lag1_random_s0__chart3b_agent_supply_stacked_area.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_per_run/weekly_lag1_random_s0__chart3b_agent_supply_stacked_area.png`

(binary file weekly_lag1_random_s0__chart3b_agent_supply_stacked_area.png)

### weekly_lag1_random_s1__chart3b_agent_supply_stacked_area.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_per_run/weekly_lag1_random_s1__chart3b_agent_supply_stacked_area.png`

(binary file weekly_lag1_random_s1__chart3b_agent_supply_stacked_area.png)

### weekly_lag1_random_s2__chart3b_agent_supply_stacked_area.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_per_run/weekly_lag1_random_s2__chart3b_agent_supply_stacked_area.png`

(binary file weekly_lag1_random_s2__chart3b_agent_supply_stacked_area.png)

### eda_figure_01_weekly_lag_meme_trajectory.png (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/eda_figure_01_weekly_lag_meme_trajectory.png`

(binary file eda_figure_01_weekly_lag_meme_trajectory.png)

### eda_figure_01_weekly_lag_meme_trajectory.svg (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/eda_figure_01_weekly_lag_meme_trajectory.svg`

(binary file eda_figure_01_weekly_lag_meme_trajectory.svg)

### eda_figure_02_weekly_lag_event_and_arm_gap.png (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/eda_figure_02_weekly_lag_event_and_arm_gap.png`

(binary file eda_figure_02_weekly_lag_event_and_arm_gap.png)

### eda_figure_02_weekly_lag_event_and_arm_gap.svg (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/eda_figure_02_weekly_lag_event_and_arm_gap.svg`

(binary file eda_figure_02_weekly_lag_event_and_arm_gap.svg)

### eda_figure_03_weekly_lag_agent_supply_stacked_area.png (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/eda_figure_03_weekly_lag_agent_supply_stacked_area.png`

(binary file eda_figure_03_weekly_lag_agent_supply_stacked_area.png)

### eda_figure_03_weekly_lag_agent_supply_stacked_area.svg (`eda`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/eda_figure_03_weekly_lag_agent_supply_stacked_area.svg`

(binary file eda_figure_03_weekly_lag_agent_supply_stacked_area.svg)

### weekly_lag1_agent_supply_by_type.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/weekly_lag1_agent_supply_by_type.csv`

arm,week,week_num,type,agent_posts_mean,agent_posts_min,agent_posts_max,agent_posts_std
interest,2026-W12,12,education,3.3333333333333335,3,4,0.5773502691896257
interest,2026-W12,12,marketing,19.0,19,19,0.0
interest,2026-W12,12,meme,0.0,0,0,0.0
interest,2026-W12,12,mourning,0.0,0,0,0.0
interest,2026-W12,12,other,0.0,0,0,0.0
interest,2026-W13,13,education,7.666666666666667,4,13,4.725815626252609
interest,2026-W13,13,marketing,13.333333333333334,13,14,0.5773502691896258
interest,2026-W13,13,meme,0.0,0,0,0.0
interest,2026-W13,13,mourning,1.0,1,1,0.0
interest,2026-W13,13,other,0.0,0,0,0.0
interest,2026-W14,14,education,9.666666666666666,9,11,1.1547005383792517
interest,2026-W14,14,marketing,8.0,8,8,0.0
interest,2026-W14,14,meme,0.0,0,0,0.0
interest,2026-W14,14,mourning,8.666666666666666,5,13,4.041451884327381
interest,2026-W14,14,other,1.3333333333333333,0,2,1.1547005383792517
interest,2026-W15,15,education,5.666666666666667,5,6,0.5773502691896257
interest,2026-W15,15,marketing,5.0,4,6,1.0
interest,2026-W15,15,meme,0.0,0,0,0.0
interest,2026-W15,15,mourning,14.0,12,17,2.6457513110645907
interest,2026-W15,15,other,5.333333333333333,3,7,2.081665999466133
interest,2026-W16,16,education,5.0
…(truncated)

### weekly_lag1_arm_week_summary.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/weekly_lag1_arm_week_summary.csv`

arm,week,week_num,supply_share_meme_mean,supply_share_meme_min,supply_share_meme_max,supply_share_meme_std,exposure_share_meme_mean,exposure_share_meme_min,exposure_share_meme_max,exposure_share_meme_std,meme_spoke_rate_mean,meme_spoke_rate_min,meme_spoke_rate_max,meme_spoke_rate_std,bias_meme_mean,bias_meme_min,bias_meme_max,bias_meme_std,supply_share_mourning_mean,supply_share_mourning_min,supply_share_mourning_max,supply_share_mourning_std,exposure_share_mourning_mean,exposure_share_mourning_min,exposure_share_mourning_max,exposure_share_mourning_std,total_supply_mean,total_supply_min,total_supply_max,total_supply_std,benchmark_meme_share,benchmark_mourning_share
interest,2026-W12,12,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,39.333333333333336,39,40,0.5773502691896247,0.0,0.0
interest,2026-W13,13,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.05042735042735036,0.0444444444444444,0.0555555555555555,0.005604648311369222,0.10000000000000002,0.1,0.1,0.0,40.0,36,45,4.58257569495584,0.0135185185185185,0.4364814814814815
interest,2026-W14,14,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.3662225
…(truncated)

### weekly_lag1_figure_notes.md (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/weekly_lag1_figure_notes.md`

# weekly_lag1 figure notes

- **Figure 1:** Three-seed arm means for meme supply, exposure, meme-agent speaking, and exposure-minus-supply bias. The real-data benchmark appears only where an aligned observed supply share exists.
- **Figure 2:** Mourning response, total supply, weekly interest-minus-random gaps, and W19-W22 mean comparisons.
- **Figure 3:** Agent-only weekly post counts by content type, stacked using three-seed arm means; colors and 0-80 scale follow the archived chart3b template.
- Bands and error bars are the minimum and maximum across three seeds. They are descriptive ranges, not confidence intervals.
- Source: all six completed `weekly_lag1_{interest,random}_s{0,1,2}` runs. The non-rerun chronological arm is excluded.

### weekly_lag1_run_week_metrics.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/weekly_lag1_run_week_metrics.csv`

run_id,arm,seed,week,week_num,total_supply,supply_share_meme,supply_share_mourning,exposure_share_meme,exposure_share_mourning,meme_spoke_rate,bias_meme,benchmark_meme_share,benchmark_mourning_share
weekly_lag1_interest_s0,interest,0,2026-W12,12,39,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
weekly_lag1_interest_s0,interest,0,2026-W13,13,39,0.0,0.0512820512820512,0.0,0.1,0.0,0.0,0.0135185185185185,0.4364814814814815
weekly_lag1_interest_s0,interest,0,2026-W14,14,64,0.0,0.421875,0.0,0.17,0.0,0.0,0.018585960065302,0.1817154338817028
weekly_lag1_interest_s0,interest,0,2026-W15,15,61,0.0163934426229508,0.360655737704918,0.011,0.279,0.0,-0.0053934426229508,0.0313459009206488,0.1613327487943884
weekly_lag1_interest_s0,interest,0,2026-W16,16,46,0.0217391304347826,0.2391304347826087,0.023,0.339,0.0,0.0012608695652173,0.0227675931401537,0.1466587817859254
weekly_lag1_interest_s0,interest,0,2026-W17,17,39,0.0256410256410256,0.2051282051282051,0.021,0.321,0.0,-0.0046410256410256,0.0237659963436928,0.1293418647166362
weekly_lag1_interest_s0,interest,0,2026-W18,18,35,0.0,0.1428571428571428,0.018,0.22,0.0,0.018,0.028169014084507,0.1011523687580025
weekly_lag1_interest_s0,interest,0,2026-W19,19,25,0.0,0.08,0
…(truncated)

### weekly_lag1_summary.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/prior_weekly_lag1/weekly_lag1_summary.json`

{
  "batch": "weekly_lag1",
  "run_count": 6,
  "seeds_per_arm": 3,
  "weeks": [
    "2026-W12",
    "2026-W13",
    "2026-W14",
    "2026-W15",
    "2026-W16",
    "2026-W17",
    "2026-W18",
    "2026-W19",
    "2026-W20",
    "2026-W21",
    "2026-W22"
  ],
  "uncertainty_display": "min-max across three seeds; not a confidence interval",
  "late_period_w19_w22": {
    "interest": {
      "supply_share_meme": {
        "mean": 0.30038692569352404,
        "min": 0.2854215365435562,
        "max": 0.3107822410147991
      },
      "exposure_share_meme": {
        "mean": 0.16116666666666668,
        "min": 0.1495,
        "max": 0.16825
      },
      "meme_spoke_rate": {
        "mean": 0.3640350877192982,
        "min": 0.32894736842105265,
        "max": 0.39473684210526316
      },
      "bias_meme": {
        "mean": -0.1392202590268574,
        "min": -0.1425322410147991,
        "max": -0.13592153654355615
      },
      "supply_share_mourning": {
        "mean": 0.0564907778161155,
        "min": 0.04762780697563303,
        "max": 0.062953180169025
      },
      "exposure_share_mourning": {
        "mean": 0.09508333333333334,
        "min": 0.0845,
        "max": 0.1072
…(truncated)

### anchored_v1_chronological_s0__chart3b_agent_supply_stacked_area.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/reference/anchored_v1_chronological_s0__chart3b_agent_supply_stacked_area.png`

(binary file anchored_v1_chronological_s0__chart3b_agent_supply_stacked_area.png)

### formal_timing_comparison.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/timing_rethink/formal_timing_comparison.csv`

﻿arm,week,anchored_formal_mean,lag1_formal_mean,lag1_shifted_back_one_week_mean
interest,2026-W12,27.333333333333332,22.333333333333332,22.0
interest,2026-W13,39.0,22.0,27.666666666666668
interest,2026-W14,33.0,27.666666666666668,30.0
interest,2026-W15,24.333333333333332,30.0,24.0
interest,2026-W16,20.333333333333332,24.0,17.0
interest,2026-W17,13.666666666666666,17.0,13.666666666666666
interest,2026-W18,8.333333333333334,13.666666666666666,6.666666666666667
interest,2026-W19,5.333333333333333,6.666666666666667,5.666666666666667
interest,2026-W20,15.0,5.666666666666667,13.333333333333334
interest,2026-W21,22.666666666666668,13.333333333333334,21.666666666666668
interest,2026-W22,20.666666666666668,21.666666666666668,
random,2026-W12,27.0,23.0,19.666666666666668
random,2026-W13,36.666666666666664,19.666666666666668,24.666666666666668
random,2026-W14,30.666666666666668,24.666666666666668,23.0
random,2026-W15,27.333333333333332,23.0,16.333333333333332
random,2026-W16,17.333333333333332,16.333333333333332,15.333333333333334
random,2026-W17,13.333333333333334,15.333333333333334,15.0
random,2026-W18,9.333333333333334,15.0,9.666666666666666
random,2026-W19,7.666666666666667,9.666666666666
…(truncated)

### formal_timing_diagnostics.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/timing_rethink/formal_timing_diagnostics.json`

{
  "interest": {
    "raw_correlation": 0.6897118993944062,
    "raw_rmse": 7.413473946780683,
    "one_week_aligned_correlation": 0.9615707553335296,
    "one_week_aligned_rmse": 4.2869310442060735
  },
  "random": {
    "raw_correlation": 0.8905966600333111,
    "raw_rmse": 6.043612539305652,
    "one_week_aligned_correlation": 0.9585486022410538,
    "one_week_aligned_rmse": 6.219146064997812
  }
}

### formal_timing_rethink.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/timing_rethink/formal_timing_rethink.png`

(binary file formal_timing_rethink.png)

### formal_timing_rethink.svg (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/timing_rethink/formal_timing_rethink.svg`

(binary file formal_timing_rethink.svg)

### predicted_agent_posts_by_type.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/withdrawn_mechanical_scenario/predicted_agent_posts_by_type.csv`

﻿arm,week,week_num,type,agent_posts_mean,agent_posts_min,agent_posts_max,agent_posts_std
interest,2026-W12,12,meme,0.0,0,0,0.0
interest,2026-W12,12,mourning,0.0,0,0,0.0
interest,2026-W12,12,education,3.3333333333333335,3,4,0.5773502691896257
interest,2026-W12,12,marketing,19.0,19,19,0.0
interest,2026-W12,12,other,0.0,0,0,0.0
interest,2026-W13,13,meme,0.0,0,0,0.0
interest,2026-W13,13,mourning,22.0,22,22,0.0
interest,2026-W13,13,education,6.333333333333333,4,8,2.0816659994661326
interest,2026-W13,13,marketing,13.333333333333334,13,14,0.5773502691896257
interest,2026-W13,13,other,0.0,0,0,0.0
interest,2026-W14,14,meme,0.0,0,0,0.0
interest,2026-W14,14,mourning,20.0,19,21,1.0
interest,2026-W14,14,education,8.333333333333334,6,10,2.0816659994661326
interest,2026-W14,14,marketing,8.333333333333334,8,9,0.5773502691896257
interest,2026-W14,14,other,2.3333333333333335,1,4,1.5275252316519468
interest,2026-W15,15,meme,0.0,0,0,0.0
interest,2026-W15,15,mourning,14.666666666666666,13,16,1.5275252316519468
interest,2026-W15,15,education,7.0,7,7,0.0
interest,2026-W15,15,marketing,5.0,4,6,1.0
interest,2026-W15,15,other,4.333333333333333,3,6,1.5275252316519468
interest,2026-W16,16,meme,0.3333333333333
…(truncated)

### predicted_agent_posts_run_level.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/withdrawn_mechanical_scenario/predicted_agent_posts_run_level.csv`

﻿run_id,arm,seed,week,week_num,type,agent_posts,mean_utility,mean_threshold,mean_observed_share,mean_effective_share,event_signal_active,proxy_content_tendency_source
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,meme,0,0.5383673110236563,0.9668,0.0,0.0,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,mourning,0,0.6853932670849768,0.9641590909090909,0.0,0.0,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,education,3,0.8711484343082997,0.9470133333333333,0.06666666666666667,0.06666666666666667,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,marketing,19,1.083194103663848,0.9538391304347825,0.8086956521739131,0.8086956521739131,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W12,12,other,0,0.4196413699855122,0.9515476190476191,0.0,0.0,False,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W13,13,meme,0,0.5383673110236563,0.9668,0.0,0.0,True,weekly_lag1 completed runs median
weekly_lag1_event_v2_interest_s0,interest,0,2026-W13,13,mourning,22,1.292583759979278,0
…(truncated)

### predicted_agent_posts_total.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/withdrawn_mechanical_scenario/predicted_agent_posts_total.csv`

﻿arm,week,week_num,total_agent_posts_mean,total_agent_posts_min,total_agent_posts_max,total_agent_posts_std
interest,2026-W12,12,22.333333333333332,22,23,0.5773502691896257
interest,2026-W13,13,41.666666666666664,40,43,1.5275252316519468
interest,2026-W14,14,39.0,38,40,1.0
interest,2026-W15,15,31.0,27,34,3.605551275463989
interest,2026-W16,16,20.333333333333332,19,22,1.5275252316519468
interest,2026-W17,17,14.333333333333334,13,16,1.5275252316519468
interest,2026-W18,18,11.0,6,17,5.5677643628300215
interest,2026-W19,19,8.333333333333334,7,10,1.5275252316519468
interest,2026-W20,20,5.0,4,6,1.0
interest,2026-W21,21,14.333333333333334,11,16,2.8867513459481287
interest,2026-W22,22,22.0,22,22,0.0
interest,2026-W23,23,20.0,19,21,1.0
random,2026-W12,12,23.333333333333332,22,24,1.1547005383792515
random,2026-W13,13,42.0,41,43,1.0
random,2026-W14,14,31.0,30,32,1.0
random,2026-W15,15,25.0,21,27,3.4641016151377544
random,2026-W16,16,16.666666666666668,15,18,1.5275252316519468
random,2026-W17,17,18.333333333333332,16,20,2.0816659994661326
random,2026-W18,18,12.333333333333334,9,16,3.511884584284246
random,2026-W19,19,11.333333333333334,9,13,2.0816659994661326
random,2026-W20,20,5.6666666666666
…(truncated)

### prediction_summary.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/withdrawn_mechanical_scenario/prediction_summary.json`

{
  "artifact_status": "mechanism_only_proxy_prediction_not_experiment_result",
  "round": "weekly_lag1_event_v2",
  "weeks": [
    "2026-W12",
    "2026-W13",
    "2026-W14",
    "2026-W15",
    "2026-W16",
    "2026-W17",
    "2026-W18",
    "2026-W19",
    "2026-W20",
    "2026-W21",
    "2026-W22",
    "2026-W23"
  ],
  "seeds": [
    0,
    1,
    2
  ],
  "arms": [
    "interest",
    "random"
  ],
  "method": "Frozen v2 feed assembly and deterministic speaking rule; Agent-authored feedback uses median type-tendency vectors from the six completed weekly_lag1 runs; no LLM calls.",
  "prototype_tendencies": {
    "meme": {
      "mourning": 0.1207,
      "marketing": 0.6784,
      "education": 0.4485,
      "meme": 5.3223
    },
    "mourning": {
      "mourning": 2.7027,
      "marketing": 0.2809,
      "education": 1.1477,
      "meme": 0.0
    },
    "education": {
      "mourning": 0.0,
      "marketing": 1.2411,
      "education": 3.8934,
      "meme": 0.0
    },
    "marketing": {
      "mourning": 0.0,
      "marketing": 4.7511,
      "education": 1.7176,
      "meme": 0.0
    },
    "other": {
      "mourning": 0.274,
      "marketing": 0.8572,
      "education": 0.8877
…(truncated)

### weekly_lag1_event_v2_agent_post_volume_prediction.png (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/withdrawn_mechanical_scenario/weekly_lag1_event_v2_agent_post_volume_prediction.png`

(binary file weekly_lag1_event_v2_agent_post_volume_prediction.png)

### weekly_lag1_event_v2_agent_post_volume_prediction.svg (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_event_v2_prediction/withdrawn_mechanical_scenario/weekly_lag1_event_v2_agent_post_volume_prediction.svg`

(binary file weekly_lag1_event_v2_agent_post_volume_prediction.svg)

### weekly_lag1_figure_notes.md (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_figure_notes.md`

# weekly_lag1 figure notes

- **Figure 1:** Three-seed arm means for meme supply, exposure, meme-agent speaking, and exposure-minus-supply bias. The real-data benchmark appears only where an aligned observed supply share exists.
- **Figure 2:** Mourning response, total supply, weekly interest-minus-random gaps, and W19-W22 mean comparisons.
- **Figure 3:** Agent-only weekly post counts by content type, stacked using three-seed arm means; colors and 0-80 scale follow the archived chart3b template.
- Bands and error bars are the minimum and maximum across three seeds. They are descriptive ranges, not confidence intervals.
- Source: all six completed `weekly_lag1_{interest,random}_s{0,1,2}` runs. The non-rerun chronological arm is excluded.

### weekly_lag1_run_week_metrics.csv (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_run_week_metrics.csv`

run_id,arm,seed,week,week_num,total_supply,supply_share_meme,supply_share_mourning,exposure_share_meme,exposure_share_mourning,meme_spoke_rate,bias_meme,benchmark_meme_share,benchmark_mourning_share
weekly_lag1_interest_s0,interest,0,2026-W12,12,39,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
weekly_lag1_interest_s0,interest,0,2026-W13,13,39,0.0,0.0512820512820512,0.0,0.1,0.0,0.0,0.0135185185185185,0.4364814814814815
weekly_lag1_interest_s0,interest,0,2026-W14,14,64,0.0,0.421875,0.0,0.17,0.0,0.0,0.018585960065302,0.1817154338817028
weekly_lag1_interest_s0,interest,0,2026-W15,15,61,0.0163934426229508,0.360655737704918,0.011,0.279,0.0,-0.0053934426229508,0.0313459009206488,0.1613327487943884
weekly_lag1_interest_s0,interest,0,2026-W16,16,46,0.0217391304347826,0.2391304347826087,0.023,0.339,0.0,0.0012608695652173,0.0227675931401537,0.1466587817859254
weekly_lag1_interest_s0,interest,0,2026-W17,17,39,0.0256410256410256,0.2051282051282051,0.021,0.321,0.0,-0.0046410256410256,0.0237659963436928,0.1293418647166362
weekly_lag1_interest_s0,interest,0,2026-W18,18,35,0.0,0.1428571428571428,0.018,0.22,0.0,0.018,0.028169014084507,0.1011523687580025
weekly_lag1_interest_s0,interest,0,2026-W19,19,25,0.0,0.08,0
…(truncated)

### weekly_lag1_summary.json (`other`, phase=explore)
- path: `presentation/hypothesis_4/data/weekly_lag1_summary.json`

{
  "batch": "weekly_lag1",
  "run_count": 6,
  "seeds_per_arm": 3,
  "weeks": [
    "2026-W12",
    "2026-W13",
    "2026-W14",
    "2026-W15",
    "2026-W16",
    "2026-W17",
    "2026-W18",
    "2026-W19",
    "2026-W20",
    "2026-W21",
    "2026-W22"
  ],
  "uncertainty_display": "min-max across three seeds; not a confidence interval",
  "late_period_w19_w22": {
    "interest": {
      "supply_share_meme": {
        "mean": 0.30038692569352404,
        "min": 0.2854215365435562,
        "max": 0.3107822410147991
      },
      "exposure_share_meme": {
        "mean": 0.16116666666666668,
        "min": 0.1495,
        "max": 0.16825
      },
      "meme_spoke_rate": {
        "mean": 0.3640350877192982,
        "min": 0.32894736842105265,
        "max": 0.39473684210526316
      },
      "bias_meme": {
        "mean": -0.1392202590268574,
        "min": -0.1425322410147991,
        "max": -0.13592153654355615
      },
      "supply_share_mourning": {
        "mean": 0.0564907778161155,
        "min": 0.04762780697563303,
        "max": 0.062953180169025
      },
      "exposure_share_mourning": {
        "mean": 0.09508333333333334,
        "min": 0.0845,
        "max": 0.1072
…(truncated)

## Section: findings

### claim:seed10_c1 (`claim`, phase=claims)
- path: `.agentsociety/analysis/hypothesis_4/claims.json`

沿用W19–W22作者供给口径，兴趣与时序均高于随机，新增7seed和合计10seed方向一致。 | evidence: data/seed10_runs.csv: late_meme_posts, late_meme_share; data/seed10_paired_contrasts.csv: interest-random, chronological-random; seed0–9同seed配对

### claim:seed10_c2 (`claim`, phase=claims)
- path: `.agentsociety/analysis/hypothesis_4/claims.json`

当前时序制度在同类所见和跨群体生成玩梗再展示上高于兴趣；供给份额9正1负，不支持兴趣最强。排序与生成帖更快入池、周内回流及候选规则未分离。 | evidence: data/seed10_paired_contrasts.csv: chronological-interest; data/seed10_runs.csv: own_share, meme_post_rate, cross_generated_share; custom/envs/curation_arrival_schedule.py:131-173,278-297

### claim:seed10_c3 (`claim`, phase=claims)
- path: `.agentsociety/analysis/hypothesis_4/claims.json`

按用户确认将新旧模型版本视为本研究等价，三臂各10seed合并作为主分析；旧3与新7制度排序一致，分批结果作为补充检查，精确版本标识保留溯源。 | evidence: 用户2026-10-24明确采用等价口径；data/analysis_summary.json:model_equivalence; data/seed10_sources.json:response_model_counts; data/seed10_arm_summary.csv:old3,new7,all10

### chart_01_seed10_trajectories.png (`chart`, phase=refine_validated_charts)
- path: `presentation/hypothesis_4/charts/chart_01_seed10_trajectories.png`

(binary file chart_01_seed10_trajectories.png)

### chart_02_seed10_model_cohorts.png (`chart`, phase=refine_validated_charts)
- path: `presentation/hypothesis_4/charts/chart_02_seed10_model_cohorts.png`

(binary file chart_02_seed10_model_cohorts.png)

### chart_03_seed10_paired_seeds.png (`chart`, phase=refine_validated_charts)
- path: `presentation/hypothesis_4/charts/chart_03_seed10_paired_seeds.png`

(binary file chart_03_seed10_paired_seeds.png)

### contract:seed10_fc1 (`contract`, phase=refine)
- path: `.agentsociety/analysis/hypothesis_4/state.yaml#figure_contracts`

新增7seed与旧3seed的周玩梗供给轨迹保持时序/兴趣高于随机；合计10不是独立新样本。 -> charts/chart_01_seed10_trajectories.png

### contract:seed10_fc3 (`contract`, phase=refine)
- path: `.agentsociety/analysis/hypothesis_4/state.yaml#figure_contracts`

配对seed支持时序/兴趣均高于随机，时序对兴趣份额有1个seed反向。 -> charts/chart_03_seed10_paired_seeds.png

### contract:seed10_fc2 (`contract`, phase=refine)
- path: `.agentsociety/analysis/hypothesis_4/state.yaml#figure_contracts`

三臂各10seed按用户确认的模型等价口径作为主分析；旧3与新7的制度排序一致，分批图仅作补充检查。 -> charts/chart_02_seed10_model_cohorts.png

## Embed checklist

- **data**: After `run-eda --type bundle`, run `embed-interactive-eda` (or `sync-report-assets`) to inject multi-tab interactive EDA into `report_*.html`; keep `<!-- EDA_INTERACTIVE_BEGIN -->` … `<!-- EDA_INTERACTIVE_END -->` in the HTML shell
- **findings**: `assets/` charts only (run `collect-assets`); caption under each figure
- **appendix**: artifact table + EDA/tool paths; HTML uses `report-shell.reference.html`
- Run `ags.py analysis guidance --topic reports` for required report files and embed rules
