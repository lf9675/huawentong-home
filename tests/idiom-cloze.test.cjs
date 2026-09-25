// Run: NODE_PATH=/path/to/linkedom/node_modules node tests/idiom-cloze.test.cjs
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {parseHTML}=require('linkedom');
const root=path.resolve(__dirname,'..');
const app=fs.readFileSync(path.join(root,'du/ciyu/ciyu-lianxi/xuanci-shared/app.js'),'utf8');
const storage=new Map();
const sets=[
 ['chengyu88-106','近朱者赤，近墨者黑|惊弓之鸟|井井有条|咎由自取|居安思危|举足轻重|开门见山|开源节流|慷慨解囊|口若悬河|口是心非|扣人心弦|苦口婆心|滥竽充数|狼狈为奸|礼尚往来|理直气壮|力不从心|立竿见影'],
 ['chengyu71-87','好逸恶劳|鹤立鸡群|狐假虎威|囫囵吞枣|胡作非为|花言巧语|画龙点睛|画蛇添足|诲人不倦|混水摸鱼|豁然开朗|家喻户晓|见仁见智|见义勇为|捷足先登|金玉良言|锦上添花'],
 ['chengyu106-122','良药苦口|了如指掌|淋漓尽致|令人发指|路不拾遗|屡见不鲜|络绎不绝|落花流水|毛骨悚然|毛遂自荐|每况愈下|面面俱到|面目全非|名列前茅|名落孙山|墨守成规']
];
function load(dir){
 const {document,window:dom}=parseHTML(fs.readFileSync(path.join(dir,'index.html'),'utf8'));
 const win={addEventListener(){},innerWidth:1024,innerHeight:768};
 const ctx=vm.createContext({window:win,document,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},setTimeout:()=>0,clearTimeout(){},confirm:()=>true});
 vm.runInContext(fs.readFileSync(path.join(dir,'data.js'),'utf8'),ctx);
 vm.runInContext(app,ctx);
 const key='hwt-cloze-'+win.CLOZE_ID;
 return {document,dom,data:win.CLOZE_DATA,key,ctx,
  read:()=>JSON.parse(storage.get(key)||'{}'),
  input(num,value,retry=false){const el=document.querySelector(`#${retry?'book-q-':'q-'}${num} input`);el.value=value;el.dispatchEvent(new dom.Event('input',{bubbles:true}));return el;},
  check(num,retry=false){document.querySelector(`#${retry?'book-q-':'q-'}${num} .check`).click();},
  status(num,retry=false){return document.getElementById(`${retry?'book-q-':'q-'}${num}`).className;}
 };
}
for(const [slug,answers] of sets){
 const dir=path.join(root,'du/ciyu/chengyu-lianxi',slug);
 let page=load(dir);
 const qs=page.data.questions, expected=answers.split('|');
 assert.equal(JSON.stringify(qs.map(q=>q.answer)),JSON.stringify(expected));
 assert.equal(new Set(page.data.wordBank).size,qs.length);
 assert.notEqual(JSON.stringify(page.data.wordBank),JSON.stringify(expected));
 assert.equal(page.document.querySelectorAll('.main-input').length,qs.length);
 assert.equal(page.document.querySelectorAll('.main-check').length,qs.length);
 for(const q of qs){
  assert.equal((q.sentence.match(/_+/g)||[]).length,1);
  assert(page.data.wordBank.includes(q.answer));
  assert(q.whyZh&&q.whyEn);
  assert(q.keywords.length&&q.keywords.every(k=>q.sentence.includes(k)));
  assert(Object.keys(q.glosses).length);
  for(const [word,tip] of Object.entries(q.glosses)){assert(q.sentence.includes(word));assert.equal(tip.split('；').length,2);}
  assert(page.document.getElementById('q-'+q.num).querySelector('.keyword'));
 }
 // Empty submissions do not score; the same wrong click counts once.
 page.check('1');assert(!page.read().first?.['1']);assert.equal(page.document.querySelector('#q-1 .field-error').hidden,false);
 page.input('1','错误答案');page.check('1');page.check('1');
 assert(page.status('1').includes('wrong'));assert.equal(page.read().history['1'].wrongCount,1);
 assert.equal(page.read().first['1'],false);assert.equal(page.document.querySelector('#mistake-count').textContent,'1');
 assert(page.document.querySelector('#q-1 .feedback').textContent.includes(qs[0].whyZh));
 // Reload preserves the first response and wrong-answer history.
 page=load(dir);assert(page.status('1').includes('wrong'));assert.equal(page.read().firstAnswers['1'],'错误答案');
 page.document.querySelector('#notebook-tab').click();
 assert.equal(page.document.querySelector('#book-q-1 input').value,'');
 assert.equal(page.document.querySelector('#book-q-1 .feedback').hidden,true);
 page.input('1',qs[0].answer,true);page.check('1',true);
 assert(page.status('1',true).includes('correct'));assert.equal(page.read().first['1'],false);
 assert.equal(page.read().history['1'].firstWrong,'错误答案');assert.equal(page.read().retryStatus['1'],'correct');
 page.document.querySelector('#practice-tab').click();
 // All supplied answers can be checked. Main and review use the same validator.
 for(const q of qs){page.input(q.num,' '+q.answer+' ');page.check(q.num);assert(page.status(q.num).includes('correct'),slug+' Q'+q.num);}
 assert.equal(page.document.querySelector('#checked-count').textContent,`已核对 ${qs.length} / ${qs.length}`);
 // Editing a checked answer clears the colour; a later error keeps the first score.
 page.input('2','另一个错词');assert(!page.status('2').includes('correct'));
 page.check('2');assert.equal(page.read().first['2'],true);assert.equal(page.read().mistakes['2'],true);
 for(const q of qs.filter(q=>q.acceptedAnswers)){
  for(const alt of [q.answer.replace('，',','),...q.acceptedAnswers]){
   page.input(q.num,alt);page.check(q.num);assert(page.status(q.num).includes('correct'));
   page=load(dir);assert(page.status(q.num).includes('correct'),'Alternative must survive reload');
  }
  page.input(q.num,q.answer.slice(0,2));page.check(q.num);assert(page.status(q.num).includes('wrong'),'Partial idiom rejected');
 }
 console.log('PASS',slug,qs.length,'answers, feedback, notebook, reload, first-score preservation');
}
assert.equal(storage.size,3,'Separate progress keys for the three new sets');
// Regression: the shared validator must not break existing S1 lessons or progress.
for(const year of [2024,2023,2022]){
 const dir=path.join(root,'du/ciyu/ciyu-lianxi','s1-xuanci-'+year);
 const page=load(dir);
 for(const q of page.data.questions){page.input(q.num,q.answer);page.check(q.num);assert(page.status(q.num).includes('correct'));}
 const restored=load(dir);
 assert.equal(restored.document.querySelectorAll('.question.correct').length,20);
 console.log('PASS existing S1',year,'20 answers and restored results');
}
assert.equal(storage.size,6);
console.log('PASS 112 reference answers across six lessons; no progress-key collisions');
