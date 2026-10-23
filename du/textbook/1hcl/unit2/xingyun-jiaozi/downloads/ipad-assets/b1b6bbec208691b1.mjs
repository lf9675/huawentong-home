import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation} from '/root/.codex/skills/builtins/presentations/container_tools/artifact_tool_utils.mjs';
const root=process.cwd(),out=root+'/repo/du/textbook/1hcl/unit2/xingyun-jiaozi';
const L=JSON.parse(await fs.readFile(out+'/lesson.json','utf8'));
const P=Presentation.create({slideSize:{width:1280,height:720}}),M=[];
const K='Huawentong WenKai',S='Noto Serif CJK SC',blue='#185E94',ink='#1B354F',red='#B21F32';
const sheets=await Promise.all([1,2,3,4].map(n=>fs.readFile(out+'/assets/comic'+n+'.png')));
let lesson=1;
function txt(s,t,x,y,w,h,z=42,font=K,color=ink,bold=false){const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0,style:'solid'}});q.text=t;q.text.style={fontSize:z,typeface:font,color,bold,wrap:true,autoFit:'none',lineSpacing:1.16,verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};return q}
function sl(title,notes=''){const s=P.slides.add();s.background.fill='#F7FBFE';txt(s,title,58,32,1160,112,48,K,blue,true);txt(s,String(M.length+1),1155,657,65,48,38,S,blue);s.speakerNotes.text=notes+'\n来源：教师提供的《幸运饺子》课文、巩固练习、教参与四页原漫画。';M.push({title,notes,lesson,image:'slides/slide-'+String(M.length+1).padStart(2,'0')+'.png'});return s}
function body(title,text,notes='',z=44,font=K){const s=sl(title,notes);txt(s,text,65,165,1145,468,z,font);return s}
function panel(s,n,x,y,w){const[a,b,c,d]=L.panelRects[n-1];s.images.add({blob:sheets[L.panelSheets[n-1]-1],contentType:'image/png',alt:'原有漫画第'+n+'格',fit:'cover',position:{left:x,top:y,width:w,height:w*d/c},crop:{left:a/1024,top:b/1536,right:(1024-a-c)/1024,bottom:(1536-b-d)/1536}})}
function q(id,n){const t=L.tasks.find(t=>t.id===id);const display=({swap:'“偷龙转凤”是什么意思？\n\n为什么加引号？',open:'结合课文内容和自己的生活经验，\n说说你对第8段内容的理解。',sentence:'仿写句子。\n\n例：吃没吃到幸运饺子并不重要，\n重要的是，我们一家人能够\n开开心心地团聚在一起。',compare:'上网查一查，然后和同学讨论：\n中国北方过农历新年和新加坡\n有什么不同。'})[id]||t.questions.join('\n\n');let s;if(n){s=sl(t.title,t.role+'\n'+t.source+'\n'+t.hints.join('\n'));txt(s,display,65,180,680,420,44);panel(s,n,790,188,420)}else s=body(t.title,display,t.role+'\n'+t.source+'\n'+t.hints.join('\n'),43);for(const shape of s.shapes.items)for(const w of t.keywords)try{shape.text.get(w).color=red}catch{}return s}
let s=sl('中一高级华文 · 单元二','巩固课文，1—2课时。建议两课各40分钟，第一课至第5段；已预读可按教师文件压缩为50分钟。');txt(s,'幸运饺子',65,204,700,120,78,K,blue,true);txt(s,'巩固课文\n人物用意 · 词句 · 线索与主题',65,398,680,150,40,S);panel(s,1,800,200,410);
s=sl('第1段 · 年年包饺子','导入口头题来自教参。课文只明确传统与喜悦；象征团聚、好运为资料补充。中国文化网，2021-02-08，https://en.chinaculture.org/a/202102/08/WS6020a52ca31024ad0baa800a.html ，2026-10-22核对。');txt(s,'中国北方人为什么喜欢\n在大年三十吃饺子？\n\n结合第1段，说说你的想法。',65,185,720,400,44);panel(s,2,820,205,380);
body('第一课 · 自主读第1—5段','按段读原文，对照漫画。\n\n碰到不懂的词，可以点词查看。\n\n读完后想一想：谁做了什么？','7分钟自读，不要求写额外阅读记录。读文区一次一段，漫画直接展示。',46,S);
q('mark',8);
body('第2段 · 维护游戏规则','做记号，就能有意挑出幸运饺子。\n\n姑姑阻止“我”做记号，\n让谁吃到它仍由偶然决定。','我做：先定位“偷偷做记号”“却被姑姑打了手”，再示范从行为推断目的。补充口头问题：红枣和祝福有什么特别？包饺子基本步骤是什么？不把祝愿当作保证。',46);
q('grandma');
s=sl('第3段 · 行动与心意','直接信息已在“因为”后交代，不强行增加推断。检查学生有行动、原因和心意。');txt(s,'行动：把幸运饺子夹给奶奶。\n\n原因：奶奶向来最疼爱“我”。\n\n心意：把祝愿送给奶奶。',65,180,720,440,43);panel(s,14,820,204,380);
q('wink',15);
body('第4段 · 动作传递默契','“眨眨眼”较隐蔽，\n不容易被其他人发现。\n\n不用说出来，“我”也能明白\n奶奶已经知道这份心意。','我们做：默契（tacit understanding）。微笑主要表示慈爱、开心；不能同样具体地表达隐蔽的会意。追问奶奶为什么转送给妈妈：体谅工作与照顾一家人的辛苦，祝她幸福。',44);
q('careful',20);
body('人物题 · 用行为证明','自己的判断\n\n具体行为：谁做了什么？\n\n解释：这为什么说明人物的特点？','本题原题已给出“细心”，不提供人物特点选项。学生独立找第2、5段两处证据并写答；可连续加入多句原文。',47,S);
body('姑姑细心 · 参考答案','“我”偷偷做记号时，姑姑发现并阻止。\n\n妈妈趁她不注意换碗，她马上发现。\n\n这些行为说明她能留意细小的变化。','教师参考3点：两处具体行为各1，解释1。只抄“姑姑是个细心的人”不能证明自己；“手巧”不能直接证明这里的细心。学生先写后揭示。',42);
lesson=2;
body('第二课 · 自主读第6—8段','幸运饺子又到了谁的碗里？\n\n爸爸真的不受关心吗？\n\n最后一段，作者认为最重要的是什么？','6分钟自读。阅读问题只帮助关注，不另增三道书面题。',46);
body('第6段 · 词的本义与语境义','偷龙转凤\n\n本义：用欺骗的手法，\n暗中改变事物的内容。\n\n放回句子：谁？怎样做？改了什么？','先解释本义再练习。接着问文中的具体意思和引号作用，不把姑姑的行为定性为做坏事。',42,S);
q('swap',23);
body('第6段 · 借词写动作','姑姑趁“我”不注意，\n把幸运饺子放到“我”的碗里。\n\n引号提示借用这个词，\n形容她悄悄送来祝福的做法。','两个选择判断分别检查语境义与引号。常见误读：把妈妈换碗当成姑姑的动作；只写字典义；误以为成语在这里谴责姑姑。',44);
q('family');
body('第7段 · 传来传去的原因','家人想把美好的祝愿送给彼此，\n说明家庭关系融洽、互相关爱。\n\n爸爸碗里的普通饺子也带着心意，\n因此称为“幸运饺子”。','回看“装出”“大家立刻”。第6段“我”已吃到红枣饺子；第7段满满一碗并非许多个红枣饺子。',42);
body('第8段 · 课文结尾',L.paragraphs[7],'完整原文。先读，再进入全文综合，避免只凭漫画概括。',48);
body('线索与主题','线索：用什么把几件事串起来？\n\n主题：借这些事情表达什么想法？\n\n先看课本七行内容，再作判断。','事物线索像一根线把几件事串起来。词语反复出现只是线索之一，还要说明能连接情节。',46,S);
q('thread');
body('课本第二题 · 第1—4段','第1段：喜欢吃到幸运饺子的喜悦。\n\n第2段：姑姑包红枣，送上祝福。\n\n第3段：“我”把饺子夹给奶奶。\n\n第4段：奶奶把饺子夹给妈妈。','本页是课本表格内容的情节概括，不伪称逐字原文。网页保留课本七行完整内容。先比较，不揭示线索和主题答案。',41);
body('课本第二题 · 第5—7段','第5段：妈妈与姑姑换碗。\n\n第6段：姑姑悄悄把饺子给“我”。\n\n第7段：大家把饺子夹给爸爸，\n　　　　一家人都笑了。','概括。第7段饺子已经是承载关爱的普通饺子。线索的含义有延伸，不能把每只都当成红枣饺子。',43);
body('全文 · 线索与主题的答案','线索：幸运饺子。\n\n它串起包、转送、吃到与最后的玩笑。\n\n主题：家人互相关爱，\n　　　开心团聚比谁得到幸运更重要。','学生提交后揭示。线索是具体事物，主题是中心意思。若只答“幸运饺子”作为主题，需补充表达的思想。',43);
q('open');
body('开放回应 · 说清为什么','看法：我怎样理解？\n理由：为什么？\n依据：课文中有什么事？\n例子：我自己有过什么经历？\n回扣：这怎样支持我的看法？','9分钟独立作答。只用一个多行输入框，避免五个输入框增加操作负担。不编造学生个人经历，接受合理不同立场。',43,S);
body('开放回应 · 对照方法','课文中，家人把饺子传给彼此，\n表达了互相祝福的心意。\n\n再检查自己的真实经历：\n谁做了什么？你有什么感受？\n这怎样说明团聚或关爱的价值？','这页是答案组织示范，不是完整个人经历范文。教师逐一核对理解与理由、课文依据、个人经历、解释回扣，各1点，不自动打分。',41);
q('sentence');
body('仿句 · 一种合理示范','比赛有没有拿第一并不重要，\n重要的是，我们在准备和比赛中\n学会合作。\n\n前后谈同一件事，并比较轻重。','教师拟写。学生先写再看。接受其他语境；检查不能前面谈名次、后面突然谈无关事情。必要的诚信、安全不宜被轻易否定。',43);
q('compare');
body('两地过年 · 比较同一方面','中国北方：常见全家包饺子、吃饺子。\n\n新加坡华人：常见一起捞鱼生、\n　　　　　　说吉祥话。\n\n做法有不同，都能寄托祝福与团聚之情。','资料：'+L.sources.map(s=>s.label+' '+s.url).join('\n')+'\n2026-10-22核对。口头讨论后揭示。不能推出新加坡人不吃饺子，或北方人不吃鱼生。',40);
body('当堂检查','人物判断，有没有行为证据？\n\n词语解释，有没有放回句子？\n\n线索与主题，有没有分清？\n\n开放回应，有没有解释为什么？','检查订正，整理个人词语，按需导出记录。未自动评分的题由教师覆核。',44,S);
await fs.mkdir(root+'/build/ppt',{recursive:true});
for(let i=0;i<P.slides.items.length;i++){const b=await P.export({slide:P.slides.items[i],format:'png',scale:1});await fs.writeFile(out+'/'+M[i].image,new Uint8Array(await b.arrayBuffer()));if(i%8===0)console.log('rendered',i+1)}
await fs.writeFile(out+'/slides/slides.json',JSON.stringify(M,null,2));
const candidate=root+'/build/ppt/candidate.pptx';await(await PresentationFile.exportPptx(P)).save(candidate);
console.log('EXPORTED',M.length);
await fs.writeFile(root+'/build/ppt/manifest.json',JSON.stringify({slideCount:M.length,candidate}));
