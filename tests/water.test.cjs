/* Real lesson DOM simulation; not a browser or iPad test. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const {parseHTML}=require(process.env.LINKEDOM_PATH||'linkedom');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'du/textbook/2hcl/unit3/shui-dou-qu-na-le'),engine=path.join(root,'du/textbook/shared/lesson-v1');
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
assert.equal(w.LESSON.paragraphs.length,6);assert.equal(w.LESSON.tasks.length,10);
assert.equal(w.LESSON.tasks.filter(t=>t.mode==='objective').length,5);
assert.equal(w.LESSON.tasks.filter(t=>t.required).length,2);
assert.equal(Object.keys(w.LESSON_WORDS).length,23);
assert.deepEqual(Array.from(w.LESSON.tasks.flatMap(t=>(t.checks||[]).map(c=>c.correct))),[0,1,2]);
assert.equal(w.LESSON.figures[4].rows.reduce((a,r)=>a+r[1],0),100);
assert.deepEqual(Array.from(w.LESSON.figures[5].rows,r=>r[1]),[165,160,154,143,141,130]);
const seen=[];
for(let p=1;p<=6;p++){
 route('paragraph-'+p);assert.equal($('.source-text').textContent,w.LESSON.paragraphs[p-1]);assert($('.source-paragraph h3').textContent.includes('部分'));
 assert.equal(w.document.querySelectorAll('#activity .panel').length,w.LESSON.panels[p-1].length);seen.push(...w.LESSON.panels[p-1]);
 if(w.LESSON.figures[p]){assert($('.data-figure'));for(const row of w.LESSON.figures[p].rows)for(const x of row)assert($('.data-figure').textContent.includes(String(x)));}
 $('#paragraphTask').click();assert.equal(w.location.hash.replace(/^#/,''),'task-'+w.LESSON.paragraphTasks[p-1]);
}
assert.deepEqual(seen,Array.from({length:24},(_,i)=>i+1));
for(const t of w.LESSON.tasks){route('task-'+t.id);assert.deepEqual([...w.document.querySelectorAll('.source-paragraph')].map(e=>+e.id.slice(1)),Array.from(t.focus));if(t.order<17)assert(w.LessonEngine.range(t).every(p=>p<=Math.max(...t.focus)));if(t.bank){assert.equal(w.document.querySelectorAll('[data-blank]').length,t.blanks.length);for(const e of w.document.querySelectorAll('[data-blank]'))assert.deepEqual([...e.querySelectorAll('option')].slice(1).map(o=>o.textContent).sort(),Array.from(t.bank).sort());}}
route('task-trend');for(const term of ['下降的趋势','2030年，我们','下降的趋势']){[...w.document.querySelectorAll('.sentence')].find(e=>e.textContent.includes(term)).click();$('[data-slot="0"]').click()}
const ev=$('[data-evidence="0"]').value;assert.equal(ev.split('下降的趋势').length,2);assert.equal(w.LessonEngine.state().answers.trend.evidence[0].items.length,2);
env=setup();({$,route,window:w}=env);route('task-trend');assert.equal($('[data-evidence="0"]').value,ev);assert.equal(w.LessonEngine.state().position.task,5);
route('task-four-taps');const tap=w.LESSON.tasks.find(t=>t.id==='four-taps').checks[0];choice(tap.id,1);$('#submit').click();assert($('#submit').disabled);assert(!$('#solution').textContent);const first=JSON.stringify(w.LessonEngine.state().answers['four-taps'].first);advance();choice(tap.id,0);$('#submit').click();assert(w.LessonEngine.state().answers['four-taps'].unlocked);assert.equal(JSON.stringify(w.LessonEngine.state().answers['four-taps'].first),first);assert.equal(w.LessonEngine.state().answers['four-taps'].firstCorrect,false);
for(const id of ['trend','save-water']){route('task-'+id);const t=w.LESSON.tasks.find(t=>t.id===id);evidence(t);for(const c of t.checks||[])choice(c.id,c.correct);$('#submit').click();assert(!w.LessonEngine.state().answers[id].first);$('#nextTask').click();assert($('#feedback').textContent.includes('先完成'));}
for(const t of w.LESSON.tasks.filter(t=>t.id!=='four-taps')){
 route('task-'+t.id);evidence(t);for(const c of t.checks||[])choice(c.id,c.correct);for(const b of t.blanks||[])chooseSelect(`[data-blank="${b.id}"]`,b.answer);fields(t);$('#submit').click();assert(w.LessonEngine.state().answers[t.id].unlocked,t.id);
 if(t.required)assert.equal(w.LessonEngine.state().answers[t.id].firstCorrect,null);
 if(t.fields){const original=JSON.stringify(w.LessonEngine.state().answers[t.id].first);const f=$('[data-field]');f.value='修改后的当前回答';f.oninput();$('#revision').value='订正：读准年份、对象和单位，并解释为什么。';$('#revision').dispatchEvent(new w.Event('input'));assert.equal(JSON.stringify(w.LessonEngine.state().answers[t.id].first),original);}
}
env=setup();({$,route,window:w}=env);route('task-trend');assert.equal($('#field-trend-answer').value,'修改后的当前回答');assert.equal($('#revision').value,'订正：读准年份、对象和单位，并解释为什么。');
route('review');assert($('#review').textContent.includes('首次正确率'));assert($('#review').textContent.includes('(4/5)'));
for(const [k,v] of [['name','测试学生'],['class','2H'],['number','07']]){const e=$(`[data-identity="${k}"]`);e.value=v;e.oninput()}
$('#downloadCSV').click();$('#downloadJSON').click();$('#downloadText').click();assert.equal(downloads.length,3);
const key='huawentong-personal-words-v1';w.WordBook.add('趋势');w.WordBook.add('自建词');let book=JSON.parse(storage.get(key));let e=book.entries.find(x=>x.word==='趋势');assert(w.WordBook.sources(e).some(s=>s.lessonId==='s2u3l1'&&s.unit===3));assert.equal(e.examples[0].p,null);assert(e.examples[0].lessonTitle.includes('第5部分'));e.meaning='我的释义';e.status='known';storage.set(key,JSON.stringify(book));
const context=w.HWT_WORD_CONTEXT;w.HWT_WORD_CONTEXT=()=>({lessonId:'s2u1l2',paragraphs:['他的成绩有上升的趋势。']});w.WordBook.add('趋势');w.WordBook.add('其他课词');w.HWT_WORD_CONTEXT=context;book=JSON.parse(storage.get(key));assert.equal(book.entries.find(x=>x.word==='趋势').meaning,'我的释义');assert.equal(book.entries.find(x=>x.word==='趋势').status,'known');assert.equal(book.entries.find(x=>x.word==='自建词').meaning,'');const before=storage.get(key);assert.throws(()=>w.WordBook.importBook({schema:'invalid'}));assert.equal(before,storage.get(key));
w.WordBook.open();assert(w.WordBook.list().some(x=>x.word==='其他课词'));$('#thisLesson').click();assert(!w.WordBook.list().some(x=>x.word==='其他课词'));assert.equal(w.WordBook.list().length,2);$('#wordFlashTab').click();assert($('.flash-word').textContent==='自建词');$('#flipCard').click();assert(! $('[data-mastery="known"]'));assert($('#fixFlashWord'));$('#fixFlashWord').click();$('#editMeaning').value='这是学生自己补充的释义。';$('#saveWordEdit').click();$('#wordFlashTab').click();$('#flipCard').click();$('[data-mastery="known"]').click();assert.equal(JSON.parse(storage.get(key)).entries.find(x=>x.word==='自建词').status,'known');
const savedBook=JSON.parse(storage.get(key));w.WordBook.importBook(savedBook);assert.equal(JSON.parse(storage.get(key)).entries.length,3);
route('review');$('#resetLesson').click();$('#confirmReset').click();assert(storage.get(key));assert.deepEqual(Object.keys(w.LessonEngine.state().answers),[]);assert(!storage.has('huawentong-lesson-s2u1l1-v1'));
(async()=>{const [csv,json,txt]=await Promise.all(downloads.map(b=>b.text()));for(const s of [csv,json,txt]){assert(s.includes('测试学生'));assert(s.includes('图表的主要信息'));assert(s.includes('订正：读准年份、对象和单位，并解释为什么。'));}assert(csv.includes('not_auto_graded'));assert.equal(JSON.parse(json).answers.trend.firstCorrect,null);console.log('PASS: six ordered parts and 24 panels; exact figure values; ten task groups; task-specific banks; cumulative evidence/reload; five-second retry and preserved first answer; two required written tasks without automatic grading; identity and three exports; shared wordbook, filters, edit, flashcards, merge and reset. DOM simulation only.');})().catch(e=>{console.error(e);process.exitCode=1});
