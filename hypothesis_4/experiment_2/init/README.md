# experiment_2配置与冻结输入

配置依据[实验方案](../EXPERIMENT.md)和同seed配对原则生成。官方`experiment-config run --hypothesis-id 4 --experiment-id 2`使用本目录生成器；不导入实验1有写入副作用的脚本。本轮只准备与离线验收，不启动LLM。详细进度统一见[实验README](../README.md)。

| 一级资产 | 职责 |
|---|---|
| [config_params.py](config_params.py) | 标准库生成器，读取冻结资产并校验人口、时间窗口及三臂共同参数；再次生成核对源哈希 |
| `inputs/` | 逐字节复制的六份样本、各seed共享人口和行动表；子目录README维护文件索引 |
| `configs/` | 九份timestamp_v1正式配置；子目录README维护文件索引 |
| `manifest.json` | 源/输出哈希、九run路径、完整性、机制和预算；execution_authorized=false |
| `steps_s0.yaml`、`steps_s1.yaml`、`steps_s2.yaml` | 各seed全部非空行动小时；末tick推进至2026-06-01 00:00，不添加行动 |
| `init_config.json`、`steps.yaml` | 官方默认兼容入口，分别逐字节等于interest_s0配置及s0步骤 |
| [README.md](README.md) | 本级资产与使用约束 |

以上生成资产由官方run命令写出，文件存在不代表实验已经运行。配置保留原B、数值参数和测量词表，人设仅清理确定性离世陈述。三臂共享timestamp时钟；random/interest保持次周回流，chronological批末回流；生命周期与议程键虽共同存在，仅相应推荐分支执行。

共享额外请求上限990、每次行动最多一次额外请求，独立ledger在experiment_2运行目录。该额度是配置限制，活动时长仍未授权；不继承旧四格24小时、440次额度或checkpoint。最终源码、测试、manifest及配置哈希已保存于上级配置验收记录；实际模型在未来启动前确定。生成器不读取凭据。
