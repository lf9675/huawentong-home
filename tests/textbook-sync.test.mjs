import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const source=fs.readFileSync(new URL('../du/textbook/shared/lesson-v1/cloud.js',import.meta.url),'utf8');
const turn=()=>new Promise(r=>setImmediate(r));
function setup({pending,answers={},failFirst=false}={}){
 const buttons=[],timers=new Map(),writes=[],store=new Map(),events={};let timerId=0,revision=0,fail=failFirst;
 const state={answers,position:{view:'task',p:1},cloudReadParagraphs:[]};
 const element=tag=>({tag,textContent:'',dataset:{},append(...els){for(const e of els)if(e.tag==='button')buttons.push(e)},prepend(){},setAttribute(){},classList:{add(){}}});
 const host=element('main');const storageKey='test-lesson';if(pending)store.set(storageKey+'-sync-pending',JSON.stringify(pending));store.set(storageKey+'-sync',JSON.stringify({revision:0}));
 const w={LESSON:{id:'pilot',version:'v1',tasks:[{id:'a'},{id:'b'}]},LessonEngine:{state:()=>state,restore:()=>{}},HWTTextbookConnection:{assignmentId:'a',studentId:'s',token:'t'},LESSON_STORAGE_KEY:storageKey,addEventListener:(n,f)=>events[n]=f};
 const context={window:w,document:{createElement:element,querySelector:s=>s==='main'?host:null,body:element('body'),head:element('head'),addEventListener(){},hidden:false},localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)},location:{pathname:'/',replace(){}},confirm:()=>false,crypto,AbortController,Uint8Array,Date,Set,JSON,Error,setTimeout:(f,ms)=>{timers.set(++timerId,{f,ms});return timerId},clearTimeout:id=>timers.delete(id),setInterval:()=>1,fetch:async(_url,options)=>{const b=JSON.parse(options.body);if(b.action==='connect')return {ok:true,json:async()=>({assignment:{lessonId:'pilot',contentVersion:'v1',className:'Test',title:'Test'},student:{revision,student_no:'01'},responses:[]})};writes.push(b);if(fail){fail=false;throw Error('offline')}return {ok:true,json:async()=>({saved:true,revision:++revision,receivedAt:new Date().toISOString()})}}};
 vm.runInNewContext(source,context);return {buttons,writes,state,events,async settle(){for(let i=0;i<8;i++){await turn();const ts=[...timers].filter(([,v])=>v.ms<20000);for(const [id,t]of ts){timers.delete(id);t.f()}}}};
}
const answer=n=>({first:{fields:{response:n},choices:{},evidence:{},timestamp:'2026-10-22T05:00:00Z'},attempts:[],revision:'',hintCount:0});
test('pending offline retry keeps request ID, then sends newer work',async()=>{
 const old={lessonId:'pilot',contentVersion:'v1',records:[{taskId:'a',first:answer('first').first,latest:answer('first').first,revision:'',hintCount:0}],readParagraphs:[],final:false,baseRevision:0,requestId:'fixed-retry-id'};
 const h=setup({pending:old,answers:{a:answer('first'),b:answer('new work')},failFirst:true});await h.settle();
 await h.buttons.find(b=>b.textContent==='立即同步').onclick();await h.settle();assert.equal(h.writes[0].requestId,h.writes[1].requestId);assert.equal(h.writes[2].records.length,2);assert.equal(h.writes[2].baseRevision,1);assert.equal(h.writes.length,3);
});
test('final submission cannot claim an incomplete lesson',async()=>{const h=setup({answers:{a:answer('one')}});await h.settle();await h.buttons.find(b=>b.textContent==='交齐本课').onclick();await h.settle();assert.ok(h.writes.every(x=>!x.final))});
test('final intent survives an older queued request',async()=>{const old={lessonId:'pilot',contentVersion:'v1',records:[],readParagraphs:[],final:false,baseRevision:0,requestId:'queued'};const h=setup({pending:old,answers:{a:answer('one'),b:answer('two')},failFirst:true});await h.settle();await h.buttons.find(b=>b.textContent==='交齐本课').onclick();await h.settle();assert.ok(h.writes.some(x=>x.final&&x.records.length===2))});
