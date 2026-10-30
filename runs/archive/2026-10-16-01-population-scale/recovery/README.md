# 归档恢复材料

本run没有科学机制源码修改。baseline_source/custom从固定commit 69d243955d341444ae769fae5bf23dc160465cd6通过git archive取得，和原worktree逐文件核对一致，不含主区未提交custom。

## 安全入口

在项目根读取.env的PYTHON_PATH，用该解释器运行归档根verify_population_archive.py --offline-check。它在新临时目录恢复固定custom、全部有价值workspace文件/原链接（本机含原始输出）和冻结三臂配置，禁用所有socket连接后检查schema和环境构造，不启动LLM、Ray仿真或流水线。凭据.env不会复制到临时恢复目录或任何恢复材料。

GitHub副本使用--skip-raw可核代码/分析/配置，不冒充原始输出已核。完整复核需从本机归档复制raw_outputs并按raw_manifest.json校验；对照旧模型仍是正式experiment_2稳定冻结资产，SHA保留于原source_index。本归档不重跑或复制主区未提交结果。

## 材料

- files_manifest.json：可随Git保存文件/链接的SHA清单，不含.env、raw_outputs或缓存。
- raw_manifest.json：本机2710份原始输出的SHA和大小；raw Git忽略。
- workspace_preservation.json：全部工作区新增/改变状态及原相对链接。
- baseline_source/custom/：固定基线完整科学源码。
- workspace_progress.patch、original_sources/progress.json：唯一tracked进度差异与起点，重放已逐字节通过；完整终态在workspace_snapshot/.agentsociety/progress.json。
- path_map.json：原workspace与归档/raw映射，冻结记录不改。
- archive_preflight.json、environment.json：1387份原来源复核、凭据/忽略检查、自动汇报暂停与环境条件。
- verification_latest.json、archive_verification.json：本次实际临时恢复、原始终态、worktree安全移除和归档结果。
- pre_archive_README.md、workspace_git_status.txt：此前状态原文。

原历史准备/提取/报告脚本含当时workspace和层级假设，保留原字节，不作为归档默认入口。不声称它们迁移后可直接运行；报告冻结数据、图和新核验入口自含。正式采用、扩大规模或再次请求LLM需另行授权。
