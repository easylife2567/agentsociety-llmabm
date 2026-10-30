"""将已审阅的比较叙述与可追溯表格写入本 run；不调用模型或修改实验。"""
from pathlib import Path
import csv, json, shutil, html
A=Path(__file__).resolve().parent
R=A.parent
W=R/'workspace'
P=W/'presentation/hypothesis_4_cuc'
S=W/'synthesis'
for p in [P,S]: p.mkdir(parents=True, exist_ok=True)

def write_json(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def md_table(headers,rows): return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)
def ht_table(headers,rows): return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+html.escape(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(c))+'</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table></div>'
late=list(csv.DictReader((A/'data/late_author_participation.csv').open()))
part=[]
for arm,name in [('random','随机 / Random'),('chronological','时序 / Chronological'),('interest','兴趣 / Interest')]:
 row=[name]
 for typ in ['mourning','meme','education','marketing','other']:
  vals=[next(x for x in late if x['version']==v and x['algorithm']==arm and x['author_type']==typ) for v in ['old','new']]
  row.append(' → '.join(f"{x['late_posted']}/{x['late_opportunities']} ({100*float(x['late_participation']):.2f}%)" for x in vals))
 part.append(row)
main_headers_zh=['制度','发布帖数（旧→新）','W13悼念作者参与','W13悼念曝光（旧→新）','W19–22玩梗作者参与（旧→新）','W19–22 Agent玩梗供给份额（旧→新）','W19–22玩梗曝光（旧→新）']
main_headers_en=['Regime','Posts, old → new','W13 mourning author participation','W13 mourning exposure, old → new','Late meme author participation, old → new','Late Agent meme supply share, old → new','Late meme exposure, old → new']
main_rows=[['随机 / Random','176 → 176','2/22 (9.09%) → 同 / same','7.90% → 7.90%','4/76 (5.26%) → 同 / same','4/30 (13.33%) → 同 / same','118/4000 (2.95%) → 同 / same'],['时序 / Chronological','210 → 210','21/22 (95.45%) → 同 / same','31.10% → 31.10%','41/76 (53.95%) → 同 / same','41/59 (69.49%) → 同 / same','1582/4000 (39.55%) → 同 / same'],['兴趣 / Interest','214 → 217','21/22 (95.45%) → 同 / same','28.50% → 28.10%','34/76 (44.74%) → 35/76 (46.05%)','34/54 (62.96%) → 35/51 (68.63%)','795/4000 (19.875%) → 799/4000 (19.975%)']]
quality_headers_zh=['制度','首次生成数 旧→新','首次空输出 旧→新','本地年龄门控修正 旧→新','正文重写 旧→新','发布正文中位字符数 旧→新','发布正文>300字符 旧→新']
quality_headers_en=['Regime','First generations, old → new','Initially empty, old → new','Local age-check edits, old → new','Body rewrites, old → new','Median published characters, old → new','Published >300 chars, old → new']
quality_rows=[['Random','176 → 176','1 → 0','0 → 0','1 → 0','216 → 175.5','2 → 0'],['Chronological','210 → 210','0 → 0','0 → 1','0 → 0','202.5 → 176','5 → 2'],['Interest','214 → 217','0 → 0','0 → 2','0 → 0','205.5 → 178','0 → 0']]
part_zh=['制度','悼念','玩梗','教育','营销','其他']
part_en=['Regime','Mourning','Meme','Education','Marketing','Other']
zh='''# CUC 服务三制度与旧服务的配对比较

**结论：本次服务替换没有反转主要制度排序，但生成内容存在质量差异，兴趣制度也有可测的回流变化。** 随机、时序的数值轨迹保持一致；后期玩梗的作者参与、Agent 供给份额和曝光均仍为“时序 > 兴趣 > 随机”。这支持当前冻结配置下的结论稳健性，不能证明两模型等价。

本报告为指定 run 内的候选分析成果，未正式采用、提交或归档。

## 设计、数据和口径

新批为 100 个 Agent、W12–W22 共 11 周，每制度一次。没有显式环境 seed，也没有模型 seed；环境默认值为 0，因此本批不能称为“无随机性”。主要配对对象为旧 `experiment_2/runs/timestamp_v1` 下三制度的 s0，因为冻结输入由这些条件复用。旧 s1、s2 仅提供已有波动范围，未混入配对估计。

三臂各完成 693 步、1100 个唯一 Agent×周行动，环境实际发布与 Agent 账本一致，共 603 帖。监督器与子进程均已退出。正文外层请求 603 次，额外请求 0/330，技术失败、兜底均为 0；三次本地年龄修正不额外请求模型。3630 仅是正文外层预算上限，SDK observe/statistics 与一次探测另计；SDK 三次超时已恢复，不能把“正文失败为零”解释成服务从无超时。

官方 EDA 在兴趣臂确认 11 行环境周记录、1100 行 Agent 周记录，每周 1000 个阅读槽位。全比较由 ReplayReader、ENV_STATE 和 AGENT 账本复算，输出见 [来源与校验和](data/source_index.json)、[完整性核验](data/integrity.json)。

口径必须分开：**固定作者类型**决定作者参与和 Agent 供给；**feed 池标签**决定曝光槽位；**正文词表分类 `assigned_type`**只是文本诊断，不是真实语义金标。本文的“玩梗份额”均指指定前两类口径，不能读作人工判定的玩梗语义比例。作者参与率分母为该类人口×周数，例如后期玩梗为 19×4=76；Agent 供给份额分母为同一时段全部 Agent 帖；曝光份额分母包含外部与 Agent 的全部阅读槽位，W13 为1000，后期为4000。后期比例按计数合并，非逐周份额的无权平均。

## 数值结果：方向保持，兴趣局部变化

MAIN_TABLE

W13 是预先指定的事件反应周，不能把它预称为每条曲线的全期峰。兴趣制度的悼念曝光在 W15 达到最高值，完整周序列与峰位见 [11周比较附表](data/weekly_comparison.md) 与 [逐周原始指标](data/weekly_metrics.csv)。事件周悼念作者参与的“时序=兴趣>随机”关系保持；后期玩梗三个主要指标的“时序>兴趣>随机”也保持。

随机、时序各 11 周环境 Replay 科学字段（排除时间元字段）、1100 个决策的发言/效用/阈值等数值字段以及实际 feed 稳定键序列及池标签一致；其中Agent帖正文和倾向分数不同，所以完整提示仍可不同。兴趣臂有 815 个 Agent×周的所查决策字段不同，其中只有 73 个 Agent×周改变是否发言，实际 feed 键序列有 999 处不同。这些数量不是 815 或 999 次发言翻转。全期净增 3 帖也不意味着仅 3 个决策改变。

兴趣后期 Agent 玩梗供给份额增加 **5.66 个百分点**，既因为玩梗帖从34增至35，也因为全部 Agent 帖从54降至51；曝光只增加 **0.10 个百分点**。新兴趣 W13 悼念曝光28.1%低于旧s0–s2范围28.5%–37.0%，后期Agent玩梗份额68.63%高于旧范围62.96%–67.21%。因此不能说“全部变化都在旧随机波动内”；三个旧重复的最小最大值也不是置信区间。

![新旧服务的轨迹和后期制度比较](assets/figure_01_model_comparison.png)
图1：上排展示兴趣臂11周的局部轨迹变化，下排展示三制度后期排序保持；旧实线与新虚线及百分比分母见图。完整三臂周序列在附表。

### 各固定作者类型的后期参与率

每格为旧s0→新批的“发言 Agent×周/该类全部 Agent×周”；这里不是独立发言人数，也不是帖子语义分类。

PART_TABLE

## 生成质量：可完成正文任务，不等于质量相同

QUALITY_TABLE

旧 s0 合计600次首次生成，1次空输出后重写；新批603次首次生成无空输出、无接口标记拒答，3条命中运行时年龄门控并本地修正（3/603=0.50%），没有正文付费重写或模板兜底。语义核对显示，兴趣两条为输入未支持的人物年龄；时序一条更像与persona一致的自述年龄，被门控误删。因此3/603是修正率，不是人物年龄幻觉率。旧s0无年龄门控修正。两批所有制度内按NFKC规范化并去空白后，完全重复正文均为0；这不排除语句套式和语义重复。

新批发布文本中位长度在三制度均更短。`>300`是对提示长度的诊断；实际实现上限为400，不能把每条超过300的内容直接算技术失败。原始输出与修复后发布内容分开保存，字符表以最终环境发布文本为准，详细分布见 [质量统计](data/quality_summary.json)。

SEMANTIC_ZH

## 正文如何进入数值机制

发言决定由环境根据所见 feed 标签和冻结参数计算，LLM负责生成已决定发布的正文。生成正文经词表计算四类倾向，兴趣推荐会使用这些分数；随机抽样、时间排序不会按该分数选帖。因此前两制度数值完全相同有明确结构原因，不能据此称新旧模型能力相同。

可追踪的最早链条是：兴趣 W12 Agent57 的营销帖改变正文倾向，例如营销分数3.4826→3.2178、教育0.4975→0.7426；下一周 W13 Agent80 的 feed 教育标签由1/10变为2/10，效用0.8883→1.1117，两版均发言。随后 Agent90 首次出现发言分歧，效用1.0401→0.8764，由发布转为低于阈值而沉默。后续改变还可经曝光、供给与疲劳累积传播。这是同一冻结机制下观察到的路径，不应归因于某一个词独自造成全部差异。[机制与原始记录](data/mechanism_trace.json)

## 速度与适用结论

新批北京时间10月16日13:51:50–19:35:25完成，含调度343.59分钟（约5小时44分），距12小时保护上限尚有约6小时16分。旧s0三臂从旧batch开始到interest_s0完成176.34分钟（约2小时56分），新批约为1.95倍耗时。旧三臂引擎各57.97/58.48/59.37分钟，合计175.83分钟；调度口径与引擎口径分开。[运行对比](data/runtime_comparison.json) 这些运行跨时段，混有服务负载、辅助请求和调度开销，不能认定模型固有吞吐降低1.95倍。价格未核实，不能凭速度或用户预期宣称更便宜。

本次能够支持的是：**当前100人、固定机制与输入的服务替换检查中，主要制度排序维持，正文更短且存在事实/角色边界问题，兴趣回流指标有局部变化。** 请求别名为`cuc/deepseek`，返回过`deepseek-v4.1-flash`及`-2/-3/-4`；旧请求为`deepseek-v4-1-flash-260910`、返回`deepseek-v4-1-flash`。后台底层及别名对应不确定，不能断言在比较两个不同基础模型。

每个新制度仅一次，未加入新seed或额外实验；不作跨重复显著性推断、总体幻觉率估计或笼统能力排名。仿真证据也不直接证明现实平台上的因果效应。扩大到500/1000人的可信度与成本问题尚未由本轮解决。

## 证据与复算

- [提取脚本](extract_comparison.py)、[全部来源与SHA256](data/source_index.json)、[配对差值](data/paired_metric_differences.csv)、[制度差值方向](data/institution_contrasts.csv)。
- [11周数据](data/weekly_metrics.csv)、[周序列可读附表](data/weekly_comparison.md)、[作者参与](data/late_author_participation.csv)、[首次分歧](data/first_differences.json)。
- [抽样规则](data/sample_selection.json)、[59对正文与实际feed](data/paired_text_samples.jsonl)、[语义审读注释](data/text_review_annotations.jsonl)、[审读说明](data/text_review_findings.md)、[补充异常样本](data/supplementary_anomaly_samples.jsonl)。
- [综合判断](synthesis_report_zh.md)、[图的可编辑SVG](assets/figure_01_model_comparison.svg)。复算命令与原始文件路径在source_index；报告和统计均在本run内，未改正式机制、配置或主区流水线。研究仍为H4，4_cuc仅为隔离分析命名；具体claims结果尚未逐项获用户确认，正式发布保持未签，不声称validate-synthesis或流水线完成。此流程边界不否定已经核验的证据，用户无需为本次候选交付批准额外操作。
'''
en='''# Paired comparison of the CUC service and the previous service

**The service replacement did not reverse the principal regime ordering in this check. Text quality differs, and interest curation shows measurable feedback changes.** Numerical trajectories are identical under random and chronological curation. Late meme-author participation, Agent meme supply share and meme exposure remain ordered chronological > interest > random. This supports robustness under the frozen configuration; it does not establish model equivalence.

This is a candidate analysis inside the designated run, without formal adoption, commit or archival.

## Design, data and definitions

The new batch has 100 Agents, 11 weeks (W12–W22), and one run per regime. No explicit environment seed or model seed was supplied; the environment uses its default 0. The paired baseline consists of the three old s0 conditions in `experiment_2/runs/timestamp_v1`, whose frozen inputs were reused. Old s1/s2 runs describe an existing range only; they are not additional paired observations.

Each new regime completed 693 steps and 1100 unique Agent-week actions; environment publication totals match Agent ledgers. There are 603 posts. Supervisor and child processes have exited. The batch used603 outer body requests,0/330 additional requests, no body technical failures and no fallbacks. Three local age repairs required no model request. The3630 ceiling covers outer body requests only: SDK observe/statistics and one probe are separate. Three recovered SDK timeouts must not be erased by reporting zero body failures.

Official EDA confirmed11 environment rows and1100 Agent rows for interest, with1000 feed slots per week. ReplayReader, ENV_STATE and AGENT ledgers underpin the full comparison; see [provenance and hashes](data/source_index.json) and [integrity](data/integrity.json).

Three classifications are distinct: fixed author type determines author participation and Agent supply; feed pool labels determine exposure; lexical `assigned_type` is a text diagnostic, not semantic ground truth. Participation divides speaking Agent-weeks by all opportunities for that author group (late meme:19×4=76). Agent supply share divides by all Agent posts in the same period. Exposure divides by all external and Agent feed slots (1000 in W13;4000 in W19–W22). Late ratios pool counts across weeks rather than averaging weekly percentages.

## Numerical findings: preserved direction, local interest changes

MAIN_TABLE

W13 is the prespecified event-response week, not a presumed global peak of every curve. Interest mourning exposure peaks at W15. The [weekly appendix](data/weekly_comparison.md) and [complete series](data/weekly_metrics.csv) retain all11 weeks. W13 mourning-author participation keeps chronological=interest>random; all three late meme metrics keep chronological>interest>random.

For random and chronological, all11 environment replay scientific fields (excluding time metadata), selected numerical decision fields across1100 Agent-weeks, and ordered feed stable keys and pool labels agree. Agent text and tendency scores differ, so full prompts can still differ. Under interest,815 Agent-weeks differ in checked decision fields, but only73 change whether the Agent speaks;999 ordered feed-key sequences differ. These counts do not mean815 or999 speaking flips. A net increase of3 posts also does not mean only3 decisions changed.

Interest late Agent meme supply share increases **5.66 percentage points**: meme posts increase34→35 while all Agent posts decline54→51. Meme exposure changes only **+0.10 points**. New W13 interest mourning exposure28.1% lies below the old s0–s2 range28.5%–37.0%; late Agent meme share68.63% exceeds the old62.96%–67.21% range. Therefore, not all metrics remain within the old range. A minimum–maximum over three old runs is not a confidence interval.

![Service comparison trajectories and regime ordering](assets/figure_01_model_comparison.png)
Figure1. Upper panels show11-week interest trajectories; lower panels show the preserved late ordering across regimes. Old solid/new dashed conventions and percentage denominators appear in the figure; complete series are in the appendix.

### Late participation by fixed author type

Cells show old s0→new speaking Agent-weeks / all opportunities for that type. These are not unique-person participation rates or semantic content categories.

PART_TABLE

## Generation quality: task completion is not equivalence

QUALITY_TABLE

The old paired s0 runs contain600 first generations, with one empty response followed by a rewrite. All603 new first generations are nonempty and carry no provider refusal flag. Runtime age checks locally edited3 new texts (3/603=0.50%); old paired s0 has no such edit. Context review finds unsupported subject ages in two interest texts, whereas the chronological case more plausibly states the Agent’s own persona-consistent age and was overfiltered. Thus3/603 is an edit rate, not a subject-age hallucination rate. No new paid body rewrite or template fallback occurred. After NFKC normalization and whitespace removal, exact duplicate excess is zero within each regime for both batches; formulaic phrasing and semantic repetition are not excluded.

Published median length decreases in all regimes. A >300-character count diagnoses the prompt preference; the actual implementation limit is400, so every >300 output is not a technical failure. Raw and published texts are retained separately; length statistics use final environment publications. [Full quality statistics](data/quality_summary.json).

SEMANTIC_EN

## How text enters the numerical mechanism

The environment determines speaking from observed feed labels and frozen parameters; the LLM writes bodies after the decision. Lexical scores derived from text enter interest recommendations. Random sampling and chronological ordering do not select posts by these scores, providing a structural reason for numerical identity under those regimes. That identity is not evidence of equal language-model ability.

The earliest traceable path starts with interest Agent57 in W12: marketing tendency3.4826→3.2178 and education0.4975→0.7426. Agent80 in W13 subsequently sees1/10→2/10 education slots, with utility0.8883→1.1117; it speaks in both versions. Agent90 is the first speaking divergence: utility1.0401→0.8764, switching from publication to below-threshold silence. Exposure, supply and accumulated fatigue can propagate later changes. This is an observed path through the frozen mechanism, not proof that a single word caused all downstream changes. [Mechanism trace](data/mechanism_trace.json).

## Runtime and warranted interpretation

The new batch completed on October16,13:51:50–19:35:25 Beijing time:343.59 minutes including dispatch (about5h44m), leaving about6h16m under the12-hour guard. Old s0 took176.34 minutes from batch start through interest_s0 completion (about2h56m); new elapsed time is about1.95×. Old engine-only times are57.97/58.48/59.37 minutes, totaling175.83 minutes. [Runtime comparison](data/runtime_comparison.json). These executions occurred at different times and include service load, auxiliary calls and dispatch overhead; they do not identify intrinsic model throughput. Price was not verified.

The defensible conclusion is limited to this100-Agent service replacement check: **principal regime ordering persists; text is shorter and exhibits factual/role-boundary issues; interest feedback changes locally.** Requested alias`cuc/deepseek` returned`deepseek-v4.1-flash` and`-2/-3/-4`; the old request`deepseek-v4-1-flash-260910` returned`deepseek-v4-1-flash`. Backend identity and alias mappings are uncertain; distinct underlying foundation models cannot be assumed.

There is one new run per regime and no added seed or experiment. No repeated-run significance inference, population hallucination rate or broad capability ranking is warranted. Simulation evidence does not directly establish real-platform causal effects. The credibility/cost tradeoff of scaling to500/1000 Agents remains unresolved by this batch.

## Evidence and reproduction

- [Extraction script](extract_comparison.py), [source hashes](data/source_index.json), [paired metric deltas](data/paired_metric_differences.csv), [regime contrasts](data/institution_contrasts.csv).
- [Weekly data](data/weekly_metrics.csv), [readable appendix](data/weekly_comparison.md), [participation](data/late_author_participation.csv), [first differences](data/first_differences.json).
- [Sampling rules](data/sample_selection.json), [59 text pairs with actual feeds](data/paired_text_samples.jsonl), [review annotations](data/text_review_annotations.jsonl), [review findings](data/text_review_findings.md), [supplementary anomalies](data/supplementary_anomaly_samples.jsonl).
- [Synthesis](synthesis_report_en.md), [editable SVG](assets/figure_01_model_comparison.svg). Commands and original paths are recorded in source_index. Outputs stay inside this run; formal mechanisms, configuration and the main pipeline are unchanged. H4 remains the research hypothesis;4_cuc is an isolated analysis namespace. Specific claims have not received item-by-item user approval; formal release signatures remain unsigned and no validate-synthesis/pipeline completion is asserted. This boundary does not negate verified evidence or require approval of additional work for candidate delivery.
'''
# 审读完成前不生成带有最终质量结论的报告。
zh_review=A/'data/text_review_findings.md'
if not zh_review.exists():
 (A/'report_draft_zh.txt').write_text(zh)
 (A/'report_draft_en.txt').write_text(en)
 print('Draft narratives saved; awaiting independent semantic review.')
 raise SystemExit(0)
# 下列审读段落由报告作者在读取全部注释后填写，避免自动把词表结果冒充语义金标。
semantic=json.loads((A/'semantic_report_passages.json').read_text())
zh=zh.replace('SEMANTIC_ZH',semantic['zh'])
en=en.replace('SEMANTIC_EN',semantic['en'])
for lang,body,headers,qh,ph in [('zh',zh,main_headers_zh,quality_headers_zh,part_zh),('en',en,main_headers_en,quality_headers_en,part_en)]:
 body=body.replace('MAIN_TABLE',md_table(headers,main_rows)).replace('QUALITY_TABLE',md_table(qh,quality_rows)).replace('PART_TABLE',md_table(ph,part))
 (A/f'report_{lang}.md').write_text(body)
print('Markdown reports written.')
# HTML 为单独组织的原生正文，未从 Markdown 转换。
style='''<style>:root{color-scheme:light;--ink:#173045;--muted:#526474;--line:#d5dfe5;--accent:#0a6662}*{box-sizing:border-box}body{margin:0;background:#f1f4f5;color:var(--ink);font:16px/1.8 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1190px;margin:auto;background:#fff;padding:44px 5vw}h1{font-size:2.15rem;line-height:1.25;max-width:900px}h2{margin-top:2.4em;border-top:1px solid var(--line);padding-top:1em}h3{margin-top:1.8em}p{max-width:1000px}a{color:var(--accent)}nav{display:flex;gap:1.3em;flex-wrap:wrap;padding:1em 0;border-block:1px solid var(--line)}.lead{font-size:1.14rem;border-left:4px solid var(--accent);padding:8px 20px;background:#edf7f5}.metrics{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}.metric{flex:1;min-width:180px;border:1px solid var(--line);padding:16px}.metric strong{display:block;font-size:1.7rem}.muted,figcaption,footer{color:var(--muted);font-size:.9rem}.table-wrap{overflow:auto;margin:24px 0}table{border-collapse:collapse;width:100%;font-size:.88rem}th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;min-width:130px}th{background:#eaf0f3}figure{margin:30px 0}img{max-width:100%;height:auto}.limitations{background:#fff8e8;border:1px solid #dfcfa6;padding:18px 22px}code{font-size:.88em;overflow-wrap:anywhere}li{margin:.7em 0}@media(max-width:650px){main{padding:25px 6vw}h1{font-size:1.7rem}}</style>'''
zh_html='''<h1>CUC 服务替换：制度排序保持，内容与兴趣回流有变化</h1><p class="muted">AgentSociety · 指定 run 候选分析 · 2026-10-16 · H4 / 隔离分析命名 4_cuc</p><p class="lead">当前100人冻结配置下，新服务未反转主要制度排序：后期玩梗的作者参与、Agent供给份额和曝光均为<strong>时序 &gt; 兴趣 &gt; 随机</strong>。随机/时序数值相同有机制原因；正文更短并有事实、角色边界及后处理问题，不能称模型等价。</p><nav><a href="#data">设计与口径</a><a href="#findings">数值结果</a><a href="#quality">正文质量</a><a href="#mechanism">回流机制</a><a href="#conclusions">速度与边界</a><a href="#appendix">证据</a></nav><div class="metrics"><div class="metric"><strong>3 / 3</strong>制度完成，693步/臂</div><div class="metric"><strong>603</strong>发布帖；3300唯一行动</div><div class="metric"><strong>0</strong>正文技术失败与兜底</div><div class="metric"><strong>343.59 min</strong>全批含调度耗时</div></div><h2 id="data">设计、数据与口径</h2><p>100个Agent，W12–W22共11周，各制度一次。未显式设置环境seed或模型seed，环境实际默认0。主要配对旧experiment_2的random_s0、chronological_s0、interest_s0，复用其冻结输入；旧s1/s2只显示已有范围。</p><p>三臂各1100个唯一Agent×周行动、693步，发布与Agent账本一致，监督器和引擎均已退出。正文请求603次，额外0/330；年龄门控本地修正3条，不额外调用模型。3630仅约束正文外层请求，SDK observe/statistics和探测另计；SDK三次超时已恢复，正文零失败不代表服务零超时。</p><div class="eda-panel"><p>官方EDA：兴趣臂11行环境记录、1100行Agent记录，每周1000个feed槽位。全比较使用ReplayReader、环境状态与Agent账本，而非仅以总帖数判断。<a href="data/eda_quick_stats.md">EDA明细</a> · <a href="data/source_index.json">来源与校验和</a> · <a href="data/integrity.json">完整性</a></p><!-- EDA_INTERACTIVE_BEGIN --><!-- EDA_INTERACTIVE_END --></div><p><strong>固定作者类型、feed池标签、正文assigned_type词表分类</strong>分别对应参与/供给、曝光、文本诊断，不混称语义金标。后期作者参与分母是该类人口×4周（玩梗19×4=76）；Agent供给份额分母为该时段全部Agent帖；曝光分母包含外部与Agent全部槽位（W13为1000，后期4000）。跨周按计数合并，不取周比例无权平均。</p><h2 id="findings">方向保持，兴趣局部变化</h2>MAIN_HTML<p>W13是预设事件反应周，不预断所有轨迹在此全期达峰；兴趣悼念曝光最高周为W15。<a href="data/weekly_comparison.md">11周附表与峰位</a>保留全部制度的悼念/玩梗供给与曝光。</p><p>随机与时序的11周环境Replay科学字段（排除时间元字段）、所查1100个决策数值字段、实际feed键序列/标签一致，但feed内Agent帖正文不同，完整提示不是固定不变。兴趣所查决策字段有815个Agent周不同，实际feed键序列999处不同，其中73个Agent周改变是否发言，净增3帖。这是机制内服务替换比较，不是固定同一完整prompt的纯模型测评。</p><p>兴趣后期Agent玩梗份额+5.66个百分点，来自玩梗34→35帖且全部Agent54→51帖；曝光仅+0.10个百分点。新W13兴趣悼念曝光28.1%低于旧三重复28.5%–37.0%，新后期Agent玩梗68.63%高于旧62.96%–67.21%。不能说全部变化都落在旧范围内；三个重复的极值不是置信区间。</p><figure><img src="assets/figure_01_model_comparison.png" alt="兴趣11周轨迹与三制度后期排序"><figcaption>图1：上排为兴趣11周悼念曝光、Agent玩梗供给、玩梗曝光；下排显示后期三制度排序保持。各分母与旧实线/新虚线见图。</figcaption></figure><h3>五类作者的后期参与率</h3><p>旧s0→新；发言Agent周/该类全部Agent周，非独立人数或正文语义分类。</p>PART_HTML<h2 id="quality">正文可完成生成，质量未证明等价</h2>QUALITY_HTML<p>旧600次首次生成有1次空输出后重写；新603次无空输出和接口标记拒答，无付费正文重写或兜底。本地年龄门控修改3/603=0.50%，但其中时序77/W13的“三十八岁，家里也有正在读书的孩子”与38岁persona一致，更像自述误删；只有兴趣58、85/W13两条审读为无源人物年龄。不能将门控命中率冒充幻觉率。</p><p>最终正文中位长度三制度均更短；NFKC去空白后的制度内全文完全重复为零，不排除套式表达。>300字符仅诊断提示偏好，实际上限400。长度按最终ENV发布记录，原始与发布文本分别保留。</p><p>按制度×五类型×前/中/后期的共同发言Agent周，SHA256稳定排序每格最多2对，共59对118篇。逐侧核对实际提示、persona、首次生成、最终发布和feed；稀疏格不补造。补充异常样本不混入59对分母。助手审读无独立人类金标、无收费模型裁判，不能外推总体幻觉率。59对仅15对完整messages相同、44对不同；随机/时序回流正文也会使提示不同，兴趣还会改变feed键。</p><p>固定样本均能回应所见，未发现无所见依据提前宣告死亡；角色“尚待确认”不算拒答。原始无源人物年龄旧0/59、新2/59，发布后均0/59。例子可按ID在<a href="data/text_review_annotations.jsonl">逐对注释</a>定位：</p><ul><li><code>interest:58:2026-W13</code>新“才41岁”无提示依据，被删后正文可读；旧以“若属实”回应所见讣告。</li><li><code>interest:85:2026-W13</code>新“才四十出头吧”被删，留下“愣了一下。吧，孩子还那么小”，同时暴露原始事实约束与后处理损伤。</li><li>补充<code>new:chronological:77:2026-W13</code>自述年龄疑遭误删；<code>new:chronological:86:2026-W20</code>原始432字符逐字空格，截至399字符以“建 议 出”结尾。删除成功不等于自然、完整。</li><li><code>random:22:2026-W19</code>把自己的旧帖当“@22说的”回应，混淆自他；<code>random:91:2026-W17</code>新增家庭背景与其他来源相近，须与人物硬事实分开评价。</li><li>旧侧<code>random:19:2026-W17</code>将“轻松过线/核心600母题”强化为“600题保过”；<code>interest:61:2026-W13</code>将讣告日期写成自己看到的时间。旧服务不是无错误金标准。</li><li>新时序87、32/W12共享25字符开场，旧营销/玩梗也有套式；新<code>interest:4:2026-W21</code>“火车头/新闻学”确有来源，幽默延展不能机械计作事实幻觉。</li></ul><p>更短不自动等于更差；本次证据支持可完成短帖任务，同时存在来源边界、角色细节、文本自然性问题。<a href="data/text_review_findings.md">完整审读与补充样本</a>。</p><h2 id="mechanism">正文怎样进入数值回流</h2><p>环境根据feed标签和冻结参数决定发言，LLM写已决定发布的正文。词表倾向分数进入兴趣推荐；随机抽样和时序排序不按该分数选帖，故前两臂数值一致不能证明语言能力相同。</p><p>兴趣W12 Agent57正文倾向先变：营销3.4826→3.2178、教育0.4975→0.7426。W13 Agent80教育标签1/10→2/10，效用0.8883→1.1117，两侧均发言；Agent90首次发言翻转，效用1.0401→0.8764，由发布转沉默。后续曝光、供给及累积疲劳可传播差异；这不是单个词导致全部结果的因果识别。<a href="data/mechanism_trace.json">可追踪链条</a>。</p><h2 id="conclusions">速度、结论与适用边界</h2><p>北京时间10月16日13:51:50–19:35:25，新批含调度343.59分钟，距12小时上限约6小时16分。旧s0三臂同口径176.34分钟，新批约1.95倍耗时；旧引擎各57.97/58.48/59.37分钟，合计175.83。跨时段服务负载、SDK及调度混合，不能认定固有模型速度下降1.95倍，价格未核实。<a href="data/runtime_comparison.json">原始时间与计算</a>。</p><div class="limitations"><p><strong>当前100人固定机制与输入的服务替换检查，主要制度排序保持，正文更短但质量未证等价，兴趣反馈局部变化。</strong>新每制度仅一次，无跨重复显著性推断、总体幻觉率或能力排名；仿真不直接证明现实平台因果。</p><p>请求cuc/deepseek返回deepseek-v4.1-flash及-2/-3/-4；旧请求deepseek-v4-1-flash-260910返回deepseek-v4-1-flash。别名和后台不确定，不能假定底层模型不同。本轮未回答500/1000人的可信度与成本。</p></div><h2 id="appendix">来源、复算与交付</h2><ul><li><a href="extract_comparison.py">提取脚本</a> · <a href="data/source_index.json">来源/SHA256/复算命令</a> · <a href="data/paired_metric_differences.csv">配对差值</a> · <a href="data/institution_contrasts.csv">制度差值</a></li><li><a href="data/weekly_metrics.csv">逐周指标</a> · <a href="data/late_author_participation.csv">五类参与率</a> · <a href="data/quality_summary.json">原始/发布质量统计</a></li><li><a href="data/sample_selection.json">抽样规则</a> · <a href="data/paired_text_samples.jsonl">正文和实际feed</a> · <a href="data/supplementary_anomaly_samples.jsonl">补充异常</a></li><li><a href="report_zh.md">中文Markdown</a> · <a href="report_en.html">English copy</a> · <a href="synthesis_report_zh.html">综合判断</a> · <a href="assets/figure_01_model_comparison.svg">可编辑SVG</a></li></ul><footer>本run候选比较已交付；正式claims结果确认/发布签名仍未批准，不冒充流水线完成。此边界不撤销已核验的数据与分析。未改正式资产、root.env或主区流水线；不自动采用、归档、commit、push。</footer>'''
en_html='''<h1>CUC service replacement: preserved ordering with text and feedback differences</h1><p class="muted">AgentSociety · Run-scoped candidate analysis · 2026-10-16 · H4 / isolated namespace 4_cuc</p><p class="lead">In this frozen100-Agent check, late meme-author participation, Agent meme supply and meme exposure remain <strong>chronological &gt; interest &gt; random</strong>. Random/chronological numerical identity has a structural explanation. Shorter text and factual, role-boundary and processing issues preclude a claim of model equivalence.</p><nav><a href="#data">Design</a><a href="#findings">Findings</a><a href="#quality">Text quality</a><a href="#mechanism">Feedback</a><a href="#conclusions">Runtime &amp; limits</a><a href="#appendix">Evidence</a></nav><div class="metrics"><div class="metric"><strong>3 / 3</strong>regimes;693 steps each</div><div class="metric"><strong>603</strong>posts;3300 unique actions</div><div class="metric"><strong>0</strong>body technical failures/fallbacks</div><div class="metric"><strong>343.59 min</strong>batch elapsed including dispatch</div></div><h2 id="data">Design, data and denominators</h2><p>100 Agents,11 weeks W12–W22, one run per regime. No explicit environment or model seed; the environment defaults to0. Primary paired baselines are old experiment_2 random_s0,chronological_s0,interest_s0 whose frozen inputs were reused. Old s1/s2 describe an existing range only.</p><p>Each regime completed693 steps and1100 unique Agent-week actions, with matching environment/Agent publication ledgers. Processes exited.603 body requests,0/330 additional requests,3 local age-check edits; the3630 cap excludes SDK observe/statistics and the probe. Three recovered SDK timeouts are separate from zero body failures.</p><div class="eda-panel"><p>Official EDA confirms11 environment rows and1100 Agent rows for interest,1000 feed slots/week. Full comparisons use ReplayReader,ENV_STATE and Agent ledgers.<a href="data/eda_quick_stats.md">EDA</a> · <a href="data/source_index.json">Provenance</a> · <a href="data/integrity.json">Integrity</a>.</p><!-- EDA_INTERACTIVE_BEGIN --><!-- EDA_INTERACTIVE_END --></div><p>Fixed author type defines participation/supply; feed pool labels define exposure; lexical assigned_type is only a text diagnostic, not semantic gold labels. Late participation divides speaking Agent-weeks by type population×4 (meme19×4=76). Agent supply divides by all Agent posts; exposure includes all external/Agent slots (1000 W13;4000 late). Late ratios pool counts, not unweighted weekly shares.</p><h2 id="findings">Preserved direction, local interest changes</h2>MAIN_HTML<p>W13 is the prespecified event-response week, not a presumed global peak; interest mourning exposure peaks at W15. The<a href="data/weekly_comparison.md">11-week appendix</a>contains mourning/meme supply and exposure for all regimes.</p><p>Random and chronological agree on11-week environmental scientific replay fields (excluding time metadata), selected numerical decision fields across1100 Agent-weeks, and ordered feed keys/labels. Agent text in those feeds differs, so complete prompts are not held fixed. Interest has815 Agent-weeks with changed checked decision fields and999 changed feed-key sequences, but73 speaking flips; net posts rise by3. This is an in-mechanism service replacement check, not an identical-prompt offline model benchmark.</p><p>Interest late Agent meme share rises5.66 points because meme posts34→35 and all Agent posts54→51; exposure rises0.10 points. New W13 mourning exposure28.1% is below the old28.5%–37.0% range; new late Agent meme share68.63% exceeds62.96%–67.21%. Not all changes lie within the old range, whose three-run extrema are not a confidence interval.</p><figure><img src="assets/figure_01_model_comparison.png" alt="Interest trajectories and late regime ordering"><figcaption>Figure1: upper panels show interest mourning exposure, Agent meme share and meme exposure over11 weeks; lower panels retain late regime ordering. Denominators and old-solid/new-dashed conventions are shown.</figcaption></figure><h3>Late participation by five fixed author types</h3><p>Old s0→new; speaking Agent-weeks/all opportunities, not unique individuals or semantic text classes.</p>PART_HTML<h2 id="quality">Generation completes; equivalence is not established</h2>QUALITY_HTML<p>Old paired first generations:600, one empty then rewritten. New:603, none empty or provider-refused; no paid body rewrite or fallback. Age checks edited3/603=0.50%, but chronological77/W13 plausibly states its persona-consistent own age38 and was overfiltered. Two interest58,85/W13 cases introduce unsupported subject ages. Check-hit rate is not hallucination rate.</p><p>Published medians are shorter in all regimes. NFKC normalization/whitespace removal finds zero within-regime exact duplicate excess, not zero formulaic or semantic repetition.>300 characters diagnoses a prompt preference; the implementation limit is400. Statistics use final ENV publications; raw responses are retained separately.</p><p>The fixed audit uses SHA256 ordering of common speaking Agent-weeks, selecting at most two pairs per regime×five types×W12/middle/late cell:59 pairs,118 texts. Each side is checked against actual prompt,persona,raw/final text and feed; sparse cells are not fabricated. Supplementary anomalies are excluded from59. This assistant audit has no independent human gold labels or paid judge and cannot estimate a population hallucination rate. Only15 of59 full messages pairs are identical;44 differ. Random/chronological prompts can change through recirculated text,while interest also changes feed keys.</p><p>All sampled texts respond to seen material; none declares death prematurely without seen basis. Waiting for confirmation is not a model refusal. Unsupported raw subject ages are0/59 old versus2/59 new; both final sets have0/59. Traceable examples:</p><ul><li><code>interest:58:2026-W13</code>new“才41岁”is unsupported and locally deleted; old conditions on“若属实”.</li><li><code>interest:85:2026-W13</code>new“才四十出头吧”is deleted, leaving“愣了一下。吧，孩子还那么小”: a raw grounding issue plus a processing defect.</li><li>Supplementary<code>new:chronological:77:2026-W13</code>probably loses a persona-consistent self-description;86/W20 has432 raw characters with inter-character spaces and a399-character publication ending“建 议 出”.</li><li><code>random:22:2026-W19</code>addresses its own post as“@22说的”;91/W17 adds family details resembling another user's background. Role/source boundaries differ from subject-event factual errors.</li><li>Old<code>random:19:2026-W17</code>strengthens easy-pass/600-question material into“600题保过”;<code>interest:61:2026-W13</code>turns a notice date into personal viewing memory. Old is not error-free ground truth.</li><li>New chronological87/32 W12 share a25-character opening; both versions have formulaic advertising/memes. New interest4/W21“火车头/新闻学”is source-grounded humor, not mechanically a factual hallucination.</li></ul><p>Shorter is not inherently worse; removing an age does not ensure naturalness/completeness. The check supports task completion alongside quality concerns.<a href="data/text_review_findings.md">Full review</a> · <a href="data/text_review_annotations.jsonl">Pair annotations</a>.</p><h2 id="mechanism">How text enters feedback</h2><p>The environment decides speaking from observed feed labels/frozen parameters; the LLM writes the body. Lexical tendencies enter interest recommendations, whereas random/time ordering do not select by them. Numerical identity is therefore not evidence of equal language ability.</p><p>Earliest trace: interest Agent57 W12 changes marketing3.4826→3.2178 and education0.4975→0.7426. W13 Agent80 education slots1/10→2/10 and utility0.8883→1.1117; both speak. Agent90 is the first speaking flip,utility1.0401→0.8764,publication→silence. Exposure,supply and fatigue can propagate differences; this does not isolate a single-word cause.<a href="data/mechanism_trace.json">Trace</a>.</p><h2 id="conclusions">Runtime and warranted interpretation</h2><p>New batch:October16,13:51:50–19:35:25 Beijing time,343.59min including dispatch,~6h16m remaining under the12h guard. Old s0 same batch interval176.34min; new takes~1.95×. Old engine times57.97/58.48/59.37min,total175.83. Different execution times,service load,SDK and dispatch prevent intrinsic-throughput attribution; price is unverified.<a href="data/runtime_comparison.json">Timing sources</a>.</p><div class="limitations"><p><strong>The principal ordering persists in this frozen100-Agent replacement check; text is shorter with quality concerns and local interest-feedback changes.</strong> One new run/regime does not support repeated-run significance,population hallucination rates or broad capability ranking. Simulation evidence does not directly establish real-platform causality.</p><p>Requested cuc/deepseek returned deepseek-v4.1-flash and-2/-3/-4; old deepseek-v4-1-flash-260910 returned deepseek-v4-1-flash. Backend/alias identity is uncertain; distinct foundation models are not assumed. Scaling credibility/cost to500/1000 remains unresolved.</p></div><h2 id="appendix">Evidence and reproduction</h2><ul><li><a href="extract_comparison.py">Extraction</a> · <a href="data/source_index.json">Source hashes/commands</a> · <a href="data/paired_metric_differences.csv">Paired deltas</a> · <a href="data/institution_contrasts.csv">Regime contrasts</a></li><li><a href="data/weekly_metrics.csv">Weekly metrics</a> · <a href="data/late_author_participation.csv">Participation</a> · <a href="data/quality_summary.json">Quality statistics</a></li><li><a href="data/sample_selection.json">Sampling rules</a> · <a href="data/paired_text_samples.jsonl">Actual feeds/text</a> · <a href="data/supplementary_anomaly_samples.jsonl">Supplementary anomalies</a></li><li><a href="report_en.md">English Markdown</a> · <a href="report_zh.html">中文主报告</a> · <a href="synthesis_report_en.html">Synthesis</a> · <a href="assets/figure_01_model_comparison.svg">Editable SVG</a></li></ul><footer>Candidate run comparison delivered; formal claims/release approvals remain unsigned and no pipeline completion is claimed. This procedural boundary does not undo verified evidence. No formal asset,root.env or main pipeline changes; no automatic adoption,archival,commit or push.</footer>'''
for lang,body,headers,qh,ph,title in [('zh',zh_html,main_headers_zh,quality_headers_zh,part_zh,'CUC服务替换比较'),('en',en_html,main_headers_en,quality_headers_en,part_en,'CUC service replacement comparison')]:
 body=body.replace('MAIN_HTML',ht_table(headers,main_rows)).replace('QUALITY_HTML',ht_table(qh,quality_rows)).replace('PART_HTML',ht_table(ph,part))
 (A/f'report_{lang}.html').write_text(f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>{style}</head><body><main>{body}</main></body></html>')
# 单范围综合同时讨论研究目的、结果一致与张力、生成质量进入机制的条件以及适用边界。
syn_zh='''# 本轮服务替换的综合判断

本轮想回答“换用预期成本较低的服务后，原实验结论会不会改变”，不是检验500或1000人的人口规模效应。当前100人、11周、三制度各一次的证据表明：后期玩梗作者参与、Agent供给份额、曝光都保持时序>兴趣>随机，W13事件反应的悼念作者参与仍为时序=兴趣>随机。数值方向具有本轮条件内的稳健性。

一致性与张力同时存在。随机/时序正文不同，但帖子键/标签和数值轨迹相同，因为它们不依正文倾向选择推荐。兴趣制度会读取正文词表倾向，所以实际feed和73个发言决策发生分歧；后期Agent玩梗份额62.96%→68.63%，曝光19.875%→19.975%。W13兴趣悼念曝光28.1%以及后期Agent玩梗份额都超出旧三重复极值。主要排序未变不等于所有结果不变，也不等于变化必在旧波动内。

正文任务全部完成，但原始与发布质量要分开：新603次首次生成没有空输出或接口拒答；三次本地年龄门控包含两次无源人物年龄与一次可能误删自述。59对固定抽查中两版大多能贴合所见，旧版也有来源强化；新原始无源人物年龄2/59，发布后删净，但残句、逐字空格后截断、自他混淆和套式话语均需保留为质量限制。该审读是助手上下文判断，不是人类金标或全量幻觉率。

对当前研究，较谨慎的可用判断是：这套服务足以完成本批，并维持主要制度差值方向，可作为候选服务继续评估；本轮不批准自动替换正式配置或扩大人数。它比旧s0同批间隔耗时约1.95倍，价格和底层模型映射均未核实，不能据此确认便宜或进行能力排名。

新每制度仅一次，不能做跨重复显著性推断；100人结论不自动外推500/1000人或现实平台。详细分母、峰位、数据来源、复算和例子见[中文主报告](report_zh.md)。本综合属于本run候选交付；正式claims和发布门禁仍未签，不声称流水线完成。没有新增LLM仿真、收费裁判、正式采用、归档、commit或push。
'''
syn_en='''# Synthesis of the service replacement check

The question is whether replacing the generation service changes existing findings; this batch does not test500/1000-Agent population scaling. With100 Agents,11 weeks and one run per regime, late meme-author participation,Agent supply share and exposure retain chronological>interest>random. W13 event-response mourning participation retains chronological=interest>random. This is conditional robustness within the current configuration.

Agreement and tension coexist. Random/chronological text differs but feed keys/labels and numerical trajectories agree because those recommendation rules do not select using text tendencies. Interest uses lexical tendencies,changes actual feeds and73 speaking decisions; late Agent meme share rises62.96%→68.63% and exposure19.875%→19.975%. New interest W13 mourning exposure28.1% and late Agent meme share both lie outside old three-run extrema. Preserved ordering does not mean unchanged outcomes or changes necessarily within historical variation.

All generation tasks complete, but raw and published quality differ. New603 first responses have no empty output/provider refusal. Three local age-check edits include two unsupported subject ages and one probable overfilter of self-description. The fixed59-pair audit finds context-responsive writing on both sides and source amplification in old text too. New unsupported raw subject ages are2/59 and removed in publication,while residual fragments,spacing/truncation,self-other confusion and formulaic phrasing remain limitations. This contextual assistant audit is not human gold labels or a population hallucination estimate.

For this study,the candidate service completes the batch and retains principal contrast directions; further evaluation is reasonable,but this report does not authorize automatic formal replacement or scale expansion. Batch elapsed time is about1.95× old s0. Price and backend identity remain unverified,so neither lower cost nor broad model superiority is established.

One new run per regime does not support repeated-run significance inference.100-Agent simulation findings do not automatically extrapolate to500/1000 Agents or real platforms. See the[full English report](report_en.md)for denominators,peaks,provenance,reproduction and examples. This is run-scoped candidate delivery; formal claims/release sign-offs remain unsigned and pipeline completion is not asserted. No additional LLM simulation,paid judge,formal adoption,archival,commit or push occurred.
'''
for lang,body in [('zh',syn_zh),('en',syn_en)]:
 (A/f'synthesis_report_{lang}.md').write_text(body)
 # 综合HTML亦使用独立段落组织，非MD转换。
 synbody={'zh':'<h1>综合判断：方向稳健与机制敏感性并存</h1><p class="lead">本轮候选服务完成100人、11周三制度生成，后期玩梗排序保持时序&gt;兴趣&gt;随机；W13悼念作者参与保持时序=兴趣&gt;随机。此结论有明确配置边界。</p><h2>证据的一致与张力</h2><p>随机/时序数值一致，因为排序不使用正文倾向；正文及完整提示内容仍不同。兴趣根据正文倾向回流，73个发言Agent周翻转，后期玩梗供给份额+5.66个百分点，曝光+0.10个百分点。新W13悼念曝光28.1%和后期Agent玩梗份额68.63%在旧三重复范围外。主要排序保持不等于变化可忽略。</p><h2>生成质量怎样限制研究解释</h2><p>新603次首次生成无空输出/接口拒答，三次年龄门控包含两条无源人物年龄与一条可能误删自述。59对上下文审读区分原始和发布质量；修复后仍有残句、截断、自他混淆、套式表达。旧也有来源强化。数值不变不能证明语言等价；助手审读不能当人类金标或总体幻觉率。</p><h2>当前能作的判断</h2><p>该服务可完成本批且未反转主要制度差值方向，可保留为候选；不能自动替换正式配置或扩大人数。新耗时343.59分钟，旧s0同批间隔176.34分钟，约1.95倍；跨时段不能归因固有吞吐。价格、后台模型映射未核实。</p><div class="limitations"><p>新各制度仅一次，不做跨重复显著性、能力排名；100人仿真不直接外推500/1000人或现实平台。</p></div><p><a href="report_zh.html">主报告、指标分母和来源</a> · <a href="synthesis_brief.json">综合范围与证据索引</a></p><footer>本run候选交付，正式claims/发布签名仍未签；未新增实验、付费裁判、正式采用、归档或Git提交。</footer>', 'en':'<h1>Synthesis: robust direction with mechanism sensitivity</h1><p class="lead">The candidate service completes100 Agents,11 weeks and three regimes. Late meme ordering remains chronological&gt;interest&gt;random; W13 mourning participation remains chronological=interest&gt;random,conditional on the configuration.</p><h2>Agreement and tension</h2><p>Random/chronological numerical identity reflects recommendation rules that do not use text tendencies; text and full prompt contents still differ. Interest feedback changes73 speaking Agent-weeks,late Agent meme share+5.66 points and exposure+0.10 points. W13 mourning exposure28.1% and late Agent meme share68.63% exceed old three-run extrema in opposite directions. Preserved ordering is not negligible change.</p><h2>How quality constrains interpretation</h2><p>All603 new first responses are nonempty/non-refused. Three age-check edits include two unsupported subject ages and one probable self-description overfilter. The59-pair contextual audit separates raw/final quality: fragments,truncation,self-other confusion and formulaic phrasing remain. Old text also amplifies sources. Numerical identity is not language equivalence; assistant review is not human gold labels or a population hallucination rate.</p><h2>Warranted use</h2><p>The service completes this batch and preserves principal contrast directions; it remains a candidate,without automatic formal replacement or population expansion. New elapsed343.59min versus old s0 batch interval176.34min is~1.95×; different execution periods prevent intrinsic-throughput attribution. Price and backend mapping are unverified.</p><div class="limitations"><p>One new run/regime does not support repeated-run significance or capability ranking;100-Agent simulations do not directly extrapolate to500/1000 or real platforms.</p></div><p><a href="report_en.html">Main report,denominators and sources</a> · <a href="synthesis_brief.json">Scope and evidence</a></p><footer>Candidate run delivery;formal claims/release signatures remain unsigned. No added simulation,paid judge,formal adoption,archival or Git commit.</footer>'}[lang]
 (A/f'synthesis_report_{lang}.html').write_text(f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Synthesis</title>{style}</head><body><main>{synbody}</main></body></html>')
write_json(A/'report_outline.json',{'hypothesis_id':'4_cuc','sections':[{'id':x,'title':t} for x,t in [('overview','服务替换比较'),('data','设计、数据与指标分母'),('findings','制度方向与局部变化'),('quality','原始与发布正文质量'),('mechanism','正文进入兴趣回流'),('conclusions','速度与适用边界'),('appendix','来源与复算')]],'figures':[{'asset':'figure_01_model_comparison.png','caption':'兴趣11周轨迹局部变化，但后期三制度玩梗排序保持；各口径分母明确。','finding_number':1}]})
write_json(A/'analysis_summary.json',{'summary':'当前冻结100人服务替换中主要制度排序保持，正文更短但质量未证明等价，兴趣回流局部改变。','key_findings':['随机/时序所查数值与feed键/标签一致，正文不同。','兴趣73个发言Agent周不同，后期Agent玩梗供给份额+5.66pp，曝光+0.10pp。','固定59对原始无源人物年龄旧0新2，最终均0；三次年龄门控含可能误删。','新批343.59min，旧s0同批间隔176.34min，约1.95倍。'],'limitations':'新每制度仅一次；别名/后台不确定；助手审读非人类金标，不能外推总体幻觉率；仿真不直接证明现实因果；未验证价格或人口扩大；正式claims与发布签名未完成。','evidence_index_path':'data/source_index.json','formal_release_approved':False,'status':'candidate_comparison_delivered'})
used=['report_zh.md','report_en.md','data/paired_metric_differences.csv','data/institution_contrasts.csv','data/late_author_participation.csv','data/quality_summary.json','data/text_review_findings.md','data/text_review_annotations.jsonl','data/mechanism_trace.json','data/runtime_comparison.json','data/source_index.json']
write_json(A/'synthesis_brief.json',{'synthesis_question':'服务替换后生成质量与主要实验结论是否改变，正文变化如何进入数值回流？','scope_hypothesis_ids':['4_cuc'],'research_hypothesis_id':'4','source_artifacts':[str(A/u) for u in used],'comparison_mode':'within_hypothesis_service_replacement','formal_release_approved':False,'limitations':['one new run per regime','backend identity unknown','contextual assistant audit, not human gold standard']})
for name in ['report_zh.md','report_en.md','report_zh.html','report_en.html','report_outline.json','analysis_summary.json']:
 shutil.copy2(A/name,P/name)
for name in ['synthesis_report_zh.md','synthesis_report_en.md','synthesis_report_zh.html','synthesis_report_en.html','synthesis_brief.json']:
 shutil.copy2(A/name,S/name)
# 综合位于专属synthesis根目录，调整链接回报告位置。
for path in S.glob('synthesis_report_*'):
 text=path.read_text()
 for lang in ['zh','en']:
  text=text.replace(f'(report_{lang}.md)',f'(../presentation/hypothesis_4_cuc/report_{lang}.md)').replace(f'href="report_{lang}.html"',f'href="../presentation/hypothesis_4_cuc/report_{lang}.html"')
 path.write_text(text)
# 主报告目录仅有data/assets/charts子目录；复算脚本和候选综合通过相对路径回run分析入口。
for path in P.glob('report_*'):
 if path.suffix not in ['.md','.html']: continue
 text=path.read_text()
 for name in ['extract_comparison.py','synthesis_report_zh.md','synthesis_report_en.md','synthesis_report_zh.html','synthesis_report_en.html']:
  text=text.replace(f'({name})',f'(../../../model-comparison-analysis/{name})').replace(f'href="{name}"',f'href="../../../model-comparison-analysis/{name}"')
 path.write_text(text)
for name in ['data/eda_quick_stats.md']:
 if (P/name).exists(): shutil.copy2(P/name,A/name)
# 引用的数据材料复制到隔离presentation，以便报告相对链接离线打开。
for path in (A/'data').glob('*'):
 if path.is_file(): shutil.copy2(path,P/'data'/path.name)
manifest={'status':'candidate_comparison_delivered','formal_release_approved':False,'files':[{'path':str(p.relative_to(A)),'purpose':('Chinese primary report' if p.name=='report_zh.html' else 'analysis deliverable')} for p in sorted(A.glob('*')) if p.is_file() and p.suffix in ['.md','.html','.json','.py']],'raw_evidence_index':'data/source_index.json','workspace_presentation':str(P),'workspace_synthesis':str(S)}
write_json(A/'artifact_manifest.json',manifest);shutil.copy2(A/'artifact_manifest.json',P/'artifact_manifest.json')
print('Bilingual Markdown/native HTML, summaries, synthesis and isolated workspace copies written.')
