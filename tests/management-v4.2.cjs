// DOM simulation and score fixtures only; no live student data or credentials.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM}=require('jsdom');
const Cloud=require('../bei/shared/classroom.js');
let passed=0;async function test(name,fn){await fn();passed++;console.log('PASS '+name);}
const lesson={id:'00000000-0000-4000-8000-000000000001',title:'工程测试',created_at:'2026-09-10T00:00:00Z',bank:{questions:[{id:'L1',type:'choice',stage:'你做',points:1,prompt:'题干',options:['甲','乙','丙','丁'],answer:0},{id:'O1',type:'open',stage:'你做',points:2,prompt:'解释',rubric:['内容','情感'],explanation:'参考答案'}]}};
const attempt={id:'00000000-0000-4000-8000-000000000002',created_at:'2026-09-10T00:01:00Z',class_name:'TEST',student_no:'01',student_name:'测试学生',records:[{id:'L1',type:'choice',stage:'你做',score:0,max:1,chosenIndex:1,correct:false},{id:'O1',type:'open',stage:'你做',answer:'原始答案',selfScore:2,teacherScore:null,max:2,reviewRevision:0}]};
(async()=>{
await test('pending open marks are not treated as zero or self-assessment',()=>{assert.equal(Cloud.grade(attempt).total,null);const a=structuredClone(attempt);a.records[1].teacherScore=0;assert.equal(Cloud.grade(a).total,0);assert.equal(Cloud.grade(a).pending,0);});
await test('first submission is chronological, not input order',()=>{const later={...attempt,id:'00000000-0000-4000-8000-000000000003',created_at:'2026-09-10T00:02:00Z'};const s=Cloud.summary(lesson,[later,attempt]);assert.equal(s.rows[0].id,attempt.id);assert.equal(Cloud.exportRows(lesson,[later,attempt])[1][8],2);});
await test('roster detects missing, mismatched and unlisted without guessing',()=>{const s=Cloud.rosterStatus([{class_name:'TEST',students:[{studentNo:'01',name:'另一个名字'},{studentNo:'02',name:'未提交'}]}],[attempt,{...attempt,student_no:'03'}]);assert.equal(s.missing[0].studentNo,'02');assert.equal(s.mismatch[0].studentNo,'01');assert.equal(s.unlisted[0].student_no,'03');assert.equal(Cloud.rosterStatus([],[]).missing.length,0);assert.throws(()=>Cloud.parseRoster('01\t甲\n01\t乙'));assert.equal(Cloud.parseRoster('01\t甲')[0].studentNo,'01');});
await test('CSV quotes fields and neutralizes spreadsheet formulas',()=>{const s=Cloud.csv([['=HYPERLINK("x")','甲,乙','line\nnext']]);assert.ok(s.startsWith('\ufeff'));assert.ok(s.includes("\"'=HYPERLINK"));assert.ok(s.includes('"甲,乙"'));});
await test('frontend and server export the same authoritative scores',async()=>{const server=await import('../supabase/functions/hwt-classroom/management.ts');assert.deepEqual(Cloud.exportRows(lesson,[attempt]),server.sheetRows(lesson,[attempt]));assert.deepEqual(Cloud.grade(attempt),server.gradeAttempt(attempt));});
const dom=new JSDOM('<main id="host"></main>',{url:'https://fixture.invalid/bei/textbook-generator/',runScripts:'outside-only'}),w=dom.window;w.module={exports:{}};w.structuredClone=structuredClone;
let failSave=false,calls=[],pending,askImpl=async()=>'';const data={lesson,attempts:[structuredClone(attempt)],rosters:[],truncated:false};
w.fetch=async(url,opts)=>{const b=JSON.parse(opts.body);calls.push(b);let body;
 if(b.action==='list')body={lessons:[lesson]};
 else if(b.action==='records')body=structuredClone(data);
 else if(b.action==='sheets_status')body={configured:false};
 else if(b.action==='review'){if(failSave)return Response.json({error:'工程测试断网'},{status:503});body={saved:true,review:{score:b.score,feedback:b.feedback,revision:b.revision+1,reviewed_at:'2026-09-10T01:00:00Z'}};}
 else throw Error('unexpected '+b.action);return Response.json(body);
};
w.eval(fs.readFileSync(path.join(__dirname,'../bei/shared/classroom.js'),'utf8'));
w.module.exports.mount({host:w.document.querySelector('#host'),ask:(...args)=>askImpl(...args),run:fn=>{pending=fn();return pending;},improve:async()=>{}});
const $=id=>w.document.getElementById(id),click=async id=>{$(id).click();await pending;};
await test('teacher can load roster and open-answer review controls',async()=>{await click('cloudRefresh');await click('cloudRecords');assert.match($('cloudRoster').textContent,/待覆核/);assert.match($('mgAnswers').textContent,/原始答案/);assert.match($('mgMissing').textContent,/不能判断/);assert.equal($('mgExport').disabled,false);});
await test('teacher can save a zero mark with the current revision',async()=>{const card=$('mgAnswers').querySelectorAll('section')[1];card.querySelector('select').value='0';card.querySelector('textarea').value='按证据给分';card.querySelector('button').click();await pending;const request=calls.at(-1);assert.equal(request.action,'review');assert.equal(request.score,0);assert.equal(request.revision,0);assert.match(card.textContent,/已保存/);assert.equal($('cloudImprove').disabled,true);});
await test('failed save preserves feedback and never reports saved',async()=>{failSave=true;const card=$('mgAnswers').querySelectorAll('section')[1];card.querySelector('textarea').value='尚未保存的评语';card.querySelector('button').click();await assert.rejects(pending);assert.equal(card.querySelector('textarea').value,'尚未保存的评语');assert.match(card.textContent,/尚未保存/);assert.equal(card.querySelector('button').disabled,false);});
await test('late AI report cannot appear under another class',async()=>{let resolve;askImpl=()=>new Promise(r=>resolve=r);$('cloudAnalyze').click();await new Promise(setImmediate);assert.equal(typeof resolve,'function');$('cloudClass').value='OTHER';$('cloudClass').dispatchEvent(new w.Event('input'));resolve('stale report');await pending;assert.equal($('cloudReport').textContent,'');assert.equal($('cloudImprove').disabled,true);});
await test('changing selection clears old student data and disables export',()=>{$('cloudClass').value='OTHER';$('cloudClass').dispatchEvent(new w.Event('input'));assert.equal($('mgAnswers').textContent,'');assert.equal($('mgExport').disabled,true);});
dom.window.close();console.log(JSON.stringify({passed,mode:'simulated DOM; no live browser or Google writes'}));
})().catch(e=>{console.error(e);process.exitCode=1;});
