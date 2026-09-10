import {SHEET_HEADERS,sheetRows,validSheetURL,sendSheet} from './management.ts';
// Custom teacher sessions and lesson-scoped submission tokens replace gateway JWT auth.
// Privileged database keys exist only in Supabase's server environment.
const enc = new TextEncoder();
const digest = async (s: string) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(s))), x => x.toString(16).padStart(2, '0')).join('');
const secret = () => crypto.randomUUID().replaceAll('-', '') + crypto.randomUUID().replaceAll('-', '');
const uuid = (v: unknown) => typeof v === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v);
const fail = (message: string, status = 400): never => { throw Object.assign(new Error(message), { status }); };
const clean = (v: unknown, max: number) => { if (typeof v !== 'string' || !v.trim() || v.length > max) fail('资料缺失或过长。'); return (v as string).trim(); };
const eq = (a: string, b: string) => { if (a.length !== b.length) return false; let n = 0; for (let i = 0; i < a.length; i++) n |= a.charCodeAt(i) ^ b.charCodeAt(i); return n === 0; };
const canonical = (v: any): string => JSON.stringify(v, (_key,value) => value && typeof value==='object' && !Array.isArray(value) ? Object.fromEntries(Object.keys(value).sort().filter(k=>value[k]!==undefined).map(k=>[k,value[k]])) : value);
async function db(path: string, method = 'GET', body?: unknown, extra: Record<string,string> = {}) {
 const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
 if (!key) fail('成绩服务尚未配置。', 503);
 const r = await fetch(Deno.env.get('SUPABASE_URL') + '/rest/v1/' + path, { method,
  headers: { apikey: key!, Authorization: 'Bearer ' + key, 'Content-Type': 'application/json', ...extra },
  ...(body === undefined ? {} : { body: JSON.stringify(body) }) });
 if (!r.ok) fail('成绩服务暂时不可用，请重试。', 503);
 const text = await r.text(); return text ? JSON.parse(text) : null;
}
async function rate(bucket: string, maximum: number, seconds = 900) {
 if (!await db('rpc/hwt_take_rate', 'POST', { bucket, maximum, seconds })) fail('请求较多，请稍后再试。', 429);
}
async function teacher(req: Request) {
 const token = req.headers.get('x-hwt-session') || '';
 if (!/^[0-9a-f]{64}$/.test(token)) fail('请重新用教师密码登录。', 401);
 const hash = await digest(token);
 const rows = await db('hwt_sessions?token_hash=eq.' + hash + '&expires_at=gt.' + encodeURIComponent(new Date().toISOString()) + '&select=token_hash');
 if (!rows.length) fail('教师登录已过期，请重新登录。', 401);
 return hash;
}
export function scoreRecords(bank: any, submitted: any) {
 if (!Array.isArray(submitted) || submitted.length !== bank.questions.length) fail('请完成全部题目后提交。');
 const seen = new Set();
 return bank.questions.map((q: any) => {
  const r = submitted.find((x: any) => x?.id === q.id);
  if (!r || seen.has(r.id)) fail('题号与学习单版本不符。'); seen.add(r.id);
  const base = { id: q.id, type: q.type, stage: q.stage, skill: q.skill, section: q.section, max: q.points };
  if (q.type === 'choice') {
   if (!Number.isInteger(r.chosenIndex) || r.chosenIndex < 0 || r.chosenIndex > 3) fail('选择题记录不完整。');
   return { ...base, chosenIndex: r.chosenIndex, correctIndex: q.answer, correct: r.chosenIndex === q.answer,
    score: r.chosenIndex === q.answer ? q.points : 0, misconception: q.misconceptions[r.chosenIndex], teacherScore: null };
  }
  if (!Number.isInteger(r.selfScore) || r.selfScore < 0 || r.selfScore > q.points) fail('自评分无效。');
  return { ...base, answer: clean(r.answer, 5000), selfScore: r.selfScore, teacherScore: null };
 });
}
async function allRows(path:string,maximum=10000){
 const rows=[];for(let offset=0;offset<maximum;offset+=500){const page=await db(path+'&limit=500&offset='+offset);rows.push(...page);if(page.length<500)return rows;}
 fail('记录超过读取上限，未生成不完整报告。',413);
}
async function readLesson(id:unknown){
 if(!uuid(id))fail('请选择学习单。');
 const lesson=(await db('hwt_lessons?id=eq.'+id+'&select=id,title,input,bank,created_at'))[0];if(!lesson)fail('学习单不存在。',404);return lesson;
}
async function readAttempts(id:string){
 const attempts=await allRows('hwt_attempts?lesson_id=eq.'+id+'&select=id,class_name,student_no,student_name,group_name,records,created_at&order=created_at.asc,id.asc');
 const reviews=await allRows('hwt_reviews?lesson_id=eq.'+id+'&select=attempt_id,question_id,score,feedback,revision,reviewed_at&order=attempt_id.asc,question_id.asc',30000);
 const index=new Map(reviews.map((r:any)=>[r.attempt_id+'\0'+r.question_id,r]));
 return attempts.map((a:any)=>({...a,records:a.records.map((r:any)=>{const v:any=index.get(a.id+'\0'+r.id);return r.type==='open'?{...r,teacherScore:v?.score??null,teacherFeedback:v?.feedback||'',reviewRevision:v?.revision||0,reviewedAt:v?.reviewed_at||null}:r;})}));
}
export async function handle(req: Request) {
 const headers = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'content-type,x-hwt-session',
  'Access-Control-Allow-Methods': 'POST,OPTIONS', 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' };
 if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers });
 try {
  if (req.method !== 'POST') fail('请使用POST。', 405);
  const raw = await req.text(); if (raw.length > 500000) fail('资料超过大小限制。', 413);
  let b: any; try { b = JSON.parse(raw); } catch { fail('资料格式不正确。'); }
  if (!b || typeof b.action !== 'string') fail('缺少操作。');
  let result: any;
  if (b.action === 'login') {
   await rate('teacher-login-global', 100);
   const ip = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
   await rate('teacher-login-' + await digest(ip), 15);
   const password = clean(b.password, 256);
   const settings = await db('hwt_settings?key=eq.teacher_password_sha256&select=value');
   if (!settings.length || !eq(await digest(password), settings[0].value)) fail('密码不正确。', 401);
   const token = secret(), expires = new Date(Date.now() + 8 * 3600000).toISOString();
   await db('hwt_sessions?expires_at=lt.' + encodeURIComponent(new Date().toISOString()), 'DELETE');
   await db('hwt_sessions', 'POST', { token_hash: await digest(token), expires_at: expires });
   result = { token, expires };
  } else if (b.action === 'submit') {
   if (!uuid(b.lessonId) || !uuid(b.attemptId)) fail('学习单标识无效。');
   const token = clean(b.token, 100);
   const lesson = (await db('hwt_lessons?id=eq.' + b.lessonId + '&select=bank,publish_token'))[0];
   if (!lesson || !eq(token, lesson.publish_token)) fail('学习单收集凭据无效，请联系教师。', 403);
   await rate('submit-' + b.lessonId, 1200, 3600);
   const row = { id: b.attemptId, lesson_id: b.lessonId, class_name: clean(b.className, 40),
    student_no: clean(b.studentNo, 30), student_name: clean(b.name, 80), group_name: typeof b.group === 'string' ? b.group.slice(0, 40) : '',
    records: scoreRecords(lesson.bank, b.records) };
   const existing = (await db('hwt_attempts?id=eq.' + b.attemptId + '&select=*'))[0];
   if (!existing) await db('hwt_attempts', 'POST', row, { Prefer: 'resolution=ignore-duplicates' });
   const stored = existing || (await db('hwt_attempts?id=eq.' + b.attemptId + '&select=*'))[0];
   if (!stored || stored.lesson_id !== row.lesson_id || stored.class_name !== row.class_name || stored.student_no !== row.student_no || stored.student_name !== row.student_name || canonical(stored.records) !== canonical(row.records)) fail('此提交已经保存，不能覆盖首次记录。', 409);
   result = { saved: true, attemptId: b.attemptId };
  } else {
   const sessionHash = await teacher(req);
   if (b.action === 'logout') { await db('hwt_sessions?token_hash=eq.' + sessionHash, 'DELETE'); result = { ok: true }; }
   else if (b.action === 'list') result = { lessons: await db('hwt_lessons?select=id,title,mode,created_at&order=created_at.desc&limit=200') };
   else if (b.action === 'publish') {
    const input = b.input, bank = b.bank;
    if (!input || !['writing','textbook','vocab'].includes(input.mode) || !bank || !Array.isArray(bank.questions) || bank.questions.length < 10 || bank.questions.length > 30 || new Set(bank.questions.map((q: any) => q?.id)).size !== bank.questions.length) fail('题稿不完整。');
    clean(input.title, 200);
    for (const q of bank.questions) {
     if (!q || !['choice','open'].includes(q.type) || !Number.isInteger(q.points) || q.points < 1 || q.points > 5) fail('题目分值或题型无效。');
     if (q.type === 'choice' && (!Array.isArray(q.options) || q.options.length !== 4 || !Number.isInteger(q.answer) || q.answer < 0 || q.answer > 3 || q.misconceptions?.length !== 4)) fail('题目答案不完整。');
     if (q.type === 'open' && q.rubric?.length !== q.points) fail('评分量表不完整。');
    }
    // Explicit input allow-list: no teacher API key, session or unrelated form fields.
    const safe: any = {};
    for (const k of ['mode','grade','unit','minutes','questionCount','support','title','passage','terms','known','reference','writing','writingPrompt','genre','writingFocus']) if (input[k] !== undefined) safe[k] = input[k];
    const hash = await digest(canonical({ input: safe, bank }));
    await db('hwt_lessons?on_conflict=content_hash', 'POST', { content_hash: hash, title: safe.title, mode: safe.mode, input: safe, bank, publish_token: secret() }, { Prefer: 'resolution=ignore-duplicates' });
    const saved = (await db('hwt_lessons?content_hash=eq.' + hash + '&select=id,publish_token'))[0];
    result = { lessonId: saved.id, token: saved.publish_token };
   } else if (b.action === 'review') {
    if(!uuid(b.attemptId)||!Number.isInteger(b.score)||b.score<0||!Number.isInteger(b.revision)||b.revision<0)fail('覆核资料无效。');
    const questionId=clean(b.questionId,100),feedback=typeof b.feedback==='string'?b.feedback.trim():'';
    if(feedback.length>2000)fail('评语最多2000字。');
    const attempt=(await db('hwt_attempts?id=eq.'+b.attemptId+'&select=lesson_id,records'))[0];if(!attempt)fail('提交不存在。',404);
    const lesson=await readLesson(attempt.lesson_id),q=lesson.bank.questions.find((q:any)=>q.id===questionId);
    if(!q||q.type!=='open'||b.score>q.points||!attempt.records.some((r:any)=>r.id===questionId))fail('只能覆核本次作答的开放题，分数不能超过题目满分。');
    const saved=await db('rpc/hwt_save_review','POST',{p_attempt:b.attemptId,p_question:questionId,p_score:b.score,p_feedback:feedback,p_revision:b.revision});
    if(saved?.conflict)fail('此题已有新的覆核，请刷新记录后再修改。',409);
    if(!saved||saved.attempt_id!==b.attemptId||saved.score!==b.score)fail('没有收到覆核保存确认。',503);
    result={saved:true,review:saved};
   } else if(b.action==='roster_save'){
    const lesson=await readLesson(b.lessonId),className=clean(b.className,40);
    if(!Array.isArray(b.students)||!b.students.length||b.students.length>300)fail('名册须有1至300名学生。');
    const students=b.students.map((x:any)=>({studentNo:clean(x.studentNo,30),name:clean(x.name,80)}));
    if(new Set(students.map((x:any)=>x.studentNo)).size!==students.length)fail('名册有重复学号，请先修正。');
    await db('hwt_rosters?on_conflict=lesson_id,class_name','POST',{lesson_id:lesson.id,class_name:className,students,updated_at:new Date().toISOString()},{Prefer:'resolution=merge-duplicates'});
    const saved=(await db('hwt_rosters?lesson_id=eq.'+lesson.id+'&class_name=eq.'+encodeURIComponent(className)+'&select=students'))[0];
    if(canonical(saved?.students)!==canonical(students))fail('没有收到名册保存确认。',503);
    result={saved:true,count:students.length};
   } else if(b.action==='sheets_status'){
    const value=(await db('hwt_settings?key=eq.google_sheets_sink&select=value'))[0]?.value;
    result={configured:!!value};
   } else if(b.action==='sheets_configure'){
    if(!validSheetURL(b.url)||typeof b.secret!=='string'||!/^[A-Za-z0-9_-]{32,200}$/.test(b.secret))fail('请填写Google Apps Script的/exec网址和同步码。');
    const config={url:b.url,secret:b.secret};let ping;
    try{ping=await sendSheet(config,{action:'ping'});}catch{fail('Google连接验证失败；请检查部署访问设置及同步码。原设置保留。',502);}
    if(ping.kind!=='hwt-grades-v1')fail('Google返回的不是华文通成绩接收服务。');
    await db('hwt_settings?on_conflict=key','POST',{key:'google_sheets_sink',value:JSON.stringify(config)},{Prefer:'resolution=merge-duplicates'});
    result={configured:true};
   } else if(b.action==='sheets_sync'){
    const lesson=await readLesson(b.lessonId),attempts=await readAttempts(lesson.id);
    const rows=sheetRows(lesson,attempts);if(!rows.length)fail('尚无学生提交，不能同步空成绩。');if(rows.length>2000)fail('记录超过单次同步上限，请先导出成绩表。');
    const value=(await db('hwt_settings?key=eq.google_sheets_sink&select=value'))[0]?.value;if(!value)fail('请先连接Google成绩表。');
    const requestId=crypto.randomUUID();let saved;
    try{saved=await sendSheet(JSON.parse(value),{action:'sync',requestId,headers:SHEET_HEADERS,rows});}catch{fail('未收到Google保存确认，请重试；同一提交不会重复新增。',502);}
    if(saved.requestId!==requestId||saved.saved!==rows.length)fail('Google保存结果不完整，请重试。',502);
    result={saved:true,count:saved.saved};
   } else if (b.action === 'load' || b.action === 'records') {
    const lesson=await readLesson(b.lessonId);
    if(b.action==='load')result={lesson};
    else result={lesson,attempts:await readAttempts(lesson.id),rosters:await allRows('hwt_rosters?lesson_id=eq.'+lesson.id+'&select=class_name,students,updated_at&order=class_name.asc'),truncated:false};
   } else fail('未知操作。');
  }
  return new Response(JSON.stringify(result), { headers });
 } catch (e: any) {
  return new Response(JSON.stringify({ error: e.status ? e.message : '成绩服务暂时无法完成请求，请重试。' }), { status: e.status || 500, headers });
 }
}
Deno.serve(handle);

