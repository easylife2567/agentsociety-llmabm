# 小时回流随机/兴趣seed1–9并行补齐

> 2026-10-30已归档。当前状态、路径映射与复验入口见[run README](../README.md)。以下为当时的执行/分析记录；历史控制器及含旧绝对路径的命令不再作为启动入口，原始记录保持。

用户于北京时间2026-10-29明确授权补齐随机/兴趣各seed1–9，共18次；复用已完成的两个seed0。本批仍在当前run的隔离workspace执行，不代表正式落地；时序、组件消融、更多seed、调参、commit/push和论文修改均不在本批范围。

实时人工状态统一见[run README](../README.md)。实际状态由本级run_extension.py单写batch_execution.json；不要手改，勿使用旧pilot停止入口操作本批。

本批18/18已于北京时间2026-10-29 06:08:20完成，全批复验、16140文件原始镜像及--check复算通过；实际模型均261017，103项冻结来源保持。复用seed0后随机/兴趣各10seed，共1702/2185帖。没有活跃监督器或本批引擎，每30分钟汇报的后台检查18已删除。12项控制器检查、18配置及1800份profile禁网预检属于启动前证据，收尾证据见checks/closeout*.log。

| 直接资产 | 用途 |
|---|---|
| [configs/](configs/README.md) | 18份执行配置，只更改候选的独立请求保护预算/账本 |
| [runtime_plan.json](runtime_plan.json) | 已冻结18次授权、两路顺序、103项来源、独立预算与seed0复用；绝对截止为北京时间10月31日00:10:02 |
| run_extension.py、test_extension.py | 新批监督器及禁网假进程检查；不重启、不恢复失败条件 |
| verify_preflight.py | 18配置官方结构/实例、1800份Agent创建恢复、来源与seed0复用的禁网预检 |
| closeout_extension.py | 全部完成后逐18复验、20行含复用seed0汇总及原始镜像保全；--check只复算不覆盖 |
| batch_execution.json | 监督器独占维护的实际状态，不手改 |
| completion_hourly_return_v1_{algorithm}_s{seed}.json | 每项自然完成后监督器保存的实际完整性、正文/模型与103项原始来源哈希 |
| extra_attempts.count | 本批独立共享额外请求账本，首次启动创建；不改旧pilot账本 |
| supervisor.log、supervisor.stderr.log | 本批监督器持久日志，启动后产生 |
| [checks/](checks/README.md) | 12项控制器检查、18配置/1800profile禁网预检与启动核对等证据 |
| completion_summary.json、completion_runs.csv | 收尾生成的18新运行＋2复用seed0实际汇总、正文请求/旧消耗分账与来源 |
| raw_results_manifest.json | 18份完整原始结果镜像的来源路径、目录和逐文件SHA256 |
| results/ | 已保全18个run共16140份原始文件，目录索引见results/README.md；Git忽略但不可当缓存删除 |

现阶段只读查看用`run_extension.py --status`；预检、启动和停止入口保留为历史，不重新调用。`--start-authorized`原本只允许全新启动一次，现有状态、账本或输出会拒绝重复。workspace原始结果位于`hypothesis_4/experiment_2/runs/hourly_return_v1/`，并已独立复制到本级results；每算法×seed单独目录，未包含seed0、时序或消融。

离线收尾复算：在本run目录执行`/Users/easylife/Project/AgentSociety/AgentSociety2/.venv/bin/python seed_extension/closeout_extension.py --check`，只核对，不改产物，不发模型请求。新批正文请求3508、额外1；复用seed0历史380、撤回时序历史30分别单列，跨批账面3918。先导seed0已看过结果的身份保留，汇总不冒充全部20次未看结果的前瞻验证，不据发帖数量直接判断整体效果最优。

新增19,800次行动机会、额外请求最多1,980次、正文外层请求最多21,780次，最多每行动一次额外。48小时保护以最终runtime_plan的绝对deadline_at为准，停机或交接不重置。该计数不等于全部SDK辅助调用或token账单。任一路失败、模型不符、预算或截止到达即停止本批，保留现场，不自动重试或resume。

所有成功正文须实际返回`deepseek-v4-1-flash-261017`，不发独立接口探针。完成时逐run核对693步、100名Agent、1100条完整唯一决策与环境行动、11周、真实正文及发布入池守恒；完成状态不依据监督器摘要单独推断。已有seed0来源和旧批410次账面正文请求保持单列，不作为本批新消耗或重新运行。
