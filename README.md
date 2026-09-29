# 算法策展与公众人物身后数字表征

本仓库使用 AgentSociety 研究：推荐机制如何通过改变既有表达群体的可见度与参与，影响公众人物身后的公共数字表征。

**工作区继续采用 AgentSociety2 官方推荐的文件夹结构；研究思路从新增的 [runs/README.md](runs/README.md) 梳理。** 任务 README 提供目标、资产、实时进度和下一步；课题推进任务中的同主题方案解释已做过的实验和证据边界。项目总览不重复维护各任务进度。

## 阅读入口与职责

1. [TOPIC.md](TOPIC.md)：研究问题、理论目标和既有规模预算。
2. [AGENTS.md](AGENTS.md)：工作规范，与 [CLAUDE.md](CLAUDE.md) 共享正文。
3. [runs/](runs/README.md)：当前工作与后续决策的入口。
4. [ARCHIVE_MANIFEST_H4E1.md](ARCHIVE_MANIFEST_H4E1.md)：已运行批次、敏感性及撤回设计的证据分类。

根级 `runs/` 是用户新增的研究思路管理目录，管理方案、决策和交接，不替代官方实验目录。`data/` 同样由用户新增，用于本实验的预处理数据及相关处理材料。正式代码、实验配置和结果留在原来的官方对应位置，通过任务文档引用。一个算法×seed 的仿真运行是实验单元，不自动成为一个新工作任务。历史报告和机器来源清单可能存在口径冲突，使用前核对实际入口与冻结配置；本次已发现的冲突见活动任务 README。

## 根文件索引

| 文件 | 职责与使用方式 |
|---|---|
| [README.md](README.md) | 项目介绍与一级导航 |
| [AGENTS.md](AGENTS.md)、[CLAUDE.md](CLAUDE.md) | 唯一工作规范正文与兼容链接 |
| [TOPIC.md](TOPIC.md) | 研究主题与既有设计背景 |
| [TOPIC_1788166337268_0_u31u.md](TOPIC_1788166337268_0_u31u.md) | 初始主题澄清记录 |
| [PARAMETERS.md](PARAMETERS.md) | 参数说明；具体实验以对应冻结配置为准 |
| [EXPERIMENT_CONSTITUTION_1788335113228_0_gm0h.md](EXPERIMENT_CONSTITUTION_1788335113228_0_gm0h.md) | 实验约束及设计背景 |
| [实验设计阶段.md](实验设计阶段.md)、[锚定式事件表达激活模型.md](锚定式事件表达激活模型.md) | 实验设计与行为公式说明 |
| [ARCHIVE_MANIFEST.md](ARCHIVE_MANIFEST.md) | 历史资产总清单 |
| [ARCHIVE_MANIFEST_H4E1.md](ARCHIVE_MANIFEST_H4E1.md) | H4E1 批次证据分类 |
| [ARCHIVE_MANIFEST_H4E1_formal_20260913.md](ARCHIVE_MANIFEST_H4E1_formal_20260913.md)、[ARCHIVE_MANIFEST_H4E1_history_20260915.md](ARCHIVE_MANIFEST_H4E1_history_20260915.md) | 历史冻结批次与运行记录索引 |
| [词表_哀悼型_最终版.md](词表_哀悼型_最终版.md)、[词表_玩梗型_最终版.md](词表_玩梗型_最终版.md)、[词表_教育型_最终版.md](词表_教育型_最终版.md)、[词表_营销型_最终版.md](词表_营销型_最终版.md) | 各类型词表资产，使用时说明测量与生成用途 |
| [图表解读.docx](图表解读.docx) | 用户提供的经验图表解读 |
| [AgentSociety 2- An Integrated Research Environment for Executable Social Science.pdf](<AgentSociety 2- An Integrated Research Environment for Executable Social Science.pdf>) | 研究环境参考文档 |
| [env.template](env.template) | 不含真实凭据的环境模板 |
| `.env`、`easypaper_config.yaml` | 本地环境、服务与论文工具配置，含敏感信息，不提交 |
| [.gitignore](.gitignore) | 凭据、临时文件、大型数据和引擎产物的跟踪边界 |
| `.mcp.json` | 本地工具连接配置 |

## 一级目录索引

| 目录 | 职责 |
|---|---|
| [runs/](runs/README.md) | 用户新增：研究思路、方案、决策与交接入口 |
| [hypothesis_4/](hypothesis_4/) | 主假设、实验配置、兼容入口与派生结果；历史状态需与冻结证据核对 |
| [custom/](custom/) | 正式 Agent 与环境实现 |
| [data/](data/README.md) | 用户新增：本实验预处理数据，以及处理所需的输入、脚本和记录 |
| [datasets/](datasets/) | 仿真使用的数据资产 |
| [user_data/](user_data/) | 用户输入文件 |
| [papers/](papers/) | 文献检索与阅读材料 |
| [paper/](paper/README.md) | 论文、附录与审稿材料 |
| [presentation/](presentation/) | 分析图表、演示及相关来源清单 |
| [research/](research/) | 研究背景与探索材料 |
| [change/](change/)、[refine-logs/](refine-logs/) | 已有机制修改和方案探索记录；新日常任务从根级 runs 进入 |
| [archive/](archive/) | 本地冻结历史与批次原始结果，按根目录归档清单查找；不入 Git |
| `AgentSociety2/` | 上游引擎源码及虚拟环境，不随项目源码打包 |
| `.agentsociety/` | CLI 管理的流水线状态与工作区启动器 |
| `.claude/`、`.codex/` | 技能、工具与代理配置 |
| `agentsociety_data/` | 引擎运行产物与缓存，按相关任务索引复现 |
| `.git/`、`.vscode/`、`.playwright-mcp/`、`__pycache__/` | Git、编辑器与本地工具运行目录，不作为研究结论证据 |

## 环境和只读检查

从 `.env` 解析解释器，优先使用项目 uv 环境；不要输出密钥。研究工具入口：

```bash
PYTHON_PATH=$(sed -n 's/^PYTHON_PATH=//p' .env)
PYTHON_PATH=${PYTHON_PATH:-python3}
"$PYTHON_PATH" .agentsociety/bin/ags.py research-pipeline where-am-i --json
```

实验启动命令放所属任务或实验目录，只有确认方案、配置与预算在授权范围内才运行。部分历史验证器会导入配置生成器并写文件，不能仅凭“verify”名称判断它是只读工具。

## 证据与复现

三种推荐条件包含候选池和更新制度差异，应按完整策展制度解释；不能自动宣称为相同候选池下的纯排序效应。数值代理、完整 LLM 仿真、敏感性与预测图分别登记。当前研究方法和时间可见性的待决策事项从 runs 工作入口查阅。

Git 保留规则、代码、文档及允许跟踪的派生证据；原始 replay、大数据和本地 archive 可能被忽略。交付复现包时按对应 manifest 检查所需文件、符号链接和校验和，不能假设 `git archive` 含全部运行证据。公开真实帖子及作者数据前按具体交付范围检查使用授权。
