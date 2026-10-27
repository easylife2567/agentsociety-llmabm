# 融合框架图第二版：清晰走线与增强局部配色

2026-10-23按用户对第一版遮挡和颜色偏弱的反馈制作。保留环形设计、英文跨双栏长横版、约三七开的互补研究、白底与悼念情境图标；原版完整保留。本轮中文研究思路单独回复，不加入图内。

| 文件 | 用途 |
|---|---|
| [framework_fusion_en_v2.svg](framework_fusion_en_v2.svg) | 原生可编辑矢量主图，2800×1100；物理尺寸180×70.71mm |
| [framework_fusion_en_v2.png](framework_fusion_en_v2.png) | 彩色预览，395dpi元数据 |
| [framework_fusion_en_v2_grayscale.png](framework_fusion_en_v2_grayscale.png) | 灰度校样 |
| [framework_fusion_en_v2.drawio](framework_fusion_en_v2.drawio) | 本地draw.io可编辑版，217个独立对象 |
| [framework_fusion_drawio_v2_preview.png](framework_fusion_drawio_v2_preview.png) | 本机draw.io实际导出预览，2800×1101；页边界舍入多1像素 |
| [draw_fusion_v2.py](draw_fusion_v2.py) | 独立SVG生成脚本，无第三方Python依赖 |
| [render_v2.mjs](render_v2.mjs) | 用本机Codex捆绑sharp导出彩色和灰度PNG |
| [convert_v2_to_drawio.py](convert_v2_to_drawio.py) | 将SVG对象重建为原生draw.io对象，不嵌入整图图片 |
| [conversion_manifest.json](conversion_manifest.json) | 源图指纹、60处文字及对象清单 |
| [framework_fusion_v2_roundtrip.xml](framework_fusion_v2_roundtrip.xml) | 本机draw.io实际打开解析并导出的未压缩XML |
| [validation.json](validation.json) | XML、文字对应、页内边界、预览尺寸和输入指纹检查 |

## 本次修改

- 中央效用卡片完整放入圆环内；内外圆弧同时留出开口。D、供后续行动使用的R和效用输出分别穿过留出的通道，避免用卡片遮住圆弧。
- 圆弧箭头头部改为固定尺寸，避免线宽加粗时同步变成大三角。内容回流沿左侧和底部外通道返回候选池，与独立的接触历史虚线分开。
- “No”“later R”和回流说明避开连线；回流资格直接放在独立模块。draw.io文字基线和底部留量同步调整，实际导出为单张长横图。
- 蓝色`#0072B2`用于内容分析与可见性配置，朱橙`#D55E00`用于表达阶段圆弧与编号，深橙`#AA4600`用于表达模块标题，深蓝灰`#283D4F`用于内容回流。局部浅蓝`#D8EAF6`、浅橙`#FFE5C7`提示相关模块，保留白色背景；不恢复整块彩色分区。编号、文字和实虚线继续提供颜色以外的辨识。
- 使用蓝/朱橙语义配色的既有依据见[前轮圆环说明](../../divergent/README.md)。本版是现有融合图的本地矢量修订，不新增画廊参考或外部图像。

## 科学内容与检查范围

经验内容区与仿真内容区宽约840:1740，约33:67；经验模式提供机制问题与标定参照，两部分共同解释公共表征重组。只显示49,930总样本与来源名称，不展示两个平台各自数量、比例或条形。

保留100名固定作者类型智能体、W12—W22、固定个体阈值、精确效用公式`U_it = B_i + R_it(D_it − B_i)`、决策feed最多10条，以及LLM生成所用最多5条摘录/每条最多120字符。当前接触独立更新后续行动所用的历史；只有成功发布内容回流。时序为批次完成后入池、后续批次可见；随机/兴趣为次周取得资格。模拟冻结输入独立于全量经验语料，同一seed内制度共用外部样本，不表示共用候选池。

主比较仍为3制度×3seed，兴趣制度内B=0、D=1、R=1组件干预。各3次配对、复用完整模型以及分批/生成服务配置不同的限定继续使用[上一级完整英文图注](../README.md#英文图注)，没有从短标签推导严格同期控制。圆弧长度、图标数量、模块面积均为版式示意，不编码数据比例。蜡烛、白菊和缎带只说明悼念语境。

已实际查看SVG彩色与灰度渲染、本机draw.io导出预览，并完成定向走线和内容复核；未见原有卡片压圆弧、箭头穿标签的问题。SVG和draw.io均无嵌入位图；60处文字逐项对应，draw.io包含16条原生连线、21个原生矢量路径、96个椭圆、23个矩形、1个菱形及60个文字对象。细弧和花束为原生矢量对象，可选择、移动与改色；部分曲线使用draw.io自定义形状，修改路径可用“编辑形状”。字体保留可编辑性，跨机器若缺Arial/Times New Roman可能替代。

当前原Word与run冻结副本SHA256一致。检查针对正文描述和图件结构，不代表重跑实验或重新核实原始数值结果。候选仅保存在当前run，未修改正式论文、实验、数据或流水线；未commit、push或归档。

## 本地使用与复现

在draw.io桌面版选择“文件→打开”并选择本目录`.drawio`文件即可继续编辑。导出PNG建议选择当前页面；本机实测页面导出为2800×1101。

依次以项目`.env`配置的`PYTHON_PATH`运行`draw_fusion_v2.py`和`convert_v2_to_drawio.py`，再以本机Codex捆绑Node运行`render_v2.mjs`。绘图脚本均为本轮新增文件，未修改既有代码。渲染依赖的绝对路径换机需适配。

本机draw.io验证命令（将文件名替换为绝对路径）：

```text
/Applications/draw.io.app/Contents/MacOS/draw.io --export --format png --output framework_fusion_drawio_v2_preview.png --width 2800 --size page --theme light --timeout 45 --disable-update framework_fusion_en_v2.drawio
/Applications/draw.io.app/Contents/MacOS/draw.io --export --format xml --uncompressed --output framework_fusion_v2_roundtrip.xml --timeout 45 --disable-update framework_fusion_en_v2.drawio
```
