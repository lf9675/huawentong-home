import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation} from '/root/.codex/skills/builtins/presentations/container_tools/artifact_tool_utils.mjs';
const root='/workspace/scratch/6e755f6b886c', out=root+'/huawentong-home/du/textbook/2hcl/unit6/xinjiapo-yu-shijie';
const L=JSON.parse(await fs.readFile(out+'/lesson.json','utf8')),meta=[];
const pres=Presentation.create({slideSize:{width:1280,height:720}});
const K='LXGW WenKai TC',S='Noto Serif CJK SC',blue='#154E75',ink='#19344B',red='#B51C2D';
const sheets=await Promise.all([1,2,3,4].map(n=>fs.readFile(out+'/assets/comic'+n+'.png')));
function text(sl,s,x,y,w,h,size=40,font=K,color=ink,bold=false){const sh=sl.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0,style:'solid'}});sh.text=s;sh.text.style={fontSize:size,typeface:font,color,bold,wrap:true,autoFit:'none',lineSpacing:1.22,verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};return sh;}
function slide(title,notes=''){const s=pres.slides.add();s.background.fill='#FFFFFF';text(s,title,54,32,1172,100,44,K,blue,true);text(s,'新加坡与世界的联系',54,655,1040,48,38,S,'#466379');text(s,String(meta.length+1),1155,655,70,48,38,S,'#466379');s.speakerNotes.text=notes;meta.push({title,notes,image:'slides/slide-'+String(meta.length+1).padStart(2,'0')+'.png'});return s}
function body(title,content,notes='',font=K,size=42){const s=slide(title,notes);text(s,content,64,160,1152,455,size,font);return s}
function panel(s,n,x,y,w){const [a,b,c,d]=L.panelRects[n-1];s.images.add({blob:sheets[L.panelSheets[n-1]-1],contentType:'image/png',alt:'原有漫画第'+n+'格',fit:'cover',position:{left:x,top:y,width:w,height:w*d/c},crop:{left:a/1024,top:b/1536,right:(1024-a-c)/1024,bottom:(1536-b-d)/1536}})}
function para(p){const s=slide('第'+p+'段 · '+L.paragraphLabels[p-1],`按原文朗读；漫画辅助理解，不作为额外证据。段意：${L.paragraphIdeas[p-1]}`);text(s,L.paragraphs[p-1],60,155,695,465,40);const ns=L.panels[p-1];panel(s,ns[0],840,160,330);if(ns.length>1){const h=330*L.panelRects[ns[0]-1][3]/500;panel(s,ns[1],840,175+h,330)}}
function question(t,extra=''){const s=body('课本问题 · '+t.title,t.questions.join('\n')+'\n\n'+extra,t.guide+'\n先不显示答案。'+t.hints.join('；'),K,42);const sh=s.shapes.items?.[2];for(const shape of s.shapes.items||[])for(const word of t.keywords)try{shape.text.get(word).color=red}catch{}return s}
function answer(t,extra=''){body('核对 · '+t.title,t.answer+'\n\n'+extra,t.explain+'\n'+t.scoreGuide,K,42)}
let s=slide('中二高级华文 · 单元六','50分钟：鸡饭3分钟，古代14分钟，现代19分钟，开放回应9分钟，词语与订正5分钟。');text(s,'新加坡与世界的联系',64,210,1150,110,62,K,blue,true);text(s,'生活空间\n从餐桌走向课文',70,375,1100,150,44,S);
body('今天，我们练习什么？','找全信息：货物、做法与发展方面\n\n根据题干，组织多个答案点\n\n提出新例子，解释与世界的联系','目标不以记住数字或猜国家为中心。',S,42);
body('一盘鸡饭，怎样连着世界？','鸡肉、米饭、青瓜……\n这顿饭为什么让你想到外地？\n\n鸡饭旁的一杯水，又可能有怎样的联系？','口头导入约1分钟。先听学生猜想，再呈现资料；不要求猜具体产地。',K,44);
body('两条资料，修正猜想','新加坡超过九成食物依靠进口，\n同时也有本地农业生产。\n\n部分原水来自马来西亚柔佛河。','资料：SFA Singapore Food Statistics 2025；PUB Imported Water。网址见教师教案。不能由整体资料断言本盘鸡饭或本杯水的来源。两条资料及转入课文约2分钟。',K,44);
for(let p=1;p<=4;p++)para(p);
question(L.tasks[0],'回看第二至第四段：找出三类货物。');
answer(L.tasks[0],'辨清：货物 ≠ 货物的用途。');
para(5);para(6);
question(L.tasks[1],'点原句取证，再独立写完整答案。');
answer(L.tasks[1],'圈出三个意思点，再检查是否遗漏。');
para(7);
question(L.tasks[2],'“不但……也……”连接了哪两项做法？');
answer(L.tasks[2],'共同身份与文化传承可以同时存在。');
para(8);
question(L.tasks[3],'找“推动”后的三个并列方面。');
answer(L.tasks[3],'高科技是手段；国民受惠是预期作用。');
question(L.tasks[4],'先独立写，再和同学分享。');
body('写清楚“为什么”','方面：我想说哪一种课外联系？\n例子：谁与哪个地方发生什么联系？\n解释：例子怎样体现跨国联系？\n回扣：它怎样支持我的看法？','约5分钟独立写，2分钟同伴分享，2分钟讲评。不因有连接词就判定内容合理。',S,42);
body('开放题 · 一种合理回应',L.tasks[4].answer,'旅游为示例，不是唯一答案。先让学生说，再展示参考。具体赛事、机构或数字须核实。',K,42);
body('课本词语 · 找出对应词语','1. 花费太多钱财，过分享受。\n\n2. 事物相互联系的中心环节。','回看第二段及第六段小标题。四项词语只做一次，可在网页统一完成。',K,44);
body('课本词语 · 找出对应词语','3. 用简单的笔墨描写事物的大致情况。\n\n4. 形容眼光远大。','回看第八段。辨清勾勒不是详细叙述，高瞻远瞩不是实际站得高。',K,44);
body('词语核对','1. 奢侈　　　　2. 枢纽\n\n3. 勾勒　　　　4. 高瞻远瞩\n\n把需要复习的词加入个人词语本。','“奢侈”在正文以“奢侈品”出现；“枢纽”在小标题。网页提供本课37词释义，但学生只收藏自己需要的词。',K,44);
body('回看主线，检查答案','古代：贸易带来货物流通与文化交流。\n\n今天：物流、文化与科技的联系。\n\n开放题：提出一个课外方面，用例子解释。','收束与订正。不要再布置重复的阅读题或一周小测。',K,42);
body('课后可以怎样回读？','完整漫画：连起来回顾课文\n\n学习记录：查看首次作答与订正\n\n个人词语本：释义、原句与闪卡','这是自选回读入口，不增加必交作业。教师资源包含教材与统计来源、旧版参考；网站与离线记录需分别备份。',S,42);
await fs.mkdir(root+'/build/ppt',{recursive:true});
if(!process.env.SKIP_RENDER)for(let i=0;i<pres.slides.items.length;i++){const blob=await pres.export({slide:pres.slides.items[i],format:'png',scale:1});await fs.writeFile(out+'/'+meta[i].image,new Uint8Array(await blob.arrayBuffer()));console.log('rendered',i+1)}
await fs.writeFile(out+'/slides/slides.json',JSON.stringify(meta,null,2));
const candidate=root+'/build/ppt/candidate.pptx';await(await PresentationFile.exportPptx(pres)).save(candidate);
execFileSync(process.env.CODEX_PRIMARY_RUNTIME_PYTHON,[root+'/build/dedupe_pptx.py',candidate]);
const base='/root/.codex/skills/builtins/presentations/container_tools';
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:out+'/downloads/singapore-world.pptx',pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:base+'/inspect_presentation_package_integrity.py',layoutValidatorPath:base+'/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--expected-slide-count',String(meta.length)],fontPolicy:{basis:'user_request',families:[K,S]},requiredNativeTableOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:root+'/build/ppt/validation.json'});console.log('FINAL',meta.length,result.finalSha256);
