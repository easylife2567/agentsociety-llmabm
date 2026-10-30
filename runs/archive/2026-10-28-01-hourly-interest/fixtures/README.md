# 离线回归的补充输入

| 文件 | 用途 |
|---|---|
| [historical_content_sample.json](historical_content_sample.json) | 既有内容修复回归测试需要的一条W14历史生成文本，仅含week/content；不是新实验输入 |
| [provenance.json](provenance.json) | 原文件与最小提取版本SHA256、目标测试路径和提取说明 |

干净Git基线不含被忽略的历史Agent工作区，首次广义回归因此缺少该样本。提取本文件后由verify_tests.py放到隔离目标中的既有测试路径，不复制Agent配置或凭据、不修改原始历史记录。
