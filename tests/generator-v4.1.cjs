// Engineering fixtures only: these are not teaching questions or live student records.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const path=require('node:path'),root=path.join(__dirname,'..');
const HWT=require(path.join(root,'bei/shared/prep-v3.js'));
const source=fs.readFileSync(path.join(root,'bei/shared/prep-v3.js'),'utf8');
let count=0;async function test(name,fn){await fn();count++;console.log('PASS '+name);}
const items=Array.from({length:4},(_,i)=>({id:'L'+(i+1)}));
const response=batch=>({questions:batch.map(q=>({...q,prompt:'fixture'}))});
const input={mode:'textbook',title:'Engineering fixture',passage:'原文',questionCount:12,minutes:60,terms:[]};
const bank={objectives:['理解证据','判断关系'],worksheetMinutes:22,plan:['我做','我们做','你做'].map(stage=>({stage,minutes:20,activity:'测试活动'})),scaffolds:[],questions:Array.from({length:12},(_,i)=>({id:'L'+(i+1),phase:'live',stage:'你做',section:'证据',type:'choice',word:'',skill:'分析',context:'工程测试情境',sourceKind:'transfer',sourceQuote:'',prompt:'工程测试题'+i,hint:'检查对象',english:'Check the subject.',options:['一个合理解释','另一个相关解释','还有一种相关解释','最后一种不同解释'],answer:0,optionReasons:['依据','误区','误区','误区'],misconceptions:['正确','范围','对象','关系'],highDistractor:1,attractionReason:'对象易混',explanation:'工程测试解释',improve:'再看对象',points:1}))};
const reviewResponse=batch=>({checks:batch.map(q=>({id:q.id,verdict:'pass',reason:'工程测试审查结果'})),global:{verdict:'pass',reason:'工程测试审查结果'}});
(async()=>{
await test('batch request has only local count and explicit ids',async()=>{let payload;await HWT.questionRequest(async(system,data)=>{payload={system,data};return {};},input,[{id:'L7'}],{}, {retry:true});assert.equal(payload.data.input.questionCount,1);assert.equal(payload.data.input.totalQuestionCount,12);assert.match(payload.system,/本批共1题/);assert.match(payload.system,/精简重试/);assert.doesNotMatch(payload.system,/格式：\{"objectives/);});
await test('retry changes request instead of repeating it',async()=>{const retry=[];await HWT.batches([{id:'L1'}],async(b,o)=>{retry.push(o.retry);if(!o.retry)throw HWT.aiError('本批超时','AI_TIMEOUT');return response(b);},HWT.checkQuestions);assert.deepEqual(retry,[false,true]);});
await test('final error preserves actual failure reason',async()=>{await assert.rejects(HWT.batches([{id:'L1'}],async()=>{throw HWT.aiError('本批请求超过3分钟。','AI_TIMEOUT');},HWT.checkQuestions),e=>e.code==='AI_TIMEOUT'&&e.message.includes('3分钟'));});
await test('complete reordered responses are aligned without changing question identity',()=>{assert.deepEqual(HWT.checkQuestions({questions:[{id:'L2'},{id:'L1'}]},items.slice(0,2)).questions.map(q=>q.id),['L1','L2']);assert.throws(()=>HWT.checkQuestions({questions:[{id:'L1'},{id:'L1'}]},items.slice(0,2)));});
await test('AI request selects current model and explicit non-thinking JSON mode',()=>{const p=HWT.aiPayload('JSON',{});assert.equal(p.model,'deepseek-flash');assert.equal(p.thinking.type,'disabled');assert.equal(p.response_format.type,'json_object');assert.equal(HWT.aiPayload('text',{},false).response_format,undefined);});
await test('ignore absent-word placeholders',()=>assert.deepEqual(HWT.split('无、 暂无,明白\n明白\tn/a'),['明白']));
await test('truncated output never becomes a bank',()=>assert.throws(()=>HWT.decodeAI({choices:[{finish_reason:'length',message:{content:'{"questions":[]}'}}]}),e=>e.code==='AI_INCOMPLETE'));
await test('broken JSON is recoverable',()=>assert.throws(()=>HWT.decodeAI({choices:[{finish_reason:'stop',message:{content:'{"questions":['}}]}),e=>e.code==='AI_INCOMPLETE'));
await test('valid fenced JSON preserves Chinese',()=>assert.deepEqual(HWT.decodeAI({choices:[{finish_reason:'stop',message:{content:'```json\n{"题目":"证据"}\n```'}}]}),{'题目':'证据'}));
await test('incomplete two-question batches split and preserve order',async()=>{const calls=[],parts=[];await HWT.batches(items,async b=>{calls.push(b.map(q=>q.id));if(b.length>1)throw HWT.aiError('length');return response(b);},HWT.checkQuestions,()=>{},()=>false,r=>parts.push(...r.questions));assert.deepEqual(parts.map(q=>q.id),items.map(q=>q.id));assert.deepEqual(calls,[['L1','L2'],['L1'],['L2'],['L3','L4'],['L3'],['L4']]);});
await test('mismatched IDs split and retry; no silent omissions',async()=>{let n=0;const out=await HWT.batches(items.slice(0,2),async b=>{n++;return b.length>1?{questions:[]}:response(b);},HWT.checkQuestions);assert.equal(n,3);assert.equal(out.length,2);});
await test('single-question failures are bounded',async()=>{let n=0;await assert.rejects(HWT.batches(items.slice(0,1),async()=>{n++;throw HWT.aiError('length');},HWT.checkQuestions));assert.equal(n,2);});
await test('authorization errors never retry or split',async()=>{let n=0;await assert.rejects(HWT.batches(items,async()=>{n++;throw HWT.aiError('HTTP 401','AI_SERVICE');},HWT.checkQuestions));assert.equal(n,1);});
await test('cancel prevents saving late responses',async()=>{let cancelled=false,saved=0;await assert.rejects(HWT.batches(items,async b=>{cancelled=true;return response(b);},HWT.checkQuestions,()=>{},()=>cancelled,()=>saved++));assert.equal(saved,0);});
await test('completed batches survive a later failure',async()=>{const saved=[];await assert.rejects(HWT.batches(items,async b=>{if(b[0].id==='L3')throw HWT.aiError('401','AI_SERVICE');return response(b);},HWT.checkQuestions,()=>{},()=>false,r=>saved.push(...r.questions)));assert.deepEqual(saved.map(q=>q.id),['L1','L2']);});
await test('metadata retry is bounded and requests concise output',async()=>{let n=0;const x=await HWT.smallRequest(async system=>{n++;if(n===1)throw HWT.aiError('length');assert.match(system,/不.*题库/);return {ok:true};},'JSON',{});assert.equal(n,2);assert.equal(x.ok,true);});
await test('audit validates every question after splitting',async()=>{const calls=[];const r=await HWT.autoReview(bank,input,async(system,data)=>{calls.push(data.questions.map(q=>q.id));if(data.questions.length>1)throw HWT.aiError('length');return reviewResponse(data.questions);},()=>{},()=>{});assert.equal(r.passed,true);assert.equal(calls.filter(b=>b.length===1).length,12);});
await test('teacher evidence conflict cannot be auto-approved',async()=>{const r=await HWT.autoReview(bank,input,async(s,d)=>{const r=reviewResponse(d.questions);r.checks[0].verdict='teacher';r.checks[0].reason='参考与原文冲突';return r;},()=>{},()=>{});assert.equal(r.passed,false);assert.ok(r.conflicts.length);});
await test('writing requires an independent writing task',()=>{const r=HWT.validate(HWT.balance(bank),{...input,mode:'writing'});assert.ok(r.errors.some(x=>/独立构思/.test(x.message)));assert.match(HWT.taskRules({mode:'writing'}),/写前.*选材/s);});
await test('writing source quotes can refer to the actual prompt',()=>{const b=structuredClone(bank);b.questions[0].sourceKind='original';b.questions[0].sourceQuote='你原来很内向';const r=HWT.validate(HWT.balance(b),{...input,mode:'writing',writingPrompt:'你原来很内向，后来参与活动。'});assert.ok(!r.errors.some(x=>x.id==='L1'&&/定位/.test(x.message)));});
await test('generation resumes after partial failure without redoing saved questions',async()=>{
 const start=source.indexOf(' async function materials(){'),end=source.indexOf("\n $('generate').onclick",start);let fail=true;const requested=[];
 const ctx={HWT,JSON,Map,Set,snapshot:{...input},checkpoint:null,bank:null,outline:null,cancelled:false,invalidated:0,reviewed:0,saveDraft(){},status(){},invalidate(){ctx.invalidated++;},setBank(b){ctx.bank=b;},async review(){assert.equal(ctx.bank.questions.length,12);ctx.reviewed++;},async ask(system,data){
  if(!data.batch&&/仅输出JSON/.test(system))return {questions:bank.questions.map(({id,phase,stage,section,type,skill,prompt})=>({id,phase,stage,section,type,skill,prompt}))};
  if(!data.batch)return {objectives:bank.objectives,plan:bank.plan,worksheetMinutes:22,scaffolds:[]};
  requested.push(data.batch.map(q=>q.id));if(fail&&data.batch[0].id==='L3')throw HWT.aiError('HTTP 401','AI_SERVICE');return {questions:data.batch.map(q=>bank.questions.find(r=>r.id===q.id))};
 }};vm.createContext(ctx);vm.runInContext(source.slice(start,end),ctx);await assert.rejects(ctx.materials());assert.equal(ctx.checkpoint.full.length,2);fail=false;await ctx.materials();assert.equal(ctx.reviewed,1);assert.equal(requested.filter(b=>b[0]==='L1').length,1);assert.equal(ctx.bank.questions.length,12);
});
await test('three mode forms render required controls without manual imports',()=>{
 for(const mode of ['writing','textbook','vocab']){
  let html='';const stop=Error('CAPTURE');const app={set innerHTML(value){html=value;throw stop;}};
  const document={body:{dataset:{mode}},head:{appendChild(){}},createElement(){return {};},getElementById(id){return id==='app'?app:null;}};
  assert.throws(()=>vm.runInNewContext(source,{document,module:{exports:{}},console}),e=>e===stop);
  assert.match(html,/id="repair" disabled>AI检查题目/);assert.doesNotMatch(html,/importDraft|importFile|导入JSON/);
  if(mode==='writing'){assert.match(html,/id="genre"/);assert.match(html,/id="writingPrompt"/);assert.match(html,/<div hidden><label for="terms">/);}else assert.doesNotMatch(html,/id="genre"/);
 }
});
await test('generated HTML has no key and correctly labels writing materials',()=>{const html=HWT.student(bank,{...input,mode:'writing',writingPrompt:'完整作文任务',key:'SECRET_MUST_NOT_EXPORT'});assert.match(html,/回看题目与材料/);assert.match(html,/完整作文任务/);assert.doesNotMatch(html,/SECRET_MUST_NOT_EXPORT|x-deepseek-key/);assert.match(html,/此预览没有连接成绩收集/);});
await test('existing navigation DATA is unchanged by new year placeholders',()=>{
 const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
 const read=s=>s.match(/const DATA=(.*);\n/)[1];assert.equal(require('node:crypto').createHash('sha256').update(read(html)).digest('hex'),'a38492d717c6c103f067192da54f1e515b0b2f1f874550efefc45b9c957bd809');assert.match(html,/aria-disabled="true"/);assert.match(html,/制作中…/);
});
console.log(JSON.stringify({passed:count,liveAI:false,browserDOM:false,database:false}));
})().catch(e=>{console.error(e);process.exitCode=1;});

