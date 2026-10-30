# 100人模型服务测试冻结输入

本目录是workspace之外的恢复副本；实时授权、状态及结论统一见[run README](../README.md)。三臂无多seed重复；环境省略显式seed后默认0，不传模型seed。人口/样本/行动表引用旧主批s0作为共同参照。

| 资产 | 用途 |
|---|---|
| README.md | 本级索引与恢复说明 |
| manifest.json | 三臂矩阵、预算、源/输入哈希、对应旧主批及默认seed事实 |
| init_config.json | 官方check默认入口，等于interest配置 |
| steps.yaml | 原s0的693小时调度批，字节保留 |
| configs/ | 本轮random／chronological／interest三份实际配置，不含API凭据 |
| references/ | 原三臂s0科学配置，用于核对本轮唯一允许的差异 |
| inputs/ | 原真实窗口帖、历史池、人口及行动表的字节冻结；population文件保留旧版参照，实际执行人口在configs中，独立账本以实际配置为准 |

从记录commit建立干净工作区，将本目录完整复制为`hypothesis_4/experiment_4/init/`，保留custom代码和项目uv引擎版本；从工作区根运行manifest的config/steps/run_dir。凭据通过独立.env或环境变量配置，不复制主项目密钥。原始结果不在本目录，见run README。
