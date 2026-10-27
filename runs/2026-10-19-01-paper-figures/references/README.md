# 框架图参考

从已安装skill的本地索引筛选framework/pipeline及agent、society、causal主题，实际查看以下三图后选取布局规律；这些是他人论文参考图，不属于本项目研究结果。索引固定版本538355a3fdd4d4475e00fe48adbbae54a890a6c5。图片来自指定画廊，仅用于内部设计参考，未嵌入本项目SVG。

| 图像 | 论文来源 | 借鉴布局 |
|---|---|---|
| [proagent.jpg](proagent.jpg) | [ProAgent, AAAI 2024](https://ojs.aaai.org/index.php/AAAI/article/view/29710) | 主循环与机制细节分层；本图采用单一主回路，减少交叉线 |
| [adasociety.jpg](adasociety.jpg) | [AdaSociety, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/3e4d8407cb468850f2f8f4a949e64bf0-Abstract-Datasets_and_Benchmarks_Track.html) | 色彩分区与清晰组件边界；用于现实、仿真、比较三分区 |
| [causal-pipeline.jpg](causal-pipeline.jpg) | [End-To-End Causal Effect Estimation, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/8d2aad53fa148791ffd004a7c9cce5ad-Abstract-Conference.html) | 同尺寸比较模块与对齐层级；用于制度及组件比较 |

图片URL均为`https://qwdwqfwq.github.io/topconf-paper-figure-gallery/images/`下索引对应路径。

## 用户新指定的浅色分区参考

| 文件 | 来源与用途 |
|---|---|
| [user_pastel_template.png](user_pastel_template.png) | 用户本轮粘贴的原始7680×4320图像；保留为版式参考，来源论文未另行核实。借鉴顶部虚线圆角背景/人设栏、四个浅色阶段、白色子卡片、黑色方向箭头及底部粉色反馈带；不借用其中的Belief/Value Update、SVO或活动优化机制 |

新增图件见[framework/](../framework/README.md)。附件只作为视觉参考，未嵌入候选SVG。

## 用户最新双带配色参考

[user_vivid_two_band_template.png](user_vivid_two_band_template.png)为用户最新粘贴的参考图，图内为ANGraph示意；来源论文未另行核实。借鉴上下研究带、深色连线、白底与更鲜明的绿/蓝/红/紫色块，未借用其网络模型或实验内容，也未将附件嵌入框架SVG。本轮图件见[complementary/](../framework/complementary/README.md)。
