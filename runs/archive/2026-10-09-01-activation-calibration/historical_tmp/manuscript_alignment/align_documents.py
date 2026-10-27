from pathlib import Path
import re
import json
import hashlib
import shutil
import difflib
import subprocess

root = Path('/Users/easylife/Project/AgentSociety')
run = root / 'runs/2026-10-09-01-activation-calibration'
out = run / 'manuscript_alignment'
assert not out.exists(), '不得覆盖已有对齐证据'
out.mkdir()
paths = ['README.md', 'TOPIC.md', 'hypothesis_4/README.md', 'hypothesis_4/HYPOTHESIS.md',
         'hypothesis_4/experiment_2/README.md', 'hypothesis_4/experiment_2/EXPERIMENT.md',
         '锚定式事件表达激活模型.md', 'data/README.md', 'paper/README.md',
         'paper/manuscript/INTAKE_AUDIT.md', 'paper/manuscript/manuscript.accepted.md',
         'runs/README.md', 'runs/2026-10-09-01-activation-calibration/README.md']
before = {p: (root/p).read_text() for p in paths}
for p in paths:
    dst = out/'before'/p
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root/p, dst)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
sources = ['悼念退潮之后：基于多智能体仿真的逝者数字形象塑造机制研究.pdf',
           '【1009批注版】ICA-研究背景和文献综述.docx', '【修订1】1008 理论框架.docx']
source_hashes = {p: sha(root/p) for p in sources}
git_start = subprocess.check_output(['git','status','--short'], cwd=root, text=True)
(out/'git_start.txt').write_text(git_start)
rq1 = '逝者数字形象呈现何种时序结构与演化特征，这一过程在不同平台之间呈现出何种共性与差异？'
rq2 = '不同算法推荐机制与用户发帖行为形成的循环交互过程，如何共同塑造逝者数字形象的演化轨迹与玩梗话语扩散格局？'
rq3 = '不同算法推荐机制是否会差异化推动网络氛围由庄重悼念向迷因化、戏谑化玩梗方向转变？'
def put(p, s):
    (root/p).write_text(s)
def replace(p, old, new):
    s = (root/p).read_text()
    assert s.count(old) == 1, (p, old[:80], s.count(old))
    put(p, s.replace(old, new, 1))
def after_title(p, text):
    s = (root/p).read_text()
    pos = s.index('\n\n')+2
    put(p, s[:pos]+text+'\n\n'+s[pos:])

after_title('TOPIC.md', f'''## 研究问题与证据分工（2026-10-12作者修订）

本次以作者最新的[研究背景与文献综述](<【1009批注版】ICA-研究背景和文献综述.docx>)及[理论框架](<【修订1】1008 理论框架.docx>)更新研究思路；[PDF初稿](悼念退潮之后：基于多智能体仿真的逝者数字形象塑造机制研究.pdf)用于核对原章节与历史结果。新稿覆盖对应部分，不覆盖既有编码可靠性修订或实验证据身份。

| 研究问题 | 主要证据与任务 |
|---|---|
| （1）{rq1} | 原始数据挖掘与分析：识别内容构成、时序演化及平台之间的共性与差异；报告分类口径与测量不确定性 |
| （2）{rq2} | LLM ABM：观察可见性配置、选择性表达与内容回流的循环，检验这一微观过程能否生成所关注的宏观轨迹 |
| （3）{rq3} | LLM ABM：比较随机、时序与兴趣三种完整策展制度下悼念与玩梗表征的相对变化及seed差异 |

问题（1）的现实平台差异用于识别现象与提供建模参照，不能仅凭这种差异归因于算法。问题（2）（3）的制度比较是在冻结模型条件下进行的机制重演，不将模拟的三种制度分别等同于抖音、微博或小红书，也不据此主张已验证精准遏制恶意玩梗的治理效果。

总体框架采用Trilling（2024）的传播反馈回路视角，并以Thorson与Wells（2016）的策展流框架解释每轮个人信息暴露如何形成。数字哀悼研究提供记忆与表征问题，迷因研究解释参与和意义改写，平台研究解释可见性与用户反馈；本研究通过循环机制连接这三条脉络。D（意见气候响应）、B（常态表达基线）、R（事件注意力权重）用于操作化其中的选择性表达，命名、函数和参数为本文建模设定，不能写成文献直接提供的一套变量。

文献与作者正文见[论文接入审计](paper/manuscript/INTAKE_AUDIT.md)和[对齐后的论文Markdown](paper/manuscript/manuscript.accepted.md)。下列实验事实、运行状态与冻结参数继续按原证据理解。''')
replace('TOPIC.md', '个人所见经意见气候D和注意力余量R进入U', '个人所见经意见气候响应D和事件注意力权重R进入U')
replace('TOPIC.md', '全局 `alpha_D` 与五类疲劳系数 λ 只用 W13–W18 标定，W19–W22用于后段模式检查，不据此主张事前预测能力。', '全局 `alpha_D` 与五类衰减系数 λ 的最后一轮参数搜索目标使用 W13–W18；W19–W22用于后段模式检查，但早期设计与选择已参考后期形态，不能称为从未参与建模的独立验证集，也不据此主张事前预测能力。')
replace('TOPIC.md', '**主假设**：推荐算法选择性放大已有的玩梗群体（其曝光份额超过供给占比），驱动公共表征沿"专业→悼念→迷因"转移', '**当前检验任务（问题2、3）**：可见性、表达与回流如何共同塑造轨迹，以及完整策展制度是否差异化推动悼念向玩梗转变；原定向放大假设保留历史身份，曝光是否超过供给由结果判断')
replace('TOPIC.md', '仿真复现"哀悼→玩梗"表征转移形态（拟合真实曲线）', '检查仿真能否生成现实分析所识别的时序形态（问题1提供参照，仿真不代替现实分析）')

replace('README.md', '本仓库使用 AgentSociety 研究算法策展如何通过', '本仓库先以原始数据挖掘与分析回答逝者数字形象的时序结构及平台差异，再使用 AgentSociety 的LLM多智能体仿真，主要回答算法与发帖行为的循环机制及不同策展制度是否差异化推动悼念向玩梗转变。总体上研究算法策展如何通过')
replace('README.md', '| [图表解读.docx](图表解读.docx) |', '''| [悼念退潮之后：基于多智能体仿真的逝者数字形象塑造机制研究.pdf](悼念退潮之后：基于多智能体仿真的逝者数字形象塑造机制研究.pdf) | 作者PDF初稿，供章节结构与历史结果核对 |
| [【1009批注版】ICA-研究背景和文献综述.docx](<【1009批注版】ICA-研究背景和文献综述.docx>) | 当前研究背景、三条文献脉络与三个研究问题的作者来源 |
| [【修订1】1008 理论框架.docx](<【修订1】1008 理论框架.docx>) | 当前传播反馈回路视角与策展流框架的作者来源 |
| [图表解读.docx](图表解读.docx) |''')

after_title('hypothesis_4/README.md', '主研究承接[TOPIC.md](../TOPIC.md)中的问题（2）（3）：解释算法与发帖行为的循环如何塑造表征，并比较完整策展制度是否差异化推动悼念向玩梗转变。问题（1）主要由原始数据挖掘与分析回答，提供时序和平台差异参照；本目录的仿真不代替该项现实分析。总体理论为传播反馈回路视角与策展流框架，U模型负责选择性表达的操作化。')
replace('hypothesis_4/README.md', '根级runs探索已交接结束。', '此前到达时机探索已交接结束；当前U标定与文稿讨论run仍保持活跃，实验运行状态以experiment_2 README为准。')
replace('hypothesis_4/HYPOTHESIS.md', '### 已采用的行为与时间规则', '''### 当前研究问题与理论层次（2026-10-12）

按作者最新文稿，问题（1）的时序结构及平台共性/差异由原始数据分析回答，本假设与三臂仿真主要承担问题（2）的循环机制解释和问题（3）的制度差异检验。完整问题原句及证据分工见[TOPIC.md](../TOPIC.md)。

Trilling（2024）的反馈回路视角解释传播结果如何成为下一轮条件，Thorson与Wells（2016）的策展流框架解释每轮可见性如何形成。D为意见气候响应，B为常态表达基线，R为事件注意力权重；它们是选择性表达的模型操作化，具体公式与取值不是文献直接提出的变量体系。三臂比较不预设兴趣推荐必然导致更强玩梗，也不把玩梗类别直接等同于恶意表达或负面评价。

### 已采用的行为与时间规则''')
replace('hypothesis_4/HYPOTHESIS.md', '因此长期回归常态而不是机械归零。', '因此长期效用回归B；能否恢复非零常态发言还受门槛与整数映射约束。')
replace('hypothesis_4/HYPOTHESIS.md', '`alpha_D=0.429695` 与五类 `λ_i` 只用 W13–W18 在统一目标函数下标定，W19–W22 严格留出；', '`alpha_D=0.429695` 与五类 `λ_i` 的最后一轮搜索目标使用W13–W18，W19–W22用于后段模式检查；早期设计已参考后期形态，不能称为从未参与建模的独立验证集；')
replace('hypothesis_4/HYPOTHESIS.md', '\n算法策展主假设（2026-09-08', '\n### 历史定向假设与机制选择记录\n\n算法策展主假设（2026-09-08')

after_title('hypothesis_4/experiment_2/README.md', '本文稿分工已于2026-10-12按作者修订同步：本实验主要回答问题（2）算法与发帖的循环机制，以及问题（3）完整策展制度是否差异化推动悼念向玩梗转变。问题（1）的现实轨迹与平台差异由原始数据分析回答。理论来源与实验对应见[EXPERIMENT.md](EXPERIMENT.md)，作者文稿接入见[paper](../../paper/README.md)。')
replace('hypothesis_4/experiment_2/README.md', '根级runs探索已交接，本目录是当前官方实验入口', '此前到达时机探索已交接，当前U标定与文稿run保持活跃；本目录是当前官方实验入口')
after_title('hypothesis_4/experiment_2/EXPERIMENT.md', '''## 与最新作者文稿的对应（2026-10-12）

本实验主要回答[TOPIC.md](../../TOPIC.md)的问题（2）（3）：循环交互如何形成表征轨迹，以及不同策展制度是否差异化推动悼念向玩梗转变。问题（1）的时序结构、跨平台共性与差异主要由原始数据挖掘与分析回答；三种模拟制度不对应三个真实平台，现实平台差异也不单独构成算法因果证据。

总体解释采用传播反馈回路视角（Trilling，2024）与策展流框架（Thorson、Wells，2016）。算法组织个人可见内容，D（意见气候响应）将所见构成映射到表达参与，B（常态表达基线）提供事件影响消退后的效用参照，R（事件注意力权重）随同类累计接触降低事件影响的权重；新表达按本臂规则回流并成为下一轮可见性条件。具体函数、命名及参数属于本文操作化，文献迁移的假设与适用边界仍须在方法及补充材料中说明。

B使用W05–W12供给形状及W13共同换算尺度，低频正期望可能映射为零发言；R初始为1时首次效用不由B决定。因此“事件前数据校准B”不等于独立事件前估计或完整常态复现。最后一轮搜索使用W13–W18，后段模式检查不能抹去早期参考后期形态的历史；数值代理与完整LLM验证分别报告。这里仅对齐解释和证据分工，不改下列冻结设计，也不宣称这几项效度问题已经全部解决。

玩梗份额、表达参与及可见性用于观察问题（3）的方向与幅度；类别份额不是直接测量情绪、道德评价或恶意程度。三臂继续比较完整制度，包含候选池、生命周期及回流差异；不改称相同候选池下的纯排序效应。''')

replace('锚定式事件表达激活模型.md', '# 从潜伏群体到主导表征：推荐算法为何激活并放大玩梗表达', '# 锚定式事件表达激活模型：选择性表达的操作化说明')
replace('锚定式事件表达激活模型.md', '> **文档性质**：本文件总结当前关于新理论模型的讨论，用于冻结概念、理论来源、数学结构、可检验命题与解释边界。它目前是一项**待检验的理论模型**，不代表既有实验文件、代码或运行配置已经据此修改。', '''> **文档性质（2026-10-12对齐）**：本文件是总体传播反馈回路框架中“选择性表达”的操作化讨论，不作为另一套总体理论。采用作者修订稿中的名称：D为意见气候响应，B为常态表达基线，R为事件注意力权重；下文“气候效用”“常态锚点”“注意力余量”为既有讨论中的对应称呼。当前正式函数与冻结参数以experiment_2为准，文献提供机制依据，具体变量、函数与取值是本文设定。历史推演与候选命题不因文稿对齐而自动成为已验证结论。''')
replace('锚定式事件表达激活模型.md', '研究总标题暂定为：', '以下标题是此前U模型讨论的题名，当前论文题名以作者文稿为准：')
replace('锚定式事件表达激活模型.md', '本文当前提出的新理论模型首先解释“激活”。', '这一表达操作化首先解释“激活”。')
replace('锚定式事件表达激活模型.md', '理论模型暂命名为：', '表达操作化模型沿用名称：')
replace('锚定式事件表达激活模型.md', '事件引起的异常表达冲击逐渐消失，哀悼表达回到常态，而不是被机械压缩为完全沉默。', '事件引起的异常表达冲击逐渐消失，效用回到B；这不保证哀悼表达人数非零，当前低频锚点与门槛映射仍可能产生零发言。')

after_title('data/README.md', '## 在论文中的职责（2026-10-12对齐）\n\n原始数据挖掘与分析主要回答研究问题（1）：逝者数字形象的时序结构、演化特征及平台之间的共性与差异；同时为问题（2）（3）的LLM ABM提供群体、供给和模式参照。研究问题完整表述见[TOPIC.md](../TOPIC.md)。现实内容类别、仿真作者类型和仿真正文语义类别分别说明，玩梗不直接等同于负面态度或恶意。文稿对齐不更换标签、分母或已有测量不确定性证据，也不将跨平台观察差异直接归因于推荐算法。')

put('paper/README.md', '''# Paper 工作区

本目录承接论文正文、附录、图件、参考资料与审阅记录。2026-10-12按作者最新两份Word修订对齐研究背景、文献综述和第二章第一节理论框架；这是文稿更新，不改变机器研究阶段。

## 当前文稿与证据入口

作者最新来源保留在项目根目录：[研究背景与文献综述](<../【1009批注版】ICA-研究背景和文献综述.docx>)、[理论框架](<../【修订1】1008 理论框架.docx>)；[PDF初稿](../悼念退潮之后：基于多智能体仿真的逝者数字形象塑造机制研究.pdf)供完整章节与历史结果核对。来源身份、批注处理和同步范围见[接入审计](manuscript/INTAKE_AUDIT.md)。

当前可检索文本为[manuscript.accepted.md](manuscript/manuscript.accepted.md)：研究背景、第一章和第二章第一节已同步最新作者稿；摘要、第二章后续部分、第三至五章保留已有文本与编码诚信修订，须按标记区分历史结果，尚未完成整稿更新。Markdown不代替作者原始DOCX或排版PDF。

问题（1）主要由原始数据挖掘与分析回答，LLM ABM主要承担问题（2）的循环机制解释和问题（3）的制度差异检验。总体框架采用传播反馈回路视角与策展流框架，D、B、R为选择性表达的模型操作化；完整分工见[TOPIC.md](../TOPIC.md)。

当前主设计是[experiment_2的timestamp_v1](../hypothesis_4/experiment_2/README.md)，九份配置已离线验收，尚未启动LLM。anchored_v1的九次已完成仿真与1904条Agent帖属于既有结果；weekly_lag1是已完成的信息延迟敏感性批；weekly_lag1_event_v2已撤回。旧稿数字不改称timestamp结果，证据身份以实验README和[归档清单](../ARCHIVE_MANIFEST_H4E1.md)为准。

## 一级资产

| 资产 | 用途 |
|---|---|
| `manuscript/` | 可检索正文、接入审计、source历史原稿和嵌入图件；不覆盖原件 |
| `appendices/` | 作者维护的论文附录，当前对齐不改写 |
| `reviews/` | 历史或进行中的审阅材料，不等于完成官方paper review |
| `spot_check/` | 人工复编码抽检工具包；执行情况以对应记录为准 |
| `refs_mechanism_D_R.*` | 表达机制参考资料 |
| [REMEDIATION_PLAN.md](REMEDIATION_PLAN.md) | 已有编码可靠性及论文诚信修订依据 |

## 后续写作边界

在[当前U标定run](../runs/2026-10-09-01-activation-calibration/README.md)内，后续讨论并重写第二章第二部分及第三、四章；本次先完成思路对齐，尚未开始这些章节的重写。八项U问题均在正文保留必要信息，在线补充材料展开依据与复现细节；具体分工及未解决项见该run README。写作不得把数值代理写成完整LLM验证，也不得把组织材料写成已解决效度问题。

修改正文前先读接入审计；数值结论回查对应冻结结果及编码轮。用户原始DOCX/PDF、附录和历史审阅包保留。内容更新后再生成新的排版稿并检查版面，不沿用旧PDF的验收结论。
''')

def clean_export(name, prefix):
    s = (run/'tmp/manuscript_alignment'/name).read_text()
    s = re.sub(r'\[([^\]\n]+)\]\{\.mark\}', r'\1', s)
    s = s.replace('^\\[^[^', '[^').replace(']^\\]^', ']')
    s = s.replace('------', '——').replace('---', '—')
    s = re.sub(r'\[\^(\d+)\]', lambda m: f'[^{prefix}{m.group(1)}]', s)
    s = re.sub(r'(\[\^[^\]]+\]:) \\\[\\\] ', r'\1 ', s)
    return s
bg = clean_export('background.md', 'bg')
tf = clean_export('framework.md', 'tf')
bgbody, bgnotes = bg.split('[^bg1]:', 1)
tfbody, tfnotes = tf.split('[^tf1]:', 1)
tfbody = tfbody.split('\n\n', 1)[1]
(out/'background.accepted.md').write_text(bg)
(out/'framework.accepted.md').write_text(tf)
p = 'paper/manuscript/manuscript.accepted.md'
s = before[p]
start = s.index('在社交媒体深度嵌入公共生活的当下', s.index('**关键词：**'))
end = s.index('**二、研究设计**', start)
s = s[:start]+bgbody.strip()+'\n\n'+s[end:]
start = s.index('**（一）理论框架**')+len('**（一）理论框架**')
end = s.index('**（二）研究方法**', start)
boundary_note = '> **后续章节待重写**：自第二章（二）起保留既有正文及编码可靠性修订；第二章第二部分和第三、四章将在当前run另行讨论后重写。现有实验数值保留历史来源身份，不作为尚未运行的timestamp_v1结果。\n\n'
s = s[:start]+'\n\n'+tfbody.strip()+'\n\n'+boundary_note+s[end:]
intro_note = '> **作者文稿对齐（2026-10-12）**：研究背景、第一章文献综述与第二章（一）按作者最新两份Word稿接受修订后的正文同步，批注不自动写入正文；原始Word及PDF未修改。问题（1）由原始数据挖掘与分析回答，LLM ABM主要回答问题（2）（3）。本文件为分部分更新稿；下列旧摘要、关键词及第二章后续部分、第三至五章仍待相应复核，保留已有编码可靠性修订，不能将其结论视作最新主批结果。来源和引用对应见[接入审计](INTAKE_AUDIT.md)。\n\n'
pos = s.index('\n\n')+2
s = s[:pos]+intro_note+s[pos:]
s += '\n\n<!-- 2026-10-12作者修订稿引用，bg/tf前缀避免与历史脚注混淆。书目信息沿用作者稿，未作独立文献真实性审计。 -->\n\n[^bg1]:'+bgnotes.rstrip()+'\n\n[^tf1]:'+tfnotes.rstrip()+'\n'
put(p, s)

audit = '''# 正文接入与版本审计

## 2026-10-12作者修订稿对齐

本轮只落实研究背景、文献综述、第二章第一节理论框架及相关项目研究文档；原始文件未覆盖。PDF初稿全文20页已提取阅读，并核对第6、8、11页的机制图、公式与实验表。两份Word按接受插入、排除删除的当前正文读取，同时读取全部批注与脚注。

| 作者来源（根目录） | 身份与处理 |
|---|---|
| `悼念退潮之后：基于多智能体仿真的逝者数字形象塑造机制研究.pdf` | 全稿初稿；章节、模型说明与历史结果参照，不能覆盖既有编码诚信修订 |
| `【1009批注版】ICA-研究背景和文献综述.docx` | 新研究背景、第一章三节综述和三个研究问题；7处插入、0处删除、7条批注、14项脚注 |
| `【修订1】1008 理论框架.docx` | 最新总体理论；24处插入、11处删除、8条批注、4项脚注；来源独立标题在合稿中放入第二章（一） |

Word正文已同步到[manuscript.accepted.md](manuscript.accepted.md)，清理转换器的高亮/上标包装，不改作者论点；新脚注分别使用bg1–bg14、tf1–tf4避免与旧稿冲突。引用信息沿用作者来源，尚未进行独立文献真实性审计。批注作为理解语境：未把“正面形象六成”等建议当作数据事实，未将玩梗直接等同恶意或负面。

研究分工按用户明确要求落实：问题（1）主要由原始数据挖掘与分析回答，问题（2）（3）主要由LLM ABM回答。理论以传播反馈回路视角与策展流框架解释整体循环，B、D、R是表达环节的操作化，而非文献直接提出的一套变量。原先精准遏制恶意玩梗的治理问题不再是当前问题（3），治理意义保留为讨论方向。

作者理论正文中“B由事件前供给数据校准”的概括按原文保留；项目方法文档同时明确W13参与共同尺度、低频映射零人数和初始化限制，具体解释留待第二章后续重写。制度差异包含候选池及回流，不能缩写为同候选池下仅改变排序。仿真类别份额用于观察表征构成，不直接测量情绪或恶意。

摘要、关键词、第二章（二）及以后、第三至五章保持此前文本与编码诚信修订；本轮没有重写或更新实验数字。当前timestamp_v1九配置已离线验收、未启动LLM；anchored_v1结果、数值代理和敏感性分开解释。第二章第二部分与第三、四章后续在当前run中讨论后重写。

来源SHA256、本轮前文件副本、逐文件差异与范围核验保存在[本轮对齐证据](../../runs/2026-10-09-01-activation-calibration/manuscript_alignment/README.md)。下文为历史接入审计，版本与“当前”表述只对应当时。

---

'''
put('paper/manuscript/INTAKE_AUDIT.md', audit+before['paper/manuscript/INTAKE_AUDIT.md'].replace('# 正文接入审计（2026-09-15）', '## 历史接入审计（2026-09-15）', 1))

replace('runs/2026-10-09-01-activation-calibration/README.md', '- 当前阶段：2026-10-12用户明确授权的实验1与2离线阶段已完成，窗口检查与45单元有限正文闭环代理全部通过执行验收；恢复验证通过。run保持活跃，B标定与行动候选未采纳。', '- 当前阶段：实验1与2离线阶段及恢复验证已完成；2026-10-12按用户授权将最新文稿的研究问题、背景、综述及理论框架对齐主工作区。第二章第二部分与第三、四章尚未开始重写；run保持活跃，B标定与行动候选未采纳。')
replace('runs/2026-10-09-01-activation-calibration/README.md', '| `workspace/` |', '| [manuscript_alignment/](manuscript_alignment/README.md) | 作者最新来源校验、前状态副本、正文提取、主工作区文档差异及核验 |\n| `workspace/` |')
replace('runs/2026-10-09-01-activation-calibration/README.md', '## 待办与下一步', '''## 最新作者文稿对齐与后续写作授权（2026-10-12）

用户明确授权先把最新研究背景、文献综述和第二章第一节理论框架落实主工作区，再在本run讨论和重写第二章第二部分及第三、四章。本轮完成前一阶段，主工作区的研究文档与论文Markdown已更新；原始DOCX/PDF、实验代码、配置、数据、历史结果与机器状态保留。实际修改路径及逐文件差异见[对齐证据](manuscript_alignment/README.md)。这是后续新增的文档采用授权，不改变原离线实验候选未采纳的状态。

问题（1）由原始数据挖掘与分析回答；LLM ABM主要回答问题（2）的循环机制与问题（3）的制度差异。总体解释采用传播反馈回路视角与策展流框架，U中的B、D、R为选择性表达的操作化；三臂仍比较完整策展制度。文稿对齐不构成这些机制已获全部验证的声明。

用户已认可：八项U问题都在正文留下关键信息，补充材料展开依据与复现细节。后续撰写采用下列分工；仅为已接受的写作安排，不表示各项实验已经完成。

| 问题 | 正文关键信息 | 在线补充材料 |
|---|---|---|
| 1．0.95的选择 | 简述探索后保留的共同门槛基准，非实测心理临界值 | 历史探索、门槛分布、候选值与敏感性 |
| 2．文献公式迁移 | 文献依据、从意见气候到可见内容/从集体注意力到个体接触的迁移与新增假设 | 原模型逐项对应、D/R全式、变量及适用边界 |
| 3．B、D、R标定 | 数据窗口、W13作用、固定/拟合项、三制度共享 | 参数表、换算映射、搜索目标与范围、可识别性及代码 |
| 4．低频差异压零 | 100人尺度下正低频期望被近似为零发言及解释限制 | 原始期望、映射人数、取整与替代规则检验 |
| 5．U组合形式 | U公式、R降低使效用回B，可能减弱激活或释放抑制 | 数学性质、边界、替代组合与检验 |
| 6．初始化与常态 | 初始累计接触、首次行动B不起作用及常态主张边界 | 初始化、W12现实/模拟对照、敏感性 |
| 7．标定与验证 | 数据使用历史、后段检查性质、数值代理与完整生成验证区别 | 设计历史、数据用途、版本及全部验证 |
| 8．反馈机制支持 | 机制干预设计、实际关键结果与可支持的解释 | 全部干预条件、类型/周次结果、重复与补充图 |

下一阶段先具体讨论第二章第二部分的方法叙述，再组织第三章现实分析与第四章仿真机制/制度比较；实际章节结构以作者后续决定为准。不得将现实平台差异当算法因果证据，不将旧批结果写作timestamp结果，不借写作启动新LLM或扩大实验矩阵。

## 待办与下一步''')
replace('runs/2026-10-09-01-activation-calibration/README.md', '- 本轮未修改主项目源码/配置/数据/理论文档，仅本run资产及runs索引；', '- 上述离线实验阶段未修改主项目源码/配置/数据/理论文档，仅本run资产及runs索引；后续2026-10-12文稿对齐已按独立授权更新正式研究文档，详见上节；')
replace('runs/README.md', '| 核查U公式与B标定质疑，落实已授权理论框架表述 | 实验1/2离线完成、恢复验证通过；候选未采纳，未启动LLM |', '| 核查U/B标定、落实最新作者文稿与研究分工；后续章节在本run重写 | 实验1/2离线完成；主工作区文稿对齐完成，后续章节尚未重写；实验候选未采纳，未启动LLM |')

# 对齐后逐文件证据由实际文件产生，不混入任务开始前已有差异。
changes = ''.join(''.join(difflib.unified_diff(before[p].splitlines(True), (root/p).read_text().splitlines(True), fromfile='a/'+p, tofile='b/'+p)) for p in paths)
(out/'alignment.diff').write_text(changes)
evidence = {'date':'2026-10-12', 'git_commit':subprocess.check_output(['git','rev-parse','HEAD'], cwd=root,text=True).strip(),
            'sources_sha256':source_hashes, 'updated_paths':paths,
            'before_sha256':{p:hashlib.sha256(before[p].encode()).hexdigest() for p in paths},
            'after_sha256':{p:sha(root/p) for p in paths}, 'checks':{}}
(out/'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n')
(out/'README.md').write_text('''# 最新作者文稿对齐证据

本目录保存2026-10-12主工作区文稿对齐的来源与差异，实时状态只在[run README](../README.md)维护。用户授权直接落实研究背景、文献综述、理论框架及研究分工；第二章第二部分与第三、四章尚未重写。

| 资产 | 用途 |
|---|---|
| `before/` | 本轮修改前13份文档的实际文件副本，含此前已有未提交修改，不以HEAD冒充起点 |
| [git_start.txt](git_start.txt) | 修改前主工作区Git状态 |
| [background.accepted.md](background.accepted.md)、[framework.accepted.md](framework.accepted.md) | Word接受修订后提取的正文与脚注，去转换器包装、保留作者论点 |
| [alignment.diff](alignment.diff) | 本轮13份文档相对于上述副本的差异，不含用户其他已有修改 |
| [evidence.json](evidence.json) | 三份作者来源与前后文档SHA256、Git基线及实际核验结果 |

作者原始文件位于项目根目录，名称与SHA256见evidence.json；本目录不复制或修改原DOCX/PDF。差异用于审阅和追溯文档对齐，不是新的代码候选补丁，也不包含参数或数据变更。本轮完整验证仅为文档核验，不重跑实验、调用LLM或改变机器阶段。
''')
print('Updated', len(paths), 'documents; evidence:', out)
