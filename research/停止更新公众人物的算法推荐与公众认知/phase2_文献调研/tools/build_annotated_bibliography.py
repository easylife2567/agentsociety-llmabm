#!/usr/bin/env python3
"""根据已获取原文的精读摘要生成注释书目与证据等级表。"""

from __future__ import annotations

import concurrent.futures
import csv
import html
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "04_全文下载计划.tsv"
MANIFEST = ROOT / "文献全文" / "下载与校验清单.tsv"
META = json.loads((ROOT / "03_元数据交叉核验.json").read_text(encoding="utf-8"))
META_BY_DOI = {item["doi"].lower(): item for item in META}
APA_CACHE = ROOT / "05_APA7_引文缓存.json"
OUTPUT = ROOT / "06_注释书目与证据等级_v0.1.md"


APA_OVERRIDES = {
    "10.1007/s11023-017-9445-2": "Öhman, C., & Floridi, L. (2017). The political economy of death in the age of information: A critical approach to the digital afterlife industry. Minds and Machines, 27(4), 639–662. https://doi.org/10.1007/s11023-017-9445-2",
    "10.1177/13678779231213990": "Clancy, L. (2024). #MournHub and @GrieveWatch: Mediating monarchy and mourning in the digital age. International Journal of Cultural Studies, 27(3), 428–443. https://doi.org/10.1177/13678779231213990",
    "10.1177/14614448221096768": "Jacobsen, B. N. (2024). When is the right time to remember? Social media memories, temporality and the kairologic. New Media & Society, 26(5), 2872–2888. https://doi.org/10.1177/14614448221096768",
    "10.1017/mem.2024.8": "Henriksen, E. E. (2024). Algorithmically generated memories: Automated remembrance through appropriated perception. Memory, Mind & Media, 3, e11. https://doi.org/10.1017/mem.2024.8",
    "10.1017/mem.2024.18": "Ben-David, A., Meyers, O., & Neiger, M. (2024). How social memory works on social media: A methodological framework. Memory, Mind & Media, 3, e20. https://doi.org/10.1017/mem.2024.18",
    "10.1177/17456916231180809": "Lewandowsky, S., Robertson, R. E., & DiResta, R. (2024). Challenges in understanding human-algorithm entanglement during online information consumption. Perspectives on Psychological Science, 19(5), 758–766. https://doi.org/10.1177/17456916231180809",
    "10.1177/17456916231185057": "Metzler, H., & Garcia, D. (2024). Social drivers and algorithmic mechanisms on digital media. Perspectives on Psychological Science, 19(5), 735–748. https://doi.org/10.1177/17456916231185057",
    "10.1073/pnas.2025334119": "Huszár, F., Ktena, S. I., O’Brien, C., Belli, L., Schlaikjer, A., & Hardt, M. (2022). Algorithmic amplification of politics on Twitter. Proceedings of the National Academy of Sciences, 119(1), e2025334119. https://doi.org/10.1073/pnas.2025334119",
    "10.1007/s13278-024-01343-5": "Cakmak, M. C., Agarwal, N., & Oni, R. (2024). The bias beneath: Analyzing drift in YouTube’s algorithmic recommendations. Social Network Analysis and Mining, 14, Article 171. https://doi.org/10.1007/s13278-024-01343-5",
    "10.1038/s41598-023-43980-4": "Bouchaud, P., Chavalarias, D., & Panahi, M. (2023). Crowdsourced audit of Twitter’s recommender systems. Scientific Reports, 13, Article 16815. https://doi.org/10.1038/s41598-023-43980-4",
    "10.1038/s41598-023-33370-1": "Gao, Y., Liu, F., & Gao, L. (2023). Echo chamber effects on short video platforms. Scientific Reports, 13, Article 6282. https://doi.org/10.1038/s41598-023-33370-1",
    "10.1080/10584609.2019.1674979": "Hameleers, M., Powell, T. E., van der Meer, T. G. L. A., & Bos, L. (2020). A picture paints a thousand lies? The effects and mechanisms of multimodal disinformation and rebuttals disseminated via social media. Political Communication, 37(2), 281–301. https://doi.org/10.1080/10584609.2019.1674979",
    "10.3389/fpsyg.2021.656365": "Qin, Y., Cho, H., Li, P., & Zhang, L. (2021). First impression formation based on valenced self-disclosure in social media profiles. Frontiers in Psychology, 12, Article 656365. https://doi.org/10.3389/fpsyg.2021.656365",
    "10.1186/s41235-021-00301-5": "Hassan, A., & Barber, S. J. (2021). The effects of repetition frequency on the illusory truth effect. Cognitive Research: Principles and Implications, 6, Article 38. https://doi.org/10.1186/s41235-021-00301-5",
    "10.1186/s41235-020-00251-4": "Nadarevic, L., Reber, R., Helmecke, A. J., & Köse, D. (2020). Perceived truth of statements and simulated social media postings: An experimental investigation of source credibility, repeated exposure, and presentation format. Cognitive Research: Principles and Implications, 5, Article 56. https://doi.org/10.1186/s41235-020-00251-4",
}


ANNOTATIONS = {
    "A01": ("supporting", "数字来生产业对死者数据有持续商业利益；作者认为，企业有动机维持、重新呈现甚至改变死者的“信息身体”，这会带来人格尊严与治理问题。", "概念性政治经济分析：建立Digital Afterlife Industry概念，结合马克思主义信息经济解释和四个现实案例。", "概念构造与案例选取有启发性，但无系统抽样、无推荐曝光数据，不能识别算法对人物印象的因果效应。", "提醒本项目把平台商业激励与死者身份治理纳入机制：停止自主表达后，平台并非中性存档者。", "VII", "B"),
    "A03": ("core", "文章表明，死者账号会成为所有权、隐私、共同创作与不同哀悼者冲突的场域；网络悲伤实践并不统一。", "对Facebook死者页面政策相关的博客、新闻及评论进行定性主题分析。", "样本为有限的公开讨论，作者明确拒绝普遍化结论；适合解释死后身份的多方协商，不支持算法因果主张。", "为“本人停止生产后，他者与平台如何接管其数字身份”提供制度与关系性起点。", "VI", "B"),
    "A06": ("core", "传统媒体假定统一的全国哀悼，但#MournHub与@GrieveWatch显示出阶级、种族、国家身份与商业化围绕死亡意义的竞争。", "以英国女王伊丽莎白二世去世后的两个社交媒体实践为批判性案例研究。", "深描述而非代表性抽样；能证明死后叙事可以多元且冲突，不能单独确证推荐机制。", "提醒本项目不能把娱乐化内容的高可见性误写为全部公众的统一哀悼。", "VI", "B"),
    "A08": ("core", "名人Jade Goody的网络致敬集中使用“天使”，将生前身份、天堂想象与死后继续关照子女的能动性连接起来；作者也指出名人与公关在死前提供了强线索。", "对该名人去世后在线致敬语料的定性内容与文化诠释。", "能直接显示少数符号如何汇聚复杂人物意义，但不测量推荐曝光或受众因果效应。", "为“死后标签凝聚”提供直接的名人案例，并表明标签可能同时来自生前线索和死后再语境化。", "VI", "B"),
    "A09": ("core", "四起名人自杀事件后，不同离散情绪表现出不同转发级联特征：厌恶传播快、广且持久，愤怒与惊讶快但短，恐惧较弱。", "对超过100万条推文与转发的完整数据集进行BERT情绪识别，用回归分析级联规模、生命期、速度与爆发性。", "大样本计算观察设计；能识别内容情绪与再分发的关联，无法把效应特定归因于推荐算法。", "为死亡后哪些情绪化片段更容易获得用户再分发提供供给侧机制。", "IV", "B"),
    "A10": ("core", "社交媒体通过纪念日逻辑、个性化、日常节律和紧张关系，在“正确时刻”重新呈现过去，从而共同生产记忆的情感强度。", "访谈与焦点小组，以“恰当时机”与算法媒体的kairologic概念进行主题分析。", "优势是把算法作用具体化为“什么时候让记忆变得重要”；自报经验不能估计排序的平均因果效应。", "直接支持将时序、再曝光间隔和记忆触发时点纳入张雪峰案例。", "VI", "A"),
    "A11": ("supporting", "算法生成记忆是平台对过去数据的存储、排名和分类；作者认为其更像对过去的局部感知，而非人类式回忆。", "基于伯格森哲学的概念分析，无实证数据。", "理论创新性高，但不能单独作为张雪峰案例的经验证据。", "为“片段为何会取代人物整体”提供“部分感知代理记忆”的观念工具。", "VII", "B"),
    "A12": ("core", "社交媒体记忆工作可以从方向性、时间性和平台方言三类“记忆标记”来测量。", "上层数据挖掘加平台特定的自下而上分析；演示数据包含530万条Facebook帖文/评论和500万条Twitter帖文/转发。", "是方法论框架而非针对推荐效应的识别；跨平台演示提升了可迁移性。", "可直接转化为案例编码：谁发起记忆、何时出现峰值、什么平台化语汇变成标签。", "VI", "A"),
    "B01": ("core", "对22,000余篇文章和500位用户的模拟显示，被测试的推荐逻辑并未必然降低多样性，基于用户历史甚至可提高推荐集内的主题多样性。", "使用荷兰大报实际内容（N=21,973）和用户（N=500）模拟多种推荐逻辑，与编辑策展比较多个多样性维度。", "设计能对“算法必然造成单一化”构成强反证；但新闻推荐模拟不等同于抖音的实际曝光反馈循环。", "要求本项目将“单一化”作为待测结果，而非推荐系统的必然后果。", "III", "A"),
    "B02": ("core", "YouTube在视频层面随时间呈现多样性，但频道层面出现稳定的“赢家”；平台提升权威来源的同时，仍会推荐误导和争议内容。", "六周追踪“新冠”“女权”“美容”的搜索与三步推荐链，结合计算分析和定性视频分析。", "反复定时采集提高了时间稳健性；关键词、地点和未登录/有限个性化场景限制外推。", "直接表明“片段多样”可与“来源集中”并存，为单一化提供多层测量。", "IV", "A"),
    "B03": ("core", "三类地缘政治叙事的四层YouTube推荐网络出现情绪、道德语气、毒性和主题漂移；各层视频的点赞、播放和评论分布高度不均，Atkinson指数随推荐深度接近1。", "每个议题手工选择40个种子视频，在未登录、清除Cookie的会话中用Selenium展开四层推荐；结合情绪/道德/毒性分类、BERTopic、网络与不平等度统计。", "可观察到推荐路径上的叙事漂移与可见性集中；但种子人工选取、只测三个议题、无随机或倒时序对照，且平台内容库与创作者供给可同时造成漂移；作者的强算法影响表述需降级为关联证据。", "对本项目最有用的是“随推荐深度的片段漂移”和“可见性不平等”两类可测指标，而不是其因果措辞。", "IV", "B"),
    "B04": ("core", "美妆博主通过共享的“算法传闻”形成可见性策略；这些想象会反过来改变上传频率和内容类型。", "数字民族志、行业利益相关者研究和10名全职美妆博主访谈。", "不能用创作者信念证明算法实际逻辑，但能有力证明内容供给会因预期排名而改变。", "是区分“算法直接放大”与“创作者预先适配算法”的关键竞争解释。", "VI", "A"),
    "B05": ("core", "Twitter算法时间线相对用户订阅选择，更强地放大同社群账号、情绪化/毒性帖文，并在政治倾向上不均衡。", "志愿者浏览器扩展采集真实时间线，结合Twitter API重建其可选帖文池，比较算法呈现与关注关系。", "真实用户数据弥补了木偶审计的行为真实性；作者明确不声称解开复杂的社会—算法反馈回路。", "提供了“曝光相对用户自选关注的放大比”这一可迁移的算法作用指标。", "IV", "A"),
    "B07": ("supporting", "人的互动改变当前推荐，也可通过社会网络结构的更长期变化反过来塑造算法环境；纯时序流也会偏向高频发布者。", "概念与证据评论，将人机纠缠置于隐性到显性需求的连续体上。", "是叙述性评论而非新实验；优势在于明确指出不存在“有算法/无算法”的简单对照。", "为后续LLMABM要求双向规则：用户行为改变曝光，曝光又改变用户与社会结构。", "VII", "B"),
    "B08": ("core", "现有证据不支持把福祉、错误信息或两极化简单归因于算法；算法更常见的作用是强化已有社会驱动力。", "对数字媒体算法、福祉、错误信息与两极化证据的简要评论。", "给出强反方框架，但非系统综述也无新的因果识别。", "使研究问题从“算法造成了什么”调整为“算法如何与供给、用户偏好和社会文化共同产生结果”。", "VII", "A"),
    "B09": ("supporting", "算法审计生态尚未标准化；受访审计者常遭遇被审计方不配合、无执法力、保密协议和难以纳入真实伤害等障碍。", "实地扫描438人和189个组织，匿名问卷N=152，并访谈10位行业领导者。", "覆盖面广但对平台推荐不是直接效果证据；调查对象为审计生态参与者。", "为抖音黑箱研究的可行性、独立性与透明度局限提供方法治理背景。", "VI", "B"),
    "B10": ("supporting", "普通用户能依凭情境化经验发现正式审计容易遗漏的伤害，且这种发现不要求用户了解算法的技术细节。", "分析Twitter图像裁剪、平台评分等多个现实世界的日常算法审计案例。", "案例法适合发现问题与变量，不足以估计算法的一般平均效应。", "支持将普通用户的“为什么又看到这个片段”经验作为审计线索，但需与系统采集交叉。", "VI", "B"),
    "B12": ("core", "语言、位置、关注、点赞和观看时长都会影响TikTok推荐；在所测因素中，关注影响最强，其次为点赞和视频观看率。", "受控木偶账号审计；每个情景约20次运行，活动账号与控制账号配对，用Jaccard重叠等指标比较信息流。", "控制性强，但木偶行为、Web端、实验时段和平台更新限制生态效度。", "直接支持机制链中“观看和互动会改变后续曝光”；也显示显性选择与隐性行为需分开建模。", "III", "A"),
    "B13": ("core", "研究建立了将单个用户信息流分解为“探索”与“利用”的可解释度量，并在真实TikTok数据、自动机器人和随机基线上验证。", "真实用户时间线+自动TikTok机器人+随机基线，并检查观看时长、点赞和关注的个性化作用。", "方法上直接针对个性化的可观测分解；所得结论依赖兴趣标签和探索/利用分类规则。", "可为LLMABM设定“探索新标签”与“重复利用已学标签”的分配参数。", "III", "A"),
    "B14": ("core", "TikTok推荐解释常包含通用理由，并可与账号实际行为不一致；例如零评论账号仍有34%视频被解释为“你评论过类似视频”。", "使用自动木偶账号采集短视频及平台解释，将解释与视频元数据和账号行为比较。", "审计对解释的准确性和完整性有直接证据，但解释文案不等于真实模型内部特征权重。", "说明用户面临的“为何推荐”说明不能直接当作机制真值。", "IV", "A"),
    "B17": ("supporting", "TikTok的网红、注意力经济与可见性劳动受其独特平台规范和功能组织，无法直接套用Instagram/YouTube模型。", "长时段数字民族志，辅以传统参与观察及对TikTok网红和经纪机构的访谈。", "对平台文化和供给侧有高生态效度，不提供推荐排名的准实验估计。", "为张雪峰死后内容生产者为何选择可复制、可识别、可变现的片段提供平台文化解释。", "VI", "A"),
    "B18": ("core", "评论网络中，抖音和B站显示显著回声室，TikTok不显著；平台与议题并非表现完全相同。", "对抖音、TikTok、B站三类平台的社会/国际/娱乐议题进行30天评论网络与选择性曝光/同质性分析。", "直接包含抖音和娱乐议题，但观察窗只有30天，且用评论网络作为回声室代理，不能把结果纯归于推荐。", "提供抖音直接背景，也要求本项目将平台、议题和用户网络差异纳入模型。", "IV", "A"),
    "B19": ("supporting", "在近200万日活账号的长期随机对照中，排名时间线在7国中的6国更放大主流右翼政党；但未支持算法更放大极端政治的通俗假设。", "Twitter平台内部大规模随机实验，对照组使用无个性化的倒时序流，并分析政治人物和美国媒体来源。", "随机分组为排名流与倒时序流的对照提供强识别；但作者明确说明网络干扰违反SUTVA、处理随时间变动，因而不能给出无偏的平均处理效应；精确驱动机制未识别，政治Twitter场景向死后名人的迁移也需谨慎。", "证明算法放大差异可在强对照下被观测，同时警告不要把“放大了谁”与“为什么放大”混为一谈。", "II", "A"),
    "B20": ("supporting", "用户会从较温和社群迁移到更极端社群；推荐路径分析显示Alt-lite可从I.D.W.视频达到，Alt-right主要通过频道推荐可达。", "分析330,925个视频、349个频道、7200万+评论和200万+视频/频道推荐。", "规模大、用户迁移和推荐路径分析丰富；观察到的时序迁移不能单独证明推荐导致激进化。", "强调“推荐可达路径”、“用户实际迁移”和“算法因果”是三个不同层次。", "IV", "A"),
    "C03": ("core", "将现有图像与伪造文本重新配对后，图文虚假信息只在难民—恐怖主义议题中比纯文本略显可信，在校园枪击议题和总体比较中均未呈现稳定差异；事实核查则稳定降低虚假信息的可信度。", "美国多样化样本N=1,404的在线实验，操纵文本/图文虚假信息与文本/多模态事实核查，议题为难民与校园枪击。", "对“去语境化的现成视觉材料”有直接操纵，但视觉效应具有议题依赖性；政治虚假信息到人物印象的外部效度仍需另行验证。", "为“图像脱离原语境后可能改变可信度”提供一项具边界条件的直接操纵，也阻止将该效应写成普遍规律。", "II", "A"),
    "C04": ("supporting", "视觉和多模态信息容易被操纵或脱离语境，并被当作较接近真实的“证据”；碎片化媒介生态会放大该风险。", "由多位学者组成的邀请论坛/评论集，整合视觉误导、深度伪造、预防与事实核查研究。", "便于概念导航，但不是按预注册方法完成的系统综述，各分节证据强度不一。", "给出将迷因、图像、视频和脱离上下文统一放入“视觉误导”框架的理据。", "VII", "B"),
    "C05": ("supporting", "迷因通过将GIF与新字幕配对，把人的身体与表情变成可重复使用的“库存图像”，并选择性重写性别、种族和阶级意义。", "基于Tumblr幽默迷因的文本—读者分析，结合女性主义文化研究与新读写研究。", "能深入解释再语境化如何变成社会分类，但为单一迷因社群的解释性研究。", "为“人物片段成为库存素材，通过新文字与标签被重新分类”提供微观话语机制。", "VI", "B"),
    "D01": ("core", "陌生人社交媒体资料中的自我披露价性会影响可信度和可喜爱度；可信度起中介作用，感知同质性调节该路径。", "微信用户N=204的在线实验，操纵未知合作者资料中主导性正面/平衡/主导性负面帖文。", "对低熟悉度人物首印象有直接实验相关性；材料是本人资料而非死后第三方片段，故需迁移验证。", "支持将低熟悉用户的可信度、喜爱度和同质性作为中介/调节结果。", "II", "A"),
    "D03": ("core", "对真实Facebook样式假新闻标题的一次先前曝光，就能提高其后续被评为准确的程度；该效应在一周后、事实核查争议标签存在时及与政治立场不一致时仍可出现，但对极端荒谬命题不出现。", "多项实验，使用实际假新闻标题，操纵新/重复曝光、即时/一周延迟、争议警示和政治一致性。", "对重复→真实性判断的因果识别强；结果是命题准确性，不是对整个公众人物的综合理解。", "为“少数片段重复出现会改变其被接受程度”提供强证据，但需避免把真理效应等同于人格标签化。", "II", "A"),
    "D04": ("core", "重复越多，陈述越被视为真，但关系是对数形：第二次遇见带来最大增量，之后边际增量递减。", "两项实验，分别将知识陈述最多重复9次和27次，一周后测量新旧陈述的真实性评分。", "给出可用于模拟的非线性频次—结果关系；实验材料为知识陈述，对娱乐化人物片段的迁移需检验。", "可将“第二次曝光影响最大、后续递减”作为ABM的候选更新函数。", "II", "A"),
    "D05": ("core", "来源可信度和重复对真实性判断呈强且叠加的影响；逐字一致的重复提高真实感，语义不一致的重复反而降低真实感，无诊断性图片未呈现稳定效应。", "四项实验，从一般陈述扩展到模拟社交媒体帖文，联合操纵来源可信度、图片、重复和重复一致性。", "直接包含模拟社交媒体刺激，且能区分原样重复与语义不一致；仍以真实性判断而非人物印象为结果。", "直接支持本项目分开“同一片段重复”和“相互冲突的片段竞争”两种曝光结构。", "II", "A"),
    "D06": ("core", "只需一次既往曝光就能提高分享意愿，且该关系由感知准确性中介；健康与一般知识两个领域都复现。", "两项实验（总N=260），让参与者在新/重复陈述中选择想在社交媒体分享的内容，并检验感知准确性的中介作用。", "对重复→准确感→分享的机制链有直接实验支持；使用意愿而非真实平台分享行为。", "把受众认知与内容供给反馈连起来：重复不只改变相信，还可能诱发更多再分发。", "II", "A"),
}


def apa_lookup(doi: str) -> tuple[str, str]:
    if doi in APA_OVERRIDES:
        return doi, APA_OVERRIDES[doi]
    request = urllib.request.Request(
        f"https://doi.org/{urllib.parse.quote(doi, safe='/')}",
        headers={"Accept": "text/x-bibliography; style=apa; locale=en-US", "User-Agent": "AgentSociety-literature-review/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            text = response.read().decode("utf-8", errors="ignore").strip()
        if text and not text.lower().startswith("<html"):
            return doi, html.unescape(html.unescape(text)).replace("&Amp;", "&")
    except Exception:
        pass
    item = META_BY_DOI[doi.lower()]["crossref"]
    authors = ", ".join(item.get("authors", []))
    return doi, f'{authors} ({item.get("year")}). {item.get("title")}. {item.get("venue")}. https://doi.org/{doi}'


def load_rows():
    with PLAN.open(encoding="utf-8", newline="") as handle:
        plan = {row["ID"]: row for row in csv.DictReader(handle, delimiter="\t")}
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        verified = [row for row in csv.DictReader(handle, delimiter="\t") if row["状态"] == "verified_downloaded"]
    return plan, sorted(verified, key=lambda row: row["ID"])


def main() -> None:
    plan, rows = load_rows()
    missing = sorted(set(row["ID"] for row in rows) - set(ANNOTATIONS))
    if missing:
        raise SystemExit(f"缺少注释: {missing}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        citations = dict(pool.map(apa_lookup, [row["DOI"] for row in rows]))
    APA_CACHE.write_text(json.dumps(citations, ensure_ascii=False, indent=2), encoding="utf-8")

    recent_count = sum(2020 <= int(plan[row["ID"]]["年份"]) <= 2025 for row in rows)
    recent_pct = round(recent_count / len(rows) * 100)

    lines = [
        "# 注释书目与证据等级（v0.1）", "",
        f"> 仅收录{len(rows)}篇已取得原文并通过题名/文件一致性校验的文献。“关键发现”均依据当前保存的原文摘要、方法、结果或结论部分；证据等级与综合评级按社会科学的学科适配规则给出。", "",
        "## 检索与筛选摘要", "",
        "- 已实际使用的发现/核验来源：OpenAlex、Crossref、Semantic Scholar、DOI落地页与开放机构仓储。",
        "- 检索日期：2026-08-17；语言：英语为主，中文概念词做了试探性检索。",
        f"- 题录唯一候选：67；通过题录存在性核验：67；获得可验证正文：{len(rows)}；进入本注释书目：{len(rows)}。",
        "- 先导检索未保存每个查询的去重前总命中数，因此不宣称达到PRISMA系统综述的穷尽性。", "",
        "### DISTRIBUTIONAL_SKEW_ADVISORY", "", "- 维度：时间分布。", f"- 集中度：2020–2025年 = {recent_count}/{len(rows)}（{recent_pct}%）。",
        "- 说明：这是覆盖分布信号，不是缺陷；社交媒体推荐为快速变化领域，近年集中具有实质理由。", "- 搜索响应：保留早期数字哀悼与重复曝光经典文献，同时将抖音/TikTok的当代审计放在核心位置。", "",
        "## 注释书目", "",
    ]
    current = ""
    group_titles = {"A": "主题A：死后数字身份与平台记忆", "B": "主题B：推荐机制、审计与曝光结构", "C": "主题C：去语境化、视觉误导与迷因", "D": "主题D：重复曝光与首印象"}
    for row in rows:
        id_ = row["ID"]
        if id_[0] != current:
            current = id_[0]
            lines.extend([f"### {group_titles[current]}", ""])
        rel, findings, method, quality, contribution, level, grade = ANNOTATIONS[id_]
        lines.extend([
            f'#### {id_}｜{plan[id_]["中文译名"]}', "",
            f'**{citations[row["DOI"]]}**', "",
            f'- **相关性**：{rel}。{contribution}',
            f'- **关键发现**：{findings}',
            f'- **方法**：{method}',
            f'- **质量与限制**：{quality}',
            f'- **证据等级**：Level {level}；学科适配综合评级 {grade}。',
            f'- **原文**：`{row["本地文件"]}`', "",
        ])
    lines.extend([
        "## 证据结构的阶段性说明", "",
        "- 强因果证据主要存在于政治Twitter的平台随机实验、多模态去语境化实验和重复曝光/首印象实验；它们都不是张雪峰死后的抖音实验。",
        "- 对抖音/TikTok的直接证据以木偶审计、真实时间线度量、解释审计、评论网络和数字民族志为主，能支持机制候选，但不能单凭一项研究识别完整因果链。",
        "- “算法只是放大已有社会选择”获得重要理论支持；供给侧可见性劳动、用户关注/点赞/观看与社群结构均是必须对照的替代解释。", "",
        "## 检索限制", "",
        "- 本轮正式注释书目被“可合法取得正文”筛选，可能对开放获取文献产生偏向。",
        "- 中文学术数据库尚未通过用户机构授权路径完成系统检索，中国大陆的本土传播学证据不足。",
        "- 对张雪峰、“雪毙”和“你跑不过我你信吗”的平台内曝光规模、原始视频语境与用户实际印象尚未进入本轮学术文献证据；需在后续案例数据研究中独立核验。", "",
        "## Material Passport", "", "- Origin Skill: academic-research-suite / deep-research / bibliography_agent + source_verification_agent",
        "- Origin Mode: lit-review", "- Origin Date: 2026-08-17", f"- Verification Status: {len(rows)}_ORIGINALS_ACQUIRED_AND_READ_FOR_ANNOTATION",
        "- Version Label: annotated_bibliography_v0.1", "- Upstream Dependencies: candidate_corpus_v0.2, source_verification_v0.2, download_manifest_v0.1",
        "- Repro Lock: null", "- Experiment Intake Declaration: no_experiments_declared", "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"写入 {OUTPUT}，条目 {len(rows)}")


if __name__ == "__main__":
    main()
