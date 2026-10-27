# 归档恢复与迁移材料

父级入口为[归档README](../README.md)。

| 资产 | 用途 |
|---|---|
| pre_archive_inventory.json | 归档前资产逐文件SHA256，不含workspace、tmp及缓存 |
| archive_baseline_recovery.json | 本次干净基线worktree恢复窗口与两个原单元的通过结果 |
| archive_u_recovery.json | 本次准确Git对象恢复静态映射与两个U候选单元的通过结果 |
| original_documents/ | 本次归档修改文档的前状态副本，保留迁移前路径及说明 |
| archive_verification.json | 迁移后资产、文档链接、worktree及完成状态的核验 |

基线69d243955d341444ae769fae5bf23dc160465cd6。已有源码未修改，无候选代码patch；新增脚本完整保留在父级。输入取父级frozen及manifest，依赖版本见manifest。verify_recovery.py的--run-dir传恢复副本（需有空tmp及父级冻结输入/脚本/原审计），--restored-root传从基线建立的干净worktree；verify_u_recovery.py放同样的恢复副本下执行即可，临时结果不会覆盖归档原始证据。只复算已登记的窗口、静态表和四单元，不重跑LLM或扩大矩阵。

历史manifest、日志、失败包及前状态证据不改写。原始文档副本中的链接按当时位置解释，不能用来判断现行导航。
