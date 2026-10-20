/* Real lesson DOM simulation; not a browser or iPad test. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const {parseHTML}=require(process.env.LINKEDOM_PATH||'linkedom');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'du/textbook/2hcl/unit1/wo-xiang-dui-ni-shuo'),engine=path.join(root,'du/textbook/shared/lesson-v1');
const storage=new Map();let now=Date.now(),timers=[],downloads=[];
const localStorage={getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k)};
function setup(){const {window}=parseHTML(fs.readFileSync(process.env.LESSON_OFFLINE_PATH||path.join(dir,'reading.html'),'utf8'));
 const location={hash:''};Object.assign(window,{location,localStorage,console,Blob,confirm:()=>true,scrollTo:()=>{},setTimeout:f=>{timers.push(f);return timers.length},clearTimeout:()=>{},Date:class extends Date{static now(){return now}},URL:{createObjectURL:b=>{downloads.push(b);return'blob:mock'},revokeObjectURL:()=>{}},speechSynthesis:{cancel:()=>{},speak:()=>{}}});window.window=window;const ctx=vm.createContext(window);
 if(process.env.LESSON_OFFLINE_PATH){for(const script of window.document.querySelectorAll('script'))vm.runInContext(script.textContent,ctx)}else for(const file of [path.join(dir,'content.js'),path.join(dir,'lexicon.js'),path.join(engine,'catalog.js'),path.join(engine,'wordbook.js'),path.join(engine,'app.js')])vm.runInContext(fs.readFileSync(file,'utf8'),ctx,{filename:file});
 const $=s=>window.document.querySelector(s),route=h=>{location.hash='#'+h;window.dispatchEvent(new window.Event('hashchange'))};return{window,$,route,ctx};}
let env=setup(),{$,route,window:w}=env;
function advance(){now+=5010;const list=timers;timers=[];list.forEach(f=>f())}
function chooseSelect(sel,value){const e=$(sel);assert(e,sel);Object.defineProperty(e,'value',{value:String(value),configurable:true});e.onchange({target:e})}
function choice(id,value){const e=$(`input[name="${id}"][value="${value}"]`);assert(e);e.checked=true;e.onchange()}
function fields(t){for(const f of [...t.fields||[],...t.answerTable?.fields||[]]){const e=$('#field-'+f.id);e.value='我的回答：'+f.label+'；根据原文说明理由。';e.oninput()}}
function evidence(t){for(const [i,r] of(t.evidence||[]).entries()){const parts=[];for(const term of r.requiredTerms||[r.terms[0]]){let found;for(const p of r.p){found=(w.LESSON.paragraphs[p-1].match(/[^。！？]+[。！？][”’]?|[^。！？]+$/g)||[]).find(s=>s.includes(term));if(found)break}assert(found,'evidence '+t.id);if(!parts.includes(found))parts.push(found)}const e=$(`[data-evidence="${i}"]`);e.value=parts.join('\n');e.oninput()}}
assert.equal(w.LESSON.paragraphs.length,6);assert.equal(w.LESSON.tasks.length,8);
assert.equal(w.LESSON.tasks.flatMap(t=>t.blanks||[]).length,6);assert.equal(Object.keys(w.LESSON_WORDS).length,32);
assert.deepEqual(Array.from(w.LESSON.tasks.flatMap(t=>(t.checks||[]).map(c=>c.correct))),[1,3,0,2]);
for(let p=1;p<=6;p++){route('paragraph-'+p);assert.equal($('.source-text').textContent,w.LESSON.paragraphs[p-1]);assert($('.source-paragraph h3').textContent.includes(w.LESSON.paragraphLabels[p-1]));assert.equal(w.document.querySelectorAll('#activity .panel').length,4);$('#paragraphTask').click();assert.equal(w.location.hash.replace(/^#/,''),'task-'+w.LESSON.paragraphTasks[p-1]);}
for(const t of w.LESSON.tasks){route('task-'+t.id);assert.deepEqual([...w.document.querySelectorAll('.source-paragraph')].map(e=>+e.id.slice(1)),Array.from(t.focus));if(t.order<=6)assert(w.LessonEngine.range(t).every(p=>p<=t.order));if(t.answerTable)assert.equal(w.document.querySelectorAll('.answer-table textarea').length,2);}
route('task-guoming-advice');for(const term of ['别犹豫','卡片','别犹豫']){[...w.document.querySelectorAll('.sentence')].find(e=>e.textContent.includes(term)).click();$('[data-slot="0"]').click()}
const ev=$('[data-evidence="0"]').value;assert.equal(ev.split('别犹豫').length,2);assert(ev.includes('拥抱'));assert.equal(ev.split('\n').length,2);
env=setup();({$,route,window:w}=env);route('task-guoming-advice');assert.equal($('[data-evidence="0"]').value,ev);
choice('gm-advice-q',0);$('#submit').click();assert($('#submit').disabled);assert(!$('#solution').textContent);const first=JSON.stringify(w.LessonEngine.state().answers['guoming-advice'].first);advance();choice('gm-advice-q',3);$('#submit').click();assert(w.LessonEngine.state().answers['guoming-advice'].unlocked);assert.equal(JSON.stringify(w.LessonEngine.state().answers['guoming-advice'].first),first);assert.equal(w.LessonEngine.state().answers['guoming-advice'].firstCorrect,false);
// Both independent written tasks require answers, but never claim automatic correctness.
for(const id of ['anonymous-advice','my-message']){route('task-'+id);const t=w.LESSON.tasks.find(t=>t.id===id);evidence(t);$('#submit').click();assert(!w.LessonEngine.state().answers[id].first);$('#nextTask').click();assert($('#feedback').textContent.includes('先完成'));}
for(const t of w.LESSON.tasks.filter(t=>t.id!=='guoming-advice')){
 route('task-'+t.id);evidence(t);for(const c of t.checks||[])choice(c.id,c.correct);for(const b of t.blanks||[])chooseSelect(`[data-blank="${b.id}"]`,b.answer);fields(t);
 $('#submit').click();assert(w.LessonEngine.state().answers[t.id].unlocked,t.id);
 if(t.required)assert.equal(w.LessonEngine.state().answers[t.id].firstCorrect,null);
 if(t.answerTable||t.fields){const original=JSON.stringify(w.LessonEngine.state().answers[t.id].first);const f=$('[data-field]');f.value='修改后的当前回答';f.oninput();$('#revision').value='订正：依据课文区分建议与事实。';$('#revision').dispatchEvent(new w.Event('input'));assert.equal(JSON.stringify(w.LessonEngine.state().answers[t.id].first),original);}
}
env=setup();({$,route,window:w}=env);route('task-anonymous-advice');assert.equal($('#field-trouble').value,'修改后的当前回答');assert.equal($('#revision').value,'订正：依据课文区分建议与事实。');assert(w.LessonEngine.state().answers['anonymous-advice'].first.fields.advice.includes('辅导员的建议'));
route('review');assert($('#review').textContent.includes('点选与取证首次正确率'));for(const [k,v] of [['name','测试学生'],['class','2H'],['number','07']]){const e=$(`[data-identity="${k}"]`);e.value=v;e.oninput()}
$('#downloadCSV').click();$('#downloadJSON').click();$('#downloadText').click();assert.equal(downloads.length,3);
const key='huawentong-personal-words-v1';w.WordBook.add('犹豫');w.WordBook.add('自建词');w.WordBook.add('刀子嘴豆腐心');let book=JSON.parse(storage.get(key));const e=book.entries.find(x=>x.word==='犹豫');assert(w.WordBook.sources(e).some(s=>s.lessonId==='s2u1l1'));assert(book.entries.find(x=>x.word==='刀子嘴豆腐心').meaning);e.meaning='我的释义';e.status='known';storage.set(key,JSON.stringify(book));
w.HWT_WORD_CONTEXT=()=>({lessonId:'s2u1l2',paragraphs:['他有些犹豫。']});w.WordBook.add('犹豫');book=JSON.parse(storage.get(key));assert.equal(book.entries.find(x=>x.word==='犹豫').meaning,'我的释义');assert.equal(book.entries.find(x=>x.word==='犹豫').status,'known');assert.equal(book.entries.find(x=>x.word==='自建词').meaning,'');const before=storage.get(key);assert.throws(()=>w.WordBook.importBook({schema:'invalid'}));assert.equal(before,storage.get(key));
route('paragraph-4');assert(w.document.querySelector('[data-word="刀子嘴豆腐心"]'));
route('review');$('#resetLesson').click();$('#confirmReset').click();assert(storage.get(key));assert.deepEqual(Object.keys(w.LessonEngine.state().answers),[]);
(async()=>{const [csv,json,txt]=await Promise.all(downloads.map(b=>b.text()));for(const s of [csv,json,txt]){assert(s.includes('测试学生'));assert(s.includes('辅导员的建议'));assert(s.includes('订正：依据课文区分建议与事实。'));}assert(csv.includes('not_auto_graded'));assert.equal(JSON.parse(json).answers['anonymous-advice'].firstCorrect,null);console.log('PASS: six messages, eight groups, six vocabulary items, complete ordered panels, cumulative evidence/reload, first-attempt lock, optional and required answer tables, subjective answers without auto grading, identity/three exports, shared wordbook and alias, isolated reset. DOM simulation only.');})().catch(e=>{console.error(e);process.exitCode=1});
