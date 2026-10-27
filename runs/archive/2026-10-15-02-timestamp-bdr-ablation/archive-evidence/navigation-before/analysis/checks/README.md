# 分析核验与流程记录

`baseline.json`记录任务开始的Git、主项目机器状态、消融执行记录和账本。`extraction.json`/`extraction.log`记录12次replay—环境—Agent三路对账；`pairing_and_identity.json`记录9900条消融/Full实际时钟配对及W12的B零权重审计；`template_and_exports.json`记录指定PNG和模板源哈希；`final_verification.json`记录27项原始记录复算、5394项源文件哈希、本地链接/字体/SVG和零新增调用。`dependencies.json`记录既有uv工具链版本。`artifact_integrity.json`为最终候选材料校验和。

其余JSON为本目录私有analysis CLI回执：frame/explore门禁通过，claims以approved=false登记；report-context-dry-run记录refine gate尚未通过，未伪造正式发布签署。没有独立模型reviewer调用。

保留的分析过程问题：intake首次缺少本目录技能定位链接（保留空stdout）；首次extract在W22帖子不在推荐池_posts时出现KeyError（extraction.failure-01.log）。现从final week_posts核对这些已成功发布帖，replay与所有决策记录对账通过，没有删除W22或改原始实验。两项均为本轮离线工具修正，不是新的正式实验失败；原403失败仍在run原位置。
