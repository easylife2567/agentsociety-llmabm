# Paper 工作区

本目录用于承接论文正文、附录、图件、参考资料与审阅记录。当前研究流水线仍处于 `analysis` 阶段；正文已经接入，但 `generate_paper` 尚未开始或完成。

## 目录

- `manuscript/source/`：作者提供的各版原始 DOCX 与 PDF，按版本和接收时间留档，不直接改写；当前版本为 `v3_20260915_2306_*`。
- `manuscript/manuscript.accepted.md`：从 DOCX 接受修订后导出的可检索文本，便于证据核对；它不是新的权威排版稿。
- `manuscript/media/`：当前 v3 DOCX 中嵌入的图件；`media_v1/`、`media_v2/` 保存历史版本图件。
- `manuscript/INTAKE_AUDIT.md`：本次正文接入、版本关系与待修订项。
- `appendices/`：作者维护的论文附录；保持现状，不由本次接入覆盖。
- `reviews/`：历史或进行中的审阅材料；不等同于已完成的官方 paper review。
- `refs_mechanism_D_R.*`：机制模型相关参考资料。

## 当前证据基线

`anchored_v1`曾是论文的正式仿真批，但已因真实帖注入时机修订被取代。其原始run已归档，以下聚合路径只用于复核旧稿，不能继续作为最新结论：

```text
hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/
```

完成性证据位于：

```text
hypothesis_4/experiment_1/runs/anchored_v1/_derived/monitor/overview.json
```

新的正式批为`weekly_lag1`：interest/random×3 seeds。新批完成并重新分析前，论文中的旧实验数值应标记为待更新。`hypothesis_4/experiment_1/run`现指向`weekly_lag1_interest_s0`。

历史烟测、旧正式批和中止残留不进入最新正式结果；历史材料已在工作区外层归档规则下单独保存，不应复制回 `hypothesis_4/` 或混入论文证据。

## 使用约定

1. 修改正文前，先阅读 `manuscript/INTAKE_AUDIT.md`。
2. 任何数值性结论优先回查 `_derived/data/arm/`，并明确真实数据、模拟数据与混合数据口径。
3. 当前 v3 DOCX 已无修订标记和批注。需要形成新版本时，仍应显式版本化，不覆盖 `source/` 中的原件。
4. 当前 v3 DOCX 与 PDF 接收时间相邻，PDF 已通过 20 页渲染检查；内容修订后仍需重新导出并复核 PDF。
5. 附录和审阅记录存在用户维护中的改动，正文整理不得顺手覆盖或清理。
