# timestamp_v1三臂主实验（每臂10个seed）

这是假设4、实验2的统一主实验运行目录。random、chronological、interest各seed0–9，共30次完整条件；seed3–9已并入本目录，不作为另一项实验。当前状态和分析入口见[实验README](../../README.md)。2026-10-24仅整理目录，未启动、补跑或重做分析，消融未动；新旧模型按用户确认在本研究中视为等价，具体版本仍保留溯源。

## 完整结果

| seed | 随机 | 时序 | 兴趣 |
|---|---|---|---|
| 0 | [timestamp_v1_random_s0](timestamp_v1_random_s0/) | [timestamp_v1_chronological_s0](timestamp_v1_chronological_s0/) | [timestamp_v1_interest_s0](timestamp_v1_interest_s0/) |
| 1 | [timestamp_v1_random_s1](timestamp_v1_random_s1/) | [timestamp_v1_chronological_s1](timestamp_v1_chronological_s1/) | [timestamp_v1_interest_s1](timestamp_v1_interest_s1/) |
| 2 | [timestamp_v1_random_s2](timestamp_v1_random_s2/) | [timestamp_v1_chronological_s2](timestamp_v1_chronological_s2/) | [timestamp_v1_interest_s2](timestamp_v1_interest_s2/) |
| 3 | [timestamp_v1_random_s3](timestamp_v1_random_s3/) | [timestamp_v1_chronological_s3](timestamp_v1_chronological_s3/) | [timestamp_v1_interest_s3](timestamp_v1_interest_s3/) |
| 4 | [timestamp_v1_random_s4](timestamp_v1_random_s4/) | [timestamp_v1_chronological_s4](timestamp_v1_chronological_s4/) | [timestamp_v1_interest_s4](timestamp_v1_interest_s4/) |
| 5 | [timestamp_v1_random_s5](timestamp_v1_random_s5/) | [timestamp_v1_chronological_s5](timestamp_v1_chronological_s5/) | [timestamp_v1_interest_s5](timestamp_v1_interest_s5/) |
| 6 | [timestamp_v1_random_s6](timestamp_v1_random_s6/) | [timestamp_v1_chronological_s6](timestamp_v1_chronological_s6/) | [timestamp_v1_interest_s6_resume1](timestamp_v1_interest_s6_resume1/) |
| 7 | [timestamp_v1_random_s7_retry1](timestamp_v1_random_s7_retry1/) | [timestamp_v1_chronological_s7](timestamp_v1_chronological_s7/) | [timestamp_v1_interest_s7](timestamp_v1_interest_s7/) |
| 8 | [timestamp_v1_random_s8](timestamp_v1_random_s8/) | [timestamp_v1_chronological_s8](timestamp_v1_chronological_s8/) | [timestamp_v1_interest_s8](timestamp_v1_interest_s8/) |
| 9 | [timestamp_v1_random_s9](timestamp_v1_random_s9/) | [timestamp_v1_chronological_s9](timestamp_v1_chronological_s9/) | [timestamp_v1_interest_s9](timestamp_v1_interest_s9/) |

兴趣seed6采用resume1，随机seed7采用retry1，属于原条件的授权恢复，不另算seed。原[timestamp_v1_interest_s6/](timestamp_v1_interest_s6/)和[timestamp_v1_random_s7/](timestamp_v1_random_s7/)是保留的中断现场，不计入30次完整结果。

## 其他直接资产

| 资产 | 用途 |
|---|---|
| [execution_records/](execution_records/README.md) | 同一实验两次启动的计划、预算、原始状态、停止/恢复/完成证据及迁移前读取代码 |
| [relocation.json](relocation.json) | 30个最终条件的当前目录、2次中断现场、旧路径至新路径映射，以及28,700个原文件的大小和SHA256校验和；不是新的运行状态或实验结果 |

原始配置、状态、checkpoint、日志、来源清单和指标表保留原字节，其历史路径不批量改写。缺失的旧路径按relocation.json中moved_entries的最长前缀定位；读取辅助函数为[run_asset_paths.py](../../run_asset_paths.py)。合并前timestamp_v1_seed3_9实体目录已移除，没有保留第二个实验目录或软链接副本。

读取入口路径修订通过[run_storage_merge.patch](../../run_storage_merge.patch)先git apply --check后应用，新增辅助模块单独保留。基线commit、5份任务开始时的代码原字节与SHA256位于迁移清单及execution_records/code_before_storage_merge/；补丁仅包含本次路径解析和记录位置变更。冻结运行计划中的历史源码哈希仍对应迁移前代码，不能当作当前读取代码哈希；科学Agent/环境源码、冻结配置和输入均未改变。
