import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation} from '/root/.codex/skills/builtins/presentations/container_tools/artifact_tool_utils.mjs';
const out=process.env.LESSON_DIR; if(!out)throw Error('Set LESSON_DIR to this lesson directory'); const root=process.cwd();
const L=JSON.parse(await fs.readFile(out+'/lesson.json','utf8'));
const P=Presentation.create({slideSize:{width:1280,height:720}}),M=[];
const K='Huawentong WenKai',S='Noto Serif CJK SC',blue='#175A87',ink='#19374B',red='#B51C2D';
const sheets=await Promise.all([1,2,3,4,5].map(n=>fs.readFile(out+'/assets/comic'+n+'.png')));
function txt(s,t,x,y,w,h,z=42,font=K,color=ink,bold=false){const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0,style:'solid'}});q.text=t;q.text.style={fontSize:z,typeface:font,color,bold,wrap:true,autoFit:'none',lineSpacing:1.2,verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};return q}
function sl(title,notes='',lesson=1){const s=P.slides.add();s.background.fill='#FFFFFF';txt(s,title,55,35,1170,92,46,K,blue,true);txt(s,String(M.length+1),1150,656,70,48,38,S,blue);s.speakerNotes.text=notes+'\n来源：教师提供的课文、课本问题、教参与原漫画。';M.push({title,notes,lesson,image:'slides/slide-'+String(M.length+1).padStart(2,'0')+'.png'});return s}
function body(title,text,notes='',lesson=1,z=43,font=K){const s=sl(title,notes,lesson);txt(s,text,65,166,1145,440,z,font);return s}
function panel(s,n,x,y,w){const [a,b,c,d]=L.panelRects[n-1];s.images.add({blob:sheets[L.panelSheets[n-1]-1],contentType:'image/png',alt:'原有漫画第'+n+'格',fit:'cover',position:{left:x,top:y,width:w,height:w*d/c},crop:{left:a/1024,top:b/1536,right:(1024-a-c)/1024,bottom:(1536-b-d)/1536}})}
function read(title,text,n,lesson=1){const s=sl(title,'先读原文，再看对应漫画。漫画为情境示意，答案依据来自课文。',lesson);txt(s,text,60,160,745,460,40);panel(s,n,825,180,385);return s}
function question(id,sub=''){const t=L.tasks.find(t=>t.id===id);const s=body(t.title,t.questions[0]+'\n\n'+sub,'先独立思考。'+t.hints.join(' '),t.lesson,44);for(const q of s.shapes.items)for(const w of t.keywords)try{q.text.get(w).color=red}catch{}return s}
function answer(id,text=null){const t=L.tasks.find(t=>t.id===id);return body('核对 · '+t.title,text||t.answer,t.explain+'\n'+t.scoreGuide,t.lesson,42)}
let s=sl('中二高级华文 · 单元六','完整版三课时。两课时压缩流程详见教师教案。');txt(s,'多元而开放的\n新加坡',60,200,740,240,66,K,blue,true);panel(s,1,835,210,360);
body('今天的阅读重点','从具体事例，理解作者的观点\n\n解释第五段怎样连接上下文\n\n用自己的例子说明多元与开放','保留课本目标。教师不以年代或文化名称背诵为主要检测。',1,44,S);
body('从生活空间接着想','上节课，我们读到新加坡与世界的联系。\n\n来自不同地方的人与文化，\n会给新加坡带来怎样的特色？','短导入2分钟，不重复上一课鸡饭活动。只听学生初步看法。',1,44);
read('第一段 · 作者的观点',L.paragraphs[0],2);
question('p1-view','留意时间范围和所写的特色。');answer('p1-view');
read('第二段 · 地理与贸易',L.paragraphs[1].split('考古人员')[0],4);
question('p2-position','找出位置和贸易作用。');answer('p2-position');
read('第二段 · 实物证据','考古人员曾经在福康宁山上挖掘出中国唐宋时期的钱币。\n\n由此可见，远在那个时候，新加坡就已经为海上丝绸之路的发展做出了贡献。',7);
question('p2-coins','证据之后，作者怎样得出结论？');
body('教师示范 · 由证据到解释','证据：福康宁山出土唐宋钱币。\n\n课文结论：很早已参与海上贸易。\n\n联系观点：支持“自古以来”。','边指原句边示范。不能只凭钱币推定所有族群、人口数量或开放的一切原因。',1,44);
answer('p2-coins','按课文的论述，唐宋钱币说明：\n\n远在唐宋时期，新加坡已参与海上贸易，\n为海上丝绸之路的发展作出贡献。');
read('第三段 · 命名的记载','作为中转站，新加坡一直以开放的心胸迎接着不同的族群。按《马来纪年》的记载，大约在十三世纪末，一位名叫山尼拉乌他马的王子来到这座小岛，将她命名为“新加坡拉”，也就是“狮城”。',11);
read('第三段 · 不同区域的人汇集','十四世纪开始，来自不同区域的人汇集到这个小岛，这里的族群也逐渐变得多元化。\n\n东南亚一些群岛的居民聚集在这里，成为最早的马来族群。',14);
read('第三段 · 华人到来与交流','十五世纪，郑和下西洋后，中国福建和广东等沿海地区的华人陆续来到这里，形成早期的华人群体。\n\n早期华人中有一部分和当地人通婚，他们的后代就是我们今天所说的峇峇和娘惹。',18);
question('p3-timeline','按课文顺序整理：人群汇集、华人到来、通婚与后代。');
body('核对 · 族群逐渐多元','十四世纪：不同区域的人汇集。\n\n十五世纪：华人陆续到来。\n\n部分华人与当地人通婚，形成后代。','通婚与后代没有明确年份，不强行补日期。此处只处理第三段，第四段随后学习。',1,44);
question('p3-relation','“人数多”和“族群多元”有什么区别？');answer('p3-relation');
read('第四段 · 新的族群与特色',L.paragraphs[3].split('新加坡虽然')[0],20);
read('第四段 · 开放接纳', '新加坡虽然是个小岛，却有着海纳百川的心胸。\n\n直到今天，她依然保有开放的态度，迎接来自五湖四海的朋友。',24);
question('p4-open','结合第三、第四段，说清人群怎样汇集。');
answer('p4-open','更多华人、欧洲人、淡米尔人到来。\n各族群带来新的特色。\n\n“海纳百川”形容开放包容的心胸。');
body('第一课 · 口头回顾','地理与贸易：怎样与外界发生联系？\n\n不同族群：怎样逐渐汇集和交流？\n\n这些内容怎样支持作者观点？','3分钟回顾，不重复做旧题。学生可口头回答，教师记录共同误区。',1,44);
body('第二课 · 生活与艺术','继续按段阅读：第五段至第七段\n\n看段落怎样衔接，\n看具体事例怎样支持观点。','本课仅第五段作用题需书面组织完整答案。',2,46,S);
read('第五段 · 连接上下文',L.paragraphs[4],25,2);
body('过渡段（transition）','连接前后的段落\n\n小示例：“交通方便，饮食也丰富。”\n前半回顾交通，后半带出饮食。','先建立概念，再分析课文。小示例只解释术语，不增加新篇章或额外练习。',2,44,S);
question('p5-link','承接上文什么？引出下文什么？');
answer('p5-link','承上：海上贸易与多元种族。\n\n启下：日常生活和文化艺术。\n\n因此，这一段起承上启下的过渡作用。');
read('第六段 · 货物流通','南来北往的船只，东奔西走的客商，把东南亚、印度的香料和中国的瓷器、丝绸、茶叶运到新加坡，再从这里运往世界各地。',26,2);
read('第六段 · 饮食体验','各种各样的食材和不同的饮食习惯给予人们不同的体验。\n\n想喝点什么？这里有清香的中国茶，也有浓郁的奶茶与咖啡。',29,2);
read('第六段 · 不同饮食并存','想吃点什么？这里有香喷喷的鸡饭和椰浆饭，也有香料味十足的黄姜饭。\n\n多元化的美食，常常会让很多初来乍到的游客啧啧称奇。',30,2);
question('p6-food','先按“喝的”“吃的”找全信息。');answer('p6-food');
read('第六段 · 文化艺术','与此同时，不同族群的文化艺术也在这块土地上生根发芽。\n\n这里有华族传统的南音，也有极富时代特色的新谣；有婉转悠扬的马来班顿诗，也有姿态优美的印度婆罗多舞。',35,2);
question('p6-art','先找形式与族群，再解释多元、传承与创新。');
body('核对 · 不同的艺术形式','华族：南音、新谣\n\n马来族：班顿诗\n\n印度族：婆罗多舞','配对是定位支架，后面必须回到观点解释。',2,46);
body('传承与创新','传统南音：接续已有文化。\n\n富有时代特色的新谣：发展新的形式。\n\n不同形式并存，也体现多元。','按照课文的“传统”“时代特色”解释，不说一种文化比另一种更高级。',2,44);
read('第六段 · 回扣观点','无论饮食还是艺术，我们都能从中看出传承与创新，更能从这美妙的多元文化中看出国人开放的心胸。',38,2);
read('第七段 · 延续特色',L.paragraphs[6],40,2);
question('p7-ending','“始终未变”回应了开头的哪个意思？');
answer('p7-ending','“始终未变”呼应“自古以来”。\n\n继续兼容并蓄，求同存异，\n才能共同开创未来。');
body('意义段与自然段','自然段：按书写形式划分。\n\n意义段：按内容划分，\n可包括一个或几个相邻自然段。','结合课本“第3—4段组成一个意义段”的已给例子。',2,46,S);
question('whole-structure','先按内容分组，再填写课本结构表。');
body('全文结构 · 前半篇','第1段：提出观点。\n\n第2段：地理位置与古代贸易。\n\n第3—4段：族群汇集与文化形成。','与网页第8组答案一致。',2,44);
body('全文结构 · 后半篇','第5—6段：生活和艺术中的多元开放。\n\n第7段：总结特色，展望未来。\n\n第5段同时起连接上下文的作用。','段落结构作用与意义段分组采用不同观察角度，两者不冲突。',2,44);
body('第三课 · 运用与表达','四字短语怎样组成、怎样使用？\n\n自己的例子怎样说明多元而开放？','先完成课本词语核对，再做四字短语，最后开放回应。',3,46,S);
question('words-prep','按课本指定段落找词，只核对一次。');
body('课本词语 · 核对','狭窄水道：海峡\n\n聚集：汇集\n\n胸怀宽广：海纳百川\n\n初次来到：初来乍到','注意课本第二项解释是“聚集”，应找出的词为“汇集”。',3,42);
body('四字短语 · 四方面','衣、食、住、行\n\n分别代表穿衣、饮食、住宿、交通，\n合起来表示日常生活。','先解释教材第一类，再观察下一页第二类。',3,46,S);
body('四字短语 · 两部分','求同＋存异：\n寻找共同点，保留不同点。\n\n引人＋瞩目：\n引起人们的注意。','两个双音节部分组成整体意思。按教材分类，不改为数字、反义、比喻分类。',3,44,S);
question('phrases','请在网页完成三句原题的替换。');
body('四字短语 · 替换核对','南方和北方之间来往：南来北往\n\n生育、养老、疾病、死亡：生老病死\n\n吸取长处、补足不足：取长补短','要求保留句中原意；可以口头读完整句子检查是否通顺。',3,43);
question('words-usage','四道短题：赋予、得天独厚、初来乍到、啧啧称奇。');
body('用词核对','赋予：给予新的意义。\n得天独厚：具有优越条件。\n初来乍到：刚到一个新地方。\n啧啧称奇：连声赞叹奇妙之处。','按网页答案比较语境。题库中四题正确项依次B、D、A、C；课堂应读选项内容，避免只记字母。',3,44);
question('open-response','先独立想具体例子，再解释为什么。');
body('开放题 · 说清理由','看法：我选择哪个方面？\n理由：为什么体现这个特色？\n例子：具体有什么事或现象？\n回扣：例子怎样支持看法？','学生独立书面回答，之后交流。主观题不能用字数或关键词自动判对。',3,44,S);
body('开放题 · 一种合理示范','学校的文化分享活动能体现多元与开放。\n\n同学介绍各自家庭习俗，\n大家交流并尊重不同做法。','这是情境示范，不冒充某个学生的真实经历。学生先答，再揭示此页。',3,44);
body('示范 · 为什么能说明？','保留各自特色，体现多元。\n\n相互接触、交流与尊重，体现开放。\n\n例子与看法之间的联系要说清楚。','不强制唯一例子。可用建筑、服饰、宗教等，但陈述须准确，不编造事件、人物或数据。',3,44,S);
body('当堂检查与订正','证据有没有真正支持答案？\n\n作用题有没有写清前后内容？\n\n开放题有没有解释“为什么”？','学生导出记录；教师检查首次答案与订正。词语本只收藏学生自己需要复习的词。',3,44,S);
await fs.mkdir(root+'/build/ppt',{recursive:true});
for(let i=0;i<P.slides.items.length;i++){const blob=await P.export({slide:P.slides.items[i],format:'png',scale:1});await fs.writeFile(out+'/'+M[i].image,new Uint8Array(await blob.arrayBuffer()));if(i%10===0)console.log('rendered',i+1)}
await fs.writeFile(out+'/slides/slides.json',JSON.stringify(M,null,2));
const candidate=root+'/build/ppt/candidate.pptx';await(await PresentationFile.exportPptx(P)).save(candidate);
execFileSync(process.env.CODEX_PRIMARY_RUNTIME_PYTHON,[root+'/build/dedupe_pptx.py',candidate]);
const base='/root/.codex/skills/builtins/presentations/container_tools';
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:out+'/downloads/duoyuan.pptx',pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:base+'/inspect_presentation_package_integrity.py',layoutValidatorPath:base+'/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--expected-slide-count',String(M.length)],fontPolicy:{basis:'user_request',families:[K,S]},requiredNativeTableOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:root+'/build/ppt/validation-final.json'});console.log('FINAL',M.length,result.finalSha256);
