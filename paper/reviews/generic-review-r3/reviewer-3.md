---
schema: agentsociety.paper-review.individual/v1
title: Internal Mock Review — Independent Reviewer R3
review_mode: author_side_internal_mock_individual
round_id: generic-r3
reviewer_id: R3
independence: isolated
input_manifest: paper/reviews/generic-review-r3/input-manifest.yaml
venue: generic
venue_edition: "project-local"
template_verified_at: "2026-09-25"
template_source: "none"
score_scale_origin: project_local
reviewed_at: "2026-09-25T20:24:49+08:00"
reviewed_artifacts:
  - path: "paper/manuscript/source/v3_20260915_2306_悼念退潮之后.pdf"
    sha256: 48a4111f22b7b8952d591e2e61721a1382b73e7c4579e4f0da25558cd2aa7340
  - path: "paper/manuscript/manuscript.accepted.md"
    sha256: 6945443a48ed2382fb84990db1c71de8ee5f57a181b8d6591da3bf40693049b6
  - path: "paper/appendices/附录Ⅰ和Ⅱ：Prompt模板与算法伪代码.md"
    sha256: f24ea9daf675e5cd4c916909a7a5ff038adf4c6b67ca084f0fed2070b03e4a41
  - path: "hypothesis_4/experiment_1/EXPERIMENT.md"
    sha256: 2ab46542078bf85521d678ee919edd7aa28881d6a8eec33233a3a9a9aca995e3
  - path: "hypothesis_4/experiment_1/ABLATION_anchored_v1.md"
    sha256: bd40881013aa417d5ffd7d14c55499779178f80f3095d50d031d5786ced84a55
  - path: "hypothesis_4/experiment_1/results/numerical_ablation_drb/RESULTS.md"
    sha256: 644dbc73456a14d317b37adf8740659b4348d1b4af1802ca6aae9e8076524a27
  - path: "hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_dtw_fit_summary.csv"
    sha256: 8ee15d5460b64a9b6c06bc56fbf5bfa40f89116d8bf04498a185f310ac12ece8
  - path: "hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_platform_user_chain.csv"
    sha256: 1543930ea5d57a72ca5b2e7f2bd16eaff9768aab32a88bc2a9cac5a1bf56d35d
  - path: "hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/benchmark.csv"
    sha256: ef841e6bce9e75a69cb7e787b5167864bd425d1e44988625e534212398cebded
pdf_intake:
  status: pass
  report_path: paper/reviews/generic-review-r3/pdf-intake/extraction-report.json
  report_sha256: fa2dd0a6a7fffb9fc28b8aacd73736c35187bfde6bc70cdcb99904a55547e3cc
  warnings: []
overall_score:
  value: 2
  label: Reject / substantial revision
confidence:
  value: 3
  label: fairly confident
recommendation: reject
primary_reroute: experiment_config
secondary_reroutes:
  - analysis
  - run_experiment
  - generate_paper
blocking_issue_ids:
  - W1
  - W2
  - W3
  - W4
---

# Internal Mock Review — Generic — R3

> This is one isolated author-side mock review. It is not an official venue review or acceptance prediction. The 1–5 scores below use a project-local rubric, not an ACM Web or CSCW review form.

## Review target

R3 reviews round `generic-r3` under the frozen [input manifest](input-manifest.yaml), primarily the 20-page manuscript `paper/manuscript/source/v3_20260915_2306_悼念退潮之后.pdf` (SHA-256 `48a4111f22b7b8952d591e2e61721a1382b73e7c4579e4f0da25558cd2aa7340`). I cross-checked the accepted Markdown, prompt/algorithm appendix, experiment and ablation records, numerical result summary, and three frozen derived CSVs listed in the frontmatter. The venue template is the project-local generic template, edition `project-local`. The manuscript is understandable as a Chinese research draft but not self-contained as a submission: page 18 points to workspace appendices for model details and data mining results. The raw post corpus, annotation audit, real platform exposure logs, and formal LLM ablation outputs were not part of the frozen evidence inspected here.

## Artifact intake and limitations

Shared PDF intake passed for all 20 pages with no warnings. I read its full `document.txt` and inspected rendered pages 6, 8, 10, 11, 13, 14, and 15 for Figure 1, the utility equations, Tables 1–4, and Figures 2–4. The equations are legible in the renders although several mathematical glyphs are corrupted in extracted text. No material element cited below remained unreadable. I did not independently verify the 52,716 individual posts, coder decisions, platform collection procedures, or live platform algorithms; the numerical CSVs allow checks of reported aggregates only.

## Paper summary

The paper studies the shift from education and mourning discourse to death-related memes after one Chinese public figure's death. It codes 52,716 posts from Xiaohongshu, Douyin, and Weibo, then injects a sample of real posts into a 100-agent simulation over 11 weeks. Nine LLM runs compare random, chronological, and interest feed regimes. A deterministic expression gate combines baseline activity, perceived own-type visibility, and attention decay; LLMs write text after the gate opens. The main finding is that all regimes show a late meme rise, with different exposure and agent posting patterns. A separate 100-seed numerical proxy removes each gate component.

## Claimed contributions

1. A measured three-stage shift in public representation, including delayed meme growth.
2. A mechanistic account of visibility, expression, and content feedback under different feed regimes.
3. A simulation framework and tentative platform governance implications for digital mourning.

## Venue scorecard

| Field | Score | Evidence and rationale |
|-------|-------|------------------------|
| Technical soundness | 2/5 | Paired seeds and explicit gate equations help, but real-platform causality and the separate roles of feed features are not identified (Methods pp. 7–9; Appendix B). |
| Novelty and relation to prior work | 3/5 | The intersection of posthumous memes and feed curation is interesting; Section 1 covers relevant mourning, meme, and algorithm literatures, but does not yet establish a distinct method or general mechanism against close CSCW/social computing work. |
| Significance | 3/5 | Digital mourning and representational power matter. One event and a stylized recommender limit the breadth of the conclusion (Introduction p. 2; Discussion pp. 16–18). |
| Empirical or theoretical evidence | 2/5 | Nine LLM runs, three seeds per regime, W22 overshoot, injected real content, and proxy-only ablation make the broad mechanism claim under-supported (Figures 2–4, rendered pp. 13–15). |
| Clarity | 3/5 | The real/simulated/mixed distinction is unusually explicit in Table 4 (rendered p. 11). Some claims exceed that distinction, and the denominator of key comparisons needs clarification. |
| Reproducibility | 3/5 | Appendix gives prompts, formulas, and pseudo-code; collection, coding reliability, model version, raw trace access, and exact fit pipeline remain insufficiently auditable from the reviewed bundle. |
| Limitations, ethics, and societal impact | 2/5 | Section 5 recognizes governance limits, but the paper lacks a concrete treatment of post privacy, consent/quotation, annotation sensitivity, and costs to legitimate criticism. |

**ACM Web 2027 fit.** A web-specific question about platform visibility is plausible for Social Networks and Social Media, Responsible Web, or Web Economics and Digital Society. The official [research-track call](https://www2027.thewebconf.org/research-track-papers/) requires an explicit Web challenge on page 1 and says merely using a social-network dataset is out of scope. The paper has such a question in principle, but the present causal evidence is too stylized to establish a Web system result. This PDF is also Chinese, single-column, 20 pages; the call specifies English, ACM double-column, and an 8-page self-contained main paper with at most 12 pages including appendix (references additional). Thus the current file is not submission-ready even if the scientific concerns were solved. These are venue-fit and format observations, not inputs to the project-local numerical score.

**CSCW 2027+ fit.** The digital mourning, social norms, and platform-mediated interaction question is a natural sociotechnical topic. Under the official [CSCW 2027+ route](https://cscw.acm.org/2026/rolling.html), a presentation follows acceptance in PACM HCI/CSCW or ToCHI; it is not a direct conference-paper deadline. The official [track guidance](https://cscw.acm.org/2026/tracks.html) allows quantitative, mixed-methods, systems, and design/theory work, each with matching evidence standards. This draft most nearly resembles quantitative social computing with a simulation component. It presently lacks the measurement validity and empirical connection needed for that path; it also lacks the qualitative grounding or user evaluation that could support a different CSCW contribution. A systems framing would require a clear system advance and evaluation beyond a stylized simulation. No CSCW score is inferred from the generic score.

## Strengths

- The question separates *how much* a person is discussed from *how* they are represented, which is more informative than a total-mention curve (Sections 1 and 5).
- The formal process records exposure, speaking, agent-only supply, and mixed supply separately; Table 4 (rendered p. 11) makes provenance explicit.
- Matching injections across three regimes and acknowledging that the DTW ranges overlap (p. 12, Figure 2 rendered p. 13) are good practices. The draft correctly says the 22.0 versus 23.7 mean difference is not statistically significant.
- The appendix discloses the persona, vocabulary, gate, feed construction, and simulation order, enabling targeted critique.

## Concerns

### W1 — Real platform causality is not identified by simulation fit

- Severity: major
- Paper pointer: Abstract p. 1; Section 2 pp. 6–9; Figure 2 rendered p. 13; Discussion pp. 16–17.
- Suggested reroute: experiment_config
- Why it matters: The main venue-level claim says platform algorithms and users jointly *caused* the observed public-memory shift and motivates visibility governance. A simulation can establish that stipulated rules suffice to generate a similar curve, but cannot determine that opaque real platforms used those rules or that real users reacted through the stipulated gate.
- Evidence: Approximately 250 real posts per week, preserving their observed time and type composition, are injected into every run. The gate hard-codes own-type visibility and attention decay. All three regimes reproduce the W20 phase while their W22 agent-only meme shares range from about 44% to 84% versus the 63% observed comparison (Section 4.1 and Figure 2). No actual impression/ranking data or user response observations are reported in the manuscript.
- Suggested action: Define the narrower structural-sufficiency claim and test it against a null that carries the same time-varying injection but no endogenous exposure-to-expression response. For a claim about real platforms, add an independent exposure or behavioral measure, or a credible natural/controlled intervention; specify the estimand and falsifier before running it.
- Resolution evidence: A preregistered contrast showing added predictive or mechanistic value beyond the injection-only/null process, and field evidence if the paper retains claims about actual platform algorithms.
- Score impact: A clean structural test plus bounded language could raise soundness/evidence by one point; substantiated field identification is needed for the broad causal conclusion. A null that explains the phase equally well lowers confidence further.

### W2 — Feed-regime differences bundle several mechanisms

- Severity: major
- Paper pointer: Section 2.2 pp. 7–8; Table 1 rendered p. 10; prompt/algorithm appendix B.3–B.7.
- Suggested reroute: experiment_config
- Why it matters: The paper attributes the high meme speaking rate under `Interest` to interest matching, and treats regime differences as a recommendation mechanism. That attribution requires a comparison in which the matching rule is the changed element.
- Evidence: The frozen appendix specifies `Interest` alone has a roughly three-week candidate life, exposure saturation, official pins, a W13 mourning floor, and weighted sampling. `Random` draws from all history without these components; `Chronological` uses hourly actions, latest-ten feeds, and within-week feedback, whereas the other two use weekly action batches. The experiment document itself describes the contrast as complete curation regimes.
- Suggested action: Add minimal matched contrasts holding candidate eligibility, pins/floor, and action timing constant while changing selection only; separately vary the other features if they remain claimed. If that design is unaffordable, report the result only as a comparison of bundled stylized regimes.
- Resolution evidence: A design matrix and completed contrasts that isolate interest weighting from candidate-age, pins/floor, and temporal feedback, with effect sizes on meme exposure and speaking.
- Score impact: Isolated effects would materially strengthen technical soundness; persistence only under bundled regimes would require a narrower conclusion.

### W3 — Observed shift and model fit need a denominator and coding audit

- Severity: major
- Paper pointer: Section 2.2 p. 6; Section 2.3 p. 9; Figure 2 rendered p. 13; Section 4.1 p. 12; frozen `benchmark.csv` and `arm_platform_user_chain.csv`.
- Suggested reroute: analysis
- Why it matters: The 52,716-post trajectory is the empirical anchor. Category validity, collection coverage, and a like-for-like fit definition determine whether the key shift and claimed model agreement are robust.
- Evidence: The paper states three human-coded columns and excludes 20 doubtful records but gives no coder count, overlap, agreement, adjudication, sampling frame, deduplication, or weekly platform mix. Xiaohongshu contributes 33,328 of 52,736 raw records; Weibo contributes 2,806. The paper compares a W22 observed meme share of 63.0% to modeled values of 44.3%/83.9%/83.9%. Yet the frozen `benchmark.csv` records W22 meme share 60.3% with noise present, while `arm_platform_user_chain.csv` records random W22 agent-only meme share 44.3% and mixed-supply meme share 55.6%. These may be intentionally different views, but the Figure 2 denominator and fit input are not fully traceable from the manuscript.
- Suggested action: Publish a measurement audit: platform/week sampling and deduplication flow, independent recoding of a stratified subset with disagreements, category examples/boundaries, and each figure's exact inclusion rule and denominator. Recompute the main curves and DTW under consistent core/full, agent-only/mixed, and platform-stratified alternatives.
- Resolution evidence: An auditable codebook, coding-quality report, and reproducible figure/fit table reconciling 60.3%, 63.0%, 44.3%, and 55.6%; robustness of the delayed rise across platforms and coding choices.
- Score impact: Robust reconstruction would raise empirical-evidence confidence; a shift driven mainly by one platform or denominator choice would lower significance and fit claims.

### W4 — Mechanism ablation does not yet exercise the full LLM system

- Severity: major
- Paper pointer: Table 3 rendered p. 11; Figure 4 rendered p. 15; `ABLATION_anchored_v1.md`; `results/numerical_ablation_drb/RESULTS.md`.
- Suggested reroute: run_experiment
- Why it matters: Section 5 treats B, D, and R as evidence for a real social mechanism. In the current evidence, their directional roles are consequences of an authored gate tested in a proxy, not an empirical validation of silence or attention in people.
- Evidence: The result file explicitly states that the 100-seed ablation did not call the LLM or run AgentSociety; post type in the proxy is the agent's fixed type. The registration lists three full-system ablation configurations but says formal LLM ablations have not run. Figure 4 plots proxy agent supply, and its 95% intervals are Monte Carlo variation only.
- Suggested action: Run the already specified matched full-system ablations and check whether generated-text classes and exposure/feedback paths agree with the proxy. Present the result as a model-component sensitivity test; empirical language about actual users requires separate evidence.
- Resolution evidence: Completed full-run logs, text-classification checks, matched contrasts, and a clear comparison to numerical proxy estimates.
- Score impact: Concordant full runs could raise reproducibility and internal mechanism evidence; disagreement would weaken the paper's central explanation.

### W5 — Submission format and normative scope need work

- Severity: minor
- Paper pointer: PDF pp. 1–20, especially abstract, Conclusion pp. 16–18, and Appendix pointer p. 18.
- Suggested reroute: generate_paper
- Why it matters: Venue reviewers need a self-contained, appropriately scoped paper. Governance recommendations concerning memorial content can affect criticism and satire as well as harassment.
- Evidence: The current PDF is 20 Chinese single-column pages; the first 8 pages do not contain the results. The discussion concedes that no governance policy was causally evaluated, yet still argues for lowering meme exposure and preserving mourning norms. No explicit data ethics or privacy protocol appears in the manuscript.
- Suggested action: After resolving W1–W4, write an English, venue-specific manuscript whose opening page states the contribution and whose claims stop at demonstrated effects. Add a precise ethics/data-handling statement and articulate whose interests a visibility intervention serves. A PI or ethics authority should decide any non-routine data-release or consent issue before public sharing.
- Resolution evidence: A compliant Web paper or a CSCW journal manuscript, with qualified governance claims and documented data handling.
- Score impact: Necessary for submission readiness, but prose and formatting alone would not change the present rejection.

## Questions and score-change conditions

1. What baseline using the identical observed injection schedule, but no feedback from simulated visibility to expression, produces the W19–W22 rise? If the current model outperforms it on a frozen check with transparent metrics, evidence rises; if not, retain only descriptive findings (W1).
2. How much of the `Interest`–`Random` or `Interest`–`Chronological` difference remains when candidate life, pinned/floor content, and event-time cadence are matched? A persistent differential supports matching as a mechanism; its disappearance supports only a bundled-regime interpretation (W2).
3. Who coded the posts, how was reliability/adjudication assessed, and what exact denominator enters Figure 2 and DTW? Reconciled, robust trajectories raise confidence; instability across coders or platforms lowers it (W3).
4. Do the registered full-system B/D/R runs reproduce proxy directions and content types? Agreement raises internal-model confidence, but does not itself validate human behavior; reversal lowers the overall score (W4).

## Limitations, ethics, and reproducibility

The one-event case, nonrepresentative and platform-skewed harvested sample, fixed user types, engineered utility, stylized feeds, and three main-run seeds bound generalization. The Figure 2 DTW ranges overlap; its interest-regime mean is not a statistically established winner. The numerical ablation's intervals describe simulation randomness, not population uncertainty. Detailed prompts and pseudo-code aid reproducibility, but the frozen review bundle lacks raw coded data, extraction scripts, annotation audit, and full ablation runs. A privacy and quotation policy is particularly important because the corpus contains public reactions to a death; any release of identifiable posts or material involving minors warrants accountable human review. No ethics violation is inferred from the available materials.

## Overall recommendation

**Project-local 2/5 — Reject / substantial revision; confidence 3/5.** The question and descriptive trajectory are promising, and a bounded simulation paper could be viable after stronger validation. The present evidence establishes behavior of a constructed model more clearly than behavior of actual recommendation systems or mourners. I would not submit this version to either target: ACM Web additionally has immediate language/page-format obstacles, while CSCW 2027+ requires the journal acceptance route and a stronger sociotechnical contribution. This is an internal readiness judgment, not an acceptance probability.

## Advisory reroute

Primary reroute: `experiment_config` for W1 and W2. The identification target and controls must be fixed before more runs or wording changes can establish the central mechanism. Ordered secondary reroutes are `analysis` for W3, `run_experiment` for the already defined formal ablations in W4 after the design is checked, and `generate_paper` for W5 and calibrated venue framing. Later-stage writing alone cannot repair a confounded comparison or an unaudited empirical benchmark; existing output analysis alone cannot isolate feed features that were never separately varied. A PI/ethics authority should make any consequential privacy or data-release decision. These are advisory routes; this review does not change pipeline state.

## Machine-readable handoff

```json
{
  "schema": "agentsociety.paper-review.individual-handoff/v1",
  "review_path": "paper/reviews/generic-review-r3/reviewer-3.md",
  "round_id": "generic-r3",
  "reviewer_id": "R3",
  "overall_score": {"value": 2, "label": "Reject / substantial revision"},
  "confidence": {"value": 3, "label": "fairly confident"},
  "recommendation": "reject",
  "primary_reroute": "experiment_config",
  "secondary_reroutes": ["analysis", "run_experiment", "generate_paper"],
  "blocking_issue_ids": ["W1", "W2", "W3", "W4"],
  "issues": [
    {"id": "W1", "severity": "major", "reroute": "experiment_config", "summary": "Simulation fit does not identify real platform causality"},
    {"id": "W2", "severity": "major", "reroute": "experiment_config", "summary": "Feed contrasts bundle candidate, pinning, and timing mechanisms"},
    {"id": "W3", "severity": "major", "reroute": "analysis", "summary": "Observed trajectory and fit need coding and denominator audits"},
    {"id": "W4", "severity": "major", "reroute": "run_experiment", "summary": "B/D/R ablation has only numerical proxy outcomes"},
    {"id": "W5", "severity": "minor", "reroute": "generate_paper", "summary": "Venue format and normative scope need revision"}
  ]
}
```
