# Three arms, ten seeds each: stability after seed extension

Hypothesis 4 · Experiment 2 · timestamp_v1 · 30 completed main-experiment runs · 23 October 2026

**Under the convention explicitly adopted by the user, the old and new models are treated as equivalent for this study (adopted convention); pooling ten seeds per arm is the primary analysis, and precise version labels are retained only for provenance.** The direction of interest and chronological above random remains stable, with the complete chronological configuration generally higher on late-window outcomes. However, the chronological arm also admits generated posts sooner, permits within-week recirculation and uses different candidate rules; its advantage cannot be attributed to chronological ranking alone.

## 1. Scope and original measurement

This analysis covers only the three main arms, with seed0–9 in each arm. It updates neither ablations nor simulations. Measurement follows the original paper Figures 3/4 and `paper/figures/scripts/prepare_simulation.py`: successful `posted` outcomes are classified by author `agent_type`, without an independent semantic classification of the generated text. External, official and initial-pool posts are excluded from Agent supply; exposure outcomes retain their own source definitions.

The core window remains W19–W22. Late meme-author supply share is computed within each run and then averaged across seeds, rather than pooling posts first. Meme share seen by meme agents includes external and generated `type=meme` items over 760 numeric feed slots. Meme-agent posting rate uses 76 Agent×week opportunities. Cross-group generated-meme redisplay counts only `source=agent, type=meme` items over 3240 non-meme-agent slots. Ten numeric feed slots are not the first five items read in the text-generation prompt; observed redisplay is not an independently identified net feedback effect.

### Design interpretation: common external eligibility, different generated-post admission

This is the main attribution limit. In timestamp mode, [`curation_arrival_schedule.py` lines61–62](../../custom/envs/curation_arrival_schedule.py#L61) grant external real posts eligibility at the same `published_at` in all three arms. Common eligibility does not imply identical exposure. Generated-post admission and candidate selection differ.

| Design component | Chronological | Random / interest |
|---|---|---|
| External real-post eligibility | Same published_at | Same published_at |
| Agent-generated post availability | Admitted at the end of the current batch; visible in later hourly batches | Delayed until the next weekly boundary |
| Feedback within the current batch | Frozen feed snapshots are not revised | Frozen feed snapshots are not revised |
| Candidates / selection | Admitted candidates ordered by publication time | Random sampling / interest live candidates, floors, vitality and related rules |

[`step()` lines278–297](../../custom/envs/curation_arrival_schedule.py#L278) explicitly set generated-post `available_at` by arm; candidate and feed rules are at [lines131–173](../../custom/envs/curation_arrival_schedule.py#L131). The chronological arm is thus a bundle of ranking, faster generated-post admission / within-week recirculation and candidate rules. Shared external eligibility does not remove this difference. The present three-arm results cannot quantify each component's independent contribution; ablations and simulations remain unchanged.

## 2. Data and verification

The analysis includes 30 completed runs, 330 run×week rows and 3000 Agent workspaces, with 6041 successful posts. Each completed run has 100 agents, 11 weeks, 693 steps, 1100 unique environmental actions and complete unique decisions without failures. Seeds are the statistical replicate; neither the 3000 workspaces nor 33000 Agent×week decisions are independent observations.

| Data layer | Included scope | Verification role |
|---|---:|---|
| Run level | 30 rows | Ten seeds per arm; original five outcomes |
| Weekly level | 330 rows | W12–W22 trajectories and late window |
| Agent workspaces | 3000 | posted, author type, decisions and feed records |
| Successful posts | 6041 | Posts from the completed scientific results |

[EDA quick statistics](data/seed10_quick_stats/eda_quick_stats.md) and the [exploration audit](data/seed10_explore.md) document dimensions, outcome distributions and measurement reproduction; the [evidence index](data/evidence_index.json) links sources. The old nine-run weekly table and the original paper Figures 3/4 run-level metrics reproduce cell for cell. Only the current `seed10_*` assets enter this report; unrelated historical analyses in the index do not enter these results.

Recovery paths are fixed in the [source manifest](data/seed10_sources.json): interest seed6 uses `timestamp_v1_interest_s6_resume1`, and random seed7 uses `timestamp_v1_random_s7_retry1`. The failed original random seed7 attempt, with 224 actions, 54 posts and 54 body requests, remains operational evidence and is excluded from completed scientific results. The original and resumed interest seed6 directories are not double counted. Historical requests in the operational budget and scientific outcomes in this report use distinct accounting scopes.

## 3. Finding 1: both structured arms retain their advantage over random

`seed10_c1`: Under the original W19–W22 author-supply definition, interest and chronological both exceed random, with the same direction in the added seven seeds and all ten. These two paired contrasts are positive for all ten seeds on the five core outcomes, and for 7/7 seeds within the extension. The following are seed-level means, n=10 per arm.

Table 1: All-ten-seed W19–W22 means; percentages use the original denominator within each run before averaging.

| Metric | Random | Chronological | Interest |
|---|---:|---:|---:|
| Late meme-author posts | 3.100 | 45.400 | 37.800 |
| Meme-author supply share | 10.780% | 75.011% | 68.472% |
| Meme share seen by meme agents | 3.224% | 43.632% | 26.316% |
| Meme-agent posting rate | 4.079% | 59.737% | 49.737% |
| Cross-group generated-meme redisplay share | 0.114% | 24.920% | 7.373% |

The mean late supply-share difference is +57.692 percentage points for interest minus random, with an approximate paired-mean t 95% interval of 52.978–62.406; chronological minus random is +64.231 points, with an interval of 60.413–68.049. Extending the seeds adds repeated evidence for the original direction: no seed puts either structured arm below random.

![Figure 1: Weekly meme-author supply in W12–W22; old3, new7 and all10 retain the same direction, with shading showing the observed seed range rather than a confidence interval.](assets/chart_01_seed10_trajectories.png)
Figure 1: Weekly meme-author supply in W12–W22; old3, new7 and all10 retain the same direction, with shading showing the observed seed range rather than a confidence interval.

Stability refers to late growth and arm ordering; the transition week can differ by one week. By the largest category in mean weekly author supply, meme authors lead chronological from W20 in both cohorts. They lead interest from W21 in old3, W20 in new7 and W21 in all10. Marketing leads all three arms in W12, so this simulation does not establish a full education→mourning→meme sequence observed in real-world data.

As a descriptive supplement, the mourning-author supply peak occurs in W13 for 10/10 seeds in both chronological and interest, while random peaks often occur later. This is consistent with event-timing response but supplies no new causal identification of a mechanism and does not replace the late-window outcomes.

## 4. Finding 2: chronological is generally above interest, with one seed exception

`seed10_c2`: Chronological exceeds interest in within-group meme exposure and cross-group generated-meme redisplay. Its supply-share difference is positive in 9/10 seeds and negative in one, so the findings do not support interest as strongest. Late meme-author post count and posting rate have nine positive differences and one tie, at seed5. Late supply share reverses at seed5 by −1.347 percentage points; the other nine differences are positive. Within-group exposure and cross-group generated-meme redisplay are positive in all ten paired comparisons.

Chronological minus interest in late supply share averages +6.539 percentage points, with an approximate paired t 95% interval of 3.592–9.487. Meme share seen by meme agents is 43.632% versus 26.316%, and cross-group generated-meme redisplay is 24.920% versus 7.373%. These are comparisons of complete curation configurations, not an isolated effect of chronological ranking. Faster generated-post admission and later-hour within-week recirculation vary together with ranking and candidate rules, and their separate contributions cannot be quantified from these results.

![Figure 3: Within-seed contrasts place interest and chronological above random; chronological minus interest in supply share reverses for seed5 and is positive for the other nine seeds.](assets/chart_03_seed10_paired_seeds.png)
Figure 3: Within-seed contrasts place interest and chronological above random; chronological minus interest in supply share reverses for seed5 and is positive for the other nine seeds.

Leaving out any single seed preserves the positive mean direction for all five outcomes and all three contrasts. Thus no single seed drives the aggregate ordering. This does not mean every individual contrast is strictly positive, and it does not separate ranking from generated-post admission and related mechanisms.

## 5. Batch provenance and supplementary robustness

`seed10_c3`: Under the adopted study convention that the models are equivalent, all ten seeds form the primary analysis. Old3 and new7 are supplementary robustness strata and retain the same qualitative ordering. Provenance: old seed0–2 requested `deepseek-v4-1-flash-260910` and returned the undated alias `deepseek-v4-1-flash`; new seed3–9 requested `deepseek-v4.1-flash` and returned `deepseek-v4-1-flash-261017`.

Table 2: Old seed0–2, n=3 per arm.

| Metric | Random | Chronological | Interest |
|---|---:|---:|---:|
| Late meme-author posts | 3.000 | 43.000 | 36.333 |
| Meme-author supply share | 10.324% | 73.300% | 65.614% |
| Meme share seen by meme agents | 3.202% | 42.018% | 25.175% |
| Meme-agent posting rate | 3.947% | 56.579% | 47.807% |
| Cross-group generated-meme redisplay share | 0.113% | 22.737% | 6.842% |

Table 3: Added seed3–9, n=7 per arm.

| Metric | Random | Chronological | Interest |
|---|---:|---:|---:|
| Late meme-author posts | 3.143 | 46.429 | 38.429 |
| Meme-author supply share | 10.975% | 75.745% | 69.697% |
| Meme share seen by meme agents | 3.233% | 44.323% | 26.805% |
| Meme-agent posting rate | 4.135% | 61.090% | 50.564% |
| Cross-group generated-meme redisplay share | 0.115% | 25.855% | 7.601% |

Late supply share in the added cohort averages 75.745% for chronological and 69.697% for interest, compared with 73.300% and 65.614% in the old cohort. Random averages 10.975% versus 10.324%. These supplementary strata preserve the qualitative ordering before and after extension. All10 is the primary analysis, containing old3 plus new7, and is not double counted as a third independent cohort.

![Figure 2: The five original W19–W22 metrics supplementarily stratified by execution batch; interest and chronological exceed random, and all10 combines old3 and new7 rather than forming an independent cohort.](assets/chart_02_seed10_model_cohorts.png)
Figure 2: The five original W19–W22 metrics supplementarily stratified by execution batch; interest and chronological exceed random, and all10 combines old3 and new7 rather than forming an independent cohort.

Figure 2 uses untruncated approximate t 95% intervals. Its vertical axes start at zero, so some negative lower bounds for old3 random are outside the plot. Full untruncated intervals are in `seed10_arm_summary.csv`; a negative bound reflects an unbounded approximation, not negative posts or proportions.

## 6. Statistical interpretation and conclusion limits

Within each cohort, the five outcomes and three paired contrasts form a 15-test family, using exact two-sided sign flips and Holm multiplicity correction. Exact refers to complete enumeration of sign combinations; it still requires exchangeable signs or symmetric paired differences under the null. It is not an assumption-free causal test. Meme-author post count and posting rate are linearly related, so the 15-test family contains redundancy and correction is conservative. The t mean intervals use a small-sample distributional approximation, are not simultaneous intervals.

| Cohort | Seeds per arm | Holm-adjusted p across 15 tests | Supported interpretation |
|---|---:|---:|---|
| Old3 | 3 | All 1 | Same direction, limited test resolution |
| New7 (supplementary) | 7 | All 0.234375 | Directional agreement; subset does not independently pass corrected 0.05 |
| All10 (primary) | 10 | All 0.029296875 | Ten-seed paired comparisons support configuration differences |

**Under the adopted model-equivalence convention, the pooled ten-seed primary analysis supports stable directions of interest and chronological above random; the complete chronological configuration is generally higher on late outcomes, and interest is not strongest.** The added-seven supplementary analysis is directionally consistent, although its 15 corrected tests do not independently pass 0.05. The main attribution limit is simultaneous variation in ranking, faster generated-post admission / within-week recirculation and candidate rules; the results cannot quantify their separate contributions.

External validity is limited to this 100-agent, 11-week simulation and its frozen complete curation configurations. Author type does not independently confirm the semantics of a post; numeric feed exposure does not establish actual reading or real-user exposure; generated-post redisplay does not identify a net causal feedback contribution. Ablations remain untouched, so prior limits on mechanism decomposition remain. No conditions, simulations or raw outcomes were added or modified for this analysis.

## 7. Appendix: auditable artifacts

| File | Purpose |
|---|---|
| [seed10_runs.csv](data/seed10_runs.csv) | Thirty completed runs, model labels and original five outcomes |
| [seed10_weekly.csv](data/seed10_weekly.csv) | 330 run×week rows under the original definition |
| [seed10_arm_summary.csv](data/seed10_arm_summary.csv) | old3/new7/all10 means and intervals |
| [seed10_paired_contrasts.csv](data/seed10_paired_contrasts.csv) | Differences, signs, exact tests, Holm and leave-one-out means |
| [seed10_sources.json](data/seed10_sources.json) | Actual run paths, hashes, model responses and denominators |
| [seed10_metrics.sqlite](data/seed10_metrics.sqlite) | Thirty run rows and 330 weekly rows |
| [Evidence index](data/evidence_index.json) | Sources for figures, data and claims |

Figures 1–3 use the same thirty completed runs; the Chinese and English reports contain matching figures and numbers. The figures cover trajectories, supplementary execution-batch robustness and paired seeds, not additional experiments.
