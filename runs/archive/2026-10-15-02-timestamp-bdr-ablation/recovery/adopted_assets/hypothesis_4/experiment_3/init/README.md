# 九份timestamp消融配置

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
