# 图1效用公式与门槛科学含义复核

结论：最终公式、门槛、参数释义和环形机制通过核对。已再次实际查看四条释义统一8pt、主卡56mm宽的最终PNG，并对照正式Agent、小时行动入口和最新正文。未修改图件、代码或数据。

## 核对结果

- 公式U_it = B_i + R_it(D_it − B_i)与正式curation_mechanisms.anchored_utility返回值一致，保持baseline与当前气候间的锚定插值关系。
- U为Expression utility，B为Baseline expression utility，D为Opinion-climate response，均与正文一致。D为个人信息流中的同类表达构成所形成的气候响应，不是固定作者倾向或一般情绪值。
- 图中U_it ≥ activity_i → LLM generation符合正式小时入口curation_arrival_action.py:102的u >= agent._params['activity']；activity: Fixed individual threshold与现有个体参数一致，没有引入新阈值。该箭头只表示触发生成，并未承诺生成必然发布。
- R是随累计同类接触而衰减的注意力权重，R=exp(−λ·cum_own/15)。图中没有把R画作曝光量本身，也没有添加R减小时表达归零的错误关系。R趋零时U回到B。
- 成功发布图标、Hourly return与图注中的批末入池/后续批次可选一致。环形路径未暗示作者类型改变；三种模拟制度也没有绑定到两个真实平台。
- 空feed在U计算前被记为no_context。当前框架的信息流语境充分，不需要再画额外空feed分支，也未声称门槛在无内容时无条件触发发布。

## 最终英文释义

最终图中R已经改为“Exposure-dependent attention weight”，明确权重由累计接触决定，消除了此前exposure decay可能让读者误以为曝光量自身衰减的歧义。U/B/D及R四条释义均为8pt，当前56mm宽主卡内完整呈现，没有文本截断。主卡内公式和门槛未改变。

建议最终中文图注补充i为智能体、t为行动时点，activity_i为固定个体发言门槛，便于独立阅读。
