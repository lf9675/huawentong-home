/* Real lesson DOM simulation; not a browser or iPad test. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const {parseHTML}=require(process.env.LINKEDOM_PATH||'linkedom');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'du/textbook/2hcl/unit2/zhu-yang-ye-sheng-dong-wu'),engine=path.join(root,'du/textbook/shared/lesson-v1');
const storage=new Map();let now=Date.now(),timers=[],downloads=[];
const localStorage={getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k)};
function setup(){const {window}=parseHTML(fs.readFileSync(path.join(dir,'reading.html'),'utf8'));
 const location={hash:''};Object.assign(window,{location,localStorage,console,Blob,confirm:()=>true,scrollTo:()=>{},setTimeout:f=>{timers.push(f);return timers.length},clearTimeout:()=>{},Date:class extends Date{static now(){return now}},URL:{createObjectURL:b=>{downloads.push(b);return'blob:mock'},revokeObjectURL:()=>{}},speechSynthesis:{cancel:()=>{},speak:()=>{}}});window.window=window;const ctx=vm.createContext(window);
 for(const file of [path.join(dir,'content.js'),path.join(dir,'lexicon.js'),path.join(engine,'catalog.js'),path.join(engine,'wordbook.js'),path.join(engine,'app.js')])vm.runInContext(fs.readFileSync(file,'utf8'),ctx,{filename:file});
 const $=s=>window.document.querySelector(s),route=h=>{location.hash='#'+h;window.dispatchEvent(new window.Event('hashchange'))};return{window,$,route,ctx};}
let env=setup(),{$,route,window:w}=env;
function advance(){now+=5010;const list=timers;timers=[];list.forEach(f=>f())}
function chooseSelect(sel,value){const e=$(sel);assert(e,sel);Object.defineProperty(e,'value',{value:String(value),configurable:true});if(e.onchange)e.onchange({target:e});else e.dispatchEvent(new w.Event('change'))}
function choice(id,value){const e=$(`input[name="${id}"][value="${value}"]`);e.checked=true;e.onchange()}
function fields(t){for(const f of t.fields||[]){const e=$('#field-'+f.id);e.value='我的回答：'+f.label+'；根据原文说明理由。';e.oninput({target:e})}}
function evidence(t){for(const [i,r] of(t.evidence||[]).entries()){const parts=[];for(const term of r.requiredTerms||[r.terms[0]]){let found;for(const p of r.p){found=(w.LESSON.paragraphs[p-1].match(/[^。！？]+[。！？][”’]?|[^。！？]+$/g)||[]).find(s=>s.includes(term));if(found)break}assert(found,'evidence '+t.id);if(!parts.includes(found))parts.push(found)}const e=$(`[data-evidence="${i}"]`);e.value=parts.join('\n');e.oninput()}}
assert.equal(w.LESSON.paragraphs.length,7);assert.equal(w.LESSON.tasks.length,8);
assert.equal(w.LESSON.tasks.flatMap(t=>t.blanks||[]).length,5);
assert.equal(Object.keys(w.LESSON_WORDS).length,36);
for(let p=1;p<=7;p++){route('paragraph-'+p);assert.equal($('.source-text').textContent,w.LESSON.paragraphs[p-1]);assert.equal(w.document.querySelectorAll('#activity .panel').length,w.LESSON.panels[p-1].length);$('#paragraphTask').click();assert.equal(w.location.hash.replace(/^#/,''),'task-'+w.LESSON.paragraphTasks[p-1]);}
for(const t of w.LESSON.tasks){route('task-'+t.id);assert.deepEqual([...w.document.querySelectorAll('.source-paragraph')].map(e=>+e.id.slice(1)),Array.from(t.focus));if(t.order<=7)assert(w.LessonEngine.range(t).every(p=>p<=t.order));if(t.summaryRow)assert($('#summaryAnswer'));}
route('task-uses');for(const term of ['拯救','医疗设备','购买食物','活动经费','调查研究','拯救']){const e=[...w.document.querySelectorAll('.sentence')].find(e=>e.textContent.includes(term));assert(e);e.click();$('[data-slot="0"]').click()}
const ev=$('[data-evidence="0"]').value;assert.equal(ev.split('拯救').length,2);assert(ev.includes('调查研究'));
env=setup();({$,route,window:w}=env);route('task-uses');assert.equal($('[data-evidence="0"]').value,ev);
const m=w.LESSON.tasks[0];route('task-'+m.id);evidence(m);choice('method-q',1);$('#submit').click();assert($('#submit').disabled);assert(!$('#solution').textContent);const first=JSON.stringify(w.LessonEngine.state().answers[m.id].first);advance();choice('method-q',0);$('#submit').click();assert(w.LessonEngine.state().answers[m.id].unlocked);assert.equal(JSON.stringify(w.LessonEngine.state().answers[m.id].first),first);
route('task-public-message');$('#submit').click();assert(!w.LessonEngine.state().answers['public-message'].first);$('#nextTask').click();assert($('#feedback').textContent.includes('先完成'));assert.equal(w.document.querySelectorAll('#activity a[target="_blank"]').length,2);
for(const t of w.LESSON.tasks.filter(t=>t.id!==m.id)){
 route('task-'+t.id);evidence(t);for(const c of t.checks||[])choice(c.id,c.correct);for(const b of t.blanks||[])chooseSelect(`[data-blank="${b.id}"]`,b.answer);fields(t);
 if(t.summaryRow){const e=$('#summaryAnswer');e.value='我的概括：'+t.summaryRow;e.dispatchEvent(new w.Event('input'));}
 $('#submit').click();assert(w.LessonEngine.state().answers[t.id].unlocked,t.id);
 if(t.summaryRow){assert(w.LessonEngine.state().answers[t.id].first.summary.includes(t.summaryRow));const e=$('#revision');assert(e);e.value='订正：注意原文中的转折。';e.dispatchEvent(new w.Event('input'));}
 if(t.required)assert.equal(w.LessonEngine.state().answers[t.id].firstCorrect,null);
}
env=setup();({$,route,window:w}=env);route('task-orangutan');assert($('#summaryAnswer').value.includes('红毛猩猩'));assert.equal($('#revision').value,'订正：注意原文中的转折。');
route('review');assert($('#review').textContent.includes('取证与点选首次正确率'));$('#downloadCSV').click();$('#downloadJSON').click();$('#downloadText').click();assert.equal(downloads.length,3);
const key='huawentong-personal-words-v1';w.WordBook.add('敏捷');w.WordBook.add('自建词');let book=JSON.parse(storage.get(key));const e=book.entries.find(x=>x.word==='敏捷');assert(w.WordBook.sources(e).some(s=>s.lessonId==='s2u2l1'));e.meaning='我的释义';e.status='known';storage.set(key,JSON.stringify(book));
w.HWT_WORD_CONTEXT=()=>({lessonId:'s2u2l2',paragraphs:['猫的动作敏捷。']});w.WordBook.add('敏捷');book=JSON.parse(storage.get(key));assert.equal(book.entries.find(x=>x.word==='敏捷').meaning,'我的释义');assert.equal(book.entries.find(x=>x.word==='敏捷').status,'known');assert.equal(book.entries.find(x=>x.word==='自建词').meaning,'');const before=storage.get(key);assert.throws(()=>w.WordBook.importBook({schema:'invalid'}));assert.equal(before,storage.get(key));
route('review');$('#resetLesson').click();$('#confirmReset').click();assert(storage.get(key));assert.deepEqual(Object.keys(w.LessonEngine.state().answers),[]);
console.log('PASS: source text/order, 8 groups, 5 word items, 4 optional summary cells, evidence accumulation and reload, first attempt/cooldown/revisions, required response without auto grading, all exports, shared-wordbook source and preservation, isolated reset. DOM simulation only.');
