const API='https://rodtizxezbtlhnuljzsc.supabase.co/functions/v1/hwt-essay';
const $=id=>document.getElementById(id),show=(id,on=true)=>{$(id).hidden=!on;};
const state={code:'',account:null,photos:[],job:null,page:0,busy:false,retry:null};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function error(e){$('error').textContent=e?.message||String(e);show('error');}
async function api(action,data={}){
 let r;try{r=await fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,code:state.code,...data}),signal:AbortSignal.timeout(135000)});}catch{throw Error('服务连接中断或超时。已完成结果会保留，请重试。');}
 const d=await r.json().catch(()=>({error:'服务返回了异常响应，请稍后重试。'}));if(!r.ok||d.error)throw Error(d.error||'暂时无法完成请求。');return d;
}
async function health(){
 try{const r=await fetch(API,{signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error();const d=await r.json();
  const missing=[!d.services.database&&'数据库',!d.services.ocr&&'照片识别',!d.services.grading&&'AI 批改'].filter(Boolean);
  $('service').textContent=missing.length?'页面已就绪；'+missing.join('、')+'服务尚未就绪，请老师检查配置。':'服务配置已读取 · 使用原访问码开始；识别与批改将在提交后验证';$('service').classList.toggle('warn',missing.length>0);
 }catch{$('service').textContent='页面已打开，但批改服务暂时无法连接。请稍后刷新，或联系老师。';$('service').classList.add('warn');}
}
function account(info){state.account=info;$('accountInfo').textContent=`${info.nickname} · ${info.exam} · 新作文余 ${info.newRemaining} 篇 / 总次数余 ${info.remaining} 次 · 有效至 ${info.expiry||'未设置'}`;show('account');show('loginPanel',false);
 const genres=info.exam==='HCL'?['记叙文','议论文','材料议论文','演讲词']:['记叙文','议论文'];$('genre').replaceChildren(...[...genres,'私人电邮','公务电邮','网上论坛'].map(g=>new Option(g,g)));
 $('recentList').replaceChildren();for(const row of info.recent||[]){if(row.status==='draft'&&new Date(row.expires_at)<new Date())continue;const b=document.createElement('button');b.className='quiet';b.textContent=`${row.created_at.slice(0,10)} · ${row.input.prompt?.slice(0,18)||'语言检查'} · ${row.status==='complete'?'查看':'继续'}`;b.onclick=()=>guard(()=>resume(row.id));$('recentList').append(b);}show('recent',$('recentList').childElementCount>0);show('setup');}
async function guard(fn){if(state.busy)return;state.busy=true;show('error',false);const buttons=[...document.querySelectorAll('button,input[type=file]')];const disabled=buttons.map(b=>b.disabled);buttons.forEach(b=>b.disabled=true);try{return await fn();}catch(e){error(e);}finally{state.busy=false;buttons.forEach((b,i)=>b.disabled=disabled[i]);$('ocrButton').disabled=!state.photos.length;if(state.job?.result.feedback){$('prev').disabled=state.page===0;$('next').disabled=state.page===state.job.input.pageCount-1;}$('gradeButton').disabled=!!state.job&&Array.from({length:state.job.input.pageCount},(_,i)=>state.job.result['ocr_'+i]).some(x=>!x);}}
function setProgress(text,n){show('progressPanel');$('progressText').textContent=text;$('progress').value=n;show('retry',false);}
async function run(fn){state.retry=fn;try{await fn();state.retry=null;show('retry',false);}catch(e){show('retry');throw e;}}
$('retry').onclick=()=>guard(()=>run(state.retry));
$('loginForm').onsubmit=e=>{e.preventDefault();guard(async()=>{state.code=$('code').value.trim().toUpperCase();const info=await api('login');$('code').value='';account(info);});};
$('logout').onclick=()=>{state.code='';state.photos=[];state.job=null;location.reload();};
async function photo(file){
 if(!/^image\/(jpeg|png|webp)$/.test(file.type)||file.size>25*1024*1024)throw Error('请选择小于 25 MB 的 JPG、PNG 或 WebP 图片。');
 const bitmap=await createImageBitmap(file,{imageOrientation:'from-image'});if(bitmap.width*bitmap.height>50000000){bitmap.close();throw Error('照片像素过大，请先缩小。');}
 const p={name:file.name,bitmap,rotation:0,data:''};await renderData(p);return p;
}
async function renderData(p){const swap=p.rotation%180!==0,scale=Math.min(1,2400/Math.max(p.bitmap.width,p.bitmap.height));const w=Math.round(p.bitmap.width*scale),h=Math.round(p.bitmap.height*scale),canvas=document.createElement('canvas');canvas.width=swap?h:w;canvas.height=swap?w:h;const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.translate(canvas.width/2,canvas.height/2);ctx.rotate(p.rotation*Math.PI/180);ctx.drawImage(p.bitmap,-w/2,-h/2,w,h);p.data=canvas.toDataURL('image/jpeg',.94);if(p.data.length>12500000)p.data=canvas.toDataURL('image/jpeg',.8);}
function thumbs(){$('thumbs').replaceChildren();state.photos.forEach((p,i)=>{const div=document.createElement('div'),img=new Image(),label=document.createElement('p'),rotate=document.createElement('button'),up=document.createElement('button');img.src=p.data;img.alt=`第 ${i+1} 页预览`;label.textContent=`${i+1}. ${p.name}`;rotate.className=up.className='quiet';rotate.textContent='转正 ↻';up.textContent='前移';up.disabled=i===0;rotate.onclick=()=>guard(async()=>{p.rotation=(p.rotation+90)%360;await renderData(p);thumbs();});up.onclick=()=>{[state.photos[i-1],state.photos[i]]=[p,state.photos[i-1]];thumbs();};div.append(img,label,rotate,up);$('thumbs').append(div);});$('ocrButton').disabled=!state.photos.length;}
$('photos').onchange=()=>guard(async()=>{const files=[...$('photos').files];if(!files.length||files.length>6)throw Error('每篇作文请选择 1 至 6 页。');const loaded=[];try{for(const f of files)loaded.push(await photo(f));}catch(e){loaded.forEach(p=>p.bitmap.close());throw e;}state.photos.forEach(p=>p.bitmap?.close());state.photos=loaded;thumbs();});
async function ocrAll(){
 if(!state.job){state.job=await api('create',{id:crypto.randomUUID(),genre:$('genre').value,prompt:$('prompt').value,requirements:$('requirements').value,pageCount:state.photos.length});state.photoJobId=state.job.id;show('setup',false);sessionStorage.setItem('hwt-essay-job',state.job.id);}
 for(let i=0;i<state.job.input.pageCount;i++){
  if(state.job.result['ocr_'+i])continue;if(!state.photos[i])throw Error('缺少原照片，请取消本次后重新上传。');setProgress(`正在识别第 ${i+1} / ${state.job.input.pageCount} 页`,(i/state.job.input.pageCount)*100);
  state.job=await api('ocr',{id:state.job.id,page:i,image:state.photos[i].data});
 }renderVerify();show('progressPanel',false);show('setup',false);
}
$('ocrButton').onclick=()=>guard(()=>run(ocrAll));
function renderVerify(){show('verify');$('editors').replaceChildren();for(let i=0;i<state.job.input.pageCount;i++){const label=document.createElement('label');label.textContent=`第 ${i+1} 页`;const text=document.createElement('textarea');text.id='page-text-'+i;text.rows=12;text.value=state.job.result.pages?.[i]??state.job.result['ocr_'+i]?.text??'';text.disabled=!!state.job.result.pages;label.append(text);$('editors').append(label);}}
$('cancel').onclick=()=>guard(async()=>{if(state.job)await api('cancel',{id:state.job.id});reset();});
function reset(){state.job=null;state.page=0;state.retry=null;sessionStorage.removeItem('hwt-essay-job');show('verify',false);show('result',false);show('progressPanel',false);show('setup');}
async function grading(){
 if(!state.job.result.pages){const pages=Array.from({length:state.job.input.pageCount},(_,i)=>$('page-text-'+i).value);state.job=await api('confirm',{id:state.job.id,pages});}
 show('verify',false);const count=state.job.result.chunkCount,total=count+2;let done=0;
 for(let i=0;i<count;i++){setProgress(`逐句复核语言：第 ${i+1} / ${count} 段`,Math.round(done/total*100));if(!state.job.result['audit_'+i])state.job=await api('audit',{id:state.job.id,chunk:i});done++;}
 setProgress(state.job.input.mode==='grade'?'正在按题目和评分规则评阅全文……':'正在整理语言检查结果……',Math.round(done/total*100));if(!state.job.result.grade)state.job=await api('grade',{id:state.job.id});
 setProgress('正在保存批改与用量……',95);state.job=await api('finish',{id:state.job.id});renderResult();const info=await api('login');$('accountInfo').textContent=`${info.nickname} · ${info.exam} · 新作文余 ${info.newRemaining} 篇 / 总次数余 ${info.remaining} 次 · 有效至 ${info.expiry}`;
}
$('gradeButton').onclick=()=>guard(()=>run(grading));
async function resume(id){state.job=await api('get',{id});sessionStorage.setItem('hwt-essay-job',id);show('setup',false);show('recent',false);if(state.job.status==='complete')renderResult();else if(state.job.result.pages)await run(grading);else{renderVerify();if(Array.from({length:state.job.input.pageCount},(_,i)=>state.job.result['ocr_'+i]).every(Boolean))return;show('verify');error(Error('部分页面尚未识别。重新打开页面后原图不可恢复，请取消本次，再上传同一篇作文。'));$('gradeButton').disabled=true;}}
function val(x){return typeof x==='string'?x:JSON.stringify(x??'',null,2);}
function renderResult(){show('result');show('setup',false);show('verify',false);show('progressPanel',false);show('recent',false);state.page=0;const f=state.job.result.feedback;$('resultStatus').textContent='语言复核已完成 · 已保存 · AI 建议仍需核对';$('score').replaceChildren();if(f.scores){$('score').textContent=`${f.scores.total} / ${f.scores.max} · ${f.grade_estimate}`;const detail=document.createElement('span');detail.textContent=`内容 ${f.scores.content} · 语文 ${f.scores.language}`;$('score').append(detail);}else $('score').textContent='本次只检查语言，未评分';$('comment').textContent=val(f.overall_suggestion||f.top_issue?.problem||f.overall_comment||f.overall_feedback||f.summary||'请结合原文逐条核对下面的修改建议。');$('issueCount').textContent=`(${f.annotations.length})`;
 $('issueList').replaceChildren();f.annotations.forEach((a,i)=>{const el=document.createElement('article');el.className='issue';el.id=a.id;const tag=document.createElement('span');tag.className='tag';tag.textContent=`${i+1} · ${a.uncertain?'需核对原字':a.category||'语言'} · ${a.location==='character'?'字级定位':a.location==='region'?'待核对区域':'待定位'}`;const button=document.createElement('button');const quote=document.createElement('span');quote.className='quote';quote.textContent=a.quote||'未提供原句';button.append(quote);button.onclick=()=>{document.querySelectorAll('.issue').forEach(x=>x.classList.remove('selected'));el.classList.add('selected');if(a.marks?.length)state.page=a.marks[0].page;renderPage(a.id);};const fix=document.createElement('p');fix.className='fix';fix.textContent='建议：'+(a.fix||'请教师确认');const why=document.createElement('p');why.textContent=val(a.why);el.append(tag,document.createElement('br'),button,fix,why);$('issueList').append(el);});if(!f.annotations.length)$('issueList').textContent='此次没有发现明确语言问题，不代表全文一定没有错误。';
 $('paragraphs').replaceChildren();(f.paragraph_feedback||[]).forEach((p,i)=>{const el=document.createElement('article');el.className='paragraph';const title=document.createElement('strong');title.textContent=`第 ${p.para_num||i+1} 段 · ${p.para_role||'段落反馈'}`;el.append(title);
 const line=(label,text)=>{if(!text)return;const node=document.createElement('p'),b=document.createElement('b');b.textContent=label+'：';node.append(b,document.createTextNode(val(text)));el.append(node);};
 line('原文',p.original_text);line('值得保留',p.highlights);line('为什么改、怎样改',p.why_and_how);
 for(const g of p.green_issues||[])line('表达建议',`${g.original||''} — ${g.issue_detail||''} ${g.suggestion||''}`);
 for(const x of p.structure_content_issues||[])line(x.aspect||'内容与结构',`${x.problem||''} ${x.suggestion||''} ${x.example?'例如：'+x.example:''}`);
 if(p.revised_top){const d=document.createElement('details'),summary=document.createElement('summary'),body=document.createElement('p');summary.textContent='查看修改示例';body.textContent=p.revised_top;d.append(summary,body);el.append(d);}
 $('paragraphs').append(el);});renderPage();$('result').scrollIntoView({behavior:'smooth'});
}
function renderPage(selected){const n=state.job.input.pageCount;$('pageLabel').textContent=`第 ${state.page+1} / ${n} 页`;$('prev').disabled=state.page===0;$('next').disabled=state.page===n-1;const p=state.photoJobId===state.job.id?state.photos[state.page]:null;$('photo').hidden=!p;$('photo').src=p?.data||'';$('photoNote').textContent=p?'黄色框表示 OCR 文字区域，不代表错误字的精确边界。':'历史记录保留文字与批改；原照片仅在上传时的页面中显示。';$('overlay').replaceChildren();if(!p)return;for(const a of state.job.result.feedback.annotations){if(selected&&selected!==a.id)continue;for(const mark of a.marks.filter(x=>x.page===state.page))for(const [x,y,w,h] of mark.rects){const r=document.createElementNS('http://www.w3.org/2000/svg','rect');for(const [k,v] of Object.entries({x,y,width:w,height:h,rx:.3}))r.setAttribute(k,String(v));if(mark.precision!=='character'||a.uncertain)r.classList.add('region');$('overlay').append(r);}}}
$('prev').onclick=()=>{state.page--;renderPage();};$('next').onclick=()=>{state.page++;renderPage();};
$('newEssay').onclick=()=>guard(async()=>{reset();state.photos.forEach(p=>p.bitmap?.close());state.photos=[];$('photos').value='';thumbs();account(await api('login'));});
$('export').onclick=()=>{const f=state.job.result.feedback,issues=f.annotations.map((a,i)=>`<li><strong>${i+1}. ${esc(a.quote)}</strong> → ${esc(a.fix)}<p>${esc(val(a.why))} (${a.uncertain?'待核对':a.location==='character'?'字级定位':a.location==='region'?'待核对区域':'待定位'})</p></li>`).join('');const photos=(state.photoJobId===state.job.id?state.photos:[]).map((p,i)=>{const marks=f.annotations.flatMap(a=>a.marks.filter(m=>m.page===i).flatMap(m=>m.rects.map(([x,y,w,h])=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="none" stroke="${m.precision==='character'&&!a.uncertain?'#c33':'#b80'}" stroke-width=".25"/>`))).join('');return `<h2>第 ${i+1} 页</h2><div style="position:relative;max-width:800px"><img alt="作文原图" style="width:100%;display:block" src="${p.data}"><svg style="position:absolute;inset:0;width:100%;height:100%" viewBox="0 0 100 100" preserveAspectRatio="none">${marks}</svg></div>`;}).join('');
 const html=`<!doctype html><html lang="zh"><meta charset="utf-8"><title>华文通作文批改报告</title><style>body{font:16px/1.8 system-ui;margin:40px;max-width:1000px}li{margin:20px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere}@media print{h2{break-before:page}}</style><h1>华文通作文批改报告</h1><p>AI 建议，待教师核对。黄色区域不是精确字框；无法定位的建议仍列在完整清单中。</p><p>${esc($('score').textContent)}</p><p>${esc($('comment').textContent)}</p>${photos}<h2>完整批注清单（${f.annotations.length} 条）</h2><ol>${issues}</ol><h2>段落反馈</h2>${$('paragraphs').innerHTML}</html>`;
 const url=URL.createObjectURL(new Blob([html],{type:'text/html;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='huawentong-essay-report.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);
};
health();

$('progressCancel').onclick=()=>guard(async()=>{if(state.job)await api('cancel',{id:state.job.id});reset();});
