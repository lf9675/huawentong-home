import {importDocuments,renderData,releasePages} from './documents.mjs';
import {cropTargets} from './refine.mjs';
import {renderReview} from './review.mjs';
const API='https://rodtizxezbtlhnuljzsc.supabase.co/functions/v1/hwt-essay-v2';
const $=id=>document.getElementById(id),show=(id,on=true)=>{$(id).hidden=!on;};
const state={code:'',account:null,photos:[],job:null,page:0,busy:false,retry:null,services:null};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function error(e){$('error').textContent=e?.message||String(e);show('error');}
async function api(action,data={}){
 let r;try{r=await fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,code:state.code,...data}),signal:AbortSignal.timeout(135000)});}catch{throw Error('服务连接中断或超时。已完成结果会保留，请重试。');}
 const d=await r.json().catch(()=>({error:'服务返回了异常响应，请稍后重试。'}));if(!r.ok||d.error)throw Error(d.error||'暂时无法完成请求。');return d;
}
async function health(){
 try{const r=await fetch(API,{signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error();const d=await r.json();
  state.services=d.services;providerNotice(d.providers);
  const missing=[!d.services.database&&'数据库',(!d.services.ocr||!d.services.grading)&&'Gemini'].filter(Boolean);
  $('service').textContent=missing.length?'图片和 PDF 可正常预览；'+missing.join('、')+'服务尚未开通，请联系老师。':'识别与批改均使用 Google Gemini · 已读取配置，实际调用将在提交后验证';$('service').classList.toggle('warn',missing.length>0);
 }catch{$('service').textContent='页面已打开，但批改服务暂时无法连接。请稍后刷新，或联系老师。';$('service').classList.add('warn');}
}
function providerNotice(providers){if(!providers)return;$('privacy').textContent=`开始识别后，页面图片会交由 ${providers.ocr||'待配置的识别服务'} 识别，核对后的文字会交由 ${providers.grading||'待配置的批改服务'} 批改。请遮住学生姓名和学校。原图、文字和批改将保存到受控记录，供本人和教师复核；不会公开展示。`;}
function account(info){state.services=info.services;providerNotice(info.providers);state.account=info;$('accountInfo').textContent=`${info.nickname} · ${info.exam} · 新作文余 ${info.newRemaining} 篇 / 总次数余 ${info.remaining} 次 · 有效至 ${info.expiry||'未设置'}`;show('account');show('loginPanel',false);
 const genres=info.exam==='HCL'?['记叙文','议论文','材料议论文','演讲词']:['记叙文','议论文'];$('genre').replaceChildren(...[...genres,'私人电邮','公务电邮','网上论坛'].map(g=>new Option(g,g)));
 $('recentList').replaceChildren();for(const row of info.recent||[]){if(row.status==='draft'&&new Date(row.expires_at)<new Date())continue;const b=document.createElement('button');b.className='quiet';b.textContent=`${row.created_at.slice(0,10)} · ${row.input.prompt?.slice(0,18)||'语言检查'} · ${row.status==='complete'?'查看':'继续'}`;b.onclick=()=>guard(()=>resume(row.id));$('recentList').append(b);}show('recent',$('recentList').childElementCount>0);show('setup');}
async function guard(fn){if(state.busy)return;state.busy=true;show('error',false);const buttons=[...document.querySelectorAll('button,input[type=file]')];const disabled=buttons.map(b=>b.disabled);buttons.forEach(b=>b.disabled=true);try{return await fn();}catch(e){error(e);}finally{state.busy=false;buttons.forEach((b,i)=>b.disabled=disabled[i]);$('ocrButton').disabled=!state.account||!state.photos.length||!state.services?.ocr||!state.services?.grading;$('gradeButton').disabled=!!state.job&&Array.from({length:state.job.input.pageCount},(_,i)=>state.job.result['ocr_'+i]).some(x=>!x);}}
function setProgress(text,n){show('progressPanel');$('progressText').textContent=text;$('progress').value=n;show('retry',false);}
async function run(fn){state.retry=fn;try{await fn();state.retry=null;show('retry',false);}catch(e){show('retry');throw e;}}
$('retry').onclick=()=>guard(()=>run(state.retry));
$('loginForm').onsubmit=e=>{e.preventDefault();guard(async()=>{state.code=$('code').value.trim().toUpperCase();const info=await api('login');$('code').value='';account(info);});};
$('logout').onclick=()=>{state.code='';state.photos=[];state.job=null;location.reload();};
function thumbs(){
 $('thumbs').replaceChildren();state.photos.forEach((p,i)=>{
  const div=document.createElement('div'),img=new Image(),label=document.createElement('p');img.src=p.data;img.alt=`第 ${i+1} 页预览`;label.textContent=`${i+1}. ${p.name}`;div.append(img,label);
  const button=(text,fn,disabled=false)=>{const b=document.createElement('button');b.className='quiet';b.textContent=text;b.disabled=disabled;b.onclick=()=>guard(fn);div.append(b);};
  button('转正 ↻',async()=>{p.rotation=(p.rotation+90)%360;await renderData(p);thumbs();});
  button('前移',()=>{[state.photos[i-1],state.photos[i]]=[p,state.photos[i-1]];thumbs();},i===0);
  button('后移',()=>{[state.photos[i+1],state.photos[i]]=[p,state.photos[i+1]];thumbs();},i===state.photos.length-1);
  button('删除',()=>{releasePages([p]);state.photos.splice(i,1);thumbs();});$('thumbs').append(div);
 });
 $('pageCount').textContent=state.photos.length?`已准备 ${state.photos.length} / 6 页 · 请核对方向与顺序`:'尚未选择文件';
 $('ocrButton').disabled=!state.account||!state.photos.length||!state.services?.ocr||!state.services?.grading;show('clearPhotos',state.photos.length>0);
}
$('photos').onchange=()=>guard(async()=>{
 const files=[...$('photos').files];if(!files.length)return;
 try{const loaded=await importDocuments(files,{existingCount:state.photos.length,onProgress:text=>{$('uploadStatus').textContent=text;}});state.photos.push(...loaded);thumbs();$('uploadStatus').textContent='页面已准备好。可以继续添加同一篇作文的图片或 PDF。';}
 catch(e){$('uploadStatus').textContent='本次选择未添加，已有页面保持不变。';throw e;}
 finally{$('photos').value='';}
});
$('clearPhotos').onclick=()=>guard(()=>{releasePages(state.photos);state.photos=[];thumbs();$('uploadStatus').textContent='已清空，可以重新选择文件。';});
async function ocrAll(){
 if(!state.account)throw Error('请先输入老师的访问码。');
 if(!state.services?.ocr||!state.services?.grading)throw Error('Gemini 服务尚未开通，请联系老师。');
 if(!state.job){state.job=await api('create',{id:crypto.randomUUID(),genre:$('genre').value,prompt:$('prompt').value,requirements:$('requirements').value,pageCount:state.photos.length});state.photoJobId=state.job.id;show('setup',false);sessionStorage.setItem('hwt-essay-job',state.job.id);}
 for(let i=0;i<state.job.input.pageCount;i++){
  if(!state.photos[i]&&!state.job.result['ocr_'+i])throw Error('缺少原照片，请取消本次后重新上传。');setProgress(`正在识别第 ${i+1} / ${state.job.input.pageCount} 页`,(i/state.job.input.pageCount)*100);
  if(!state.job.result['ocr_'+i])state.job=await api('ocr',{id:state.job.id,page:i,image:state.photos[i].data});
  if(!state.job.result['ocr_'+i].review_complete){setProgress(`对照原图复核涂改：第 ${i+1} 页`,(i/state.job.input.pageCount)*100);state.job=await api('ocr_review',{id:state.job.id,page:i});}
 }renderVerify();show('progressPanel',false);show('setup',false);
}
$('ocrButton').onclick=()=>guard(()=>run(ocrAll));
function renderVerify(){
 show('verify');$('editors').replaceChildren();
 for(let i=0;i<state.job.input.pageCount;i++){
  const row=document.createElement('section');row.className='verifyPage';const label=document.createElement('label');label.textContent=`第 ${i+1} 页`;
  const ocr=state.job.result['ocr_'+i],text=document.createElement('textarea');text.id='page-text-'+i;text.rows=14;text.value=state.job.result.pages?.[i]??ocr?.text??'';text.disabled=!!state.job.result.pages;label.append(text);
  if(ocr?.review_changed){const n=document.createElement('p');n.className='notice';n.textContent='两次识别结果有差异，请特别核对涂改、插入及模糊字；保留学生真正写错的字。';label.append(n);}
  if(ocr?.uncertainLines?.length){const notice=document.createElement('p');notice.className='small';notice.textContent=`Gemini 标记第 ${ocr.uncertainLines.join('、')} 行有不确定文字；□ 表示看不清的字，请对照原图核对。`;label.append(notice);}
  const p=state.photoJobId===state.job.id?state.photos[i]:null;
  if(p){const image=new Image();image.src=p.data;image.alt=`第 ${i+1} 页原图，供核对文字`;row.append(image);}const check=document.createElement('label');check.className='checkLine';check.innerHTML=`<input id="ack-${i}" type="checkbox">我已对照原图核对，保留学生原写法`;label.append(check);row.append(label);$('editors').append(row);
 }
}
$('cancel').onclick=()=>guard(async()=>{if(state.job)await api('cancel',{id:state.job.id});reset();});
function reset(){state.job=null;state.page=0;state.retry=null;sessionStorage.removeItem('hwt-essay-job');show('verify',false);show('result',false);show('progressPanel',false);show('setup');}
async function grading(){
 if(!state.job.result.pages){const pages=Array.from({length:state.job.input.pageCount},(_,i)=>$('page-text-'+i).value);if(!pages.every((_,i)=>$('ack-'+i)?.checked))throw Error('请逐页核对识别结果，并勾选确认。');state.job=await api('confirm',{id:state.job.id,pages,acknowledged:true});}
 show('verify',false);const count=state.job.result.chunkCount,total=count+state.job.input.pageCount+2;let done=0;
 for(let i=0;i<count;i++){setProgress(`逐句复核语言：第 ${i+1} / ${count} 段`,Math.round(done/total*100));if(!state.job.result['audit_'+i])state.job=await api('audit',{id:state.job.id,chunk:i});done++;}
 setProgress(state.job.input.mode==='grade'?'正在按题目和评分规则评阅全文……':'正在整理语言检查结果……',Math.round(done/total*100));if(!state.job.result.grade)state.job=await api('grade',{id:state.job.id});
 for(let i=0;i<state.job.input.pageCount;i++){setProgress(`回看原笔迹、定位红蓝批注：第 ${i+1} 页`,Math.round((count+1+i)/total*100));if(!state.job.result['visual_'+i])state.job=await api('visual',{id:state.job.id,page:i});if(!state.job.result['refine_'+i]){setProgress(`局部放大核对错字位置：第 ${i+1} 页`,Math.round((count+1+i)/total*100));const {targets}=await api('refine_targets',{id:state.job.id,page:i});const crops=await cropTargets(state.photos[i]?.data,targets);state.job=await api('refine',{id:state.job.id,page:i,crops});}}
 setProgress('正在保存批改与用量……',95);state.job=await api('finish',{id:state.job.id});renderResult();const info=await api('login');$('accountInfo').textContent=`${info.nickname} · ${info.exam} · 新作文余 ${info.newRemaining} 篇 / 总次数余 ${info.remaining} 次 · 有效至 ${info.expiry}`;
}
$('gradeButton').onclick=()=>guard(()=>run(grading));
async function resume(id){
 state.job=await api('get',{id});
 if(state.photoJobId!==id){const images=await api('images',{id});state.photos=images.urls.map(data=>data?{data}:null);state.photoJobId=id;}
 sessionStorage.setItem('hwt-essay-job',id);show('setup',false);show('recent',false);
 if(state.job.status==='complete')renderResult();
 else if(state.job.result.pages)await run(grading);
 else if(Array.from({length:state.job.input.pageCount},(_,i)=>state.job.result['ocr_'+i]).every(Boolean))await run(ocrAll);
 else {renderVerify();error(Error('部分页面尚未上传，请取消本次，再上传同一篇作文。'));$('gradeButton').disabled=true;}
}
function renderResult(){show('result');show('setup',false);show('verify',false);show('progressPanel',false);show('recent',false);renderReview($('result'),state.job,state.photoJobId===state.job.id?state.photos:[],{newEssay:()=>guard(async()=>{reset();releasePages(state.photos.filter(Boolean));state.photos=[];$('photos').value='';thumbs();account(await api('login'));})});$('result').scrollIntoView({behavior:'smooth'});}
thumbs();
health();

$('progressCancel').onclick=()=>guard(async()=>{if(state.job)await api('cancel',{id:state.job.id});reset();});

