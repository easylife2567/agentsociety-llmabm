# 跨双栏的四种英文框架图

本级是本次“3—5种构图、色盲友好、精简文字、长而矮”要求的四个候选版本。统一为180 × 63.75 mm，宽高比约2.82:1；SVG viewBox为2400×850，PNG为2400×850。图件均为原生文字与矢量，不含嵌入位图；旧版本保留。

| 候选 | 构图与用途 | 可编辑图 | 预览 | 生成脚本 |
|---|---|---|---|---|
| A | 紧凑横向流水线；主步骤与两条反馈易于顺读，适合论文主框架 | [a_compact.svg](a_compact.svg) | [a_compact.png](a_compact.png) | [draw_a_compact.py](draw_a_compact.py) |
| B | 横向椭圆回路；突出内容回流和接触历史两条反馈 | [b_radial.svg](b_radial.svg) | [b_radial.png](b_radial.png) | [draw_b_radial.py](draw_b_radial.py) |
| C | 平台／智能体／生成三条泳道；突出本次行动和后续展示／历史的时间关系 | [c_swimlane.svg](c_swimlane.svg) | [c_swimlane.png](c_swimlane.png) | [draw_c_swimlane.py](draw_c_swimlane.py) |
| D | 黑白主题区与双层机制图；主题较鲜明，正文流程较紧凑 | [d_nested.svg](d_nested.svg) | [d_nested.png](d_nested.png) | [draw_d_nested.py](draw_d_nested.py) |
| 共用 | 色彩、矢量图标、公式与基础绘图函数 | [diagram_lib.py](diagram_lib.py) | — | — |
| 比较 | 四图拼版，仅用于选构图；查看细字请打开单图 | — | [comparison.png](comparison.png) | — |
| 灰度 | 检查不依赖颜色的文字、形状与虚实线 | — | [comparison_grayscale.png](comparison_grayscale.png) | — |
| 打包 | 四套SVG/PNG、拼版、源脚本及本说明 | [four_layouts_180mm.zip](four_layouts_180mm.zip) | — | — |

## 设计与配色

- 继续以用户指定的ProAgent英文第二版为事实起点，重新组织构图，不为美化增加心理状态更新或行动优化机制。
- 蓝色`#0072B2`用于内容、策展与曝光，橙色`#D55E00`用于表达与生成；橙色文字使用深色`#9C4300`保证对比，黑白/中灰用于固定条件、研究背景及对照信息。暖冷色仅标记职责，不以颜色代替标签。
- 主流程与内容回流为实线；接触历史为灰色虚线，同时直接写明后续行动。候选池、判定、生成和历史具有文字/形状/位置差别，灰度下仍能追踪。
- 配色与多重编码参考[Okabe与Ito的Color Universal Design](https://jfly.uni-koeln.de/color/index.html)：颜色之外同时使用线型、形状与直接标记。没有将“色盲友好”当作只换一套配色。
- 蜡烛与白花只作digital mourning主题插画；普通发布帖不统一标作悼念。图标不是观测样本、类型比例或新变量。
- “75%信息密度”作为内容组织区约占画布四分之三的设计目标，不等同于可精确量出的墨迹像素比例。已缩短重复说明、压缩各层间隔，保留路由和必要分组留白，不以无效装饰凑密度。
- 图内文字由原ProAgent第二版按空格统计的274词，缩减至约160—175词；完整解释进入图注。主标签约7—9 pt（按180 mm宽），脚注约6 pt，数学下标另按比例设置。不同期刊如要求更大字号，可在选定构图后继续精简或调整。

## 事实核对与实际检查

直接对照当前原Word及冻结副本，确认内容指纹一致；核对Word数学对象U_it = B_i + R_it(D_it − B_i)。四图均保留：

1. 两平台49,930条现实语料与另行冻结的仿真输入分开。正文方法节与局限节的仿真来源范围尚未统一，本轮不为仿真写平台数量，不将49,930条全量直接画作仿真输入。
2. 100名智能体、五类固定作者、W12—W22、每人每周一次机会。固定阈值及类型不由反馈更新。
3. 每次feed最多10条；当前接触进入D， prior same-type exposure进入R。R是回归B的权重，不把衰减画成效用必然下降。
4. 先判定达到个体门槛，再由大模型按人设与最多5条feed摘录生成，每条不超过120字符；未达则本次不发帖。
5. 成功发布帖回候选池：时序为批次结束后、后续批次可见；随机/兴趣为次周取得展示资格。图内短写after batch/next week，以上准确时机在图注补全。
6. 接触历史独立于是否发帖，记录后用于后续行动R；不把生成成功作为累积接触的前提。
7. 3制度×3种子九次主运行；兴趣内B=0、D=1、R=1各三次配对，复用完整模型参照；分批及生成服务配置差异保留。

已完成SVG XML、唯一ID、无嵌入位图、180×63.75mm尺寸及原Word公式一致性检查；四个PNG均实际查看，修正了若干箭头与文字遮挡。对A/D及B/C分别进行了定向只读核对，无未解决的实质事实冲突。已查看灰度拼版；这属于可辨识性检查，不是对所有色觉类型的临床模拟。文字与常用底色的相对亮度对比：正文黑白16.29:1、深橙文字/淡橙5.86:1、蓝文字/淡蓝4.57:1、灰文字/浅灰7.28:1。

本轮仅在本run新增候选及所属索引，不改正式论文、实验或原始数据，不运行LLM仿真，未commit或push。最终投稿版的字号/宽度需按确定的期刊版式确认。

## 共用英文图注候选

**Curation–expression feedback in digital mourning.** Empirical analysis describes temporal and platform patterns, while separately frozen samples provide time-stamped simulation inputs. A fixed population receives regime-specific personal feeds. Baseline expression utility (B), the current opinion-climate response (D), and a weight based on prior same-type exposure (R) determine whether utility reaches the individual threshold. Only then does the LLM generate a post from the persona and at most five feed excerpts of up to 120 characters each. Successfully published posts become eligible for later display after batch completion in the chronological regime and in the next week under random and interest-based regimes. Exposure history is stored independently of posting and used in subsequent actions. Component ablations reuse the interest-based full model as their reference; generation-service configurations differed between full-model and ablation batches. Candle and flower icons indicate context only.

## 复现

从项目根目录读取.env中的PYTHON_PATH，分别运行本级四个draw_*.py脚本即可生成SVG；脚本仅用Python标准库，不调用项目模型或网络。PNG用本机已捆绑的sharp渲染。修改diagram_lib.py会影响四图，选定版式后的变更应按项目补丁规范保存，避免覆盖其他候选。
