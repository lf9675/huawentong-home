import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation} from '/root/.codex/skills/builtins/presentations/container_tools/artifact_tool_utils.mjs';
const root='/workspace/scratch/700b63fb1eec',out=root+'/site/du/textbook/2hcl/unit6/jiaxinxi';
const L=JSON.parse(await fs.readFile(out+'/lesson.json','utf8'));
const P=Presentation.create({slideSize:{width:1280,height:720}}),M=[];
const K='Huawentong WenKai',S='Noto Serif CJK SC',green='#176962',ink='#173D41',red='#B51C2D';
const sheets=await Promise.all([1,2,3,4,5].map(n=>fs.readFile(out+'/assets/comic'+n+'.png')));
function txt(s,t,x,y,w,h,z=42,font=K,color=ink,bold=false){const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0,style:'solid'}});q.text=t;q.text.style={fontSize:z,typeface:font,color,bold,wrap:true,autoFit:'none',lineSpacing:1.18,verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};return q}
function sl(title,notes='',lesson=1){const s=P.slides.add();s.background.fill='#FAFCFA';txt(s,title,55,32,1170,100,46,K,green,true);txt(s,String(M.length+1),1150,656,70,48,38,S,green);s.speakerNotes.text=notes+'\n来源：教师提供的课本74—77页、教参与原漫画。';M.push({title,notes,lesson,image:'slides/slide-'+String(M.length+1).padStart(2,'0')+'.png'});return s}
function body(title,text,notes='',lesson=1,z=44,font=K){const s=sl(title,notes,lesson);txt(s,text,65,160,1145,470,z,font);return s}
function panel(s,n,x,y,w){const[a,b,c,d]=L.panelRects[n-1];s.images.add({blob:sheets[L.panelSheets[n-1]-1],contentType:'image/png',alt:'原有漫画第'+n+'格',fit:'cover',position:{left:x,top:y,width:w,height:w*d/c},crop:{left:a/1024,top:b/1536,right:(1024-a-c)/1024,bottom:(1536-b-d)/1536}})}
function read(title,text,n,lesson=1){const s=sl(title,'原文节选。完整段落和全部原漫画在学生页面；先读原文，再看图，答案依据回到原文。',lesson);txt(s,text,60,152,730,475,40);panel(s,n,825,170,385);return s}
function question(id,sub=''){const t=L.tasks.find(t=>t.id===id);const s=body(t.title,t.questions[0]+(sub?'\n\n'+sub:''),'原题出处：'+t.source+'\n'+t.hints.join(' '),t.lesson,44);for(const q of s.shapes.items)for(const w of t.keywords)try{q.text.get(w).color=red}catch{}return s}
function answer(id,text=null){const t=L.tasks.find(t=>t.id===id);return body('核对 · '+t.title,text||t.answer,t.explain+'\n'+t.scoreGuide,t.lesson,42)}
let s=sl('中二高级华文 · 单元六','两课时，每课按50分钟。第一课第1—4段，第二课第5—8段与全文统整。');txt(s,'别上\n假信息的当',60,195,740,240,72,K,green,true);txt(s,'巩固课文 · 两课时',65,510,720,70,40,S);panel(s,2,825,200,385);
body('今天要练的阅读能力','辨认观点：作者想说明什么？\n\n解释事例：它怎样支持观点？\n\n提出方法：为什么能帮助判断？','不以事实背诵或转发次数作为主要检测。',1,44,S);
read('第1段 · 现象与观点',L.paragraphs[0],3);
question('p1-view','找出作者表明态度的原句。');answer('p1-view');
body('教师示范 · 观点与内容','现象：每天接触海量信息，其中有假信息。\n\n观点：千万不能小看它的影响。\n\n后文：从事例与危害解释这个观点。','口头追问核心课文首段与本段共同点：均在段末提出观点。不能推成所有文章都如此。',1,43);
read('第2段 · 传言不等于事实','据说，汉朝的刘邦在领兵打仗时，曾砍杀一条白蛇。\n\n杀蛇可能确有其事，但说杀了蛇会做皇帝就是典型的假信息。',7);
question('p2-example','事例中，哪一种推断没有依据？');answer('p2-example','流言把“杀蛇”说成“会做皇帝”的预兆。\n\n这说明古代已有假信息。\n\n“可能确有其事”仍然保留不确定性。');
question('p2-cause','本题要作合理推断，写清原因与传播的联系。');
answer('p2-cause','社会动荡 → 人们焦虑，急于了解情况\n\n未经查证便相信和转说\n\n因此，假信息可能传播得更广。');
read('第3段 · 数量、速度与范围','在资讯科技发达的今天，\n由于互联网的发展和手机的普及，\n假信息的数量和传播速度\n都远远超过了古代，\n影响更是无远弗届。',10);
question('p3-compare','先看古代方式，再比较现代的数量、速度、范围。');
answer('p3-compare','古代：多以流言或传闻传播。\n\n现代：借助互联网和手机。\n\n数量更多、速度更快、影响范围更广。');
body('词语 · 无远弗届','这条谣言影响无远弗届，遍及各地。\n\n“无远弗届”强调影响范围广，\n不能用来形容思考方式或内容详细。','先让学生在网页完成词语题，再揭示此页。此页讲评，不另做一套练习。',1,44);
read('第3段 · 两处证据一起看','本世纪初，一则“2012年世界末日即将降临”的流言借助互联网传遍世界各地。\n\n……不少人受到这则假信息的影响。',12);
question('p3-example','加入两句原文，再用“说明……”解释联系。');
answer('p3-example','证据：传遍世界各地；不少人受到影响。\n\n解释：假信息能传播到很广的范围，\n并且影响人们。','');
read('第4段 · 图像也能被修改','但是，如今人们却可以轻松地利用科技将图像改头换面，制造出更难分辨的虚假信息，让人更难发现事情的真相。',15);
question('p4-tech','注意“修改图像”与“辨别困难”的关系。');answer('p4-tech','科技能修改图像，使虚假内容看起来逼真。\n\n因此，我们更难辨别真假、发现真相。\n\n课文的“以前”不能直接换成“古代”。');
body('第一课 · 检查解释是否到位','事例不只要复述，还要联系观点。\n\n推断不只要合理，还要解释关系。\n\n两道书面题：动荡原因、2012流言事例。','保留首次回答，完成订正；个人需要复习的词再收藏入词语本。',1,44,S);
body('第二课 · 危害与辨别','第5—6段：危害怎样发生？\n\n第7—8段：怎样减少危害？\n\n全文：这些内容怎样支持开头观点？','第二课仅句式仿写与开放回应需要键盘输入。',2,46,S);
read('第5段 · 三人成虎','如果只有一个人对魏王说街上出现老虎，他一定觉得不可能，也不会信。\n\n但如果很多人都跟他这样说，他就会信以为真。',21,2);
question('p5-mislead','用“反复出现的说法”和“人的判断”解释道理。');
answer('p5-mislead','假信息重复多了，会使人分不清真伪。\n\n原本不信 → 半信半疑 → 甚至信以为真\n\n重复次数多，不等于证据充分。');
body('词语 · 真伪与陷阱','辨别真伪：判断真假。\n\n“消息很真伪”不通。\n\n假信息的陷阱：诱使人受骗的圈套。','对照网页两个语境题；陷阱在课文用的是比喻义。',2,44);
read('第6段 · 信任是合作的基础','假信息的传播会破坏这种信任。如果人们缺乏基本的互信，真诚的合作也就无从说起。这样的社会很难取得进步，更无法跟上时代的步伐。',28,2);
question('p6-harm','在网页排列因果链，再口头把关系说完整。');
answer('p6-harm','假信息传播 → 破坏互信\n\n缺乏互信 → 难以真诚合作\n\n合作受阻 → 社会难以进步');
body('词语 · 步伐与步骤','跟上时代的步伐：跟上发展的进程。\n\n这道题的解题步伐 ×\n\n操作的先后次序，应说“步骤”。','先判断语境，再比较词义。',2,44);
read('第7段 · 方法要落实','我们可以通过对信息来源的查证，确定信息是否可靠，也可以通过多方询问、比较来辨别信息的真假。',36,2);
question('p7-method','查什么？问谁？比较哪些来源？');
answer('p7-method','不轻信，查证原始来源。\n\n多方询问与比较，留意来源是否独立。\n\n从小培养警觉与辨别能力，独立思考。');
body('一个必须分清的判断','多个转发 ≠ 多份独立证据\n\n暂时查不到证实 ≠ 已证明为假\n\n无法确定：先不转发，继续核实。','这是对课文方法的课堂应用解释。纠正旧题“官网查不到就说明是假的”。',2,46,S);
body('词语 · 询问与人云亦云','向老师询问通知的来源：打听情况。\n\n未经查证，跟着别人说消息属实：\n人云亦云。\n\n比较证据后同意别人，不等于盲从。','先完成网页点选，课堂只讲评。',2,42);
body('7b 句式仿写','要……，就要……。\n\n例：要减少假信息的危害，就要提高我们\n对假信息的警觉与辨别信息真伪的能力。\n\n前半句提目标；后半句说所需做法。','课本巩固练习第一题，保留例句。学生独立写一句。',2,42);
answer('p7-sentence','要提高辨别假信息的能力，\n就要学会查证信息来源。\n\n也可写其他内容，但目标与做法须有关联。');
read('第8段 · 回扣开头',L.paragraphs[7],40,2);
question('p8-ending','开头提醒什么？结尾总结什么？');
answer('p8-ending','开头：不能小看假信息的影响。\n\n结尾：提高警觉与辨别能力，\n增强社会互信与凝聚力。\n\n结尾总结应对方法与积极作用。');
body('词语 · 对假信息的免疫力','本来指身体抵抗疾病的能力。\n\n文中比喻：\n辨别并抵抗假信息影响的能力。','本课是比喻义，不是接种疫苗或记住信息的速度。',2,46);
question('whole-structure','在网页完成课本原表，九个填空只做一次。');
body('结构表核对 · 开头与传播','第1段：假信息古今普遍，影响不可小看。\n\n第2段：流言或传闻；动荡时更多、\n传得更广、影响更大。\n\n第3—4段：数量与速度超过古代；\n科技使辨别更困难。','对应原表前五空。第2段完整答案也应包含“影响更大”。',2,41);
body('结构表核对 · 危害与应对','第5—6段：把假的当成真的；\n破坏人与人之间的信任。\n\n第7—8段：提高警觉与辨别信息真伪的能力；\n增强互信与凝聚力。','对应后四空。主体对观点进行论述，结尾总结概括。',2,41);
question('open-response','建议—理由—例子—回扣。每一项都要写。');
body('开放题 · 虚构应用情境','班群传出：\n“明天全国学校停课一天，快转告同学！”\n\n你会怎样核实？为什么这样做有效？\n暂时无法确定时，怎么办？','沿用旧练习情境并入课本原题，不增加另一篇阅读。学生先个人回答，再讨论。',2,43);
body('示范 · 方法与理由','方法：查原始发布者，核对正式通知。\n\n理由：核实消息是否确有出处，\n避免把反复转发当成多份证据。','接受其他可执行方法，但必须解释有效性。',2,44);
body('示范 · 例子与回扣','例子：查看教育部或学校正式通知，\n并向老师核实。\n\n回扣：暂时无法确定，先不转发，\n继续核实，避免传播尚未证实的消息。','示范不是唯一答案。教师按具体方法、理由、应用、审慎处理四个意义点核对。',2,43);
body('当堂订正与记录','证据有没有支持答案？\n\n事例与观点的关系有没有说清？\n\n方法为什么有效，有没有解释？\n\n保存订正，导出学习记录。','首答保留不覆盖；自检不等于教师评分。个人词语本按需收藏，不强制收藏整份词表。',2,42,S);
await fs.mkdir(root+'/build/ppt',{recursive:true});
for(let i=0;i<P.slides.items.length;i++){const b=await P.export({slide:P.slides.items[i],format:'png',scale:1});await fs.writeFile(out+'/'+M[i].image,new Uint8Array(await b.arrayBuffer()));if(i%10===0)console.log('rendered',i+1)}
await fs.writeFile(out+'/slides/slides.json',JSON.stringify(M,null,2));
const candidate=root+'/build/ppt/candidate.pptx';await(await PresentationFile.exportPptx(P)).save(candidate);
execFileSync(process.env.CODEX_PRIMARY_RUNTIME_PYTHON,[root+'/build/dedupe_pptx.py',candidate]);
const base='/root/.codex/skills/builtins/presentations/container_tools';
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:out+'/downloads/jiaxinxi-v2.pptx',pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:base+'/inspect_presentation_package_integrity.py',layoutValidatorPath:base+'/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--expected-slide-count',String(M.length),'--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:[K,S]},requiredNativeTableOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:root+'/build/ppt/validation-release.json'});console.log('FINAL',M.length,result.finalSha256);
