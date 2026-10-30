# 论文图件重制与项目框架图

用户于2026-10-19明确授权新建本run，专门重制论文全部图件，并新增整个项目的框架图。

## 目标与边界

- 重制初稿全部图件，新增展示整个研究项目的框架图；统一视觉语言，保留准确的科学含义及数据口径。
- 用户指定风格参考：[Top-Conf Figure Gallery · 框架总览](https://qwdwqfwq.github.io/topconf-paper-figure-gallery/?p=framework)。已通过浏览器查看画廊首屏；已选定三张具体参考图并记录于references入口。可借鉴模块分区、浅色配色、箭头组织及多面板布局，不能将画廊中的不同图视为单一模板。
- 候选图、可编辑源文件、作图数据引用和检查材料保存在本run；正式paper图件及Word保持原状，待用户明确采用时选择性落地。
- 不启动新实验、不改原始数据或研究流水线，不commit、push或归档。
- 当前新增本run独立绘图脚本，无现有项目代码修改，不需要worktree。若后续修改或运行现有项目代码，按项目规范先建立本run隔离workspace。

## 当前阶段与下一步

状态：2026-10-30已在[figures_unified_v1/](figures_unified_v1/README.md)更新图1：180×66mm，以“选择性表达”主卡突出U_it=B_i+R_it(D_it−B_i)、U_it≥activity_i→LLM generation，简释U/B/D/R与固定门槛。保留环形主线、三七开、固定类型、小时回流、悼念图标与现色卡；无防御性或次要参数文字。主公式/条件12pt、数学下标8.4pt、文字最低8pt，代码事实及最后对齐/字体/遮挡/实际预览通过。SVG/PDF/PNG、图1中文图注和六页合集同步；图2—6与数据保持原字节。完整补丁和核验见qa/framework_utility。Word未改，未提交或归档。

此前同日阶段：用户按V7图号仅更新图4供给轨迹的交付保留于[figures_hourly_return_v1/](figures_hourly_return_v1/README.md)，新版全套图件从figures_unified_v1进入。

2026-10-26阶段：用户要求补制已跑完的图5；已从40个完整运行单元（10个复用Full、30个干预）复算十种子配对结果，完成英文五面板SVG/PDF/PNG、中文图注与五图合集，数据及独立图件审查通过。当前图1—5均为十种子版本，详见[figures_seed10/](figures_seed10/README.md)。此前另存的修订Word保持其原交付字节，未自动插入新图5。

2026-10-24阶段：用户提供ICA2027-V5.docx，明确采用每制度十组主实验并暂撤原图5。已在[figures_seed10/](figures_seed10/README.md)完成图1—4及中文图注、修改意见。用户随后明确授权更新Word：现已在[word_seed10/](word_seed10/README.md)另存真实修订副本，更新30次主运行、插入四张SVG和图注、追踪删除旧图5及相关内容，保留原有格式与原稿。此前框架图各版及原图件均保留；原Word和正式paper未覆盖。

十组修订Word的来源正文为用户2026-10-24提供的ICA2027-V5.docx，冻结副本、SHA256和检索文本见[inputs/](inputs/README.md)。此前ICA2027v1.docx仍保留为框架旧版本依据，初始指纹见[input.sha256](input.sha256)。原件均只读；用户另行授权的十组修订Word保存在word_seed10，不覆盖来源。当前全套图件按用户最新约定以框架图为图1，其余顺延；本轮不修改Word。文档与批注仅作为研究材料，不当作操作授权。
原图件入口：[paper/figures/README.md](../../paper/figures/README.md)。V5现存图1—5分别涉及现实总体轨迹、平台差异、仿真轨迹、反馈与接触、B/D/R消融。本轮已逐图核对面板、数据分母和正文数值；当前图1—5交付及实际验收见figures_seed10，旧paper图件保持原状。

此前图5工作：图5十种子图件与正文修改建议已就绪；用户随后指出森林绿首版结构变化不足，现已新增[两种结构候选](figures_seed10/style_rework/README.md)：五列种子配对图谱与五行配对差值表，待作者判断后再决定是否统一全篇；[首轮配色版](figures_seed10/style_trial_forest/README.md)保留对照。另存Word仍是此前图1—4的修订副本，保留原有接受/拒绝状态及旧图5删除修订；本次仅制作图5和同步图件材料。此前框架图独立保留。

### 当前图号与旧制图run映射

当前图1为最新小时方案的精简环形框架；图2—6为统一出版版。旧图件目录不重命名。

| 当前图号 | 旧图号 | 当前内容 |
|---|---|---|
| 图1 | 新增框架 | 两项互补研究与三阶段环形机制，统一小时回流 |
| 图2 | 图1 | 两平台五类周数量堆积及悼念/玩梗数量 |
| 图3 | 图2 | Douyin与Rednote五类内容周比例堆积 |
| 图4 | 图3 | 统一小时回流三制度固定作者供给轨迹(a—c)，30run |
| 图5 | 图4 | 统一小时回流同类接触、表达参与与生成帖跨群体再展示，30run |
| 图6 | 图5 | 原组件消融批次B/D/R各10配对，R → 1 |

框架图应体现现实描述与仿真机制检验的分工；固定作者类型下的供给变化不能画成人群普遍改变态度。当前图5的生成帖再展示与图6包含外部帖的全部玩梗内容展示保留不同口径；实际分子、分母与来源核对见figures_unified_v1。

## 基线与资产

- 初始化commit：`69d243955d341444ae769fae5bf23dc160465cd6`。
- 初始工作区有大量既有已修改、删除及未跟踪资产，见[初始状态](initial_git_status.txt)，均不属于本run成果，不覆盖或清理。
- 本run使用独立绘图脚本与图件，未修改项目引擎或运行新实验。图3紧凑排版对已有run脚本的最终补丁与起始副本见[figures_seed10/qa/fig3_compact_footer/](figures_seed10/qa/fig3_compact_footer/README.md)；当前图件与实际核验见对应目录。

| 本级资产 | 用途 |
|---|---|
| [README.md](README.md) | 唯一实时状态、边界及交接入口 |
| [figures_unified_v1/](figures_unified_v1/README.md) | 当前nature技能统一出版图1—6：精简环形框架、数量/比例面积图、小时主实验三制度供给轨迹、过程图和原批消融；矢量图件、图注、数据、脚本及恢复验证 |
| [figures_hourly_return_v1/](figures_hourly_return_v1/README.md) | 当前V7图4：统一小时回流主实验四面板、原生SVG/PDF/PNG、中文图注及30run来源核验 |
| [figures_seed10/](figures_seed10/README.md) | 旧回流V5图1—5十组版本、英文SVG/PDF/PNG、中文图注、修改意见、冻结数据、独立脚本和验收；旧三种子图5另存历史资料 |
| [word_seed10/](word_seed10/README.md) | 用户授权另存的十组修订Word：真实增删修订、四张SVG与中文图注、原格式保留和结构/视觉核验 |
| [framework/](framework/README.md) | 中文初版、ProAgent英文版本、新附件风格候选、悼念元素版、四种此前长横版、三种互补研究长横版、三种差异化视觉语言、当前ProAgent×圆环融合版与draw.io可编辑文件、PNG与生成脚本 |
| [references/](references/README.md) | 三张画廊参考、用户指定浅色模板及鲜明双带配色附件、来源与借鉴说明 |
| [inputs/](inputs/README.md) | 当前正文冻结副本 |
| [input.sha256](input.sha256) | 原件初始内容指纹 |
| [manuscript.extracted.txt](manuscript.extracted.txt) | 仅供检索的正文提取文本 |
| [.gitignore](.gitignore) | 忽略隔离workspace与可丢弃tmp |
| [initial_git_status.txt](initial_git_status.txt) | 创建时已有Git改动记录 |
