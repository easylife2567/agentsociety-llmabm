# 逐行动审计

父级入口为[run README](../README.md)。本目录直接包含45个`条件_制度_s种子.jsonl.gz`文件；条件为current、sample_population、unique_authors、half_stress、double_stress；制度为random、chronological、interest；种子为0、1、2。每文件1100条agent×week唯一记录。

字段保留完整精度U/B/A、舍入的描述分量、曝光累计、feed稳定键/类型/来源、行动时刻候选池类型数量、开口判定、正文素材来源ID。素材正文在冻结输入中，审计不重复保存帖子全文。它们是数值代理审计，不是官方SDK replay或LLM生成日志。

完整精度效用和决策已独立复算49,500次；闭环扰动比较见父级experiment_summary.json。单文件SHA256在对应cell_metrics文件中登记；gzip时间戳不参与科学数据比较，恢复验证使用解压后的内容哈希。
