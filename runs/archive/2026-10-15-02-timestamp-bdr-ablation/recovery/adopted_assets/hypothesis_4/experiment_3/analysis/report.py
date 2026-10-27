"""将离线配对表与人工撰写的解释整理成双语Markdown/原生HTML，不调用模型。"""
from pathlib import Path
import json,html,shutil,hashlib
import pandas as pd
import numpy as np
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[1];P=ROOT/'presentation/hypothesis_4/timestamp_bdr_v1';D=P/'data';A=P/'assets'
metrics=pd.read_csv(D/'run_metrics.csv');pairs=pd.read_csv(D/'paired_differences.csv');stats=pd.read_csv(D/'paired_summary.csv');weekly=pd.read_csv(D/'weekly_by_type.csv');dec=pd.read_csv(D/'decisions.csv');ex=pd.read_csv(D/'weekly_exposure_by_cohort.csv')

def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def mdtable(headers,rows):return '| '+' | '.join(headers)+' |\n|'+ '|'.join('---' for _ in headers)+'|\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in rows)
def htable(headers,rows):return '<div class="table-scroll"><table><thead><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def srow(cond,key):return stats[(stats.condition==cond)&(stats.metric==key)].iloc[0]

primary=[]
for name,cond,key,scale,unit in [('B','no_b','late_posts_per_week',1,'帖/周'),('D','no_d','late_meme_speak_rate',100,'%'),('R','no_r','mid_speak_rate',100,'%')]:
 x=srow(cond,key);primary.append([name,f'{x.full_mean*scale:.2f}',f'{x.ablation_mean*scale:.2f}',f'{x.delta_mean*scale:+.2f}',f'[{x.delta_min*scale:+.2f}, {x.delta_max*scale:+.2f}]'])
seed_rows=[]
for seed in range(3):
 row=[seed]
 for cond,key,scale in [('no_b','late_posts_per_week',1),('no_d','late_meme_speak_rate',100),('no_r','mid_speak_rate',100)]:
  x=pairs[(pairs.condition==cond)&(pairs.seed==seed)&(pairs.metric==key)].iloc[0];row.append(f'{x.full*scale:.2f} → {x.ablation*scale:.2f} ({x.delta*scale:+.2f})')
 seed_rows.append(row)
run_rows=[]
for seed in range(3):
 row=[seed]
 for cond in ['full','no_b','no_d','no_r']:
  x=metrics[(metrics.condition==cond)&(metrics.seed==seed)].iloc[0];row.append(f'{int(x.posts)} / {int(x.requests)}')
 run_rows.append(row)
late_by_type=weekly[weekly.week>='2026-W19'].groupby(['condition','agent_type']).posted.sum().unstack().div(3)
late_rows=[]
for cond in ['full','no_b','no_d','no_r']:
 z=metrics[metrics.condition==cond];late_rows.append([cond,*[f'{late_by_type.loc[cond,k]:.2f}' for k in ['meme','mourning','education','marketing','other']],f'{z.late_meme_author_share.mean()*100:.2f}%'])
late=dec[dec.week>='2026-W19'];state=late[late.agent_type=='meme'].groupby('condition')[['cum_own','R','D']].mean();state_rows=[]
for cond in ['full','no_b','no_d','no_r']:
 z=metrics[metrics.condition==cond];state_rows.append([cond,f'{z.late_meme_exposure_meme.mean()*100:.2f}%',f'{state.loc[cond,"cum_own"]:.2f}',f'{state.loc[cond,"R"]:.3f}',f'{state.loc[cond,"D"]:.3f}',f'{z.late_meme_speak_rate.mean()*100:.2f}%'])
# 按实际同一Agent×周连接；确认全矩阵的时钟/机会配对，不将周当重复样本。
full=dec[dec.condition=='full'].set_index(['seed','agent_id','week']);pairchecks=[]
for cond in ['no_b','no_d','no_r']:
 v=dec[dec.condition==cond].set_index(['seed','agent_id','week']);assert v.index.equals(full.index) or set(v.index)==set(full.index)
 joined=v[['acted_at','agent_type']].join(full[['acted_at','agent_type']],lsuffix='_ab',rsuffix='_full');assert all(joined.acted_at_ab==joined.acted_at_full) and all(joined.agent_type_ab==joined.agent_type_full)
 pairchecks.append({'condition':cond,'paired_opportunities':len(joined),'actual_clock_and_author_type_equal':True})
# B在R=1时系数为零：仅审计已发生W12记录的代数等价，不生成新仿真。
w12=[]
for seed in range(3):
 a=dec[(dec.condition=='full')&(dec.seed==seed)&(dec.week=='2026-W12')].sort_values('agent_id');b=dec[(dec.condition=='no_b')&(dec.seed==seed)&(dec.week=='2026-W12')].sort_values('agent_id')
 w12.append({'seed':seed,'max_abs_U_difference':float(np.max(np.abs(a.u.to_numpy()-b.u.to_numpy()))),'all_R_one':bool((a.R==1).all() and (b.R==1).all()),'posted_equal':bool((a.posted.to_numpy()==b.posted.to_numpy()).all())})
# 按声明的条件确定性选取三个真实分叉案例；不是随机样本，不用于估计效应。
alltexts=json.loads((D/'generated_examples_all.json').read_text());lookup={(x['condition'],x['seed'],x['agent_id'],x['week']):x for x in alltexts};examples=[]
for role,cond,kind,window,fullposts,abposts in [('B','no_b','marketing',list(range(19,23)),1,0),('D','no_d','meme',list(range(19,23)),1,0),('R','no_r','mourning',list(range(14,19)),0,1)]:
 f=dec[(dec.condition=='full')&(dec.agent_type==kind)&dec.week.isin([f'2026-W{n}' for n in window])];ab=dec[dec.condition==cond]
 j=f.merge(ab,on=['seed','agent_id','week'],suffixes=('_full','_ab'));j=j[(j.posted_full==fullposts)&(j.posted_ab==abposts)].sort_values(['seed','week','agent_id']);assert len(j)
 v=j.iloc[0];sample=dict(role=role,condition=cond,seed=int(v.seed),agent_id=int(v.agent_id),agent_type=kind,week=v.week,selection_rule='first by seed/week/agent_id satisfying the declared posted divergence; illustrative, not representative',records=[])
 for c in ['full',cond]:
  z=dec[(dec.condition==c)&(dec.seed==v.seed)&(dec.agent_id==v.agent_id)&(dec.week==v.week)].iloc[0];text=lookup.get((c,int(v.seed),int(v.agent_id),v.week),{}).get('content')
  sample['records'].append(dict(condition=c,speak=bool(z.speak),posted=bool(z.posted),U=float(z.u),D=float(z.D),R=float(z.R),B=float(z.B),threshold=float(z.threshold),margin=float(z.margin),content=text,source_file=z.source_file,source_sha256=z.source_sha256,record_index=int(z.record_index),assigned_type=z.assigned_type if isinstance(z.assigned_type,str) else None))
 examples.append(sample)
dump(D/'illustrative_examples.json',examples);dump(BASE/'checks/pairing_and_identity.json',{'paired_clock_checks':pairchecks,'B_W12_identity_observed':w12,'note':'observed-record audit, not additional model or LLM runs'})
summary={'scope':'timestamp-interest, 3 paired seeds, Full + no_b/no_d/no_r, 12 runs','primary_metrics':primary,'key_findings':['B retains late supply; removing B lowers late mean by 7.00 posts/week in every seed.','D response shapes selective timing; removing it lowers late meme-author speaking by 30.70 pp although early and total author supply rises.','R decay/return-to-B limits overall post-event activity; no R raises W14–W18 speaking by 30.07 pp.','Higher meme-author share after no B coexists with lower absolute meme-author output; author types are not semantic labels.'],'limitations':'n=3 with same population/schedule; all effects conditional on frozen timestamp-interest and params; closed-loop total changes, not additive or direct effects; R=1 also removes B weight; reused Full is a separate generation batch and API routes/returned model identifiers differ; no human semantic gold or extra independent model review.','evidence_index_path':'data/evidence_index.json','analysis_release':'user-approved and adopted; no independent model review or formal harness sign-off','additional_LLM_calls':0}
dump(D/'analysis_summary.json',summary)

zh=[
('范围与数据',[
'本分析只回答冻结的timestamp兴趣制度内B、D、R的作用。Full为主实验timestamp_v1_interest_s0/s1/s2，九次消融使用相同seed对应的外部样本、人口、门槛、行动表和科学配置；规范化操作路径后，只差指定组件参数。三个seed实际使用同一人口和行动表，不能视为三个人口样本。',
'12次均完成693步、100人×11周=1100次机会；合计13,200次机会，3,309次speak=true且全部成功发布，9,891次below_threshold，空feed及行动/生成/发布失败均为0。九次消融发布2,652条、外层模型请求2,657次；本轮分析没有新增模型请求。已逐run用官方CLI查询replay，并与环境逐周计数及每个Agent的决策记录交叉核对。',
'配对单位是seed。预设三项主指标：B用W19–W22每周成功发布数（先在run内取4周均值）；D用W19–W22玩梗型作者speak=true / 76次机会；R用W14–W18全体speak=true / 500次机会。所有差值为消融−同seed Full。只有3对，列实际差值与最小–最大，不报告显著性、置信区间，也不将周或行动当作独立重复。',
'完整模型与消融分批运行；本run中API从coding/v3变为plan/v3，请求模型固定deepseek-v4-1-flash-260910，但Full及较早消融返回deepseek-v4-1-flash，较晚消融返回完整版本ID。Full计划只保存服务host，未保存可完整核查的API路径。相同请求模型与冻结代码/输入不证明后台模型和随机生成完全一致。这是复用对照的剩余限制，不能通过同seed标签消除。']),
('预设指标的配对结果',[
'三个预设指标的方向在三个seed中一致。B的晚期供给均值由13.83降至6.83帖/周；去D后晚期玩梗型作者发言率由47.81%降至17.11%；去R衰减后W14–W18整体发言率由19.13%升至49.20%。下表列出均值及三个配对差值，百分比之差使用“百分点”。']),
('B：维持退潮后的表达底座，也保留非玩梗供给',[
'去B后的晚期总供给下降7.00帖/周，三个seed的差值为-7.00、-7.75、-6.25。晚期每run四周内，非玩梗型作者供给从平均19.00条变为0；玩梗型作者也从36.33条降至27.33条。其晚期份额却由65.61%升至100%。因此，“份额更高”在这里来自其他类型清零，不能写成玩梗型作者产量增加。',
'这与U=B+R(D−B)的结构一致：同一状态下Full相对去B的差为(1−R)B，R=1时B权重为零。已发生W12记录的同Agent数值审计显示三个seed均R=1、Full与去B的在记录精度内U和发布决策一致；后续闭环分叉才逐步显现。B不是独立于R的固定加分，其作用随R衰减而增强。']),
('D：调节表达时机及晚期选择性，不是单向增加总量',[
'去D是令D=1，并非令D=0。全窗口总供给反而从Full平均219.00条升到269.33条，但晚期玩梗型作者发言率平均下降30.70个百分点，晚期其成功发帖量从36.33条降至13.00条。它没有消灭晚期发言，不能声称D是所有晚期表达的必要条件。',
'过程证据显示，去D后W12和W13各平均有12位玩梗型作者发言，而Full这两周均为0；去D把表达前移，随后逐步回落。到晚期，该群体实际阅读中的玩梗标签份额由25.18%升至31.18%，累计同类接触均值由2.36升至11.45，R均值从0.835降至0.414，晚期发言却更少。这支持“时序门控—生成反馈—累计接触衰减”的闭环解释；不是对这条中介路径的独立识别，也不能只归结为一个当周D均值。',
'早期“玩梗型/悼念型作者发言”并不自动意味着当时就在发布相应语义的正文。例如去D的W12悼念型作者共发36条，其中现有词表将29条判为marketing、7条判为mourning；这只说明作者标签与词表判类不同，不构成对提前悼念或事实幻觉的人工裁定。']),
('R：约束持续高供给，并参与晚期群体优势的重排',[
'去R衰减令R=1，W14–W18全体发言率提高30.07个百分点，三个seed分别为+31.80、+31.40、+27.00个百分点。晚期全体供给也由13.83升至50.42帖/周；悼念型作者在W18仍平均发13.67条，而Full为0。因而累计同类接触的衰减机制，对本配置下的事件后总体退潮有明显约束作用。',
'去R并未让所有类型都更活跃。晚期玩梗型作者每run四周发帖从36.33降至25.33条，份额由65.61%降至12.56%；其阅读中的玩梗标签份额由25.18%降至13.11%，D均值由1.009降至0.835。持续的教育、营销、悼念及其他作者供给占据了更多空间。这些是闭环联合变化，不能从总量上升推断每一群体都上升。',
'R度量累计同类接触的影响，不是仅按日历时间自动变小。且R=1使U=D，B的系数也同时归零。因此本比较检验的是“衰减并向B回归”的整套机制，不是保持B贡献不变的正交R效应。']),
('能够支持的结论与边界',[
'在这组冻结的timestamp-interest参数和输入下，结果支持：B维持退潮后的供给与一定类型多样性；D响应参与早期抑制和晚期选择性表达；R的接触衰减限制事件后的持续高供给，并与B、D共同改变作者类型构成。三项不能相加为贡献率；单因素消融允许后续feed、接触与正文自然分叉，得到的是闭环总变化。',
'不能据此声称B、D、R在现实世界或所有策展制度中均为必要条件，不能声称偏好发生普遍转变，也不能声称所有玩梗型作者生成文本均被独立确认是玩梗。主图的类型恒为固定作者类型（pool_type）；实际阅读标签和现有四词表assigned_type另行列出，词表也不是人工语义金标。',
'局限还包括n=3、相同人口/调度表、单一interest制度、保留的17条历史池与W13条件化机会安排、B尺度/floor及既有门槛、温度为1的随机生成、分批API/服务端漂移。未新增LLM、同期Full或组合消融，也没有额外模型审稿。用户已确认接受本轮结论并授权落地主工作区；正式数据和复算入口位于experiment_3。没有独立模型审阅或额外LLM调用，不将用户采纳冒充独立审阅。'])]
en=[
('Scope and data',[
'This analysis concerns only the frozen timestamp-interest regime. The three Full runs are timestamp_v1_interest_s0/s1/s2. Each ablation is paired with the same-seed Full and retains its external sample, population, thresholds, action schedule and scientific configuration. After normalizing operational paths, only the designated component parameter differs. All three seeds share the population and action schedule; they are not three population samples.',
'All 12 runs completed 693 steps and 1,100 opportunities each: 13,200 opportunities, 3,309 speaking decisions, all successfully published, and 9,891 below-threshold decisions. There were no empty feeds or action/generation/publication failures. The nine ablations produced 2,652 posts with 2,657 outer provider requests. This analysis added no model calls. Official replay queries were cross-checked against weekly environment counts and individual Agent decision logs.',
'The seed is the paired unit. Prespecified primary measures are: B, mean weekly successful posts over W19–W22, computed within each run first; D, meme-author speaking decisions over 76 opportunities in W19–W22; R, all-author speaking decisions over 500 opportunities in W14–W18. Every difference is ablation minus same-seed Full. With only three pairs, we show the observed differences and min–max range, without significance tests or confidence intervals, and do not treat weeks or opportunities as independent replicates.',
'Full and ablations were generated in separate batches. The ablation API route changed from coding/v3 to plan/v3. Requests pinned deepseek-v4-1-flash-260910, while Full and earlier ablations returned deepseek-v4-1-flash and later ablations returned the full version identifier. The Full runtime plan records the service host but not a fully auditable API path. Matching requested identifiers and frozen code/inputs does not establish identical backend behavior or stochastic text generation. Same-seed pairing does not eliminate this remaining limitation.']),
('Prespecified paired outcomes',[
'All three seeds agree on the direction of each primary contrast. Removing B reduces late mean supply from 13.83 to 6.83 posts/week; removing D response reduces late meme-author speaking from 47.81% to 17.11%; removing R decay raises W14–W18 overall speaking from 19.13% to 49.20%. Rate differences below are percentage points.']),
('B: sustaining late supply and non-meme-author participation',[
'No B reduces late supply by 7.00 posts/week on average; seed differences are -7.00, -7.75 and -6.25. Across the four late weeks, non-meme authors decline from 19.00 posts per run to zero, while meme authors also decline from 36.33 to 27.33. Their share nevertheless rises from 65.61% to 100%. The larger share comes from other types disappearing, not increased absolute meme-author production.',
'The algebra is consistent with this result: at a fixed state, Full minus no B equals (1−R)B, which vanishes at R=1. Auditing observed W12 decisions finds R=1 in every seed, equal U at recorded precision and equal publication decisions. Subsequent feedback produces divergence. B is not a fixed bonus independent of R; its weight increases as R declines.']),
('D: selective timing rather than a one-way supply multiplier',[
'No D sets D=1, not zero. Total full-window supply rises from 219.00 to 269.33 posts/run, yet late meme-author speaking falls by 30.70 percentage points and late meme-author posts fall from 36.33 to 13.00. Late expression remains possible; these results do not establish D as necessary for every late speaking decision.',
'With no D, 12 meme authors speak on average in each of W12 and W13, versus zero in Full. Expression shifts earlier and then declines. By the late window, meme-label exposure among meme authors increases from 25.18% to 31.18%, mean cumulative own-type exposure rises from 2.36 to 11.45, and mean R falls from 0.835 to 0.414 despite less late expression. This supports a feedback interpretation involving timing, generated supply and accumulated-exposure decay; it does not separately identify mediation or reduce the result to a contemporaneous mean D difference.',
'Early speaking by a meme- or mourning-type author does not establish the corresponding text semantics. For example, no-D mourning authors publish 36 W12 posts across seeds; the existing vocabulary classifier assigns 29 to marketing and seven to mourning. This is disagreement between author and vocabulary labels, not a human judgment of premature mourning or factual hallucination.']),
('R: limiting sustained output and reshaping late group advantage',[
'Setting R=1 increases W14–W18 overall speaking by 30.07 percentage points; the three differences are +31.80, +31.40 and +27.00. Late total supply rises from 13.83 to 50.42 posts/week. Mourning authors still publish 13.67 posts on average in W18, versus zero in Full. Accumulated-own-type-exposure decay therefore substantially constrains sustained post-event output in this configuration.',
'Not every author group becomes more active. Late meme-author posts fall from 36.33 to 25.33 per run and their share falls from 65.61% to 12.56%; meme-label exposure among them drops from 25.18% to 13.11%, with mean D falling from 1.009 to 0.835. Education, marketing, mourning and other authors account for much of the sustained supply. These are joint feedback changes, not a direct effect on each group.',
'R responds to cumulative own-type exposure rather than calendar time alone. At R=1, U=D and the coefficient on B also becomes zero. This contrast tests the entire decay-and-return-to-B mechanism, not an orthogonal R effect with B held influential.']),
('Supported conclusions and limits',[
'For these frozen timestamp-interest inputs and parameters, the results support B sustaining late supply and some author-type diversity, D response shaping early suppression and late selective expression, and R decay limiting sustained overall output while interacting with B and D to reshape composition. Contrasts cannot be added as contribution percentages. Single-parameter interventions allow feeds, exposure and text to diverge, so estimates are closed-loop total changes.',
'The evidence does not establish universal necessity in the real world or across curation regimes, general preference change, or independently verified meme semantics for all meme-author text. Stacked charts use fixed author pool_type. Observed feed labels and vocabulary assigned_type are separately reported; vocabulary labels are not human semantic gold.',
'Other limitations include n=3 with a shared population/schedule, one interest regime, the retained 17-post initial history and conditional W13 opportunities, existing B scaling/floor and thresholds, temperature-1 generation, and temporal/API/backend differences. No new LLM, concurrent Full, combined ablation, or additional model review was run. The user accepted these bounded findings and authorized main-workspace adoption; no independent model review was performed.'])]

# 已获用户接受的过程解释：仅由既有轨迹和原始记录核对，不新增实验。
process=json.loads((D/'mechanism_checks.json').read_text())
trajectory=pd.read_csv(D/'mechanism_weekly_mean.csv')
trajectory_rows=[]
for week in sorted(trajectory.week.unique()):
 row=[week.replace('2026-','')]
 for condition in ['full','no_d','no_r']:
  x=trajectory[(trajectory.condition==condition)&(trajectory.week==week)].iloc[0]
  row.append(f'{x.total:.2f} / {x.meme:.2f}')
 trajectory_rows.append(row)
worked=json.loads((D/'mechanism_agent12_records.json').read_text())
worked_rows=[]
for x in worked:
 if x['week']!='2026-W20':continue
 row=x['decision'];c=row['components'];worked_rows.append([x['condition'],x['feed_types'].get('meme',0),c['cum_own'],f"{c['spiral']:.4f}",f"{c['decay']:.4f}",f"{row['u']:.4f}",str(row['speak'])])
zh.insert(5,('D/R的反向总量与群体效应：事实与机制推断分开',[
'已验证事实：去D的全窗口平均总供给由219.00增至269.33条；玩梗型作者在W12–W18由1.33增至61.33条，W19–W22却由36.33降至13.00条。因此增加主要出现在前期，其全窗口产量由37.67增至74.33条，并非全程减少。',
'原始记录显示，seed0 Agent12在W12的同类份额与累计同类接触都为0：Full的D=0.526、U=0.526，低于0.9445门槛；去D固定D=1，U=1并发布。后续去D组累计同类阅读更高、R更低。R累计的是读到的同类内容，不是自己写帖次数；没有提前用完发帖配额，每周仍有19次该类型机会。',
'已验证事实：去R后全窗口玩梗型作者平均产量由37.67降至25.67条，其他四类却由181.33增至495.00条，全体由219.00增至520.67条。晚期Full发言而去R沉默共34次，反向1次，净少33条，即每run少11条；34次损失记录的去R组D全部低于Full。',
'公式性质：本组玩梗型作者门槛均高于B。在已经发言的Full记录上保持D不变、仅令R=1，U会变为D，按公式不会使其转为沉默。因此观察到的损失必须结合路径改变后的D解释，不能归因于去R在同状态下直接压低表达。这是代数性质，不是另跑的反事实实验。',
'机制推断：去D解除早期抑制、改变后续信息流并更早积累接触衰减，同时取消晚期D>1的增益；去R主要维持其他作者类型供给，使玩梗型作者的实际同类阅读和气候响应较弱。记录支持这两条闭环解释，但没有独立识别推荐竞争、正文生成和累计接触各自的净贡献。生成帖的同类标签按作者类型归池，不是人工正文语义金标。']))
en.insert(5,('Opposing aggregate and subgroup effects: verified facts versus inference',[
'Verified: removing D raises total mean output from 219.00 to 269.33. Meme-author output increases from 1.33 to 61.33 over W12–W18 but falls from 36.33 to 13.00 over W19–W22. Its full-window output increases from 37.67 to 74.33: the reduction is late, not throughout the run.',
'In seed0 Agent12 at W12, own-type share and cumulative exposure are zero in both records: Full has D=0.526 and U=0.526 below threshold 0.9445, while no D has D=1 and U=1 and publishes. Later no D accumulates more own-type reading and lower R. R tracks reading exposure, not the author’s own number of posts; the 19 weekly opportunities remain fixed.',
'Verified: no R lowers full-window mean meme-author output from 37.67 to 25.67, but raises other-author output from 181.33 to 495.00 and total output from 219.00 to 520.67. Late paired records contain 34 Full-speaking/no-R-silent cases and one reverse case: a net loss of 33 posts, or 11 per run. All 34 losses have lower D in no R.',
'Algebraic implication: every meme-author threshold exceeds B. At a Full state that already speaks, fixing D and setting R=1 yields U=D and cannot silence that author. Observed losses therefore involve changed D along the feedback trajectory, rather than a same-state direct reduction from removing R. This is an algebraic check, not another counterfactual simulation.',
'Mechanistic inference: no D releases early suppression and changes later feeds and exposure decay while removing late D>1 amplification; no R sustains other authors, with weaker own-type reading and D for meme authors. Records support these feedback explanations without separately identifying recommendation, generated text and cumulative-exposure mediation. Generated pool labels follow author type and are not human semantic gold.']))

captions_zh={
'chart_03_supply_mean_comparison':'图1：三seed均值的作者类型供给。复用指定模板五色、W13事件线和0–80轴；只含Agent成功发布，逐seed单图见附录。',
'chart_04_primary_paired_effects':'图2：预设三指标的同seed配对。每条线连接相同seed，差值均为消融−Full；范围不是置信区间。',
'chart_05_speaking_trajectories':'图3：全体与玩梗型作者的发言率轨迹。粗线为均值、浅带为三个seed实际最小–最大，不是统计置信区间。'}
captions_en={
'chart_03_supply_mean_comparison':'Figure 1. Mean author-type supply over three seeds. Template colors, W13 event line and 0–80 scale are retained; only successful Agent publications are counted. Individual-seed charts are linked below.',
'chart_04_primary_paired_effects':'Figure 2. Prespecified paired measures. Each line connects the same seed; differences are ablation minus Full and ranges are not confidence intervals.',
'chart_05_speaking_trajectories':'Figure 3. Overall and meme-author speaking trajectories. Solid lines are means; bands are the observed three-seed min–max, not confidence intervals.'}
for path in (P/'charts').glob('*'):
    if path.suffix in ('.png','.svg','.pdf'):shutil.copy2(path,A/path.name)

def build(lang,sections,captions):
    cn=lang=='zh';title='B、D、R消融：timestamp-interest同seed配对分析' if cn else 'B, D and R ablations: paired timestamp-interest analysis'
    intro='结论仅限本组冻结仿真；n=3，复用Full的分批与API差异仍可能影响生成反馈。' if cn else 'Conditional simulation evidence; n=3. Batch and API differences in reused Full may affect generated feedback.'
    md=[f'# {title}',intro];body=[f'<header><div class="eyebrow">TIMESTAMP · INTEREST · PAIRED ABLATIONS</div><h1>{title}</h1><p class="lead">{intro}</p><div class="stats"><span><b>12</b> runs</span><span><b>3</b> paired seeds</span><span><b>13,200</b> opportunities</span><span><b>0</b> new LLM calls</span></div></header>']
    for i,(heading,paras) in enumerate(sections):
        md+=['',f'## {i+1}. {heading}','',*sum(([p,''] for p in paras),[])]
        body.append(f'<section id="s{i}"><h2>{i+1}. {heading}</h2>'+''.join('<p>'+html.escape(x)+'</p>' for x in paras))
        table=None
        if i==0:table=(['seed','Full','No B','No D','No R'],run_rows)
        if i==1:
            table=((['指标','Full均值','消融均值','平均差','三个配对差值范围'] if cn else ['Metric','Full mean','Ablation mean','Mean delta','Paired delta range']),[[('B：晚期帖/周' if cn else 'B: late posts/week'),*primary[0][1:]],[('D：晚期玩梗作者发言率(%)' if cn else 'D: late meme-author speaking (%)'),*primary[1][1:]],[('R：事件后全体发言率(%)' if cn else 'R: post-event speaking (%)'),*primary[2][1:]]])
        if table:md+=['',mdtable(*table),''];body.append(htable(*table))
        if i==0:
            note='表中每单元为11周成功发布数 / 外层模型请求数。' if cn else 'Each cell is successful posts / outer provider requests over the full 11-week run.'
            md +=[note,''];body.append('<div class="caption">'+note+'</div>')
        if i==1:
            h=['seed','B：帖/周 / posts/week','D：百分点 / pp','R：百分点 / pp'];md+=['',mdtable(h,seed_rows),''];body.append(htable(h,seed_rows))
        if i==2:
            h=['条件 / condition','Meme','Mourning','Education','Marketing','Other','Meme作者份额 / author share'];md+=['',mdtable(h,late_rows),''];body.append(htable(h,late_rows));note='表：W19–W22四周累计帖数的三seed均值；份额为各run先求份额再取均值。' if cn else 'Table: three-seed mean four-week counts over W19–W22; shares are computed per run before averaging.';md+=[note];body.append('<div class="caption">'+note+'</div>')
        if i==3:
            h=['条件 / condition','Meme标签阅读 / exposure','累计同类 / cum. own','R均值 / mean','D均值 / mean','晚期Meme作者发言 / speaking'];md+=['',mdtable(h,state_rows),''];body.append(htable(h,state_rows))
        if i==5:
            h=['周 / week','Full total / meme','No D total / meme','No R total / meme'];md+=['',mdtable(h,trajectory_rows),''];body.append(htable(h,trajectory_rows))
            note='每格为总发帖数 / 玩梗型作者发帖数，三seed均值。下表为seed0 Agent12在W20的原始记录，门槛均为0.9445；数值显示四位小数。' if cn else 'Each cell is total / meme-author posts, averaged over three seeds. Below: original seed0 Agent12 W20 records; threshold is 0.9445 throughout, values shown to four decimals.'
            md +=[note,''];body.append('<p>'+html.escape(note)+'</p>')
            h=['condition','meme / 10 feed','cum. own','D','R','U','speak'];md+=['',mdtable(h,worked_rows),''];body.append(htable(h,worked_rows))
        fig={1:'chart_04_primary_paired_effects',2:'chart_03_supply_mean_comparison',3:'chart_05_speaking_trajectories'}.get(i)
        if fig:
            caption=captions[fig];md+=['',f'![{caption}](assets/{fig}.png)',caption,''];body.append(f'<figure><a href="assets/{fig}.svg"><img src="assets/{fig}.png" alt="{html.escape(caption)}"></a><figcaption>{caption} <a href="assets/{fig}.svg">SVG</a> · <a href="assets/{fig}.pdf">PDF</a></figcaption></figure>')
        body.append('</section>')
    ap='真实正文分叉例示与证据' if cn else 'Illustrative text divergences and evidence'
    md+=['',f'## {ap}',''];body.append('<section><h2>'+ap+'</h2>')
    for x in examples:
        head=f'{x["role"]}: seed{x["seed"]}, Agent{x["agent_id"]}, {x["week"]} ({x["agent_type"]})';md+=['',f'### {head}',''];body.append('<h3>'+head+'</h3>')
        for z in x['records']:
            text=z['content'] if z['posted'] else ('未发帖（低于门槛）' if cn else 'No post (below threshold)');head=f'{z["condition"]}: U={z["U"]:.4f}, threshold={z["threshold"]:.4f}, R={z["R"]:.4f}, D={z["D"]:.4f}'
            md +=[head,'',f'> {text}',''];body.append('<p class="mechanism">'+html.escape(head)+'</p><blockquote>'+html.escape(text)+'</blockquote>')
    note='以上按预先声明的分叉条件、seed/周/ID排序取首例，非随机样本，不用于估计效应。完整定位和正文见data/illustrative_examples.json；作者类型不替代正文语义。' if cn else 'Examples are the first matching divergence ordered by seed/week/ID, not random samples or effect estimators. Full source coordinates and text are in data/illustrative_examples.json; author type is not text semantics.'
    md +=[note,''];body.append('<p class="caption">'+note+'</p></section>')
    heading='附录：逐seed图与复核材料' if cn else 'Appendix: individual-seed charts and audit files';md+=['',f'## {heading}',''];body.append('<section><h2>'+heading+'</h2>')
    for seed in range(3):
        links=[f'[{c}](assets/chart_01_{c}_s{seed}_agent_supply.png)' for c in ['full','no_b','no_d','no_r']];md.append(f'- seed{seed}: '+' · '.join(links))
        body.append('<p>seed '+str(seed)+': '+ ' · '.join(f'<a href="assets/chart_01_{c}_s{seed}_agent_supply.png">{c}</a>' for c in ['full','no_b','no_d','no_r'])+'</p>')
    files=['paired_differences.csv','paired_summary.csv','run_metrics.csv','weekly_by_type.csv','weekly_exposure_by_cohort.csv','vocab_label_counts.csv','illustrative_examples.json','source_index.json','mechanism_checks.json','mechanism_weekly_by_seed.csv','mechanism_agent12_records.json']
    md+=['']+[f'- [{name}](data/{name})' for name in files];body.append('<ul>'+''.join(f'<li><a href="data/{f}">{f}</a></li>' for f in files)+'</ul></section>')
    foot='用户已接受并授权采用：已落地主工作区；未新增LLM调用或独立模型reviewer，未提交Git。' if cn else 'User-approved analysis adopted in the main workspace; no new LLM calls, independent model review or Git commit.'
    md+=['',foot];body.append('<footer>'+foot+'</footer>')
    (P/f'report_{lang}.md').write_text('\n'.join(md)+'\n')
    css='''*{box-sizing:border-box}body{margin:0;background:#f4f5f7;color:#243244;font:17px/1.8 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1220px;margin:32px auto;background:white;padding:52px 64px;border-top:5px solid #4c72b0}header{border-bottom:1px solid #dce2e9;padding-bottom:30px}h1{font-size:34px;line-height:1.35;margin:10px 0 20px}h2{font-size:25px;line-height:1.4;margin:52px 0 18px;color:#1c3550}h3{font-size:19px}.eyebrow{letter-spacing:.16em;color:#607891;font-size:12px}.lead{font-size:19px;color:#596b7d}.stats{display:flex;gap:35px;flex-wrap:wrap}.stats span{color:#617286;font-size:13px}.stats b{display:block;color:#264d76;font-size:30px}.table-scroll{overflow:auto}table{width:100%;border-collapse:collapse;margin:22px 0;font-size:14px}th,td{text-align:left;border-bottom:1px solid #dde3eb;padding:10px 12px;white-space:nowrap}th{background:#eef3f8;color:#365573}figure{margin:28px 0}img{width:100%;height:auto;display:block}figcaption,.caption{font-size:13px;color:#6a7888;line-height:1.6}blockquote{margin:10px 0 24px;border-left:3px solid #7b9ebc;padding:14px 20px;background:#f5f8fb;font-size:15px}.mechanism{font:13px/1.6 ui-monospace,monospace;color:#526c84}a{color:#376da0;text-decoration:none}a:hover{text-decoration:underline}footer{border-top:1px solid #dce2e9;padding-top:20px;margin-top:45px;font-size:13px;color:#758395}@media(max-width:760px){main{padding:24px 18px;margin:0}h1{font-size:28px}.stats{gap:22px}body{font-size:16px}}@media print{body{background:white}main{margin:0;padding:12px}h2{break-after:avoid}figure,table{break-inside:avoid}}'''
    (P/f'report_{lang}.html').write_text(f'<!doctype html><html lang="{lang}"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>{css}</style><main>'+''.join(body)+'</main></html>')
    return sections
build('zh',zh,captions_zh);build('en',en,captions_en)
outline={'hypothesis_id':'4','sections':[{'id':str(i),'title':head} for i,(head,paras) in enumerate(zh)],'figures':[dict(asset=k+'.png',caption=v,finding_number=i+1) for i,(k,v) in enumerate(captions_zh.items())]};dump(P/'report_outline.json',outline)
evidence={'hypothesis_id':'4','sources':[dict(path='data/paired_differences.csv',kind='paired_metrics',report_section='findings',label='三个同seed差值',fields=['condition','seed','metric','full','ablation','delta']),dict(path='data/weekly_by_type.csv',kind='weekly_counts',report_section='findings',label='零周保留的作者类型供给'),dict(path='data/weekly_exposure_by_cohort.csv',kind='observed_feeds',report_section='findings',label='实际阅读标签/来源分母'),dict(path='data/source_index.json',kind='provenance',report_section='data',label='12次来源哈希、冻结配置与三路对账')],'notice':'User-approved and adopted evidence bundle; no independent model review or formal harness release sign-off.'};dump(D/'evidence_index.json',evidence)
(D/'report_context.md').write_text('# Evidence context\n\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n\nPrimary metrics: paired_summary.csv; all seed deltas: paired_differences.csv; observed processes: decisions.csv and weekly_exposure_by_cohort.csv; raw file hashes: source_index.json.\n')
manifest={'adoption_record':'../../../hypothesis_4/experiment_3/adoption.json','formal_harness_release_signed':False,'status':'adopted','claims_user_approved':True,'independent_model_review':False,'figures':[dict(asset=k+'.png',finding_number=i+1,caption=v,source_files=['data/weekly_by_type.csv','data/run_metrics.csv','data/paired_summary.csv']) for i,(k,v) in enumerate(captions_zh.items())],'reports':['report_zh.md','report_en.md','report_zh.html','report_en.html']};dump(P/'artifact_manifest.json',manifest)
# 在独立synthesis根中整合本次12单元；不延伸到未运行的其他制度消融。
S=ROOT/'synthesis/timestamp_bdr_v1';brief={'synthesis_question':'冻结timestamp-interest中的B、D、R如何共同改变表达参与与作者供给？','scope_hypothesis_ids':['4'],'experiment_id':'3','user_approved':True,'source_artifacts':[str(P/'report_zh.md'),str(P/'report_en.md'),str(D/'paired_summary.csv'),str(D/'weekly_exposure_by_cohort.csv'),str(D/'source_index.json')],'comparison_mode':'within_hypothesis_paired_ablation','release':'user-approved and adopted; no independent LLM review'};dump(S/'synthesis_brief.json',brief)
for lang,text in [('zh','B维持晚期表达底座，D响应调节表达时序与晚期选择性，R的累计同类接触衰减抑制持续高供给。三者不是可相加的独立贡献：去R同时令B权重归零，去D可通过更早发言和更高累计接触改变后续R。份额必须与绝对产量并列，作者类型必须与正文标签分开。三项主指标的三个配对seed方向一致，但只有同一人口/调度表下3对，且Full分批复用与API路径/返回标识存在差异，不能推广到现实或其他策展制度。'),('en','B sustains a late participation floor; D response shapes timing and late selective expression; R decay with cumulative own-type exposure limits sustained overall supply. These are not additive independent contributions: removing R also removes B weight, and removing D changes later R through early activity and exposure. Shares must be reported alongside absolute counts, and author type separately from text labels. All three paired seeds agree on each primary direction, but only three pairs share one population/schedule and reused Full differs in generation batch/API route or returned identifiers; no real-world or cross-regime generalization follows.')]:
 title='B、D、R配对证据综合' if lang=='zh' else 'Synthesis of paired B, D and R evidence';link='../../presentation/hypothesis_4/timestamp_bdr_v1/report_'+lang+'.html';(S/f'synthesis_report_{lang}.md').write_text('# '+title+'\n\n'+text+'\n\n[完整报告]('+link+')\n\n用户已接受并授权采用；未通过独立模型审稿，未追加LLM调用。\n');(S/f'synthesis_report_{lang}.html').write_text('<!doctype html><meta charset="utf-8"><title>'+title+'</title><main style="max-width:850px;margin:60px auto;font:18px/1.9 system-ui"><h1>'+title+'</h1><p>'+text+'</p><p><a href="'+link+'">Full report / 完整报告</a></p><p>User-approved and adopted synthesis; no independent model review or additional LLM calls.</p></main>')
print('Adopted bilingual reports and bounded synthesis written; model calls added: 0')
