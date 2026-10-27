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
  - `meme_post_rate` (`meme_post_rate`): min=0.013157894736842105, max=0.6842105263157895, avg=0.3785
  - `cross_generated_share` (`cross_generated_share`): min=0.0, max=0.287962962962963, avg=0.108
  - `all_feed_meme_share` (`all_feed_meme_share`): min=0.0295, max=0.47, avg=0.2287
  - `w13_mourning_posts` (`w13_mourning_posts`): min=2, max=21, avg=14.5333
  - `w13_mourning_rate` (`w13_mourning_rate`): min=0.09090909090909091, max=0.9545454545454546, avg=0.6606
**Categorical Stats**:
  - `run_id` (`run_id`): 30 unique, top: 'timestamp_v1_random_s9'(1), 'timestamp_v1_random_s8'(1), 'timestamp_v1_random_s7'(1)
  - `arm` (`arm`): 3 unique, top: 'random'(10), 'interest'(10), 'chronological'(10)
  - `cohort` (`cohort`): 2 unique, top: 'new7'(21), 'old3'(9)
  - `request_model` (`request_model`): 2 unique, top: 'deepseek-v4.1-flash'(21), 'deepseek-v4-1-flash-260910'(9)
  - `response_models` (`response_models`): 2 unique, top: 'deepseek-v4-1-flash-261017'(21), 'deepseek-v4-1-flash'(9)
  - `run_dir` (`run_dir`): 30 unique, top: 'hypothesis_4/experiment_2/runs/timestamp_v1_seed3_9/timestamp_v1_random_s9'(1), 'hypothesis_4/experiment_2/runs/timestamp_v1_seed3_9/timestamp_v1_random_s8'(1), 'hypothesis_4/experiment_2/runs/timestamp_v1_seed3_9/timestamp_v1_random_s7_retry1'(1)
  - `mourning_peak_week` (`mourning_peak_week`): 4 unique, top: '2026-W13'(22), '2026-W14'(5), '2026-W15'(2)

### Dataset: `seed10_weekly_metrics` (330 rows)
- Table: `seed10_weekly_metrics`
Sample data (first rows):
  Row 1:
  - week: 2026-W12
  - agent_supply: 24
  - agent_supply_meme: 0
  - agent_supply_mourning: 0
  - agent_supply_education: 5
  Row 2:
  - week: 2026-W13
  - agent_supply: 27
  - agent_supply_meme: 0
  - agent_supply_mourning: 2
  - agent_supply_education: 11
  Row 3:
  - week: 2026-W14
  - agent_supply: 29
  - agent_supply_meme: 0
  - agent_supply_mourning: 8
  - agent_supply_education: 8

**Numeric Stats**:
  - `agent_supply` (`agent_supply`): min=3, max=52, avg=18.3061
  - `agent_supply_meme` (`agent_supply_meme`): min=0, max=19, avg=2.6394
  - `agent_supply_mourning` (`agent_supply_mourning`): min=0, max=21, avg=3.2515
  - `agent_supply_education` (`agent_supply_education`): min=0, max=12, avg=3.6424
  - `agent_supply_marketing` (`agent_supply_marketing`): min=3, max=19, avg=6.4758
  - `agent_supply_other` (`agent_supply_other`): min=0, max=20, avg=2.297
  - `seed` (`seed`): min=0, max=9, avg=4.5
**Categorical Stats**:
  - `week` (`week`): 11 unique, top: '2026-W22'(30), '2026-W21'(30), '2026-W20'(30)
  - `run_id` (`run_id`): 30 unique, top: 'timestamp_v1_random_s9'(11), 'timestamp_v1_random_s8'(11), 'timestamp_v1_random_s7'(11)
  - `arm` (`arm`): 3 unique, top: 'random'(110), 'interest'(110), 'chronological'(110)
  - `cohort` (`cohort`): 2 unique, top: 'new7'(231), 'old3'(99)
  - `request_model` (`request_model`): 2 unique, top: 'deepseek-v4.1-flash'(231), 'deepseek-v4-1-flash-260910'(99)
  - `response_models` (`response_models`): 2 unique, top: 'deepseek-v4-1-flash-261017'(231), 'deepseek-v4-1-flash'(99)
  - `run_dir` (`run_dir`): 30 unique, top: 'hypothesis_4/experiment_2/runs/timestamp_v1_seed3_9/timestamp_v1_random_s9'(11), 'hypothesis_4/experiment_2/runs/timestamp_v1_seed3_9/timestamp_v1_random_s8'(11), 'hypothesis_4/experiment_2/runs/timestamp_v1_seed3_9/timestamp_v1_random_s7_retry1'(11)
