# experiment_2配置与冻结输入

**当前已采用hourly_return_v1**：见[新版30配置与来源](hourly_return_v1/README.md)。三臂生成帖统一批末回流，真实结果为新两臂20次及复用时序10次；没有重跑授权。下文原生成器、默认入口、旧manifest与旧预算仍属于timestamp_v1历史设计，保持字节以保证既有结果可追溯，不能当新版默认启动入口。

配置依据[实验方案](../EXPERIMENT.md)和同seed配对原则生成。官方`experiment-config run --hypothesis-id 4 --experiment-id 2`使用本目录生成器；不导入实验1有写入副作用的脚本。本轮只准备与离线验收，不启动LLM。详细进度统一见[实验README](../README.md)。

| 一级资产 | 职责 |
|---|---|
| [hourly_return_v1/](hourly_return_v1/README.md) | 当前采用主实验30份机制配置、接收清单及准备期原件；实际预算与结果另指正式矩阵 |
| [prepare_seed_extension.py](prepare_seed_extension.py) | 仅准备seed 3–9的新增21配置及样本；`--check`只读复算，拒绝覆盖不一致资产 |
| [manifest_seed3_9.json](manifest_seed3_9.json) | 新增主实验批次的冻结清单、原规则复算、历史候选资格修正、独立输出与账本路径；execution_authorized=false |
| `steps_s3.yaml`–`steps_s9.yaml` | 新seed各693批，与原steps_s0.yaml逐字节相同 |
| [config_params.py](config_params.py) | 标准库生成器，读取冻结资产并校验人口、时间窗口及三臂共同参数；再次生成核对源哈希 |
| `inputs/` | 原seed0–2冻结输入及新增seed3–9样本、各seed共享人口和行动表；子目录README维护文件索引 |
| `configs/` | 原九份及新增21份timestamp_v1配置，分别由两个manifest冻结；子目录README维护文件索引 |
| `manifest.json` | 源/输出哈希、九run路径、完整性、机制和预算；execution_authorized=false |
| `steps_s0.yaml`、`steps_s1.yaml`、`steps_s2.yaml` | 各seed保留原63小时调度网格；W13原hour18为空批；末tick推进至2026-06-01 00:00，不添加行动 |
| `init_config.json`、`steps.yaml` | 官方默认兼容入口，分别逐字节等于interest_s0配置及s0步骤 |
| [README.md](README.md) | 本级资产与使用约束 |

原seed0–2由官方run命令写出，新增seed3–9由prepare_seed_extension.py直接准备，文件存在不代表实验已经运行。配置保留原B、数值参数和测量词表，人设仅清理确定性离世陈述。三臂共享timestamp时钟；random/interest保持次周回流，chronological批末回流；生命周期与议程键虽共同存在，仅相应推荐分支执行。

原seed0–2共享额外请求上限990、每次行动最多一次额外请求，独立ledger在experiment_2运行目录。该额度是配置限制，活动时长仍未授权；不继承旧四格24小时、440次额度或checkpoint。最终源码、测试、manifest及配置哈希已保存于上级配置验收记录；实际模型在未来启动前确定。生成器不读取凭据。

W13共同覆盖表由独立固定种子20261009确定，仅顺延5位悼念Agent；三臂三seed共享。原小时表用于其他周，环境覆盖和5份profile覆盖来自同一映射；行动表及manifest保存选择规则和原新时刻，steps逐字节保留。当前源码与配置哈希见上级2026-10-09-06-ordinary-official-verification.json；早期验收记录是原版本证据。

九配置共同声明arrival_official_policy=ordinary。正式custom环境据此让官方退出置顶和悼念保底、进入普通兴趣评分/抽样；其他悼念保底与参数保持。生成器仅声明配置，不承担推荐执行。

## 主实验seed 3–9补充准备

扩充仅覆盖random/chronological/interest三臂，21个新增配置，与既有seed 0–2合计每臂10个seed；消融不扩充。旧config_params.py、manifest.json、默认入口及全部旧样本/配置/steps保持原字节。本次使用独立新增脚本，不运行会重写旧资产的官方生成命令。项目根执行：

```bash
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
"$PYTHON_PATH" hypothesis_4/experiment_2/init/prepare_seed_extension.py
"$PYTHON_PATH" hypothesis_4/experiment_2/init/prepare_seed_extension.py --check
```

窗口250帖仍按Random(seed+777)及原逐周类型分层最大余数法生成。历史17帖仍按Random(seed+1777)及原类型分层规则，但先执行既有timestamp历史资格：上海发布时间严格早于2026-03-16 00:00。原W11标签池890条中有6条时间跨界，合规池为884条；未经资格修正的seed 4/8均抽中pid4496并会被现有引擎拒绝初始化。修正前后对seed 0–2复算的帖子、次序、全部字段仍与原样本完全一致；对seed 3–9的逐seed差异和6条排除记录均在manifest中披露。没有重抽seed、修改时间戳或改动引擎。

人口、行为参数、词表、63小时网格和W13五人顺延完全继承；同seed三臂只在推荐算法上不同。新人口文件仅替换额外请求配置为新批共享上限2310及独立账本。新增共23100次行动机会；该上限是配置约束，不是调用授权。未来输出隔离在`experiment_2/runs/timestamp_v1_seed3_9/`，本次不创建运行结果或账本，不启动仿真。旧启动器固定旧九次批次，不适用于新增矩阵。

完整70MB原始池继续使用Git中已有冻结资产，manifest记录准确基线commit和SHA256；恢复时按记录commit取回并核验字节，不复制另一份源池。新增样本自身均保存在inputs中。模型及运行条件核对与离线验收结论见实验级记录；本脚本不读取凭据。

目录整理补注（2026-10-24）：上述准备阶段的timestamp_v1_seed3_9输出声明保留历史上下文。已完成seed3–9现与seed0–2统一存于[同一主实验目录](../runs/timestamp_v1/README.md)，原冻结配置和manifest中的历史路径保持原字节，按其relocation.json解析。
