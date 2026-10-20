import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),W=path.dirname(R),O=R+'/du/textbook/2hcl/unit4/kongbushijian';
await fs.mkdir(W+'/ppt-build',{recursive:true});
const L=JSON.parse(await fs.readFile(O+'/lesson.json','utf8')),T=L.tasks,pres=Presentation.create({slideSize:{width:1280,height:720}}),deck=[];
const K='LXGW WenKai TC',S='Noto Serif CJK SC',ink='#243D37',green='#245E51',red='#AE3F37',paper='#FFFCF6';pres.theme.defaultFont=K;
const comicBytes=await Promise.all([1,2,3,4,5].map(i=>fs.readFile(O+'/assets/comic'+i+'.png')));
function text(sl,s,x,y,w,h,size=44,color=ink,font=K,bold=false){const a=sl.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});a.text=s;a.text.style={typeface:font,fontSize:size,color,bold,wrap:'square',autoFit:'none',insets:0};return a;}
function start(title,notes='',lesson=1,kind='concept'){const sl=pres.slides.add();sl.background.fill=paper;text(sl,title,64,42,1152,105,50,kind==='question'?red:green,K,true);deck.push({title,notes,lesson,kind});sl.speakerNotes.text='中二高级华文 单元四 核心课文《恐怖事件》。来源：用户提供的课文、阅读放大镜、预习、教参及五张漫画。\n'+notes;text(sl,String(deck.length).padStart(2,'0'),1154,661,64,44,38,green);return sl;}
function std(title,rows,notes='',lesson=1,kind='concept',size=44){const sl=start(title,notes,lesson,kind);rows.forEach((s,i)=>text(sl,s,72,178+i*145,1130,132,size,ink,kind==='answer'?S:K));deck.at(-1).lines=rows;return sl;}
function panel(sl,n,x,y,w){const r=L.panelRects[n-1],h=w*r[3]/r[2];sl.images.add({blob:comicBytes[L.panelSheets[n-1]-1],contentType:'image/png',alt:'用户原图第'+n+'格',fit:'contain',position:{left:x,top:y,width:w,height:h},crop:{left:r[0]/1024,top:r[1]/1536,right:1-(r[0]+r[2])/1024,bottom:1-(r[1]+r[3])/1536}});}
const note=id=>{let t=T.find(t=>t.id===id);return t.source+'\n'+t.role+'。'+t.answer+'\n'+t.scoreGuide+'\n常见误读：'+t.reject;};
let s=start('恐怖事件','三课时展开，两课时可按教师流程精简。先只读第1—2段，提问：为什么讨厌蒋妍？不要先讲结局。',1,'cover');text(s,'中二高级华文 · 单元四',72,185,670,70,42);text(s,'一次误会，\n怎样改变了两人的关系？',72,290,660,200,46,red);panel(s,1,780,190,430);
std('第一、二段：为什么讨厌蒋妍？',['“我”为什么讨厌蒋妍？','为什么“坏习惯”要加上引号？','找出晚间、清晨的两种影响。'],note('p1-hidden')+'\n'+note('p2-habits'),1,'question');
std('教师示范：行为与影响',['读到十二点，灯光使室友无法入睡。','清晨闹钟又把室友吵醒。','勤奋本身未必是坏习惯；影响室友，才有这种称呼。'],note('p2-habits'),1,'answer',42);
std('第三段：“我”为什么终于发怒？',['我们怎样提醒她？“委婉”是什么意思？','提醒以后，她有没有改变？','“再次”“忍无可忍”说明了什么？'],note('p3-anger'),1,'question');
std('愤怒逐渐累积',['委婉：温和含蓄，不生硬责备。','已经提醒，她却没有改变。','美梦再次被吵醒，“我”再也忍不住。'],note('p3-anger'),1,'answer');
std('第四段：不敢反驳等于服气吗？',['“我——”蒋妍看着我怒气冲冲的样子，','一句话也不敢反驳。','这能确定她已经服气了吗？'],note('p4-response'),1,'question',43);
s=start('确定的反应与未确定的内心',note('p4-response'),1,'answer');text(s,'确定：她不敢反驳，\n没有把话说完。\n\n不能据此确定已服气，\n也不能断定她心里委屈。',72,185,630,430,42,ink,S);panel(s,8,780,190,430);
std('第五段：两人关系怎样变化？',['从哪里可以看出两人成了“冤家”？','“抬头不见低头见”是什么意思？','经常见面，却不搭理对方，感觉怎样？'],note('p5-conflict'),1,'question');
std('有相处机会，却缺少交流',['原本没有什么交流。','后来谁也不搭理谁，各走各的路。','经常见面却互不理睬，相处十分尴尬。'],note('p5-conflict'),1,'answer');
std('第六段：先理解夸张',['夸张：有意把程度说得特别强烈。','“等了半天”有时夸大等待之久。','判断写法要看语境，不能只认一个词。'],'夸张 hyperbole。示例不是课文引句。先解释，再请学生看下一页原句。',1,'concept');
std('第六段：第3句有什么作用？',['“宿舍中的空气仿佛凝固起来，','房间里安静得可以听到彼此心跳的声音。”','用了什么修辞手法？有什么作用？'],note('p6-hyperbole'),1,'question',43);
std('写法、气氛与关系',['夸张：凝固的空气，可听见的心跳。','突出宿舍气氛凝重、房间十分安静。','烘托两人互不搭理造成的尴尬。'],note('p6-hyperbole')+'\n第一课书面作答。原句可以连续加入，参考后订正。',1,'answer');
std('第六段：能否改成“打开”？',['原句：“门缓缓裂开一条缝……”','改句：“门打开……”','哪一种让你看清开门的过程？为什么？'],note('p6-door'),1,'question');
s=start('窄缝慢慢出现，紧张感加强',note('p6-door'),1,'answer');text(s,'“缓缓”“一条缝”\n呈现慢慢开门的过程。\n\n动作更具体，\n画面更紧张。',72,185,630,400,44,ink,S);panel(s,15,780,190,430);
std('第九段：从眼神找证据',['从哪里可以看出“我”和蒋妍很恐惧？','先只找第9段。','第8段的古怪笑容，能证明来者是鬼吗？'],note('p9-eyes'),1,'question');
std('两人都流露恐惧',['“在彼此的眼睛里都看到了恐惧。”','“彼此”“都”：两人同样害怕。','古怪是当时的感受，来者身份尚未揭明。'],note('p9-eyes'),1,'answer',42);
std('第十段：动作怎样表现恐惧？',['继续找原句：怎样开门、查看、回床？','可连续加入查看和回床的两句证据。','“熄灯”是什么意思？'],note('p10-actions'),1,'question');
std('敢查看，仍然会害怕',['“鼓起勇气”“小心”：勉强克服害怕。','“锁上门”“赶紧熄灯上床”：急切回避。','熄灯：把灯关掉，使灯不亮。'],note('p10-actions'),1,'answer',42);
std('第二课：第十一、十二段',['蒋妍主动问：“你看见了吗？”','“我”怎样回答？声音有什么变化？','“好可怕啊！”表达什么情感？'],note('p12-voice'),2,'question');
std('感叹句与声音一起表现恐惧',['感叹句表达较强烈的情感。','“好可怕啊！”直接说出害怕。','“我的声音有些颤抖”使恐惧更具体。'],note('p12-voice')+'\n课本感叹句还包括惊喜、愤怒等，不能只凭感叹号定情绪。',2,'answer',42);
std('第十三段：怎样看出蒋妍害怕？',['找被子里蒋妍的具体反应。','“蜷缩”“瑟瑟发抖”写出了什么？','“奇异；奇特”对应文中哪个词？'],note('p13-body'),2,'question');
std('动作让害怕看得见',['“蜷缩在被子里瑟瑟发抖”。','结合刚才的经历，反映她心中恐惧。','“诡异”：奇异、奇特，让人感到不寻常。'],note('p13-body'),2,'answer',42);
std('第十四至十六段：“也”告诉我们什么？',['蒋妍说自己喜欢看鬼故事。','“我”问：“你也喜欢读鬼故事？”','这个“也”多说明了谁的爱好？'],note('p16-common'),2,'question');
std('共同话题使交流继续',['“我”也喜欢读鬼故事。','两人发现共同爱好，逐渐有话可说。','“恐怖”：令人害怕。此时还没有查明真相。'],note('p16-common'),2,'answer',42);
std('第十七段：“讨厌鬼”为什么不见了？',['“我”心中的“讨厌鬼”是谁？','为什么这个“讨厌鬼”最后不见了？','“通宵”是什么意思？'],note('p17-change'),2,'question');
std('交流改变了“我”的看法',['“讨厌鬼”指原先令“我”讨厌的蒋妍。','聊了一夜，发现共同点；蒋妍也道了歉。','“我”不再讨厌她，并主动把小说借给她。'],note('p17-change'),2,'answer',42);
std('第十八段：真相为什么写得简略？',['闹鬼的真相是什么？','为什么这个部分写得很简略？','作者把较多篇幅留给了什么变化？'],note('p18-truth'),2,'question');
std('补全误会，把重点留给关系变化',['来者是楼上的新同学，走错了宿舍。','真相补充事情的完整性。','文章重点在交流怎样改善关系，因此略写。'],note('p18-truth'),2,'answer',42);
std('第十八段：“惊悚而美丽”怎样理解？',['作者为什么说新同学走错宿舍是一个','“惊悚而美丽的误会”？','分别解释两个词指什么，再联系起来。'],note('p18-beauty'),2,'question',43);
std('过程吓人，结果美好',['惊悚：误把女生当鬼，两人感到恐惧。','美丽：误会促成交流，消除隔阂。','两人的关系改善，所以结果令人欣喜。'],note('p18-beauty')+'\n第二课第一项独立书面作答，不以关键词评分。',2,'answer',42);
std('第十九段：抒情句与议论句',['抒情句：直接表达对人或事的情感。','议论句：对事情提出看法或道理。','感叹号可作线索，仍要判断句子的内容。'],'抒情句 expressing feelings；议论句 expressing a view。对照例：好漂亮的鸟蛋！与相处时应顾及别人的需要。',2,'concept');
std('关键句怎样帮助理解主题？',['找出抒情句与议论句。','议论句可连续加入两句，保留完整意思。','结合“我”和蒋妍的关系变化，概括主题。'],note('p19-theme'),2,'question');
std('抒情句：对误会的感慨',['“多么惊悚而美丽的误会啊！”','两人虽然受惊，却因此增进了解。','这份欣喜，与关系变好的结果相连。'],note('p19-theme'),2,'answer');
std('议论句：由故事说出道理',['“其实，人与人相处，总会出现这样那样的问题。”','“很多时候，只要多点交流，就可以解决这些问题，','人们之间的关系也会变得更和谐。”'],note('p19-theme'),2,'answer',40);
std('主题须和故事内容相连',['人与人相处需要多交流，增进了解。','文中两人原本互不搭理，交流后关系改善。','故事说明：交流有助于化解隔阂，使相处和谐。'],note('p19-theme')+'\n第二课第二项书写，师生共同整理。注意“很多时候”的范围。',2,'answer',41);
std('第三课：内容与关系的变化',['先按课本表格回想四个阶段。','每个阶段发生什么？两人的关系怎样？','完整读完后，再把全篇联系起来。'],note('full-table'),3,'question');
function tableSlide(title,values,notes){let sl=start(title,notes,3,'answer');let tb=sl.tables.add({rows:values.length,columns:2,left:72,top:175,width:1136,height:410,columnWidths:[705,431],values});tb.borders.assign({style:'solid',fill:'#D5DDD8',width:1});tb.cells.block({row:0,column:0,rowCount:values.length,columnCount:2}).assign({textStyle:{typeface:K,fontSize:40,color:ink},margins:{left:20,right:16,top:16,bottom:16},anchor:'center'});for(let c=0;c<2;c++){tb.getCell(0,c).fill='#E6EEE8';tb.getCell(0,c).text.style={typeface:K,fontSize:40,color:green,bold:true};}}
tableSlide('先有作息冲突，后来互不搭理',[['主要内容','关系变化'],['晚睡早起，影响室友休息','“我”讨厌蒋妍'],['提醒无效，“我”忍不住吼起来','两人成了“冤家”']],note('full-table'));
tableSlide('交流带来了解，关系逐渐改善',[['主要内容','关系变化'],['发生误会，两人聊了一夜','发现共同点，蒋妍道歉'],['“我”把恐怖小说借给蒋妍','不再讨厌她，成为朋友']],note('full-table'));
std('感叹句：先比较语气',['“这里的景色很美丽。”平实陈述。','“这里的景色多么美丽啊！”强烈赞叹。','感叹句也可表达愤怒、恐惧等情感。'],'回顾课本三个例句：好漂亮的鸟蛋！惊喜；蒋妍，你真的很讨厌！愤怒；好可怕啊！恐惧。',3,'concept',42);
std('按提示改写成感叹句',['1. 你这么做很过分。（真）','2. 这店里的东西很便宜。（好）','3. 这里的景色很美丽。（多么）'],note('exclamation'),3,'question');
std('感叹句参考答案',['1. 你这么做真过分！','2. 这店里的东西好便宜啊！','3. 这里的景色多么美丽啊！'],note('exclamation'),3,'answer');
std('必做开放题：交流为什么有用？',['“很多时候，只要多点交流，就可以解决这些问题，人们之间的关系也会变得更和谐。”','你是否赞同这个看法？为什么？','说一说你和同学相处时曾遇到的问题，以及你是如何解决这个问题的。'],note('open-response'),3,'question',40);
std('立场、理由、例子与回扣',['立场：我怎么看？理由：为什么？','例子：真实的问题、做法和后来变化。','回扣：交流改变了什么？怎样支持看法？'],T.at(-1).explain+'\n先独立作答，后看示范。不要求同意；按理由与例证判断。',3,'concept');
std('虚构示范：说清分工后改变行动',['我赞同交流常能改善关系。','小组有人没有交稿，询问后才知道他不清楚分工。','我们重新确认任务和时间，后来顺利完成。'],T.at(-1).answer+'\n这是虚构示范，不是学生个人经历。不可照抄成自己的事。',3,'answer',42);
std('例子为什么支持观点？',['交流让双方找到问题的原因。','重新分工把了解落实为行动。','所以减少误会、改善合作，而不只是聊了几句。'],T.at(-1).scoreGuide+'\n可接受部分赞同：还需要愿意调整行动。',3,'answer',42);
std('当堂检查与订正',['我的答案有没有回答“为什么”？','原句支持了什么？哪些只是我的推测？','保存订正，整理自己的词语本。'],'检查页填写姓名、班级、学号或组别；导出记录。没有速度分或个人榜。',3,'concept');
await fs.writeFile(O+'/slides.json',JSON.stringify(deck,null,2));await fs.writeFile(W+'/ppt-build/proto.json',JSON.stringify(pres.toProto()));
await (await PresentationFile.exportPptx(pres)).save(W+'/ppt-build/candidate.pptx');
for(const [i,s]of pres.slides.items.entries()){const png=await pres.export({slide:s,format:'png',scale:1});await fs.writeFile(O+'/slides/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await png.arrayBuffer()));console.log('rendered',i+1)}
console.log('slides',deck.length);
