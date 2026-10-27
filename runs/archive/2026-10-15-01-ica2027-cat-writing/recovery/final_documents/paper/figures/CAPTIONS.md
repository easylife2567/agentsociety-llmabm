# 图题与图注

中文图题沿用定稿，面板说明对应本次实际输出。英文为图件配套图注，尚未替换写作run的已确认正文。

## 图1

**抖音与小红书合并样本中悼念与玩梗表达的周度演化**

a呈现两平台合并样本的五类内容周内比例；b呈现悼念与玩梗帖文的周度数量。虚线标记事件发生周W13。周范围为W05—W22。合并比例先汇总两平台各类别计数，再计算其占当周五类内容总数的比例。数据为真实帖文的模型辅助编码结果。

**Figure 1. Weekly evolution of mourning and memetic expression in the pooled Douyin and Xiaohongshu corpus.**

a, Within-week shares of five content categories. b, Weekly numbers of mourning and memetic posts. Dashed lines mark the event week, W13. The observed window covers W05–W22 of 2026. Pooled shares are calculated after summing category counts across the two platforms. Categories are based on LLM-assisted coding of observed posts.

## 图2

**抖音与小红书内容构成的周度演化比较**

a为抖音，b为小红书，均呈现五类内容的周内比例，采用相同的时间轴、比例轴及类别配色。虚线标记W13。比例依据各平台当周五类内容合计计算，周范围与图1一致。

**Figure 2. Weekly content composition on Douyin and Xiaohongshu.**

a, Douyin. b, Xiaohongshu. Each panel shows within-week shares of the same five content categories, with identical time axes, percentage scales and category colours. Dashed lines mark W13. Shares are calculated within each platform and week over the same observed window as Figure 1.

## 图3

**三种策展制度下固定作者类型供给的时间轨迹与晚期构成**

a—c分别呈现随机、时序和兴趣制度下五种作者类型的周度发帖数量，采用相同坐标尺度与类别配色；浅色细线为每个seed，粗线为三个seed的算术均值，虚线标记W13。d呈现W19—W22玩梗型供给份额的三次重复取值及均值，点形依次对应seed 0、1、2，黑色短横线表示均值。仅统计智能体成功发布的帖文，不含外部输入与历史初始内容；类别依据固定作者类型确定。晚期份额先在每次运行内计算，再跨三次重复取均值。

**Figure 3. Supply trajectories and late-period composition by fixed author type under three curation regimes.**

a–c, Weekly posts under random, chronological and interest curation, respectively. Thin translucent lines show individual seeds; thick lines show arithmetic means across three seeds. Axes and author-type colours are shared across panels. Dashed lines mark W13. d, Shares of posts contributed by memetic-type authors during W19–W22. Circles, triangles and squares represent seeds 0, 1 and 2, respectively; black horizontal bars show means. Counts include successfully published agent posts. Categories identify fixed author types. Late-period shares are computed within each run before averaging.

## 图4

**不同策展制度下的个人接触、表达参与与生成帖再流通**

a呈现W19—W22玩梗型作者信息流中的同类内容比例；b呈现该群体成功发帖数占表达机会的比例；c呈现来自玩梗型作者的生成帖占其他作者群体全部信息流展示条目的份额。生成帖按固定作者群体追踪，外部帖按来源数据的内容类别计入接触构成。每个seed中，a的分母为玩梗型群体实际获得的760条信息流展示，b为该群体76次表达机会，c为其他作者群体实际获得的3,240条信息流展示。圆、三角、方形分别对应seed 0、1、2，黑色短竖线表示三个seed指标的均值。

**Figure 4. Individual exposure, posting participation and recirculation of generated posts across curation regimes.**

a, Same-type content as a share of feed items displayed to memetic-type authors during W19–W22. b, Successful posts as a share of their expression opportunities. c, Generated posts from memetic-type authors as a share of all feed items displayed to other author groups. Generated posts are tracked by fixed author type; external posts retain their source content categories. Per seed, denominators are 760 feed displays in a, 76 expression opportunities in b and 3,240 feed displays in c. Circles, triangles and squares denote seeds 0, 1 and 2; black vertical bars show arithmetic means across three seeds.

## 图5

**表达组件干预下的参与变化与供给、可见位置重组**

a比较完整模型与B=0条件下W19—W22的平均每周总供给；b比较完整模型与D=1条件下同期玩梗型作者的成功发帖率；c比较完整模型与R=1条件下W14—W18全体作者的成功发帖率；d、e比较完整模型与R=1条件下W19—W22玩梗型作者供给份额及跨群体玩梗内容展示份额。供给份额以全部智能体成功发布的帖文为分母；e以非玩梗型作者实际获得的全部信息流条目为分母，计入外部帖与生成帖。所有比较均在兴趣制度内进行，点形区分三个seed，连线连接同seed的完整模型与干预条件，黑色短横线表示均值。各项指标先在每run内计算，再对三个配对seed汇总。

**Figure 5. Paired component ablations and changes in participation, supply composition and visibility.**

a, Mean weekly output during W19–W22: full model versus B = 0. b, Memetic-type authors' posting rate during W19–W22: full model versus D = 1. c, Overall posting rate during W14–W18: full model versus R = 1. d,e, Late-period memetic-type supply share and cross-group exposure to memetic content, respectively: full model versus R = 1. Supply shares use all successfully published agent posts as the denominator. Cross-group exposure uses all feed items displayed to non-memetic-type authors and includes external and generated posts. All comparisons use the interest regime. Marker shapes identify three seeds; lines connect the same seed across conditions; black horizontal bars show means. Metrics are calculated within each run and then averaged across the three paired seeds.

## 核对锚点

| 项目 | 复算均值或比例 |
|---|---|
| 图1 W22合并玩梗 | 63.5% |
| 图2 W22抖音／小红书玩梗 | 82.4%／19.3% |
| 图3 晚期玩梗型供给份额，随机／时序／兴趣 | 10.3%／73.3%／65.6% |
| 图4 同类接触，随机／时序／兴趣 | 3.2%／42.0%／25.2% |
| 图4 玩梗型发帖率，随机／时序／兴趣 | 3.9%／56.6%／47.8% |
| 图4 生成帖跨群体展示，随机／时序／兴趣 | 0.1%／22.7%／6.8% |
| 图5a B干预，帖／周 | 13.8 → 6.8 |
| 图5b D干预，晚期玩梗型发帖率 | 47.8% → 17.1% |
| 图5c R干预，事件后总体发帖率 | 19.1% → 49.2% |
| 图5d R干预，晚期玩梗型供给份额 | 65.6% → 12.6% |
| 图5e R干预，晚期跨群体玩梗内容展示份额 | 20.2% → 7.8% |
