# Ten-seed primary analysis: retained findings and attribution limits of the chronological configuration

Hypothesis 4 · Experiment 2 · Single-hypothesis integration · Revised 24 October 2026

## Adopted convention and primary conclusion

**As explicitly adopted by the user, the old and new models are treated as equivalent for this study (adopted convention). Pooling ten seeds per arm is the primary analysis; precise version labels are retained only for provenance.** The late-window direction of chronological and interest above random remains, with the complete chronological configuration generally higher. Its advantage cannot be attributed to chronological ranking alone because it also includes faster generated-post admission, within-week recirculation and different candidate rules. The [full report](../presentation/hypothesis_4/report_en.md) contains the original outcomes, three figures and verification evidence.

Scope remains 30 completed runs, 330 run×week rows and 6041 successful posts, with W19–W22 as the core window. Following original paper Figures 3/4, successful posts are classified by author agent_type; supply share is calculated within a run before averaging seeds. Interest seed6 uses its resumed copy and random seed7 its retry directory; failed attempts are excluded and duplicates avoided. Ablations, simulations and the paper are unchanged.

## From three to ten seeds: stable direction, differing details

Interest−random and chronological−random are positive on all five core outcomes for 10/10 seeds, including 7/7 added seeds. Leaving out any seed preserves the positive mean direction for five outcomes and three contrasts. All-ten late meme-author supply shares are 10.780%/75.011%/68.472% for random/chronological/interest, with late meme-author post counts of 3.1/45.4/37.8.

Chronological−interest supply share averages +6.539 percentage points, but reverses at seed5 by −1.347 points. Post count and posting rate have nine positives and one tie at seed5; within-group exposure and cross-group generated-meme redisplay have ten positives. “The complete chronological configuration is generally higher” is defensible; “interest is strongest” and “chronological is strictly higher on every outcome in every seed” are not.

Stability refers to late growth and arm ordering, not identical transition weeks. Meme authors lead mean weekly supply from W20 in chronological old3 and new7; in interest they lead from W21 in old3, W20 in new7 and W21 in all10. Marketing leads all arms in W12, so this is not full reproduction of a real-world education→mourning→meme sequence. W13 mourning peaks in all ten seeds of both structured arms are descriptive timing supplements.

## Main limit: generated-post admission and recirculation also change

[`curation_arrival_schedule.py` lines61–62](../custom/envs/curation_arrival_schedule.py#L61) give external real posts eligibility at the same published_at under timestamp mode in all three arms. Chronological does not obtain external posts earlier. Common eligibility does not imply identical exposure.

Agent-generated posts differ: [`step()` lines278–297](../custom/envs/curation_arrival_schedule.py#L278) admit chronological posts at the end of the current batch, making them visible in later hourly batches, whereas random and interest delay them until the next weekly boundary. Current-batch feed snapshots stay frozen and are not revised using that batch's output. [Lines131–173](../custom/envs/curation_arrival_schedule.py#L131) also specify candidate and selection differences: publication-time ordering, random sampling, and interest live candidates / floors / vitality rules.

The comparison is therefore a bundle of ranking, faster generated-post admission / within-week recirculation and candidate rules. Existing three-arm results cannot quantify each mechanism's separate contribution; exposure and redisplay do not identify an independent net causal effect of ranking or feedback. This design limitation, rather than version differences, is central to manuscript interpretation.

## Primary statistics and supplementary batch checks

Seeds are replicates. Each stratum has 15 exact two-sided sign-flip tests (five outcomes × three contrasts), corrected by Holm. The all-ten primary analysis has adjusted p=0.029296875 throughout. Old3 and new7 retain the same directional ordering as supplementary checks, with adjusted p values all 1 and 0.234375 respectively; the added-seven subset does not independently pass multiplicity correction. All10 contains the two subsets and is not an independent third cohort.

Complete enumeration still requires exchangeable signs or symmetric paired differences under the null. The t intervals use a small-sample approximation, and post-count/posting-rate dependence makes the 15-test correction conservative. The 33000 Agent×week decisions are not independent replicates. Provenance retains the old request deepseek-v4-1-flash-260910 and undated response deepseek-v4-1-flash, and the new request deepseek-v4.1-flash and response deepseek-v4-1-flash-261017. Model equivalence is the adopted study convention.

## Wording suitable for a subsequent manuscript

> Under the study convention treating old and new models as equivalent, the ten-seed-per-arm primary analysis using fixed W19–W22 author-supply and exposure definitions supports stable directions of interest and chronological above random, with the complete chronological configuration generally higher on late-window outcomes. Besides ordering by publication time, the chronological arm admits generated posts at batch end, allowing recirculation in later hourly batches within the same week; random and interest delay generated posts to the next week and candidate rules also differ. Observed differences therefore concern bundled configurations, and the present results cannot separate the contributions of ranking, generated-post admission and recirculation.

Author type is not independent text semantics, and ten numeric feed slots are not the first five prompt items or real reading. Interpretation remains limited to this 100-agent, 11-week simulation and its frozen configurations, without direct real-world generalization or expanded ablation or mechanism evidence.

## Evidence entry points

[Run outcomes](../presentation/hypothesis_4/data/seed10_runs.csv), [stratum means](../presentation/hypothesis_4/data/seed10_arm_summary.csv), [paired tests](../presentation/hypothesis_4/data/seed10_paired_contrasts.csv), [source records](../presentation/hypothesis_4/data/seed10_sources.json), and the [analysis summary](../presentation/hypothesis_4/data/analysis_summary.json). Original measurement is in [prepare_simulation.py](../paper/figures/scripts/prepare_simulation.py); admission and selection design is in [curation_arrival_schedule.py](../custom/envs/curation_arrival_schedule.py), both inspected read-only. [synthesis_brief.json](synthesis_brief.json) records scope and sources.
