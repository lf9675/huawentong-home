import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),W=process.env.HWT_BUILD_WORKSPACE||path.dirname(R),O=R+'/du/textbook/2hcl/unit3/shou-ji-bei-diu-qi-zhi-hou';
await fs.mkdir(W+'/ppt-build',{recursive:true});
const L=JSON.parse(await fs.readFile(O+'/lesson.json','utf8')),T=L.tasks,pres=Presentation.create({slideSize:{width:1280,height:720}}),deck=[];
const K='LXGW WenKai TC',S='Noto Serif CJK SC',ink='#243D37',green='#245E51',red='#AE3F37',paper='#FFFCF6';
pres.theme.defaultFont=K;
const comicBytes=await Promise.all([1,2,3,4].map(i=>fs.readFile(O+'/assets/comic'+i+'.png')));
const trendBytes=await fs.readFile(O+'/assets/textbook-trend.png');
function text(sl,s,x,y,w,h,size=44,color=ink,font=K,bold=false){const a=sl.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});a.text=s;a.text.style={typeface:font,fontSize:size,color,bold,wrap:'square',autoFit:'none',insets:0};return a;}
function start(title,notes='',lesson=1,kind='concept'){const sl=pres.slides.add();sl.background.fill=paper;text(sl,title,64,42,1152,105,52,kind==='question'?red:green,K,true);deck.push({title,notes,lesson,kind});sl.speakerNotes.text='中二高级华文 单元三 阅读巩固《手机被丢弃之后》。来源：用户提供的课文3页、巩固练习1页、教参2页及4张原有图画。\n'+notes;text(sl,String(deck.length).padStart(2,'0'),1154,661,64,44,38,green);return sl;}
function standard(title,rows,notes='',lesson=1,kind='concept',{size=44,step=125,y=178}={}){const sl=start(title,notes,lesson,kind);for(let i=0;i<rows.length;i++){if(y+i*step+step>652)throw Error('Overflow '+title);text(sl,rows[i],72,y+i*step,1130,step-10,size,ink,kind==='answer'?S:K)}deck.at(-1).lines=rows;return sl;}
function panel(sl,n,x,y,w){const r=L.panelRects[n-1],h=w*r[3]/r[2];if(y+h>650)throw Error('Panel overflow '+n);sl.images.add({blob:comicBytes[L.panelSheets[n-1]-1],contentType:'image/png',alt:'用户原图第'+n+'格',fit:'contain',position:{left:x,top:y,width:w,height:h},crop:{left:r[0]/1024,top:r[1]/1536,right:1-(r[0]+r[2])/1024,bottom:1-(r[1]+r[3])/1536}});}
let sl=start('手机被丢弃之后','两课时，每课50分钟。导入只听两三名学生口头回答：更换手机后，旧手机怎样处理？',1,'cover');text(sl,'中二高级华文 · 单元三',72,190,690,65,42);text(sl,'第一课：构成、增长与原因',72,295,680,65,44,red);text(sl,'第二课：价值、危害与行动',72,400,680,65,44);panel(sl,1,780,185,430);
standard('第一段：三个问句有什么作用？',['第1段用了第二人称和三个问句，','有什么作用？','“你”在和谁说话？最后引出什么？'],T[0].source+'\n教师示范。先问再揭。',1,'question');
standard('从读者的经验引出说明对象',['“你”：直接与读者交流，拉近距离。','三个问句：引导回想换手机的经验。','旧手机的去向：引出电子垃圾。'],T[0].answer,1,'answer');
standard('第二段：图表告诉我们什么？',['这个图表要告诉我们什么？','哪一类电器或设备占的比例最大？','这说明了什么？'],T[1].source+'\n先看标题，再看类别和比例。',1,'question');
sl=start('全球电子垃圾的构成','据教材引用的2020年全球电子废弃物监测报告。保留六类及精确比例，合计100%。本页使用可编辑饼状图与表格。');
const cats=['小型电器','大型电器','制冷、取暖电器','电子显示屏','资讯科技产品','照明产品'],vals=[32,24,20,13.5,9,1.5],colors=['#2A91C8','#DB575C','#58A251','#EBCB42','#8874B1','#D9DD71'];
sl.charts.add('pie',{position:{left:50,top:170,width:550,height:410},categories:cats,series:[{name:'电子垃圾构成（%）',values:vals,points:colors.map((fill,idx)=>({idx,fill}))}],hasLegend:false,dataLabels:{showValue:false,showPercent:false,showCategoryName:false},chartFill:paper,plotAreaFill:paper});
const tb=sl.tables.add({rows:6,columns:2,left:640,top:167,width:570,height:438,columnWidths:[395,175],values:cats.map((c,i)=>[c,vals[i]+'%'])});tb.borders.assign({style:'solid',fill:paper,width:2});tb.cells.block({row:0,column:0,rowCount:6,columnCount:2}).assign({textStyle:{typeface:K,fontSize:38,color:ink},margins:{left:14,right:8,top:8,bottom:8},anchor:'center'});for(let i=0;i<6;i++){tb.getCell(i,0).fill=colors[i];tb.getCell(i,0).text.style={typeface:K,fontSize:38,color:[0,1,4].includes(i)?'#FFFFFF':ink};}
standard('76%包括图中的哪些部分？',['“家用电器占百分之七十六”，','这包括图表中的哪些部分？','先找类别，再相加验证。'],T[1].questions[2]+'\n师生共同点认三类；不要预先给合计答案。',1,'question');
standard('单独类别与合并类别',['小型32%＋大型24%＋制冷取暖20%＝76%','单独一类最大：小型电器，32%。','合起来看：家用电器占大多数。'],T[1].answer+'\n巩固练习二第一行：资讯科技产品9%，家用电器76%。',1,'answer',{size:42});
standard('第三段：怎样看整体变化？',['第3段如何说明电子垃圾总量的整体变化？','第3段下面的折线图主要告诉我们什么？','先核对年份、单位和线型。'],T[2].source,1,'question',{size:42});
sl=start('全球电子垃圾总量','保留教材原折线图，不虚构逐年精确数列。纵轴：百万吨；2019年之后虚线为预测。教材引用2020年报告。');
sl.images.add({blob:trendBytes,contentType:'image/png',alt:'教材折线图原绘图区，实线历史资料和虚线预测',fit:'contain',position:{left:240,top:190,width:755,height:348},crop:{left:67/693,top:315/816,right:1-608/693,bottom:1-532/816}});
text(sl,'百万吨',1000,138,200,50,38);for(const [value,y]of [[80,165],[60,255],[40,343],[20,432],[0,516]])text(sl,String(value),155,y,75,50,38);
for(const [yr,x]of [[2014,180],[2019,416],[2024,652],[2030,935]])text(sl,String(yr),x,554,120,50,38);
text(sl,'年份',1100,554,130,50,38);
text(sl,'实线：历史资料　　虚线：预测',280,621,840,48,38,green);
standard('按课文整理三个时间点',['2014年：4440万吨。','2019年：比2014年增加21%。','预计2030年：约7400万吨。'],T[2].answer+'\n巩固练习二第二行。注意“增加”与“增至”；2030年是预测。',1,'answer');
standard('为什么要列举这些数字？',['加入数字原句，可连续加入多句。','用2—3句话说明：数字和折线图，','怎样让我们看清电子垃圾的问题？'],T[2].source+'\n第一课独立书面作答之一。允许先在学习单取证。主观答案由教师核对。',1,'question');
standard('数字要联系说明重点',['数量：总量很大。变化：持续增长。','具体年份、数量与增幅让变化清楚可见。','这说明电子垃圾问题日益严重。'],T[2].answer+'\n'+T[2].scoreGuide,1,'answer');
standard('“几乎会翻一番”与精确计算',['课文原句保留，精确计算另作区分。','7400÷4440≈1.67，即增加约67%。','概括趋势时写“总量明显增长”。'],'教材第3段“几乎会翻一番”与精确翻倍有距离。翻一番应为原来的2倍；不把这句话设为精确计算得分点。仅作答后辨析。',1,'answer',{size:42});
standard('仿写句子',['随着____________，','____________逐年______。','前后变化要有合理联系。'],T[3].questions.join('\n')+'\n原句完整显示在互动页左侧。第一课第二项书写。',1,'question');
standard('仿句对照',['随着同学们越来越重视节约用水，','学校的用水量逐年减少。','“逐年”是一年一年地，不能只写今天。'],T[3].answer+'\n示例是假设句式练习，不是某校实测资料。'+T[3].scoreGuide,1,'answer');
standard('第四段：为什么泛滥成灾？',['电子垃圾为什么会泛滥成灾？','先按“一是”“二是”分清两方面。','用完整句口头回答。'],T[4].source+'\n点选归类，保留全部原因。',1,'question');
standard('两方面共同增加电子垃圾',['产品：易损坏、寿命短、维修途径有限。','人们：喜新厌旧、缺乏危害认识。','不断追新并随意丢弃，使垃圾更多。'],T[4].answer+'\n第一课末订正；词语按个人需要收藏。',1,'answer');
standard('第二课：第五段的说明方法',['第5段使用了哪些说明方法？','用来说明什么？'],T[5].source+'\n先教学方法，再让学生在本段辨认。',2,'question');
standard('举例子与列数字',['举例子：用具体事物说明一般情况。','列数字：用数量、比例说明大小或程度。','答题还要说：具体说明了什么。'],'方法先解释再练习。举例子 giving examples；列数字 using statistics。英文仅为术语辅助。',2,'concept');
sl=start('第五段：找完整的证据',T[5].source+'\n先点手机材料的原句，再点“数据显示”一句，保留两句。第二课第一项独立书面作答。',2,'question');text(sl,'连续加入两句原文，\n再写出：\n方法＋例子／数字＋重点。',72,205,620,275,44);panel(sl,18,775,180,430);
standard('手机的例子说明什么？',['以智能手机和其中的贵金属为例，','具体说明电子垃圾中有可利用的资源。','一般说明与具体事物联系起来。'],T[5].answer+'\n方法：举例子。接受黄金、白银等对应例证。',2,'answer');
standard('数字说明什么？',['60种：说明手机材料中的资源丰富。','95亿美元：说明全部回收的价值很高。','注意“如果”“全部回收”的条件。'],T[5].answer+'\n按课文表述；不是已经实现的收入，也不是单部手机的价值。',2,'answer');
standard('把方法与作用连起来',['本段用了举例子和列数字，','以手机及其中金属为例，列出有关数量，','具体说明大部分电子垃圾可回收、价值高。'],T[5].scoreGuide+'\n各独立意义单位分别判断。比较首次回答，完成订正。',2,'answer',{size:42});
standard('第六段：为什么要写回收价值？',['作者为什么要说明可回收电子垃圾的价值？','留意“遗憾的是”前后写了什么。'],T[6].source+'\n把可回收价值与实际利用情况比较。',2,'question',{size:42});
standard('可回收价值与实际利用',['2019年：估计可回收价值570亿美元。','现实：大部分填埋，再利用不到20%。','资源值得回收，却有大量尚未利用。'],T[6].answer+'\n570亿美元不是已经获得的回收收入。不到20%不是恰好20%。',2,'answer',{size:42});
standard('第七段：处理不好会有什么危害？',['电子垃圾处理不好会有什么危害？','找“渗透”“污染”“影响”。','先按顺序点选，再口头说明。'],T[7].source,2,'question');
sl=start('填埋后的危害过程',T[7].answer+'\n按课文因果整理。漫画帮助理解，回答仍需原文证据。',2,'answer');panel(sl,26,72,190,530);text(sl,'重金属渗透到地下。\n污染土壤和地下水源。\n影响动植物与人类健康。',660,195,550,300,42,ink,S);
standard('第八段：为什么设置许多回收点？',['为什么要在300多个地点设置','电子垃圾回收箱？','数量多、遍布全岛，对公众有什么帮助？'],T[8].source+'\n300多个为课文资料，不作为当前地点数量。',2,'question');
standard('直接信息与合理推断',['原文：收集公众投放的废弃电子产品。','原文：交给专人集中处理，再循环利用。','推断：回收点遍布全岛，方便公众投放。'],T[8].answer+'\n直接信息 Direct info；合理推断 Inference。推断不能伪装成原文引句。',2,'answer',{size:42});
standard('第九段：为什么要三思而行？',['最后一段为什么强调更换手机时','要三思而行？','更换前和更换后，各要注意什么？'],T[9].source+'\n此时读完全篇，才回看第4、6、7段。',2,'question');
standard('把前文落实为行动',['更换前：先考虑是否确有需要。','更换后：妥善处理旧手机。','减少垃圾，珍惜资源，避免不当处理。'],T[9].answer+'\n三思而行是慎重考虑，不是机械地想三次。',2,'answer');
standard('必做开放题',['想想看，你在生活中怎么做才能减少','电子垃圾，为环保尽一份力？','为什么这样做有效？请举具体例子。'],T[10].source+'\n第二课第二项书写。不能只勾已讨论；开放题由教师核对。',2,'question',{size:43});
standard('建议、理由、例子与回扣',['建议：我准备怎样做？理由：为什么有效？','例子：在什么具体情境中怎样做？','回扣：这怎样减少垃圾或利用资源？'],T[10].explain+'\n这一题是建议型，不硬套认同／不认同。',2,'concept',{size:42});
standard('开放回应示例',['建议：继续使用仍能满足需要的手机。','理由：减少为了追新而提前丢弃。','例子：新款推出，旧机仍适用，就继续用。'],T[10].answer+'\n只在学生提交后展示，不要求学生照抄。',2,'answer',{size:42});
standard('解释例子怎样支持建议',['继续用适用的旧机，可减少不必要购买，','也减少本来还能使用的手机被提前丢弃。','因此，这个做法能从源头减少电子垃圾。'],T[10].scoreGuide+'\n维修、转让、合规回收等其他建议也可接受，须解释因果。',2,'answer',{size:42});
standard('检查与订正',['答案是否真正回答了“为什么”？','证据、年份、单位与预测是否准确？','完成订正，整理自己的词语本。'],'检查页补齐姓名、班级、学号／组别，可导出首次回答、尝试与订正。没有速度分或个人排名。',2,'concept');
await fs.writeFile(O+'/slides.json',JSON.stringify(deck,null,2));await fs.writeFile(W+'/ppt-build/proto.json',JSON.stringify(pres.toProto()));
await (await PresentationFile.exportPptx(pres)).save(W+'/ppt-build/candidate.pptx');
for(const [i,s]of pres.slides.items.entries()){const png=await pres.export({slide:s,format:'png',scale:1});await fs.writeFile(O+'/slides/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await png.arrayBuffer()));console.log('rendered',i+1)}
console.log('slides',deck.length);
