/* Rebuild the server snapshots and teacher metadata from the actual published content. */
import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';
const root=new URL('../',import.meta.url),base=path.resolve(root.pathname);
const walk=p=>fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(p,e.name)):[path.join(p,e.name)]);
const all=[];
for(const file of walk(path.join(base,'du/textbook')).filter(p=>p.endsWith('/content.js')).sort()){
 const c={};c.window=c;vm.createContext(c);vm.runInContext(fs.readFileSync(file,'utf8'),c);
 const rel=path.relative(base,path.dirname(file)),match=rel.match(/\/(\d)hcl\/unit(\d)\//),grade=match[1]+'hcl',unit=Number(match[2]);
 let l=c.LESSON;
 if(!l){const d=vm.runInContext('DATA',c);l={id:d.lessonId,version:'tuanyuanfan-v'+d.version,title:'团圆饭',paragraphs:d.paragraphs,tasks:d.tasks.map(t=>{
 const task={id:String(t.id),title:t.id+' · '+t.title,questions:[t.question],mode:['write','thread','open'].includes(t.type)?'written':'objective',legacyType:t.type,answer:t.answer,role:'原课文学习步骤',scoreGuide:t.points.join('；')};
 if(t.checks)task.checks=t.checks.map(x=>({...x,question:x.label}));
 if(t.slots){task.evidence=t.slots.map((label,i)=>({label,p:[t.evidenceRules[i].p],allTerms:t.evidenceRules[i].terms,anyTerms:t.evidenceRules[i].any}));task.evidenceMatcher='legacy';task.unorderedEvidence=t.unorderedEvidence===true;}
 if(t.type==='write')task.fields=[{id:'response',label:'我的完整回答'}];
 if(t.type==='thread')task.fields=[{id:'thread',label:'线索'},{id:'theme',label:'主题'}];
 if(t.type==='open')task.fields=[{id:'stance',type:'select',options:['认同','部分认同','不认同'],label:'立场'},...['reason','example','link'].map((id,i)=>({id,label:['理由','例子','回扣'][i]}))];
 if(t.type==='quotes')task.tokenSelections=d.quoteExercises.map((q,i)=>({id:'quote'+i,...q}));
 return task;})};fs.writeFileSync(path.join(path.dirname(file),'cloud-lesson.js'),'/* Generated from content.js; collection metadata only. */\nwindow.LESSON='+JSON.stringify(l)+';\n');
 }
 // Do not change published teaching labels. Normalize only the server's review categories.
 const tasks=l.tasks.map(t=>({...t,mode:['objective','oral'].includes(t.mode)?t.mode:'written',...(t.blanks?{bank:t.bank||l.idioms.map(x=>x[0])}:{})}));
 all.push({id:l.id,title:l.title,version:l.version,grade,gradeLabel:grade==='1hcl'?'中一高级华文':'中二高级华文',unit,readingPath:'/'+rel+'/reading.html',tasks,paragraphs:l.paragraphs});
}
// Two earlier published worksheets retain their own UI and storage format.
for(const [unit,slug,id,title] of [[5,'haidi','s1u5l2','海底牧场游记'],[6,'shicheng','s1u6l2','我为狮城做贡献']]){
 if(all.some(lesson=>lesson.id===id))continue; // New package supersedes legacy catalogue entry.
 const rel=`du/textbook/1hcl/unit${unit}/1hcl-unit${unit}-${slug}.html`,html=fs.readFileSync(path.join(base,rel),'utf8');
 const code=html.slice(html.indexOf('const VOC_A'),html.indexOf('/* ================= 存储'));
 const c=vm.createContext({});vm.runInContext(code,c);const get=name=>vm.runInContext(name,c),tasks=[];
 function mcqs(rows,prefix,section){rows.forEach(([question,options,correct,answer],i)=>tasks.push({id:prefix+i,title:section+' '+(i+1),mode:'objective',checks:[{id:'choice',question,options,correct}],questions:[question],answer,legacyKey:prefix+i,legacyKind:'index'}));}
 mcqs(get('VOC_A'),'a','词语一');mcqs(get('VOC_B'),'b','词语二');mcqs(get('VOC_C'),'c','词语三');
 function selectTask(key,title,question,options,correct,values=options){tasks.push({id:key,title,questions:[question],mode:'objective',fields:[{id:'value',label:question,type:'select',options,correct}],legacyKey:key,legacyKind:'value',legacyValues:values,answer:correct});}
 if(slug==='haidi'){
 mcqs(get('ROUTE_Q'),'q','行程理解');mcqs(get('FIGS').map(f=>[f[0],get('FIG_OPTS'),f[1],f[2]]),'f','修辞');
 get('LEGS').forEach(([para,question,correct,seen,demo],i)=>{if(!demo)selectTask('L'+i,para,question,['空中','海面','海里','海底'],correct)});
 const core=get('CORE'),allowed=get('OK_TOO'),tokens=get('TOKENS').map(t=>t.replace(/[，。！]/g,''));
 tasks.push({id:'verbs',title:'动词雷达',questions:['圈出高潮段的关键动作。'],mode:'objective',legacyKind:'verbs',verbCore:core,verbAllowed:allowed,verbTokens:tokens,fields:[...core.map((w,i)=>({id:'verb'+i,label:w,type:'select',options:['已圈选','未圈选'],correct:'已圈选'})),{id:'extra',label:'是否圈入不相关词',type:'select',options:['没有','有'],correct:'没有'},{id:'picked',label:'实际圈选',optional:true}],answer:'关键动作：'+core.join('、')});
 }else{
 mcqs(get('TL_AFTER'),'t','时间线理解');mcqs(get('HERO'),'h','幕后英雄');
 get('TL').forEach(([clock,correct,options],i)=>selectTask('T'+i,'时间线 '+clock,clock+' 在做什么？',options,correct));
 get('JUDGE').forEach(([question,fact,answer],i)=>selectTask('J'+i,'事实与意见 '+(i+1),question,['事实','意见'],fact?'事实':'意见',['fact','opin']));
 }
 tasks.push({id:'reflection',title:'读后说',questions:[slug==='haidi'?'未来市想把“羊鱼”“牛鱼”引进新加坡，解决粮食供应问题。你是否赞成？请写至少两点理由，并记录听完别组发言后是否改变立场。':'有人说：“把简单的事做好，就是不简单。”你同意吗？结合课文或生活写至少两点理由；生活里，谁也是这样的“幕后英雄”？'],mode:'written',legacyKind:'written',fields:[{id:'stance',label:'立场',type:'select',options:slug==='haidi'?['非常赞成','赞成','反对','非常反对']:['同意','不完全同意']},{id:'reason',label:'理由'},{id:slug==='haidi'?'switch':'hero_life',label:slug==='haidi'?'交流后的想法':'生活中的例子'}],answer:'按原题立场、理由和具体内容由教师覆核，不按字数自动评分。'});
 const l={id,title,version:slug+'-collection-v1',grade:'1hcl',gradeLabel:'中一高级华文',unit,readingPath:'/'+rel,format:'旧版自主学习单',paragraphs:[],tasks};all.push(l);
 fs.writeFileSync(path.join(base,path.dirname(rel),slug+'-cloud-lesson.js'),'/* Generated from the published worksheet. */\nwindow.LESSON='+JSON.stringify(l)+';\n');
}
const wordbookContext=vm.createContext({window:{}});vm.runInContext(fs.readFileSync(path.join(base,'du/textbook/shared/lesson-v1/catalog.js'),'utf8'),wordbookContext);
const order=l=>wordbookContext.window.LESSON_CATALOG.find(c=>c.id===l.id||c.aliases.includes(l.id))?.id||l.id;
all.sort((a,b)=>a.grade.localeCompare(b.grade)||a.unit-b.unit||order(a).localeCompare(order(b),'en',{numeric:true}));
fs.writeFileSync(path.join(base,'supabase/functions/hwt-textbook/lessons.json'),JSON.stringify(all));
fs.writeFileSync(path.join(base,'bei/management/textbook/catalog.json'),JSON.stringify(all.map(({tasks,paragraphs,...l})=>({...l,taskCount:tasks.length})),null,2)+'\n');
console.log('Built '+all.length+' lessons, '+all.reduce((n,l)=>n+l.tasks.length,0)+' learning steps.');
