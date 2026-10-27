# 正式离线复算工具

所有工具只读取已完成批次，禁止网络/新LLM调用。九份配置及源哈希检查会拒绝参数或冻结输入漂移；不执行旧控制器、仿真启动或checkpoint续跑。

| 文件 | 职责 |
|---|---|
| [verify_schema.py](verify_schema.py) | 正式位置官方九配置check、693步schema和registry实际加载路径 |
| [extract.py](extract.py) | 12次官方replay SQL及环境/Agent三路对账，提取配对表和正式来源索引 |
| [mechanism.py](mechanism.py) | 已有D/R轨迹、228对晚期玩梗机会、原始Agent12记录和公式性质核验 |
| [plot.py](plot.py) | 12逐seed、4均值、3比较主图；沿用指定模板，不裁剪0–80轴 |
| [report.py](report.py) | 双语原生HTML/MD、逐周事实/机制推断及独立综合；登记用户已采纳 |
| [verify.py](verify.py) | 从原始记录独立复算27项指标，核对5394项来源、图片、字体及边界 |
| [chart3b_template.py](chart3b_template.py) | 原绘图模板字节副本，来源哈希在checks/template_and_exports.json |
| offline_guard/ | 仅本分析进程及其子进程禁网，不改全局环境 |

从项目根运行；解释器仅从.env读取PYTHON_PATH，不输出或复制密钥：

```bash
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
export PYTHONPATH="$PWD/hypothesis_4/experiment_3/analysis/offline_guard"
export BDR_ANALYSIS_NETWORK_AUDIT="$PWD/hypothesis_4/experiment_3/checks/network_attempts.jsonl"
export LITELLM_LOCAL_MODEL_COST_MAP=True
export MEM0_TELEMETRY=False ANONYMIZED_TELEMETRY=False
"$PYTHON_PATH" hypothesis_4/experiment_3/analysis/verify_schema.py
"$PYTHON_PATH" hypothesis_4/experiment_3/analysis/extract.py
"$PYTHON_PATH" hypothesis_4/experiment_3/analysis/mechanism.py
"$PYTHON_PATH" hypothesis_4/experiment_3/analysis/plot.py > hypothesis_4/experiment_3/checks/plot.log 2>&1
"$PYTHON_PATH" hypothesis_4/experiment_3/analysis/report.py
"$PYTHON_PATH" hypothesis_4/experiment_3/analysis/verify.py
```

生成器init/config_params.py可单独重建配置，先验全部源哈希；这不是LLM运行命令。正式分析依赖experiment_2的三个Full以及本experiment_3的九次原始结果，不依赖探索run。原始replay可能不入Git，独立复算须保留本机原始文件，不能声称仅git archive即可复现原始LLM。
