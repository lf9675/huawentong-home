import {emphasisParts,problemPhrases,evidenceRows,focusFlow,exampleParts,verdictLabel} from './presentation.mjs';
// Entire report, rendered locally in bounded A4 canvases. No DOM screenshots or external fonts.
const W=595.28,H=841.89,M=42,SCALE=2.5;
const RED='#b52c36',BLUE='#185e9a',INK='#243744';
const excluded=a=>['ocr_error','deleted_text','not_error','teacher_rejected'].includes(a.review_state);
const checked=a=>['visual_checked','teacher_confirmed'].includes(a.review_state);
const clean=s=>String(s??'').replace(/\r/g,'');
const labels={adequate:'充分',missing:'缺少',weak:'尚未充分展开',off_topic:'感悟偏离重点',not_applicable:'本体裁不适用',aligned:'重点与详写匹配',underdeveloped:'重点正确但未展开',off_focus:'详写偏向另一重点'};
export function reportBlocks(job){
 const f=job.result.feedback||{},r=f.overall_review||{},out=[];
 const add=(text,kind='text',color=INK,phrases=[])=>{if(clean(text).trim())out.push({text:clean(text),kind,color,phrases});};
 const section=t=>add(t,'section');
 const card=(title,x,action=true)=>{if(!x)return;add(title,'reviewHeading',RED);add(x.judgement,'text',INK,problemPhrases(x));if(action)add(x.suggestion);};
 const compare=kind=>{const steps=focusFlow(f,kind),rows=evidenceRows(f,kind);if(steps.length)out.push({kind:'flow',steps});if(rows.length)out.push({kind:'table',rows});};
 const example=(text,notes)=>{const parts=exampleParts(text,notes),runs=parts.flatMap(x=>x.note?[{text:x.text,color:RED,bold:true},{text:'〔扣“'+x.note.keyword+'”：'+x.note.why+'〕',color:RED,bold:true}]:[{text:x.text}]);out.push({kind:'text',text:runs.map(x=>x.text).join(''),runs});};
 add('华文通 · 完整作文批改报告','title');
 add(job.input.genre||'作文','small');add('题目：'+(job.input.prompt||'未提供题目，本次只检查语言。'));
 add(job.input.requirements&&'特别要求：'+job.input.requirements);
 add('AI 初评；待核对项目不作为确定的学生错误。红圈标错字，红波浪线标病句，蓝波浪线标好句。悬停内容已展开为文字订正。','small');
 card('选材与扣题',r.materials||{judgement:f.material_review||f.overall_comment});
 card('详略安排',r.detail_balance);
 card('紧扣关键词详写',r.keyword_detail,false);compare('keyword');
 if(!r.keyword_detail&&job.input.mode!=='language')add('此旧记录尚未提供关键词专项点评。','small');
 if(r.ending_reflection&&r.ending_reflection.status!=='not_applicable'){card('结尾抒情议论',r.ending_reflection,false);compare('ending');}
 if(r.ending_reflection?.example){add('结尾修改示范','heading',RED);example(r.ending_reflection.example,r.ending_reflection.example_notes);}
 for(const text of f.strengths||[])add('值得保留：'+text,'text',BLUE);
 for(const [i,text] of (r.priorities||[]).entries())add('先改 '+(i+1)+'：'+text,'text',RED);
 add(f.overall_suggestion);add(f.encouragement);
 section('二、评分与依据');
 if(f.scores)add(`总分 ${f.scores.total} / ${f.scores.max}；内容 ${f.scores.content}；语文 ${f.scores.language}；参考等级 ${f.grade_estimate||'待定'}`);
 else add('本次没有评分。');add(f.score_note);add(f.grade_distance);
 for(const value of Object.values(f.grading_rationale||f.scoring_basis||{}))add(typeof value==='string'?value:JSON.stringify(value));
 for(const text of f.auto_caps||[])add(text,'small');
 for(let page=0;page<(job.input.pageCount||job.result.pages?.length||0);page++)out.push({kind:'photo',page});
 section('四、完整原文、逐段旁批与修改示范');
 const paragraphs=f.paragraph_feedback?.length?f.paragraph_feedback:(job.result.pages||[]).map((text,i)=>({original_text:text,para_num:i+1,status:'keep'}));
 for(const [i,p] of paragraphs.entries()){
  add(`第 ${p.para_num||i+1} 段${p.para_role?' · '+p.para_role:''}`,'heading');add('原文：'+p.original_text);
  if(p.highlights)add('写得好：'+p.highlights,'text',BLUE);
  if(p.status==='keep')add('本段内容保留；语言订正见批注清单。','small');
  const revise=p.status==='needs_revision';
  add(p.why_and_how&&(revise?'主要问题与改法：':'本段点评：')+p.why_and_how,'text',revise?RED:p.status==='good'?BLUE:INK);
  for(const x of p.structure_content_issues||[])add([x.problem,x.suggestion].filter(Boolean).join('；'),'text',revise?RED:INK);
  const en=p.explanation_en||(p.structure_content_issues||[]).map(x=>x.voice_en).filter(Boolean).join(' ');add(en&&'English explanation: '+en,'small');
  if(revise&&p.revised_top){add('修改示范','heading',RED);example(p.revised_top,p.revision_notes);}
 }
 section('五、全部字词、句子批注与核对记录');
 if(!f.annotations?.length)add('暂无批注记录。');
 for(const [i,a] of (f.annotations||[]).entries()){
  const state=excluded(a)?'已排除，不算学生错误':a.review_state==='teacher_confirmed'?'教师已确认':checked(a)?'已回看原笔迹，位置需核对':'待核对，不作为确定错误';
  const pages=[...new Set((a.marks||[]).map(m=>m.page+1))];
  add(`${i+1}. ${a.category||'语言'}${pages.length?' · 第 '+pages.join('、')+' 页':''} · ${state}`,'heading',excluded(a)?INK:a.kind==='praise'?BLUE:RED);
  add('原文：'+a.quote);add((a.kind==='praise'?'好在哪里：':'建议：')+(a.kind==='praise'?a.why:a.fix));
  if(a.kind!=='praise')add(a.why);add(a.visual_note&&'原图核对：'+a.visual_note,'small');
 }
 section('六、整篇修改示范（未改段落保留原文）');
 add('以下是内容修改示范；字词订正及待核对项目请同时参照批注清单。','small');
 for(const p of paragraphs){if(p.status==='needs_revision'&&p.revised_top)example(p.revised_top,p.revision_notes);else add(p.original_text);}
 section('七、学习建议与讲解');
 for(const t of f.coaching_advice||[])add(t);
 if(f.top_issue){add(f.top_issue.problem,'heading',RED);add(f.top_issue.evidence_quote);add(f.top_issue.why);add(f.top_issue.fix);}
 for(const t of f.top_issues||[])add([t.problem,t.impact,t.suggestion].filter(Boolean).join('；'));
 add(f.audio_script&&'中文讲解文字稿：'+f.audio_script);return out;
}
export function wrapText(ctx,text,maxWidth){
 const lines=[];for(const paragraph of clean(text).split('\n')){let line='';for(const c of paragraph){if(line&&ctx.measureText(line+c).width>maxWidth){const chars=Array.from(line);if(/[，。！？；：、）】》”’]/.test(c)&&chars.length>1){const last=chars.pop();lines.push(chars.join(''));line=last+c;}else{lines.push(line);line=c;}}else line+=c;}lines.push(line);}return lines;
}
function drawMarks(ctx,annotations,index,box){
 const {x,y,w,h}=box;ctx.save();ctx.lineWidth=1.25;
 for(const a of annotations||[]){if(excluded(a)||!checked(a))continue;ctx.strokeStyle=a.kind==='praise'?BLUE:RED;
  for(const mark of a.marks||[]){if(mark.page!==index||!['visual_estimate','character','teacher'].includes(mark.precision))continue;
   for(const r of mark.rects||[]){if(!Array.isArray(r)||r.length!==4||!r.every(Number.isFinite)||r[2]<=0||r[3]<=0)continue;
    const [rx,ry,rw,rh]=[x+r[0]/100*w,y+r[1]/100*h,r[2]/100*w,r[3]/100*h];ctx.beginPath();
    if(a.kind!=='praise'&&/错别字|错字/.test(a.category))ctx.ellipse(rx+rw/2,ry+rh/2,rw/2+1,rh/2+1,0,0,Math.PI*2);
    else {ctx.moveTo(rx,ry+rh);for(let d=0;d<rw;d+=3){const step=Math.min(3,rw-d);ctx.quadraticCurveTo(rx+d+step/2,ry+rh+(Math.floor(d/3)%2?1.5:-1.5),rx+d+step,ry+rh);}}
    ctx.stroke();
   }
  }
 }ctx.restore();
}
async function browserImage(source){
 const r=await fetch(source,{signal:AbortSignal.timeout(30000)});if(!r.ok)throw Error('原图读取失败，请重新打开这份批改后再下载。');
 const url=URL.createObjectURL(await r.blob());try{return await new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error('原图无法解码，请重新打开这份批改。'));i.src=url;});}finally{URL.revokeObjectURL(url);}
}
export async function createReportPdf(job,photos=[],options={}){
 const {PDFDocument}=await import('./vendor/pdf-lib/pdf-lib.min.mjs');
 const pdf=await PDFDocument.create();pdf.setTitle('华文通完整作文批改报告');pdf.setProducer('华文通');
 const makeCanvas=options.createCanvas||((w,h)=>Object.assign(document.createElement('canvas'),{width:w,height:h}));
 const canvas=makeCanvas(Math.ceil(W*SCALE),Math.ceil(H*SCALE)),ctx=canvas.getContext('2d');
 if(!ctx)throw Error('此浏览器无法生成 PDF，请使用下方打印功能。');
 let y=M,page=0,hasContent=false;const layout=[];
 const font=(size,bold=false)=>{ctx.font=`${bold?'bold ':''}${size}px ${options.fontFamily||'"PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif'}`;};
 const reset=()=>{ctx.setTransform(SCALE,0,0,SCALE,0,0);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);ctx.textBaseline='top';y=M;hasContent=false;};
 reset();
 const flush=async()=>{if(!hasContent)return;ctx.fillStyle='#6b747a';font(9);ctx.fillText('华文通 · 作文批改',M,H-26);ctx.fillText(String(++page),W-M-20,H-26);const img=await pdf.embedJpg(canvas.toDataURL('image/jpeg',.94));pdf.addPage([W,H]).drawImage(img,{x:0,y:0,width:W,height:H});options.onProgress?.('正在生成 PDF：已完成 '+page+' 页');await new Promise(resolve=>setTimeout(resolve,0));reset();};
 // Measure bold and normal runs separately, preserving every character across page breaks.
 const richLines=(runs,maxWidth,size)=>{const lines=[];let current=[],width=0;const push=()=>{lines.push(current);current=[];width=0;};for(const run of runs){for(const ch of clean(run.text)){if(ch==='\n'){push();continue;}font(size,!!run.bold);const w=ctx.measureText(ch).width;if(current.length&&width+w>maxWidth)push();const last=current.at(-1);if(last&&last.bold===!!run.bold&&last.color===(run.color||INK))last.text+=ch;else current.push({text:ch,bold:!!run.bold,color:run.color||INK});width+=w;}}if(current.length)push();return lines;};
 const drawLine=(runs,x,top,size)=>{const start=x;for(const run of runs){font(size,run.bold);ctx.fillStyle=run.color;ctx.fillText(run.text,x,top);x+=ctx.measureText(run.text).width;}layout.push({kind:'line',text:runs.map(x=>x.text).join(''),pdfPage:page+1,y:top,size,x:start,width:x-start,runs});};
 try{
  for(const block of reportBlocks(job)){
   if(block.kind==='photo'){
    await flush();font(16,true);ctx.fillStyle=INK;ctx.fillText((block.page===0?'三、全部原稿图片与圈注 · ':'')+'第 '+(block.page+1)+' 页',M,M);hasContent=true;
    const source=photos[block.page]?.data||photos[block.page];
    if(!source){font(12);ctx.fillText('此旧记录未保存这一页原图，完整文字仍列在后文。',M,M+40);layout.push({kind:'missing_photo',page:block.page});}
    else {let img;try{img=await (options.loadImage||browserImage)(source);}catch{throw Error('第 '+(block.page+1)+' 页原图读取失败；未生成不完整 PDF，请重新打开批改后重试。');}
     const width=img.naturalWidth||img.width,height=img.naturalHeight||img.height,scale=Math.min((W-2*M)/width,(H-2*M-58)/height);
     const box={x:(W-width*scale)/2,y:M+36,w:width*scale,h:height*scale};ctx.drawImage(img,box.x,box.y,box.w,box.h);drawMarks(ctx,job.result.feedback?.annotations,block.page,box);img.close?.();layout.push({kind:'photo',sourcePage:block.page,pdfPage:page+1,box});
    }await flush();continue;
   }
   if(block.kind==='table'){
    const col=(W-2*M)/2,pad=12,lh=20,size=11.5;
    const header=async()=>{if(y+70>H-M)await flush();ctx.fillStyle='#eef0e9';ctx.fillRect(M,y,W-2*M,32);font(12,true);ctx.fillStyle=INK;ctx.fillText('你的原句',M+pad,y+7);ctx.fillText('对照题目，怎样改',M+col+pad,y+7);y+=32;hasContent=true;};
    await header();
    for(const row of block.rows){
     const left=[{text:(row.paragraph?'第 '+row.paragraph+' 段':'原文')+'\n',color:'#68746c'},{text:row.quote||'原文尚未写出这一点。',bold:true}];
     const right=[{text:row.keyword+' · '+verdictLabel(row.status)+'\n',bold:true},{text:row.problem+'\n',bold:true,color:row.status==='met'?BLUE:RED},{text:row.action===row.problem?'':row.action}];
     const cells=[left,right].map(runs=>richLines(runs,col-2*pad,size)),pos=[0,0];
     const total=Math.max(...cells.map(x=>x.length))*lh+2*pad;
     if(y+total>H-M&&total<H-2*M-32){await flush();await header();}
     while(pos.some((p,i)=>p<cells[i].length)){
      let limit=Math.floor((H-M-y-2*pad)/lh);if(limit<1){await flush();await header();limit=Math.floor((H-M-y-2*pad)/lh);}
      const slices=cells.map((lines,i)=>lines.slice(pos[i],pos[i]+limit)),height=Math.max(...slices.map(a=>a.length))*lh+2*pad;
      ctx.strokeStyle='#dce1da';ctx.lineWidth=.7;ctx.strokeRect(M,y,col,height);ctx.strokeRect(M+col,y,col,height);
      slices.forEach((lines,i)=>{lines.forEach((runs,n)=>drawLine(runs,M+i*col+pad,y+pad+n*lh,size));pos[i]+=lines.length;});
      layout.push({kind:'tableRow',paragraph:row.paragraph,pdfPage:page+1,y,height});y+=height;hasContent=true;
      if(pos.some((p,i)=>p<cells[i].length)){await flush();await header();}
     }
    }y+=18;continue;
   }
   if(block.kind==='flow'){
    const gap=14,col=(W-2*M-gap*(block.steps.length-1))/block.steps.length,size=10.5,lh=18;
    const lines=block.steps.map(x=>richLines([{text:x.label+'\n',bold:true},{text:x.status==='guide'?'':verdictLabel(x.status)}],col-14,size));
    const height=Math.max(...lines.map(x=>x.length))*lh+18;if(y+height+12>H-M)await flush();
    block.steps.forEach((x,i)=>{const left=M+i*(col+gap);ctx.fillStyle=x.status==='met'?'#edf5fb':'#fff3ec';ctx.fillRect(left,y,col,height);ctx.strokeStyle='#d8cbc6';ctx.strokeRect(left,y,col,height);lines[i].forEach((runs,n)=>drawLine(runs,left+7,y+9+n*lh,size));if(i){font(12);ctx.fillStyle='#68746c';ctx.fillText('→',left-gap,y+height/2-7);}});
    layout.push({kind:'flow',pdfPage:page+1,y,height});y+=height+18;hasContent=true;continue;
   }
   const size=block.kind==='title'?23:block.kind==='reviewHeading'?19:block.kind==='section'?17:block.kind==='heading'?14:block.kind==='small'?10:12;
   const lineHeight=size*1.75,bold=['title','section','heading','reviewHeading'].includes(block.kind);
   if((block.kind==='section'||block.kind==='reviewHeading')&&hasContent){if(y>H-M-140)await flush();else y+=14;}
   const runs=block.runs||emphasisParts(block.text,block.phrases).map(x=>({...x,bold:bold||x.bold,color:block.color}));
   const lines=richLines(runs,W-2*M,size);
   if(bold&&y+Math.min(lines.length,2)*lineHeight+25>H-M)await flush();
   for(const runs of lines){if(y+lineHeight>H-M)await flush();drawLine(runs,M,y,size);hasContent=true;y+=lineHeight;}y+=bold?9:6;
  }await flush();return {bytes:await pdf.save(),pageCount:page,layout};
 }finally{canvas.width=1;canvas.height=1;}
}
export async function downloadReportPdf(job,photos,options={}){
 const {bytes,pageCount}=await createReportPdf(job,photos,options),blob=new Blob([bytes],{type:'application/pdf'}),url=URL.createObjectURL(blob);
 const link=document.createElement('a');link.href=url;link.download='作文完整批改-'+(job.id?.slice(0,8)||'报告')+'.pdf';link.textContent='PDF 已生成，点此下载／打开（'+pageCount+' 页）';link.className='buttonLink';link.target='_blank';link.rel='noopener';
 // Retain a user-tappable link: Safari may require another gesture after asynchronous generation.
 if(options.target){options.target.replaceChildren(link);options.target.hidden=false;}else document.body.append(link);
 link.click();setTimeout(()=>{URL.revokeObjectURL(url);link.remove();},30*60*1000);return pageCount;
}
