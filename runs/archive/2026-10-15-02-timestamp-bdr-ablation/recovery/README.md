# 消融配置恢复包

恢复起点为`69d243955d341444ae769fae5bf23dc160465cd6`。本轮仅新增隔离experiment_3，不修改已有代码，所以没有代码patch或前置未提交差异。

以上指配置准备阶段的原45文件恢复包，作为冻结证据保持不变。后续输出布局修正修改了run控制器，新增恢复材料为[控制器起点及核验](../evidence/layout-fix/README.md)与[最终补丁](../output-layout.patch)：先按该baseline.json目标路径放回run_ablation.before.py，再应用补丁即可重建控制器。它不改变配置包，也不删除首次失败记录。

| 直接资产 | 用途 |
|---|---|
| [manifest.json](manifest.json) | 45份overlay文件的SHA256、精确commit、授权边界及依赖入口 |
| [overlay/](overlay/README.md) | 按目标相对路径保存的新增配置、输入、生成器和禁网验收工具 |

## 应用顺序

1. 从准确commit建立一个新的干净worktree；不复制主工作区未提交修改，不使用原workspace或其他run。
2. 逐项核对manifest中的overlay_sha256，将overlay里的`hypothesis_4/experiment_3/`复制到新worktree的同名位置。已有同名目录时先核查，不能覆盖未知内容。
3. 使用[依赖记录](../evidence/dependencies.json)中的现有项目解释器与SDK，确认已安装官方实验配置技能脚本的哈希。不要复制.env、凭据或重新构建环境。本包依赖记录的SDK/官方技能，不包含其运行时二进制。
4. 从新worktree根依次运行`verify_offline.py setup`、`generate`、`verify`，调用形式见[候选资产说明](overlay/hypothesis_4/experiment_3/README.md)。这些步骤不启动社会引擎，不调用LLM。
5. 比较重生成manifest与输出哈希；本包已在第二个干净worktree完成上述恢复和全套离线复验，证据见[恢复记录](../evidence/recovery/RESULT.json)。

恢复后九份配置、输入和新账本路径均在恢复worktree内。Full的历史配置作为来源冻结，但其原始LLM结果没有打包；本包用于配置与离线验收复现，不能用于凭空生成正式消融结果或重新计算Full结果。

运行授权仍为false。未来LLM启动需再确认本批授权和版本；正式采用、commit、push及归档不属于恢复操作。当前隔离workspace继续保留；本恢复包不是自动清理授权。

## 2026-10-18归档恢复交接

原45文件overlay与manifest保持字节不变；已在本run新建的干净基线worktree实际setup/generate/verify，通过900份profile、8100公式及26项继承测试，11项生成输出和manifest逐字节一致，证据在../archive-evidence/restore。原控制器从layout-fix/before按output-layout.patch、parallel-control.patch顺序check/apply重建一致，合成并行/联停复验通过，不启动实验。

workspace-final/保留原workspace的1891份独有资产，含完整CLI入口验收现场及机器状态；原始正式运行8165份文件已和../results/timestamp_bdr_v1_attempt_02及主项目独立副本核对一致。原workspace和本轮验证worktree已通过Git管理命令安全移除。

adopted_assets/及adopted_assets_manifest.json保存采用后的201份最终工具/配置/报告与独立Full依赖的2707项指纹。在空目录恢复201项校验通过，当前Full原始依赖亦核验通过；12单元主指标又从原始记录复算27项通过。配置可从Git基线和overlay恢复；结果分析还需要归档results及主项目experiment_2的冻结Full原始输出，不能凭代码重生LLM正文。未把其他活跃run列为依赖。

恢复历史控制器和候选analysis脚本时，应在临时检出中复原原runs/<run-id>/层级和workspace位置；不从runs/archive直接运行旧控制器，不复制.env或沿用过期48小时授权。正式离线复算优先采用主项目experiment_3/analysis，其来源已经脱离私有run。归档不授权新LLM、清空账本或重跑。
