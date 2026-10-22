import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation} from '/root/.codex/skills/builtins/presentations/container_tools/artifact_tool_utils.mjs';
const root=process.cwd(),out=root+'/site/du/textbook/1hcl/unit2/xinnian-fengsu';
const L=JSON.parse(await fs.readFile(out+'/lesson.json','utf8'));
const P=Presentation.create({slideSize:{width:1280,height:720}}),M=[];
const K='Huawentong WenKai',S='Noto Serif CJK SC',blue='#185E94',ink='#1B354F',red='#B21F32';
const sheets=await Promise.all([1,2,3].map(n=>fs.readFile(out+'/assets/comic'+n+'.png')));
function txt(s,t,x,y,w,h,z=42,font=K,color=ink,bold=false){const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0,style:'solid'}});q.text=t;q.text.style={fontSize:z,typeface:font,color,bold,wrap:true,autoFit:'none',lineSpacing:1.2,verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};return q}
function sl(title,notes=''){const s=P.slides.add();s.background.fill='#F7FBFE';txt(s,title,58,32,1160,112,48,K,blue,true);txt(s,String(M.length+1),1155,657,65,48,38,S,blue);s.speakerNotes.text=notes+'\n来源：教师提供的课文《世界各地的新年风俗》、阅读放大镜、教参和原漫画。';M.push({title,notes,lesson:1,image:'slides/slide-'+String(M.length+1).padStart(2,'0')+'.png'});return s}
function body(title,text,notes='',z=44,font=K){const s=sl(title,notes);txt(s,text,65,168,1145,465,z,font);return s}
function panel(s,n,x,y,w){const[a,b,c,d]=L.panelRects[n-1];s.images.add({blob:sheets[L.panelSheets[n-1]-1],contentType:'image/png',alt:'原有漫画第'+n+'格',fit:'cover',position:{left:x,top:y,width:w,height:w*d/c},crop:{left:a/1024,top:b/1536,right:(1024-a-c)/1024,bottom:(1536-b-d)/1536}})}
function wrapText(t,n=24){let out=[];while(t.length>n){let k=n;if(/[，。；：！？]/.test(t[k]))k++;out.push(t.slice(0,k));t=t.slice(k)}out.push(t);return out.join('\n')}
function q(id,sub=''){const t=L.tasks.find(t=>t.id===id);const s=body(t.title,t.questions.join('\n\n')+(sub?'\n\n'+sub:''),t.role+'\n'+t.source+'\n'+t.hints.join('\n'),42);for(const shape of s.shapes.items)for(const w of t.keywords)try{shape.text.get(w).color=red}catch{}return s}
let s=sl('中一高级华文 · 单元二','生活空间，一课时50分钟。先图文自读，再完成原题。问题与讲解分页。');txt(s,'世界各地的\n新年风俗',60,198,760,220,70,K,blue,true);txt(s,'生活空间 · 一课时',65,500,700,68,40,S);panel(s,1,835,200,370);
body('迎新年的方式','你熟悉哪一种迎新方式？\n\n什么时候做？\n\n人们希望新的一年怎样？','3分钟口头导入，不要求另写一题。不要把“刚刚过完新年”当作实际课堂日期。',46);
body('读懂一种风俗','什么时候？\n\n做什么？\n\n这个做法表达什么愿望？','自主图文阅读7分钟，按第1—5段顺序。允许查词与回看漫画；不设阅读解锁。',48,S);
body('象征意义','“象征”是借事物或动作表达意义。\n\n例如：握手，可以表示友好。\n\n读课文时，留意“象征、以示、表示、\n预示、希望”后面的内容。','短概念示范，不用未教概念直接测试。握手例子为解释词义，不新增测验。',42,S);
for(const [i,r] of L.rows.entries()){
 const t=L.tasks[i],p=i+1;
 body('第'+p+'段 · '+L.paragraphLabels[i],wrapText(L.paragraphs[i],i===4?26:24),r.role+'。本页完整原文，先读，暂不揭示下一页整理答案。',i===4?40:44);
 body('整理信息 · '+L.paragraphLabels[i],'根据课文内容，填写下面的表格。\n\n迎接新年的方式：____________\n\n本段的具体寓意：____________',t.role+'\n课本第二题按地区拆步。先口头说时间，再在网页点选。\n'+t.hints.join('\n'),43);
 const ans=['时间：'+r.time,'方式：'+r.action,'寓意：'+r.meaning].join('\n\n');
 body('核对 · '+L.paragraphLabels[i],ans,t.explain+'\n'+t.reject+'\n'+t.scoreGuide,p===5?40:42);
}
body('元旦与春节','元旦：阳历1月1日\n\n春节：农历正月初一\n\n农历新年也叫“春节”。','对应课本小知识和原漫画第17—18格。只核对日期名称，不增加阴阳历知识测验。',48);
q('common');
body('共同点 · 答题方法','共同愿望\n\n两个地区的具体例子\n\n例子怎样表达这个愿望','独立短答6分钟。回看不同段落，支持连续加入两句原文。不是只列举两个动作。',48,S);
body('共同点 · 合理示范','这些风俗寄托了对新年的美好期盼。\n\n西班牙：吃12颗葡萄，祝愿各月如意。\n华人：向亲友拜年，祝愿健康、吉利。\n\n做法不同，都希望新一年生活美好。',L.tasks[5].scoreGuide+'\n接受古巴、意大利、丹麦的准确例子。只说“都很有趣”或“都在午夜”不能概括全文。',42);
body('词语搭配 · 课本第一题','工作　　　厄运\n路途　　　烟火\n按照　　　遥远\n去除　　　忙碌\n燃放　　　风俗','根据课文内容，把可以搭配的词语连起来。保留课本左右两栏的初始次序，网页选项随机打乱。5分钟内完成与订正。',50);
body('词语搭配 · 核对','工作忙碌　　路途遥远\n\n按照风俗　　去除厄运\n\n燃放烟火','五组各1点；解释搭配要放回语境。网页统计为整组首次全对率，不能当逐空得分。',48);
q('share');
body('分享 · 说清为什么','看法：哪一种风俗有趣？\n\n理由：为什么？\n\n例子：什么时候，做什么？\n\n回扣：它怎样表达新年愿望？','查资料与同桌分享9分钟。记录网站名称与网址。可用已核对的日本国家旅游局链接，也可自找可靠来源。',42,S);
body('分享 · 一种合理示范','我觉得新年前夜吃荞麦面很有趣，\n因为面条的形状也能表达祝福。\n\n细长的面条让人联想到长寿，\n人们借此祝愿长寿，表达美好期盼。','资料：日本国家旅游局（JNTO），New Year food traditions，2018-12-21。https://www.japan.travel/en/sg/story/new-year-food-traditions/ ，2026-10-22核对。学生先作答才揭示。此示范不是唯一答案。',43);
body('当堂检查','方式与寓意，有没有分清？\n\n共同点，有没有两个例子支持？\n\n分享时，有没有说清为什么？\n\n订正并导出自己的学习记录。','3分钟收束。首次答案保留，订正另存。开放题由教师覆核，不以字数或关键词自动评分。',43,S);
await fs.mkdir(root+'/build/ppt',{recursive:true});
for(let i=0;i<P.slides.items.length;i++){const b=await P.export({slide:P.slides.items[i],format:'png',scale:1});await fs.writeFile(out+'/'+M[i].image,new Uint8Array(await b.arrayBuffer()));if(i%10===0)console.log('rendered',i+1)}
await fs.writeFile(out+'/slides/slides.json',JSON.stringify(M,null,2));
const candidate=root+'/build/ppt/candidate.pptx';await(await PresentationFile.exportPptx(P)).save(candidate);
execFileSync(process.env.CODEX_PRIMARY_RUNTIME_PYTHON,[root+'/build/dedupe_pptx.py',candidate]);
const base='/root/.codex/skills/builtins/presentations/container_tools';
const stamp=Date.now();const finalFile=out+'/downloads/xinnian-fengsu-'+stamp+'.pptx';
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:finalFile,pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:base+'/inspect_presentation_package_integrity.py',layoutValidatorPath:base+'/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--expected-slide-count',String(M.length),'--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:[K,S]},requiredNativeTableOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:root+'/build/ppt/validation-'+stamp+'.json'});console.log('FINAL',M.length,result.finalSha256);

await fs.copyFile(finalFile,out+'/downloads/xinnian-fengsu.pptx');await fs.unlink(finalFile);
