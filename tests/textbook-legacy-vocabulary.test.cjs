const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),cp=require('child_process');
const {parseHTML}=require(process.env.LINKEDOM_PATH||'linkedom');
const root=path.resolve(__dirname,'..'),base='88d102f6d15c4c7cc8672d2f31d332b4d3a91eaa';
const paths=['du/textbook/1hcl/unit5/1hcl-unit5-haidi.html','du/textbook/1hcl/unit6/1hcl-unit6-shicheng.html'];
async function open(file,saved={}){
 const html=fs.readFileSync(path.join(root,file),'utf8'),{window:w}=parseHTML(html);
 Object.assign(w,{console,IntersectionObserver:class{observe(){}},setTimeout:()=>1,clearTimeout:()=>{},localStorage:{setItem(){}},location:{reload(){}},storage:{get:async()=>({value:JSON.stringify(saved)}),set:async()=>{},delete:async()=>{}},confirm:()=>true});w.window=w;const ctx=vm.createContext(w);
 for(const s of w.document.querySelectorAll('script')){const src=s.getAttribute('src');if(src&&!src.includes('legacy-vocabulary'))continue;Object.defineProperty(w.document,'currentScript',{value:s,configurable:true});vm.runInContext(src?fs.readFileSync(path.join(root,src.split('?')[0]),'utf8'):s.textContent,ctx);}
 await w.HWTWorksheetReady;
 const tables=vm.runInContext('JSON.stringify([VOC_A,VOC_B,VOC_C])',ctx);
 const original=cp.execFileSync('git',['show',base+':'+file],{cwd:root,encoding:'utf8'}),c=vm.createContext({});
 const start=original.indexOf('const VOC_A'),end=original.indexOf('];',original.indexOf('const VOC_C'))+2;
 vm.runInContext(original.slice(start,end),c);assert.equal(tables,vm.runInContext('JSON.stringify([VOC_A,VOC_B,VOC_C])',c));
 return w;
}
(async()=>{for(const file of paths){let w=await open(file),qs=[...w.document.querySelectorAll('#vocA .q,#vocB .q,#vocC .q')];assert.equal(qs.length,14);assert(w.document.querySelector('.hwt-explained-word'));assert.equal(w.document.querySelectorAll('.hwt-english').length,0);for(const q of qs){q.querySelector('button').click();assert(q.querySelector('.fb .hwt-english')?.textContent);assert(q.querySelector('.fb .hwt-explained-word'));}const saved=w.HWTWorksheet.state();assert.equal(Object.keys(saved).length,14);w=await open(file,saved);assert.equal(w.document.querySelectorAll('.hwt-english').length,14);assert.deepEqual(w.HWTWorksheet.state(),saved);assert.equal(Object.keys(w.HWT_LEGACY_LEXICON).length,file.includes('haidi')?7:12);console.log('PASS',file,'14 bilingual feedbacks; original questions, choices, answers and saved responses preserved');}})().catch(e=>{console.error(e);process.exitCode=1});
