import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const R=process.env.ZM_REPO_DIR||path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),O=R+'/du/textbook/2hcl/unit4/zui-mei-de-zi-shi',W=process.env.ZM_BUILD_DIR;
await fs.mkdir(W+'/ppt-build',{recursive:true});await fs.mkdir(W+'/output',{recursive:true});
const L=JSON.parse(await fs.readFile(O+'/lesson.json','utf8')),T=L.tasks,deck=[],pres=Presentation.create({slideSize:{width:1280,height:720}});
const K='LXGW WenKai TC',S='Noto Serif CJK SC',ink='#243D37',green='#245E51',red='#AE3F37',paper='#FFFCF6';pres.theme.defaultFont=K;let lesson=1;
function text(sl,s,x,y,w,h,size=44,color=ink,font=K,bold=false){const a=sl.shapes.add({name:'text-'+sl.shapes.items.length,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});a.text=s;a.text.style={typeface:font,fontSize:size,color,bold,wrap:'square',autoFit:'none',insets:0};return a;}
function start(title,notes='',kind='concept'){const sl=pres.slides.add();sl.background.fill=paper;text(sl,title,64,38,1152,118,50,kind==='question'?red:green,K,true);deck.push({title,notes,kind,lesson});sl.speakerNotes.text='中二高级华文 单元四《最美的姿势》。来源：教师提供的课本两张截图、教参三张截图及四页漫画。\n'+notes;text(sl,String(deck.length).padStart(2,'0'),1152,661,70,44,38,green);return sl;}
function standard(title,rows,notes='',kind='concept',size=44){const sl=start(title,notes,kind);rows.forEach((s,i)=>text(sl,s,72,178+i*145,1134,132,size,ink,kind==='answer'?S:K));deck.at(-1).lines=rows;return sl;}
const note=id=>{const t=T.find(t=>t.id===id);return t.source+'\n'+t.role+'。\n'+t.questions.join('\n')+'\n参考：'+t.answer+'\n解析：'+t.explain+'\n'+t.scoreGuide+'\n常见误读：'+t.reject;};
async function comic(title,n,notes){const sl=start(title,notes,'comic'),r=L.panelRects[n-1],bytes=await fs.readFile(O+'/assets/comic'+L.panelSheets[n-1]+'.png');const h=475,w=h*r[2]/r[3];sl.images.add({blob:bytes,contentType:'image/png',alt:'原漫画第'+n+'格，画面与台词未改',fit:'contain',position:{left:(1280-w)/2,top:165,width:w,height:h},crop:{left:r[0]/1024,top:r[1]/1536,right:1-(r[0]+r[2])/1024,bottom:1-(r[1]+r[3])/1536}});deck.at(-1).panel=n;}
standard('最美的姿势',['中二高级华文 · 单元四 · 巩固阅读','两课时：从自卑到自信','一张照片，怎样让“我”重新看见自己？'],'第一课读第1—5段，第二课读第6—10段。每课50分钟，四项书写任务，其他用口头、点选和取证。','cover',46);
standard('拍照时，你会摆什么姿势？',['你拍照时最喜欢摆什么姿势？','摆出什么姿势会让你有自信？为什么？','只谈愿意分享的内容。'],'教参1.2导入。口头交流5分钟，不评价学生外貌，不要求展示个人照片。','question');
standard('第一段 · 先分清人物的感受',['“即使是别人不经意的一瞥……”','“我觉得同学们的目光都落在……”','无意的一眼，在“我”心里有多大影响？'],'先读第一段完整原文。原文中的“我觉得”表明叙述者主观感受，不能据此断定同学的意图。','question');
standard('比喻要说清具体作用',['“声音像雷声” → 突出声音大。','比喻（metaphor / simile）：写相似特点。','找到比较对象，再解释特点与感受。'],'概念先教后练。“像”字不一定单独决定修辞，要看有无用另一事物突出相似特点。');
standard('第一段 · 两个比喻有什么作用？',['这一段的两个比喻句有什么作用？','“射向我的利箭”','“好像被烈日炙烤着”'],note('p1-metaphor'),'question');
standard('两个比喻 · 从感受到心理',['一瞥像利箭 → 目光使“我”感到受伤。','被注视像被炙烤 → 内心非常难受。','共同表现：“我”敏感、自卑，在意目光。'],note('p1-metaphor'),'answer',42);
standard('第二段 · 没有信心的依据',['从哪里可以看出“我”对自己的外表','没有自信？','找行为，再找想法；可连续加入多句原文。'],note('p2-confidence'),'question');
standard('行为与想法，一起证明',['行为：沉默、独来独往，害怕摄像头。','想法：怎样打扮也掩饰不了缺陷。','“丑小鸭”是“我”否定自己的看法。'],note('p2-confidence'),'answer',42);
standard('仿写句子 · 先独立写一句',['例：在我看来，丑小鸭就是丑小鸭，\n永远都成不了天鹅。','在我看来，________就是________，','________。'],note('p2-imitation')+'\n第一课文字作答1。可仿用句式，不必赞同原句。','question',42);
standard('仿句参考 · 表达自己的看法',['在我看来，朋友就是愿意真诚相待的人，','不会只凭外表评价别人。','“在我看来”＋判断＋相关说明'],note('p2-imitation')+'\n先收取学生句子再显示示例。','answer',42);
standard('第三段 · 两种不同的心情',['“我”和同学们的心情有什么不同？','先说同学，再说“我”。','用“却”连起两种心情。'],note('p3-mood'),'question');
standard('期待拍照与害怕拍照',['同学：兴致勃勃，积极讨论和摆姿势。','“我”：心沉到谷底，心情低落。','区别源于“我”对自己的外表缺乏信心。'],note('p3-mood'),'answer',42);
await comic('第四段 · 轮到“我”拍照',16,'原漫画第16格对应第4段。先读第4—5段完整原文，再观察画面帮助理解；答题以原句为准。');
standard('第四、五段 · 反应与原因',['轮到“我”拍照时，“我”有什么反应？','为什么“我”会有这样的反应？','先独立写，再比较。'],note('p4-response')+'\n第一课文字作答2。','question');
standard('反应与原因，要分开回答',['反应：做了什么？心里怎样？神态怎样？','原因：为什么这样？联系前文哪一句？','不能用“因为慌乱”解释“心里慌乱”。'],'先让学生独立写答；需要时才提供此框架。要求反应＋原因，避免循环解释。');
standard('反应参考 · 至少两种表现',['慢吞吞走上前，拘束地站着。','心里慌乱，更加局促不安，脸红发烫。','沮丧地说：自己没有美的姿势。'],note('p4-response'),'answer',42);
standard('原因参考 · 连接前文',['对外表没有信心，觉得掩饰不了缺陷。','不知道怎样面对镜头和同学的注视。','别人的目光，让“我”更紧张。'],note('p4-response'),'answer',42);
standard('教室为什么突然安静？',['轮到“我”拍照时，','教室里为什么突然变得无比安静？','同学的具体想法，原文写明了吗？'],note('p4-response')+'\n教参补充原题，口头讨论，不增加打字。可推测大家把注意力转向“我”，不能断言嘲笑。','question');
standard('第一课 · 用已有答案自检',['比喻：有没有写出具体感受与心理？','反应和原因：有没有分别说明？','原文证据：有没有把“我觉得”当事实？'],'第一课最后4分钟，对照已有回答并订正，整理收藏词语。不加新出口题。');
lesson=2;
standard('第二课 · 什么帮助“我”改变',['读第6—10段，按段落顺序思考。','老师与同学做了什么？','这些言行怎样影响“我”？'],'回顾前文3分钟。第二课两项书写为主题题和必做开放题。','section');
standard('第六段 · 怎样理解老师的话',['你如何理解这句话？','“这个世界上每个人都有自己','最美丽的姿势。”'],note('p6-meaning'),'question');
standard('每个人都有可以自信的一面',['即使有不完美，也有值得欣赏的地方。','老师先肯定“每个人”，','再请大家帮助宜欣找到美。'],note('p6-meaning'),'answer');
await comic('第七段 · 帮助变成具体行动',24,'原漫画第24格，老师为宜欣拍下照片。先读第7段动作；原文的左右手细节以文字为准。');
standard('第七段 · 照片展的用意',['你认为陈老师为什么提议办照片展？','联系照片展名称、老师说的话和做法。','哪些是明写的信息？哪些是你的推测？'],note('p7-purpose'),'question',42);
standard('用言行支持对目的的推测',['希望学生发现、展现自己的美。','也学会欣赏、帮助和鼓励同学。','这是有依据的推测，不能说只为宜欣办展。'],note('p7-purpose'),'answer',42);
standard('第八段 · 为什么鼓掌',['为什么同学们都鼓起掌来？','同学先说了什么？','联系前文，掌声还可能有什么用？'],note('p8-applause'),'question');
standard('掌声 · 赞美与鼓励',['直接信息：同学觉得照片好看。','结合前文：希望鼓励因外表而自卑的宜欣。','感动落泪是反应，不能倒过来当鼓掌原因。'],note('p8-applause'),'answer',42);
standard('第九段 · 变化与原因',['“我”后来发生什么变化？','为什么“我”会发生这样的变化？','分别找心态、行动和促成变化的原因。'],note('p9-change'),'question');
standard('变化 · 从心态走向行动',['照片与肯定 → 发现自己也可以很美。','找回信心和勇气 → 突破心防。','主动交流、结交朋友；没有脖子复原的情节。'],note('p9-change'),'answer',42);
standard('第十段 · “姿势”的意思',['这里“姿势”的意思和前面的一样吗？','先解释拍照时的“姿势”，','再解释结尾的“姿势”。'],note('p10-posture'),'question');
standard('从动作，写到人的优点',['前面：拍照时摆出的具体动作。','结尾：自身优点，或值得自信的一面。','由宜欣一个人的经历，写到每个人。'],note('p10-posture'),'answer',42);
standard('关键句 · 先分清两种作用',['抒情句：直接表达情感。\n例：“多么令人高兴啊！”','议论句：提出看法或道理。\n例：“真诚能帮助人建立友谊。”'],'课本巩固练习二之前先解释概念。例句为教师补充。不要先公布本课关键句。','concept',42);
standard('课本巩固练习二 · 关键句与主题',['找出课文中的关键句，','结合内容理解文章的主题。','找抒情句、议论句，再写主题与内容依据。'],note('theme')+'\n第二课文字作答1。两个证据框可累加多句；主题不可只抄原文。','question',44);
standard('关键句参考',['抒情句：“原来，我也可以很美！”','议论句：第10段的两句话。','从“每个人或多或少都有不完美的地方”\n到“活得自信，活出精彩”。'],note('theme'),'answer',42);
standard('主题参考 · 连接经历与道理',['每个人都有不完美之处，','但可以发现自己的优点，自信生活。','宜欣获得帮助和肯定，重拾信心并主动交友。'],note('theme')+'\n可补充欣赏和鼓励他人的价值，但不能取代核心自信主题。','answer',42);
standard('课本巩固练习三 · 必做',['你觉得人们在结交朋友时，','比较注重外在美还是内在美？','为什么？'],note('open-friendship')+'\n第二课文字作答2。题目问实际观察；先回应，再谈应有态度。','question');
standard('理由要解释，例子要连接',['看法＋理由：比较看重什么？为什么？','例子：哪个具体行为能说明？','回扣：这个行为怎样影响友谊？'],'可讨论初识和长期相处的差别。两者都重视也可接受，但须回答比较关系或说明条件。');
standard('开放题示范 · 用课文说明',['我觉得长久友谊通常更看重内在美，\n因为真诚、体贴使人感到被理解。','甜甜热心帮助宜欣，同学们鼓励她，\n使她敢于交流，交到朋友。','这些行动帮助建立信任，\n说明内在美对友谊很重要。'],note('open-friendship')+'\n示例不是唯一立场，学生先答后显示。','answer',40);
standard('对照、订正、留下记录',['主题：关键句与情节有没有连起来？','开放题：有没有说清“为什么”？','订正后，可从检查页导出学习记录。'],'第二课最后3分钟。不新增短文、课后一周小测或打卡。主观题由教师核对；个人词语本可跨课收藏。');
await fs.writeFile(O+'/slides.json',JSON.stringify(deck,null,2));
for(const [i,sl] of pres.slides.items.entries()){const png=await pres.export({slide:sl,format:'png',scale:1});await fs.writeFile(O+`/slides/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await png.arrayBuffer()));console.log('Rendered',i+1,'of',deck.length);}
await(await PresentationFile.exportPptx(pres)).save(W+'/ppt-build/candidate.pptx');
await fs.writeFile(W+'/ppt-build/slide-count.txt',String(deck.length));console.log('PPT candidate exported',deck.length);
