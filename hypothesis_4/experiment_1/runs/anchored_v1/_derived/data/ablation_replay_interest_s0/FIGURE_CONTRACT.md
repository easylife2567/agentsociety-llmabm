# D/R/B 正式 replay 离线消融图合同

- **核心发现**：在正式 `anchored_v1_interest_s0` 的同一条 B/D/R 事实路径上，移除 B、D、R 会产生不同的周度供给构成。
- **图件范围**：三张模板同构单图 + 一张 2×2 总对比图。
- **图件角色**：趋势、构成、反事实比较。
- **证据来源**：正式 run 的 100 份 `agents/agent_*/AGENT.json` decision log；注入类型供给来自 `_derived/monitor/anchored_v1_interest_s0/status.json`。
- **分析范围**：100 Agents × 11 周 = 1100 个事实门控记录；full / no B / no D / no R。反事实发言统一按 1 帖计。
- **图件结构**：与 `anchored_v1_chronological_s1__chart3_supply_stacked_area.png` 相同的六类绝对供给堆叠面积。
- **视觉中心**：2×2 图中的三项消融与完整模型之间的形态差异。
- **坐标与分组**：横轴 W12–W22，纵轴 combined 供给绝对量；所有面板共同使用 0–100。
- **图例策略**：复用模板的六类固定颜色与标签；复合图只保留一个共享图例。
- **输出目录**：`runs/anchored_v1/_derived/charts/ablation_replay_interest_s0/`。
- **审稿风险检查**：no D 峰值 92，故不能照搬模板 0–80 而截断；事实路径有 1 次发言后未成功落帖，所有面板统一画门控隐含供给；离线反事实固定事实 D/R 路径，不应写成反馈路径重新演化的正式动态消融 run。
