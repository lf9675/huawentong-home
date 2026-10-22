import lesson from './lesson.json' with {type:'json'};
import {fail,text,normalize,summarize} from './core.mjs';
const digest=async(s:string)=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s))),x=>x.toString(16).padStart(2,'0')).join('');
const token=()=>Array.from(crypto.getRandomValues(new Uint8Array(32)),x=>x.toString(16).padStart(2,'0')).join('');
const id=(v:any)=>{if(typeof v!=='string'||!/^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(v))fail('任务标识无效。');return v};
const origins=new Set(['https://huawentong-home.lyqlym2015.workers.dev','http://localhost:4173','http://127.0.0.1:4173']);
async function db(path:string,method='GET',body?:any,extra={}){
 const key=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');if(!key)fail('收件服务尚未配置。',503);
 const r=await fetch(Deno.env.get('SUPABASE_URL')+'/rest/v1/'+path,{method,headers:{apikey:key,Authorization:'Bearer '+key,'Content-Type':'application/json',...extra},...(body===undefined?{}:{body:JSON.stringify(body)})});
 if(!r.ok)fail('收件服务暂时无法完成请求。',503);const raw=await r.text();return raw?JSON.parse(raw):null;
}
async function rate(bucket:string,max:number,seconds=60){if(!await db('rpc/hwt_take_rate','POST',{bucket,maximum:max,seconds}))fail('操作较多，请稍后再试。',429)}
async function teacher(req:Request){const t=req.headers.get('x-hwt-session')||'';if(!/^[0-9a-f]{64}$/.test(t))fail('请先登录教师工作台。',401);const h=await digest(t);const rows=await db('hwt_sessions?token_hash=eq.'+h+'&expires_at=gt.'+encodeURIComponent(new Date().toISOString())+'&select=token_hash');if(!rows.length)fail('教师登录已过期，请重新登录。',401);await rate('tb-teacher-'+h,150);}
async function assignment(v:any){const a=(await db('hwt_tb_assignments?id=eq.'+id(v)+'&select=*'))[0];if(!a)fail('找不到这项课堂任务。',404);return a}
async function student(req:Request,b:any){const t=req.headers.get('x-hwt-student')||'';if(!/^[0-9a-f]{64}$/.test(t))fail('请使用教师发给你的专属学习链接。',401);const h=await digest(t);const s=(await db('hwt_tb_students?id=eq.'+id(b.studentId)+'&assignment_id=eq.'+id(b.assignmentId)+'&token_hash=eq.'+h+'&select=id,assignment_id,student_no,revision,last_seen_at,submitted_at,read_paragraphs'))[0];if(!s)fail('学习链接已失效，请联系教师。',403);await rate('tb-student-'+s.id,90);return {s,h};}
async function readRows(path:string){const all=[];for(let offset=0;offset<10000;offset+=500){const r=await db(path+'&limit=500&offset='+offset);all.push(...r);if(r.length<500)return all;}fail('记录超出读取上限，请联系管理员。',413)}
export async function handle(req:Request){
 const origin=req.headers.get('origin')||'';const headers:any={'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Vary':'Origin','Access-Control-Allow-Headers':'content-type,x-hwt-session,x-hwt-student','Access-Control-Allow-Methods':'POST,OPTIONS'};
 if(origins.has(origin))headers['Access-Control-Allow-Origin']=origin;
 try{
 if(origin&&!origins.has(origin))fail('此来源不允许访问收件服务。',403);
 if(req.method==='OPTIONS')return new Response(null,{status:204,headers});
 if(req.method!=='POST')fail('请使用POST。',405);
 if(Number(req.headers.get('content-length'))>250000)fail('提交内容过大。',413);
 const raw=await req.text();if(raw.length>250000)fail('提交内容过大。',413);let b:any;try{b=JSON.parse(raw)}catch{fail('资料格式无效。')}
 if(!b||typeof b.action!=='string')fail('缺少操作。');
 let result:any;
 if(b.action==='health')return Response.json({ok:true,service:'hwt-textbook-v1',lessonId:lesson.id,version:lesson.version},{headers});
 if(['connect','submit'].includes(b.action)){
 await rate('tb-entry-'+await digest(req.headers.get('x-forwarded-for')?.split(',')[0]||'unknown'),600);
 const {s,h}=await student(req,b),a=await assignment(s.assignment_id);
 if(b.action==='connect'){
 if(!a.is_open||Date.parse(a.expires_at)<Date.now())fail('本次课堂已停止收件，本机记录仍保留。',410);
 const responses=await db('hwt_tb_responses?student_id=eq.'+s.id+'&select=*&order=task_id');
 result={assignment:{id:a.id,className:a.class_name,title:a.lesson.title,lessonId:a.lesson_id,contentVersion:a.content_version,expiresAt:a.expires_at},student:s,responses};
 }else{
 if(!Number.isInteger(b.baseRevision)||b.baseRevision<0)fail('同步版本无效。');
 const p=normalize(a.lesson,b);result=await db('rpc/hwt_tb_submit','POST',{p_student:s.id,p_token_hash:h,p_request:id(b.requestId),p_hash:await digest(JSON.stringify(p)),p_base:b.baseRevision,p_payload:p});
 if(result.error==='revision_conflict')fail('另一台设备有更新。请先恢复云端记录，再继续；本机备份保留。',409);
 if(result.error==='closed')fail('本次课堂已停止收件，本机记录仍保留。',410);
 if(result.error)fail('未能确认保存，请重新连接后再试。',409);
 }
 }else{
 await teacher(req);
 if(b.action==='catalog')result={lesson:{id:lesson.id,title:lesson.title,version:lesson.version,tasks:lesson.tasks.map(t=>({id:t.id,title:t.title,mode:t.mode,role:t.role}))}};
 else if(b.action==='list')result={assignments:await readRows('hwt_tb_assignments?select=id,class_name,lesson_id,content_version,is_open,expires_at,created_at&order=created_at.desc')};
 else if(b.action==='create'){
 const requestId=id(b.assignmentId);const existing=(await db('hwt_tb_assignments?id=eq.'+requestId+'&select=id'))[0];if(existing)return Response.json({saved:true,assignmentId:requestId,links:[]},{headers});
 const className=text(b.className,60,true);if(!Array.isArray(b.numbers)||!b.numbers.length||b.numbers.length>80)fail('每次请登记1至80个学号。');const numbers=b.numbers.map((n:any)=>text(n,30,true));if(new Set(numbers).size!==numbers.length)fail('学号不能重复。');
 const days=Number(b.days??30);if(!Number.isInteger(days)||days<1||days>90)fail('收件期限为1至90天。');
 const assignmentId=requestId,students=await Promise.all(numbers.map(async(n:string)=>{const t=token();return {id:crypto.randomUUID(),student_no:n,token_hash:await digest(t),token:t}}));
 const a={id:assignmentId,class_name:className,lesson_id:lesson.id,content_version:lesson.version,lesson,expires_at:new Date(Date.now()+days*86400000).toISOString()};
 await db('rpc/hwt_tb_create','POST',{p_assignment:a,p_students:students.map(({token,...s})=>s)});
 result={saved:true,assignmentId,links:students.map(s=>({studentId:s.id,number:s.student_no,token:s.token}))};
 }else if(b.action==='dashboard'){
 const a=await assignment(b.assignmentId),students=await db('hwt_tb_students?assignment_id=eq.'+a.id+'&select=id,student_no,revision,last_seen_at,submitted_at,read_paragraphs&order=student_no');
 const ids=students.map((s:any)=>s.id).join(',');const [responses,reviews]=await Promise.all([readRows('hwt_tb_responses?student_id=in.('+ids+')&select=*&order=student_id,task_id'),readRows('hwt_tb_reviews?student_id=in.('+ids+')&select=*&order=student_id,task_id')]);
 result={assignment:a,summary:summarize(a,students,responses,reviews),responses,reviews,serverTime:new Date().toISOString()};
 }else if(b.action==='review'){
 if(!['达到','部分达到','需帮助'].includes(b.verdict)||!Number.isInteger(b.baseRevision)||b.baseRevision<0)fail('覆核资料无效。');
 result=await db('rpc/hwt_tb_review','POST',{p_student:id(b.studentId),p_task:text(b.taskId,80,true),p_verdict:b.verdict,p_note:text(b.note??'',2000),p_base:b.baseRevision});
 if(result.error)fail('此题已有新的覆核，请刷新后再修改。',409);
 }else if(b.action==='close'){
 const a=await assignment(b.assignmentId);if(typeof b.open!=='boolean')fail('收件状态无效。');
 await db('hwt_tb_assignments?id=eq.'+a.id,'PATCH',{is_open:b.open,closed_at:b.open?null:new Date().toISOString()});result={saved:true,open:b.open};
 }else if(b.action==='rotate'){
 const a=await assignment(b.assignmentId),s=(await db('hwt_tb_students?id=eq.'+id(b.studentId)+'&assignment_id=eq.'+a.id+'&select=id,student_no'))[0];if(!s)fail('学生不在这个任务中。');const t=token();await db('hwt_tb_students?id=eq.'+s.id,'PATCH',{token_hash:await digest(t)});result={saved:true,studentId:s.id,number:s.student_no,token:t};
 }else fail('不支持此操作。');
 }
 return Response.json(result,{headers});
 }catch(e:any){return Response.json({error:e.status?e.message:'收件服务暂时无法完成请求，请稍后重试。'},{status:e.status||500,headers});}
}
Deno.serve(handle);
