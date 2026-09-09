# Experiment 1：算法策展 × 悼念规范压力对逝者数字表征转移的影响

## 设计

全因子 **3 × 2 = 6 cells，每 cell 3 seeds，共 18 runs**：

| 因子 | 水平 |
|------|------|
| 推荐算法 `recommendation_algorithm` | random / chronological / interest（纯兴趣匹配，无热度项） |
| 悼念规范压力 `mourning_norm_pressure` | decay（内生逐周衰减）/ sustained（冻结 W13 峰值） |
| 种子 `random_seed` | 0 / 1 / 2 |

- 环境：`CurationDynamicsSpace`（custom/envs/curation_dynamics_space.py）
- Agent：`CurationDiscourseAgent`（custom/agents/，固定内容类型，~2-3 LLM 调用/agent-tick）
- 规模：100 agents × 11 ticks（2026-W12→W22，事件周 W13）× 18 runs ≈ 1.98 万 agent-ticks

## 群体（全部 18 runs 共享）

用户口径类型比例（xlsx author_handle，n=14,313）：**玩梗 41 / 悼念 21 / 营销 13 / 教育 13 / 其他 12**。
由 `curation_personas.build_population(seed=42)` 生成，id-类型打散；人设含沉默螺旋 /
注意力衰减 / 规范压力三机制的类型化表现（锚定数据挖掘实证）。

## 真实帖子注入（用户裁定：全程约 250 条）

- 源：custom/envs/curation_assets/injection_posts.json（52,716 行 W05–W22，剔除存疑）
- 每 seed 预抽样 250 条（`Random(seed+777)`，W12–W22 池）：保底 15/周 + 85 条按真实周量比例
  → W12=17, W13=35, W14=30, W15=24, W16=22, W17=19, W18=18, W19=18, W20=20, W21=23, W22=24
- W13/W14 保证 ≥1 条官方帖（官方议程置顶处理的载体）
- env 侧 `sampling_ratio=1.0`：样本文件即全量注入，不再二次抽样
- 样本文件：init/injection_sample_s{0,1,2}.json

## 配置产物（init/）

- `config_params.py` — 生成脚本（stdlib-only），`experiment-config run` 执行
- `configs/{algorithm}_{pressure}_s{seed}.json` — 18 个 init_config 变体
- `configs/manifest.json` — 批次清单（因子、共享群体、样本、运行命令）
- `init_config.json` — 默认配置（= interest_decay_s0，供标准 CLI / 冒烟）
- `steps.yaml` — start_t=2026-03-16（W12 周一），11 steps × 604800s（1 tick = 1 周）

固定 kwargs：feed_size=20，start_week=2026-W12，event_week=2026-W13，num_ticks=11，
agent_types 映射（100 agents），vocab_path=custom/envs/curation_assets/vocabs.json。
其余（α/β/γ=1.0/1.0/0.5、P_t 权重 0.3/0.4/0.3、official_pin_extend_weeks=1 等）
取 DesignSpec 默认值，待校准与敏感性分析（U2）。

## 运行方式

```bash
# 单个 run
$PYTHON_PATH .agentsociety/bin/ags.py run-experiment start \
  --hypothesis-id 4 --experiment-id 1 \
  --init-config hypothesis_4/experiment_1/init/configs/<run_id>.json \
  --run-id <run_id>
```

先冒烟 1 run（interest_decay_s0）确认管线与 LLM 预算，再跑全部 18 runs。

## 判类与指标口径

- 帖子主类型 = 作者类型（by construction）；env 判类器（悼念>营销>教育>玩梗>噪音>其他，
  仅用 main + meme 四列表）产出 assigned_type / type_mismatch 诊断。
- 主基准：benchmark_curves.json 周度类型矩阵 vs 模拟供给/曝光份额。
