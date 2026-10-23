import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=process.cwd(),out=root+'/repo/du/textbook/1hcl/unit3/xingyao-changi',L=JSON.parse(await fs.readFile(out+'/lesson.json','utf8'));
const P=Presentation.create({slideSize:{width:1280,height:720}}),M=[],tableOwners=[];
const K='Huawentong WenKai',S='Noto Serif CJK SC',blue='#185E94',ink='#1B354F',red='#B21F32';
const sheets=await Promise.all([1,2,3,4,5].map(n=>fs.readFile(out+'/assets/comic'+n+'.png')));let lesson=1;
function txt(s,t,x,y,w,h,z=44,font=K,color=ink,bold=false){const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0,style:'solid'}});q.text=t;q.text.style={fontSize:z,typeface:font,color,bold,wrap:true,autoFit:'none',lineSpacing:1.15,verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};return q}
function sl(title,notes=''){const s=P.slides.add();s.background.fill='#F7FBFE';txt(s,title,58,32,1160,112,48,K,blue,true);txt(s,String(M.length+1),1155,657,65,48,38,S,blue);s.speakerNotes.text=notes+'\n来源：教师提供的《魅力四射 星耀樟宜》课文、阅读放大镜、读后说、教参与五页原漫画。日期和数据按课文理解。';M.push({title,notes,lesson,image:'slides/slide-'+String(M.length+1).padStart(2,'0')+'.png'});return s}
function body(title,text,notes='',z=44,font=K){const s=sl(title,notes);txt(s,text,65,168,1145,468,z,font);return s}
function panel(s,n,x,y,w){const[a,b,c,d]=L.panelRects[n-1];s.images.add({blob:sheets[L.panelSheets[n-1]-1],contentType:'image/png',alt:'原漫画第'+n+'格',fit:'cover',position:{left:x,top:y,width:w,height:w*d/c},crop:{left:a/1024,top:b/1536,right:(1024-a-c)/1024,bottom:(1536-b-d)/1536}})}
function pic(title,text,n,notes=''){const s=sl(title,notes);txt(s,text,65,178,680,450,43);panel(s,n,785,188,430);return s}
function question(title,text,id,n){const t=L.tasks.find(t=>t.id===id),notes=t.role+'\n'+t.source+'\n'+t.hints.join('\n');const s=n?pic(title,text,n,notes):body(title,text,notes,44);for(const x of s.shapes.items)for(const k of t.keywords)try{x.text.get(k).color=red}catch{}return s}
function table(title,values,widths,notes=''){const s=sl(title,notes),tb=s.tables.add({rows:values.length,columns:values[0].length,left:65,top:176,width:1150,height:430,columnWidths:widths,values});tableOwners.push(M.length);tb.borders.assign({fill:'#B9CCD9',width:1,style:'solid'});for(let r=0;r<values.length;r++)for(let c=0;c<values[r].length;c++){const cell=tb.getCell(r,c);cell.fill=r===0?'#DDEBF5':'#FFFFFF';cell.text.style={fontSize:38,typeface:K,color:ink,bold:r===0,wrap:true,autoFit:'none',verticalAlignment:'middle',insets:{left:16,right:16,top:12,bottom:12}};}return s}
let s=sl('中一高级华文 · 单元三','核心课文，建议三课各40分钟，或两课各50分钟。具体节奏见教师资料。');txt(s,'魅力四射\n星耀樟宜',65,190,690,230,76,K,blue,true);txt(s,'数字与例子怎样说明特点',65,485,700,76,40,S);panel(s,1,800,220,410);
body('本课的阅读重点','找到事物的特点。\n\n读准数字的对象和单位。\n\n解释：数字或例子怎样说明特点？','四个目标详见教师文件。本页不展开术语墙。',48,S);
body('第一课 · 自读第1—3段','按段读原文，对照原漫画。\n\n遇到不懂的词，可以点词查看。\n\n留意小标题和数字。','自主阅读，允许看图和查词，不要求额外打卡或留痕解锁。',48,S);
question('第1段 · 作者的提醒','星耀樟宜只是一个\n休闲娱乐的好去处吗？\n\n“不过”之后，作者怎样提醒读者？','intro',3);
body('第1段 · 暂时保留的问题','第1段先说它是休闲娱乐的好去处，\n又提醒我们不能只当它是普通购物中心。\n\n还有哪些特点？\n带着这个问题继续读。',L.tasks[0].explain,44);
question('小标题 · 阅读的提示','文中的小标题有什么作用？\n\n以“令人赞叹的外形设计”为例。','exterior');
body('小标题 · 作用','概括这一部分的内容。\n\n提示作者介绍的是哪一个方面。\n\n读者因此更容易抓住重点。','课文小标题没有给出游览先后或吸引力排名。',48);
question('第2段 · 每片玻璃','结合上下文，\n推断“独一无二”的意思。\n\n“看似一样”与“实际上”有何不同？','exterior',8);
body('每片玻璃 · 语境义','表面上好像一样，\n实际上每片都按所在位置量身定制。\n\n“独一无二”指没有完全一样的另一片。','不能解释为只有一片玻璃。',46);
body('列数字 · 从数据读到特点','“有很多横梁”只说多。\n\n“大约1万8000根”把数量写具体。\n\n再想：这怎样帮助说明外壳设计？','我做：数字本身不等于作用。联系9000多片特制玻璃及量身定制说明构造精细，不推出安全性。',44,S);
table('统整表 · 建筑外壳',[['项目','内容'],['特点','设计独特，构造精细'],['说明依据','约1万8000根横梁\n9000多片特制玻璃'],['方法','列数字']],[240,910],'课本表第一行。小标题提示方面；“像一颗宝石”的比喻另作口头赏析。');
question('第3段 · 雨漩涡','为什么要提“雨漩涡”的高度？\n\n数字说明了什么具体特点？','waterfall',11);
body('40米 · 高度的作用','40米，从五楼一直到地下二楼。\n\n数字让读者具体了解瀑布有多高，\n突出高大壮观的特点。','教材称“目前世界上最高”；按课文理解。仅凭40米一个数字不能独立证明世界排名。',46);
question('第3段 · 环保功能','从哪里看出“雨漩涡”具环保功能？\n\n找出完整依据，可以加入两句原文。','waterfall');
body('环保功能 · 两处依据','水通过水管循环使用，因此不造成浪费。\n\n除了供人观赏，还能帮助降低室内温度。\n\n用水量大，不等于浪费同样多的水。','依据第3段后两句。可以连续点选加入证据；不能写成已知节省多少电。',43);
table('统整表 · 雨漩涡',[['项目','内容'],['特点','高大壮观，兼具环保功能'],['说明依据','高40米\n每日用水多达50万公升，可循环'],['方法','列数字']],[240,910],'把水量、循环和功能区分；并补充降低室温。');
lesson=2;
body('第二课 · 自读第4—7段','一次读一段，继续完成统整表。\n\n哪些数字说明“多”？\n\n哪些例子说明“特别”？','先读后练。按第4、5、6、7段推进，不提前做跨段综合。',47,S);
question('第4段 · 室内绿洲','为什么说“森林谷”是室内绿洲？\n\n找植物的数量、种类，\n以及访客的感受。','forest',18);
table('森林谷 · 数字的对象',[['课文数据','说明什么'],['超过2000棵树木\n超过10万株灌木','植物数量多'],['约120个植物品种','种类丰富'],['两棵超过100岁的橄榄树','其中有古老树木']],[650,500],'对象和单位要一起读。树龄不是机场年龄；品种不等于棵数。');
body('举例子 · 具体说明','课文说植物来自世界各地。\n\n具体例子：两棵百年橄榄树来自西班牙。\n\n读者因此更清楚地了解植物来源。','先教举例子，再完成统整表方法一栏。百年说明树龄，西班牙说明来源。',45,S);
table('统整表 · 森林谷',[['项目','内容'],['特点','植物繁多，品种与来源丰富'],['说明依据','数量与品种数据\n来自西班牙的百年橄榄树'],['方法','列数字和举例子']],[240,910],'说明绿色环境让短暂逗留的访客也能放松，领略花园城市魅力。');
question('第5段 · 游乐设施','这里举的例子，\n是要说明什么特点？\n\n天悬桥、镜子迷宫、天空之网。','play',25);
body('设施与体验 · 例子怎样支持特点','天悬桥：云雾中行走，仿佛腾云驾雾。\n\n镜子迷宫：奇幻而神秘。\n\n天空之网：令人步步惊心。\n\n共同说明：别具一格，好玩又刺激。','腾云驾雾在此是感觉，不是真的飞天。蹦跳网还有腾空而起的感觉。',41);
table('天空之网 · 长度与高度',[['设施','长度','离地高度'],['步行网','50米','25米'],['蹦跳网','250米','课文未说明']],[360,320,470],'两个长度与一个高度不可混淆。没有提供的高度不猜测。');
question('独立短答 · 数字的作用','这里提到步行网离地面25米高，\n有什么作用？\n\n先找原句，再写完整回答。','height-effect');
body('作用题 · 答题结构','说明方法\n\n数字具体说明了什么\n\n这怎样帮助读者理解事物的特点','框架不直接给本题答案。学生独立写，教师按意义给分。',48,S);
body('25米 · 一种完整回答','作者运用列数字的说明方法，\n具体写出步行网离地面25米高。\n\n结合走起来摇摇晃晃、需要胆量，\n让读者理解它惊险刺激的特点。','参考3分：方法、具体高度、与刺激特点的联系各1分。只说生动形象不够；不可推出不安全。',43);
table('统整表 · 游乐设施',[['项目','内容'],['特点','别具一格，好玩又刺激'],['说明依据','天悬桥、镜子迷宫、天空之网\n步行网长50米，离地25米'],['方法','列数字和举例子']],[240,910],'完整依据还包括蹦跳网长250米、跳起如腾空。');
question('第6段 · 美食的选择','为什么要提到200多家商店？\n\n除了列数字，有举例子吗？','food',34);
body('统计范围 · 商店与餐馆','课文写“200多家商店”，\n“其中不少”与吃有关。\n\n不能把全部商店都改成餐馆。\n\n准确数量与范围，都要保留。','学生先判断范围。原题教参“现场里的美食”保留在网页，课件作简洁呈现。',44);
table('统整表 · 美食',[['项目','内容'],['特点','种类丰富，选择多样'],['说明依据','200多家商店\n零食店、甜品店、饮料店、特色餐馆'],['方法','列数字和举例子']],[240,910],'例子说明饮食选择多样；本地难得一见的美食增加吸引力。');
question('第7段 · 迷人与魅力','为什么说星耀樟宜\n是一个很迷人、很有魅力的地方？\n\n回看自己的五方面统整表。','ending');
body('全文结构 · 总分总','开头：提醒读者它不只是普通购物中心。\n\n中间：从五方面具体介绍特点。\n\n结尾：让人放松身心，增添机场魅力。','读完全篇后才作结构综合。“总分总”补充英文 overall–details–overall 可按需口头解释。',45);
body('结尾 · 与时俱进','“时代在发展”\n\n“与时俱进，不断创新”\n\n意思是跟着时代发展不断进步、创新。','课本预习二第3项。不能把“时”解释为营业时间或旅客停留时间。',46);
lesson=3;
body('第三课 · 词语与推荐','先看共同字怎样帮助理解词语。\n\n再选三个地方，向朋友说明推荐理由。\n\n每个理由都要有具体依据。','词语12分钟，推荐21分钟，检查7分钟。',47,S);
body('词语串串串 · 课本例子','木：树木、灌木、草木、木材、木柴\n\n桥：天悬桥、波浪桥、木桥、铁桥、吊桥\n\n顶：屋顶、房顶、山顶、楼顶、头顶\n\n习：学习、练习、补习、预习、复习','先观察共同字在这些词中的意义，再归类。',40);
question('词语串串串 · 课本原题','下面这些字代表什么类别？\n写一写它们构成的词语。\n\n盒　书　杯　馆　衣　树','word-families');
table('词语串串串 · 参考一',[['字与类别','可以写的词语'],['盒：盒状容器','饭盒、纸盒、笔盒、礼盒'],['书：书籍','故事书、工具书、教科书、百科全书'],['杯：杯状器皿','水杯、茶杯、酒杯、奖杯']],[340,810],'接受正确的其他词语。图书馆是场所，不是一本书。');
table('词语串串串 · 参考二',[['字与类别','可以写的词语'],['馆：活动或服务场所','图书馆、博物馆、美术馆、体育馆'],['衣：衣服','上衣、外衣、雨衣、泳衣'],['树：树木','雨树、椰树、橄榄树、苹果树']],[440,710],'“树立”中的树表示建立，不属于树木一类。按语境判断，不按字形机械分类。');
question('读后说 · 必做','向你的朋友推荐星耀樟宜\n最有吸引力的三个地方，\n并说明理由。','recommend');
body('推荐 · 说清为什么','建议：推荐哪里？\n理由：朋友有什么兴趣或需要？\n依据：课文中的哪项数字或例子？\n回扣：这个特点怎样适合朋友？','保留课本三个地方，不缩减为一个。先独立构思和写答，再展示示范。',44,S);
pic('一种合理推荐 · 雨漩涡','朋友喜欢新奇景观。\n\n课文写雨漩涡高40米，\n能让朋友欣赏壮观的室内瀑布。',13,'示范推荐一；非唯一答案，不要求学生真去过。');
pic('一种合理推荐 · 森林谷','朋友喜欢大自然。\n\n约120个植物品种，\n还有来自西班牙的百年橄榄树，\n适合观察植物、放松身心。',23,'示范推荐二；文本依据与朋友兴趣连接。');
pic('一种合理推荐 · 天悬桥','朋友喜欢新奇体验。\n\n桥上不时喷出云雾，\n走起来仿佛腾云驾雾，\n能满足朋友体验新环境的兴趣。',26,'示范推荐三；不能编造免费、无须预约等旅游信息。');
body('对照 · 推荐的依据与理由','每处都要有准确的课文依据。\n\n每处都要说清它怎样吸引朋友。\n\n三个地方可以不同，合理理由也可以不同。','教师参考9分，每处3点：不同且明确的地方、准确依据、与朋友需要的联系。各处独立给分。',45,S);
body('当堂检查','数字：对象、单位、限制词有没有保留？\n\n作用：有没有说明具体特点？\n\n推荐：有没有解释为什么？\n\n订正答案，整理词语，导出记录。','本课7组客观任务按组统计首次全部答对率；3组主观任务由教师核对，不当作自动总分。',42,S);
await fs.mkdir(root+'/build/ppt',{recursive:true});
for(let i=0;i<P.slides.items.length;i++){const b=await P.export({slide:P.slides.items[i],format:'png',scale:1});await fs.writeFile(out+'/'+M[i].image,new Uint8Array(await b.arrayBuffer()));if(i%10===0)console.log('rendered',i+1)}
await fs.writeFile(out+'/slides/slides.json',JSON.stringify(M,null,2));await(await PresentationFile.exportPptx(P)).save(root+'/build/ppt/candidate.pptx');
await fs.writeFile(root+'/build/ppt/manifest.json',JSON.stringify({slideCount:M.length,tableOwners}));console.log('EXPORTED',M.length);
