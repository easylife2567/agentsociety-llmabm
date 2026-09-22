import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {resolvePresentationFont,applyPresentationChartFont,finalizePresentation} from '/Users/easylife/.codex/plugins/cache/openai-primary-runtime/presentations/26.915.20218/skills/presentations/container_tools/artifact_tool_utils.mjs';
const ROOT='/Users/easylife/Project/AgentSociety';
const WORK='/private/tmp/agentsociety_groupmeeting';
const SKILL='/Users/easylife/.codex/plugins/cache/openai-primary-runtime/presentations/26.915.20218/skills/presentations';
const FONT=resolvePresentationFont({fontFamily:'PingFang SC'});
const pres=Presentation.create({slideSize:{width:1600,height:900}});
const C={black:'#161616',mid:'#555555',gray:'#929292',pale:'#EFEFEF',line:'#D5D5D5'};
function txt(s,str,x,y,w,h,size=25,bold=false,color=C.black){const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}}); sh.text=str; sh.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none',verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};return sh;}
function table(s,vals,x,y,w,h,widths,size=23){let t=s.tables.add({rows:vals.length,columns:vals[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values:vals});t.borders.assign({fill:'#FFFFFF',width:0});t.styleOptions={headerRow:false,bandedRows:false};for(let i=0;i<vals.length;i++){t.rows[i].height=h/vals.length;for(let j=0;j<vals[0].length;j++){const c=t.getCell(i,j);c.fill=i===0?C.black:(i%2===1?'#F0F0F0':'#FAFAFA');c.text.style={typeface:FONT,fontSize:size,bold:i===0,color:i===0?'#FFFFFF':C.black,verticalAlignment:'middle',insets:{left:13,right:10,top:7,bottom:7}};}}return t;}
function head(s,title,sub,n){s.background.fill='#FFFFFF';txt(s,title,64,43,1472,66,44,true);txt(s,sub,64,118,1460,44,24,false,C.mid);txt(s,`${n} / 02`,1458,850,80,26,18,false,C.mid);}
function chart(s,series,x,y,w,h,max=1){const ch=s.charts.add('line',{position:{left:x,top:y,width:w,height:h},categories:Array.from({length:11},(_,i)=>`W${i+12}`),series,hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{typeface:FONT,fontSize:21,fill:C.black}},xAxis:{textStyle:{typeface:FONT,fontSize:18,fill:C.mid},line:{fill:C.gray,width:1},majorGridlines:null},yAxis:{min:0,max,majorUnit:0.2,numberFormatCode:'0%',textStyle:{typeface:FONT,fontSize:18,fill:C.mid},majorGridlines:{fill:'#E4E4E4',width:1}},chartFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaFill:'#FFFFFF',lineOptions:{smooth:false}});applyPresentationChartFont(ch,{fontFamily:FONT});return ch;}
const bench=JSON.parse(await fs.readFile(ROOT+'/hypothesis_4/benchmark_curves.json','utf8'));
const weeks=Array.from({length:11},(_,i)=>`2026-W${12+i}`);
const real=(key)=>weeks.map(w=>{const r=bench.weekly_category_matrix[w];return r[key]/(r.total-r['爬取噪音']);});
const csv=await fs.readFile(ROOT+'/hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_weekly_summary.csv','utf8');
const lines=csv.replace(/^\uFEFF/,'').trim().split(/\r?\n/); const fields=lines.shift().split(',');const records=lines.map(l=>Object.fromEntries(l.split(',').map((v,i)=>[fields[i],v])));
const metric=(arm,m)=>weeks.map(w=>Number(records.find(r=>r.arm===arm&&r.week===w&&r.metric===m).mean));
const series=(name,values,color,symbol='circle',dash='solid')=>({name,values:values.map(v=>Number(v.toFixed(8))),line:{fill:color,width:3,style:dash},marker:{symbol,size:6}});
let s=pres.slides.add();
head(s,'悼念退潮之后：算法策展与逝者数字表征','研究问题：平台如何通过“谁看见什么”，改变既有群体的发声权重与公共记忆？','01');
txt(s,'经验事实｜三平台帖文中的表征转移',64,194,700,38,27,true);
txt(s,'张雪峰案例 · 抖音 / 微博 / 小红书 · 52,716 条有效记录',64,239,700,32,20,false,C.mid);
chart(s,[series('教育',real('教育观点讨论'),'#999999','square'),series('悼念',real('事件悼念讨论'),'#5E5E5E','diamond','dashed'),series('玩梗',real('梗文化讨论'),'#111111')],58,284,729,278,0.8);
txt(s,'W13 悼念 43.6%  →  W19 玩梗 8.6%  →  W22 玩梗 63.0%',64,576,742,38,23,true);
txt(s,'分母为五类有效内容（含营销、其他）；图中仅显示三类表征',64,614,742,30,18,false,C.mid);
txt(s,'机制建模｜可见性—表达—内容回流',836,194,700,38,27,true);
txt(s,'固定群体：营销 23 / 悼念 22 / 其他 21 / 玩梗 19 / 教育 15',836,239,700,32,21,false,C.mid);
txt(s,'平台分发 Γ → 个体信息流 → 表达决策 U\n生成文本回流内容池，进入下一轮分发',836,293,700,82,27,true);
txt(s,'U = B + R(D − B)',836,389,700,53,40,true);
txt(s,'B 常态表达锚点；D 同类内容可见度形成的意见气候；\nR 随累计同类曝光衰减的注意力余量。\n达到个体门槛后，由 LLM 依人设和所见内容生成表达。',836,453,700,112,24);
txt(s,'基线：W05–W12 固定 B；标定：W13–W18；\n后段检查：W19–W22。类型固定，检验群体构成效应。',836,579,700,68,23,false,C.mid);
table(s,[['全历史随机','小时级时序','纯兴趣匹配'],['截至当周全部帖子均匀抽取 10 条','按真实到达与行动时间取最新 10 条','类型词表 × 文本特征；保留生命周期'],['去策展反事实；无时间 / 热度加权','小时内同步；跨小时新内容可见','个性化选择性曝光；无热度项']],64,669,1472,129,[490,491,491],22);
txt(s,'实验规模：100 个智能体 × 11 周 × 3 制度 × 3 seeds = 9,900 个智能体—周机会；同 seed 跨制度匹配注入样本',64,814,1430,32,22,true);
s.speakerNotes.textFrame.setText('项目介绍，第1页。数据来源：TOPIC.md；hypothesis_4/benchmark_curves.json 中 weekly_category_matrix；paper/manuscript/manuscript.accepted.md 的实验设计；hypothesis_4/experiment_1/runs/anchored_v1/README.md。原始表52,736条，剔除20条存疑记录后有效编码记录52,716条。图表按五类有效内容归一化，排除爬取噪音；只画教育、悼念、玩梗三条线，未画营销与其他，不应将图中三类当作全部。W13悼念4714/(11394-594)=43.65%；W19玩梗139/(1792-171)=8.58%；W22玩梗3220/(5338-230)=63.04%。研究以张雪峰逝后舆论场为案例，介绍以用户提供的研究材料为据。LLM只负责达到门槛后的具体表达；是否发言由U与门槛决定。三臂差异是完整信息流制度，候选池与时序也不同，不能称为纯排序实验。');
s=pres.slides.add();
head(s,'主要结果：策展制度改变表征演化轨迹','正式实验：9 / 9 runs 完成，生成 1,904 条 Agent 帖；三臂均在 W20 起出现玩梗供给增长','02');
txt(s,'玩梗供给份额｜现实基准与 Agent-only 仿真',64,194,760,38,27,true);
chart(s,[series('现实',real('梗文化讨论'),'#111111','diamond','dashed'),series('随机',metric('random','meme_share_agent_only'),'#B0B0B0','square'),series('时序',metric('chronological','meme_share_agent_only'),'#777777','triangle'),series('兴趣',metric('interest','meme_share_agent_only'),'#111111','circle')],56,245,762,322,1);
txt(s,'W22 终点：现实 63.0%；随机 44.3%；时序 / 兴趣均 83.9%',64,581,760,35,22,true);
table(s,[['五类轨迹 DTW 距离 ↓','随机','时序','兴趣'],['3-seed 均值','23.7','27.0','22.0'],['seed 范围','19.9–26.9','24.3–30.6','19.6–24.3']],64,632,746,135,[280,154,156,156],21);
txt(s,'兴趣平均距离最低，但与随机范围重叠；两臂不可据此判显著。\n时序 / 兴趣高估后段幅度，复现相位不等于精确复现现实。',64,782,755,67,21,false,C.mid);
txt(s,'可见性配置与表达响应的耦合',862,194,674,38,27,true);
txt(s,'W22 时序的总体玩梗曝光更高（71.2% vs 59.9%），\n兴趣下玩梗群体却更活跃（发言率 91.2% vs 82.5%）。\n个性化配置改变表达响应；总体曝光量不足以解释差异。',862,247,674,110,23);
txt(s,'机制消融｜100 个配对 seeds 的数值代理',862,376,674,38,26,true);
table(s,[['移除项','相对完整模型的变化','作用解释'],['B 常态锚点','后期全体发言率 −12.0 pp','维持常态供给'],['D 意见气候','后期玩梗发言率 −70.4 pp','选择性激活'],['R 注意力余量','中期全体发言率 +43.2 pp','驱动事件退潮']],862,426,674,176,[169,331,174],20);
txt(s,'后期 W20–W22；中期 W16–W19。消融未调用 LLM。',862,615,674,30,18,false,C.mid);
txt(s,'当前贡献与下一步',862,666,674,38,26,true);
txt(s,'已完成：现实轨迹、可追溯仿真闭环、制度反事实与机制消融。\n证据边界：含现实注入；三臂比较完整制度，非纯排序效应。\n下一步：检查注入依赖、扩大重复与跨案例验证。',862,714,674,115,22);
txt(s,'注：现实按五类有效内容归一化；仿真折线为各臂 3-seed 均值。DTW 为五类周轨迹的受限动态时间规整距离（越低越好）。',64,859,1338,26,16,false,C.mid);
s.speakerNotes.textFrame.setText('来源：hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_weekly_summary.csv；arm_dtw_fit_summary.csv；_derived/charts/report_composites/figure_04_dtw_reproduction_and_fit.json；hypothesis_4/experiment_1/results/numerical_ablation_drb/RESULTS.md；paper/manuscript/manuscript.accepted.md。折线为Agent-only供给份额，排除了注入帖分母，但仿真行为受到真实注入信息流驱动，因此不是无外源输入的独立生成验证。W22总体玩梗曝光时序0.712，兴趣0.59933；玩梗型Agent发言率兴趣0.91228，时序0.82456，发言率分母为19名玩梗型Agent。DTW基于五类内容份额、欧氏局部距离、±1周窗口并按路径长度归一化，以百分点尺度报告；3 seeds不足以支持统计显著性。消融为共享机制的数值代理，4条件×100配对seed，没有运行LLM。去B后期发言率差95% Monte Carlo CI [-12.5,-11.5] pp；去D玩梗发言率差[-71.2,-69.5] pp；去R中期全体发言率差[42.7,43.6] pp。这些区间只反映仿真随机性，不是现实总体误差。工作区pipeline仍处于analysis in_progress；正文已有作者稿，但不把分析阶段标记为已完成。');
await fs.mkdir(WORK+'/output',{recursive:true});
const draft=WORK+'/build/draft.pptx';await(await PresentationFile.exportPptx(pres)).save(draft);
for(let i=0;i<2;i++){const sl=pres.slides.items[i];const p=await pres.export({slide:sl,format:'png',scale:1});await fs.writeFile(WORK+`/build/slide-${i+1}.png`,new Uint8Array(await p.arrayBuffer()));}
await finalizePresentation({workspaceDir:WORK,candidatePath:draft,finalPath:WORK+'/output/项目组会介绍_2页.pptx',pythonExecutable:'/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-heading-fit','--require-native-table-slide','1','--require-native-table-slide','2'],explicitTotalSlideCount:2,requiredNativeTableOwnerSlides:[1,2],requiredNativeChartOwnerSlides:[1,2],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:WORK+'/build/validation.json'});
console.log('Done',FONT);
