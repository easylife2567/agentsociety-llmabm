# timestamp兴趣制度消融配置

从冻结的三份timestamp-interest Full逐份复制，只把100位Agent的baseline_utility、spiral_scale、decay之一设为0；参数之外仅变更两项真实输入路径及共享重试账本路径。其余内容、人口、时钟、W13覆盖和推荐参数保留。

| 直接资产 | 用途 |
|---|---|
| [config_params.py](config_params.py) | 标准库生成器；先验来源哈希，后写九配置、默认入口和manifest |
| [source_lock.json](source_lock.json) | 精确Git基线、19份冻结来源及7份机制/词表哈希 |
| [manifest.json](manifest.json) | 九条件顺序、配对来源、输出哈希、操作差异和execution_authorized=false |
| [configs/](configs/README.md) | 三条件×seed 0/1/2，共九个独立变体 |
| [inputs/](inputs/README.md) | 字节不变的十二份配对输入/人口/行动表 |
| [reference/](reference/README.md) | 三份原Full配置及主批实际运行计划 |
| steps_s0.yaml、steps_s1.yaml、steps_s2.yaml | 对应主实验步骤字节副本，各693批 |
| init_config.json、steps.yaml | 官方check默认兼容入口，分别等于no_b_s0及steps_s0；不是额外第十个条件 |

共享新账本为`hypothesis_4/experiment_3/runs/timestamp_bdr_v1/_extra_attempts.count`，九run合计额外请求上限990；这是冻结的历史逻辑路径，实际已完成批次共享额外请求为5；映射及当前结果见上级runs/README.md，不创建新批或消耗预算。输入默认不吸收新user_data；原user_data为空。

九次已完成且用户已接受，现为主工作区正式配置。manifest中的execution_authorized=false保留准备期原值，不是当前结果未执行，也不构成新批授权；实际历史运行授权在runs中的runtime_plan，采用授权在adoption.json。

## seed3–9新增21份准备配置

[prepare_seed_extension.py](prepare_seed_extension.py)独立准备no_b/no_d/no_r×seed3–9；仅改变各100人一个指定参数为0及独立账本路径，不修改原config_params.py或九次默认入口。冻结配对、原指标、预算、时限与输出SHA256在[manifest_seed3_9.json](manifest_seed3_9.json)。reference/新增7份Full原字节副本，steps_s3–9.yaml保留主实验步骤原字节；真实输入沿用experiment_2已有冻结文件，不重抽、不改变内容时钟。

所有新增run_dir位于同一个runs/timestamp_bdr_v1_attempt_02主目录，准备验收时21个引擎目录均未创建；现已按后续授权正式启动，进度见上级README；控制计划和独立0账本在其execution_records/seed3_9。未来正式启动必须显式采用新manifest的配置与路径，不能用仍指向旧no_b_s0的init_config.json默认入口重跑旧结果。

复验生成资产（只读，不启动仿真）：用.env的PYTHON_PATH执行`init/prepare_seed_extension.py --check`。完整禁网验收为实验目录verify_seed_extension.py；接口探针已存在，不能自动再次调用。
