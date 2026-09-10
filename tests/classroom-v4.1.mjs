import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const hash=s=>createHash('sha256').update(s).digest('hex');
const tables={hwt_settings:[{key:'teacher_password_sha256',value:hash('fixture-only-password')}],hwt_sessions:[],hwt_lessons:[],hwt_attempts:[]};
globalThis.Deno={env:{get:k=>({SUPABASE_SERVICE_ROLE_KEY:'fixture-server-key',SUPABASE_URL:'https://fixture.invalid'})[k]},serve(){}};
globalThis.fetch=async(url,opts={})=>{
 const u=new URL(url),table=u.pathname.split('/').pop(),body=opts.body?JSON.parse(opts.body):null;
 if(table==='hwt_take_rate')return Response.json(true);
 assert.ok(opts.headers.Authorization.includes('fixture-server-key'));
 let rows=tables[table];assert.ok(rows,table);
 const matches=x=>[...u.searchParams].every(([k,v])=>!v.startsWith('eq.')&&!v.startsWith('gt.')&&!v.startsWith('lt.')||v.startsWith('eq.')?(!v.startsWith('eq.')||String(x[k])===v.slice(3)):v.startsWith('gt.')?x[k]>v.slice(3):x[k]<v.slice(3));
 if(opts.method==='DELETE'){tables[table]=rows.filter(x=>!matches(x));return new Response(null,{status:204});}
 if(opts.method==='POST'){
  const key=u.searchParams.get('on_conflict')||(table==='hwt_sessions'?'token_hash':'id');
  if(table==='hwt_lessons'&&rows.some(x=>x.content_hash===body.content_hash)&&key!=='content_hash')return new Response(null,{status:409});
  if(!rows.some(x=>x[key]===body[key]))rows.push({created_at:new Date().toISOString(),id:crypto.randomUUID(),...body});
  return new Response(null,{status:201});
 }
 return Response.json(rows.filter(matches));
};
const {handle,scoreRecords}=await import('../supabase/functions/hwt-classroom/index.ts');
const Cloud=(await import('../bei/shared/classroom.js')).default;
let passed=0;const test=async(name,fn)=>{await fn();passed++;console.log('PASS '+name);};
const call=async(b,token='')=>{const r=await handle(new Request('https://fixture.invalid',{method:'POST',headers:{'x-hwt-session':token},body:JSON.stringify(b)}));return {status:r.status,body:await r.json()};};
let session,lesson;
await test('anonymous teacher data access rejected',async()=>assert.equal((await call({action:'list'})).status,401));
await test('public legacy browser flag is not authentication',async()=>assert.equal((await call({action:'list'},'1')).status,401));
await test('wrong password rejected',async()=>assert.equal((await call({action:'login',password:'wrong'})).status,401));
await test('server validates password and returns expiring opaque session',async()=>{const r=await call({action:'login',password:'fixture-only-password'});assert.equal(r.status,200);session=r.body.token;assert.match(session,/^[a-f0-9]{64}$/);assert.equal(tables.hwt_sessions[0].token_hash,hash(session));assert.notEqual(tables.hwt_sessions[0].token_hash,session);});
const q={id:'L1',type:'choice',stage:'你做',skill:'fixture',section:'fixture',points:1,answer:2,options:['A','B','C','D'],misconceptions:['a','b','正确','d']};
const bank={questions:Array.from({length:10},(_,i)=>({...q,id:'L'+(i+1)}))};
await test('publish requires auth and strips unrecognized input secrets',async()=>{assert.equal((await call({action:'publish',bank,input:{}})).status,401);const r=await call({action:'publish',bank,input:{title:'fixture',mode:'textbook',key:'DO-NOT-SAVE'}},session);assert.equal(r.status,200);lesson=r.body;assert.equal(tables.hwt_lessons.length,1);assert.equal(tables.hwt_lessons[0].input.key,undefined);});
await test('same content reuses immutable version',async()=>{const r=await call({action:'publish',bank,input:{title:'fixture',mode:'textbook'}},session);assert.equal(r.body.lessonId,lesson.lessonId);assert.equal(tables.hwt_lessons.length,1);});
const payload={action:'submit',lessonId:lesson.lessonId,token:lesson.token,attemptId:crypto.randomUUID(),className:'TEST',studentNo:'01',name:'Fixture',group:'',records:bank.questions.map(q=>({id:q.id,chosenIndex:0,score:999,teacherScore:5}))};
await test('invalid student token rejected',async()=>assert.equal((await call({...payload,token:'bad'})).status,403));
await test('server recomputes objective scores and discards invented teacher scores',async()=>{const r=await call(payload);assert.equal(r.status,200);assert.equal(tables.hwt_attempts[0].records[0].score,0);assert.equal(tables.hwt_attempts[0].records[0].teacherScore,null);});
await test('retry is idempotent even when JSONB key order changes',async()=>{tables.hwt_attempts[0].records=tables.hwt_attempts[0].records.map(r=>Object.fromEntries(Object.entries(r).reverse()));assert.equal((await call(payload)).status,200);assert.equal(tables.hwt_attempts.length,1);});
await test('first answers cannot be overwritten',async()=>{const r=await call({...payload,records:payload.records.map(x=>({...x,chosenIndex:2}))});assert.equal(r.status,409);assert.equal(tables.hwt_attempts[0].records[0].chosenIndex,0);});
await test('student submission token cannot read class records',async()=>assert.equal((await call({action:'records',lessonId:lesson.lessonId},lesson.token)).status,401));
await test('authenticated teacher can read records',async()=>{const r=await call({action:'records',lessonId:lesson.lessonId},session);assert.equal(r.status,200);assert.equal(r.body.attempts.length,1);});
await test('open answers remain self-assessment pending teacher review',()=>{const r=scoreRecords({questions:[{...q,type:'open',rubric:['evidence']}]},[{id:'L1',answer:'fixture',selfScore:1,teacherScore:1}]);assert.equal(r[0].teacherScore,null);assert.equal(r[0].selfScore,1);assert.equal(r[0].score,undefined);});
await test('missing or duplicate submitted questions rejected',()=>{assert.throws(()=>scoreRecords(bank,payload.records.slice(1)));assert.throws(()=>scoreRecords(bank,payload.records.map(()=>payload.records[0])));});
await test('analysis separates classes and excludes repeat attempts',()=>{const a=tables.hwt_attempts[0];const s=Cloud.summary({bank},[a,{...a,id:crypto.randomUUID()},{...a,class_name:'OTHER'}]);assert.equal(s.students,2);assert.equal(s.repeatsExcluded,1);assert.equal(s.items[0].submitted,2);});
await test('logout invalidates the server session',async()=>{assert.equal((await call({action:'logout'},session)).status,200);assert.equal((await call({action:'list'},session)).status,401);});
console.log(JSON.stringify({passed,backend:'mock HTTP and database; no real credentials or student writes'}));
