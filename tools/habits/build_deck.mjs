import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),D=R+'/du/textbook/1hcl/unit4/peiyang-hao-xiguan',W=R+'/../build';
const L=JSON.parse(await fs.readFile(D+'/lesson.json','utf8')),meta=[],nativeTables=[];
const K='LXGW WenKai TC',S='Noto Serif CJK SC',p=Presentation.create({slideSize:{width:1280,height:720}});p.theme.defaultFont=K;
const ink='#18344F',blue='#185E94';
function tx(sl,text,x,y,w,h,size=44,font=K,color=ink,bold=false){const a=sl.shapes.add({name:'text-'+sl.shapes.items.length,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});a.text=text;a.text.style={typeface:font,fontSize:size,color,bold,wrap:'square',autoFit:'none',insets:0};return a;}
const notes=id=>{const t=L.tasks.find(t=>t.id===id);return t.source+'。'+t.role+'。\n'+t.questions.join('\n')+'\n参考：'+t.answer+'\n解释：'+t.explain+'\n'+t.scoreGuide+'\n常见误区：'+t.reject;};
function start(title,nt='',kind='concept'){const sl=p.slides.add();sl.background.fill='#F7FAFD';tx(sl,title,66,42,1148,116,50,K,blue,true);tx(sl,String(meta.length+1).padStart(2,'0'),1150,660,70,46,38,K,blue);sl.speakerNotes.text='中一高级华文 单元四 生活空间《培养好习惯》\n来源：教师所附课本、教学参考及四页原漫画。漫画情节辅助理解，海报事实以课本原图为准。\n'+nt;meta.push({title,notes:nt,kind});return sl;}
function lines(title,rows,nt='',kind='concept',size=44){const sl=start(title,nt,kind);rows.forEach((s,i)=>tx(sl,s,76,180+i*143,1120,132,size,kind==='answer'?S:K));meta.at(-1).lines=rows;return sl;}
async function pic(title,n,rows=[],nt=''){const sl=start(title,nt,'comic');const bytes=await fs.readFile(D+'/assets/panel-'+String(n).padStart(2,'0')+'.png');sl.images.add({blob:bytes,contentType:'image/png',alt:'原漫画第'+n+'格',fit:'contain',position:{left:65,top:170,width:700,height:454}});rows.forEach((s,i)=>tx(sl,s,805,184+i*145,400,137,40));meta.at(-1).panel=n;return sl;}
function table(title,values,nt){const sl=start(title,nt,'answer');const tb=sl.tables.add({rows:values.length,columns:values[0].length,left:75,top:183,width:1130,height:405,columnWidths:values[0].length===2?[300,830]:[300,415,415],values});tb.borders.assign({style:'solid',fill:'#B9CBD9',width:1});for(let r=0;r<values.length;r++){tb.rows[r].height=405/values.length;for(let c=0;c<values[0].length;c++){const ce=tb.getCell(r,c);ce.fill=r===0?'#DCEAF4':'#FFFFFF';ce.text.style={typeface:K,fontSize:40,color:ink,bold:r===0,wrap:'square',autoFit:'none',insets:18,verticalAlignment:'middle'};}}nativeTables.push(meta.length);meta.at(-1).table=values;}

await pic('培养好习惯',27,['中一高级华文','单元四 生活空间','一课时'],'50分钟。两次书面作答：工作坊目的、维护友情的真实经验。');
lines('海报阅读',['标题告诉我们介绍什么。','小标题帮助我们找到对应活动。','日期、时间、地点和报名方式要分清。'],'导入3分钟。请学生找出海报标题“青年节特备活动”。');
{const sl=start('八种好习惯','图文自读10分钟，依次看八种习惯。四个课本词义题穿插口头解释。');['守时惜时','勤于阅读','坚持不懈','信守诺言','健康生活','制定计划','为人诚实','以礼待人'].forEach((s,i)=>tx(sl,String(i+1)+'  '+s,80+(i%2)*585,180+Math.floor(i/2)*110,540,90,46));}
await pic('开卷有益',3,['用自己的话解释','“开卷有益”。','读书带来什么？'],notes('word-reading'));
lines('开卷有益的意思',['读书能够使人得到益处。','这里鼓励我们勤于阅读。','可获得知识，也可开阔眼界。'],notes('word-reading'),'answer');
await pic('坚持不懈',5,['用自己的话解释','“坚持不懈”。','遇到困难时怎样？'],notes('word-persist'));
lines('坚持不懈的意思',['一直努力做下去，不松懈。','即使遇到困难，也不轻易放弃。','“滴水穿石”说明坚持能见成效。'],notes('word-persist'),'answer',42);
await pic('一诺千金',7,['用自己的话解释','“一诺千金”。','承诺为什么重要？'],notes('word-promise'));
lines('一诺千金的意思',['答应别人的事，要认真做到。','比喻说话算数，很守信用。','生活中的小承诺，也值得重视。'],notes('word-promise'),'answer');
await pic('互动剧场有什么特别之处',17,['先在海报中找','“不只是……','也是……”这句话。'],notes('theatre')+'\n本环节8分钟，点选后请学生口头连成完整回答。');
lines('观众也能参与演出',['你不只是观众，也是演员。','你可以参与剧情，','帮助差不多先生改掉坏习惯。'],notes('theatre'),'answer');
await pic('一帆风顺',29,['“友谊的小船','一帆风顺”','在这里是什么意思？'],notes('word-smooth'));
lines('一帆风顺的意思',['比喻事情进行得很顺利。','这里指朋友相处顺利，','友情不因言语不当而出现问题。'],notes('word-smooth'),'answer');
lines('工作坊的目的',['举办工作坊的目的是什么？','先选取有关“学习”和“掌握”的证据。','用一个完整句子写出两个要点。'],notes('purpose')+'\n第一次书面作答。工作坊环节共13分钟。','question',42);
lines('工作坊目的的证据',['“学习如何培养良好的习惯”','“掌握人际交往的有效策略”','先找到两处，再组织自己的答案。'],notes('purpose'),'concept',42);
lines('工作坊目的参考',['工作坊帮助参加者培养良好的习惯，','并掌握人际交往的有效策略。','这样能减少交往中的烦恼，维护友情。'],notes('purpose')+'\n前两项为核心意义点，最后一句说明联系。','answer',42);
lines('工作坊的参加对象',['工作坊适合哪些人参加？','先看“青年节”，再看工作坊内容。','哪些青年会从这个活动中获益？'],notes('audience'),'question',42);
lines('参加对象参考',['想学习维护友情、','改善人际交往的青年。','对象要联系工作坊的学习内容。'],notes('audience'),'answer',44);
table('两项活动的资料',[['活动','日期','时间'],['互动剧场','7月21日','晚上7点至9点'],['工作坊','7月20日','下午3点至5点']],'两项活动地点均为欢乐民众俱乐部礼堂。资料仅用于课本阅读，不是现实活动通知。活动与报名资料共4分钟。');
lines('报名方式',['如何报名参加青年节特备活动？','找出海报最下面的报名说明。','报名方式与活动地点相同吗？'],notes('register'),'question');
lines('课本海报中的报名方式',['登录欢乐民众俱乐部网站报名：','www.huanlecommunity.com.sg','网址仅作课本阅读资料。'],notes('register')+'\n课本写此网址，教参与漫画第32格另写www.huanleminzhongjulebu.com.sg。答题遵照课本，原漫画保持不变。','answer',40);
lines('你怎样维护友情',['你是怎么维护友情的？','和同学分享你的经验。','选一件真实经历，写清做法和原因。'],notes('friendship')+'\n必做开放题9分钟。第二次书面作答，先独立写再分享。','question',44);
lines('把经验说具体',['当时发生了什么？','你具体做了什么？','这样做为什么有助于维护友情？'],notes('friendship')+'\n如学生没有想到经历，先请他回想一次误会、合作或兑现承诺的事，不额外增加写作题。');
lines('友情经验示例',['一次合作中，我误会朋友没有做事。','了解情况后，我主动向他道歉。','道歉说明我愿意承担错误，\n有助于消除误会，让朋友感到被尊重。'],notes('friendship')+'\n此例仅示范解释联系，学生须写自己的经历。不是唯一答案。','answer',40);
lines('检查与订正',['目的题：是否写出两个核心要点？','友情经验：是否解释做法的作用？','收藏不熟悉的词，再按需要复习。'],'最后3分钟。保留首次回答后订正，导出学习记录。旧词语页是按需巩固，不要求全班再完成整套。主观题由教师覆核。', 'concept',42);
await fs.mkdir(W+'/ppt',{recursive:true});await fs.mkdir(D+'/slides',{recursive:true});
await fs.writeFile(D+'/slides.json',JSON.stringify(meta,null,2));await fs.writeFile(D+'/slides-data.js','window.SLIDES='+JSON.stringify(meta)+';');
for(const [i,sl]of p.slides.items.entries()){const png=await p.export({slide:sl,format:'png',scale:1});await fs.writeFile(D+'/slides/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await png.arrayBuffer()));console.log('Rendered',i+1,'/',meta.length);}
await(await PresentationFile.exportPptx(p)).save(W+'/ppt/candidate.pptx');await fs.writeFile(W+'/ppt/requirements.json',JSON.stringify({count:meta.length,tables:nativeTables}));console.log('PPT candidate ready',meta.length);
