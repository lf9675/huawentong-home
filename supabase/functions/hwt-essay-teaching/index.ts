import {geminiRequest,geminiResult} from '../hwt-essay/google.mjs';
import {pageUrls} from '../hwt-essay/storage.mjs';
import {validRect,norm,span} from '../hwt-essay/core.mjs';
import {candidates,LESSON_RULES,LESSON_REVIEW_RULES,validateLesson} from './core.mjs';
const secret=(s:string)=>Deno.env.get(s)?.trim();
const fail=(message:string,status=400):never=>{throw Object.assign(Error(message),{status});};
const hash=async(s:string)=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))].map(x=>x.toString(16).padStart(2,'0')).join('');
const uuid=(s:any)=>typeof s==='string'&&/^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(s);
async function db(path:string,body?:unknown,method?:string){
 const key=secret('SUPABASE_SERVICE_ROLE_KEY');const r=await fetch(secret('SUPABASE_URL')+'/rest/v1/'+path,{method:method||(body===undefined?'GET':'POST'),headers:{apikey:key!,Authorization:'Bearer '+key,'Content-Type':'application/json',Prefer:'return=representation'},...(body===undefined?{}:{body:JSON.stringify(body)}),signal:AbortSignal.timeout(15000)});
 if(!r.ok)fail('教师资料暂时无法保存或读取，请重试。',503);return r.json();
}
async function getJob(id:string){
 if(!uuid(id))fail('作文编号不正确。');const j=(await db('hwt_essay_jobs?id=eq.'+id+'&status=eq.complete&select=id,input,result,created_at,submission_id'))[0];
 if(!j?.result?.feedback)fail('作文记录不存在或尚未完成。',404);return j;
}
async function review(id:string){return (await db('hwt_essay_reviews?job_id=eq.'+id+'&select=annotations,revision'))[0]||{annotations:{},revision:0};}
export async function handle(req:Request){
 const origin=req.headers.get('origin')||'',allowed=!origin||['https://huawentong-home.lyqlym2015.workers.dev','https://huawentong-home.pages.dev','http://localhost:4173','http://127.0.0.1:4173'].includes(origin);
 const headers:any={'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Vary':'Origin','Access-Control-Allow-Headers':'content-type,x-hwt-session','Access-Control-Allow-Methods':'POST,OPTIONS'};if(origin&&allowed)headers['Access-Control-Allow-Origin']=origin;
 try{
  if(!allowed)fail('此来源无权访问。',403);if(req.method==='OPTIONS')return new Response(null,{status:204,headers});if(req.method!=='POST')fail('请使用POST。',405);
  const token=req.headers.get('x-hwt-session')||'';if(!/^[0-9a-f]{64}$/.test(token))fail('请先登录教师页面。',401);
  const session=await hash(token);if(!(await db('hwt_sessions?token_hash=eq.'+session+'&expires_at=gt.'+encodeURIComponent(new Date().toISOString())+'&select=expires_at')).length)fail('教师登录已过期。',401);
  if(!await db('rpc/hwt_take_rate',{bucket:'essay-teaching-'+session,maximum:240,seconds:900}))fail('操作较多，请稍后重试。',429);
  const raw=await req.text();if(raw.length>80000)fail('资料过长。',413);let b:any;try{b=JSON.parse(raw);}catch{fail('请求格式错误。');}let result;
  if(b.action==='statistics'){result=await db('rpc/hwt_essay_error_counts',{});
  }else if(b.action==='list'){
   const page=Number.isInteger(b.page)&&b.page>0?Math.min(b.page,10000):1;
   result={jobs:await db(`hwt_essay_jobs?status=eq.complete&select=id,code_id,input,created_at,submission_id&order=created_at.desc&limit=30&offset=${(page-1)*30}`),lessons:await db('hwt_essay_lessons?status=eq.complete&select=id,created_at,input&order=created_at.desc&limit=20')};
  }else if(b.action==='detail'){
   const j=await getJob(b.id),r=await review(j.id);result={job:j,review:r,candidates:candidates(j,r.annotations),urls:await pageUrls(j)};
  }else if(b.action==='review'){
   const j=await getJob(b.id),r=await review(j.id),all=candidates(j,r.annotations);let original=all.find(x=>x.id===b.key)||j.result.feedback.annotations?.find((x:any)=>x.id===b.key)||r.annotations[b.key];
   if(!original&&typeof b.key==='string'&&b.key.startsWith('teacher-')&&uuid(b.key.slice(8))){const quote=b.edit?.quote,full=j.result.pages.map(norm).join('');if(typeof quote!=='string'||!norm(quote)||!full.includes(norm(quote)))fail('补充批注的原文必须确实出现在作文中。');original={kind:b.edit.kind==='praise'?'praise':'error',category:b.edit.kind==='praise'?'好词好句':b.edit.category||'错别字',quote,fix:'',why:'',span:span(full,quote),marks:[]};}
   if(!original)fail('批注不存在。');if(!Number.isInteger(b.revision))fail('缺少记录版本。');
   const e=b.edit;if(!e||!['teacher_confirmed','teacher_rejected','pending'].includes(e.review_state))fail('审核状态不正确。');
   const edit:any={kind:original.kind||'error',category:original.category,quote:original.quote,fix:original.fix,why:original.why,paragraph:original.paragraph,marks:original.marks||[],...(original.span?{span:original.span}:{}),review_state:e.review_state,teacher_reviewed:e.review_state!=='pending',uncertain:e.review_state==='pending',updated_at:new Date().toISOString()};
   for(const key of ['quote','fix','why','category'])if(e[key]!==undefined){if(typeof e[key]!=='string'||e[key].length>6000)fail('评语过长。');edit[key]=e[key];}
   if(e.marks!==undefined){if(!Array.isArray(e.marks)||e.marks.length>12||e.marks.some((m:any)=>!Number.isInteger(m.page)||m.page<0||m.page>=j.input.pageCount||!Array.isArray(m.rects)||m.rects.length>30||!m.rects.every(validRect)))fail('圈注范围不正确。');edit.marks=e.marks.map((m:any)=>({page:m.page,rects:m.rects,precision:'teacher'}));edit.location=edit.marks.some((m:any)=>m.rects.length)?'teacher':'pending';}
   result=await db('rpc/hwt_essay_review_save',{p_session:session,p_job:j.id,p_revision:b.revision,p_key:b.key,p_edit:{...(r.annotations[b.key]||{}),...edit}});
   if(result.error)fail(result.error,result.status||400);
  }else if(b.action==='lesson'){
   if(!uuid(b.id))fail('讲评编号错误。');const row=(await db('hwt_essay_lessons?id=eq.'+b.id+'&select=id,status,result,input'))[0];if(!row)fail('讲评材料不存在。',404);result=row;
  }else if(b.action==='generate'){
   if(!uuid(b.id)||!Array.isArray(b.job_ids)||b.job_ids.length<1||b.job_ids.length>10||b.job_ids.some((id:any)=>!uuid(id)))fail('请选择1至10篇作文。');
   const ids=[...new Set(b.job_ids)].sort(),sources:any[]=[],jobs=[];
   for(const id of ids){const j=await getJob(id as string),r=await review(j.id);jobs.push(j);for(const c of candidates(j,r.annotations).filter(x=>x.review_state==='teacher_confirmed'))sources.push({id:j.id+':'+c.id,category:c.category,kind:c.kind,quote:c.quote,why:c.why,fix:c.fix});}
   if(!sources.length)fail('请先确认至少一个真实问题，再生成讲评材料。');
   if(jobs.some(j=>j.input.prompt!==jobs[0].input.prompt||j.input.genre!==jobs[0].input.genre))fail('请选择相同题目、相同文体的作文。');
   if(sources.length>80)fail('确认的问题较多，请分批选择作文生成讲评。');
   const input={job_ids:ids,prompt:jobs[0].input.prompt,genre:jobs[0].input.genre,source_count:sources.length},sourceHash=await hash(JSON.stringify({input,sources})),lease=crypto.randomUUID();
   const claimed=await db('rpc/hwt_essay_lesson_claim',{p_session:session,p_id:b.id,p_hash:sourceHash,p_input:input,p_lease:lease});if(claimed.error)fail(claimed.error,claimed.status||400);
   if(claimed.status==='complete')result=claimed;else{
    try{
     if(!await db('rpc/hwt_take_rate',{bucket:'essay-lesson-generate-'+session,maximum:12,seconds:3600}))fail('本小时生成次数较多，请稍后重试。',429);
     const key=secret('GEMINI_API_KEY'),model=secret('GEMINI_MODEL')||'gemini-3.8-flash';if(!key||!/^gemini-[a-zA-Z0-9.-]+$/.test(model))fail('Gemini配置暂时不可用。',503);
     let draft=claimed.result?.draft;
     if(!draft){const body=geminiRequest(LESSON_RULES,{prompt:input.prompt,genre:input.genre,essay_count:jobs.length,confirmed_errors:sources},24000);body.generationConfig.thinkingConfig={thinkingLevel:'LOW'};
     const response=await fetch('https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',{method:'POST',headers:{'x-goog-api-key':key,'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(60000)});
     if(!response.ok)fail('Gemini暂未完成讲评生成，请稍后重试。',502);
     draft=geminiResult(await response.json());await db('hwt_essay_lessons?id=eq.'+b.id+'&lease=eq.'+lease,{result:{draft}},'PATCH');}
     const reviewBody=geminiRequest(LESSON_REVIEW_RULES,{prompt:input.prompt,genre:input.genre,essay_count:jobs.length,confirmed_errors:sources,draft},24000);reviewBody.generationConfig.thinkingConfig={thinkingLevel:'LOW'};
     const checked=await fetch('https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',{method:'POST',headers:{'x-goog-api-key':key,'Content-Type':'application/json'},body:JSON.stringify(reviewBody),signal:AbortSignal.timeout(60000)});if(!checked.ok)fail('讲评材料复核暂未完成，请稍后重试。',502);
     const reviewed=geminiResult(await checked.json());await db('hwt_essay_lessons?id=eq.'+b.id+'&lease=eq.'+lease,{result:{draft:reviewed}},'PATCH');const pack=validateLesson(reviewed,sources);pack.quality_reviewed=true;pack.source_count=sources.length;pack.essay_count=jobs.length;
     const rows=await db('hwt_essay_lessons?id=eq.'+b.id+'&lease=eq.'+lease,{status:'complete',result:pack,lease:null,lease_until:null,updated_at:new Date().toISOString()},'PATCH');if(!rows.length)fail('保存结果冲突，请重新打开材料。',409);result=rows[0];
    }catch(e:any){await db('hwt_essay_lessons?id=eq.'+b.id+'&lease=eq.'+lease,{status:'draft',lease:null,lease_until:null},'PATCH');if(!e.status&&/^(讲评材料|讲评重点|错误范文|课件内容|Gemini 输出|Gemini 返回)/.test(e.message||''))fail(e.message,502);throw e;}
   }
  }else fail('未知操作。');
  return Response.json(result,{headers});
 }catch(e:any){return Response.json({error:e.status?e.message:e.name==='TimeoutError'?'生成超时，已确认问题保留，可以重试。':'暂时无法完成，请重试。'},{status:e.status||503,headers});}
}
Deno.serve(handle);
