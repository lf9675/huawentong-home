/* DOM regression checks; actual iPad Safari rendering still needs a device check. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),cp=require('child_process');
const {parseHTML}=require(process.env.LINKEDOM_PATH||'linkedom');
const root=path.resolve(__dirname,'..'),inventory=require('../tools/textbook-ipad/inventory.cjs'),current=inventory(),before=inventory(true);
let paragraphCount=0,wordCount=0;
for(const a of current){
 const prior=before.find(x=>x.dir===a.dir),dir=path.join(root,a.dir),legacy=a.dir.endsWith('/tuanyuanfan'),same=k=>assert.equal(JSON.stringify(a.L[k]),JSON.stringify(prior.L[k]),a.dir+' '+k);
 for(const k of ['id','sequenceVersion','paragraphs','tasks','paragraphTasks','panels','readPanels','panelRects','panelSheets'])if(!legacy||!['panelRects'].includes(k))same(k);
 for(const [term,v]of Object.entries(a.words)){assert(v.en?.trim()&&v.meaning);assert.equal(v.meaning,prior.words[term].meaning);wordCount++;}
 const html=fs.readFileSync(dir+'/reading.html','utf8'),{window:w}=parseHTML(html),storage=new Map(),location={hash:''};
 const oldWord=Object.keys(a.words)[0];storage.set('huawentong-personal-words-v1',JSON.stringify({schema:'huawentong-words-v1',entries:[{word:oldWord,meaning:a.words[oldWord].meaning,en:'',note:'保留笔记',source:'本课语境释义',lessons:[a.L.id||'s1u2l2'],status:'known',createdAt:'original'}]}));
 Object.assign(w,{console,Blob,location,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k)},setTimeout:()=>1,clearTimeout:()=>{},scrollTo:()=>{},confirm:()=>true,speechSynthesis:{cancel:()=>{},speak:()=>{}},URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}}});w.window=w;const ctx=vm.createContext(w);
 for(const match of html.matchAll(/<script[^>]*src="([^"]+)"[^>]*><\/script>/g)){
  const src=match[1].split('?')[0];if(/cloud|package-v2/.test(src))continue;
  vm.runInContext(fs.readFileSync(path.resolve(dir,src),'utf8'),ctx,{filename:src});
 }
 const $=s=>w.document.querySelector(s),route=h=>{location.hash='#'+h;w.dispatchEvent(new w.Event('hashchange'));};
 for(let p=1;p<=a.L.paragraphs.length;p++){
  route('paragraph-'+p);paragraphCount++;assert.equal((legacy?$('.passage'):$('.source-text')).textContent,a.L.paragraphs[p-1]);
  const imgs=[...w.document.querySelectorAll(legacy?'.comic-panel img':'#activity .panel img')];assert.equal(imgs.length,(a.L.panels||a.L.readPanels)[p-1].length);
  for(const img of imgs){assert(fs.existsSync(path.resolve(dir,img.getAttribute('src'))));assert.equal(img.getAttribute('loading'),'eager');assert(+img.getAttribute('width')>0&&+img.getAttribute('height')>0);assert(!img.getAttribute('style'));}
  for(const el of [...w.document.querySelectorAll('#source [data-word]')]){el.click();assert($('#dialogContent .word-english')?.textContent.trim());assert(!$('#dialogContent details'));$('#dialogClose').click();}
 }
 w.WordBook.open();const e=JSON.parse(storage.get('huawentong-personal-words-v1')).entries[0];assert(e.en);assert.equal(e.note,'保留笔记');assert.equal(e.status,'known');assert.equal(e.createdAt,'original');assert($('#wordDialogContent .word-english'));
 $('#wordFlashTab').click();$('#includeKnown').checked=true;$('#includeKnown').onchange({target:$('#includeKnown')});$('#flipCard').click();assert($('.flash-back .word-english'));
 console.log('PASS',a.dir.split('/').pop(),a.L.paragraphs.length,'paragraphs',Object.keys(a.words).length,'bilingual words');
}
console.log('TOTAL',current.length,'lessons',paragraphCount,'paragraphs',wordCount,'bilingual entries');

for(const a of current){const dir=path.join(root,a.dir),p=dir+'/vocabulary.html';if(!fs.existsSync(p))continue;const html=fs.readFileSync(p,'utf8'),{window:w}=parseHTML(html),location={hash:''};Object.assign(w,{console,Blob,location,localStorage:{getItem:()=>null,setItem:()=>{}},setTimeout:()=>1,clearTimeout:()=>{},scrollTo:()=>{},speechSynthesis:{cancel:()=>{},speak:()=>{}}});w.window=w;const ctx=vm.createContext(w);for(const m of html.matchAll(/<script[^>]*src="([^"]+)"[^>]*><\/script>/g)){vm.runInContext(fs.readFileSync(path.resolve(dir,m[1].split('?')[0]),'utf8'),ctx)}location.hash='#paragraph-1';w.dispatchEvent(new w.Event('hashchange'));assert(w.LESSON.wordEnglishVisible);assert(w.document.querySelector('#activity .panel img').getAttribute('src').includes('/panels/'));w.document.querySelector('#source [data-word]').click();assert(w.document.querySelector('#dialogContent .word-english'));console.log('PASS vocabulary',a.dir.split('/').pop())}
